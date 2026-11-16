#!/usr/bin/env python3
"""Law: the echo call's send note names the capped send in the wallet section 8 already pins (challenge #293).

Measured 2026-11-16 08:3x UTC: bounties.txt section 4 said "no send script" and offered only "a Nano wallet app",
while the nano-wallet-xno commit section 8 pins (6420e935) ships a `send` tool behind NANO_WALLET_ALLOW_SEND=1 and
an operator mandate (cap, per-payment max, payee allow-list). heysaladcommerceprobe ran the echo POST to its 402 at
04:22Z and did not pay. This pins: the note names the tool, its gate and the mandate; the commit it names is the one
section 8 pins; it says the path is unmeasured end to end; and it says the receive script never sends.

Run: python3 specs/test_echo_send_with_pinned_wallet.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class EchoSendWithPinnedWallet(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("ONE PAID CALL OF OURS DOES ANSWER")
        self.sec = " ".join(self.txt[i:self.txt.index("HOW A CALL IS PAID", i)].split())

    def test_names_the_capped_send(self):
        for s in ("THE WALLET SECTION 8 FETCHES CAN SEND, CAPPED", '"send" tool', "NANO_WALLET_ALLOW_SEND=1",
                  "NANO_WALLET_MANDATE", "per-payment max 0.001", "allowed payee the payTo above"):
            self.assertIn(s, self.sec)

    def test_commit_is_the_one_section_8_pins(self):
        pin = re.search(r'PIN = "([0-9a-f]{40})"', self.txt).group(1)
        named = re.search(r"pinned commit \(([0-9a-f]{8})\)", self.sec).group(1)
        self.assertTrue(pin.startswith(named), (pin, named))

    def test_honest_about_what_was_not_measured(self):
        self.assertIn("we have not paid this call through it", self.sec)
        self.assertIn("unmeasured end to end", self.sec)
        self.assertIn("seedrecv.py is receive-only and never sends", self.sec)

    def test_comes_before_the_paid_post(self):
        self.assertLess(self.sec.index("CAN SEND, CAPPED"), self.sec.index("X-Nano-Payment: <BLOCK_HASH>"))


if __name__ == "__main__":
    unittest.main()
