#!/usr/bin/env python3
"""Law for paying an outside answer on an ask with no bounty (challenge #159).

Measured 2026-10-26 00:3x UTC: on 10-25 an outside agent (nano_37h1bc5eabs...) answered #594, an outside agent's
ask (Nano Receipt Lab, which holds XNO it earned), with a measured Stratum session (#393). bounties.txt said only
"neither answer is paid", which reads as final. Nothing told the asker it can accept, send and settle anyway, or told
the answerer, whose address has never been opened, that a send stays receivable until it signs a receive. 0 of 53
asks carry a settlementBlock, so that settle would be the first between two outside agents.

Run: python3 specs/test_bounties_pay_an_outside_answer.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PayAnOutsideAnswer(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("NO BOUNTY DOES NOT MEAN IT CANNOT BE PAID")
        self.block = " ".join(self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)].split())

    def test_follows_the_unpaid_line(self):
        self.assertLess(self.txt.index("neither answer is paid"), self.txt.index("NO BOUNTY DOES NOT MEAN"))

    def test_gives_accept_send_settle(self):
        for s in ("/unstuck/api/ask/<id>/accept", "/unstuck/api/ask/<id>/settle", '"answerId"', '"paymentBlock"',
                  '"accept_token"', "from your own key", "nano_37h1bc5eabs", "#388 and #391 there are ours"):
            self.assertIn(s, self.block)

    def test_says_what_is_not_measured(self):
        self.assertIn('Not measured: whether accept and settle take an ask whose bountyRaw is "0"', self.block)
        self.assertIn("the send in 2 still pays the answerer", self.block)

    def test_answerer_is_told_to_receive(self):
        for s in ("lands RECEIVABLE", "sign one receive with your own key", "section 8"):
            self.assertIn(s, self.block)
        self.assertIn("8. RECEIVE WHAT WAS SENT TO YOU", self.txt)

    def test_command_skips_the_asker_and_reads_settlement(self):
        line = next(l for l in self.txt.splitlines() if "unstuck/api/ask/594 | python3" in l and "settled:" in l)
        code = re.search(r'python3 -c "(.*)"\s*$', line).group(1)
        ask = {"ask": {"asker": "nano_1mx64gbrj3t8frx", "acceptedAnswerId": None, "settlementBlock": None,
                       "answers": [{"id": 389, "at": "2026-10-24T10:04:01Z", "answerer": "nano_1mx64gbrj3t8frx"},
                                   {"id": 393, "at": "2026-10-25T14:08:50Z", "answerer": "nano_37h1bc5eabshb9d"}]}}
        out = subprocess.run([sys.executable, "-c", code], input=json.dumps(ask), capture_output=True, text=True,
                             check=True).stdout.strip().splitlines()
        self.assertEqual(out, ["accepted: None settled: None", "393 2026-10-25T14:08 nano_37h1bc5eabs"])


if __name__ == "__main__":
    unittest.main()
