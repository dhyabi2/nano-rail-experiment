#!/usr/bin/env python3
"""Law for challenge #257: the RIGHT NOW box at the top of bounties.txt is re-measured whenever the page is updated.

Measured 04:20 UTC 2026-11-12: the header said "Updated 2026-11-11" (three merges that day) while the box under it
still said "measured 12:30 UTC 2026-11-09". Every claim in the box still held when re-run (work_generate 402, echo 402,
five sellers 200, 0 of 64 asks settled, treasury2 6 starters sent and 1 received), but a sceptical reader sees a
"right now" three days older than the page around it and takes the box - the only part most readers read - as
abandoned. The box's own date must be no older than the page's "Updated" date.

Run: python3 specs/test_right_now_box_not_older_than_page.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def box_and_stamp(txt):
    head = "\n".join(txt.splitlines()[:8])
    updated = re.search(r"Updated (2026-\d\d-\d\d)\.", head)
    measured = re.search(r" RIGHT NOW - measured \d\d:\d\d UTC (2026-\d\d-\d\d)\.", txt)
    return (updated.group(1) if updated else None), (measured.group(1) if measured else None)


class RightNowNotOlderThanPage(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()

    def test_box_date_not_older_than_updated_stamp(self):
        updated, measured = box_and_stamp(self.txt)
        self.assertIsNotNone(updated, "header must carry 'Updated YYYY-MM-DD.'")
        self.assertIsNotNone(measured, "box must start ' RIGHT NOW - measured HH:MM UTC YYYY-MM-DD.'")
        self.assertGreaterEqual(measured, updated,
                                "page updated %s but RIGHT NOW still measured %s: re-run the box" % (updated, measured))

    def test_law_fails_on_the_old_shape(self):
        old = (" Plain text so you do not have to parse anything. Updated 2026-11-11.\n"
               " RIGHT NOW - measured 12:30 UTC 2026-11-09. Re-check; do not trust a date.\n")
        updated, measured = box_and_stamp(old)
        self.assertLess(measured, updated)

    def test_starter_line_says_when_the_last_one_left(self):
        box = " ".join(self.txt[self.txt.index(" RIGHT NOW - measured "):self.txt.index(" 1. THE REWARDS")].split())
        self.assertIn("6 sent, 1 received", box)
        self.assertRegex(box, r"none since \d\d-\d\d\)")


if __name__ == "__main__":
    unittest.main()
