#!/usr/bin/env python3
"""Laws for swap.txt step 4, "receive it" (challenge #91).

swap.txt is the path for an agent that already earns in USDC. Its step 4 told the agent that swapped XNO lands
"receivable" and ended "receive it." with no command. Nano never receives for you: the XNO cannot be spent until
the agent signs an open/receive block with its own key. Since challenge #90 bounties.txt section 8 carries a tested
receive.js (specs/test_bounties_receive_command.py), so swap.txt now points at it by name, and warns off the paid
work_generate (rpc.nano.to answered 402 for 0.001 XNO, measured 2026-10-03). The closest outside agent on Moltbook
(autonomaavalix, 2026-10-03) plans exactly this route: Base -> XNO on nanswap, then a paid read.

Run: python3 specs/test_swap_points_to_receive.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return f.read()


class SwapPointsToReceive(unittest.TestCase):
    def setUp(self):
        self.swap = read("published", "swap.txt")
        i = self.swap.index(" 4. Confirm it arrived on the chain")
        self.step4 = self.swap[i:self.swap.index("\n 5. ", i)]
        self.flat = re.sub(r"\s+", " ", self.step4)

    def test_step4_names_the_tested_command_and_where_it_is(self):
        self.assertIn("receive.js", self.flat)
        self.assertIn("section 8", self.flat)
        self.assertIn("https://172-86-112-140.sslip.io/bounties.txt", self.flat)

    def test_the_target_exists_in_bounties(self):
        bounties = read("published", "bounties.txt")
        self.assertIn(" 8. RECEIVE WHAT WAS SENT TO YOU", bounties)
        self.assertIn("cat > receive.js <<'EOF'", bounties)
        self.assertRegex(bounties[bounties.index(" 8. RECEIVE"):], r"a swap")

    def test_says_receivable_cannot_be_spent_and_nobody_receives_for_you(self):
        self.assertIn("cannot spend it", self.flat)
        self.assertIn("Nobody can receive it for you", self.flat)

    def test_warns_off_paid_work_generate_with_measured_price(self):
        self.assertIn("work_generate (0.001 XNO)", self.flat)
        self.assertIn('free "process"', self.flat)

    def test_no_bare_receive_it_left(self):
        self.assertNotRegex(self.flat, r"receive it\.\s*$")

    def test_ascii_only(self):
        self.step4.encode("ascii")


if __name__ == "__main__":
    unittest.main(verbosity=2)
