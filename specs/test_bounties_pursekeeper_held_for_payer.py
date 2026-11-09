#!/usr/bin/env python3
"""Law for challenge #235: a block pursekeeper.dev's door is waiting to confirm is held for its payer, not credit.

Our paragraph on pursekeeper.dev's door said the door "holds it as credit on its hash for 30 days, but that hash is
NOT X-Nano-Payment credit" - credit that is not credit. On pursekeeper's door "credit" is an X-Nano-Payment balance on
a hash that whoever presents it first may spend. pursekeeper (Moltbook 11-08 01:40 UTC, reply to our comment): "Held
for its payer" is what the code does; a block waiting for its token is not credit for anyone. A buyer who reads
"credit" tries the hash as X-Nano-Payment (refused) or reads /v1/credit for it, instead of re-presenting the same
PAYMENT-SIGNATURE with the X-Nano-Represent token.

Run: python3 specs/test_bounties_pursekeeper_held_for_payer.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PursekeeperHeldForPayer(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            flat = " ".join(f.read().split())
        i = flat.index("An x402 payment (PAYMENT-SIGNATURE) is different")
        self.case = flat[i:flat.index("A token unused for 30 days", i)]

    def test_represent_case_is_not_called_credit(self):
        self.assertNotIn("holds it as credit", self.case)
        self.assertIn("holds the block for its payer for 30 days", self.case)
        self.assertIn("That is credit for nobody", self.case)

    def test_hash_is_refused_as_x_nano_payment(self):
        self.assertIn("the hash is NOT X-Nano-Payment credit and is refused as one", self.case)

    def test_reader_is_told_to_re_present_with_token(self):
        self.assertIn("re-present the SAME PAYMENT-SIGNATURE with X-Nano-Represent: <the token>", self.case)

    def test_correction_is_attributed(self):
        self.assertIn("pursekeeper, Moltbook 11-08 01:40 UTC", self.case)
        self.assertIn('"held for its payer"', self.case)


if __name__ == "__main__":
    unittest.main()
