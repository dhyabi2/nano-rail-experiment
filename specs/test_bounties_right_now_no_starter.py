#!/usr/bin/env python3
"""Law: the RIGHT NOW box must say the starter try-nano promises is not being sent (challenge #223).

Measured 2026-11-06 00:2x UTC: GET /unstuck/api/try-nano step 2 says "post an ask ... The network reads it and sends
your opener" and step 3 says "receive the 0.00001 XNO opener". The Unstuck account's newest send is 08D9724E at
18:00 UTC 2026-10-14 (rpc.nano.to account_history). Seven outside accounts asked or answered since (askers of
#593-#625, answerer of #447) and none of them appears as a recipient in that history. bounties.txt said so only in
a 10-13 gate-log paragraph 280 lines down.

Run: python3 specs/test_bounties_right_now_no_starter.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"


class RightNowNoStarter(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        self.box = txt[txt.index(" RIGHT NOW - measured "):txt.index(" 1. THE REWARDS")]
        self.flat = " ".join(self.box.split())

    def test_box_names_the_broken_promise_and_its_date(self):
        self.assertIn("STARTER", self.flat)
        self.assertIn("try-nano", self.flat)
        self.assertIn("2026-10-14", self.flat)
        self.assertIn("Do not wait for it", self.flat)  # #239: still true - at most 5 a day, not every asker

    def test_section_4_gives_a_free_check_against_the_chain(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        sec = txt[txt.index("\n BEFORE STEP 6 - YOUR FIRST XNO"):txt.index("\n 5. THE NETWORK")]
        self.assertIn("NOT BEING SENT NOW", sec)
        self.assertIn("NOT BEING SENT NOW from there", " ".join(sec.split()))  # #239: the old account; treasury2 sends now
        cmd = [l for l in sec.splitlines() if "account_history" in l and "count\":\"20" in l and UNSTUCK in l]  # #239: treasury2 has its own
        self.assertEqual(len(cmd), 1)
        self.assertIn(UNSTUCK, cmd[0])
        self.assertIn("https://rpc.nano.to", cmd[0])
        self.assertNotIn("work_generate", cmd[0])  # the only paid rpc.nano.to action

    def test_receive_section_exists(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        self.assertRegex(txt, r"\n BEFORE STEP 6 - YOUR FIRST XNO")

    def test_box_lines_fit_80_columns_except_commands(self):
        for line in self.box.splitlines():
            if "curl " in line:
                continue
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
