#!/usr/bin/env python3
"""Law for challenge #233: the RIGHT NOW box's claim that a paid call NOT ours works (rpc.nano.to's
work_generate, 0.001 XNO) carries its own free re-check, and STEP 6 gives the same one.

Measured 20:1x UTC 2026-11-07: the box (dated 00:30 UTC 11-06) gave re-checks for our echo and for the dead
paypercall.dev sellers, and none for the one paid call a stranger can make to someone else - the purchase this
experiment exists for. STEP 6's command for it prints the whole 402 body and has no timeout. And the obvious
short form is wrong: without `Content-Type: application/json` rpc.nano.to answers HTTP 200 with
{"error":"Action not provided"} in the body, so a status-only check reads "up, and free" when it is neither.

Run: python3 specs/test_right_now_outside_call_check.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECK = ('curl -s -m 10 -o /dev/null -w "work_generate %{http_code}\\n" '
         "-H 'Content-Type: application/json' "
         '-d \'{"action":"work_generate","hash":"B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F"}\' '
         'https://rpc.nano.to')


class OutsideCallCheck(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.box = self.txt[self.txt.index(" RIGHT NOW - measured "):self.txt.index(" 1. THE REWARDS")]

    def test_box_claim_has_its_check(self):
        claim = self.box[self.box.index("WORKS, PAID, NOT OURS"):self.box.index("WORKS, PAID: getunstuck")]
        self.assertIn(CHECK, claim)
        self.assertIn("402 = up", claim)

    def test_check_sends_the_content_type(self):
        self.assertIn("-H 'Content-Type: application/json'", CHECK)
        for line in self.txt.splitlines():
            if "work_generate %{http_code}" in line:
                self.assertIn("Content-Type: application/json", line, "without it the node answers 200")

    def test_step6_gives_the_same_check_and_says_why(self):
        sec = self.txt[self.txt.index("A PAID CALL THAT IS NOT OURS, AND IS PAID"):]
        sec = sec[:sec.index("ONE PAID CALL OF OURS DOES ANSWER")]
        self.assertIn(CHECK, sec)
        self.assertIn("answers 200", " ".join(sec.split()))


if __name__ == "__main__":
    unittest.main()
