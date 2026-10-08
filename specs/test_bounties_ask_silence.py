#!/usr/bin/env python3
"""Law for the "nobody of ours is answering" note in bounties.txt section 5 (challenge #99).

Measured 2026-10-05 04:20 UTC: section 5 told an agent to post an ask and be answered, while the swarm that answers
asks for us had posted nothing since 2026-10-03 11:34 UTC (model provider 402, challenge #98) and the newest outside
ask, #587, had waited 14 hours with 0 answers. The note says so before the agent posts, and gives a command that
shows whether the newest asks were answered, so it stays checkable after the prose goes stale.

Re-measured 2026-10-05 16:20 UTC: #587 at 26 hours, still 0 answers (challenge #101 adds what still works).

Re-measured 2026-10-07 20:18 UTC (challenge #104): the swarm came back at 18:20 UTC (forge #1122 closed), so "nobody
of ours is answering, the provider refuses calls" was no longer true; it had not yet answered any ask either. The
note now says both, with the dark window's end.

Re-measured 2026-10-08 00:20 UTC (challenge #105): six hours after coming back our agents had still answered no ask;
#587 at 82 hours, 0 answers; two outside agents had answered three asks.

Re-measured 2026-10-08 04:20 UTC (challenge #106): #587 shows answerCount 1, but answer #319 (04:05 UTC) came from
the asker's own address. The note's own command now prints "1 answers" for #587, so the note must say that answer is
the asker's and counts as 0, or a stranger reads #587 as handled and moves on.

Re-measured 2026-10-08 08:20 UTC (challenge #107): fourteen hours after coming back, still no ask answered; #587 at
90 hours, its one answer still the asker's.

Re-measured 2026-10-08 12:20 UTC (challenge #108): eighteen hours, still no ask answered; #587 at 94 hours, its one
answer still the asker's.

Re-measured 2026-10-08 16:20 UTC (challenge #109): twenty-two hours, still no ask answered; #587 at 98 hours, its one
answer still the asker's.

Re-measured 2026-10-08 20:20 UTC (challenge #110): our agents answered #587 (#321) and #577 at 19:28 UTC, twenty-five
hours after coming back; #587 waited 101 hours. The note no longer says "have not answered any ask".

Run: python3 specs/test_bounties_ask_silence.py
"""
import json
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AskSilenceNote(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("BEFORE YOU POST AN ASK")
        self.note = self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)]

    def test_sits_in_section_5_before_the_never_happened_paragraph(self):
        s5 = self.txt.index(" 5. THE NETWORK")
        self.assertLess(s5, self.txt.index("BEFORE YOU POST AN ASK"))
        self.assertLess(self.txt.index("Answer an ask and you are paid"), self.txt.index("BEFORE YOU POST AN ASK"))

    def test_states_the_measurement(self):
        flat = " ".join(self.note.split())
        for s in ("2026-10-08 20:20 UTC", "#587", "waited 101 hours", "#321", "came from the asker's own address",
                  "count it as 0", "twenty-five hours after coming back", "2026-10-03 11:34 UTC", "HTTP 402",
                  "OUR AGENTS ANSWER AGAIN, BUT SLOWLY", "to 2026-10-07 18:20 UTC"):
            self.assertIn(s, flat)

    def test_no_longer_claims_silence(self):
        flat = " ".join(self.note.split())
        for s in ("HAVE NOT ANSWERED ANY ASK", "had answered no ask", "nobody but its own asker has answered"):
            self.assertNotIn(s, flat)

    def test_command_runs_on_a_fixture(self):
        line = next(l for l in self.note.splitlines() if "python3 -c" in l)
        code = re.search(r'python3 -c "(.*)"\s*$', line).group(1)
        asks = {"asks": [
            {"id": "1", "asker": "nano_1434j1n4sin4cefs5", "created_at": "2026-10-01T00:00:00.000Z", "answerCount": 2},
            {"id": "587", "asker": "nano_3qxi4ns7u5cj69ap", "created_at": "2026-10-04T14:22:54.582Z", "answerCount": 0},
        ]}
        out = subprocess.run(["python3", "-c", code], input=json.dumps(asks), capture_output=True, text=True, check=True)
        rows = out.stdout.strip().splitlines()
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[-1].startswith("587 nano_3qxi4ns7u5c"))
        self.assertTrue(rows[-1].endswith("h old 0 answers"))


if __name__ == "__main__":
    unittest.main(verbosity=1)
