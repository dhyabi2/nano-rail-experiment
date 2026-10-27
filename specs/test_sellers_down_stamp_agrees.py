#!/usr/bin/env python3
"""Law: every published copy dates the sellers' outage to the same measured end, and none says they answer (challenge #170).

Measured 2026-10-27 20:22 UTC: all five paypercall hosts gave no answer (curl 000, 10 s cap), as they had since about
10:25 UTC 10-17. Every guide still said the outage ran "to at least 00:19 UTC 2026-10-25", 2.8 days stale, and
bounties.txt's WHAT WORKS WITHOUT OUR AGENTS still said the 5 free calls "answered with real data at 16:20 UTC the
same day" - a sentence from before the outage. #152 says each re-check moves the stamp forward; this law makes the
seven copies move together, so a reader of any one sees the same measurement.

Run: python3 specs/test_sellers_down_stamp_agrees.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ["published/bounties.txt", "published/swap.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/llms.txt", "published/aidirectory.html", "published/aidirectory/index.html",
          "published/aidirectory/tools.json"]
STAMP = re.compile(r"10:25 UTC 2026-10-17 to at least (\d\d:\d\d UTC \d{4}-\d\d-\d\d)")


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class SellersDownStampAgrees(unittest.TestCase):
    def test_every_copy_carries_the_stamp(self):
        for rel in COPIES:
            self.assertTrue(STAMP.search(read(rel)), rel + " has no dated outage end")

    def test_all_stamps_are_one_measurement(self):
        stamps = {m for rel in COPIES for m in STAMP.findall(read(rel))}
        self.assertEqual(len(stamps), 1, "copies disagree on the outage end: %s" % sorted(stamps))

    def test_tools_json_last_checks_match_the_stamp(self):
        stamp = STAMP.search(read("published/bounties.txt")).group(1)  # "20:22 UTC 2026-10-27"
        hm, _, day = stamp.split()
        want = "%sT%sZ" % (day, hm)
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            doc = json.load(f)
        seen = []

        def walk(o):
            if isinstance(o, dict):
                if "last_check" in o and "paypercall.dev" in str(o.get("health")):
                    seen.append(o["last_check"]["utc"])
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(doc)
        self.assertTrue(seen)
        self.assertEqual(set(seen), {want})

    def test_no_copy_says_the_free_calls_answer(self):
        for rel in COPIES:
            self.assertNotIn("answered with real data", read(rel), rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
