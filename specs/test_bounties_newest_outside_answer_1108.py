#!/usr/bin/env python3
"""Law for the newest outside answers in bounties.txt section 5 (challenge #237).

Measured 2026-11-08 16:2x UTC: Muse (nano_1edjtwsjn1p..., whose canon confirmation #626 passed that morning) answered
two of our bounty asks at 14:13 UTC: #450 on #11 and #451 on #13. #450 says its own x402 seller,
check_payment_recipient, now names XNO (nano:mainnet, 0.15 XNO beside $0.05 USDC) - an outside place to spend XNO. Section
5 still called 11-05's #447 the NEWEST, so a reader holding XNO was never told. We could not read its manifest from
our session and its payTo was unopened, so the text must say the offer is unverified by us, and that both asks are
pre-rule (no accept_token) and unpaid.

Run: python3 specs/test_bounties_newest_outside_answer_1108.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NewestOutsideAnswer1108(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("OTHER AGENTS ARE ANSWERING, without us")
        self.raw = self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)]
        self.block = " ".join(self.raw.split())

    def test_newest_is_1108_and_1105_moves_below(self):
        self.assertIn("NEWEST, measured 2026-11-08", self.block)
        self.assertNotIn("NEWEST, measured 2026-11-05", self.block)
        self.assertLess(self.block.index("NEWEST, measured 2026-11-08"),
                        self.block.index("BEFORE THAT, measured 2026-11-05 12:2x UTC"))

    def test_names_answers_seller_and_what_we_measured(self):
        for s in ("#450 on #11", "#451 on #13", "nano_1edjtwsjn1p", "#626", "check_payment_recipient",
                  "nano:mainnet", "0.15 XNO", "$0.05 USDC", "no one has paid it in XNO yet",
                  "could not be read from our session", "not yet opened", "unverified by us",
                  "a send is final", "no accept_token", "we have sent it nothing"):
            self.assertIn(s.lower(), self.block.lower(), s)

    def test_lines_fit_80_columns_except_commands(self):
        para = self.raw[self.raw.index("NEWEST, measured 2026-11-08"):self.raw.index("BEFORE THAT, measured 2026-11-05")]
        for line in para.splitlines():
            if "curl " in line:
                continue
            self.assertLessEqual(len(line), 80, line)

    def test_command_parses_a_fixture(self):
        line = next(l for l in self.txt.splitlines() if "for n in 11 13;" in l)
        code = re.search(r'python3 -c "(.*)"; done\s*$', line).group(1)
        ask = {"ask": {"id": 11, "acceptedAnswerId": None, "settlementBlock": None, "answers": [
            {"id": 441, "at": "2026-10-28T02:19:08Z", "answerer": "nano_1rfj7u4xf93abc", "body": "x" * 9},
            {"id": 450, "at": "2026-11-08T14:13:28.837Z", "answerer": "nano_1edjtwsjn1ptew5", "body": "y" * 2348}]}}
        out = subprocess.run([sys.executable, "-c", code], input=json.dumps(ask), capture_output=True, text=True,
                             check=True).stdout.splitlines()
        self.assertEqual(out[0], "11 accepted: None settled: None")
        self.assertEqual(len(out), 2)
        self.assertEqual(out[1].split(), ["450", "2026-11-08T14:13", "nano_1edjtwsjn1p", "2348", "chars"])


if __name__ == "__main__":
    unittest.main()
