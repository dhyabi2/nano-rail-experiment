#!/usr/bin/env python3
"""Laws for the "HOW A CALL IS PAID" block under bounties.txt step 6 (challenge #87).

Step 6 told a funded agent to spend XNO on 24 endpoints and never said how a call is paid. Measured 2026-10-03
08:17-08:25 UTC on extract.paypercall.dev: an unpaid call past the free trial answers 402 with an x402 "accepts"
list (scheme exact, network nano:mainnet, asset XNO, amount in raw, payTo the treasury); a retry with
`X-PAYMENT: <block hash>` is checked on the ledger, and a hash it cannot find or a send to another account answers
402 "payment_invalid"; the first 5 calls a day per IP are free ("trial_limit": 5). This pins the block to those facts,
keeps the payee equal to the treasury, and keeps every command free of seeds and keys.

Run: python3 specs/test_bounties_how_to_pay.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"


class HowACallIsPaid(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        s6 = self.txt.index("\n STEP 6 - ")
        i = self.txt.index(" HOW A CALL IS PAID", s6)
        self.block = self.txt[i:self.txt.index("\n\n", i)]

    def test_block_sits_inside_step6_before_the_tools_list(self):
        self.assertLess(self.txt.index(" HOW A CALL IS PAID"), self.txt.index(" OUR XNO TOOLS"))

    def test_names_the_x402_challenge_fields(self):
        for word in ("402", '"accepts"', "XNO", "nano:mainnet", '"amount" in raw', '"payTo"'):
            self.assertIn(word, self.block)

    def test_header_is_x_payment_with_a_block_hash(self):
        cmd = re.search(r"curl -s -H 'X-PAYMENT: <BLOCK_HASH>' \\\n\s+'(https://[^']+)'", self.block)
        self.assertIsNotNone(cmd)
        self.assertTrue(cmd.group(1).startswith("https://extract.paypercall.dev/api/v1/"))
        self.assertIn("64-hex block hash", self.block)

    def test_free_trial_matches_the_measured_limit(self):
        self.assertIn("first 5 calls a day from one IP are FREE", self.block)

    def test_free_trial_is_not_promised_as_real_data(self):
        # challenge #248: measured 16:21 UTC 2026-11-10, a first call of the day answered 402 on four endpoints.
        flat = " ".join(self.block.split())
        self.assertNotIn("call with no header and you get real data", flat)
        self.assertIn("Do not count on it", flat)
        self.assertIn("answered 402 at once", flat)
        self.assertIn("STEP 5 (oracle-check)", flat)
        self.assertIn("oracle-check", self.txt[self.txt.index("\n STEP 5 - "):self.txt.index("\n STEP 6 - ")])

    def test_says_exact_amount_and_names_the_failure(self):
        self.assertIn("EXACTLY that amount", self.block)
        self.assertIn('"payment_invalid"', self.block)

    def test_no_secret_and_no_other_payee(self):
        self.assertNotRegex(self.block, r"(?i)\bseed\b|private key|[0-9A-F]{64}")
        self.assertEqual(re.findall(r"nano_[13][a-z0-9]{59}", self.block), [])
        self.assertIn('"payTo" (our treasury)', self.block)  # the manifests' payTo is TREASURY (money audit checks it)

    def test_nano_info_link_carries_its_required_parameter(self):
        self.assertIn("/api/v1/nano-info?account=nano_...", self.txt[self.txt.index("\n STEP 6 - "):])


if __name__ == "__main__":
    unittest.main(verbosity=2)
