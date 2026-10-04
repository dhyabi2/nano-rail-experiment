#!/usr/bin/env python3
"""Laws for the "PAID SO FAR" note in bounties.txt section 1 (challenge #93).

Section 1 headlines two 0.1 XNO rewards. Measured 2026-10-04 04:30 UTC (rpc.nano.to account_history, count -1):
the sender, Unstuck's account nano_1434j1n4..., has 28 blocks and exactly one send of
100000000000000000000000000000 raw (0.1 XNO): E0B513EB856B9FF2322331FD61D0F73F134FBD71F4A02FE4D58F8980D7660FF9,
2026-09-23, to ARION. Nothing schedules either scorer (specs/04). The section said none of this, while section 5
already told the same truth about the asks. This pins the note and the command that lets a stranger re-check it.

Run: python3 specs/test_bounties_rewards_paid_so_far.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SENDER = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
GRANT_RAW = "100000000000000000000000000000"
ONLY_GRANT = "E0B513EB856B9FF2322331FD61D0F73F134FBD71F4A02FE4D58F8980D7660FF9"


class RewardsPaidSoFar(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index(" 1. THE REWARDS")
        self.sec1 = txt[i:txt.index(" 2. THE CONFIRMATION", i)]
        self.flat = " ".join(self.sec1.split())

    def test_section_one_says_what_has_been_paid(self):
        self.assertIn("PAID SO FAR", self.sec1)
        self.assertIn("ONE 0.1 XNO send ever, none since 2026-09-23", self.flat)
        self.assertIn("no scorer for either runs on a schedule yet", self.flat)
        self.assertIn("block " + ONLY_GRANT[:8], self.flat)

    def test_check_command_reads_the_sender_and_the_grant_amount(self):
        cmd = next(l for l in self.sec1.splitlines() if l.strip().startswith("curl -s https://rpc.nano.to"))
        body = json.loads(re.search(r"-d '(\{.*?\})'", cmd).group(1))
        self.assertEqual(body, {"action": "account_history", "account": SENDER, "count": -1})
        self.assertIn("h['amount']=='%s'" % GRANT_RAW, cmd)
        self.assertEqual(int(GRANT_RAW), 10 ** 29)  # 0.1 XNO at 10^30 raw per XNO

    def test_command_filter_counts_one_grant_on_the_measured_history(self):
        # The filter from the command, run on the shape rpc.nano.to returned: one grant, other sends ignored.
        cmd = next(l for l in self.sec1.splitlines() if l.strip().startswith("curl -s https://rpc.nano.to"))
        src = re.search(r'python3 -c "(.*)"$', cmd.strip()).group(1)
        history = {"history": [
            {"type": "send", "amount": "1000000000000000000000000000", "hash": "A" * 64, "account": "nano_x", "local_timestamp": "1"},
            {"type": "send", "amount": GRANT_RAW, "hash": ONLY_GRANT, "account": "nano_3m8cz87zwxb", "local_timestamp": "1790200683"},
            {"type": "receive", "amount": GRANT_RAW, "hash": "B" * 64, "account": "nano_y", "local_timestamp": "2"},
        ]}
        import io
        import sys
        out, old_in, old_out = io.StringIO(), sys.stdin, sys.stdout
        sys.stdin, sys.stdout = io.StringIO(json.dumps(history)), out
        try:
            exec(src.replace(";", "\n", 1), {})
        finally:
            sys.stdin, sys.stdout = old_in, old_out
        lines = out.getvalue().splitlines()
        self.assertEqual(lines, ["E0B513EB856B9FF2 nano_3m8cz87zwxb 1790200683"])


if __name__ == "__main__":
    unittest.main()
