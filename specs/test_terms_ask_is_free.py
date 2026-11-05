#!/usr/bin/env python3
"""Law: every copy that sends a stranger to our x402 terms says posting an ask is free (challenge #199).

Measured 2026-11-01 16:20 UTC: GET https://getunstuck.space/unstuck/api/v1/x402 (15 outside clients that day, one of
the most-read paths) describes the route as "pay 0.001 XNO to post an ask with a Nano bounty". POST /unstuck/api/ask
answered a missing asker and a missing title with 400 and never asked for payment: posting an ask is free, and the
0.001 XNO buys only the echo call. An agent that believes the terms thinks the cheapest conversion we offer costs money.

Run: python3 specs/test_terms_ask_is_free.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTS = ["published/bounties.txt", "published/swap.txt", "published/aidirectory/llms.txt",
         "published/aidirectory-llms.txt", "published/aidirectory/index.html"]


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().replace("&quot;", '"').split())


class TermsSayAskIsFree(unittest.TestCase):
    def check(self, name, s):
        i = s.index("curl -s https://getunstuck.space/unstuck/api/v1/x402")
        j = s.index("/unstuck/api/v1/echo", i)
        near = s[i:j]
        self.assertIn("post an ask", near, name)
        self.assertIn("posting an ask is free", near, name)
        self.assertIn("buys only this echo call", near, name)

    def test_text_copies(self):
        for rel in TEXTS:
            self.check(rel, flat(rel))

    def test_tools_json(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            t = json.load(f)
        found = []

        def walk(o):
            if isinstance(o, dict):
                if "terms_cmd" in o and "v1/x402" in o["terms_cmd"]:
                    found.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(t)
        self.assertTrue(found)
        for o in found:
            self.assertIn("posting an ask is free", o["terms"])
            self.assertIn("buys only this echo call", o["terms"])


if __name__ == "__main__":
    unittest.main()
