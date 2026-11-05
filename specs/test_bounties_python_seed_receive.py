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


def receive_lines(txt):
    clone = [l.strip() for l in txt.splitlines() if l.strip().startswith("git clone -q " + WALLET_URL)]
    run = [l.strip() for l in txt.splitlines() if "PYTHONPATH=nano-wallet-xno python3 " in l]
    return clone, run


def receive_argv(txt, work):
    """The published receive as an argv tail for `python3`: the seedrecv.py heredoc (written into `work`) run with
    the address, or - on a page from before it - the old one-line `python3 -c`."""
    m = re.search(r"cat > seedrecv\.py <<'EOF'\n(.*?)\nEOF\n", txt, re.S)
    if m:
        with open(os.path.join(work, "seedrecv.py"), "w") as f:
            f.write(m.group(1) + "\n")
        return lambda address, *extra: ["seedrecv.py", address, *extra]
    _, run = receive_lines(txt)
    code = re.search(r'python3 -c "(.*)"$', run[0]).group(1)
    return lambda address, *extra: ["-c", code]


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
        self.step1 = " ".join(self.txt[i:i + 9000].split())

    def test_one_pinned_clone_and_one_run_line(self):
        clone, run = receive_lines(self.txt)
        self.assertEqual(len(clone), 1, clone)
        self.assertIn("checkout -q " + PIN, clone[0])
        self.assertEqual(len(run), 2, run)  # a --dry-run line, then the real one
        self.assertTrue(run[0].endswith("python3 seedrecv.py YOUR_ADDRESS --dry-run"), run)
        self.assertTrue(run[1].endswith("python3 seedrecv.py YOUR_ADDRESS"), run)
        for r in run:
            self.assertIn("NANO_NODE_URL=https://rpc.nano.to", r)
        src = re.search(r"cat > seedrecv\.py <<'EOF'\n(.*?)\nEOF\n", self.txt, re.S).group(1)
        self.assertIn('Server("receive-only")', src)
        self.assertIn('open("nano-seed.txt")', src)
        self.assertIn('PIN = "%s"' % PIN, src)

    def test_no_longer_says_python_path_cannot_receive(self):
        flat = " ".join(self.txt.split())
        self.assertNotIn("the Python wallet in step 1 has no receive of its own yet", flat)
        self.assertNotIn("RECEIVING does, for nano-seed.txt", flat)

    def test_tells_reader_to_check_the_address_and_never_post_the_seed(self):
        for s in ("it refuses, before it signs anything, if nano-seed.txt is not that address's wallet",
                  "post its reply, never the seed",
                  "is trusted for WHAT is receivable and HOW MUCH",
                  "It is NOT trusted for your balance",
                  "refuses unless the new balance is strictly above that block's balance",
                  "against a STUB node only",
                  "With --dry-run it prints each block it would hand over and sends nothing",
                  "payments.py (receive), blocks.py",
                  "It has not yet broadcast a block on mainnet",
                  "a missing nano-seed.txt is an error, never a new key"):
            self.assertIn(s, self.step1)

    def test_section8_points_no_node_readers_to_it(self):
        j = self.txt.index(" 8. RECEIVE WHAT WAS SENT TO YOU")
        s8 = " ".join(self.txt[j:j + 900].split())
        self.assertIn("No node? Step 1's nano-seed.txt has a standard-library receive now", s8)


