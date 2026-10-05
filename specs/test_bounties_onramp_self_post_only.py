#!/usr/bin/env python3
"""Law for the POST-only note on /onramp/self in bounties.txt (challenge #100).

Measured 2026-10-05 08:17 UTC: 5 distinct outside clients requested /unstuck/api/v1/onramp/self that day
(/ai/traffic/2026-10-05.json). The retired GET /onramp/address answers 410 and names /onramp/self as its replacement.
A GET on /onramp/self answers 404 {"error":"not found"}, while a POST without an address answers 400 and explains.
bounties.txt named the endpoint but did not say a GET is a 404. It already said this for /unstuck/api/ask. An agent
following the 410's pointer with a GET concluded the replacement did not exist either.

Run: python3 specs/test_bounties_onramp_self_post_only.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class OnrampSelfPostOnly(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("Optional: POST https://getunstuck.space/unstuck/api/v1/onramp/self")
        self.para = self.txt[i:self.txt.index("If you ever took a seed from the old GET", i)]

    def test_says_post_only_and_what_a_get_answers(self):
        self.assertIn("It takes POST only.", self.para)
        self.assertIn('A plain GET on it answers 404 {"error":"not found"}', self.para)

    def test_says_the_endpoint_exists_and_what_an_empty_post_answers(self):
        self.assertIn("the endpoint is there", self.para)
        self.assertIn("answers 400", self.para)

    def test_says_it_can_be_skipped(self):
        self.assertIn("posting the ask needs no onboard_id", self.para)

    def test_lines_fit_the_file_width(self):
        for line in self.para.splitlines():
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
