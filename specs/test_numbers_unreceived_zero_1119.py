#!/usr/bin/env python3
"""Law: no guide offers /ai/numbers.json's starter "unreceived" figure as current while it is known wrong
(challenge #324).

Measured 2026-11-19: /ai/numbers.json said starter_payments.unreceived 21 until 12:03 UTC and 0 from 13:18 UTC,
starters_sent 29 unchanged and no receive in between. blocks_info with receivable:true on rpc.nano.to at 13:2x UTC:
14 of the 18 starter-sized (10^25 raw) sends from treasury2 and Unstuck's account are still receivable. Same
shape as 2026-10-04 (#95): the box's Nano node is refused (the sellers' upstreams.rpc since ~11:2x UTC), and a
refused read most likely counts as "received". numbers.py runs on the box and is not deployed from this repo
(box fix drafted in drafts/box-numbers-unreceived-refused-read-2026-11-19.md).

Every guide that sent a reader to numbers.json "for the current count" quoted "21 unreceived at 04:03 11-11";
a reader checking now sees 0 and concludes every starter was taken in. This law: each such copy says the field is
wrong today, names the chain count, and no copy still offers the 11-11 figure. When the box's count is fixed and
numbers.json agrees with the chain again, change the texts and this law together.

Run: python3 specs/test_numbers_unreceived_zero_1119.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NUMBERS = "https://172-86-112-140.sslip.io/ai/numbers.json"
TEXTS = ["published/bounties.txt", "published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
         "published/aidirectory/index.html", "published/aidirectory.html", "published/aidirectory/tools.json"]


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class NumbersUnreceivedWrongToday(unittest.TestCase):
    def test_no_copy_offers_the_old_figure(self):
        for rel in TEXTS:
            self.assertNotIn("21 unreceived at", flat(rel), rel)

    def test_each_copy_says_wrong_and_gives_chain_count(self):
        for rel in TEXTS:
            s = flat(rel)
            i = s.find("ledger.json")
            self.assertGreaterEqual(i, 0, rel)
            j = s.find(NUMBERS, i)
            self.assertGreaterEqual(j, 0, rel)
            near = s[j:j + 700]
            self.assertIn("WRONG TODAY", near.upper(), rel)
            self.assertIn("0 since 13:18 UTC 11-19", near, rel)
            self.assertIn("14 of 18", near, rel)
            self.assertIn("rpc.nano.to", near, rel)
            self.assertIn("Count it on chain", near, rel)


if __name__ == "__main__":
    unittest.main()
