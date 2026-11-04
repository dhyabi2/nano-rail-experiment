#!/usr/bin/env python3
"""Law: bounties.txt names the one paid Nano call that is NOT ours and that others pay (challenge #216).

Measured 20:19 UTC 2026-11-04: the five paypercall.dev sellers (ours) still answered nothing, and the RIGHT NOW box
named one paid call - our own echo, whose 0.001 XNO comes back to our Unstuck account and which nobody has paid.
rpc.nano.to's work_generate answered an unpaid POST with x402 v2 terms (nano:mainnet exact, 0.001 XNO to
nano_1rpc19tp..., maxTimeoutSeconds 60), and that payee's history held 5 receives of exactly 0.001 XNO from 3
accounts we do not know as ours (newest 10-22). A stranger whose first Nano payment we want to see happen had no
line telling it that a real outside seller is up. The box and STEP 6 now name it, with its exact terms, the
standard PAYMENT-SIGNATURE form it takes, and the rule that a 402 after signing is not a reason to sign again.

Run: python3 specs/test_bounties_outside_paid_call.py
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
from nano_address import check_nano_address  # noqa: E402

PAYEE = "nano_1rpc19tpfzuotsk346bt674mehj96ju86n5xiop4o68mepqexf5f55xa7ycx"
OURS = (
    "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7",  # treasury
    "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9",  # Unstuck
)


class OutsidePaidCall(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.box = self.txt[self.txt.index(" RIGHT NOW - measured "):self.txt.index(" 1. THE REWARDS")]
        self.step6 = self.txt[self.txt.index(" STEP 6 - "):]
        i = self.step6.index("A PAID CALL THAT IS NOT OURS, AND IS PAID")
        self.block = self.step6[i:self.step6.index("ONE PAID CALL OF OURS DOES ANSWER")]
        self.flat = " ".join(self.block.split())

    def test_box_names_it_and_says_not_ours(self):
        flat = " ".join(self.box.split())
        self.assertIn("WORKS, PAID, NOT OURS: rpc.nano.to's work_generate, 0.001 XNO", flat)
        self.assertIn('"A PAID CALL THAT IS NOT OURS"', flat)

    def test_step6_top_counts_two_calls_and_points_at_both(self):
        head = " ".join(self.step6[:self.step6.index("24 endpoints,")].split())
        self.assertIn("Two paid calls do answer", head)
        self.assertIn('"A PAID CALL THAT IS NOT OURS"', head)
        self.assertIn('"ONE PAID CALL OF OURS"', head)

    def test_block_comes_before_our_own_call(self):
        self.assertLess(self.step6.index("A PAID CALL THAT IS NOT OURS"), self.step6.index("ONE PAID CALL OF OURS DOES"))

    def test_exact_terms(self):
        self.assertIn(PAYEE, self.block)
        self.assertTrue(check_nano_address(PAYEE), "payee must be a checksum-valid nano_ address")
        self.assertNotIn(PAYEE, OURS)
        for s in ("nano:mainnet", "1000000000000000000000000000", "maxTimeoutSeconds 60", '"action":"work_generate"'):
            self.assertIn(s, self.flat)

    def test_standard_form_and_no_second_send(self):
        self.assertIn("PAYMENT-SIGNATURE = base64 JSON", self.flat)
        self.assertIn("NOT yet published", self.flat)
        self.assertIn("no workOptional", self.flat)
        self.assertIn("read your frontier (STEP 4) before you sign anything again", self.flat)

    def test_says_what_is_measured_and_what_is_not(self):
        self.assertRegex(self.flat, r"measured \d\d:\d\d UTC 11-04")
        self.assertIn("we have not paid it ourselves", self.flat)
        self.assertIn("none of them one we know as ours", self.flat)


if __name__ == "__main__":
    unittest.main()
