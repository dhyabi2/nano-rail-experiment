#!/usr/bin/env python3
"""Law for challenge #209: the RIGHT NOW box at the top of bounties.txt must let a stranger re-check every
claim in it without trusting its date.

Measured 08:1x UTC 2026-11-03: the box still said "measured 08:22 UTC 2026-11-02", a day old. It gave a re-check
command for the one claim that was DOWN (the five sellers) and none for the one that WORKS, PAID (the echo), so a
reader who did as told ("do not trust a date") could confirm only the bad news. The off-box watch (outage-watch,
challenge #148) cannot stand in for these checks: it posts to an issue in a private repository a stranger cannot read.

Run: python3 specs/test_right_now_box_checks_itself.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ECHO_CHECK = ('curl -s -m 10 -o /dev/null -w "echo %{http_code}\\n" -X POST '
              'https://getunstuck.space/unstuck/api/v1/echo')


class RightNowBoxChecksItself(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        self.txt = txt
        self.box = txt[txt.index(" RIGHT NOW - measured "):txt.index(" 1. THE REWARDS")]
        self.flat = " ".join(self.box.split())

    def test_paid_claim_has_a_free_recheck(self):
        paid = self.box[self.box.index("WORKS, PAID"):self.box.index("DOWN:")]
        self.assertIn(ECHO_CHECK, paid)
        self.assertIn("402 = up", paid)
        self.assertIn("-X POST", paid, "a GET on the echo answers 404 (challenge #204)")

    def test_echo_check_targets_the_url_step6_pays(self):
        step6 = self.txt[self.txt.index("ONE PAID CALL OF OURS DOES ANSWER"):]
        self.assertIn("-X POST https://getunstuck.space/unstuck/api/v1/echo", step6)

    def test_every_claim_in_the_box_has_its_own_check(self):
        self.assertEqual(self.box.count("curl -s -m 10"), 2, "one check for what works paid, one for what is down")


if __name__ == "__main__":
    unittest.main()
