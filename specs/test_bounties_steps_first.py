#!/usr/bin/env python3
"""Law: in bounties.txt, section 4 ("six commands") reaches STEP 1 before anything else.

Found 2026-10-01 (challenge #78). A box-side edit put a 21-line list of our own XNO tools between the section 4
heading and STEP 1, so a stranger promised "six commands" read a product list first, and the wallet command moved
from 4 to 25 lines below the heading. The list belongs after STEP 6, where the endpoints it describes are spent.

Run: python3 specs/test_bounties_steps_first.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
MAX_LINES_TO_STEP1 = 6


class StepsFirst(unittest.TestCase):
    def setUp(self):
        with open(BOUNTIES, encoding="utf-8") as f:
            self.lines = f.read().splitlines()

    def index(self, pattern):
        for i, line in enumerate(self.lines):
            if re.search(pattern, line):
                return i
        self.fail("not found in bounties.txt: " + pattern)

    def test_step1_close_to_heading(self):
        heading = self.index(r"^ 4\. OPEN YOUR ACCOUNT")
        step1 = self.index(r"^ STEP 1 - ")
        self.assertLess(step1 - heading, MAX_LINES_TO_STEP1,
                        "section 4 must reach STEP 1 within %d lines of its heading" % MAX_LINES_TO_STEP1)

    def test_steps_in_order(self):
        idx = [self.index(r"^ STEP %d - " % n) for n in range(1, 7)]
        self.assertEqual(idx, sorted(idx))

    def test_extras_after_step6(self):
        step6 = self.index(r"^ STEP 6 - ")
        section5 = self.index(r"^ 5\. THE NETWORK")
        for i, line in enumerate(self.lines):
            if "OUR XNO TOOLS" in line:
                self.assertTrue(step6 < i < section5, "the tools list sits between STEP 6 and section 5")


if __name__ == "__main__":
    unittest.main()
