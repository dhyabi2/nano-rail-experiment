#!/usr/bin/env python3
"""Section 6's "is our receiver up" check reads the account a payment to us goes to (challenge #246).

Until 11-10 the line "this prints what is waiting at our treasury right now" read the OLD treasury
(nano_1yo6c1t6...), whose seed and auto-receive sit on the Rai box that has been down since 10-19.
A paid call to us today pays the payTo that getunstuck.space's /unstuck/api/v1/x402 names - our Unstuck
account nano_1434j1n4... (section 4). So a stranger who paid us and ran the check read a list that can
never hold its block, and always printed the old 10 XNO as "waiting" - "our receiver is down" for a
receiver that has nothing to do with its payment.

Run: python3 specs/test_bounties_receiver_check_reads_payto.py
"""
import os
import re
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
from nano_address import check_nano_address  # noqa: E402

PAYTO = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
OLD = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def check_block():
    txt = bounties()
    start = txt.index(" One thing against us, since you would find it anyway")
    end = txt.index(" One more against us: WHO HAS PAID OUR TREASURY.")
    return txt[start:end]


class ReceiverCheckReadsPayTo(unittest.TestCase):
    def test_command_reads_the_payto(self):
        block = check_block()
        cmds = [l for l in block.splitlines() if "'action':'receivable'" in l]
        self.assertEqual(len(cmds), 1, "exactly one receivable command in the block")
        self.assertIn("'account':'%s'" % PAYTO, cmds[0])
        self.assertNotIn(OLD, cmds[0])

    def test_payto_is_what_section_4_names(self):
        txt = bounties()
        sec4 = txt[txt.index(" ONE PAID CALL OF OURS DOES ANSWER"):]
        m = re.search(r"payTo\s+(nano_[13][13456789abcdefghijkmnopqrstuwxyz]{59})", sec4)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), PAYTO)
        self.assertTrue(check_nano_address(PAYTO))

    def test_says_old_treasury_is_not_where_you_pay(self):
        block = check_block()
        self.assertIn("no longer where you pay us", block)
        self.assertNotIn("waiting at our treasury right now", block)

    def test_lines_fit(self):
        for l in check_block().splitlines():
            if "python3 -c" in l:
                continue
            self.assertLessEqual(len(l), 81, l)


if __name__ == "__main__":
    unittest.main()
