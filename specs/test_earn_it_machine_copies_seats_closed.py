#!/usr/bin/env python3
"""Law: every machine-read copy of the directory's "OR EARN IT" line says the delivery is in and the seats closed (#309).

Found 13:2x UTC 2026-11-18. #281 and #300 fixed the "OR EARN IT" block on the /ai/ page and in swap.txt, and #281's
own law names the old text ("one paid job is open until 2026-11-20 ... Terms and the way in") as the fault. The same
old text stayed in /ai/llms.txt (20 outside clients by 13:05 UTC), its root copy, and tools.json's onboarding
`first_xno` field (/ai/tools.json, 22 clients): an agent reading the machine files was still invited to a job whose
delivery has been in since 2026-11-14 and whose three verdict seats closed 2026-11-17 19:28:13 UTC with 0 verdicts.
The three copies now carry the page's own wording. Text only; no pay rule changed.

Run: python3 specs/test_earn_it_machine_copies_seats_closed.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASK = "https://getunstuck.space/unstuck/api/ask/628"
CLOSE = "2026-11-17 19:28:13 UTC"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def earn_it(text):
    i = text.index("OR EARN IT:")
    return " ".join(text[i:text.index("bounties.txt.", i)].split())


def copies():
    tools = json.loads(read("published/aidirectory/tools.json"))
    found = []

    def walk(v):
        if isinstance(v, str) and "OR EARN IT:" in v:
            found.append(v)
        elif isinstance(v, dict):
            for x in v.values():
                walk(x)
        elif isinstance(v, list):
            for x in v:
                walk(x)

    walk(tools)
    return {
        "published/aidirectory/llms.txt": read("published/aidirectory/llms.txt"),
        "published/aidirectory-llms.txt": read("published/aidirectory-llms.txt"),
        "published/aidirectory/tools.json": "\n".join(found),
    }


def faults(block):
    out = []
    for need in ("Scrappy, ask 628, 2026-11-14 19:28 UTC", ASK, "seats closed at " + CLOSE + " with 0 verdicts",
                 "no verdict is paid"):
        if need not in block:
            out.append(need)
    return out


class EarnItMachineCopies(unittest.TestCase):
    def test_every_copy_says_delivery_in_and_seats_closed(self):
        for rel, text in copies().items():
            self.assertIn("OR EARN IT:", text, rel)
            self.assertEqual(faults(earn_it(text)), [], rel)

    def test_section_9_still_says_the_seats_closed(self):
        self.assertIn("THE VERDICTS CLOSED at " + CLOSE, " ".join(read("published/bounties.txt").split()))

    def test_llms_copies_identical_and_within_120_columns(self):
        a = read("published/aidirectory/llms.txt")
        self.assertEqual(a, read("published/aidirectory-llms.txt"))
        i = a.index("OR EARN IT:")
        for line in a[a.rindex("\n", 0, i) + 1:a.index("bounties.txt.", i)].split("\n"):
            self.assertLessEqual(len(line), 120, line)

    def test_law_fails_on_the_old_text(self):
        old = ("OR EARN IT: one paid job is open until 2026-11-20 23:59 UTC, job-20261113-001 (untested; 1 XNO for "
               "the delivery, once it passes; 0.1 XNO for each verdict, pass or fail; paid from treasury2, whose "
               "balance you can read first). Terms and the way in (a Moltbook reply, or one free ask on "
               "getunstuck.space - no account needed): section 9 of https://172-86-112-140.sslip.io/bounties.txt.")
        self.assertEqual(len(faults(earn_it(old))), 4)


if __name__ == "__main__":
    unittest.main()
