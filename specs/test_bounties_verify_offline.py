#!/usr/bin/env python3
"""Laws for the offline block checker in bounties.txt section 7 (challenge #79).

Found 2026-10-01. A verifier agent (hermessol, Moltbook, 19:13 and 19:17 UTC) declined to check our claims because it
had "no instrument that can read a Nano ledger": its only reader is one Solana RPC. Every proof step we published
was one node's word (rpc.nano.to block_info), so a careful stranger had nothing that shares no code with us. Section 7
publishes a stdlib-only checker that recomputes a state block's hash and verifies its ed25519/blake2b signature, so
the node can no longer lie about a block's contents. These laws run the checker exactly as published, against two
real blocks saved from the public ledger (ARION's 0.0005 XNO send to the treasury and the block before it).

Run: python3 specs/test_bounties_verify_offline.py
"""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
FIX = os.path.join(ROOT, "specs", "fixtures")
SEND = "B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F"
PREV = "37402FF0B0E37BF00EA892C078BF46F1FD6D3A79650327EB1B64CAA87E197DD4"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"


def published_checker():
    txt = open(BOUNTIES, encoding="utf-8").read()
    m = re.search(r"cat > nanoverify\.py <<'EOF'\n(.*?)\nEOF\n", txt, re.S)
    if not m:
        raise AssertionError("bounties.txt has no `cat > nanoverify.py <<'EOF'` block")
    return txt, m.group(1)


class OfflineChecker(unittest.TestCase):
    def setUp(self):
        self.txt, code = published_checker()
        self.dir = tempfile.mkdtemp()
        self.script = os.path.join(self.dir, "nanoverify.py")
        with open(self.script, "w") as f:
            f.write(code + "\n")
        self.send = os.path.join(FIX, "blk_%s.json" % SEND)
        self.prev = os.path.join(FIX, "blk_%s.json" % PREV)

    def run_checker(self, *args):
        return subprocess.run([sys.executable, self.script] + list(args), capture_output=True, text=True, timeout=60)

    def tampered(self, field, fn):
        b = json.load(open(self.send))
        b["contents"][field] = fn(b["contents"][field])
        path = os.path.join(self.dir, "bad_%s.json" % field)
        with open(path, "w") as f:
            json.dump(b, f)
        return path

    def test_stdlib_only(self):
        _, code = published_checker()
        mods = set()
        for line in code.splitlines():
            m = re.match(r"\s*import (.+)", line)
            if m:
                mods.update(x.strip() for x in m.group(1).split(","))
            self.assertNotRegex(line, r"^\s*from \S+ import", "no from-imports: stdlib hashlib/json/sys only")
        self.assertEqual(mods, {"hashlib", "json", "sys"})

    def test_real_payment_verifies_with_exact_amount(self):
        r = self.run_checker(SEND, self.send, self.prev)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("OK %s is signed by nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr" % SEND, r.stdout)
        self.assertIn("= account " + TREASURY, r.stdout)
        self.assertIn("OK previous " + PREV, r.stdout)
        self.assertIn("balance moved by -500000000000000000000000000 raw", r.stdout)

    def test_changed_balance_fails(self):
        r = self.run_checker(SEND, self.tampered("balance", lambda v: str(int(v) + 1)))
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL", r.stderr)

    def test_changed_balance_fails_even_without_expected_hash(self):
        r = self.run_checker("", self.tampered("balance", lambda v: str(int(v) + 1)))
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL: signature", r.stderr)

    def test_redirected_link_fails(self):
        r = self.run_checker("", self.tampered("link", lambda v: v[:-1] + ("0" if v[-1] != "0" else "1")))
        self.assertEqual(r.returncode, 1)

    def test_changed_signature_fails(self):
        r = self.run_checker(SEND, self.tampered("signature", lambda v: v[:10] + ("0" if v[10] != "0" else "1") + v[11:]))
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL: signature", r.stderr)

    def test_wrong_hash_fails(self):
        r = self.run_checker(PREV, self.send)
        self.assertEqual(r.returncode, 1)
        self.assertIn("FAIL: these contents hash to " + SEND, r.stderr)

    def test_wrong_previous_fails(self):
        r = self.run_checker(SEND, self.send, self.send)
        self.assertEqual(r.returncode, 1)

    def test_published_commands_name_the_fixture_blocks(self):
        sec = self.txt[self.txt.index(" 7. CHECK ANY NANO CLAIM"):]
        self.assertIn("python3 nanoverify.py " + SEND, sec)
        self.assertIn(PREV, sec)
        self.assertIn("500000000000000000000000000 raw (0.0005 XNO)", sec)
        step4 = self.txt[self.txt.index(" STEP 4 -"):self.txt.index(" STEP 5 -")]
        self.assertIn("Section 7", step4)


if __name__ == "__main__":
    unittest.main(verbosity=2)
