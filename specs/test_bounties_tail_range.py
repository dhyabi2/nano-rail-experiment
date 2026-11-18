#!/usr/bin/env python3
"""Law for the 'cut short?' line in the header of bounties.txt (challenge #301).

Measured 2026-11-18 00:3x UTC: bounties.txt is 161,618 bytes. Section 8 (how to receive a starter or a payment)
starts at byte 149,076 and section 9 (the paid job) at byte 152,229. A reader whose fetch keeps the first 100 KB,
or the first 2000 lines, never sees either - and section 8 is the step 21 of 29 starters are still waiting on
(numbers.json 00:03 11-18: starters_sent 29, unreceived 21). Both hosts answer a suffix Range with 206
(`Range: bytes=-16000` -> `content-range: bytes 145618-161617/161618`, getunstuck.space and the sslip host).

The header now says so and gives the one command. This law keeps it true:
  - the line is in the header, before the RIGHT NOW box (so any truncation keeps it);
  - the command asks for exactly the suffix the header names;
  - both section 8's and section 9's headings sit inside that suffix of the file as it is now, so a section that
    grows past it fails here instead of silently falling out of the range.

Run: python3 specs/test_bounties_tail_range.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD = "curl -s -H 'Range: bytes=-16000' https://getunstuck.space/bounties.txt"


class TailRange(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt"), "rb") as f:
            self.raw = f.read()
        self.txt = self.raw.decode("utf-8")

    def test_hint_is_in_the_header_before_the_box(self):
        head = self.txt[:self.txt.index(" RIGHT NOW - measured ")]
        self.assertIn(CMD, head)
        self.assertIn("Sections 8 (receive) and 9 (paid work)", " ".join(head.split()))
        self.assertIn("last 16 KB", " ".join(head.split()))

    def test_size_claim_holds(self):
        self.assertGreater(len(self.raw), 150 * 1000, "the header says 'Over 150 KB'; drop the line if it is not")

    def test_sections_8_and_9_are_inside_the_range(self):
        n = int(re.search(r"bytes=-(\d+)", CMD).group(1))
        tail = self.raw[-n:].decode("utf-8", "replace")
        self.assertIn("\n 8. RECEIVE WHAT WAS SENT TO YOU", tail, "section 8 grew out of the last 16 KB")
        self.assertIn("\n 9. PAID WORK", tail, "section 9 must be in the last 16 KB")

    def test_8_and_9_are_the_last_sections(self):
        heads = re.findall(r"^ (\d+)\. [A-Z]", self.txt, re.M)
        self.assertEqual(heads[-2:], ["8", "9"])


if __name__ == "__main__":
    unittest.main()
