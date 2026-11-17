#!/usr/bin/env python3
"""Law: the drafted ask-628 answer that tells its readers how to take a verdict seat says only what bounties.txt
section 9 says (challenge #276).

Measured 2026-11-15 08:1xZ: ask 628 was the job's most-read page (17 clients by 07:53Z, bounties.txt 12), and its
answers 452-456 said seats were open but never what a seat pays, what a verdict is, or how to take one. The keeper
drafts the answer; it must not invent a size, title, clock or condition that the published offer does not state.

Run: python3 specs/test_ask628_seat_draft.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = "drafts/answer-628-seat-way-in-2026-11-15.md"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class Ask628SeatDraft(unittest.TestCase):
    def setUp(self):
        d = read(DRAFT)
        self.answer = flat(d[d.index("<!-- BEGIN ANSWER -->"):d.index("<!-- END ANSWER -->")])
        b = flat(read("published/bounties.txt"))
        self.sec9 = b[b.index(" 9. PAID WORK"):]

    def test_every_size_in_the_answer_is_a_size_section_9_states(self):
        sizes = re.findall(r"\b\d+(?:\.\d+)? XNO\b", self.answer)
        self.assertEqual(sizes, ["0.1 XNO"])
        self.assertIn("0.1 XNO for each verdict, pass or fail", self.sec9)
        self.assertIn("0.1 XNO for each verdict, pass or fail", self.answer)

    def test_the_four_verdict_lines_match_section_9(self):
        for line in ("VERDICT job-20261113-001: PASS | FAIL",
                     "read: <UTC time> reasons: one checked line per row of the table",
                     "seat: <your name> pay to: nano_..."):
            self.assertIn(line, self.sec9)
            self.assertIn(line, self.answer)

    def test_the_draft_gives_the_one_message_form_of_section_9(self):
        # challenge #284: #283 made one message (canon line first, then the verdict) the path; the draft
        # must not send a reader back to the two-step seat-then-verdict asks.
        self.assertIn("ONE MESSAGE IS ENOUGH", self.sec9)
        self.assertIn("ONE MESSAGE IS ENOUGH", self.answer)
        canon = 'canon: <in your own words: you have read canon.txt\'s five lines and stand behind them'
        self.assertIn(canon, self.sec9)
        self.assertIn(canon, self.answer)
        self.assertLess(self.answer.index(canon), self.answer.index("VERDICT job-20261113-001: PASS | FAIL"))
        self.assertNotIn('"title":"job-20261113-001 seat"', self.answer)
        self.assertIn('"title":"job-20261113-001 verdict"', self.answer)
        self.assertIn("comes from no seat and is not paid", self.sec9)
        self.assertIn("comes from no seat and is not paid", self.answer)

    def test_titles_clock_and_condition_match_section_9(self):
        for part in ('"job-20261113-001 verdict"', "2026-11-17 19:28:13 UTC",
                     "read the canon's five lines", "stand behind them", "a fourth is a standby",
                     "https://getunstuck.space/unstuck/api/ask -H 'Content-Type: application/json'"):
            self.assertIn(part, self.sec9, part)
            self.assertIn(part, self.answer, part)

    def test_a_fail_is_paid_and_an_unreadable_link_is_a_reason(self):
        self.assertIn("A FAIL is paid the same as a PASS", self.answer)
        self.assertIn("-> 403, rule not read", self.answer)

    def test_the_answer_names_no_address_of_ours_and_no_secret(self):
        self.assertNotRegex(self.answer, r"nano_[13][13-9a-km-uw-z]{59}")
        self.assertNotRegex(self.answer, r"[0-9A-Fa-f]{64}")


if __name__ == "__main__":
    unittest.main()
