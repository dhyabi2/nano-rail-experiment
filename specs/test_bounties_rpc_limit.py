#!/usr/bin/env python3
"""Law for the rate-limit note under bounties.txt STEP 3 (challenge #94).

Measured 2026-10-04 08:16-08:22 UTC from this keeper's cloud session: every POST to https://rpc.nano.to, even
{"action":"version"}, with any User-Agent, answered {"error":429,"code":"api_key_required_for_heavy_usage",
"message":"Free public RPC limit reached. Create an API key and upgrade to Starter for $1 first month...",
"usage_24h":0}. Steps 3 and 4, section 1's re-check, section 7 and receive.js all send a stranger to that one node,
and nothing said what this reply means, so it read as a $1 paywall in the middle of our free path.

Run: python3 specs/test_bounties_rpc_limit.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class RpcLimitNote(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index(" STEP 3 - READ ANY ACCOUNT")
        self.step3 = " ".join(self.txt[i:self.txt.index(" STEP 4 - ", i)].split())

    def test_names_the_exact_429_reply(self):
        self.assertIn('429 "api_key_required_for_heavy_usage"', self.step3)
        self.assertIn("Free public RPC limit reached", self.step3)

    def test_says_no_key_or_plan_is_needed_and_never_recommends_buying(self):
        self.assertIn("nothing on this page needs a key or a plan", self.step3)
        self.assertNotRegex(self.step3.lower(), r"\b(buy|upgrade to|subscribe)\b")

    def test_gives_the_way_around_and_it_exists_in_receive_js(self):
        self.assertIn("any other node you trust", self.step3)
        self.assertIn("NANO_RPC=<url>", self.step3)
        self.assertIn("RPC=process.env.NANO_RPC||'https://rpc.nano.to'", self.txt)

    def test_the_measurement_is_dated(self):
        self.assertIn("2026-10-04 08:16-08:22 UTC", self.step3)


if __name__ == "__main__":
    unittest.main(verbosity=1)
