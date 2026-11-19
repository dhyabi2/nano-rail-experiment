#!/usr/bin/env python3
"""Law: bounties.txt's starter paragraph does not head itself as a live service while none has been sent
(challenge #325).

Measured 2026-11-19 14:2x UTC on rpc.nano.to: treasury2 (nano_3z335ug5...) has sent exactly six starter-sized
(10^25 raw) sends, the newest DFCD32FA... at 00:05 UTC 11-09; 5 of the 6 are still receivable. Nothing since, though
askers and answerers came (a first-seen address answered asks 587 and 590 at 03:54 UTC 11-19 and got none). The top
box already said "none since 11-09", but section 4's paragraph still opened "SENT AGAIN, FROM A NEW ACCOUNT, AT MOST
5 A DAY" - present tense, the line a reader who searches for "starter" lands on - and then "Since 20:25 UTC 11-08
the starter comes from our new treasury". A newcomer reads that as "post an ask and wait".

This law: the paragraph opens with the stop and its date, the old present-tense heading is gone, and it tells the
reader not to post an ask to get one. When treasury2 sends a starter again, change the text and this law together.

Run: python3 specs/test_starter_none_since_1109.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class StarterNoneSince1109(unittest.TestCase):
    def setUp(self):
        self.s = flat("published/bounties.txt")

    def test_old_present_tense_heading_gone(self):
        self.assertNotIn("SENT AGAIN, FROM A NEW ACCOUNT, AT MOST 5 A DAY", self.s)
        self.assertNotIn("Since 20:25 UTC 2026-11-08 the starter comes from", self.s)

    def test_paragraph_opens_with_the_stop(self):
        i = self.s.find("NONE SENT SINCE 00:05 UTC 2026-11-09")
        self.assertGreaterEqual(i, 0)
        near = self.s[i:i + 900]
        self.assertIn("try-nano's step 2", near)
        self.assertIn("Do not post an ask to get one", near)
        self.assertIn("DFCD32FA", near)
        self.assertIn("rpc.nano.to", near)
        self.assertIn("5 of the 6 receivable", near)

    def test_count_command_restamped(self):
        self.assertIn("(ran 14:2x UTC 11-19: 5 of 6)", self.s)
        self.assertNotIn("(ran 12:30 UTC 11-09: 5 of 6)", self.s)

    def test_top_box_still_says_none_since(self):
        box = self.s[:self.s.find("1. THE REWARDS")]
        self.assertIn("none since 11-09", box)


if __name__ == "__main__":
    unittest.main()
