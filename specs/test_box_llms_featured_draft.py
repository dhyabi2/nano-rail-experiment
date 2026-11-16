#!/usr/bin/env python3
"""Challenge #289: the drafted Featured-content line for getunstuck.space/llms.txt must name the paid job right.

The box's llms.txt is not in this repository, so the fix is a draft. This law keeps the draft honest offline: its
NEW block features ask 628 first, with the close, the seat size and section 9, carries no seat count (which goes
stale), keeps the OLD lines, names no nano_ address, and agrees with bounties.txt's own deadline and size.
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAFT = os.path.join(ROOT, "drafts", "unstuck-llms-featured-open-seats.md")
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")


def blocks(text):
    return re.findall(r"```\n(.*?)```", text, re.S)


class FeaturedDraft(unittest.TestCase):
    def setUp(self):
        with open(DRAFT, encoding="utf-8") as f:
            self.text = f.read()
        with open(BOUNTIES, encoding="utf-8") as f:
            self.bounties = f.read()
        self.old, self.new = blocks(self.text)[0], blocks(self.text)[1]

    def test_new_features_628_first(self):
        gets = re.findall(r"GET (/unstuck/api/\S+)", self.new)
        self.assertEqual(gets[0], "/unstuck/api/ask/628")
        self.assertNotIn("ask/628", self.old)

    def test_new_keeps_old_lines(self):
        for line in self.old.splitlines():
            if line.strip().startswith("GET"):
                self.assertIn(line, self.new)

    def test_line_names_close_size_and_section(self):
        line = [l for l in self.new.splitlines() if "ask/628" in l][0]
        for want in ("2026-11-17 19:28:13 UTC", "0.1 XNO", "job-20261113-001 verdict", "/bounties.txt section 9"):
            self.assertIn(want, line)
        self.assertNotRegex(line, r"\d of 3")

    def test_agrees_with_bounties(self):
        self.assertIn("2026-11-17 19:28:13 UTC", self.bounties)
        self.assertIn("0.1 XNO for each verdict", self.bounties)

    def test_no_address(self):
        self.assertNotRegex(self.text, r"nano_[13][13-9a-km-uw-z]{59}")


if __name__ == "__main__":
    unittest.main()
