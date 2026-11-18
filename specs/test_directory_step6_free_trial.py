#!/usr/bin/env python3
"""Challenge #305: the directory (index.html, llms.txt, tools.json and their two mirrors) told every reader "Step 6
costs XNO, and an empty wallet gets HTTP 402 there" - the line an agent holding nothing reads right before step 6, on
the most-read directory paths (aidirectory 70 requests / 42 clients by 04:07 UTC 11-18). Measured 04:2x UTC 11-18
from the cloud: step 6's own command, nano-info WITH ?account=, answered 200 with data and "free_trial": true; the
bare URL answered 402. #304 fixed this in bounties.txt only. This law keeps the trial line in all five copies and
forbids the old sentence.

Run: python3 specs/test_directory_step6_free_trial.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXT = ["published/aidirectory/llms.txt", "published/aidirectory-llms.txt"]
HTML = ["published/aidirectory/index.html", "published/aidirectory.html"]
OLD = "Step 6 costs XNO, and an empty wallet gets HTTP 402 there."


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.replace("&#x27;", "'").split())


class DirectoryStep6FreeTrial(unittest.TestCase):
    def check(self, text, where):
        self.assertNotIn(OLD, text, where)
        self.assertIn("Step 6's command, WITH its ?account=, is served FREE 5 times a day per IP", text, where)
        self.assertIn("a bare URL answers 402 at once, trial or not", text, where)
        self.assertIn("After those 5, step 6 costs XNO and an empty wallet gets HTTP 402 there.", text, where)

    def test_text_copies(self):
        for p in TEXT:
            self.check(flat(read(p)), p)

    def test_html_copies(self):
        for p in HTML:
            self.check(flat(read(p)), p)

    def test_tools_json(self):
        found = []

        def walk(x):
            if isinstance(x, dict):
                for k, v in x.items():
                    if k == "first_xno" and isinstance(v, str):
                        found.append(v)
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)

        walk(json.loads(read("published/aidirectory/tools.json")))
        self.assertTrue(found, "tools.json has no first_xno")
        for v in found:
            self.check(flat(v), "tools.json first_xno")

    def test_law_fails_on_the_old_text(self):
        with self.assertRaises(AssertionError):
            self.check("BEFORE STEP 6 - YOUR FIRST XNO. " + OLD, "old")


if __name__ == "__main__":
    unittest.main(verbosity=2)
