#!/usr/bin/env python3
"""Law: the AiDirectory's callable list names the one paid call that answers, with its method (challenge #205).

While the five paypercall.dev sellers are down (since about 10:25 UTC 2026-10-17), the one paid call that answers is
getunstuck.space's x402 echo (0.001 XNO, POST only; a GET answers 404). Before #205 it appeared only inside onboarding
step 6's prose. A program that iterates tools.json's callable_now found 22 paid entries, every one a seller that had
not answered for 16 days, and no working paid call; nothing said which method a URL takes, and on 11-02 23 outside
clients sent GET to the echo and got "not found".

Run: python3 specs/test_aidirectory_lists_live_paid_call.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
ECHO = "https://getunstuck.space/unstuck/api/v1/echo"
TERMS = "https://getunstuck.space/unstuck/api/v1/x402"
UNSTUCK_PAYTO = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"


def read(rel):
    with open(os.path.join(PUB, rel), encoding="utf-8") as f:
        return f.read()


class LivePaidCallListed(unittest.TestCase):
    def setUp(self):
        self.t = json.loads(read("aidirectory/tools.json"))
        self.echo = [e for e in self.t["callable_now"] if e["url"] == ECHO]

    def test_echo_is_a_callable_now_entry(self):
        self.assertEqual(len(self.echo), 1, "callable_now has no entry for the one paid call that answers")

    def test_echo_entry_says_post_and_where_the_terms_are(self):
        e = self.echo[0]
        self.assertEqual(e.get("method"), "POST")
        self.assertEqual(e.get("terms"), TERMS)
        self.assertEqual(e.get("price"), "0.001 XNO")
        self.assertEqual(e.get("pay_to"), UNSTUCK_PAYTO)
        self.assertIn("404", e["what"])  # a GET answers 404: say so where the GET-ers read
        self.assertIn("X-Nano-Payment", e["what"])

    def test_echo_entry_is_first_paid_entry(self):
        paid = [e["name"] for e in self.t["callable_now"] if e["price"] != "free"]
        self.assertEqual(paid[0], self.echo[0]["name"])

    def test_human_copies_list_it(self):
        for rel in ("aidirectory/index.html", "aidirectory.html"):
            html = read(rel)
            # #206: the name links to the terms (GET 200), never to the POST-only call (GET 404)
            self.assertRegex(html, r'<tr><td class="n"><a href="%s">echo</a>' % re.escape(TERMS), rel)
        for rel in ("aidirectory/llms.txt", "aidirectory-llms.txt"):
            self.assertRegex(read(rel), r"- \[echo\]\(%s\) - 0\.001 XNO - POST only" % re.escape(TERMS), rel)

    def test_counts_follow(self):
        n = len(self.t["callable_now"])
        self.assertEqual(self.t["counts"]["callable_now"], n)
        for rel in ("aidirectory/llms.txt", "aidirectory-llms.txt"):
            self.assertIn("(%d callable now," % n, read(rel))


if __name__ == "__main__":
    unittest.main()
