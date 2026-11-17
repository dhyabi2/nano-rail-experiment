#!/usr/bin/env python3
"""Law: the echo call's send note names the capped send in the wallet section 8 already pins (challenge #293).

Measured 2026-11-16 08:3x UTC: bounties.txt section 4 said "no send script" and offered only "a Nano wallet app",
while the nano-wallet-xno commit section 8 pins (6420e935) ships a `send` tool behind NANO_WALLET_ALLOW_SEND=1 and
an operator mandate (cap, per-payment max, payee allow-list). heysaladcommerceprobe ran the echo POST to its 402 at
04:22Z and did not pay. This pins: the note names the tool, its gate and the mandate; the commit it names is the one
section 8 pins; it says the path is unmeasured end to end; and it says the receive script never sends.

Break review of c1228919 (2026-11-16), read against nano-wallet-xno at 6420e935:
* the send gets its work from node.work_generate (payments.py), rpc.nano.to sells that (402) and local work is only
  receive/open (work.py LOCAL_SUBTYPES), so the note must name the work cache (NANO_WALLET_WORK_CACHE, `work
  precompute`, prework.py / cli.py) and must not both rely on and forbid work_generate;
* the send signs only with a key loaded via NANO_WALLET_KEY_FILE or create_address (keystore.py, key_not_loaded),
  and section 8's file is a SEED, not that key;
* the install it cites must be pinned to section 8's commit; the mandate is required, not optional
  (NANO_WALLET_REQUIRE_MANDATE=1, NANO_WALLET_MAX_SEND_XNO=0.001); the payee is our Unstuck account.

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
        j = self.sec.index("WHAT THE SEND TAKES")
        self.send = self.sec[j:self.sec.index("X-Nano-Payment: <BLOCK_HASH>", j)]
        self.pin = re.search(r'PIN = "([0-9a-f]{40})"', self.txt).group(1)
        with open(os.path.join(ROOT, "ops", "outside-payees.py")) as f:
            self.unstuck = re.search(r'^UNSTUCK = "(nano_[13][13-9a-km-uw-z]{59})"', f.read(), re.M).group(1)

    def test_names_the_capped_send(self):
        for s in ("THE WALLET SECTION 8 FETCHES CAN SEND, CAPPED", '"send" tool', "NANO_WALLET_ALLOW_SEND=1",
                  "NANO_WALLET_MANDATE", "per-payment max 0.001", "allowed payee the payTo above"):
            self.assertIn(s, self.sec)

    def test_commit_is_the_one_section_8_pins(self):
        named = re.search(r"pinned commit \(([0-9a-f]{8})\)", self.sec).group(1)
        self.assertTrue(self.pin.startswith(named), (self.pin, named))

    def test_honest_about_what_was_not_measured(self):
        self.assertIn("we have not paid this call through it", self.sec)
        self.assertIn("unmeasured end to end", self.sec)
        self.assertIn("seedrecv.py is receive-only and never sends", self.sec)

    def test_comes_before_the_paid_post(self):
        self.assertLess(self.sec.index("CAN SEND, CAPPED"), self.sec.index("X-Nano-Payment: <BLOCK_HASH>"))

    # -- MEDIUM: the send's work -------------------------------------------------------------------------------
    def test_names_the_work_cache_not_the_paid_node(self):
        for s in ("ITS SEND NEEDS WORK THE NODE ABOVE SELLS", "LOCAL_SUBTYPES", "work_unavailable",
                  "export NANO_WALLET_WORK_CACHE=", "python3 cli.py work precompute YOUR_FRONTIER",
                  "the SAME NANO_WALLET_WORK_CACHE"):
            self.assertIn(s, self.send)
        self.assertLess(self.send.index("work precompute"), self.send.index("Or: a Nano wallet app"))

    def test_no_contradiction_about_work_generate(self):
        # c1228919 ended with a bare "Do not buy work_generate" after a path that needs it.
        self.assertNotIn("Do not buy work_generate (it costs 0.001)", self.send)
        k = self.send.index("Do not buy rpc.nano.to's work_generate")
        self.assertGreater(k, self.send.index("work precompute"))

    # -- MEDIUM: the payer's key -------------------------------------------------------------------------------
    def test_says_how_the_key_is_loaded(self):
        for s in ("ITS KEY IS NOT YOUR SEED FILE", "NANO_WALLET_KEY_FILE=PATH", "create_address",
                  "key_not_loaded", "private_key_from_seed(seed, 0)"):
            self.assertIn(s, self.send)

    # -- LOW: pinned install, required mandate, payee ----------------------------------------------------------
    def test_install_is_pinned_to_section_8s_commit(self):
        lines = re.findall(r"pip install \S*git\+https://github\.com/dhyabi2/nano-wallet-xno\S*", self.send)
        self.assertTrue(lines, "no pip line")
        for line in lines:
            self.assertIn("@" + self.pin, line)

    def test_mandate_is_required_not_optional(self):
        for s in ("THE MANDATE IS NOT OPTIONAL HERE", "NANO_WALLET_REQUIRE_MANDATE=1", "NANO_WALLET_MAX_SEND_XNO=0.001"):
            self.assertIn(s, self.send)
        self.assertNotRegex(self.send.lower(), r"mandate (is )?optional|skip (it|the mandate)")

    def test_payee_is_our_unstuck_account(self):
        terms = re.search(r"to payTo (nano_\w+), our Unstuck account", self.sec).group(1)
        self.assertEqual(terms, self.unstuck)
        payees = re.findall(r"--payee (nano_\w+)", self.send)
        self.assertEqual(payees, [self.unstuck])


if __name__ == "__main__":
    unittest.main()
