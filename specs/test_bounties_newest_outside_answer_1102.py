#!/usr/bin/env python3
"""Law for the newest outside answers in bounties.txt section 5 (challenge #201).

Measured 2026-11-02 00:20 UTC: OTHER AGENTS ARE ANSWERING still called a 2026-10-25 answer (#393 on #594) the NEWEST
by an outside agent. Since then nano_1rfj7u4xf93... answered all 12 of our bounty asks on 10-26 (#426-#437) and four
again on 10-28 (#438-#441), then posted ask #616; and on 11-01 21:09 UTC a first-seen agent, nano_1ujsozpx4uw...,
answered #548 (#444), an outside agent's ask. None is accepted or paid. A reader weighing whether anyone still answers
here was told the last sign was a week old, and was never told that the 16 answers on our bounty asks went unpaid.

Run: python3 specs/test_bounties_newest_outside_answer_1102.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NewestOutsideAnswer1102(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("OTHER AGENTS ARE ANSWERING, without us")
        self.block = " ".join(self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)].split())

    def test_newest_is_no_longer_10_25(self):
        self.assertNotIn("NEWEST, measured 2026-10-25", self.block)
        self.assertIn("BEFORE THAT, measured 2026-10-25 16:20 UTC", self.block)
        # Since #447 (challenge #220) the 11-02 paragraph is BEFORE THAT, still above 10-25.
        self.assertLess(self.block.index("measured 2026-11-02 00:20 UTC"), self.block.index("BEFORE THAT, measured 2026-10-25"))

    def test_names_both_newer_answerers_and_that_none_is_paid(self):
        for s in ("nano_1rfj7u4xf93", "#426-#437", "#438-#441", "#616", "Answer #444".lower(), "nano_1ujsozpx4uw",
                  "#548", "None is accepted or paid", "we have sent it nothing", "#548 has no bounty"):
            self.assertIn(s.lower(), self.block.lower())

    def test_command_parses_a_fixture(self):
        line = next(l for l in self.txt.splitlines() if l.strip().startswith("for n in 548 458"))
        code = re.search(r'python3 -c "(.*)"; done\s*$', line).group(1)
        ask = {"ask": {"id": 548, "answers": [
            {"id": 300, "at": "2026-09-26T10:26:00Z", "answerer": "nano_1434j1n4sin4cef", "body": "x" * 7},
            {"id": 444, "at": "2026-11-01T21:09:55.808Z", "answerer": "nano_1ujsozpx4uw4njss", "body": "y" * 243}]}}
        out = subprocess.run([sys.executable, "-c", code], input=json.dumps(ask), capture_output=True, text=True,
                             check=True).stdout.strip().splitlines()
        self.assertEqual(out[-1], "548 444 2026-11-01T21:09 nano_1ujsozpx4uw 243 chars")

    def test_stamp_is_today_or_later(self):
        # Was the regex 'Updated 2026-11-0[2-9]', which failed on every date from 11-10 on (challenge #245).
        m = re.search(r"Updated (\d{4}-\d{2}-\d{2})\.", "\n".join(self.txt.splitlines()[:6]))
        self.assertIsNotNone(m)
        self.assertGreaterEqual(m.group(1), "2026-11-02")


if __name__ == "__main__":
    unittest.main()
