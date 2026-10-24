#!/usr/bin/env python3
"""Law for STEP 6's seller check in bounties.txt (challenge #149).

Measured 2026-10-24 08:1x UTC: the guides were back after the 10-17 outage, but all five paypercall hosts, which run
on one box of ours, had answered nothing since about 10:25 UTC 10-17 (timeouts from this session and from GitHub's
runners, issue #121). STEP 6 still said "spend it" there, and WHAT WORKS WITHOUT OUR AGENTS still said the free
calls answer with real data. A stranger who sends XNO to payTo while the sellers are down buys nothing. STEP 6 now
gives a dated measurement and a bounded check command that prints each host's status, says 000 means do not pay,
and names the steps that need no seller.

Run: python3 specs/test_bounties_sellers_down_check.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOSTS = ["extract", "search", "domain", "check", "geoip"]


class SellersDownCheck(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("STEP 6 - ")
        self.step6 = self.txt[i:self.txt.index("HOW A CALL IS PAID", i)]

    def test_check_comes_before_the_how_to_pay(self):
        self.assertIn("CHECK THEY ANSWER BEFORE YOU SEND ANY XNO", self.step6)

    def test_command_covers_every_host_and_is_bounded(self):
        cmd = next(ln.strip() for ln in self.step6.splitlines() if ln.strip().startswith("for h in"))
        self.assertEqual(re.search(r"for h in ([a-z ]+); do", cmd).group(1).split(), HOSTS)
        self.assertIn("-m 10", cmd)  # a dead host must not hang the reader
        self.assertIn("https://$h.paypercall.dev/health", cmd)
        self.assertIn("%{http_code}", cmd)
        self.assertNotIn("X-PAYMENT", cmd)  # the check never pays

    def test_says_what_000_means_and_what_still_works(self):
        s = " ".join(self.step6.split())
        self.assertIn("000 means no answer, so do not pay", s)
        self.assertIn("section 2", s)
        self.assertIn("section 5", s)
        self.assertNotIn("STEP 7", s)  # there is no STEP 7

    def test_outage_is_dated_not_claimed_current(self):
        s = " ".join(self.step6.split())
        self.assertIn("2026-10-17", s)
        # the end is a measured time, moved forward by each re-check (#152), never "still down"
        self.assertRegex(s, r"at least \d\d:\d\d UTC \d{4}-\d\d-\d\d")

    def test_what_works_bullet_points_at_the_check(self):
        i = self.txt.index("WHAT WORKS WITHOUT OUR AGENTS")
        block = " ".join(self.txt[i:i + 900].split())
        self.assertIn("run STEP 6's check before you count on them", block)


if __name__ == "__main__":
    unittest.main(verbosity=2)
