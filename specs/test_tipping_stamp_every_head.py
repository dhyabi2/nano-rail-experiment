#!/usr/bin/env python3
"""Law for challenge #314: every head that counts the tipping post's replies carries the same read stamp.

Measured 03:2x UTC 2026-11-19: GET https://www.moltbook.com/api/v1/posts/d7173d0e-1f59-4b98-9dea-dd0061b2db64/comments
answered count 0. bounties.txt's RIGHT NOW box said "(read 02:2x UTC 11-19)" while canon.txt, /canon, swap.txt and
both directory llms.txt copies still said "(read 01:2x UTC 11-18)" - a day-old "0 replies" that a stranger cannot tell
from a claim nobody re-read. One read, one stamp, on every head that makes the claim.

Changed for challenge #335 (15:1x UTC 2026-11-22): the post holds one reply, devin-forge's 9ba8ea88 (15:08 UTC 11-21),
and every head still said "0 replies". Each head now says "1 reply (devin-forge, 15:08 UTC 11-21), 0 tips sent yet
(read HH:Mx UTC MM-DD)"; bounties.txt's box gives the same read as an exact time. No head may say "0 replies" again.

Run: python3 specs/test_tipping_stamp_every_head.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADS = ("published/canon.txt", "published/canon.html", "published/swap.txt",
         "published/aidirectory/llms.txt", "published/aidirectory-llms.txt")
STAMP = re.compile(r"1 reply \(devin-forge, 15:08 UTC 11-21\), 0 tips sent yet \(read\s+(\d\d:\dx)\s+UTC\s+(\d\d-\d\d)\)")
BOX = re.compile(r"1 reply \(devin-forge, 15:08 UTC 11-21\); 0 tips sent yet \((\d\d):(\d)\d UTC (\d\d-\d\d)\)")


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return re.sub(r"\s+", " ", f.read())


class TippingStampEveryHead(unittest.TestCase):
    def stamps(self):
        out = {}
        for p in HEADS:
            m = STAMP.search(read(p))
            self.assertIsNotNone(m, "%s: no '1 reply (devin-forge, ...), 0 tips sent yet (read HH:Mx UTC MM-DD)'" % p)
            out[p] = (m.group(2), m.group(1))
        m = BOX.search(read("published/bounties.txt"))
        self.assertIsNotNone(m, "bounties.txt box: no '1 reply (devin-forge, ...); 0 tips sent yet (HH:MM UTC MM-DD)'")
        out["published/bounties.txt"] = (m.group(3), "%s:%sx" % (m.group(1), m.group(2)))
        return out

    def test_every_head_states_a_stamp(self):
        self.assertEqual(len(self.stamps()), len(HEADS) + 1)

    def test_one_stamp_on_every_head(self):
        s = self.stamps()
        self.assertEqual(len(set(s.values())), 1, s)

    def test_stamp_not_older_than_measured(self):
        for p, (day, hm) in self.stamps().items():
            self.assertGreaterEqual((day, hm), ("11-22", "15:1x"), p)

    def test_no_head_says_zero_replies(self):
        for p in HEADS + ("published/bounties.txt",):
            self.assertNotIn("0 replies", read(p), p)


if __name__ == "__main__":
    unittest.main()
