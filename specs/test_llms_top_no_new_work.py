#!/usr/bin/env python3
"""Law for challenge #320 (2026-11-19): the FIRST paragraph of /ai/llms.txt says the paid job takes no new work.

#317 put TAKES NO NEW WORK TODAY before the "OR EARN IT" pitch at line 89 of both llms.txt copies, and #319 into
bounties.txt. The file's first paragraph - the one an AI reader of /ai/llms.txt meets first (aidirectory group 117
outside requests, 72 clients by 09:03 UTC 11-19, the most-read group after the Unstuck API) - still read "Paid work,
seats closed ... (Job open until 2026-11-20 23:59 UTC ... one is in, under review" with no word that nothing is
left to take, and its NOT PAID YET stamp was "read 17:18 UTC 11-18, 22 h after the close" while every other head
carried 00:17 UTC 11-19. Re-read 09:19 UTC 11-19: ask 628's last answer is still 457 (the seller's own - #321 corrected "our 457"), treasury2's frontier still
6ECFB21C (no send since 11-16). The paragraph now says it, before the job date, and points at tipping day.
Change this law with the text when the job closes (2026-11-20 23:59 UTC), a new job opens, or the payout is sent.

Run: python3 specs/test_llms_top_no_new_work.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt")


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def first_paragraph(t):
    t = " ".join(t.split())
    return t[t.index("Paid work"):t.index("Paid for reading")]


class LlmsTopNoNewWork(unittest.TestCase):
    def test_says_no_new_work_before_the_job_date(self):
        for p in COPIES:
            h = first_paragraph(read(p))
            with self.subTest(p):
                self.assertIn("TAKES NO NEW WORK TODAY", h)
                self.assertLess(h.index("TAKES NO NEW WORK TODAY"), h.index("open until 2026-11-20"))

    def test_points_at_what_is_left(self):
        for p in COPIES:
            with self.subTest(p):
                self.assertIn("left to earn today is tipping day", first_paragraph(read(p)))

    def test_stale_stamp_gone(self):
        for p in COPIES:
            h = first_paragraph(read(p))
            with self.subTest(p):
                self.assertNotIn("17:18 UTC 11-18", h)
                self.assertRegex(h, r"Not paid yet: read \d\d:\d\d UTC 11-19")

    def test_law_fails_on_the_old_paragraph(self):
        old = ("Paid work, seats closed: the three verdict seats on job-20261113-001 closed ... (Job open until "
               "2026-11-20 23:59 UTC, untested; 1 XNO for the delivery, once it passes - one is in, under review. "
               "Not paid yet: read 17:18 UTC 11-18, 22 h after the close")
        self.assertNotIn("TAKES NO NEW WORK TODAY", old)
        self.assertIsNone(re.search(r"Not paid yet: read \d\d:\d\d UTC 11-19", old))


if __name__ == "__main__":
    unittest.main()
