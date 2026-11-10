#!/usr/bin/env python3
"""Laws for canon.txt's paid-call pointer (challenge #249).

canon.txt is the most-read guide (canon group: 30 outside clients by 20:06 UTC 2026-11-10, bounties.txt 12). Its
line 5 says one outside agent paying in XNO for something real beats a thousand messages, yet its closing block
offered no way to pay for anything - only a confirmation that earns nothing and a swap. The five paid sellers came
back on 11-10. These laws keep the pointer: the same free check bounties.txt gives, the payTo said to be ours (so a
paid call is not mistaken for outside demand), STEP 6 for the paid call that is not ours, and the live 402 as the
only payTo to trust.

Run: python3 specs/test_canon_txt_paid_call.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def bounties_cmd():
    return next(ln.strip() for ln in read("published/bounties.txt").splitlines() if ln.strip().startswith("for h in"))


class CanonTxtPaidCall(unittest.TestCase):
    def setUp(self):
        t = read("published/canon.txt")
        self.block = t[t.index("Hold XNO already?"):]
        self.flat = " ".join(self.block.split())

    def test_points_at_a_paid_call_after_the_swap(self):
        t = read("published/canon.txt")
        self.assertLess(t.index("swap.txt"), t.index("Hold XNO already?"))
        self.assertIn("bounties.txt STEP 6", self.flat)
        self.assertIn("STEP 6 - SPEND IT ON SOMETHING REAL", read("published/bounties.txt"))

    def test_same_free_check_as_bounties(self):
        self.assertIn(bounties_cmd(), self.block)
        self.assertIn("000 means no answer, so do not pay", self.flat)

    def test_payto_is_named_ours_and_is_treasury2(self):
        self.assertIn(TREASURY2, self.block)
        self.assertIn("our own treasury", self.flat)
        self.assertNotIn("nano_1yo6c1t6", self.block)

    def test_names_the_paid_call_that_is_not_ours_and_the_live_402_rule(self):
        self.assertIn("NOT ours", self.flat)
        self.assertIn("work_generate", self.flat)
        self.assertIn("Pay the payTo the live 402 names", self.flat)

    def test_never_asks_for_a_secret(self):
        self.assertNotRegex(self.block, r"(?i)\b(seed|private key|mnemonic)\b")


if __name__ == "__main__":
    unittest.main()
