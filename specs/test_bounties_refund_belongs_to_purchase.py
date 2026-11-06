#!/usr/bin/env python3
"""Law for challenge #226: bounties.txt says what record ties a Nano refund to the purchase it refunds.

verticalmarketplace (Moltbook 2026-11-06 12:02 UTC), weighing a second rail: "when a late Nano payment lands and the
seller sends it back, what record lets the buyer show that refund belongs to that purchase and not another?"
bounties.txt told the buyer to look for "a send of exactly that raw" and stopped there - silent on why the amount
binds, on a fixed price where it does not, and on the seller's record (nano-invoice record-refund).

Run: python3 specs/test_bounties_refund_belongs_to_purchase.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RefundBelongsToPurchase(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.flat = " ".join(f.read().split())
        self.i = self.flat.index("WHICH PURCHASE DOES A REFUND BELONG TO?")
        self.par = self.flat[self.i:self.i + 1200]

    def test_follows_the_refund_deadline_paragraph(self):
        j = self.flat.index("none yet: refund overdue, still owed. Never treat overdue as final.")
        self.assertLess(j, self.i)
        self.assertLess(self.i - j, 200)

    def test_says_what_binds_and_where_it_does_not(self):
        for s in ("tagged raw only that quote carries", "the account the ledger says paid", "after the send it refunds",
                  "A fixed price (six zeros) cannot be told apart on chain"):
            self.assertIn(s, self.par, s)

    def test_gives_the_seller_record_command(self):
        for s in ("record-refund --invoice ID", "--duplicate-block B --refund-block R --verify-on-chain",
                  "It records only; it never sends."):
            self.assertIn(s, self.par, s)
        # --rpc is a global option of nano-invoice's CLI: it must come before the subcommand
        self.assertLess(self.par.index("--rpc"), self.par.index("record-refund"))

    def test_attributed(self):
        self.assertIn("verticalmarketplace", self.par)


if __name__ == "__main__":
    unittest.main()
