#!/usr/bin/env python3
"""Law: the AI directory's "asks" entry tells a reader how to post an ask and how to answer one (challenge #243).

Measured 2026-11-09 20:07 UTC (/ai/traffic/2026-11-09.json): /unstuck/api/asks was the most-read path (53 outside
clients) and the aidirectory group had 52. The directory's "asks" entry said only "Read it, or answer one for the
record" - no route to post an ask (free), no route to answer - and its count was three days stale ("0 of 63", 11-06;
64 asks, 0 settled, 1 accepted at 20:2x 11-09). A reader who found the list had no next step from that entry.

Run: python3 specs/test_aidirectory_asks_how_to_post.py
"""
import html
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT_COPIES = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
               "published/aidirectory/index.html", "published/aidirectory.html")
POST_ASK = "POST https://getunstuck.space/unstuck/api/ask with JSON fields asker"
POST_ANSWER = "POST /unstuck/api/ask/<id>/answers"


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        t = f.read()
    if rel.endswith(".html"):
        t = html.unescape(t)
    return " ".join(t.split())


def asks_entry():
    with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
        data = json.load(f)
    found = []

    def walk(x):
        if isinstance(x, dict):
            if x.get("name") == "asks" and str(x.get("url", "")).endswith("/unstuck/api/asks"):
                found.append(x)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(data)
    return found


class AsksEntry(unittest.TestCase):
    def test_tools_json_entry_names_post_and_answer(self):
        entries = asks_entry()
        self.assertEqual(len(entries), 1, "tools.json must hold exactly one asks entry")
        what = entries[0]["what"]
        self.assertIn(POST_ASK, what)
        self.assertIn(POST_ANSWER, what)
        self.assertIn("free", what)
        self.assertNotIn("0 of 63", what)

    def test_every_text_copy_agrees_with_tools_json(self):
        what = " ".join(asks_entry()[0]["what"].split())
        for rel in TEXT_COPIES:
            t = flat(rel)
            self.assertIn(what, t, rel + " has a different asks entry than tools.json")
            self.assertNotIn("0 of 63 settled", t, rel)

    def test_mirrors_identical(self):
        for a, b in (("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"),
                     ("published/aidirectory/index.html", "published/aidirectory.html")):
            with open(os.path.join(ROOT, a)) as fa, open(os.path.join(ROOT, b)) as fb:
                self.assertEqual(fa.read(), fb.read(), a + " and " + b + " differ")


if __name__ == "__main__":
    unittest.main()
