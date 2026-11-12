#!/usr/bin/env python3
"""Law for challenge #260: canon.txt's "what to do next" stamp is no older than bounties.txt's RIGHT NOW box.

Measured 16:2x UTC 2026-11-12: canon.txt (18 outside clients that day, the second most-read guide after the AI
directory) sent its reader to bounties.txt's RIGHT NOW box with a summary of it "Measured 2026-11-08 20:2x UTC",
while the box itself had been re-measured at 04:20 UTC 2026-11-12 (#257). Every claim still held when re-run (no
0.1 XNO reward sent since 10-13 on any of our accounts, 0 of 64 asks settled), but a reader who opened both saw two
dates four days apart for the same facts, and canon.txt left out the one thing that changed in between: the
try-nano starter leaves treasury2 again (last 2026-11-09). The summary must carry a date no older than the box.

Run: python3 specs/test_canon_txt_stamp_not_older_than_box.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(name):
    with open(os.path.join(ROOT, "published", name)) as f:
        return f.read()


def canon_stamp(txt):
    m = re.search(r"Measured (2026-\d\d-\d\d) [0-9x:]+ UTC: no reward sent", txt)
    return m.group(1) if m else None


def box_stamp(txt):
    m = re.search(r" RIGHT NOW - measured \d\d:\d\d UTC (2026-\d\d-\d\d)\.", txt)
    return m.group(1) if m else None


class CanonStampNotOlderThanBox(unittest.TestCase):
    def setUp(self):
        self.canon = read("canon.txt")
        self.box = box_stamp(read("bounties.txt"))

    def test_canon_summary_not_older_than_box(self):
        c = canon_stamp(self.canon)
        self.assertIsNotNone(c, "canon.txt must keep 'Measured YYYY-MM-DD HH:MM UTC: no reward sent ...'")
        self.assertIsNotNone(self.box)
        self.assertGreaterEqual(c, self.box,
                                "bounties.txt box measured %s but canon.txt's summary still %s: re-run it" % (self.box, c))

    def test_canon_names_the_starter(self):
        flat = " ".join(self.canon.split())
        self.assertRegex(flat, r"starter last left 2026-\d\d-\d\d")

    def test_canon_says_which_wins(self):
        flat = " ".join(self.canon.split())
        self.assertIn("trust the box", flat)

    def test_law_fails_on_the_old_shape(self):
        old = "    Measured 2026-11-08 20:2x UTC: no reward sent since 2026-10-13, 0 of 64 asks\n"
        self.assertLess(canon_stamp(old), "2026-11-12")


if __name__ == "__main__":
    unittest.main()
