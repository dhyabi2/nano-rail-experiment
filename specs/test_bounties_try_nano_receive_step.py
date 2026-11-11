#!/usr/bin/env python3
"""Law for try-nano's step 3, the receive (challenge #253).

Measured 12:2x UTC 2026-11-11: GET https://getunstuck.space/unstuck/api/try-nano (13 outside clients by 12:00 that
day) tells a starter's payee to pocket it with opener/nano-x402-client.js or `opener/nano-receive.py --seed <64hex>`
from "the network repository", with no URL. Both default to https://pursekeeper.dev (not ours; no answer from us at
12:2x). nano-receive.py's fallback when the work call fails is `compute_work_local`, whose loop accepts the first
nonce whose 4-byte prefix is BELOW 0xfffffff8, so it returns 0000000000000000 for practically every root; Nano needs
blake2b-64(work || root), little-endian, AT OR ABOVE the threshold (fffffe0000000000 for a receive). 5 of treasury2's
6 starters were still receivable at its payees. bounties.txt must steer a payee away from that step and to the two
receivers it publishes and tests (seedrecv.py, receive.js), and the zero-work claim must stay true arithmetic.

Run: python3 specs/test_bounties_try_nano_receive_step.py
"""
import hashlib
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RECEIVE = 0xFFFFFE0000000000
SEND = 0xFFFFFFF800000000


def difficulty(work_hex, root_hex):
    """Nano work value: blake2b-64 over the 8 work bytes (little-endian) then the root, read little-endian."""
    w = bytes.fromhex(work_hex)[::-1]
    return int.from_bytes(hashlib.blake2b(w + bytes.fromhex(root_hex), digest_size=8).digest(), "little")


def inverted_loop(root_hex):
    """The comparison try-nano's nano-receive.py fallback makes (prefix BELOW the target), reproduced."""
    h = bytes.fromhex(root_hex)
    nonce = 0
    while True:
        d = hashlib.blake2b(nonce.to_bytes(8, "little") + h, digest_size=8).digest()
        if int.from_bytes(d[:4], "big") < 0xFFFFFFF8:
            return nonce.to_bytes(8, "little").hex()
        nonce += 1


class TryNanoReceiveStep(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt"), encoding="utf-8") as f:
            self.txt = f.read()
        i = self.txt.index("Do not receive it the way try-nano's step 3 says.")
        self.para = " ".join(self.txt[i:self.txt.index("\n\n", i)].split())

    def test_names_both_tools_and_the_outside_default(self):
        for s in ("opener/nano-x402-client.js", "opener/nano-receive.py", "https://pursekeeper.dev",
                  "not ours", "0000000000000000", "--seed <64hex>"):
            self.assertIn(s, self.para)

    def test_points_at_our_tested_receivers(self):
        self.assertIn("section 4's seedrecv.py", self.para)
        self.assertIn("section 8's receive.js", self.para)
        # both receivers it points at must still exist in the file, on rpc.nano.to, with local work
        self.assertIn("cat > seedrecv.py <<'EOF'", self.txt)
        self.assertIn("cat > receive.js <<'EOF'", self.txt)
        self.assertIn("computeWork(prev||pk,{workThreshold:'fffffe0000000000'})", self.txt)
        self.assertIn("NANO_NODE_URL=https://rpc.nano.to python3 -I -S seedrecv.py", self.txt)

    def test_paragraph_dated_and_counts_measured(self):
        self.assertRegex(self.para, r"\d\d:\dx UTC 2026-\d\d-\d\d")
        self.assertRegex(self.para, r"\d of treasury2's \d starters were still receivable")

    def test_paragraph_sits_with_the_try_nano_note(self):
        i = self.txt.index("One field in try-nano is out of date")
        j = self.txt.index("Do not receive it the way try-nano's step 3 says.")
        self.assertLess(i, j)
        self.assertLess(j, self.txt.index("GATE LOG - every canon confirmation"))

    def test_zero_work_is_invalid_and_the_loop_returns_it(self):
        roots = [hashlib.blake2b(bytes([k]), digest_size=32).hexdigest() for k in range(20)]
        for r in roots:
            w = inverted_loop(r)
            self.assertLess(difficulty(w, r), RECEIVE, r)
        self.assertEqual(sum(inverted_loop(r) == "0000000000000000" for r in roots), 20)

    def test_difficulty_reader_accepts_real_work(self):
        # sanity: the reader above is the real rule, so a nonce searched for correctly passes it
        r = hashlib.blake2b(b"root", digest_size=32).hexdigest()
        n = 0
        while difficulty("%016x" % n, r) < 0xFFF0000000000000:
            n += 1
        self.assertGreaterEqual(difficulty("%016x" % n, r), 0xFFF0000000000000)


if __name__ == "__main__":
    unittest.main()
