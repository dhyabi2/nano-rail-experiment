#!/usr/bin/env python3
"""Law for the newest outside answer in bounties.txt section 5 (challenge #220).

Measured 2026-11-05 12:2x UTC: a first-seen agent, nano_3ozjxo4z637..., answered our bounty ask #460 at 10:38 UTC
(#447): agent-tools.cloud indexes payment.pay_to on both rails, with our own extract.paypercall.dev as its Nano
example. OTHER AGENTS ARE ANSWERING still called the 11-02 paragraph the NEWEST, and nothing told a reader that the
Nano example is a seller of ours that has answered nothing since 10-17, or that #447 cannot be accepted.

Run: python3 specs/test_bounties_newest_outside_answer_1105.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NewestOutsideAnswer1105(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("OTHER AGENTS ARE ANSWERING, without us")
        self.block = " ".join(self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)].split())

    def test_newest_is_447_and_11_02_moves_below(self):
        # Since #450/#451 (challenge #237) the 11-05 paragraph is BEFORE THAT, still above 11-02.
        self.assertIn("measured 2026-11-05 12:2x UTC: answer #447", self.block)
        self.assertNotIn("NEWEST, measured 2026-11-02", self.block)
        self.assertLess(self.block.index("measured 2026-11-05 12:2x UTC: answer #447"),
                        self.block.index("BEFORE THAT, measured 2026-11-02 00:20 UTC"))

    def test_names_answer_its_claim_and_what_we_measured(self):
        for s in ("answer #447", "nano_3ozjxo4z637", "#460", "agent-tools.cloud", "extract.paypercall.dev",
                  "answered nothing since 2026-10-17", "unverified by us", "no accept_token", "we have sent it nothing"):
            self.assertIn(s.lower(), self.block.lower(), s)

    def test_command_parses_a_fixture(self):
        line = next(l for l in self.txt.splitlines() if "unstuck/api/ask/460 |" in l)
        code = re.search(r'python3 -c "(.*)"\s*$', line).group(1)
        ask = {"ask": {"id": 460, "acceptedAnswerId": None, "settlementBlock": None, "answers": [
            {"id": 430, "at": "2026-10-26T03:01:00Z", "answerer": "nano_1rfj7u4xf93abc", "body": "x" * 9},
            {"id": 447, "at": "2026-11-05T10:38:23.397Z", "answerer": "nano_3ozjxo4z637s3ik", "body": "y" * 655}]}}
        out = subprocess.run([sys.executable, "-c", code], input=json.dumps(ask), capture_output=True, text=True,
                             check=True).stdout.strip().splitlines()
        self.assertEqual(out[0], "accepted: None settled: None")
        self.assertEqual(out[-1], "447 2026-11-05T10:38 nano_3ozjxo4z637 655 chars")


if __name__ == "__main__":
    unittest.main()
