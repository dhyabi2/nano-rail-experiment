#!/usr/bin/env python3
"""Law for the paid call that answers while the paypercall sellers are down (challenge #153).

Measured 2026-10-25 00:19 UTC: all five paypercall hosts still gave no answer (curl 000, 10 s cap), and STEP 6 in
bounties.txt and in every AiDirectory copy said only "skip this step". But getunstuck.space's own x402 route
answered: GET /unstuck/api/v1/x402 gave 200 with XNO terms (0.001 XNO to our Unstuck account), and POST
/unstuck/api/v1/echo gave 402 with the same terms. On 10-24, 9 outside clients asked for /unstuck/api/v1/echo, where
a GET answers 404 (`/ai/traffic/2026-10-24.json`). Every copy of step 6 now names that route, says it is a POST, gives the payee
in full, says the XNO comes back to us, and says the paid answer is not yet measured.

Run: python3 specs/test_step6_live_paid_call.py
"""
import html
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
from nano_address import check_nano_address  # noqa: E402

UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
TERMS = "curl -s https://getunstuck.space/unstuck/api/v1/x402"
POST = "curl -s -X POST https://getunstuck.space/unstuck/api/v1/echo"
TEXT_COPIES = ["published/bounties.txt", "published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
               "published/aidirectory/index.html", "published/aidirectory.html"]


def flat(path):
    with open(os.path.join(ROOT, path)) as f:
        t = f.read()
    if path.endswith(".html"):
        t = html.unescape(t)
    return " ".join(t.split())


class LivePaidCall(unittest.TestCase):
    def test_every_copy_names_the_live_route_after_the_seller_check(self):
        for p in TEXT_COPIES:
            s = flat(p)
            i = s.index("000 means no answer, so do not pay")
            for needle in (TERMS, POST, UNSTUCK, "a GET answers 404", "X-Nano-Payment: <BLOCK_HASH>",
                           "not income", "not measured"):
                self.assertIn(needle, s[i:], f"{p}: {needle!r} missing after the seller check")

    def test_payee_is_a_valid_address_and_the_only_one_named(self):
        self.assertTrue(check_nano_address(UNSTUCK))
        for p in TEXT_COPIES:
            s = flat(p)
            i = s.index("ONE PAID CALL OF OURS DOES ANSWER")
            block = s[i:i + 1200]
            self.assertEqual(block.count("nano_1"), 1, p)

    def test_post_command_sends_json(self):
        for p in TEXT_COPIES:
            s = flat(p)
            line = s[s.index(POST):s.index(POST) + 200]
            self.assertIn("-H 'Content-Type: application/json'", line, p)
            self.assertIn("-d '{\"hello\"", line, p)

    def test_tools_json_carries_it_as_data(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            d = json.load(f)
        w = d["onboarding"][5]["check_first"]["while_down"]
        self.assertEqual(w["terms_cmd"], TERMS)
        self.assertTrue(w["cmd"].startswith(POST))
        self.assertIn(UNSTUCK, w["terms"])
        self.assertIn("not measured", w["then"])

    def test_amount_matches_raw(self):
        # 0.001 XNO is 10^27 raw; a wrong exponent would tell a stranger to overpay or underpay
        for p in TEXT_COPIES:
            self.assertIn("0.001 XNO (amount 1000000000000000000000000000 raw)", flat(p), p)
        self.assertEqual(10 ** 27, int("1000000000000000000000000000"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
