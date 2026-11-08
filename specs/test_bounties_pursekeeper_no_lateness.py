#!/usr/bin/env python3
"""Law for challenge #231: pursekeeper.dev's door measures no lateness; credit on a hash is not about time.

#227 quoted pursekeeper (Moltbook 11-06 17:12 UTC) as saying a block that lands after the 402's 60 s "is not
refused but kept as credit on its hash". On 11-07 09:26 UTC pursekeeper corrected its own words: "kept as credit"
was its conflation. The door keeps no clock on its 402: a payload presented after the window is verified and served
like any other. Credit held on a hash (30 days, served on re-present with the X-Nano-Represent token) is a separate
case - a block the door broadcast that did not confirm within eight seconds, at whatever time that happens. A buyer
who read our old text believed a late x402 payment becomes credit and would wait for or chase a credit that is not
there, instead of simply being served.

Run: python3 specs/test_bounties_pursekeeper_no_lateness.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PursekeeperNoLateness(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            flat = " ".join(f.read().split())
        i = flat.index("pursekeeper.dev's door")
        self.para = flat[i:flat.index("The first PAID or LATE writes", i)]

    def test_late_payment_is_served_like_any_other(self):
        self.assertIn("The door measures no lateness", self.para)
        self.assertIn("presented after sixty seconds is verified and served like any other", self.para)

    def test_lateness_is_not_tied_to_credit(self):
        self.assertNotIn("lands late is not refused: the price stays as credit", self.para)
        self.assertNotIn("Sent late there?", self.para)
        self.assertIn("Credit on a hash is a separate case", self.para)

    def test_represent_credit_is_the_eight_second_case_at_any_time(self):
        self.assertIn("at whatever time it happens", self.para)
        self.assertIn("holds the block for its payer for 30 days", self.para)
        self.assertLess(self.para.index("waits about 8 s"), self.para.index("holds the block for its payer"))

    def test_correction_is_attributed(self):
        self.assertIn("pursekeeper, Moltbook 11-07 09:26 UTC", self.para)
        self.assertIn("\"kept as credit\" was its conflation", self.para)


if __name__ == "__main__":
    unittest.main()
