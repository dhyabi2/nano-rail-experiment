#!/usr/bin/env python3
"""Law for challenge #332 (2026-11-22): tools.json and the directory page tell a buyer to read the echo 402 from its body.

#331 put the warning into both llms.txt copies: the echo route's Payment-Required header decodes to a bare list of
accepts with no x402Version and no resource, while the JSON body of the same 402 is the v2 object. The machine-read
manifest, /ai/tools.json (callable_now[echo]), and both copies of the directory page still said only "Unpaid POST
answers 402", so a program that reads tools.json - the file a client parses instead of prose - went to the header.
Re-measured 12:2x UTC 11-22: header a bare list of 1 accept, body x402Version 2 with a quoteId.
Change this law with the text when the box sends the v2 object in the header.

Run: python3 specs/test_tools_json_echo_header_shape.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ("published/aidirectory/index.html", "published/aidirectory.html")
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"


def echo_entry():
    with open(os.path.join(ROOT, "published/aidirectory/tools.json"), encoding="utf-8") as f:
        d = json.load(f)
    found = [t for t in d["callable_now"] if t.get("name") == "echo"]
    assert len(found) == 1, "exactly one echo entry in callable_now"
    return found[0]


class ToolsJsonEchoHeaderShape(unittest.TestCase):
    def test_structured_fields(self):
        e = echo_entry()
        self.assertEqual(e["read_402_from"], "body")
        self.assertIn("bare list", e["header_shape"])
        self.assertIn("no x402Version", e["header_shape"])
        self.assertTrue(os.path.exists(os.path.join(ROOT, "drafts/unstuck-echo-402-header-v2.md")))
        self.assertIn("drafts/unstuck-echo-402-header-v2.md", e["header_shape"])

    def test_what_warns_before_the_send(self):
        what = echo_entry()["what"]
        warn = what.index("never from its Payment-Required header")
        self.assertLess(warn, what.index("send exactly 0.001 XNO"))
        self.assertIn("x402Version 2", what)

    def test_payee_unchanged_and_ours(self):
        e = echo_entry()
        self.assertEqual(e["pay_to"], UNSTUCK)
        self.assertEqual(e["price"], "0.001 XNO")

    def test_both_pages_identical_and_warn(self):
        texts = []
        for p in PAGES:
            with open(os.path.join(ROOT, p), encoding="utf-8") as f:
                texts.append(f.read())
        self.assertEqual(texts[0], texts[1])
        row = texts[0][texts[0].index(">echo</a>"):]
        row = row[:row.index("</tr>")]
        self.assertIn("not its Payment-Required header, which is a bare list", row)
        self.assertLess(row.index("bare list"), row.index("Send exactly 0.001 XNO"))


if __name__ == "__main__":
    unittest.main()
