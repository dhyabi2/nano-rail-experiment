#!/usr/bin/env python3
"""Law for challenge #317 (2026-11-19): no head sends a newcomer to the paid job without saying it takes no new work.

tools.json's paid_work.read_first has said since 11-17 that job-20261113-001 "takes no new work today" (its one
delivery is in, its three verdict seats closed 2026-11-17 19:28:13 UTC with 0 verdicts). Four heads still pitched it
as the way to earn: swap.txt "HOLD NOTHING TO SWAP? Earn XNO for work instead ... One paid job is open", both
llms.txt copies "OR EARN IT: one paid job is open", canon.txt "One paid job is open until 11-20", and canon.html
"one paid job does" / "What does pay today: one paid job". A stranger holding nothing who follows any of them finds
nothing left to take. Each now says TAKES NO NEW WORK TODAY before the offer and names tipping day's 0.01 XNO as the
one thing a newcomer can still earn. When the job closes (2026-11-20 23:59 UTC) or a new job opens, change this law
with the text.

Run: python3 specs/test_job_takes_no_new_work_every_head.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADS = ("published/swap.txt", "published/canon.txt", "published/canon.html",
         "published/aidirectory/llms.txt", "published/aidirectory-llms.txt")
NO_NEW = re.compile(r"takes no new work today", re.I)
# the pitch in each head that sends a newcomer to the job; the warning must come just before it
PITCH = {
    "published/swap.txt": "one paid job is open: job-20261113-001",
    "published/canon.txt": "job is open until 11-20",
    "published/canon.html": "The job is open until 2026-11-20 23:59 UTC",
    "published/aidirectory/llms.txt": "OR EARN IT: one paid job is open",
    "published/aidirectory-llms.txt": "OR EARN IT: one paid job is open",
}


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(re.sub(r"<[^>]+>", "", s).split())


class JobTakesNoNewWork(unittest.TestCase):
    def test_each_head_says_no_new_work_before_the_offer(self):
        for p in HEADS:
            t = flat(read(p))
            with self.subTest(p):
                j = t.index(PITCH[p])
                self.assertRegex(t[max(0, j - 400):j], NO_NEW)

    def test_each_head_names_what_a_newcomer_can_still_earn(self):
        for p in HEADS:
            t = flat(read(p))
            with self.subTest(p):
                j = t.index(PITCH[p])
                self.assertIn("tipping day", t[max(0, j - 400):j])

    def test_old_pitches_gone(self):
        self.assertNotIn("one paid job does", flat(read("published/canon.html")))
        self.assertNotIn("What does pay today: one paid job", flat(read("published/canon.html")))
        self.assertNotIn("bounties.txt. OR EARN IT:", flat(read("published/aidirectory/llms.txt")))

    def test_agrees_with_tools_json(self):
        tools = json.loads(read("published/aidirectory/tools.json"))
        self.assertIn("takes no new work today", tools["paid_work"]["read_first"])

    def test_llms_copies_identical(self):
        self.assertEqual(read("published/aidirectory/llms.txt"), read("published/aidirectory-llms.txt"))

    def test_law_fails_on_the_old_head(self):
        old = flat("HOLD NOTHING TO SWAP? Earn XNO for work instead - pay, not a gift. One paid job is open:")
        self.assertIsNone(NO_NEW.search(old))


if __name__ == "__main__":
    unittest.main()
