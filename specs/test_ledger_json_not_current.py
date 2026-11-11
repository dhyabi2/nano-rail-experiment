#!/usr/bin/env python3
"""Law: no guide sends a reader to ledger.json as the current starter count without saying it predates treasury2
(challenge #251).

Measured 2026-11-11 04:2x UTC: https://getunstuck.space/ledger.json, which bounties.txt section 5 and every AI
directory copy offer as the openings ledger "published honestly", says "updated": "2026-10-29", opener the Unstuck
account, starters_sent 23, unreceived 16. The same hour /ai/numbers.json said starters_sent 29, unreceived 21, and
treasury2 (nano_3z335ug5...) had sent six starters since 2026-11-08, five still receivable at their payees
(blocks_info). A sceptical agent that checks our "honest" ledger against the chain finds six starters missing and a
different sender, and has no line telling it why. ledger.json is written on the box, not from this repository.

This law: every published copy that links ledger.json also says it is STALE, names treasury2's full address, and
points at numbers.json for the current count. When the box rewrites ledger.json to include treasury2, change the
texts and this law together.

Run: python3 specs/test_ledger_json_not_current.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = "https://getunstuck.space/ledger.json"
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"
NUMBERS = "https://172-86-112-140.sslip.io/ai/numbers.json"
TEXTS = ["published/bounties.txt", "published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
         "published/aidirectory/index.html", "published/aidirectory.html"]


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class LedgerJsonNotCurrent(unittest.TestCase):
    def test_every_text_copy_says_stale(self):
        for rel in TEXTS:
            s = flat(rel)
            i = s.find(LEDGER)
            self.assertGreaterEqual(i, 0, rel + " no longer links ledger.json: update this law")
            near = s[i:i + 900]
            self.assertIn("STALE", near, rel)
            self.assertIn("2026-10-29", near, rel)
            self.assertIn(TREASURY2, near, rel)
            self.assertIn(NUMBERS, near, rel)

    def test_tools_json_entry_says_stale(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            tools = json.load(f)
        found = []

        def walk(o):
            if isinstance(o, dict):
                if o.get("url") == LEDGER:
                    found.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(tools)
        self.assertTrue(found, "tools.json no longer lists ledger.json: update this law")
        for entry in found:
            what = entry.get("what", "")
            self.assertIn("STALE", what)
            self.assertIn(TREASURY2, what)
            self.assertIn(NUMBERS, what)


if __name__ == "__main__":
    unittest.main()
