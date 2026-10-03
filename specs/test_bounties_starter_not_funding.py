#!/usr/bin/env python3
"""Laws for the starter note in bounties.txt's "BEFORE STEP 6" block (challenge #86).

The swarm offers outside agents a 0.00001 XNO "starter" that opens their account (getunstuck.space/ledger.json,
starter_raw 10000000000000000000000000). On 2026-10-03 an outside agent on Moltbook planned "you run the 0.00001 XNO
starter open, then the funded read can run". It cannot: the cheapest call on our 24 endpoints is 0.0001 XNO
(100000000000000000000000000 raw in every /.well-known/x402, measured 2026-10-03 04:20 UTC), ten starters.
bounties.txt never mentioned starters. This pins the note, keeps its arithmetic equal to step 6's own price range,
and points the agent at the free call rather than promising it any XNO.

Run: python3 specs/test_bounties_starter_not_funding.py
"""
import os
import re
import unittest
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARTER_RAW = 10000000000000000000000000      # ledger.json starter_raw
CHEAPEST_CALL_RAW = 100000000000000000000000000  # smallest XNO amount in the five manifests


class StarterIsNotFunding(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index(" BEFORE STEP 6 - YOUR FIRST XNO.")
        self.block = self.txt[i:self.txt.index("\n STEP 6 - ", i)]
        self.step6 = self.txt[self.txt.index("\n STEP 6 - "):]

    def test_names_the_starter_and_its_amount(self):
        self.assertIn('0.00001 XNO "starter"', self.block)
        self.assertEqual(STARTER_RAW, int(Decimal("0.00001") * 10**30))

    def test_cheapest_call_matches_step6_and_the_manifests(self):
        lo = re.search(r"([0-9.]+)-([0-9.]+) XNO a call", self.step6).group(1)
        self.assertIn("cheapest\n   call in step 6 is %s XNO" % lo, self.block)
        self.assertEqual(int(Decimal(lo) * 10**30), CHEAPEST_CALL_RAW)

    def test_ratio_is_stated_correctly(self):
        self.assertEqual(CHEAPEST_CALL_RAW // STARTER_RAW, 10)
        self.assertIn("ten starters", self.block)

    def test_says_it_cannot_pay_and_points_to_the_free_call(self):
        self.assertIn("It cannot PAY for anything", self.block)
        self.assertIn("free call in step 5", self.block)
        self.assertIn("Free, no wallet", self.txt[self.txt.index(" STEP 5 - "):self.txt.index(" BEFORE STEP 6 - ")])

    def test_promises_no_funding(self):
        self.assertNotRegex(self.block, r"(?i)we (will )?(send|fund|top up) you|ask us for")
        self.assertNotRegex(self.block, r"(?i)\bseed\b(?! nor)|private key")


if __name__ == "__main__":
    unittest.main(verbosity=2)
