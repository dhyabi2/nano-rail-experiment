#!/usr/bin/env python3
"""Law for challenge #262: the AI directory's paid step 6 warns against the sellers' X-BALANCE route.

Every paypercall.dev 402 says "retry with X-PAYMENT header, or use X-BALANCE with a nano_ account that holds a
prepaid balance" (measured 00:2x UTC 2026-11-13). X-BALANCE carries only a public address, and
GET /api/v1/balance?account=<any nano_> answers that address's prepaid balance with no key, so nothing in the
published terms stops another caller who names your address from spending what you prepaid. Until 11-13 none of
the five directory copies named X-BALANCE at all, leaving a stranger to pick the route the 402 offers second.

Run: python3 specs/test_step6_warns_x_balance.py
"""
import html
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
TEXT_COPIES = ["aidirectory/llms.txt", "aidirectory-llms.txt", "aidirectory/index.html", "aidirectory.html"]


def flat(rel):
    with open(os.path.join(PUB, rel)) as f:
        return " ".join(html.unescape(f.read()).split())


class Step6WarnsXBalance(unittest.TestCase):
    def check(self, s, where):
        self.assertIn("NOT X-BALANCE", s, where)
        self.assertIn("only a public address", s, where)
        self.assertIn("Pay each call with X-PAYMENT", s, where)
        # the warning sits after the X-PAYMENT instructions, never before them
        self.assertLess(s.index("X-PAYMENT: <BLOCK_HASH>") if "X-PAYMENT: <BLOCK_HASH>" in s else 0,
                        s.index("NOT X-BALANCE"), where)

    def test_every_text_copy_warns(self):
        for rel in TEXT_COPIES:
            self.check(flat(rel), rel)

    def test_tools_json_warns(self):
        with open(os.path.join(PUB, "aidirectory", "tools.json")) as f:
            step = json.load(f)["onboarding"][5]
        self.check(" ".join(step["how_to_pay"]["then"].split()), "tools.json how_to_pay.then")

    def test_no_copy_recommends_x_balance(self):
        for rel in TEXT_COPIES:
            s = flat(rel)
            self.assertNotIn("use X-BALANCE", s.replace('"X-BALANCE with', ""), rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
