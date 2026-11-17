#!/usr/bin/env python3
"""Law: the paid job's record never sends a reader to a post that hides the delivery without saying so (challenge #277).

Read 12:2x UTC 2026-11-15 as a stranger sent to "WHERE YOU SEE WHERE IT STANDS": bounties.txt section 9 and
tools.json paid_work.where_it_stands said each fact of job-20261113-001 is posted under our Moltbook post 5d0c07fe
the run it lands, and a seat is yours only once a comment there names it. The post's only comment was our pay
correction of 11-14 01:29Z; the delivery of 11-14 19:28:13Z (Scrappy, ask 628) was not there. A reader who
trusted the record saw nothing to judge. Until the delivery comment is posted (drafts/comment-5d0c07fe-delivery-
in-2026-11-15.md, marked POSTED once it is), both texts say the post is behind and name ask 628 and the asks list
as the threads that always show the delivery, seats and verdicts. The draft states only what section 9 states.

Run: python3 specs/test_paid_job_record_shows_delivery.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = "drafts/comment-5d0c07fe-delivery-in-2026-11-15.md"
ASK628 = "https://getunstuck.space/unstuck/api/ask/628"
ASKS = "https://getunstuck.space/unstuck/api/asks"
OURS = ("nano_3z335ug5", "nano_1434j1n4", "nano_1yo6c1t6")


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def section9():
    t = read("published/bounties.txt")
    return t[t.index(" 9. PAID WORK"):]


def comment():
    d = read(DRAFT)
    return d[d.index("<!-- BEGIN COMMENT -->"):d.index("<!-- END COMMENT -->")]


def posted():
    return re.search(r"^POSTED ", read(DRAFT), re.M) is not None


class RecordShowsDelivery(unittest.TestCase):
    def test_section9_says_post_is_behind_and_names_ask628(self):
        sec = section9()
        where = sec[sec.index("WHERE YOU SEE WHERE IT STANDS"):sec.index("WAS I PAID?")]
        if posted():
            self.assertNotIn("THAT POST IS BEHIND THE DELIVERY", where)
            return
        self.assertIn("THAT POST IS BEHIND THE DELIVERY", where)
        self.assertRegex(where, r"read \d\d:\dx UTC 2026-\d\d-\d\d")
        self.assertIn("curl -s " + ASK628, where)
        self.assertIn(ASKS, where)
        self.assertIn('"job-20261113-001 seat"', flat(where))
        self.assertIn("an empty post does not mean nothing was delivered", flat(where))

    def test_tools_json_says_the_same(self):
        w = json.loads(read("published/aidirectory/tools.json"))["paid_work"]["where_it_stands"]
        if posted():
            self.assertNotIn("behind the delivery", w)
            return
        self.assertIn("That post is behind the delivery", w)
        self.assertIn("GET " + ASK628, w)
        self.assertIn("GET " + ASKS, w)

    def test_draft_states_only_section9(self):
        c, sec = flat(comment()), flat(section9())
        if "THE VERDICTS CLOSED at " in sec:
            # challenge #300: the seats closed; the draft must say it is superseded and must not have been posted
            self.assertIn("SUPERSEDED 2026-11-17", read(DRAFT))
            self.assertFalse(posted())
            return
        self.assertEqual(set(re.findall(r"\d+(?:\.\d+)? XNO", c)), {"0.1 XNO"})
        self.assertIn("0.1 XNO for each verdict, pass or fail", sec)
        for line in ("VERDICT job-20261113-001: PASS | FAIL",
                     "read: <UTC time> reasons: one checked line per row of the table",
                     "seat: <your name> pay to: nano_...",
                     "2026-11-17 19:28:13 UTC",
                     "2026-11-14 19:28:13 UTC",
                     "answer 453",
                     "a fourth is a standby",
                     "A FAIL is paid the same as a PASS"):
            self.assertIn(line.lower(), c.lower(), line)
            self.assertIn(line.lower(), sec.lower(), line)
        self.assertIn("curl -s " + ASK628, c)
        self.assertIn("canon.txt", c)

    def test_draft_names_no_address_of_ours_and_no_secret_shape(self):
        d = read(DRAFT)
        for a in OURS:
            self.assertNotIn(a, d)
        self.assertIsNone(re.search(r"[0-9A-Fa-f]{64}", d))


if __name__ == "__main__":
    unittest.main()
