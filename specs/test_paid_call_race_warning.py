#!/usr/bin/env python3
"""Law: every copy of the one live paid call warns that its fixed price lets a watcher spend the buyer's hash (challenge #179).

Measured 2026-10-29 08:24 UTC: GET /unstuck/api/v1/x402 and two unpaid POSTs to /unstuck/api/v1/echo named the same
amount (10^27 raw) every time, and the paid retry carries only `X-Nano-Payment: <BLOCK_HASH>`. A Nano block has no
memo, so the route cannot tell who sent a block that pays it: anyone watching nano_1434...'s public history can
present a buyer's hash first. #178 told sellers to quote a new amount per 402 for exactly this reason, while every
guide still sent buyers to our own fixed-price route with no word of it. Until the route quotes per request (the
owner's, server-side), each copy tells the buyer to make the send and the paid POST in one go and keep the hash.

Run: python3 specs/test_paid_call_race_warning.py
"""
import html
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ["published/bounties.txt", "published/swap.txt", "published/aidirectory/llms.txt",
          "published/aidirectory-llms.txt", "published/aidirectory/index.html", "published/aidirectory.html"]
NEEDLES = ("one fixed amount for every buyer", "carries only the hash", "present your hash before you do",
           "the moment the node returns your block's hash", "it is your receipt")


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        t = f.read()
    if rel.endswith(".html"):
        t = html.unescape(t)
    return " ".join(t.split())


class PaidCallRaceWarning(unittest.TestCase):
    def test_every_copy_warns_after_the_paid_header(self):
        for rel in COPIES:
            s = flat(rel)
            i = s.index("X-Nano-Payment: <BLOCK_HASH>")
            tail = s[i:i + 900]
            for n in NEEDLES:
                self.assertIn(n, tail, "%s: %r missing after the paid header" % (rel, n))

    def test_tools_json_carries_it_as_data(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            w = json.load(f)["onboarding"][5]["check_first"]["while_down"]
        for n in NEEDLES:
            self.assertIn(n, w["then"])

    def test_guides_point_at_the_seller_rule(self):
        # the buyer-side warning and the seller-side rule (#178) must name the same remedy
        for rel in COPIES[:1] + COPIES[2:]:
            self.assertIn("quote a new amount per 402", flat(rel), rel)
        self.assertIn("QUOTE A NEW AMOUNT IN EVERY 402", flat("published/bounties.txt"))

    def test_no_copy_keeps_the_old_measurement(self):
        for rel in COPIES + ["published/aidirectory/tools.json"]:
            self.assertNotIn("Measured 20:20 UTC 10-27", flat(rel), rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
