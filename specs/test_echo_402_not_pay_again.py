#!/usr/bin/env python3
"""Law: bounties.txt tells a buyer that a 402 after paying getunstuck.space's route does not mean pay again (challenge #198).

Measured 2026-11-01 12:20 UTC: POST /unstuck/api/v1/echo answered a made-up 64-hex X-Nano-Payment, and the real hash of
a send that did not pay it, with the same 402 and the same "Send 0.001 XNO to the payTo address" message as a call with
no header. The route gives no reason, while the seller section says a bad hash answers "payment_invalid" with one. A
buyer whose send is not yet confirmed, or who pasted a wrong hash, reads that message as "pay" and pays twice. The guide
must say: do not send again, check your own block (STEP 4), retry with the same hash.

Run: python3 specs/test_echo_402_not_pay_again.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class Echo402NotPayAgain(unittest.TestCase):
    def setUp(self):
        s = flat("published/bounties.txt")
        start = s.index("ONE PAID CALL OF OURS DOES ANSWER")
        self.block = s[start:s.index("HOW A CALL IS PAID", start)]

    def test_says_do_not_pay_again(self):
        self.assertIn("DOES NOT MEAN PAY AGAIN", self.block)
        self.assertIn("never send a second time", self.block)

    def test_says_how_to_check_and_retry(self):
        for n in ("STEP 4's block_info", 'confirmed "true"', "link_as_account",
                  "1000000000000000000000000000", "the SAME hash"):
            self.assertIn(n, self.block, n)

    def test_warning_comes_after_the_paid_header(self):
        self.assertLess(self.block.index("X-Nano-Payment: <BLOCK_HASH>"), self.block.index("DOES NOT MEAN PAY AGAIN"))

    def test_quote_id_does_not_weaken_the_race_warning(self):
        self.assertIn("quoteId", self.block)
        self.assertIn("does not tie your send to you", self.block)


if __name__ == "__main__":
    unittest.main()
