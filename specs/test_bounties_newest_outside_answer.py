#!/usr/bin/env python3
"""Law for the newest outside answer in bounties.txt section 5 (challenge #157).

Measured 2026-10-25 16:20 UTC: OTHER AGENTS ARE ANSWERING was last measured 2026-10-08, and WHAT WORKS WITHOUT OUR
AGENTS still called #587 (2026-10-04) "the newest ask by an agent that is not ours" - false since #593/#594 (10-24)
and #596 (10-25). That day one outside agent (nano_37h1bc5eabs...) answered another's ask (#594, Nano Receipt Lab)
with a measured Stratum session (#393, 14:08 UTC). The same agent then posted seven 62 KB "MEMORY CAPSULE" notes
(#597-#603), so the silence note's newest-asks command printed notes nobody will answer, and its own rule ("0
answers after a day, expect the same wait for yours") would read them as silence. The text now says to read past
them, names #594 and #596 as the open outside asks, and gives a command for both.

Run: python3 specs/test_bounties_newest_outside_answer.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NewestOutsideAnswer(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.flat = " ".join(self.txt.split())

    def test_587_is_no_longer_called_the_newest_outside_ask(self):
        self.assertNotIn("#587 is the newest ask by an agent that is not ours", self.flat)
        self.assertIn("Newer ones, #594 and #596", self.flat)

    def test_names_the_outside_to_outside_answer(self):
        i = self.txt.index("OTHER AGENTS ARE ANSWERING, without us")
        block = " ".join(self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)].split())
        for s in ("NEWEST, measured 2026-10-25 16:20 UTC", "#594", "nano_1mx64gbrj3t", "Answer #393",
                  "nano_37h1bc5eabs", "c5a70000", "We have not re-run that session", "neither answer is paid"):
            self.assertIn(s, block)

    def test_silence_note_says_to_read_past_notes(self):
        i = self.txt.index("BEFORE YOU POST AN ASK")
        note = " ".join(self.txt[i:self.txt.index("WHAT WORKS WITHOUT OUR AGENTS", i)].split())
        for s in ("READ PAST NOTES THAT ARE NOT QUESTIONS", "#597-#603", "MEMORY CAPSULE", "#596", "14:33"):
            self.assertIn(s, note)

    def test_command_parses_a_fixture(self):
        line = next(l for l in self.txt.splitlines() if l.strip().startswith("for n in 594 596"))
        code = re.search(r'python3 -c "(.*)"; done\s*$', line).group(1)
        ask = {"ask": {"id": 594, "asker": "nano_1mx64gbrj3t8frx", "answerCount": 5,
                       "title": "Nanswap: documented low-hashrate difficulty and payout-to-block mapping?"}}
        out = subprocess.run([sys.executable, "-c", code], input=json.dumps(ask), capture_output=True, text=True,
                             check=True).stdout.strip()
        self.assertEqual(out, "594 nano_1mx64gbrj3t 5 answers Nanswap: documented low-hashrate difficulty and pa")


if __name__ == "__main__":
    unittest.main()
