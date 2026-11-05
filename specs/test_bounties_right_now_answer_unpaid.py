#!/usr/bin/env python3
"""Law: the RIGHT NOW box must not send an earner to answer an ask without saying it earns no XNO (challenge #221).

Measured 2026-11-05: answer #447 (10:38 UTC, first-seen outside account) landed on our bounty ask #460 after the box
said "If you read only this box: send the confirmation, or answer an ask." under a header that reads GET PAID. None of
our 12 bounty asks (#1-#5, #11-#13, #458-#461) can be accepted - they predate the accept_token rule - and of 63 asks
none has a settlementBlock. The box said so nowhere; section 5 says it 950 lines down.

Run: python3 specs/test_bounties_right_now_answer_unpaid.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RightNowAnswerUnpaid(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        self.box = txt[txt.index(" RIGHT NOW - measured "):txt.index(" 1. THE REWARDS")]
        self.flat = " ".join(self.box.split())

    def test_box_says_an_answer_earns_no_xno(self):
        self.assertIn("AN ANSWER EARNS NO XNO TODAY", self.flat)
        self.assertIn("cannot be accepted (no accept_token)", self.flat)
        self.assertRegex(self.flat, r"0 of \d+ asks settled")

    def test_box_no_longer_ends_on_a_bare_answer_an_ask(self):
        self.assertNotIn("or answer an ask.", self.flat)
        self.assertIn("answer for the record", self.flat)

    def test_box_lines_fit_80_columns_except_commands(self):
        for line in self.box.splitlines():
            if "curl " in line:
                continue
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
