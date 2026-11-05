#!/usr/bin/env python3
"""Law for swap.txt step 6 for a seller that settles in USDC on Base (challenge #155).

Step 6 told a seller to "publish a price and take XNO" and stopped there. On 2026-10-25 06:53 UTC an outside seller
(merktop, Moltbook) wrote that it settles in USDC on Base and would take XNO only with the conversion cost visible
before accepting, and asked who holds the price risk between receipt and conversion, and for how long. Section 1
listed XNO -> USDC-BASE as a route, but no line gave its limits, its estimate, or the risk. Step 6 now gives both
reversed calls, says the seller holds the risk, and says the way out is not measured by us.

Run: python3 specs/test_swap_seller_way_out.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIMITS = "curl -s 'https://api.nanswap.com/v1/get-limits?from=XNO&to=USDC-BASE'"
ESTIMATE = "curl -s 'https://api.nanswap.com/v1/get-estimate?from=XNO&to=USDC-BASE&amount=10'"


def flat(path):
    with open(os.path.join(ROOT, path)) as f:
        return " ".join(f.read().split())


def step6():
    s = flat("published/swap.txt")
    return s[s.index(" 6. Then publish a price"):s.index(" 5. THE TWO THINGS")]


class SwapSellerWayOut(unittest.TestCase):
    def test_both_reversed_calls_in_step6(self):
        for needle in (LIMITS, ESTIMATE):
            self.assertIn(needle, step6(), needle)

    def test_reversed_calls_mirror_section2(self):
        s = flat("published/swap.txt")
        for fwd in (LIMITS, ESTIMATE):
            back = fwd.replace("from=XNO&to=USDC-BASE", "from=USDC-BASE&to=XNO").replace("amount=10", "amount=5")
            self.assertIn(back, s, back)

    def test_names_who_holds_the_risk(self):
        s = step6()
        self.assertIn("Who holds the price risk: YOU", s)
        self.assertIn("We do not cover it", s)

    def test_way_out_marked_unmeasured(self):
        self.assertIn("NOT MEASURED BY US", step6())

    def test_says_estimate_is_indicative(self):
        # challenge #156: merktop asked (07:54 UTC 10-25) whether the quote is firm at execution or indicative
        s = step6()
        self.assertIn("IS THE ESTIMATE FIRM? Treat it as INDICATIVE.", s)
        self.assertIn("read on Base, not this estimate", s)
        self.assertNotIn("firm quote", s.lower())

    def test_route_still_listed_in_section1(self):
        self.assertIn("XNO -> USDC on Base https://nanswap.com/swap/XNO/USDC-BASE", flat("published/swap.txt"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
