#!/usr/bin/env python3
"""Laws for the receive note in bounties.txt's "BEFORE STEP 6" block (challenge #88).

Challenge #86 told outside agents a 0.00001 XNO starter "puts your account on chain". It does not: a Nano send
lands receivable, and the recipient's account exists only once the recipient signs an open block. Measured
2026-10-03 12:30 UTC: /ai/numbers.json starter_payments says 21 sent, 15 unreceived; rpc.nano.to `receivable` shows
starters from Unstuck's account still pending at four recipients from 2026-09-23 on; rpc.nano.to `work_generate`
answers 402 for 1000000000000000000000000000 raw (0.001 XNO) while `process` is free; nanocurrency 2.5.0
computeWork at threshold fffffe0000000000 took 5.6 s. The closest outside agent on Moltbook wrote "0.00001 XNO
opens the account" on 2026-10-03. This pins the correction and keeps every figure equal to what was measured.

Challenge #95: from 2026-10-04 08:03 UTC /ai/numbers.json said 0 unreceived while blocks_info on rpc.nano.to showed 16 of
the 21 starter sends still receivable (12:18-12:20 UTC). The figure is now sourced from the chain, with a command that
re-counts it, and the text says numbers.json was wrong that day.

Run: python3 specs/test_bounties_starter_must_be_received.py
"""
import os
import re
import unittest
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STARTER_RAW = 10000000000000000000000000           # ledger.json starter_raw
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"  # ledger.json opener
WORK_GENERATE_RAW = 1000000000000000000000000000   # rpc.nano.to work_generate 402 "amount"
RECEIVE_THRESHOLD = "fffffe0000000000"              # Nano receive/open work threshold


class StarterMustBeReceived(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index(" BEFORE STEP 6 - YOUR FIRST XNO.")
        self.block = self.txt[i:self.txt.index("\n STEP 6 - ", i)]
        self.flat = " ".join(self.block.split())

    def test_no_longer_claims_the_starter_opens_the_account(self):
        self.assertNotIn("puts your account on chain", self.txt)
        self.assertIn("It does NOT open your account by itself", self.flat)
        self.assertIn("lands RECEIVABLE", self.flat)
        self.assertIn("YOU sign a receive", self.flat)

    def test_unreceived_figure_is_sourced_and_consistent(self):
        m = re.search(r"(\d+) of the (\d+) starters we have sent are still sitting receivable", self.flat)
        self.assertIsNotNone(m)
        self.assertLessEqual(int(m.group(1)), int(m.group(2)))
        self.assertIn("read on the chain", self.flat)
        self.assertIn("when a page and the chain disagree, the chain wins", self.flat)

    def test_recount_command_reads_the_chain_not_a_page(self):
        cmd = next(l.strip() for l in self.block.splitlines() if "starters still receivable" in l)
        self.assertTrue(cmd.startswith('python3 -c "'))
        self.assertIn("'action':'account_history','account':'" + UNSTUCK + "'", cmd)
        self.assertIn("'action':'blocks_info'", cmd)
        self.assertIn("'receivable':'true'", cmd)
        self.assertIn("'User-Agent':", cmd)  # rpc.nano.to answers 403 to a bare python-urllib (step 3)
        self.assertIn("'" + str(STARTER_RAW) + "'", cmd)
        self.assertIn("'" + str(STARTER_RAW // 1000) + "'", cmd)  # the first eleven, sent a thousandth too small
        self.assertNotIn("numbers.json", cmd)
        compile(cmd[len('python3 -c "'):-1], "<recount>", "exec")

    def test_work_is_local_and_the_paid_work_generate_is_priced_right(self):
        self.assertIn("computed LOCALLY", self.flat)
        self.assertIn(RECEIVE_THRESHOLD, self.flat)
        self.assertIn("work_generate answers 402 for 0.001 XNO, a hundred starters", self.flat)
        self.assertEqual(int(Decimal("0.001") * 10**30), WORK_GENERATE_RAW)
        self.assertEqual(WORK_GENERATE_RAW // STARTER_RAW, 100)
        self.assertIn('"process" on the node, which is free', self.flat)

    def test_never_asks_for_a_seed(self):
        self.assertNotRegex(self.block, r"(?i)(send|paste|post|give) (us )?your seed")
        self.assertNotRegex(self.block, r"\b[0-9A-Fa-f]{64}\b")

    def test_starter_still_cannot_pay(self):
        self.assertIn("It cannot PAY for anything", self.block)


if __name__ == "__main__":
    unittest.main(verbosity=1)
