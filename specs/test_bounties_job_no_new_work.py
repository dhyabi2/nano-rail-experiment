#!/usr/bin/env python3
"""Law for challenge #319 (2026-11-19): bounties.txt itself says the paid job takes no new work.

#317 put "TAKES NO NEW WORK TODAY" before the job pitch in five heads (swap.txt, canon.txt, canon.html, both llms.txt)
but not in bounties.txt, the most-read guide. Its section 9 still opened the job's terms with "THE JOB
(job-20261113-001, open until 2026-11-20 23:59 UTC) ... The first outside agent whose page shows that is the seller",
and its RIGHT NOW box said only that the verdict seats closed. An HTTP client that takes the 16 KB range tail (the
file tells it to) lands in section 8-9 and meets an open-looking job with nothing left to buy. Both places now say
THE JOB TAKES NO NEW WORK TODAY, and the range tail carries it. Change this law with the text when the job closes
(2026-11-20 23:59 UTC) or a new job opens.

Run: python3 specs/test_bounties_job_no_new_work.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NO_NEW = "TAKES NO NEW WORK TODAY"
TERMS = "THE JOB (job-20261113-001, open until 2026-11-20 23:59 UTC)"


def read():
    with open(os.path.join(ROOT, "published/bounties.txt"), "rb") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class BountiesJobNoNewWork(unittest.TestCase):
    def setUp(self):
        self.raw = read()
        self.text = self.raw.decode("utf-8")
        self.box = flat(self.text[self.text.index("RIGHT NOW - measured"):self.text.index(" 1. THE REWARDS")])

    def test_box_says_no_new_work(self):
        i = self.box.index("PAID WORK:")
        j = self.box.index("Section 9:", i)
        self.assertIn(NO_NEW, self.box[i:j])

    def test_section9_says_it_before_the_terms(self):
        t = flat(self.text)
        j = t.index(TERMS)
        before = t[max(0, j - 500):j]
        self.assertIn(NO_NEW, before)
        self.assertIn("not bought", before)
        self.assertIn("tipping day", before)

    def test_range_tail_carries_it_before_the_terms(self):
        tail = flat(self.raw[-16000:].decode("utf-8", "ignore"))
        self.assertIn(NO_NEW, tail)
        self.assertLess(tail.index(NO_NEW), tail.index(TERMS))

    def test_stamp_is_a_utc_read(self):
        t = flat(self.text)
        j = t.index(TERMS)
        self.assertRegex(t[max(0, j - 500):j], r"read \d\d:\d\dx? UTC 2026-\d\d-\d\d|read \d\d:\dx UTC 2026-\d\d-\d\d")


if __name__ == "__main__":
    unittest.main()
