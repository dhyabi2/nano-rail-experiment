#!/usr/bin/env python3
"""Laws for bounties.txt's "BEFORE STEP 6 - YOUR FIRST XNO" block (challenge #84).

Section 4 went from a wallet (STEP 1) to "SPEND IT" (STEP 6) without saying where a newcomer's first XNO comes from,
and never linked swap.txt. Two outside agents on Moltbook (2026-10-02) put the wall at exactly that step: a funded
spender its operator has authorised. This pins the block in place, keeps its swap figures equal to swap.txt's own,
and keeps the operator request free of anything secret - it must send an address, never a seed or key.

Run: python3 specs/test_bounties_first_xno.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, "published", rel)) as f:
        return f.read()


class FirstXno(unittest.TestCase):
    def setUp(self):
        self.txt = read("bounties.txt")
        i = self.txt.index(" BEFORE STEP 6 - YOUR FIRST XNO.")
        self.block = self.txt[i:self.txt.index("\n STEP 6 - ", i)]

    def test_sits_between_step5_and_step6(self):
        self.assertLess(self.txt.index(" STEP 5 - "), self.txt.index(" BEFORE STEP 6 - "))
        self.assertLess(self.txt.index(" BEFORE STEP 6 - "), self.txt.index("\n STEP 6 - "))

    def test_links_the_live_swap_guide(self):
        self.assertIn("https://172-86-112-140.sslip.io/swap.txt", self.block)

    def test_swap_minimum_matches_swap_txt(self):
        swap = read("swap.txt")
        ours = re.search(r"minimum ([0-9.]+)\s+USDC", self.block).group(1)
        theirs = re.search(r"Minimum\s+([0-9.]+) USDC-BASE", swap).group(1)
        self.assertEqual(ours, theirs)
        rate = float(re.search(r"5 USDC-BASE -> ([0-9.]+) XNO", swap).group(1)) / 5
        xno = float(re.search(r"about ([0-9.]+) XNO", self.block).group(1))
        self.assertAlmostEqual(xno, float(theirs) * rate, delta=0.01)
        self.assertGreater(xno / 0.0005, 1000, "the 'over 1,000 calls' claim")

    def test_does_not_promise_we_fund_it(self):
        self.assertIn("Nobody here sends it", self.block)
        self.assertNotRegex(self.block, r"(?i)we (will )?(send|fund|top up) you")

    def test_operator_request_sends_an_address_only(self):
        req = self.block[self.block.index('"Authorise'):self.block.rindex('"') + 1]
        self.assertIn("nano_<my address>", req)
        self.assertIn("whose key only I hold", req)
        self.assertNotRegex(req, r"(?i)\bseed\b|private key|password")
        self.assertIn("To revoke", req)


if __name__ == "__main__":
    unittest.main(verbosity=2)
