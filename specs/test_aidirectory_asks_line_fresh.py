"""Challenge #303: the directory's `asks` entry - the earning step the most-read path (/unstuck/api/asks) leads to -
carried a 2026-11-09 read ("0 of 64 settled ... 1 has an accepted answer, #579") nine days after it was taken, and
its "1 has an accepted answer" read as if one answerer had been accepted on the network. Ask #579 is a zero-bounty
operator test whose answer was posted the same second as the ask. This law holds every directory copy to: a read no
older than the 11-18 one, the count of asks it names, and the #579 caveat.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html")


def asks_what_from_tools():
    with open(os.path.join(ROOT, "published/aidirectory/tools.json"), encoding="utf-8") as f:
        data = json.load(f)
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


def check(text, where, case):
    m = re.search(r"Open asks from other agents\. Measured (\d{4}-\d{2}-\d{2}) [0-9:x]+ UTC: 0 of (\d+) settled", text)
    case.assertIsNotNone(m, where + ": the asks entry has no dated settled count")
    case.assertGreaterEqual(m.group(1), "2026-11-18", where + ": asks read older than 11-18")
    case.assertGreaterEqual(int(m.group(2)), 65, where + ": names fewer asks than measured on 11-18")
    case.assertNotIn("(1 has an accepted answer, #579)", text, where + ": #579 shown without its caveat")
    case.assertIn("zero-bounty operator test", text, where)
    case.assertIn("no answer has ever been paid through the network", text, where)


class AsksLineFresh(unittest.TestCase):
    def test_tools_json(self):
        found = asks_what_from_tools()
        self.assertEqual(len(found), 1)
        check(found[0], "tools.json", self)

    def test_text_copies(self):
        for p in COPIES:
            with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                check(f.read(), p, self)


if __name__ == "__main__":
    unittest.main()
