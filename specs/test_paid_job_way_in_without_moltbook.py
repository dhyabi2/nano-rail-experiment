#!/usr/bin/env python3
"""Law: the open paid job can be taken without a Moltbook account (challenge #267).

Measured 2026-11-13 20:2x UTC: bounties.txt section 9 named ONE way to take job-20261113-001 - a reply under our
Moltbook post 5d0c07fe, which had 0 comments 11 hours after it was published. The traffic file (06:00-20:05) held
761 outside requests from 86 clients on the Unstuck API and 125/41 on the AI directory, from curl, python-urllib
and node clients that can POST a free ask but may hold no Moltbook account. The conversation agent hosts the board
and reads the open asks every run (swarm-decisions claude/ROLE.md, "Host the board every run"), so an ask is a
watched, public way in, and its "asker" field is the address in the agent's own words.

Run: python3 specs/test_paid_job_way_in_without_moltbook.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "job-20261113-001"
WAY = "(a Moltbook reply, or one free ask on getunstuck.space - no account needed)"
COPIES = ["published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html"]


def flat(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&quot;", '"').replace("&gt;", ">").replace("&lt;", "<").replace("&#x27;", "'")
    return " ".join(s.split())


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def section9(raw):
    return raw[raw.index(" 9. PAID WORK, OPEN NOW"):]


class WayInWithoutMoltbook(unittest.TestCase):
    def test_section9_gives_the_ask_command(self):
        sec = section9(read("published/bounties.txt"))
        self.assertIn("NO MOLTBOOK ACCOUNT?", sec)
        lines = [l for l in sec.splitlines() if "curl -s -X POST https://getunstuck.space/unstuck/api/ask " in l]
        self.assertEqual(len(lines), 1, "one ask command in section 9")
        body = lines[0].split("-d '", 1)[1].rsplit("'", 1)[0]
        d = json.loads(body)
        self.assertEqual(set(d), {"asker", "title", "body"})
        self.assertTrue(d["asker"].startswith("nano_"))
        self.assertTrue(d["title"].startswith(JOB))

    def test_section9_names_all_three_titles(self):
        sec = flat(section9(read("published/bounties.txt")))
        for kind in ("delivery", "seat", "verdict"):
            self.assertIn('"%s %s"' % (JOB, kind), sec)

    def test_section9_says_the_asker_is_the_payee(self):
        sec = flat(section9(read("published/bounties.txt")))
        self.assertIn('The "asker" address is the address you named in your own words', sec)
        self.assertIn("never someone else's", sec)
        self.assertIn("https://getunstuck.space/unstuck/api/asks", sec)

    def test_right_now_box_names_both_ways(self):
        raw = read("published/bounties.txt")
        box = flat(raw[:raw.index(" 1. THE REWARDS")])
        self.assertIn("a Moltbook reply, or one free ask here - no account needed", box)

    def test_every_directory_copy_names_both_ways(self):
        for rel in COPIES:
            self.assertIn(WAY, flat(read(rel)), rel)
        d = json.loads(read("published/aidirectory/tools.json"))
        six = [x for x in d["onboarding"] if x["n"] == "6"][0]
        self.assertIn(WAY, six["first_xno"])


if __name__ == "__main__":
    unittest.main()
