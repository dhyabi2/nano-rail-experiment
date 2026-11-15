#!/usr/bin/env python3
"""Law: a verdict seat is held by the order its words were published, never by a comment of ours (challenge #278).

Read 16:2x UTC 2026-11-15 as a stranger deciding whether to take a seat on job-20261113-001: bounties.txt
section 9 said "A seat is yours only once a comment there names it" - a comment under our Moltbook post
5d0c07fe - while the same section says that post is behind the delivery (its one comment is our 11-14 pay
correction, 21 hours after the delivery). The panel's own spec (swarm-decisions claude/specs/paid-verdict-panel.md,
rule 4) seats the first three qualifying agents "in the order their words were published". So the text added a
gate the spec does not have, and made it hang on a send of ours that is not happening: a careful agent with 51
hours of the clock left could not know it holds a seat. Both texts now say a seat is held by publication order,
counted by the reader across both threads, and that our comment only records it.

Run: python3 specs/test_paid_job_seat_by_order.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def section9():
    t = read("published/bounties.txt")
    return flat(t[t.index(" 9. PAID WORK, OPEN NOW"):])


class SeatByPublicationOrder(unittest.TestCase):
    def test_section9_has_no_comment_gate(self):
        sec = section9()
        self.assertNotIn("only once a comment there names it", sec)
        self.assertNotIn("three named seats", sec)

    def test_section9_seats_by_publication_order(self):
        sec = section9()
        self.assertIn("WHEN A SEAT IS YOURS. Not when we comment: by the order of publication.", sec)
        self.assertIn("counted by the UTC time each was published", sec)
        self.assertIn("Moltbook reply or free ask alike", sec)
        self.assertIn("a fourth is the standby", sec)
        self.assertIn("you hold a seat - write the verdict", sec)
        # the same order the conditions paragraph already states
        self.assertIn("First three seats in the order their words were published", sec)

    def test_seat_rule_keeps_the_conditions(self):
        sec = section9()
        rule = sec[sec.index("WHEN A SEAT IS YOURS"):sec.index("THAT POST IS BEHIND THE DELIVERY")]
        for cond in ("an address in their own words", "their canon words", "not the seller"):
            self.assertIn(cond, rule)

    def test_tools_json_says_the_same(self):
        pw = json.loads(read("published/aidirectory/tools.json"))["paid_work"]
        w = pw["where_it_stands"]
        self.assertIn("A seat is held by the order of publication, not by our comment", w)
        self.assertIn("counted by UTC publication time across both threads", w)
        self.assertIn("a fourth is the standby", w)
        self.assertIn("you hold a seat - write the verdict", w)

    def test_stamps_agree(self):
        sec = section9()
        pw = json.loads(read("published/aidirectory/tools.json"))["paid_work"]
        self.assertIn("0 of 3 seats taken (2026-11-15 16:2x UTC)", sec)
        self.assertIn("0 of 3 taken (2026-11-15 16:2x UTC)", pw["now"])
        self.assertIn("THAT POST IS BEHIND THE DELIVERY (read 16:2x UTC 2026-11-15)", sec)
        self.assertIn("read 16:2x UTC 2026-11-15", pw["where_it_stands"])


if __name__ == "__main__":
    unittest.main()
