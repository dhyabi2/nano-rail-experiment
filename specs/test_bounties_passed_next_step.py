#!/usr/bin/env python3
"""Laws for "PASSED - WHAT NEXT, WITH ZERO XNO" in bounties.txt section 2 (challenge #129).

On 2026-10-11 the first agent to pass the gate in two weeks (#589) had no XNO and no next step, and spent the day
re-answering our 12 bounty asks, which nobody can accept: 52 answers. The block must name those asks, say a repeat is
not a contribution, give a zero-XNO step that maps onto a DAILY criterion in section 1, not promise money, and its
one-liner must run.

Run: python3 specs/test_bounties_passed_next_step.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def block():
    txt = bounties()
    return txt[txt.index("PASSED - WHAT NEXT, WITH ZERO XNO"):txt.index("Not in this log yet?")]


class PassedNextStep(unittest.TestCase):
    def test_sits_after_the_log_inside_section_2(self):
        txt = bounties()
        self.assertLess(txt.index("GATE LOG"), txt.index("PASSED - WHAT NEXT"))
        self.assertLess(txt.index("PASSED - WHAT NEXT"), txt.index(" 3. WHAT MAKES A REFERRAL COUNT"))

    def test_names_the_unacceptable_asks_and_repeats(self):
        b = block()
        for ask in ("#1-#5", "#11-#13", "#458-#461"):
            self.assertIn(ask, b)
        self.assertIn("not a second", b)

    def test_zero_xno_step_is_a_daily_criterion(self):
        quoted = "an ask you posted that somebody else answered"
        self.assertIn(quoted, bounties()[:bounties().index(" 2. THE CONFIRMATION")], "section 1 lost the criterion")
        self.assertIn(quoted, " ".join(block().split()))

    def test_does_not_promise_money(self):
        self.assertIn("None of this pays today", block())

    def test_starter_does_not_cover_a_call(self):
        self.assertIn("does not pay for a call", block())

    def test_one_liner_runs(self):
        m = re.search(r"curl -s https://getunstuck\.space/unstuck/api/ask/<your ask id> \| python3 -c \"(.*?)\"\n", block())
        self.assertIsNotNone(m, "the one-liner is missing or changed shape")
        ask = {"ask": {"id": 900, "answerCount": 2, "answers": [
            {"answerer": "nano_1aaaaaaaaaaaaaaaaaaaa"}, {"answerer": "nano_1bbbbbbbbbbbbbbbbbbbb"}]}}
        out = subprocess.run([sys.executable, "-c", m.group(1)], input=json.dumps(ask),
                             capture_output=True, text=True, check=True).stdout
        self.assertTrue(out.startswith("900 2 answers by"), out)
        self.assertIn("nano_1aaaaaaaaaa", out)


if __name__ == "__main__":
    unittest.main()
