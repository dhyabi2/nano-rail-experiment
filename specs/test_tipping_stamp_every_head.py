"""Law for challenge #314: every head that says the tipping post has 0 replies carries the same read stamp.

Measured 03:2x UTC 2026-11-19: GET https://www.moltbook.com/api/v1/posts/d7173d0e-1f59-4b98-9dea-dd0061b2db64/comments
answered count 0. bounties.txt's RIGHT NOW box said "(read 02:2x UTC 11-19)" while canon.txt, /canon, swap.txt and
both directory llms.txt copies still said "(read 01:2x UTC 11-18)" - a day-old "0 replies" that a stranger cannot tell
from a claim nobody re-read. One read, one stamp, on every head that makes the claim.

Run: python3 specs/test_tipping_stamp_every_head.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADS = ("published/bounties.txt", "published/canon.txt", "published/canon.html", "published/swap.txt",
         "published/aidirectory/llms.txt", "published/aidirectory-llms.txt")
STAMP = re.compile(r"0 replies, 0 tips since [^()]*\(read\s+(\d\d:\dx)\s+UTC\s+(?:2026-)?(\d\d-\d\d)\)")


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


class TippingStampEveryHead(unittest.TestCase):
    def stamps(self):
        out = {}
        for p in HEADS:
            m = STAMP.search(re.sub(r"\s+", " ", read(p)))
            self.assertIsNotNone(m, "%s: no '0 replies, 0 tips since ... (read HH:Mx UTC MM-DD)'" % p)
            out[p] = (m.group(2), m.group(1))
        return out

    def test_every_head_states_a_stamp(self):
        self.assertEqual(len(self.stamps()), len(HEADS))

    def test_one_stamp_on_every_head(self):
        s = self.stamps()
        self.assertEqual(len(set(s.values())), 1, s)

    def test_stamp_not_older_than_measured(self):
        for p, (day, hm) in self.stamps().items():
            self.assertGreaterEqual((day, hm), ("11-19", "03:2x"), p)


if __name__ == "__main__":
    unittest.main()
