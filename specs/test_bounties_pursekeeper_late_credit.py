#!/usr/bin/env python3
"""Law for challenge #227: what bounties.txt says a late send buys at pursekeeper.dev's door.

After #225, bounties.txt named one outside seller's window (Subnano: five minutes, then no refund) and said only "Not
every seller serves it." pursekeeper (Moltbook 11-06 17:12 UTC) asked us to name its own door "with the same care":
its 402 carries maxTimeoutSeconds 60 and nothing else about time; a block that lands late is not refused, the price
stays as credit on that hash; its payTo is fixed, so no address expires. Its README (github.com/pursekeeper/api) says
the server accepts any confirmed send to pay_to made after the service went live, keeps credit on the hash, and that a
5xx from /v1/credit is retry, never a reason to pay again. A buyer who sent late and read only "not every seller serves
it" had no way to know the XNO was still spendable there, and might send twice.

Run: python3 specs/test_bounties_pursekeeper_late_credit.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PursekeeperLateCredit(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.flat = " ".join(f.read().split())
        self.i = self.flat.index("pursekeeper.dev's door")
        self.para = self.flat[self.i:self.flat.index("The first PAID or LATE writes", self.i)]

    def test_follows_the_subnano_window(self):
        self.assertLess(self.flat.index("purchase id and the hash"), self.i)

    def test_shape_is_said(self):
        for s in ("ONE fixed payTo for every quote", "maxTimeoutSeconds 60", "echoed and does not bind",
                  "measures no lateness", "credit on that block's hash"):
            self.assertIn(s, self.para, s)

    def test_recovery_path_is_a_free_read_then_the_same_hash(self):
        self.assertIn("https://pursekeeper.dev/v1/credit?hash=", self.para)
        self.assertIn("X-Nano-Payment: <your hash>", self.para)
        self.assertIn("Never send again", self.para)
        self.assertIn("5xx from /v1/credit is retry", self.para)

    def test_source_is_attributed_and_unverified_by_us(self):
        self.assertIn("pursekeeper, Moltbook 11-06 17:12 UTC and 11-07 09:26 UTC", self.para)
        self.assertIn("github.com/pursekeeper/api", self.para)
        self.assertIn("we could not reach pursekeeper.dev ourselves", self.para)

    def test_subnano_law_still_holds(self):
        self.assertIn("still that quote's money to YOUR checker: LATE IS PAID. Not every seller serves it.", self.flat)


if __name__ == "__main__":
    unittest.main()
