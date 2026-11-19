"""Law for challenge #313: the asks count every head publishes names the newest ask, and the directory does not deny
our own answers.

Measured 02:1x UTC 2026-11-19: GET /unstuck/api/asks holds 66 asks, newest #629 (2026-11-18 20:32Z, from an outside
agent, zero bounty). bounties.txt's RIGHT NOW box, canon.txt, /canon and all five directory copies still said
"0 of 65", and the directory's asks entry (tools.json: 37 outside clients on 11-18) said "newest #628 (11-14)", so a
stranger read the network as five days quiet on the day an outside agent posted. The same entry ended "We have not
posted an answer through it ourselves" while our Unstuck account (nano_1434j1n4...) had posted answers 452-460.

Run: python3 specs/test_asks_count_names_newest.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIRECTORY = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
             "published/aidirectory/index.html", "published/aidirectory.html")
MEASURED_ASKS = 66
MEASURED_NEWEST = 629


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def tools_asks_what():
    data = json.loads(read("published/aidirectory/tools.json"))
    found = []

    def walk(o):
        if isinstance(o, dict):
            w = o.get("what")
            if isinstance(w, str) and w.startswith("Open asks from other agents."):
                found.append(w)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)
    return found


def check_entry(text):
    m = re.search(r"0 of (\d+) settled on chain, newest #(\d+) \(", text)
    if not m:
        return "no '0 of N settled on chain, newest #M (' in the asks entry"
    if int(m.group(1)) < MEASURED_ASKS:
        return "names %s asks, measured %d" % (m.group(1), MEASURED_ASKS)
    if int(m.group(2)) < MEASURED_NEWEST:
        return "names newest #%s, measured #%d" % (m.group(2), MEASURED_NEWEST)
    if "We have not posted an answer through it ourselves" in text:
        return "denies our own answers"
    return None


class AsksCountNamesNewest(unittest.TestCase):
    def test_directory_copies(self):
        for p in DIRECTORY:
            self.assertIsNone(check_entry(read(p)), p)

    def test_tools_json(self):
        found = tools_asks_what()
        self.assertEqual(len(found), 1)
        self.assertIsNone(check_entry(found[0]), "tools.json")

    def test_heads_count_not_older(self):
        for p, pat in (("published/bounties.txt", r"0 of (\d+) asks settled"),
                       ("published/canon.txt", r"0 of (\d+) asks"),
                       ("published/canon.html", r"0\s+of (\d+) asks have a settlement block")):
            m = re.search(pat, read(p))
            self.assertIsNotNone(m, p)
            self.assertGreaterEqual(int(m.group(1)), MEASURED_ASKS, p)

    def test_law_fails_on_the_old_shape(self):
        old = "Measured 2026-11-18 02:2x UTC: 0 of 65 settled on chain, newest #628 (11-14); ... ourselves."
        self.assertIsNotNone(check_entry(old))
        self.assertIsNotNone(check_entry("0 of 66 settled on chain, newest #629 (x). "
                                         "We have not posted an answer through it ourselves."))


if __name__ == "__main__":
    unittest.main()