class EndToEnd(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.wallet, cls.cloned = wallet_dir()
        if cls.wallet is None:
            raise unittest.SkipTest("could not fetch %s at %s (%s) - end-to-end UNKNOWN, not passed"
                                    % (WALLET_URL, PIN, cls.cloned))
        head = subprocess.run(["git", "-C", cls.wallet, "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
        if head != PIN:
            raise unittest.SkipTest("wallet at %s is %s, not the pinned %s" % (cls.wallet, head, PIN))
        txt = page()
        cls.work = tempfile.mkdtemp(prefix="seedrecv-")
        with open(os.path.join(cls.work, "nanokey.py"), "w") as f:
            f.write(nanokey_source(txt))
        out = subprocess.run([sys.executable, "-I", "nanokey.py"], cwd=cls.work, capture_output=True, text=True,
                             check=True).stdout
        cls.address = re.search(r"ADDRESS \(safe to publish\): (nano_\w+)", out).group(1)
        with open(os.path.join(cls.work, "nano-seed.txt")) as f:
            cls.seed_hex = f.read().strip()
        sys.path.insert(0, cls.wallet)
        from ed25519_blake2b import private_key_from_seed
        cls.private_hex = private_key_from_seed(bytes.fromhex(cls.seed_hex), 0).hex()
        sys.path.remove(cls.wallet)

        StubNode.processed = []
        srv = http.server.HTTPServer(("127.0.0.1", 0), StubNode)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        cls.argv = staticmethod(receive_argv(txt, cls.work))
        env = dict(os.environ, NANO_NODE_URL="http://127.0.0.1:%d" % srv.server_address[1],
                   PYTHONPATH=cls.wallet)
        for k in ("NANO_WALLET_KEY_FILE", "NANO_WALLET_PROFILE", "NANO_WALLET_ALLOW_SEND"):
            env.pop(k, None)
        cls.proc = subprocess.run([sys.executable, *cls.argv(cls.address)], cwd=cls.work, env=env,
                                  capture_output=True, text=True, timeout=600)
        srv.shutdown()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(getattr(cls, "work", ""), ignore_errors=True)
        if getattr(cls, "cloned", False) is True:
            shutil.rmtree(os.path.dirname(cls.wallet), ignore_errors=True)

    def test_first_line_is_nanokeys_address(self):
        self.assertEqual(self.proc.returncode, 0, self.proc.stderr)
        self.assertEqual(self.proc.stdout.splitlines()[0], self.address)

    def test_opens_that_account_with_the_sent_block(self):
        self.assertEqual(len(StubNode.processed), 1, StubNode.processed)
        req = StubNode.processed[0]
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
        b = StubNode.processed[0]["block"]
        sk = bytes.fromhex(self.private_hex)
        pk = ed.public_key_from_private(sk)
        self.assertEqual(nanoaddr.encode(pk), self.address)
        rep = nanoaddr.decode(b["representative"])
        h = blocks.block_hash(pk, bytes(32), rep, int(b["balance"]), bytes.fromhex(b["link"]))
        self.assertEqual(b["signature"].upper(), ed.sign(h, sk, pk).hex().upper())

    def test_work_meets_the_receive_threshold(self):
        # Checked here, not by the wallet: blake2b-64(work_le || root) >= 0xfffffe0000000000, root = account key
        import hashlib
        b = StubNode.processed[0]["block"]
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

    def test_missing_seed_file_fails_and_writes_nothing(self):
        empty = tempfile.mkdtemp(prefix="noseed-")
        try:
            argv = self.argv(self.address)
            if argv[0] == "seedrecv.py":
                shutil.copy(os.path.join(self.work, "seedrecv.py"), empty)
            p = subprocess.run([sys.executable, *argv], cwd=empty, capture_output=True, text=True,
                               env=dict(os.environ, NANO_NODE_URL="http://127.0.0.1:9", PYTHONPATH=self.wallet),
                               timeout=60)
            self.assertNotEqual(p.returncode, 0)
            self.assertIn("nano-seed.txt", p.stderr)
            self.assertEqual(sorted(set(os.listdir(empty)) - {"seedrecv.py"}), [])
        finally:
            shutil.rmtree(empty, ignore_errors=True)


class OpenedStub(http.server.BaseHTTPRequestHandler):
    """An ALREADY-OPENED account (frontier F, balance B) with one receivable block of 0.1 XNO. `reported` is the
    balance account_info claims; `forged` makes block_info's contents disagree with F's hash. A hostile node that
    reports 0 for an account holding B gets, from a wallet that trusts it, a block with balance 0.1 on top of F:
    by Nano's rules that is a SEND of B - 0.1 XNO to the link."""
    reported = None
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
            out = {"frontier": f["hash"], "balance": str(OpenedStub.reported), "representative": f["representative"],
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
    balance of the frontier block, read with block_info and checked against the frontier hash."""

    @classmethod
    def setUpClass(cls):
        cls.wallet, cls.cloned = wallet_dir()
        if cls.wallet is None:
            raise unittest.SkipTest("could not fetch %s at %s (%s) - opened-account laws UNKNOWN, not passed"
                                    % (WALLET_URL, PIN, cls.cloned))
        head = subprocess.run(["git", "-C", cls.wallet, "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip()
        if head != PIN:
            raise unittest.SkipTest("wallet at %s is %s, not the pinned %s" % (cls.wallet, head, PIN))
        txt = page()
        cls.work = tempfile.mkdtemp(prefix="seedrecv-open-")
        with open(os.path.join(cls.work, "nanokey.py"), "w") as f:
            f.write(nanokey_source(txt))
        out = subprocess.run([sys.executable, "-I", "nanokey.py"], cwd=cls.work, capture_output=True, text=True,
                             check=True).stdout
        cls.address = re.search(r"ADDRESS \(safe to publish\): (nano_\w+)", out).group(1)
        cls.argv = staticmethod(receive_argv(txt, cls.work))
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

    def run_against(self, reported, *extra, forged=False, address=None):
        OpenedStub.reported, OpenedStub.forged, OpenedStub.frontier = reported, forged, self.frontier
        OpenedStub.seen, OpenedStub.processed = [], []
        srv = http.server.HTTPServer(("127.0.0.1", 0), OpenedStub)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        env = dict(os.environ, NANO_NODE_URL="http://127.0.0.1:%d" % srv.server_address[1], PYTHONPATH=self.wallet)
        for k in ("NANO_WALLET_KEY_FILE", "NANO_WALLET_PROFILE", "NANO_WALLET_ALLOW_SEND"):
            env.pop(k, None)
        try:
            return subprocess.run([sys.executable, *self.argv(address or self.address, *extra)], cwd=self.work,
                                  env=env, capture_output=True, text=True, timeout=600)
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

    def test_an_honest_node_gets_a_receive_on_top_of_the_frontier(self):
        p = self.run_against(HELD_RAW)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(len(OpenedStub.processed), 1, OpenedStub.processed)
        req = OpenedStub.processed[0]
        self.assertEqual(req["block"]["previous"], self.frontier["hash"])
        self.assertEqual(int(req["block"]["balance"]), HELD_RAW + int(AMOUNT_RAW))
        self.assertEqual(req.get("subtype"), "receive")

    def test_dry_run_prints_the_block_and_sends_nothing(self):
        p = self.run_against(HELD_RAW, "--dry-run")
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(OpenedStub.processed, [], "--dry-run broadcast a block")
        self.assertIn("DRY RUN, not sent:", p.stdout)
        self.assertIn('"balance": "%d"' % (HELD_RAW + int(AMOUNT_RAW)), p.stdout)

    def test_a_seed_that_is_not_the_given_address_is_refused_before_the_node_is_asked(self):
        p = self.run_against(HELD_RAW, address=BURN)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("refused", p.stderr)
        self.assertEqual(OpenedStub.seen, [], "the node was asked before the address was checked")


if __name__ == "__main__":
    unittest.main()
