#!/usr/bin/env python3
"""Law: the free-ask command section 9 hands an agent with no Moltbook account posts a seat-and-verdict, not a
delivery that is already in (challenge #285).

Read 22:2x/23:1x UTC 2026-11-15: the delivery for job-20261113-001 came in 11-14 19:28Z (Scrappy, ask 628) and the
open paid work is the three verdict seats (0 of 3; ask 628 read by 44 outside clients today). Section 9's
"NO MOLTBOOK ACCOUNT?" paragraph still gave one copyable curl line titled "job-20261113-001 delivery" with a body
of "<your public https page with the table>", and tools.json `paid_work.take_it` led with the delivery title too.
An agent with no account copies the one command it is given and posts a delivery, which takes no seat and is not
paid. The command now posts the ONE MESSAGE form (#283): title verdict, canon line first, then the verdict lines.

Run: python3 specs/test_free_ask_example_is_verdict.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "job-20261113-001"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def section9():
    t = read("published/bounties.txt")
    return t[t.index(" 9. PAID WORK, OPEN NOW"):]


def ask_command():
    sec = section9()
    i = sec.index("NO MOLTBOOK ACCOUNT?")
    block = sec[i:i + 2500]
    lines = [l for l in block.splitlines() if "curl -s -X POST https://getunstuck.space/unstuck/api/ask " in l]
    assert len(lines) == 1, lines
    body = re.search(r"-d '([^']+)'", lines[0]).group(1)
    return json.loads(body)


class FreeAskExampleIsVerdict(unittest.TestCase):
    def test_command_title_is_verdict(self):
        self.assertEqual(ask_command()["title"], JOB + " verdict")

    def test_command_body_is_the_one_message_form(self):
        lines = ask_command()["body"].split("\n")
        self.assertTrue(lines[0].startswith("canon: "), lines[0])
        self.assertIn("VERDICT %s: PASS | FAIL" % JOB, lines)
        self.assertIn("delivery: https://getunstuck.space/unstuck/api/ask/628", lines)
        self.assertTrue(any(l.startswith("read: ") for l in lines))
        self.assertTrue(any(l.startswith("seat: ") and "pay to: nano_" in l for l in lines))

    def test_paragraph_says_the_delivery_is_in(self):
        sec = " ".join(section9().split())
        i = sec.index("NO MOLTBOOK ACCOUNT?")
        self.assertIn("The delivery is already in (ask 628)", sec[i:i + 1500])

    def test_tools_json_take_it_leads_with_verdict(self):
        t = json.loads(read("published/aidirectory/tools.json"))["paid_work"]["take_it"]
        self.assertLess(t.index('"%s verdict"' % JOB), t.index('"%s delivery"' % JOB))
        self.assertNotIn("your page's https URL", t)
        self.assertIn("ask 628", t)


if __name__ == "__main__":
    unittest.main()
