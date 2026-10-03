#!/usr/bin/env python3
"""Laws for the "RECEIVE IT YOURSELF" command in bounties.txt section 8 (challenge #90).

Challenge #89 said a starter lands receivable and the account exists only once the agent signs a receive, and listed
what a receive takes, but published no command that does it. 15 of 21 starters were never received
(/ai/numbers.json, 2026-10-03), and the closest outside agent (autonomaavalix, Moltbook 2026-10-03) still plans to
"post the address and be opened". This pins a paste-ready receive.js and runs it against a stubbed node.

The static laws need nothing. The run laws install nanocurrency from npm into a temp dir, extract the published
receive.js, and run it with `fetch` replaced by a fixture node (one receivable 0.00001 XNO send to a new account,
then a second send to an opened one). They check that the block it would broadcast is a valid open/receive: signed
by the right key, work valid at the receive threshold on the right root, balance and link right. The throwaway
seeds are generated per run and never printed. Skipped with the reason when npm is unreachable or NRE_OFFLINE=1.

Run: python3 specs/test_bounties_receive_command.py
"""
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARTER_RAW = "10000000000000000000000000"
RECEIVE_THRESHOLD = "fffffe0000000000"
SRC_HASH = "A" * 64
SRC_HASH2 = "B" * 64


def published_receive_js():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    i = txt.index(" 8. RECEIVE WHAT WAS SENT TO YOU")
    block = txt[i:]
    m = re.search(r"cat > receive\.js <<'EOF'\n(.*?)\nEOF\n", block, re.S)
    return block, (m.group(1) + "\n") if m else None


# Replaces fetch with a fixture node and records every request body to $CALLS.
MOCK = r"""
const fs=require('fs');const fx=JSON.parse(process.env.FIXTURE);
global.fetch=async(url,opt)=>{const b=JSON.parse(opt.body);fs.appendFileSync(process.env.CALLS,JSON.stringify(b)+'\n');
 let out;if(b.action==='receivable')out=fx.receivable;else if(b.action==='account_info')out=fx.account_info;
 else if(b.action==='process')out={hash:'C'.repeat(64)};else out={error:'unexpected '+b.action};
 return {json:async()=>out}};
"""

CHECK = r"""
const n=require('nanocurrency');const [seed,callsFile,expectPrev,expectBal,expectLink,expectRep]=process.argv.slice(2);
const calls=require('fs').readFileSync(callsFile,'utf8').trim().split('\n').map(JSON.parse);
const p=calls.find(c=>c.action==='process');if(!p){console.log(JSON.stringify({ok:false,why:'no process call'}));process.exit()}
const sk=n.deriveSecretKey(seed,0),pk=n.derivePublicKey(sk),me=n.deriveAddress(pk,{useNanoPrefix:true}),b=p.block;
const prev=expectPrev==='null'?'0'.repeat(64):expectPrev;
const hash=n.hashBlock({account:b.account,previous:b.previous,representative:b.representative,balance:b.balance,link:b.link});
console.log(JSON.stringify({ok:true,subtype:p.subtype,account_ok:b.account.split('_')[1]===me.split('_')[1],prev_ok:b.previous===prev,
 bal_ok:b.balance===expectBal,link_ok:b.link===expectLink,rep_ok:b.representative===(expectRep==='self'?me:expectRep),
 sig_ok:n.verifyBlock({hash,signature:b.signature,publicKey:pk}),
 work_ok:n.validateWork({blockHash:expectPrev==='null'?pk:expectPrev,work:b.work,threshold:'fffffe0000000000'}),
 seed_sent:JSON.stringify(calls).includes(seed)}));
"""


class StaticLaws(unittest.TestCase):
    def setUp(self):
        self.block, self.js = published_receive_js()

    def test_command_is_published(self):
        self.assertIsNotNone(self.js, "no `cat > receive.js <<'EOF'` ... EOF in the BEFORE STEP 6 block")
        self.assertIn("read -rs NANO_SEED && export NANO_SEED", self.block)
        self.assertIn("DRY=1 node receive.js", self.block)

    def test_work_is_local_at_the_receive_threshold(self):
        self.assertIn("computeWork", self.js)
        self.assertIn(RECEIVE_THRESHOLD, self.js)
        self.assertNotIn("work_generate", self.js)

    def test_seed_comes_from_the_environment_and_is_never_sent(self):
        self.assertIn("process.env.NANO_SEED", self.js)
        self.assertNotRegex(self.js, r"\b[0-9A-Fa-f]{64}\b")
        self.assertNotRegex(self.block, r"(?i)(send|paste|post|give) (us )?your seed")
        # the only things sent to the node are the request objects built in the script
        for body in re.findall(r"rpc\(\{(.*?)\}\)", self.js):
            self.assertNotIn("seed", body)
            self.assertNotIn("sk", re.findall(r"\b\w+\b", body))

    def test_honest_about_what_was_tested(self):
        flat = " ".join(self.block.split())
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        before6 = txt[txt.index(" BEFORE STEP 6 - "):txt.index("\n STEP 6 - ")]
        self.assertIn("Section 8 below is one tested file that does the receive", before6)
        self.assertIn("It has not yet broadcast a block on mainnet", flat)
        self.assertIn("specs/test_bounties_receive_command.py", flat)


