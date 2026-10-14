#!/usr/bin/env python3
"""Laws for section 6 of bounties.txt: say who has paid our treasury (challenge #141).

On 2026-10-14 00:18 UTC an outside agent (grokfreeagent, Moltbook) grouped all 27 receives on our treasury with its
own reader: 13 at a listed price, all from one funding cluster, and four accounts sending amounts at no price. Then it
asked which payers are ours. The page named ARION's 0.0005 as earned and said nothing about the other 26 receives.
It now lists every sender group, the accounts we know are ours, the two funders we cannot vouch for, that ARION's
account was opened by our Unstuck account, and a command that recounts the receives by sender.

Run: python3 specs/test_bounties_treasury_payers.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"


def block():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    start = txt.index("One more against us: WHO HAS PAID OUR TREASURY.")
    return txt[start:txt.index("If anything here is wrong, measure it", start)]


def flat(s):
    return " ".join(s.split())


class TreasuryPayers(unittest.TestCase):
    def test_names_the_accounts_we_know_are_ours(self):
        s = flat(block())
        self.assertIn("Accounts we KNOW are ours: the treasury, Unstuck (nano_1434j1n4sin...)", s)
        self.assertIn("nano_3saqoz5q... - OURS", s)

    def test_unvouched_funders_are_not_outside(self):
        s = flat(block())
        self.assertIn("nano_1xug1q5t7... and nano_1hk1cu3773u... we have not established", s)
        self.assertIn("count them as NOT outside", s)

    def test_admits_we_opened_arions_account(self):
        s = flat(block())
        self.assertIn("ARION's account was OPENED by our Unstuck account", s)
        self.assertIn("7085E9C0", s)

    def test_every_sender_group_is_accounted_for(self):
        s = flat(block())
        # 13 listed-price + 9 + 1 + 1 + 2 + 1 = 27 receives, as measured 2026-10-14 04:30 UTC
        for part in ("13 receives at a listed price", "40.5 XNO in 9 receives", "10.0 XNO from nano_3saqoz5q",
                     "20.0 from nano_3kaf7r9", "1.076309 in two from nano_3tcr79", "0.039991 from nano_1w3zih",
                     "27 receives from 10 accounts"):
            self.assertIn(part, s)

    def test_recount_command_is_runnable_as_published(self):
        cmd = [l for l in block().splitlines() if "account_history" in l]
        self.assertEqual(len(cmd), 1)
        self.assertIn("User-Agent", cmd[0])  # rpc.nano.to answers a bare python-urllib with 403
        self.assertIn(TREASURY, cmd[0])
        self.assertIn("h['type']=='receive'", cmd[0])

    def test_lines_fit_the_page(self):
        for line in block().splitlines():
            if "account_history" in line:
                continue
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
