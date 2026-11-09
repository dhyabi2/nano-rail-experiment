#!/usr/bin/env python3
"""Law for the nrx#203 follow-up: a late x402 send at pursekeeper.dev is not X-Nano-Payment credit.

#227 told every late buyer at pursekeeper.dev's door to read /v1/credit and call again with X-Nano-Payment. That holds
for a plain wallet send. On the x402 path (PAYMENT-SIGNATURE, the one whose maxTimeoutSeconds 60 the paragraph quotes)
the door broadcasts the block itself; a block not confirmed within ~8 s gets a 402 with a single-use X-Nano-Represent
token, and that hash "is not X-Nano-Payment credit for anyone" (github.com/pursekeeper/api README at 7e392da; server.js
REPRESENT, 30-day expiry naming agent@pursekeeper.dev). A buyer following our old text was refused and could pay twice.

Run: python3 specs/test_bounties_pursekeeper_x402_represent.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PursekeeperX402Represent(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            flat = " ".join(f.read().split())
        i = flat.index("pursekeeper.dev's door")
        self.para = flat[i:flat.index("The first PAID or LATE writes", i)]

    def test_plain_send_and_x402_are_told_apart(self):
        self.assertIn("depends on HOW you paid", self.para)
        self.assertIn("A plain wallet send to pay_to (no 402 involved) is not refused", self.para)

    def test_x402_late_block_uses_the_represent_token(self):
        for s in ("single-use X-Nano-Represent token", "NOT X-Nano-Payment credit",
                  "re-present the SAME PAYMENT-SIGNATURE with X-Nano-Represent:"):
            self.assertIn(s, self.para, s)

    def test_thirty_day_expiry_and_mail_are_said(self):
        self.assertIn("unused for 30 days", self.para)
        self.assertIn("agent@pursekeeper.dev", self.para)

    def test_bearer_and_checkout_limits_are_said(self):
        self.assertIn("bearer token", self.para)
        self.assertIn("marketplace checkout wallet", self.para)

    def test_no_second_send(self):
        self.assertIn("Never send again", self.para)


if __name__ == "__main__":
    unittest.main()
