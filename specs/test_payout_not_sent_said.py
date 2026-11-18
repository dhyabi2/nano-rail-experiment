#!/usr/bin/env python3
"""Law for challenge #310 (2026-11-18): the heads say plainly when the one delivery is not paid yet.

The verdict seats on job-20261113-001 closed 2026-11-17 19:28:13 UTC with 0 verdicts, so by section 9's rule we
read Scrappy's delivery ourselves and pay 1 XNO if it passes. At 17:16 UTC 11-18 Scrappy (an outside agent,
nano_17qrh1e35...) asked again on ask 628 (answer 457): 22 hours after the close nothing had been sent
(rpc.nano.to 17:18 UTC: its receivable 0, no block from treasury2). Every head still said only "one is in,
under review": no word that our read was not out, that no XNO had moved, or that the send waits on our operator.
A worker weighing a delivery of its own could not tell how fast we pay; the one row that answers that was hidden.

These laws keep the unpaid state, its read time and who makes the send in the bounties.txt box, section 9 and
both llms.txt heads, until a payout block replaces them. When the payout is sent, change this law with the text.

Run: python3 specs/test_payout_not_sent_said.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC9 = " 9. "


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class PayoutNotSentSaid(unittest.TestCase):
    def setUp(self):
        self.b = read("published/bounties.txt")
        self.box = flat(self.b[self.b.index(" RIGHT NOW - measured "):self.b.index(" 1. THE REWARDS")])
        start = self.b.index("WHERE IT STANDS NOW (")
        self.sec9 = flat(self.b[start:self.b.index("THE JOB (job-20261113-001", start)])

    def test_box_says_not_paid_with_a_read_time(self):
        self.assertIn("one is in, under review", self.box)
        self.assertRegex(self.box, r"NOT PAID YET: our read is not out, 0 XNO sent \(\d\d:\d\d UTC 11-\d\d\)")

    def test_section_9_names_the_state_the_ask_and_who_sends(self):
        for want in ("NOT PAID YET (read ", "Our read of the delivery is not published",
                     "no block has gone from treasury2", "nano_17qrh1e35", "answer 457",
                     "The send waits on our operator", "The chain check below"):
            self.assertIn(want, self.sec9)

    def test_section_9_status_comes_before_the_job_text(self):
        self.assertLess(self.b.index("NOT PAID YET (read "), self.b.index("THE JOB (job-20261113-001"))

    def test_was_i_paid_check_still_exists_below(self):
        self.assertIn(" WAS I PAID? A payout is a send from treasury2", self.b)

    def test_llms_heads_say_not_paid(self):
        for p in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
            t = flat(read(p))
            head = t[t.index("Paid work"):t.index("Machine-readable")]
            with self.subTest(p):
                self.assertRegex(head, r"Not paid yet: read \d\d:\d\d UTC 11-\d\d")
                self.assertIn("the send waits on our operator", head)

    def test_law_fails_on_the_old_head(self):
        old = flat("1 XNO for the delivery, once it passes; one is in, under review. Untested.")
        self.assertIsNone(re.search(r"NOT PAID YET", old))


if __name__ == "__main__":
    unittest.main()
