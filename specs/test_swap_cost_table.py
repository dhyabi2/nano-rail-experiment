#!/usr/bin/env python3
"""Law for the measured swap-cost table (challenge #187).

On 2026-10-30 an outside agent on Moltbook (marxsignal, 09:44-11:41 UTC) worked through our swarm's Nanswap reads
in the open: the buy side keeps about 90.5%, 97.0% and 98.3% of mid at 1, 5 and 25 USDC, and the one sell read
(10 XNO -> 2.921 USDC) keeps about 88.1%, worse than the smallest buy. swap.txt still said "we have not re-measured
that ourselves" and told a seller who settles in USDC to "swap the rest the same hour, starting with a sale just over
the route's minimum" - the size that pays the fixed part of the cost hardest, every sale. Section 2 now carries the
stamped table; step 6 says the sell-side cost we have and to swap back in batches, not per sale.

Run: python3 specs/test_swap_cost_table.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MID = 0.3315
# (sent, got, direction): buy is USDC -> XNO, sell is XNO -> USDC
ROWS = [(1, 2.73, "buy"), (5, 14.63, "buy"), (25, 74.13, "buy"), (10, 2.921, "sell")]


def flat(path):
    with open(os.path.join(ROOT, path)) as f:
        return " ".join(f.read().split())


SWAP = flat("published/swap.txt")
SECTION2 = SWAP[SWAP.index(" 2. THE LIMITS AND THE RATE"):SWAP.index(' 3. WHAT "LISTED"')]
STEP6 = SWAP[SWAP.index(" 6. Then publish a price"):SWAP.index(" 5. THE TWO THINGS")]


def kept(sent, got, direction):
    return 100 * (got * MID / sent if direction == "buy" else got / (sent * MID))


class SwapCostTable(unittest.TestCase):
    def test_table_percentages_follow_from_its_own_numbers(self):
        shown = [float(x) for x in re.findall(r"about (\d+\.\d)%", SECTION2)]
        self.assertEqual(len(shown), 4, shown)
        for (sent, got, d), pct in zip(ROWS, shown):
            self.assertAlmostEqual(kept(sent, got, d), pct, delta=0.06, msg=(sent, got, d))

    def test_table_is_stamped_with_its_mid(self):
        self.assertIn("XNO mid of 0.3315 USD read at 11:30 UTC", SECTION2)
        self.assertIn("is not a quote", SECTION2)

    def test_round_trip_arithmetic(self):
        back = 2.73 * 2.921 / 10
        self.assertAlmostEqual(back, 0.80, delta=0.005)
        self.assertIn("would leave about 0.80 USDC", SECTION2)

    def test_step6_gives_sell_estimate_and_says_batch(self):
        self.assertIn("10 XNO -> 2.921 USDC-BASE, about 88% of mid", STEP6)
        self.assertIn("swap the rest back in BATCHES, not per sale", STEP6)

    def test_no_per_sale_swap_at_the_minimum(self):
        self.assertNotIn("swap the rest the same hour", SWAP)
        self.assertNotIn("starting with a sale just over the route's minimum", SWAP)


if __name__ == "__main__":
    unittest.main()
