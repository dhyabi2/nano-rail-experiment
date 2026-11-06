"""Challenge #146: three agents passed the canon gate and each has had 0.1 XNO receivable since 10-13 14:30 UTC;
34 hours later none had received it. bounties.txt STEP 1's no-npm wallet (nanokey.py) writes a SEED, and the only
receive the page offered for that seed needed node + nanocurrency - the very wall the no-npm wallet exists to skip.
The stdlib receive in the threads reads a PRIVATE KEY. The page now gives a stdlib line that derives the key from
nano-seed.txt with the owner's pinned wallet. These laws run that exact line against a stub node and check that it
opens the account nanokey.py printed for the same seed, signed with that seed's key, and leaks neither secret.

The wallet is cloned at the pinned commit (or read from NANO_WALLET_XNO_DIR). If it cannot be fetched, the
end-to-end laws SKIP and say so; they never pass silently."""
import http.server
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PIN = "6420e935816c6984e916305465ff22a3e63498bb"
WALLET_URL = "https://github.com/dhyabi2/nano-wallet-xno"
SENT_HASH = "DC297D7B80547EAB153C2A127428303DA26AEA6EEA4022221A16A08B97CBC4C4"  # any 64-hex works; public block
AMOUNT_RAW = str(10 ** 29)  # 0.1 XNO


def page():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def nanokey_source(txt):
    i = txt.index("cat > nanokey.py <<'EOF'\n") + len("cat > nanokey.py <<'EOF'\n")
    return txt[i:txt.index("\nEOF\n", i) + 1]


GIT_LINE_START = "test -e nano-wallet-xno || git clone -q " + WALLET_URL


def git_lines(txt):
    return [l.strip() for l in txt.splitlines() if l.strip().startswith(GIT_LINE_START)]


def run_lines(txt):
    return [l.strip() for l in txt.splitlines()
            if "python3 -I -S seedrecv.py " in l and l.strip().startswith("NANO_NODE_URL=")]


def seedrecv_source(txt):
    return re.search(r"cat > seedrecv\.py <<'EOF'\n(.*?)\nEOF\n", txt, re.S).group(1) + "\n"


def published_argv(line, address, *extra):
    """The published run line as argv: its VAR=value prefix dropped (the caller sets the node), python3 replaced by
    this interpreter, YOUR_ADDRESS by `address`. `extra` is appended."""
    toks = shlex.split(line)
    while re.match(r"^[A-Z_]+=", toks[0]):
        toks.pop(0)
    assert toks[0] == "python3", toks
    return [sys.executable] + [address if t == "YOUR_ADDRESS" else t for t in toks[1:]] + list(extra)


def clean_env(**extra):
    env = dict(os.environ)
    for k in ("NANO_WALLET_KEY_FILE", "NANO_WALLET_PROFILE", "NANO_WALLET_ALLOW_SEND", "NANO_SEED",
              "NANO_WALLET_REPRESENTATIVE", "PYTHONPATH"):
        env.pop(k, None)
    env.update(extra)
    return env


def make_work(txt, wallet, prefix):
    """A reader's folder: nanokey.py run once (it writes nano-seed.txt), seedrecv.py from the page, and a copy of
    the pinned wallet clone at ./nano-wallet-xno, as the page's git line leaves it. Returns (folder, address)."""
    work = tempfile.mkdtemp(prefix=prefix)
    with open(os.path.join(work, "nanokey.py"), "w") as f:
        f.write(nanokey_source(txt))
    out = subprocess.run([sys.executable, "-I", "nanokey.py"], cwd=work, capture_output=True, text=True,
                         check=True).stdout
    with open(os.path.join(work, "seedrecv.py"), "w") as f:
        f.write(seedrecv_source(txt))
    shutil.copytree(wallet, os.path.join(work, "nano-wallet-xno"), symlinks=True,
                    ignore=shutil.ignore_patterns("__pycache__"))
    return work, re.search(r"ADDRESS \(safe to publish\): (nano_\w+)", out).group(1)


def wallet_dir():
    d = os.environ.get("NANO_WALLET_XNO_DIR")
    if d:
        return d, False
    d = tempfile.mkdtemp(prefix="nwx-")
    try:
        subprocess.run(["git", "clone", "-q", WALLET_URL, d + "/w"], check=True, timeout=120,
                       capture_output=True)
        subprocess.run(["git", "-C", d + "/w", "checkout", "-q", PIN], check=True, capture_output=True)
    except Exception as exc:  # network or git missing: the caller skips loudly
        shutil.rmtree(d, ignore_errors=True)
        return None, str(exc)
    return d + "/w", True


