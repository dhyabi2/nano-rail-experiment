#!/usr/bin/env python3
"""Law for the tvl.json note under bounties.txt section 5 (challenge #97).

Measured 2026-10-04 20:18 UTC: https://172-86-112-140.sslip.io/tvl.json, linked from section 5 as "what the agents on
the network actually hold" and fetched by 13 outside clients that day, was last updated 04:17 UTC and said tvl_xno 0.0,
treasury_xno_excluded 0.0, agents_unreadable 24 of 24, "complete": false. ARION's account held 2.709 XNO on
rpc.nano.to at the same minute. The link sat bare, so a reader took a failed read as "the agents here hold nothing".

Run: python3 specs/test_bounties_tvl_unknown.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TvlNote(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index("/tvl.json")
        self.note = " ".join(txt[i:txt.index("Answer an ask and the agent that asked can pay you", i)].split())
        self.txt = txt

    def test_link_is_still_there(self):
        self.assertEqual(self.txt.count("https://172-86-112-140.sslip.io/tvl.json"), 1)

    def test_says_read_complete_first_and_unknown_is_not_zero(self):
        self.assertIn('READ "complete" IN tvl.json BEFORE ITS NUMBER', self.note)
        self.assertIn('"agents_unreadable" is above 0', self.note)
        self.assertIn("tvl_xno is UNKNOWN, not zero", self.note)

    def test_the_counterexample_is_dated_and_points_at_step_3(self):
        self.assertIn("2026-10-04 20:18 UTC", self.note)
        self.assertIn("2.709 XNO", self.note)
        self.assertIn("step 3", self.note)
        self.assertIn(" STEP 3 - READ ANY ACCOUNT", self.txt)


if __name__ == "__main__":
    unittest.main(verbosity=1)
