#!/usr/bin/env python3
"""Law for challenge #311 (2026-11-19): every head that offers the paid job says the delivery is not paid yet.

#310 put "NOT PAID YET" in the bounties.txt box, section 9 and both llms.txt heads. Six other heads still offered
"1 XNO for the delivery, once it passes" with no word that our read was not out: canon.txt (26 outside clients on
11-18), canon.html (/canon 27), swap.txt (28), the /ai/ page and its mirror (/ai/ 30), and tools.json's job "now"
(37) - `/ai/traffic/2026-11-18.json`, top_paths_by_clients. Read 00:17 UTC 11-19 on rpc.nano.to: treasury2's
frontier is still 6ECFB21C (a receive of 11-16), so nothing has been sent, 29 h after the 11-17 19:28 UTC close.

When the payout is sent, change this law with the text (and #310's).

Run: python3 specs/test_payout_not_sent_every_head.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADS = ("published/canon.txt", "published/canon.html", "published/swap.txt",
         "published/aidirectory/index.html", "published/aidirectory.html")
SAID = re.compile(r"NOT PAID\s*(?:</strong>\s*)?YET(?:</strong>)? \(read \d\d:\d\d UTC 11-\d\d, \d+ h after the close\)")


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class PayoutNotSentEveryHead(unittest.TestCase):
    def test_each_head_offering_the_job_says_not_paid(self):
        for p in HEADS:
            t = flat(read(p))
            with self.subTest(p):
                self.assertIn("once it passes", t)
                self.assertRegex(t, SAID)
                self.assertIn("the send waits on our operator, with no date", t)

    def test_not_paid_follows_the_job_offer(self):
        for p in HEADS:
            t = flat(read(p))
            with self.subTest(p):
                self.assertLess(t.index("once it passes"), SAID.search(t).start())

    def test_tools_json_job_now_says_not_paid(self):
        tools = json.loads(read("published/aidirectory/tools.json"))
        found = [v for v in json.dumps(tools).split('"') if "A DELIVERY IS IN" in v]
        self.assertTrue(found)
        self.assertRegex(found[0], SAID)

    def test_mirror_identical(self):
        self.assertEqual(read("published/aidirectory/index.html"), read("published/aidirectory.html"))

    def test_law_fails_on_the_old_head(self):
        old = flat("so no verdict is paid; the row is undecided and we read the delivery ourselves. Read it,")
        self.assertIsNone(SAID.search(old))


if __name__ == "__main__":
    unittest.main()
