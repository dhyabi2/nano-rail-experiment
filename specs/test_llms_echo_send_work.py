#!/usr/bin/env python3
"""Law for challenge #336 (2026-11-22): /ai/llms.txt and tools.json say the echo payment needs SEND-level work.

The echo route's 402 (re-measured 16:1x UTC 11-22) carries, in its one accept,
"extra":{"work":"required","workThreshold":"fffffff800000000"} - the Nano send threshold, 64 times a receive's.
bounties.txt section 4 ("WHAT THE SEND TAKES") has said so since 11-16, but both llms.txt copies went straight from
the header warning to "Send exactly that amount from your own key", and the tools.json echo entry named no work at
all, so a buyer arriving from either computed receive-level work and had its send refused. Change this law with the
text if the box ever drops or changes the threshold.

Run: python3 specs/test_llms_echo_send_work.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt")
SEND = "fffffff800000000"
RECEIVE = "fffffe0000000000"


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return " ".join(f.read().split())


def before_the_send(t):
    end = t.index("Send exactly that amount from your own key")
    return t[t.index("Unpaid, it answers 402 with the same terms."):end]


class LlmsEchoSendWork(unittest.TestCase):
    def test_both_copies_identical(self):
        self.assertEqual(read(COPIES[0]), read(COPIES[1]))

    def test_work_named_before_the_send(self):
        for p in COPIES:
            para = before_the_send(read(p))
            with self.subTest(copy=p):
                self.assertIn("THE SEND NEEDS SEND-LEVEL WORK", para)
                self.assertIn(SEND, para)
                self.assertIn(RECEIVE, para)
                self.assertIn("receive-level work is refused for a send", para)
                self.assertIn("0.00001 XNO starter is a hundredth", para)

    def test_points_at_a_section_that_exists(self):
        b = read("published/bounties.txt")
        self.assertIn("WHAT THE SEND TAKES", b)
        self.assertIn(SEND, b)
        s4 = b.index("4. OPEN YOUR ACCOUNT")
        s5 = b.index(" 5. ", s4)
        self.assertTrue(s4 < b.index("WHAT THE SEND TAKES") < s5)

    def test_tools_json_echo_names_send_work(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json"), encoding="utf-8") as f:
            data = json.load(f)
        found = []

        def walk(o):
            if isinstance(o, dict):
                if o.get("name") == "echo" and "send_work" in o:
                    found.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)

        walk(data)
        self.assertEqual(len(found), 1)
        self.assertIn(SEND, found[0]["send_work"])
        self.assertIn(RECEIVE, found[0]["send_work"])


if __name__ == "__main__":
    unittest.main()
