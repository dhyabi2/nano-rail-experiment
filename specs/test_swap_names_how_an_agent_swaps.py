#!/usr/bin/env python3
"""Law: swap.txt tells an agent with no browser how the swap itself is made (challenge #263).

swap.txt is the only route we publish to a first XNO (USDC on Base -> XNO). Its section 1 names three pair pages on
nanswap.com - web forms for a person - and section 4 step 3 says "Swap a SMALL amount first" with no command. The
only commands on the page are the keyless get-limits and get-estimate GETs, so an autonomous agent following it
reaches the money step with nothing to run. Meanwhile every paypercall.dev seller's 402 carries a "rail-hint"
extension that names an outside tool ("pip install feeless402 && nano-pay init", "nano-pay topup 5 --asset
USDC-BASE --execute"), which the page never mentioned; that tool's own README says the order step needs a Nanswap
API key.

Law: step 3 of section 4 says the pair pages are for a person, that making an order is not keyless, where a keyless
agent goes instead (its operator, through bounties.txt's BEFORE STEP 6 request), names the seller 402's rail-hint
tool as outside and unrun by us, and still keeps the keyless GETs in section 2.

Run: python3 specs/test_swap_names_how_an_agent_swaps.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def step3():
    s = read("published/swap.txt")
    a = s.index(" 3. Swap a SMALL amount first")
    b = s.index(" 4. Confirm it arrived on the chain")
    return " ".join(s[a:b].split())


class SwapNamesHowAnAgentSwaps(unittest.TestCase):
    def test_pair_pages_are_for_a_person(self):
        self.assertIn("NO BROWSER?", step3())
        self.assertIn("web forms for a person", step3())

    def test_order_is_not_keyless(self):
        s = step3()
        self.assertIn("NOT keyless", s)
        self.assertIn("API key", s)

    def test_keyless_agent_is_sent_to_its_operator(self):
        s = step3()
        self.assertIn("operator", s)
        self.assertIn('"BEFORE STEP 6 - YOUR FIRST XNO"', s)
        self.assertIn("BEFORE STEP 6 - YOUR FIRST XNO", read("published/bounties.txt"))

    def test_rail_hint_tool_named_as_outside(self):
        s = step3()
        self.assertIn("rail-hint", s)
        self.assertIn("feeless402", s)
        self.assertIn("not ours", s)
        self.assertIn("We have not run it", s)

    def test_keyless_gets_still_there(self):
        s = read("published/swap.txt")
        self.assertIn("api.nanswap.com/v1/get-limits?from=USDC-BASE&to=XNO", s)
        self.assertIn("api.nanswap.com/v1/get-estimate?from=USDC-BASE&to=XNO", s)

    def test_lines_fit(self):
        s = read("published/swap.txt")
        a = s.index("    NO BROWSER?")
        b = s.index(" 4. Confirm it arrived on the chain")
        for line in s[a:b].splitlines():
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
