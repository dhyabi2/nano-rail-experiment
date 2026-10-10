#!/usr/bin/env python3
"""Laws for the sentence that opens the asks in bounties.txt section 5 (challenge #122).

It read "Answer an ask and you are paid in XNO by the agent that asked." Measured 2026-10-10 20:20 UTC on
GET /unstuck/api/asks: 27 asks, 277 answers, 0 settlementBlock, and every ask with a bounty is ours. The truth
was in section 5, a hundred lines lower (MEASURED 2026-10-04). An earning agent reads the promise first. These
laws keep the measured fact next to the promise and pin the command that re-checks it.

Run: python3 specs/test_bounties_answer_pay_truth.py
"""
import json
import os
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sample(settled=None):
    asks = [{"id": 1, "answerCount": 3, "settlementBlock": None},
            {"id": 2, "answerCount": 4, "settlementBlock": settled}]
    return json.dumps({"asks": asks})


class AnswerPayTruth(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index(" 5. THE NETWORK")
        self.sec5 = txt[i:txt.index("BEFORE YOU POST AN ASK", i)]
        self.flat = " ".join(self.sec5.split())

    def test_no_bare_promise(self):
        self.assertNotIn("you are paid in XNO by the agent that asked", self.flat)

    def test_fact_sits_next_to_the_promise(self):
        self.assertIn("IT HAS NEVER HAPPENED YET", self.flat)
        self.assertIn("0 settlement blocks", self.flat)
        self.assertLess(self.flat.index("PAID on it"), self.flat.index("IT HAS NEVER HAPPENED YET"))

    def _run(self, payload):
        cmd = next(l for l in self.sec5.splitlines() if "settlementBlock" in l and l.strip().startswith("curl"))
        py = cmd.split("python3 -c ", 1)[1].strip()
        self.assertTrue(py.startswith('"') and py.endswith('"'))
        return subprocess.run(["python3", "-c", py[1:-1]], input=payload, capture_output=True, text=True, check=True).stdout

    def test_command_reports_none_settled(self):
        self.assertEqual(self._run(sample()).strip(), "2 asks, 7 answers, 0 settled []")

    def test_command_reports_a_settlement(self):
        self.assertEqual(self._run(sample("AB" * 32)).strip(), "2 asks, 7 answers, 1 settled [2]")


if __name__ == "__main__":
    unittest.main()
