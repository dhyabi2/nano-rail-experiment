#!/usr/bin/env python3
"""Laws for the "which asks pay" one-liner in bounties.txt section 5 (challenge #72).

bounties.txt tells an agent to run a python3 one-liner over GET /unstuck/api/asks to see which open
asks carry a bounty, in XNO, and whether each was ever settled. This runs the published command
itself, offline, against a fixture shaped like the live API (2026-09-30), so a later edit cannot
publish a command that throws, prints raw as XNO (challenge #22: raw is where the zero hides), or
reports an unsettled ask as settled.

Run: python3 specs/test_bounties_asks_command.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FIXTURE = {"asks": [
    {"id": 1, "status": "open", "bountyRaw": "1000000000000000000000000000", "answerCount": 127,
     "settlementBlock": None, "title": "How do I detect an abandoned Nano account"},
    {"id": 461, "status": "open", "bountyRaw": "1000000000000000000000000", "answerCount": 2,
     "settlementBlock": None, "title": "Invitation to pursekeeper"},
    {"id": 578, "status": "open", "bountyRaw": "0", "answerCount": 0,
     "settlementBlock": None, "title": "Canon read + qualification"},
    {"id": 579, "status": "closed", "bountyRaw": "1000000000000000000000000000", "answerCount": 0,
     "settlementBlock": None, "title": "[TEST] closed"},
    {"id": 9, "status": "open", "bountyRaw": "2000000000000000000000000000", "answerCount": 1,
     "settlementBlock": "AB" * 32, "title": "A settled one"},
    {"id": 10, "status": "open", "bountyRaw": None, "answerCount": 0,
     "settlementBlock": None, "title": "No bounty field"},
]}


def published_command():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    # section 2's gate-log one-liner (challenge #73) reads the same API; this law is about section 5's
    cmds = re.findall(r"curl -s https://getunstuck\.space/unstuck/api/asks \| python3 -c \"(.*?)\"\n", txt)
    cmds = [c for c in cmds if "settlementBlock" in c]
    return cmds[0] if len(cmds) == 1 else None


class AsksCommand(unittest.TestCase):
    def run_cmd(self):
        code = published_command()
        self.assertIsNotNone(code, "bounties.txt no longer carries the asks one-liner")
        r = subprocess.run([sys.executable, "-c", code], input=json.dumps(FIXTURE),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.splitlines()

    def test_lists_only_open_asks_that_pay(self):
        ids = [ln.split()[0] for ln in self.run_cmd()]
        self.assertEqual(ids, ["1", "461", "9"])

    def test_amounts_are_xno_not_raw(self):
        out = {ln.split()[0]: ln.split()[1] for ln in self.run_cmd()}
        self.assertEqual(float(out["1"]), 0.001)
        self.assertEqual(float(out["461"]), 0.000001)
        self.assertEqual(float(out["9"]), 0.002)

    def test_settled_only_when_a_block_exists(self):
        out = {ln.split()[0]: ln for ln in self.run_cmd()}
        self.assertIn("NOT settled", out["1"])
        self.assertIn("NOT settled", out["461"])
        self.assertNotIn("NOT settled", out["9"])
        self.assertIn(" settled ", out["9"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
