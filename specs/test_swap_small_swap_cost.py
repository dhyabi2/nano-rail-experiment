#!/usr/bin/env python3
"""Law for the cost of a small swap (challenge #183).

On 2026-10-29 at 21:36 and 22:39 UTC two outside agents on Moltbook (latte6, clawbait) said Nano's feeless rail is
not free to get onto: converting a small amount to XNO costs a share comparable to the fee it saves, "until someone
tops up in bulk". swap.txt told every newcomer to swap "just over the 0.230737 minimum", and bounties.txt's operator
request suggested 0.50 USDC, yet no line showed what a small swap costs per USDC or told the reader to swap once.
swap.txt section 2 now gives two GETs that compare the reader's size against a big one, says swap once, and says who
pays; step 3 says the minimum is the cheapest mistake, not the cheapest XNO; bounties.txt points there.

Run: python3 specs/test_swap_small_swap_cost.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COMPARE = ('for a in 1 100; do curl -s "https://api.nanswap.com/v1/get-estimate?from=USDC-BASE&to=XNO&amount=$a"; '
           'echo; done')


def flat(path):
    with open(os.path.join(ROOT, path)) as f:
        return " ".join(f.read().split())


def section2():
    s = flat("published/swap.txt")
    return s[s.index(" 2. THE LIMITS AND THE RATE"):s.index(" 3. WHAT \"LISTED\"")]


class SmallSwapCost(unittest.TestCase):
    def test_section2_compares_sizes(self):
        self.assertIn("WHAT A SMALL SWAP COSTS YOU", section2())
        self.assertIn(COMPARE, section2())

    def test_says_swap_once(self):
        self.assertIn("Swap ONCE", section2())

    def test_says_who_pays(self):
        s = section2()
        self.assertIn("Who pays it: whoever swaps", s)
        self.assertIn("never swapped", s)

    def test_outside_figure_not_claimed_as_ours(self):
        # the 9% is a reporter's figure; we did not measure it and must say so
        s = section2()
        self.assertIn("about 9%", s)
        self.assertIn("we have not re-measured that ourselves", s)

    def test_step3_minimum_is_not_cheapest_xno(self):
        s = flat("published/swap.txt")
        step3 = s[s.index(" 3. Swap a SMALL amount first"):s.index(" 4. Confirm it arrived")]
        self.assertIn("cheapest MISTAKE, not the cheapest XNO", step3)
        self.assertIn("in ONE go", step3)

    def test_bounties_points_to_section(self):
        self.assertIn('swap.txt section 2, "WHAT A SMALL SWAP COSTS YOU"', flat("published/bounties.txt"))


if __name__ == "__main__":
    unittest.main()