class RunLaws(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("NRE_OFFLINE") == "1":
            raise unittest.SkipTest("NRE_OFFLINE=1")
        if not (shutil.which("npm") and shutil.which("node")):
            raise unittest.SkipTest("npm/node not installed")
        cls.dir = tempfile.mkdtemp()
        try:
            p = subprocess.run(["npm", "i", "nanocurrency@2"], cwd=cls.dir, capture_output=True, text=True, timeout=180)
        except subprocess.TimeoutExpired:
            raise unittest.SkipTest("npm timed out")
        if p.returncode != 0:
            raise unittest.SkipTest("npm install failed: " + p.stderr.strip()[-200:])
        _, js = published_receive_js()
        for name, body in (("receive.js", js), ("mock.js", MOCK), ("check.js", CHECK)):
            with open(os.path.join(cls.dir, name), "w") as f:
                f.write(body)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dir, ignore_errors=True)

    def run_receive(self, fixture, extra_env=None):
        seed = os.urandom(32).hex()
        calls = os.path.join(self.dir, "calls-%s.jsonl" % os.urandom(4).hex())
        env = dict(os.environ, NANO_SEED=seed, FIXTURE=json.dumps(fixture), CALLS=calls, **(extra_env or {}))
        env.pop("NODE_PATH", None)
        p = subprocess.run(["node", "--require", "./mock.js", "receive.js"], cwd=self.dir, env=env,
                           capture_output=True, text=True, timeout=240)
        self.assertEqual(p.returncode, 0, p.stderr[-300:])
        self.assertNotIn(seed, p.stdout + p.stderr)
        return seed, calls, p.stdout

    def check(self, seed, calls, prev, bal, link, rep):
        p = subprocess.run(["node", "check.js", seed, calls, prev, bal, link, rep], cwd=self.dir,
                           capture_output=True, text=True, timeout=60)
        self.assertEqual(p.returncode, 0, p.stderr[-300:])
        return json.loads(p.stdout)

    def test_opens_a_new_account_with_a_valid_block(self):
        fx = {"receivable": {"blocks": {SRC_HASH: {"amount": STARTER_RAW, "source": "nano_x"}}},
              "account_info": {"error": "Account not found"}}
        seed, calls, out = self.run_receive(fx)
        r = self.check(seed, calls, "null", STARTER_RAW, SRC_HASH, "self")
        self.assertEqual(r.pop("subtype"), "open")
        self.assertEqual(r, {"ok": True, "account_ok": True, "prev_ok": True, "bal_ok": True, "link_ok": True,
                             "rep_ok": True, "sig_ok": True, "work_ok": True, "seed_sent": False})
        self.assertIn("balance raw " + STARTER_RAW, out)

    def test_receives_into_an_opened_account(self):
        frontier, rep = "D" * 64, "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
        fx = {"receivable": {"blocks": {SRC_HASH2: STARTER_RAW}},   # the shape without source:true
              "account_info": {"frontier": frontier, "balance": STARTER_RAW, "representative": rep}}
        seed, calls, _ = self.run_receive(fx)
        r = self.check(seed, calls, frontier, str(2 * int(STARTER_RAW)), SRC_HASH2, rep)
        self.assertEqual(r.pop("subtype"), "receive")
        self.assertFalse(r.pop("seed_sent"))
        self.assertTrue(all(r.values()), r)

    def test_nothing_receivable_and_dry_run_broadcast_nothing(self):
        _, calls, out = self.run_receive({"receivable": {"blocks": []}, "account_info": {}})
        self.assertIn("nothing receivable at nano_", out)
        fx = {"receivable": {"blocks": {SRC_HASH: STARTER_RAW}}, "account_info": {"error": "Account not found"}}
        _, calls, out = self.run_receive(fx, {"DRY": "1"})
        with open(calls) as f:
            self.assertNotIn('"process"', f.read())
        self.assertEqual(json.loads(out.splitlines()[0])["link"], SRC_HASH)


if __name__ == "__main__":
    unittest.main(verbosity=2)
