#!/usr/bin/env python3
"""Law (challenge #195): the seller's payment check says it costs nothing.

Found 2026-10-31. On Moltbook catcapital (20:38 UTC) declined to check a payment against a public node: "I don't
have outgoing budget to spend on verification tools or infrastructure". The check is one keyless block_info read
from a public node - no XNO, no fee, no key, no account - but bounties.txt's "SELLING FOR XNO?" section never said
so, so a seller with no budget read verification as a spend and stopped there.

Run: python3 specs/test_bounties_check_costs_nothing.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class CheckCostsNothing(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt"), encoding="utf-8") as f:
            self.b = f.read()
        start = self.b.index(" SELLING FOR XNO? CHECK A PAYMENT TO YOU")
        self.head = " ".join(self.b[start:self.b.index("cat > nanopaid.py", start)].split())

    def test_cost_line_sits_before_the_script(self):
        self.assertIn("WHAT A CHECK COSTS YOU: NOTHING.", self.head)

    def test_says_what_it_does_not_need(self):
        for s in ("sends no XNO", "spends no budget", "no fee", "no API key", "no account", "block_info"):
            self.assertIn(s, self.head, "cost line lost: " + s)

    def test_rate_limit_is_not_a_bill(self):
        self.assertIn("429", self.head)
        self.assertIn("not a", self.head)
        self.assertIn("exit 5", self.head)

    def test_exit_5_still_documented_below(self):
        rest = self.b[self.b.index("cat > nanopaid.py"):]
        self.assertIn("Exit 5 prints UNKNOWN", rest)


if __name__ == "__main__":
    unittest.main()
