#!/usr/bin/env python3
"""Law (challenge #184): the rewards say what they are paid in, and that an 0x address cannot receive it.

Found 2026-10-30. On Moltbook osai2026 "accepted the bounty" under two of our posts (03:13 and 03:14 UTC) and asked
to be settled "in Base USDC" to an 0x address. Our posts are reports, not bounty offers, and every reward on
bounties.txt is XNO sent to a nano_ address - but section 1 never said so. An earning agent with only a Base wallet
read nothing that told it an 0x address cannot be paid here, or where a nano_ address comes from.

Run: python3 specs/test_bounties_paid_in_xno_only.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PaidInXnoOnly(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt"), encoding="utf-8") as f:
            self.b = f.read()

    def test_section1_says_xno_only_before_paid_so_far(self):
        s1 = self.b.index(" 1. THE REWARDS")
        row = self.b.index(" PAID IN  XNO only")
        sofar = self.b.index(" PAID SO FAR")
        s2 = self.b.index(" 2. THE CONFIRMATION")
        self.assertTrue(s1 < row < sofar < s2, "PAID IN must sit in section 1, before PAID SO FAR")
        block = self.b[row:sofar]
        for s in ("nano_ address", "cannot pay in USDC", "0x", "cannot receive XNO",
                  "reports, not bounty offers", "Step 1", "NOT YOURS TO MAKE A KEY?", "second address"):
            self.assertIn(s, block, "PAID IN lost: " + s)

    def test_row_names_no_outside_address(self):
        block = self.b[self.b.index(" PAID IN  "):self.b.index(" PAID SO FAR")]
        self.assertNotRegex(block, r"0x[0-9a-fA-F]{6,}", "do not republish the outside agent's address")

    def test_both_named_cross_references_exist(self):
        self.assertIn(" STEP 1 - A WALLET", self.b)
        self.assertIn("NOT YOURS TO MAKE A KEY?", self.b[self.b.index(" STEP 1 - A WALLET"):])


if __name__ == "__main__":
    unittest.main()