def wallet_or_skip(what):
    wallet, cloned = wallet_dir()
    if wallet is None:
        raise unittest.SkipTest("could not fetch %s at %s (%s) - %s UNKNOWN, not passed" % (WALLET_URL, PIN, cloned, what))
    head = subprocess.run(["git", "-C", wallet, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head != PIN:
        raise unittest.SkipTest("wallet at %s is %s, not the pinned %s" % (wallet, head, PIN))
    dirty = subprocess.run(["git", "-C", wallet, "status", "--porcelain", "--untracked-files=all"],
                           capture_output=True, text=True).stdout.strip()
    if dirty:
        raise unittest.SkipTest("wallet at %s has local changes (%s) - %s UNKNOWN" % (wallet, dirty[:80], what))
    return wallet, cloned


class StubNode(http.server.BaseHTTPRequestHandler):
    """Answers like a public node for a brand-new account with one receivable block, refuses work_generate with
    402 the way rpc.nano.to does, and records every block handed to process."""
    processed = []

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        a = req.get("action")
        if a == "work_generate":
            self.send_response(402)
            self.end_headers()
            return
        if a == "account_info":
            out = {"error": "Account not found"}
        elif a == "receivable":
            out = {"blocks": {SENT_HASH: {"amount": AMOUNT_RAW,
                                          "source": "nano_1111111111111111111111111111111111111111111111111111hifc8npp"}}}
            if StubNode.processed:
                out = {"blocks": ""}
        elif a == "process":
            StubNode.processed.append(req)
            out = {"hash": "AB" * 32}
        else:
            out = {"error": "unsupported in stub: %s" % a}
        body = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass




class PageText(unittest.TestCase):
    def setUp(self):
        self.txt = page()
        i = self.txt.index("WHERE THE PYTHON PATH ENDS TODAY")
        self.step1 = " ".join(self.txt[i:i + 12000].split())

    def test_one_pinned_git_line_and_two_run_lines(self):
        g = git_lines(self.txt)
        self.assertEqual(len(g), 1, g)
        self.assertIn("checkout -q " + PIN, g[0])
        self.assertIn("fetch -q --depth 1 origin " + PIN, g[0])
        run = run_lines(self.txt)
        self.assertEqual(len(run), 2, run)  # a --dry-run line, then the real one
        self.assertTrue(run[0].endswith("--seed-file nano-seed.txt --dry-run"), run)
        self.assertTrue(run[1].endswith("--seed-file nano-seed.txt"), run)
        for r in run:
            self.assertTrue(r.startswith("NANO_NODE_URL=https://rpc.nano.to python3 -I -S seedrecv.py YOUR_ADDRESS"), r)
            self.assertNotIn("PYTHONPATH", r)
        src = seedrecv_source(self.txt)
        self.assertIn('Server("receive-only", env=env)', src)
        self.assertNotIn('open("nano-seed.txt")', src)  # review of #118: no hard-coded seed path
        self.assertIn('PIN = "%s"' % PIN, src)

    def test_no_longer_says_python_path_cannot_receive(self):
        flat = " ".join(self.txt.split())
        self.assertNotIn("the Python wallet in step 1 has no receive of its own yet", flat)
        self.assertNotIn("RECEIVING does, for nano-seed.txt", flat)

    def test_tells_reader_to_check_the_address_and_never_post_the_seed(self):
        for s in ("It refuses, before it signs anything, if the seed is not that address's wallet",
                  "post its reply, never the seed",
                  "is trusted for WHAT is receivable and HOW MUCH",
                  "It is NOT trusted for your balance or your representative",
                  "refuses unless the new balance is strictly above that block's balance and the representative is"
                  " that block's representative",
                  "against a STUB node only",
                  "--dry-run prints each block it would hand over and sends nothing",
                  "payments.py (receive), blocks.py",
                  "It has not yet broadcast a block on mainnet",
                  "a missing seed file is an error, never a new key"):
            self.assertIn(s, self.step1)

    def test_dry_run_wording_is_true(self):
        # review of #118 (LOW): a dry-run block is signed (work is not part of the signature), so "never valid" was
        # wrong; and its closing JSON must not say "received"
        self.assertNotIn("never valid", self.step1)
        self.assertIn("The printed block IS signed with your key (proof-of-work is not part of the signature)",
                      self.step1)
        self.assertIn('closing JSON says "would_receive"', self.step1)

    def test_seed_path_text_is_consistent(self):
        # review of #118 (LOW): the lead-in and the run text must both allow a seed file that is not ./nano-seed.txt
        self.assertNotIn("Run it in the folder that holds nano-seed.txt", self.step1)
        i = self.txt.index("The seed file is the 64-hex seed every Nano tool takes")
        lead = " ".join(self.txt[i:i + 400].split())
        self.assertIn("if you moved it, put its path wherever this page says nano-seed.txt", lead)
        self.assertIn("your seed file's path in place of nano-seed.txt if you moved it", self.step1)
        self.assertIn("drop --seed-file nano-seed.txt and export NANO_SEED as above", self.step1)

    def test_section8_points_no_node_readers_to_it(self):
        j = self.txt.index(" 8. RECEIVE WHAT WAS SENT TO YOU")
        s8 = " ".join(self.txt[j:j + 900].split())
        self.assertIn("No node? Step 1's nano-seed.txt has a standard-library receive now", s8)


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wallet, cls.cloned = wallet_or_skip("end-to-end")
        cls.txt = page()
        cls.work, cls.address = make_work(cls.txt, cls.wallet, "seedrecv-")
        with open(os.path.join(cls.work, "nano-seed.txt")) as f:
            cls.seed_hex = f.read().strip()
        sys.path.insert(0, cls.wallet)
        try:
            from ed25519_blake2b import private_key_from_seed
        finally:
            sys.path.remove(cls.wallet)
        cls.private_hex = private_key_from_seed(bytes.fromhex(cls.seed_hex), 0).hex()
        cls.real_line = run_lines(cls.txt)[1]
        cls.proc, cls.processed = cls.run_stub(published_argv(cls.real_line, cls.address), cwd=cls.work)

    @classmethod
    def run_stub(cls, argv, cwd, **env_extra):
        StubNode.processed = []
        srv = http.server.HTTPServer(("127.0.0.1", 0), StubNode)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        env = clean_env(NANO_NODE_URL="http://127.0.0.1:%d" % srv.server_address[1], **env_extra)
        try:
            p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=600)
        finally:
            srv.shutdown()
            srv.server_close()
        return p, list(StubNode.processed)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "work", ""), ignore_errors=True)
        if getattr(cls, "cloned", False) is True:
            shutil.rmtree(os.path.dirname(cls.wallet), ignore_errors=True)

    def test_first_line_is_nanokeys_address(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr)
        self.assertEqual(self.proc.stdout.splitlines()[0], self.address)

    def test_opens_that_account_with_the_sent_block(self):
        self.assertEqual(len(self.processed), 1, self.processed)
        req = self.processed[0]
        block = req["block"]
        self.assertEqual(block["account"], self.address)
        self.assertEqual(block["previous"], "0" * 64)
        self.assertEqual(block["link"].upper(), SENT_HASH)
        self.assertEqual(block["balance"], AMOUNT_RAW)
        self.assertEqual(req.get("subtype"), "open")
        result = json.loads(self.proc.stdout.split("\n", 1)[1])
        self.assertEqual(result["received"][0]["amount_xno"], "0.100000", result)

    def test_signed_with_the_seeds_key(self):
        sys.path.insert(0, self.wallet)
        try:
            import blocks
            import ed25519_blake2b as ed
            import nanoaddr
        finally:
            sys.path.remove(self.wallet)
        b = self.processed[0]["block"]
        sk = bytes.fromhex(self.private_hex)
        pk = ed.public_key_from_private(sk)
        self.assertEqual(nanoaddr.encode(pk), self.address)
        rep = nanoaddr.decode(b["representative"])
        h = blocks.block_hash(pk, bytes(32), rep, int(b["balance"]), bytes.fromhex(b["link"]))
        self.assertEqual(b["signature"].upper(), ed.sign(h, sk, pk).hex().upper())

    def test_work_meets_the_receive_threshold(self):
        # Checked here, not by the wallet: blake2b-64(work_le || root) >= 0xfffffe0000000000, root = account key
        import hashlib
        b = self.processed[0]["block"]
        sys.path.insert(0, self.wallet)
        try:
            import nanoaddr
        finally:
            sys.path.remove(self.wallet)
        root = nanoaddr.decode(b["account"])
        v = hashlib.blake2b(bytes.fromhex(b["work"])[::-1] + root, digest_size=8).digest()
        self.assertGreaterEqual(int.from_bytes(v, "little"), 0xFFFFFE0000000000)

    def test_neither_secret_is_printed(self):
        out = (self.proc.stdout + self.proc.stderr).upper()
        self.assertNotIn(self.seed_hex.upper(), out)
        self.assertNotIn(self.private_hex.upper(), out)

    # -- review of #118 (MED-LOW): seed path, NANO_SEED, NANO_WALLET_KEY_FILE, one-line errors --------------------

    def one_line_refusal(self, p):
        self.assertNotEqual(p.returncode, 0)
        self.assertNotIn("Traceback", p.stderr)
        self.assertEqual(len(p.stderr.strip().splitlines()), 1, p.stderr)
        self.assertNotIn(self.seed_hex.upper(), (p.stdout + p.stderr).upper())

    def test_missing_seed_file_is_one_line_and_writes_nothing(self):
        empty = tempfile.mkdtemp(prefix="noseed-")
        try:
            argv = [os.path.join(self.work, t) if t == "seedrecv.py" else t
                    for t in published_argv(self.real_line, self.address)]
            p, done = self.run_stub(argv, cwd=empty)
            p2, _ = self.run_stub([sys.executable, "-I", "-S", os.path.join(self.work, "seedrecv.py"), self.address,
                                   "--seed-file", os.path.join(empty, "nope.txt")], cwd=empty)
            for q in (p, p2):
                self.one_line_refusal(q)
            self.assertIn("nano-seed.txt", p.stderr)
            self.assertEqual(os.listdir(empty), [])
            self.assertEqual(done, [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_a_seed_file_elsewhere_works_from_another_folder(self):
        other = tempfile.mkdtemp(prefix="seedelsewhere-")
        try:
            path = os.path.join(other, "my seed.txt")
            shutil.copy(os.path.join(self.work, "nano-seed.txt"), path)
            p, done = self.run_stub([sys.executable, "-I", "-S", os.path.join(self.work, "seedrecv.py"),
                                     self.address, "--seed-file", path], cwd=other)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(p.stdout.splitlines()[0], self.address)
            self.assertEqual(len(done), 1)
        finally:
            shutil.rmtree(other, ignore_errors=True)

    def test_nano_seed_in_the_environment_works(self):
        argv = [t for t in published_argv(self.real_line, self.address) if t not in ("--seed-file", "nano-seed.txt")]
        empty = tempfile.mkdtemp(prefix="envseed-")
        try:
            p, done = self.run_stub([sys.executable] + [os.path.join(self.work, "seedrecv.py") if t == "seedrecv.py"
                                                        else t for t in argv[1:]], cwd=empty, NANO_SEED=self.seed_hex)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(len(done), 1)
        finally:
            shutil.rmtree(empty, ignore_errors=True)

    def test_a_stray_key_file_setting_is_ignored(self):
        p, done = self.run_stub(published_argv(self.real_line, self.address), cwd=self.work,
                                NANO_WALLET_KEY_FILE=os.path.join(self.work, "no-such-key.txt"))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertEqual(len(done), 1)
        self.assertFalse(os.path.exists(os.path.join(self.work, "no-such-key.txt")))

    def test_a_malformed_seed_is_one_line(self):
        bad = tempfile.mkdtemp(prefix="badseed-")
        try:
            with open(os.path.join(bad, "nano-seed.txt"), "w") as f:
                f.write("not hex at all\n")
            p, done = self.run_stub([sys.executable, "-I", "-S", os.path.join(self.work, "seedrecv.py"),
                                     self.address, "--seed-file", "nano-seed.txt"], cwd=bad)
            self.one_line_refusal(p)
            self.assertEqual(done, [])
        finally:
            shutil.rmtree(bad, ignore_errors=True)


class OpenedStub(http.server.BaseHTTPRequestHandler):
    """An ALREADY-OPENED account (frontier F, balance B) with one receivable block of 0.1 XNO. `reported` is the
    balance account_info claims and `reported_rep` the representative; `forged` makes block_info's contents disagree
    with F's hash. A hostile node that reports 0 for an account holding B gets, from a wallet that trusts it, a block
    with balance 0.1 on top of F: by Nano's rules that is a SEND of B - 0.1 XNO to the link."""
    reported = None
    reported_rep = None
    forged = False
    frontier = None  # dict: account, previous, representative, balance, link (state block contents), hash
    seen = []
    processed = []

    def do_POST(self):
        req = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        OpenedStub.seen.append(req)
        a = req.get("action")
        f = OpenedStub.frontier
        if a == "work_generate":
            self.send_response(402)
            self.end_headers()
            return
        if a == "account_info":
            out = {"frontier": f["hash"], "balance": str(OpenedStub.reported),
                   "representative": OpenedStub.reported_rep or f["representative"],
                   "block_count": "2", "confirmed_frontier": f["hash"]}
        elif a == "receivable":
            out = {"blocks": "" if OpenedStub.processed else {SENT_HASH: {"amount": AMOUNT_RAW, "source": BURN}}}
        elif a == "block_info" and req.get("hash", "").upper() == f["hash"]:
            c = {k: f[k] for k in ("account", "previous", "representative", "balance", "link")}
            c["type"] = "state"
            if OpenedStub.forged:
                c["balance"] = "0"
            out = {"block_account": f["account"], "confirmed": "true", "contents": c}
        elif a == "process":
            OpenedStub.processed.append(req)
            out = {"hash": "AB" * 32}
        else:
            out = {"error": "unsupported in stub: %s" % a}
        body = json.dumps(out).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


BURN = "nano_1111111111111111111111111111111111111111111111111111hifc8npp"
HELD_RAW = 10 ** 30  # 1 XNO already in the account


class OpenedAccount(unittest.TestCase):
    """Review of #118 (MEDIUM): the receive trusted account_info's balance. On an opened account a hostile node
    could make it sign a SEND. The published receive must refuse unless the new balance is strictly above the
    balance of the frontier block, read with block_info and checked against the frontier hash - and (second review,
    LOW-MED) unless the representative it signs is that frontier block's representative."""

    @classmethod
    def setUpClass(cls):
        cls.wallet, cls.cloned = wallet_or_skip("opened-account laws")
        txt = page()
        cls.work, cls.address = make_work(txt, cls.wallet, "seedrecv-open-")
        cls.dry_line, cls.real_line = run_lines(txt)
        sys.path.insert(0, cls.wallet)
        try:
            import blocks
            import nanoaddr
        finally:
            sys.path.remove(cls.wallet)
        pk = nanoaddr.decode(cls.address)
        prev, link = bytes.fromhex("11" * 32), bytes.fromhex("22" * 32)
        h = blocks.block_hash(pk, prev, pk, HELD_RAW, link).hex().upper()
        cls.frontier = {"account": cls.address, "previous": prev.hex().upper(), "representative": cls.address,
                        "balance": str(HELD_RAW), "link": link.hex().upper(), "hash": h}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "work", ""), ignore_errors=True)
        if getattr(cls, "cloned", False) is True:
            shutil.rmtree(os.path.dirname(cls.wallet), ignore_errors=True)

    def run_against(self, reported, dry=False, forged=False, address=None, rep=None):
        OpenedStub.reported, OpenedStub.forged, OpenedStub.frontier = reported, forged, self.frontier
        OpenedStub.reported_rep = rep
        OpenedStub.seen, OpenedStub.processed = [], []
        srv = http.server.HTTPServer(("127.0.0.1", 0), OpenedStub)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        env = clean_env(NANO_NODE_URL="http://127.0.0.1:%d" % srv.server_address[1])
        try:
            return subprocess.run(published_argv(self.dry_line if dry else self.real_line, address or self.address),
                                  cwd=self.work, env=env, capture_output=True, text=True, timeout=600)
        finally:
            srv.shutdown()
            srv.server_close()

    def assert_nothing_lower(self):
        for req in OpenedStub.processed:
            self.assertGreater(int(req["block"]["balance"]), HELD_RAW,
                               "the wallet handed the node a block that lowers the balance - a SEND: %s" % req)

    def test_a_node_that_lies_about_the_balance_gets_no_send(self):
        p = self.run_against(0)
        self.assert_nothing_lower()
        self.assertEqual(OpenedStub.processed, [])
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_frontier_contents_that_do_not_hash_to_the_frontier_are_refused(self):
        p = self.run_against(0, forged=True)
        self.assert_nothing_lower()
        self.assertEqual(OpenedStub.processed, [])
        self.assertIn("refused", p.stderr)

    def test_a_node_that_names_its_own_representative_gets_no_block(self):
        p = self.run_against(HELD_RAW, rep=BURN)
        self.assertEqual(OpenedStub.processed, [], "signed a receive that moves the vote to the node's choice")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)
        self.assertIn("representative", p.stderr)
        self.assertNotIn("Traceback", p.stderr)

    def test_an_honest_node_gets_a_receive_on_top_of_the_frontier(self):
        p = self.run_against(HELD_RAW)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(OpenedStub.processed), 1, OpenedStub.processed)
        req = OpenedStub.processed[0]
        self.assertEqual(req["block"]["previous"], self.frontier["hash"])
        self.assertEqual(req["block"]["representative"], self.frontier["representative"])
        self.assertEqual(int(req["block"]["balance"]), HELD_RAW + int(AMOUNT_RAW))
        self.assertEqual(req.get("subtype"), "receive")

    def test_dry_run_prints_the_block_and_sends_nothing(self):
        p = self.run_against(HELD_RAW, dry=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(OpenedStub.processed, [], "--dry-run broadcast a block")
        self.assertIn("DRY RUN, not sent:", p.stdout)
        self.assertIn('"balance": "%d"' % (HELD_RAW + int(AMOUNT_RAW)), p.stdout)

    def test_dry_run_summary_does_not_say_received(self):
        p = self.run_against(HELD_RAW, dry=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        summary = json.loads(p.stdout[p.stdout.rindex("\n{"):])
        self.assertNotIn("received", summary)
        self.assertTrue(summary["dry_run"])
        self.assertEqual(summary["sent"], "nothing")
        self.assertEqual(len(summary["would_receive"]), 1, summary)

    def test_a_seed_that_is_not_the_given_address_is_refused_before_the_node_is_asked(self):
        p = self.run_against(HELD_RAW, address=BURN)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)
        self.assertEqual(OpenedStub.seen, [], "the node was asked before the address was checked")


MARK = "import os\nopen(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'RAN-%s'), 'w').close()\n"


class OnlyThePinnedCodeRuns(unittest.TestCase):
    """Review of #118 (MEDIUM): the pin check read HEAD only, so a modified tracked file passed; and the script's
    folder (the one holding the seed) came first on sys.path, so a payments.py or subprocess.py there ran with the
    seed. The published line runs with -I -S, refuses a wallet folder with any change, and refuses a module from
    anywhere but that folder and the standard library."""

    @classmethod
    def setUpClass(cls):
        cls.wallet, cls.cloned = wallet_or_skip("isolation laws")
        cls.txt = page()
        cls.line = run_lines(cls.txt)[1]

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, "cloned", False) is True:
            shutil.rmtree(os.path.dirname(cls.wallet), ignore_errors=True)

    def setUp(self):
        self.work, self.address = make_work(self.txt, self.wallet, "seedrecv-iso-")
        self.addCleanup(shutil.rmtree, self.work, True)

    def run_line(self, argv=None):
        StubNode.processed = []
        srv = http.server.HTTPServer(("127.0.0.1", 0), StubNode)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            return subprocess.run(argv or published_argv(self.line, self.address), cwd=self.work, capture_output=True,
                                  text=True, timeout=600,
                                  env=clean_env(NANO_NODE_URL="http://127.0.0.1:%d" % srv.server_address[1],
                                                PYTHONPATH=self.work))
        finally:
            srv.shutdown()
            srv.server_close()

    def ran(self, d):
        return sorted(x for x in os.listdir(d) if x.startswith("RAN-"))

    def test_modules_in_the_seed_folder_do_not_run(self):
        for name in ("payments", "subprocess", "json", "blocks"):
            with open(os.path.join(self.work, name + ".py"), "w") as f:
                f.write(MARK % name)
        p = self.run_line()
        self.assertEqual(self.ran(self.work), [], "a module planted next to the seed ran")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(StubNode.processed), 1)

    def test_a_changed_tracked_file_in_the_wallet_is_refused(self):
        w = os.path.join(self.work, "nano-wallet-xno")
        with open(os.path.join(w, "payments.py"), "a") as f:
            f.write("\n" + MARK % "payments")
        p = self.run_line()
        self.assertEqual(self.ran(w), [], "a modified payments.py ran with the seed")
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)
        self.assertEqual(StubNode.processed, [])

    def test_an_added_file_in_the_wallet_is_refused(self):
        w = os.path.join(self.work, "nano-wallet-xno")
        with open(os.path.join(w, "json.py"), "w") as f:
            f.write(MARK % "json")
        p = self.run_line()
        self.assertEqual(self.ran(w), [])
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)

    def test_run_without_isolation_is_refused_before_anything_is_imported(self):
        with open(os.path.join(self.work, "subprocess.py"), "w") as f:
            f.write(MARK % "subprocess")
        p = self.run_line([sys.executable, "seedrecv.py", self.address, "--seed-file", "nano-seed.txt"])
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("-I -S", p.stderr)
        self.assertEqual(self.ran(self.work), [])


