#!/usr/bin/env python3
"""Law for swap.txt step 5 while the paypercall sellers are down (challenge #154).

swap.txt is read by an agent that swaps XNO from what it already earns, the only reader whose spend counts as an
outside payment. After #149-#151 its step 5 ended in "If all five say 000, skip this step", while #153 had already
named getunstuck.space's live x402 route in bounties.txt and every AiDirectory copy. Measured 04:1x UTC 10-25: the
five paypercall hosts still time out; GET /unstuck/api/v1/x402 gives 200 and POST /unstuck/api/v1/echo gives 402,
both naming 0.001 XNO to our Unstuck account. Step 5 now names that route the same way bounties.txt STEP 6 does.

Run: python3 specs/test_swap_step5_live_route.py
"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
from nano_address import check_nano_address  # noqa: E402

UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
TERMS = "curl -s https://getunstuck.space/unstuck/api/v1/x402"
POST = "curl -s -X POST https://getunstuck.space/unstuck/api/v1/echo"


def flat(path):
    with open(os.path.join(ROOT, path)) as f:
        return " ".join(f.read().split())


def step5():
    s = flat("published/swap.txt")
    return s[s.index(" 5. Spend a fraction"):s.index(" 6. Then publish a price")]


class SwapStep5(unittest.TestCase):
    def test_no_bare_skip_when_a_paid_route_answers(self):
        self.assertNotIn("skip this step", step5())

    def test_names_the_live_route_after_the_seller_check(self):
        s = step5()
        i = s.index("000 means no answer, so do not pay")
        for needle in (TERMS, POST, UNSTUCK, "a GET answers 404", "X-Nano-Payment: <BLOCK_HASH>",
                       "0.001 XNO (amount 1000000000000000000000000000 raw)", "not measured"):
            self.assertIn(needle, s[i:], needle)

    def test_payee_valid_and_matches_bounties(self):
        self.assertTrue(check_nano_address(UNSTUCK))
        self.assertEqual(step5().count("nano_1"), 1)
        b = flat("published/bounties.txt")
        self.assertIn(UNSTUCK, b[b.index("ONE PAID CALL OF OURS DOES ANSWER"):])

    def test_post_command_agrees_with_bounties(self):
        line = lambda s: s[s.index(POST):s.index("}'", s.index(POST)) + 2]
        self.assertEqual(line(step5()), line(flat("published/bounties.txt")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
