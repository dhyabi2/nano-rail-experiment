#!/usr/bin/env python3
"""Law: no guide offers /ai/numbers.json's starter "unreceived" figure as current while it is known wrong, and no
guide keeps calling it wrong after it recovers (challenges #324, #327).

Measured 2026-11-19: /ai/numbers.json said starter_payments.unreceived 21 until 12:03 UTC and 0 from 13:18 UTC,
starters_sent 29 unchanged and no receive in between. blocks_info with receivable:true on rpc.nano.to at 13:2x UTC:
14 of the 18 starter-sized (10^25 raw) sends from treasury2 and Unstuck's account are still receivable. Same
shape as 2026-10-04 (#95): the box's Nano node was refused, and a refused read most likely counted as "received".
#324 made every guide say the field was "WRONG TODAY".

At 19:03 UTC the field read 21 again (18:03 still 0), and blocks_info at 19:2x UTC still showed 14 of 18
receivable - the box's count recovered. "WRONG TODAY" then told a stranger to distrust a correct number (#327).
Each copy now says it reads 21 again since 19:03, names the 13:18-18:03 outage, gives the chain count, and keeps
the rule for the next outage: if it reads 0 while the chain disagrees, count it on chain. If the field breaks
again, change the texts and this law together.

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


def near_numbers(rel):
    s = flat(rel)
    i = s.find("ledger.json")
    j = s.find(NUMBERS, i) if i >= 0 else -1
    return s[j:j + 800] if j >= 0 else None


class NumbersUnreceivedRecovered(unittest.TestCase):
    def test_no_copy_offers_the_old_figure(self):
        for rel in TEXTS:
            self.assertNotIn("21 unreceived at", flat(rel), rel)

    def test_no_copy_still_calls_it_wrong_today(self):
        for rel in TEXTS:
            near = near_numbers(rel)
            self.assertIsNotNone(near, rel)
            self.assertNotIn("WRONG TODAY", near.upper(), rel)

    def test_each_copy_says_recovered_names_outage_and_chain_count(self):
        for rel in TEXTS:
            near = near_numbers(rel)
            self.assertIsNotNone(near, rel)
            self.assertIn("21 again since 19:03 UTC 11-19", near, rel)
            self.assertIn("from 13:18 to 18:03 UTC", near, rel)
            self.assertIn("14 of the 18", near, rel)
            self.assertIn("rpc.nano.to", near, rel)
            self.assertIn("count it on chain", near, rel)


if __name__ == "__main__":
    unittest.main()
