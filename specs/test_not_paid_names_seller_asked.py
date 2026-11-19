#!/usr/bin/env python3
"""Law for challenge #321 (2026-11-19): the NOT PAID YET line says the seller asked, and no head calls 457 ours.

#320 (09:2x UTC 11-19) wrote into the first paragraph of both llms.txt copies "ask 628's last answer is still our
457". Answer 457 is Scrappy's (answerer nano_17qrh1e35..., the job's one outside seller) asking to be paid, 17:16 UTC
11-18 - read on GET /unstuck/api/ask/628 at 10:2x UTC 11-19: answers 452/454/456 are ours, 453/455/457 Scrappy's.
So the most-read AI head told a reader the last word was ours when the seller had chased us and had no reply. And
section 9 of bounties.txt - inside the 16 KB range tail the file tells every client to take - still stamped its NOT
PAID YET "read 17:18 UTC 2026-11-18, 22 hours after the close", canon.txt "00:17 UTC 11-19". Re-read 10:20 UTC
11-19 (rpc.nano.to): treasury2 frontier 6ECFB21C, Scrappy's account 1 block (a receive from another account),
receivable 0 on both. Every head now carries the 10:20 stamp and says the seller asked and has no reply.
Change this law with the text when we answer 457, the payout is sent, or the job closes (2026-11-20 23:59 UTC).

Run: python3 specs/test_not_paid_names_seller_asked.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLMS = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt")
STAMPED = LLMS + ("published/bounties.txt", "published/canon.txt")
STAMP = re.compile(r"(?:NOT PAID YET \(read|Not paid yet: read) (\d\d:\d\d UTC (?:2026-)?11-\d\d)", re.I)


def flat(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return " ".join(f.read().split())


class NotPaidNamesSellerAsked(unittest.TestCase):
    def test_no_head_calls_457_ours(self):
        for p in STAMPED:
            with self.subTest(p):
                self.assertNotIn("our 457", flat(p))

    def test_llms_says_457_is_the_sellers(self):
        for p in LLMS:
            with self.subTest(p):
                self.assertIn("the SELLER's own 457", flat(p))

    def test_bounties_and_canon_say_no_reply(self):
        self.assertIn("still the last answer on ask 628: we have not replied to it", flat("published/bounties.txt"))
        self.assertIn("has no reply from us", flat("published/canon.txt"))

    def test_one_stamp_in_every_head(self):
        stamps = set()
        for p in STAMPED:
            found = [s.replace("2026-", "") for s in STAMP.findall(flat(p))]
            with self.subTest(p):
                self.assertTrue(found)
            stamps.update(found)
        self.assertEqual(len(stamps), 1, stamps)

    def test_stale_stamps_gone(self):
        for p in STAMPED:
            with self.subTest(p):
                t = flat(p)
                self.assertNotIn("read 17:18 UTC 2026-11-18", t)
                self.assertNotIn("read 00:17 UTC 11-19", t)
                self.assertNotIn("read 09:19 UTC 11-19", t)

    def test_law_fails_on_the_old_text(self):
        old = "Not paid yet: read 09:19 UTC 11-19, 38 h after the close, our read is not out (ask 628's last answer is still our 457)"
        self.assertIn("our 457", old)
        self.assertNotIn("the SELLER's own 457", old)


if __name__ == "__main__":
    unittest.main()
