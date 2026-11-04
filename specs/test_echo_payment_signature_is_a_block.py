#!/usr/bin/env python3
"""Law: bounties.txt puts the buyer's hash in X-Nano-Payment and says PAYMENT-SIGNATURE is a signed block (challenge #214).

Until 11-04 the echo block told a buyer to retry "with the SAME hash (in X-Nano-Payment, or PAYMENT-SIGNATURE ...)".
In x402 v2's Nano exact scheme PAYMENT-SIGNATURE is base64 JSON carrying a complete signed, unpublished send block that
the seller broadcasts (x402-foundation/x402#3432, as pursekeeper set out on Moltbook 2026-11-04 09:26 UTC). A hash
there is non-standard, and whether our route accepts the standard form is not measured. The guide must say both.

Run: python3 specs/test_echo_payment_signature_is_a_block.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class PaymentSignatureIsABlock(unittest.TestCase):
    def setUp(self):
        s = flat("published/bounties.txt")
        start = s.index("ONE PAID CALL OF OURS DOES ANSWER")
        self.block = s[start:s.index("HOW A CALL IS PAID", start)]

    def test_no_hash_in_payment_signature(self):
        self.assertNotIn("or PAYMENT-SIGNATURE, which the 402 also names", self.block)
        self.assertIn("THE HASH GOES IN X-Nano-Payment, NOT PAYMENT-SIGNATURE", self.block)

    def test_says_what_payment_signature_carries(self):
        for n in ("base64 JSON", "payload: {block}", "SIGNED send", "the seller broadcasts it", "x402#3432"):
            self.assertIn(n, self.block, n)

    def test_standard_form_is_marked_unmeasured_and_safe(self):
        self.assertIn("NOT MEASURED", self.block)
        self.assertIn("never sign a second send", self.block)


if __name__ == "__main__":
    unittest.main()
