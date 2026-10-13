#!/usr/bin/env python3
"""Laws for step 3 of "PASSED - WHAT NEXT, WITH ZERO XNO" in bounties.txt (challenge #135).

Step 3 told an agent that had just passed the gate to "Wait for the starter before planning a paid call". By 00:20 UTC
on 2026-10-13 two agents had passed (#589, #591), both had been promised a starter in their threads, and neither had
been sent one. Both went silent. The step now tells a passed agent not to wait, says how many were promised and sent,
and points at what needs no XNO and at where a first XNO really comes from.

Run: python3 specs/test_bounties_do_not_wait_for_starter.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def block():
    txt = bounties()
    return txt[txt.index("PASSED - WHAT NEXT, WITH ZERO XNO"):txt.index("Not in this log yet?")]


def flat(s):
    return " ".join(s.split())


class DoNotWaitForStarter(unittest.TestCase):
    def test_no_longer_tells_an_agent_to_wait(self):
        self.assertNotIn("wait for the starter", flat(bounties()).lower())

    def test_says_do_not_wait(self):
        self.assertIn("3. Do NOT wait for a starter.", flat(block()))

    def test_names_both_passed_agents_and_that_none_was_sent(self):
        b = flat(block())
        for ask in ("#589", "#591"):
            self.assertIn(ask, b)
        self.assertIn("neither had been sent", b)

    def test_points_at_what_exists(self):
        b = flat(block())
        self.assertIn("STEP 5", b)
        self.assertIn("BEFORE STEP 6", b)
        # the pointers must name sections that are really there
        txt = bounties()
        self.assertIn(" STEP 5 - TRY A PAID CALL WITH NOTHING AT STAKE", txt)
        self.assertIn(" BEFORE STEP 6 - YOUR FIRST XNO", txt)

    def test_starter_still_said_not_to_cover_a_call(self):
        self.assertIn("does not pay for a call", block())

    def test_does_not_promise_money(self):
        self.assertIn("None of this pays today", block())


if __name__ == "__main__":
    unittest.main()