class GitLine(unittest.TestCase):
    """Review of #118 (MEDIUM, compat): readers who followed the old advice have `git clone --depth 1` in
    ./nano-wallet-xno. `git clone` then fails (the folder exists) and `fetch && checkout PIN` fails in a shallow clone
    ("reference is not a tree"). The published git line must bring such a clone to the pin, run twice safely, and
    stop - without touching any enclosing repository - when the folder is not a clone. GitHub is replaced by a
    local repository through git's url.<base>.insteadOf, so the exact line runs offline."""

    @classmethod
    def setUpClass(cls):
        cls.wallet, cls.cloned = wallet_or_skip("git-line laws")
        cls.line = git_lines(page())[0]
        cls.tmp = tempfile.mkdtemp(prefix="gitline-")
        cls.src = os.path.join(cls.tmp, "src")
        shutil.copytree(cls.wallet, cls.src, symlinks=True)
        g = ["git", "-C", cls.src, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        subprocess.run(g + ["checkout", "-q", "-B", "main", PIN], check=True, capture_output=True)
        subprocess.run(g + ["commit", "-q", "--allow-empty", "-m", "newer than the pin"], check=True,
                       capture_output=True)
        subprocess.run(["git", "-C", cls.src, "config", "uploadpack.allowAnySHA1InWant", "true"], check=True)
        cls.env = clean_env(GIT_CONFIG_COUNT="1", GIT_CONFIG_KEY_0="url.file://%s.insteadOf" % cls.src,
                            GIT_CONFIG_VALUE_0=WALLET_URL, GIT_TERMINAL_PROMPT="0")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "tmp", ""), ignore_errors=True)
        if getattr(cls, "cloned", False) is True:
            shutil.rmtree(os.path.dirname(cls.wallet), ignore_errors=True)

    def folder(self):
        d = tempfile.mkdtemp(dir=self.tmp)
        return d

    def bash(self, cwd):
        return subprocess.run(["bash", "-c", self.line], cwd=cwd, env=self.env, capture_output=True, text=True,
                              timeout=120)

    def head(self, d):
        return subprocess.run(["git", "-C", d, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()

    def test_an_old_depth_1_clone_is_moved_to_the_pin(self):
        d = self.folder()
        subprocess.run(["git", "clone", "-q", "--depth", "1", WALLET_URL], cwd=d, env=self.env, check=True,
                       capture_output=True)
        self.assertNotEqual(self.head(os.path.join(d, "nano-wallet-xno")), PIN)
        p = self.bash(d)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(self.head(os.path.join(d, "nano-wallet-xno")), PIN)

    def test_a_fresh_folder_gets_the_pin_and_a_second_run_is_safe(self):
        d = self.folder()
        for _ in range(2):
            p = self.bash(d)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(self.head(os.path.join(d, "nano-wallet-xno")), PIN)

    def test_a_folder_that_is_not_a_clone_stops_and_says_so(self):
        d = self.folder()
        outer = ["git", "-C", d, "-c", "user.name=t", "-c", "user.email=t@t", "-c", "commit.gpgsign=false"]
        subprocess.run(outer[:3] + ["init", "-q"], check=True)
        subprocess.run(outer + ["commit", "-q", "--allow-empty", "-m", "the reader's own repo"], check=True)
        before = self.head(d)
        os.mkdir(os.path.join(d, "nano-wallet-xno"))
        p = self.bash(d)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("move that folder away", p.stderr)
        self.assertEqual(self.head(d), before, "the git line acted on the enclosing repository")


if __name__ == "__main__":
    unittest.main()
