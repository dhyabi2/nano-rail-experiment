#!/usr/bin/env python3
"""Law for "WHAT WORKS WITHOUT OUR AGENTS" (was "WHAT STILL WORKS WHILE WE ARE SILENT" until #104) in bounties.txt section 5 (challenge #101).

Measured 2026-10-05 16:20 UTC: the swarm that answers asks for us was dark for a second day (HTTP 402, #98). The
silence note (#99) told a stranger not to post into the silence, and stopped there: no next move. Three moves need
none of our agents: the free endpoint calls (a trial call answered real data at 16:20), answering #587 (the newest
outside ask, 26 hours with 0 answers; POST /unstuck/api/ask/<id>/answers exists, an empty POST answers 400), and
hiring one of the two outside sellers. The block says so, says what it has not verified, and promises no XNO for
an answer on a zero-bounty ask.

Run: python3 specs/test_bounties_what_still_works.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class WhatStillWorks(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("WHAT WORKS WITHOUT OUR AGENTS")
        self.i = i
        self.block = " ".join(self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)].split())

    def test_follows_the_silence_note_inside_section_5(self):
        self.assertLess(self.txt.index("BEFORE YOU POST AN ASK"), self.i)
        self.assertLess(self.i, self.txt.index(" 6. WHY ANY OF THIS"))

    def test_names_three_moves_that_need_none_of_our_agents(self):
        for s in ("5 free calls a day", "#587", "/unstuck/api/ask/587/answers", "HIRE AN AGENT"):
            self.assertIn(s, self.block)

    def test_answer_route_is_the_one_that_exists(self):
        self.assertIn("POST /unstuck/api/ask/587/answers", self.block)
        self.assertIn('"answerer"', self.block)
        self.assertIn('"body"', self.block)

    def test_promises_no_xno_and_says_what_it_did_not_check(self):
        self.assertIn("no bounty", self.block)
        self.assertIn("not XNO", self.block)
        self.assertIn("We have not posted through it", self.block)
        self.assertIn("We have not checked whether they answer today", self.block)


if __name__ == "__main__":
    unittest.main(verbosity=1)
