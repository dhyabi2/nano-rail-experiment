#!/usr/bin/env python3
"""Law: swap.txt names the open paid job near its top (challenge #272).

Measured 2026-11-14 16:07 UTC (/ai/traffic): swap.txt drew 6 outside requests from 4 clients since 00:00. It is the
guide for an agent that wants XNO, and it offered only a swap from USDC, ETH or SOL - with "Nobody should fund this
for you, and we will not" - while one paid job (bounties.txt section 9) was open. `grep -c job-20261113-001` gave
swap.txt 0, every other linked guide >0. An agent holding nothing to swap was told there was no way in. swap.txt now
says, right after that sentence, that XNO can be earned for work, in rule 12's pay words, untested, with the payer and
a pointer to section 9; section 6's bounties line points at it too.

Run: python3 specs/test_swap_names_paid_job.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "job-20261113-001"
DELIVERY = "1 XNO for the delivery, once it passes."
VERDICT = "0.1 XNO for each verdict, pass or fail."
DEADLINE = "2026-11-20 23:59 UTC"
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class SwapNamesPaidJob(unittest.TestCase):
    def setUp(self):
        self.text = read("published/swap.txt")
        self.flat = flat(self.text)

    def test_block_states_the_job_in_rule_12_words(self):
        i = self.text.index("HOLD NOTHING TO SWAP?")
        block = flat(self.text[i:self.text.index("\n\n", i)])
        for want in (JOB, DELIVERY, VERDICT, DEADLINE, "untested", TREASURY2,
                     "section 9 of https://172-86-112-140.sslip.io/bounties.txt"):
            self.assertIn(want, block)
        rest = block.replace(DELIVERY, "").replace(VERDICT, "")
        self.assertNotRegex(rest, r"\b\d+(\.\d+)? XNO\b")

    def test_block_sits_before_section_1(self):
        self.assertLess(self.text.index("HOLD NOTHING TO SWAP?"), self.text.index("1. WHICH ROUTES ACTUALLY EXIST"))

    def test_words_match_bounties_section_9(self):
        b = flat(read("published/bounties.txt"))
        for want in (JOB, DELIVERY, VERDICT, DEADLINE, TREASURY2):
            self.assertIn(want, b)

    def test_section_6_points_at_the_job(self):
        i = self.text.index(" 6. THE REST")
        self.assertIn("its section 9 is the one paid job", flat(self.text[i:]))

    def test_block_lines_fit_80_columns(self):
        i = self.text.index("HOLD NOTHING TO SWAP?")
        for line in self.text[i:self.text.index("\n\n", i)].splitlines():
            self.assertLessEqual(len(line), 80, line)

    def test_no_old_treasury_as_payee(self):
        i = self.text.index("HOLD NOTHING TO SWAP?")
        self.assertNotIn("nano_1yo6c1t6", self.text[i:self.text.index("\n\n", i)])


if __name__ == "__main__":
    unittest.main()
