#!/usr/bin/env python3
"""Law for the per-entry seller check in tools.json (challenge #152).

#151 put the paypercall outage in tools.json as one top-level key, callable_now_caveat. A program that iterates
callable_now and picks an entry never reads that key, and 22 of the 25 entries were sellers that had not answered
since about 10:25 UTC 2026-10-17. Each paypercall entry now names its own /health URL and its last measured check,
and every copy of the outage line ends on the same measured time.

Run: python3 specs/test_tools_json_entry_health.py
"""
import json
import os
import re
import unittest
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
COPIES = ["aidirectory/tools.json", "aidirectory/index.html", "aidirectory.html", "aidirectory/llms.txt",
          "aidirectory-llms.txt", "swap.txt", "bounties.txt"]


def read(rel):
    with open(os.path.join(PUB, rel)) as f:
        return f.read()


class EntryHealth(unittest.TestCase):
    def setUp(self):
        self.t = json.loads(read("aidirectory/tools.json"))

    def test_every_paypercall_entry_names_its_own_health(self):
        sellers = [e for e in self.t["callable_now"] if urlparse(e["url"]).hostname.endswith(".paypercall.dev")]
        self.assertTrue(sellers)
        for e in sellers:
            host = urlparse(e["url"]).hostname
            self.assertEqual(e.get("health"), "https://%s/health" % host, e["name"])

    def test_every_paypercall_entry_carries_a_dated_check(self):
        for e in self.t["callable_now"]:
            if urlparse(e["url"]).hostname.endswith(".paypercall.dev"):
                lc = e.get("last_check") or {}
                self.assertRegex(lc.get("utc", ""), r"^\d{4}-\d\d-\d\dT\d\d:\d\dZ$", e["name"])
                self.assertTrue(lc.get("health") and lc.get("pay"), e["name"])

    def test_free_entries_need_no_health(self):
        for e in self.t["callable_now"]:
            if not urlparse(e["url"]).hostname.endswith(".paypercall.dev"):
                self.assertNotIn("health", e, e["name"])

    def test_caveat_points_at_the_entry_fields(self):
        self.assertIn("health URL and last_check", self.t["callable_now_caveat"])

    def test_outage_end_agrees_everywhere(self):
        ends = set()
        for rel in COPIES:
            found = re.findall(r"to at least (\d\d:\d\d UTC \d{4}-\d\d-\d\d)", read(rel))
            self.assertTrue(found, rel)
            ends.update(found)
        self.assertEqual(len(ends), 1, ends)

    def test_last_check_matches_outage_end(self):
        # since challenge #247 the newest measurement is the sellers' return, not the outage end
        end = re.search(r"(\d\d:\d\d)\s+UTC\s+(\d{4}-\d\d-\d\d),?\s+all five answered", read("bounties.txt"))
        stamp = "%sT%sZ" % (end.group(2), end.group(1))
        for e in self.t["callable_now"]:
            if "last_check" in e:
                self.assertEqual(e["last_check"]["utc"], stamp, e["name"])


if __name__ == "__main__":
    unittest.main()
