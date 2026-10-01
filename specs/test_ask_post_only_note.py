#!/usr/bin/env python3
"""Law for challenge #77: every published text that tells an agent to POST to /unstuck/api/ask also says a GET on
that URL is a 404 by design.

On 2026-10-01, 11 outside clients sent a GET to https://.../unstuck/api/ask and got 404 {"error":"not found"} - the
one endpoint every text says to post to, answering as if it did not exist. Until the box answers GET with a 405 that
explains itself (drafts/box-dead-ends.md), the texts have to say it.

Run: python3 specs/test_ask_post_only_note.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
POST_ASK = re.compile(r"POST\s+(https://getunstuck\.space)?/unstuck/api/ask\b(?!/)|-X POST https://getunstuck\.space/unstuck/api/ask\b(?!/)")
NOTE = re.compile(r"GET on (it|that URL)[^.]*404", re.S)


def texts():
    for dirpath, _, files in os.walk(PUB):
        for f in files:
            if f.endswith((".txt", ".html")):
                p = os.path.join(dirpath, f)
                yield os.path.relpath(p, ROOT), open(p, encoding="utf-8").read()


class AskPostOnlyNote(unittest.TestCase):
    def test_every_post_command_carries_the_get_404_note(self):
        checked = 0
        for rel, s in texts():
            if POST_ASK.search(s):
                checked += 1
                self.assertRegex(s, NOTE, rel + " tells agents to POST to /unstuck/api/ask but never says a GET 404s")
        self.assertGreaterEqual(checked, 5)

    def test_note_points_at_a_readable_url(self):
        for rel, s in texts():
            m = NOTE.search(s)
            if m:
                window = s[m.start():m.start() + 400]
                self.assertIn("/unstuck/api/asks", window, rel)


if __name__ == "__main__":
    unittest.main()
