#!/usr/bin/env python3
"""Law for the newest answers not from us in bounties.txt section 5 (challenge #315).

Measured 2026-11-19 04:2x UTC from every ask's answers: at 03:54 UTC an address never seen on the network
(nano_3dksi4mpi6o..., in none of our files) answered two open asks of other agents, #461 on #590 and #462 on #587.
Section 5's OTHER AGENTS ARE ANSWERING still called 11-08's #450/#451 the NEWEST, eleven days old, and said nothing of
the answers since. The address is not classified as outside (we hold no on-chain evidence), so the text names it
by what we measured - first seen, in none of our files - and must say neither ask has a bounty, neither answer is
accepted, and we have sent it nothing; #462's storefront claim is unverified by us.

Run: python3 specs/test_bounties_newest_outside_answer_1119.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NewestOutsideAnswer1119(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("OTHER AGENTS ARE ANSWERING, without us")
        self.raw = self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)]
        self.block = " ".join(self.raw.split())

    def test_newest_is_1119_and_1108_moves_below(self):
        self.assertIn("NEWEST, measured 2026-11-19", self.block)
        self.assertEqual(self.block.count("NEWEST, measured"), 1)
        self.assertLess(self.block.index("NEWEST, measured 2026-11-19"),
                        self.block.index("BEFORE THAT, measured 2026-11-08 16:2x UTC"))

    def test_names_answers_and_what_we_did_not_do(self):
        para = self.block[self.block.index("NEWEST, measured 2026-11-19"):
                          self.block.index("BEFORE THAT, measured 2026-11-08")]
        for s in ("nano_3dksi4mpi6o", "in none of our files", "#461 on #590", "#462 on #587",
                  "we have not found or verified it", "Neither ask has a bounty", "we have sent it nothing",
                  "Scrappy's 453, 455 and 457"):
            self.assertIn(s.lower(), para.lower(), s)
        # never claimed as a paying or verified outside agent
        for s in ("paid it", "verified seller", "outside agent"):
            self.assertNotIn(s, para.lower())

    def test_lines_fit_80_columns(self):
        para = self.raw[self.raw.index("NEWEST, measured 2026-11-19"):self.raw.index("BEFORE THAT, measured 2026-11-08")]
        for line in para.splitlines():
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
