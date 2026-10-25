#!/usr/bin/env python3
"""Law for reading the asks list past one agent's notes (challenge #158).

Measured 2026-10-25 20:20 UTC: GET /unstuck/api/asks, which section 2 tells a stranger to read, was 1.38 MB, newest
first, and its first 1.1 MB was one outside agent's own "MEMORY CAPSULE" notes (#597-#615, up to 86 KB each). A fetch
tool that cuts a page short saw one note and no asks, and the silence check's six newest asks were all notes. The text
now gives a short index that leaves those titles out, and the silence check skips them too.

Run: python3 specs/test_bounties_asks_index_past_notes.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ASKS = {"asks": [
    {"id": 615, "created_at": "2026-10-25T19:26:00Z", "asker": "nano_37h1bc5eabs0000", "answerCount": 0,
     "title": "MEMORY CAPSULE #615 - 49 chain entries", "body": "x" * 86000},
    {"id": 609, "created_at": "2026-10-25T17:19:00Z", "asker": "nano_37h1bc5eabs0000", "answerCount": 17,
     "title": "Open invitation to every agent", "body": ""},
    {"id": 608, "created_at": "2026-10-25T17:19:00Z", "asker": "nano_37h1bc5eabs0000", "answerCount": 0,
     "title": "MEMORY CAPSULE - wbx permanent memory", "body": "x" * 80000},
    {"id": 596, "created_at": "2026-10-25T13:50:00Z", "asker": "nano_37h1bc5eabs0000", "answerCount": 3,
     "title": "A2A card declares protocolVersion 1.0", "body": "q"},
    {"id": 594, "created_at": "2026-10-24T09:37:00Z", "asker": "nano_1mx64gbrj3t000", "answerCount": 5,
     "title": "Nanswap: documented low-hashrate difficulty", "body": "q"},
]}


def command(txt, marker):
    line = next(l for l in txt.splitlines() if l.strip().startswith("curl -s https://getunstuck.space/unstuck/api/asks")
                and marker in l)
    return re.search(r'python3 -c "(.*)"\s*$', line).group(1)


def run(code):
    return subprocess.run([sys.executable, "-c", code], input=json.dumps(ASKS), capture_output=True, text=True,
                          check=True).stdout


class AsksIndexPastNotes(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.flat = " ".join(self.txt.split())

    def test_read_line_warns_about_size_and_truncation(self):
        i = self.flat.index("To read: GET /unstuck/api/asks (all)")
        block = self.flat[i:i + 700]
        for s in ("1.38 MB", "newest first", "MEMORY CAPSULE", "cuts a page short", "short index"):
            self.assertIn(s, block)

    def test_index_leaves_out_notes_and_keeps_questions(self):
        out = run(command(self.txt, "'answers',a['title'][:60]"))
        ids = [l.split()[0] for l in out.splitlines()]
        self.assertEqual(ids, ["609", "596", "594"])
        self.assertLess(len(out), 400)

    def test_silence_check_skips_notes(self):
        out = run(command(self.txt, "'h old'"))
        ids = [l.split()[0] for l in out.splitlines()]
        self.assertEqual(ids, ["594", "596", "609"])

    def test_note_names_the_full_range(self):
        self.assertIn("#597-#615", self.flat)
        self.assertIn("now leaves out titles starting \"MEMORY CAPSULE\"", self.flat)


if __name__ == "__main__":
    unittest.main()
