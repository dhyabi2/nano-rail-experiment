#!/usr/bin/env python3
"""Law for challenge #225: what bounties.txt says about Subnano's quote window.

Until 2026-11-06 bounties.txt said Subnano's door gives "a new payTo per GET, 60 s" and, in the same breath,
"A late send to that address is still that quote's money: LATE IS PAID." pursekeeper (Moltbook 11-06 04:09 UTC)
corrected the number - "the number I gave you was stale. Correct it before you quote anything" - quoting Subnano's
docs: new Nano allocations last five minutes, and once an expired address is retired "new sends receive no automatic
fulfillment or refund". A buyer who read our line as "late is paid at Subnano" could send late and lose the XNO.

Run: python3 specs/test_bounties_subnano_window.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SubnanoWindow(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.flat = " ".join(f.read().split())

    def test_stale_sixty_seconds_is_gone(self):
        self.assertNotIn("a new payTo per GET, 60 s", self.flat)

    def test_five_minutes_and_no_refund_are_said(self):
        for s in ("lasts FIVE MINUTES", "maxTimeoutSeconds 300", "new sends receive no automatic fulfillment or refund",
                  "pay inside the five minutes or read a new 402", "purchase id and the hash"):
            self.assertIn(s, self.flat, s)

    def test_late_is_paid_is_scoped_to_your_own_checker(self):
        self.assertIn("still that quote's money to YOUR checker: LATE IS PAID. Not every seller serves it.", self.flat)
        self.assertNotIn("still that quote's money: LATE IS PAID.", self.flat)

    def test_prepay_step_warns_before_the_send(self):
        i = self.flat.index("PREPAY_FRESH_PAYTO=1 skips the pin")
        self.assertIn("send within the five minutes", self.flat[i:i + 400])

    def test_source_is_attributed_and_unverified_by_us(self):
        self.assertIn("pursekeeper, Moltbook 11-06 04:09 UTC", self.flat)
        self.assertIn("we could not read it ourselves", self.flat)


if __name__ == "__main__":
    unittest.main()
