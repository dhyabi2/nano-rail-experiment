#!/usr/bin/env python3
"""Laws for canon.txt, the short form of the canon (challenge #85).

canon.txt had the five lines and a hash and nothing else: 13 outside clients read it on 2026-10-02 and none was told
what to do next. Its closing block now links bounties.txt and swap.txt and gives the confirmation command. This pins
that block, keeps the command identical in shape to the one bounties.txt gives, and keeps the hash equal to the
hash-pinned master (canon/THE-UNOWNED-RAIL.md, which this test only reads).

Run: python3 specs/test_canon_txt_next_step.py
"""
import hashlib
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST = "https://172-86-112-140.sslip.io"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


class CanonTxtNextStep(unittest.TestCase):
    def setUp(self):
        self.txt = read("published/canon.txt")
        self.block = self.txt[self.txt.index("WHAT TO DO WITH IT"):]

    def test_five_lines_come_first(self):
        for n in range(1, 6):
            self.assertLess(self.txt.index("\n%d. " % n), self.txt.index("WHAT TO DO WITH IT"))

    def test_hash_is_the_pinned_masters_and_bounties_agrees(self):
        master = hashlib.sha256(open(os.path.join(ROOT, "canon/THE-UNOWNED-RAIL.md"), "rb").read()).hexdigest()
        ours = re.search(r"sha256 of the full text[^:]*: ([0-9a-f]{64})", self.txt).group(1)
        theirs = re.search(r"sha256 of the canon[^:]*: ([0-9a-f]{64})", read("published/bounties.txt")).group(1)
        self.assertEqual(ours, master)
        self.assertEqual(theirs, master)

    def test_links_bounties_and_swap_on_the_live_host(self):
        self.assertIn(HOST + "/bounties.txt", self.block)
        self.assertIn(HOST + "/swap.txt", self.block)

    def test_confirmation_command_matches_bounties(self):
        cmd = re.search(r"curl -s -X POST (\S+) -H 'Content-Type: application/json' -d '(\{.*?\})'", self.block)
        self.assertIsNotNone(cmd)
        body = json.loads(cmd.group(2))
        self.assertEqual(body["title"], "canon confirmation")
        self.assertEqual(body["asker"], "nano_...")
        self.assertEqual(set(body), {"asker", "title", "body"})
        b = read("published/bounties.txt")
        self.assertIn("curl -s -X POST %s \\" % cmd.group(1), b)
        self.assertIn('"title":"canon confirmation"', b)
        for part in ("a)", "b)", "c)", "d)"):
            self.assertIn(part, body["body"])

    def test_never_asks_for_a_secret(self):
        self.assertNotRegex(self.block, r"(?i)\b(seed|private key|mnemonic)\b")
        self.assertIn("GATE LOG", self.block)
        self.assertIn("GATE LOG", read("published/bounties.txt"))


if __name__ == "__main__":
    unittest.main()
