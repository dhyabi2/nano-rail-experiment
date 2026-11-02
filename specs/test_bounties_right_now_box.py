#!/usr/bin/env python3
"""Law for the RIGHT NOW box at the top of bounties.txt (challenge #202).

Measured 2026-11-02 04:17 UTC: the five paypercall.dev sellers had answered nothing since about 10:25 UTC 10-17,
the only paid call that answered was getunstuck.space's echo (0.001 XNO, unpaid 402), and no 0.1 XNO had been sent
to anyone since 10-13. bounties.txt said all of this, but the first word of it ("RIGHT NOW: the 24 endpoints...")
sat at line 546 of 1326, below the rewards, the confirmation and five STEPs. A stranger who reads the top and stops
learns two rewards and none of what works today. The box puts what works, what is down and what pays before
section 1, with the command that re-checks the sellers.

Run: python3 specs/test_bounties_right_now_box.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RightNowBox(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.lines = self.txt.splitlines()
        self.i = self.txt.index(" RIGHT NOW - measured ")
        self.box = self.txt[self.i:self.txt.index(" 1. THE REWARDS")]
        self.flat = " ".join(self.box.split())

    def test_before_section_1_and_near_the_top(self):
        self.assertLess(self.i, self.txt.index(" 1. THE REWARDS"))
        line = self.txt[:self.i].count("\n") + 1
        self.assertLessEqual(line, 10, "the box must start within the first 10 lines")
        self.assertLessEqual(len(self.box.splitlines()), 16, "a box nobody can read in one screen is not a box")

    def test_carries_a_measurement_time_and_says_recheck(self):
        self.assertRegex(self.flat, r"measured \d\d:\d\d UTC 2026-\d\d-\d\d")
        self.assertIn("Re-check", self.flat)

    def test_says_what_works_what_is_down_what_pays(self):
        for word in ("WORKS, FREE", "WORKS, PAID", "DOWN", "REWARDS"):
            self.assertIn(word, self.flat)
        self.assertIn("echo", self.flat)
        self.assertIn("0.001 XNO", self.flat)
        self.assertIn("Do not send them XNO", self.flat)
        self.assertIn("Plan on none", self.flat)

    def test_recheck_command_matches_step6(self):
        cmd = 'for h in extract search domain check geoip; do curl -s -m 10 -o /dev/null -w "$h %{http_code}\\n" https://$h.paypercall.dev/health; done'
        self.assertIn(cmd, self.box)
        step6 = self.txt[self.txt.index(" STEP 6 - "):]
        self.assertIn(cmd, step6, "the box and STEP 6 must give the same check")

    def test_points_at_sections_that_exist(self):
        for ref in (" 2. THE CONFIRMATION", " 5. THE NETWORK", "ONE PAID CALL OF OURS", " PAID SO FAR"):
            self.assertIn(ref, self.txt[self.i + len(self.box):], ref + " must exist below the box")

    def test_box_date_not_newer_than_stamp(self):
        stamp = re.search(r"Updated (2026-\d\d-\d\d)\.", "\n".join(self.lines[:6])).group(1)
        box = re.search(r"UTC (2026-\d\d-\d\d)", self.flat).group(1)
        self.assertLessEqual(box, stamp)


if __name__ == "__main__":
    unittest.main()
