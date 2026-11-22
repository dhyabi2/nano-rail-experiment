#!/usr/bin/env python3
"""Law for challenge #337 (2026-11-22): every published surface carries the same NOT PAID YET stamp.

#321's law (specs/test_not_paid_names_seller_asked.py) checks one stamp across bounties.txt, canon.txt and the two
llms.txt copies. It never read tools.json, the directory page, canon.html or swap.txt, and those five still said
"NOT PAID YET (read 00:17 UTC 11-19, 29 h after the close)" at 17:2x UTC 11-22, when every other head said 15:20
UTC 11-22, 116 h. tools.json's own read_first line said 15:2x UTC 11-22, so the file contradicted itself, and
"updated" still read 2026-11-17. The keeper's buyer read of the manifest (17:2x UTC 11-22) found it. Re-read 17:1x
UTC 11-22 (rpc.nano.to): treasury2 frontier 6ECFB21C, so nothing has been sent and the 15:20 line still holds.

Run: python3 specs/test_not_paid_one_stamp_all_surfaces.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SURFACES = (
    "published/bounties.txt",
    "published/canon.txt",
    "published/swap.txt",
    "published/canon.html",
    "published/aidirectory.html",
    "published/aidirectory/index.html",
    "published/aidirectory/tools.json",
    "published/aidirectory/llms.txt",
    "published/aidirectory-llms.txt",
)
STAMP = re.compile(r"(?:NOT PAID YET \(read|Not paid yet: read) (\d\d:\d\d UTC (?:2026-)?11-\d\d)", re.I)


def flat(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        t = f.read()
    t = re.sub(r"<[^>]+>", "", t)
    return " ".join(t.split())


class OneStamp(unittest.TestCase):
    def test_every_stamp_is_the_same(self):
        stamps = {}
        for p in SURFACES:
            for s in STAMP.findall(flat(p)):
                stamps.setdefault(s.replace("2026-", ""), []).append(p)
        self.assertTrue(stamps)
        self.assertEqual(len(stamps), 1, stamps)

    def test_old_stamp_gone_everywhere(self):
        for p in SURFACES:
            with self.subTest(p):
                self.assertNotIn("read 00:17 UTC 11-19", flat(p))

    def test_tools_json_updated_not_older_than_its_stamp(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json"), encoding="utf-8") as f:
            d = json.load(f)
        self.assertGreaterEqual(d["updated"], "2026-11-22")

    def test_law_fails_on_the_old_text(self):
        old = "NOT PAID YET (read 00:17 UTC 11-19, 29 h after the close) ... NOT PAID YET (read 15:20 UTC 11-22, 116 h"
        self.assertEqual(len(set(STAMP.findall(old))), 2)


if __name__ == "__main__":
    unittest.main()
