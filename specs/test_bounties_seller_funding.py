#!/usr/bin/env python3
"""Laws for what bounties.txt says about who funded the agents it calls "not ours" (challenge #123).

bounties.txt section 5 said "Two agents that are not ours sell a service for XNO here" and named pyfile-toolkit
(nano_3uojbn47...). On 2026-10-11 rpc.nano.to account_history showed 149.0 of the 151.26 XNO that account ever
received came from nano_1xug1q5t7..., the account that also sent our treasury 40.5 XNO; and tvl.json's 227.97 XNO
"the agents on the network actually hold" was 94% that same account. A stranger who checks either finds our funder,
and reads every "outside" claim on the page as staged. The page now says so next to each claim and gives a command
that prints an account's top senders. This runs that command offline against a fixture shaped like the node's reply,
and keeps the KNOWN_OUTSIDE list from calling pyfile-toolkit outside again without new evidence.

Challenge #124 (same day): the #123 text said "Only ARION's money is shown to be its own". ARION's own history says
19.65 of the 29.03 XNO it ever received came from that same funder (2026-09-28/29). Its 2026-09-23 payment to us
still came out of Nanswap money received that morning, so the page now says the first payment was its own and the
later money is not shown to be, with the same top-senders command for ARION's address.

Challenge #125 (same day): the tvl note's "215.25 of it (94%)" was a day old when it went live. By 04:17 UTC the
file said 157.98 and the funder held 133.25 (84%) after sending 82 XNO away on 10-10, so a sceptic who checked found
our figure contradicting the file we link. The note now dates both readings and carries a command that prints the
file's own top 3 with their share; it is run here against a fixture.

Run: python3 specs/test_bounties_seller_funding.py
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARION = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
PYFILE = "nano_3uojbn47b5xqcbs4yibbasamn8aeyqxgyi1z8peogwtdn6z3kagjanjpz4ss"
FUNDER = "nano_1xug1q5t7nxoj3ywwzokiea9jz8fq8qfgzp8pbyfr3co3e5xgj755uofu8ue"
XNO = 10 ** 30

HISTORY = {"account": PYFILE, "history": [
    {"type": "receive", "account": FUNDER, "amount": str(4 * XNO)},
    {"type": "send", "account": "nano_3kekc5z6wdi8a", "amount": str(50 * XNO)},
    {"type": "receive", "account": FUNDER, "amount": str(145 * XNO + 10 ** 27)},
    {"type": "receive", "account": "nano_3kekc5z6wdi8aaaaa", "amount": str(2 * XNO)},
    {"type": "receive", "account": "nano_3zzzzzzzzzzzzzzzz", "amount": str(10 ** 28)},
    {"type": "receive", "account": "nano_3yyyyyyyyyyyyyyyy", "amount": str(10 ** 27)},
]}


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def funding_command(txt, account=PYFILE):
    cmds = re.findall(r"^   curl -s https://rpc\.nano\.to .*?\"account\":\"" + account + r"\".*?\| python3 -c \"(.*?)\"\n",
                      txt, re.M)
    return cmds[0] if len(cmds) == 1 else None


class SellerFunding(unittest.TestCase):
    def test_the_page_no_longer_calls_both_sellers_not_ours(self):
        txt = bounties()
        self.assertNotIn("Two agents that are not ours sell", txt)
        self.assertIn("Two agents we do not run sell", txt)
        self.assertIn("ITS MONEY IS NOT SHOWN TO BE ITS OWN", txt)
        self.assertIn("149.0 of the 151.26 XNO", txt)
        self.assertIn("nano_1xug1q5t7...", txt)

    def test_tvl_note_names_the_one_account_behind_the_total(self):
        txt = bounties()
        self.assertIn('THEN READ "top" BEFORE THE TOTAL', txt)
        self.assertIn("215.25 of it (94%)", txt)

    def test_tvl_note_carries_both_dated_readings(self):
        txt = bounties()
        self.assertIn("on 2026-10-10 04:17 UTC it was 227.97 XNO", txt)
        self.assertIn("(updated 2026-10-11 04:17 UTC", txt)
        self.assertIn("It still held 133.25 (84%)", txt)

    def test_tvl_top_command_prints_share_and_age(self):
        cmds = re.findall(r"^   curl -s https://172-86-112-140\.sslip\.io/tvl\.json \| python3 -c \"(.*?)\"\n", bounties(), re.M)
        self.assertEqual(len(cmds), 1, "bounties.txt must carry exactly one tvl.json top-3 command")
        tvl = {"updated": "2026-10-11T04:17:03Z", "complete": True, "tvl_xno": 157.98372998183015, "top": [
            {"address": FUNDER, "balance_xno": 133.247456290742},
            {"address": PYFILE, "balance_xno": 22.1515905786748},
            {"address": "nano_1bfapscrwk7t66faz9emcqo318698d4yc9n7p8rh8gjuttg8ehgajgzw4bk1", "balance_xno": 2.05},
            {"address": ARION, "balance_xno": 0.209}]}
        r = subprocess.run([sys.executable, "-c", cmds[0]], input=json.dumps(tvl),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines(), [
            FUNDER[:16] + " 133.25 XNO 84 %", PYFILE[:16] + " 22.15 XNO 14 %", "nano_1bfapscrwk7 2.05 XNO 1 %",
            "total 157.98 complete True updated 2026-10-11T04:17:03Z"])
        tvl.update(tvl_xno=0.0, complete=False, top=[{"address": FUNDER, "balance_xno": 0.0}])
        r = subprocess.run([sys.executable, "-c", cmds[0]], input=json.dumps(tvl),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("complete False", r.stdout)

    def test_funding_command_prints_top_senders(self):
        code = funding_command(bounties())
        self.assertIsNotNone(code, "bounties.txt must carry exactly one top-senders command for pyfile-toolkit")
        r = subprocess.run([sys.executable, "-c", code], input=json.dumps(HISTORY),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        lines = r.stdout.splitlines()
        self.assertEqual(len(lines), 3)
        self.assertEqual(lines[0], FUNDER[:16] + " 149.001 XNO")
        self.assertEqual(lines[1], "nano_3kekc5z6wdi 2.0 XNO")

    def test_arion_is_not_called_independent(self):
        txt = bounties()
        self.assertNotIn("ARION's money is shown to be its own", txt)
        self.assertNotIn("not ours sell", txt)
        self.assertNotIn("sellers there are not ours", txt)
        self.assertNotIn("first settled payment between two agents that are not us", txt)
        self.assertIn("NEITHER IS SHOWN TO BE INDEPENDENT OF US TODAY", txt)
        self.assertIn("19.65 of the 29.03 XNO", txt)
        self.assertIn("ITS FIRST PAYMENT WAS ITS OWN", txt)

    def test_arion_funding_command_prints_top_senders(self):
        code = funding_command(bounties(), ARION)
        self.assertIsNotNone(code, "bounties.txt must carry exactly one top-senders command for ARION")
        hist = dict(HISTORY, account=ARION)
        r = subprocess.run([sys.executable, "-c", code], input=json.dumps(hist),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0], FUNDER[:16] + " 149.001 XNO")

    def test_pyfile_is_not_known_outside_without_evidence(self):
        path = os.path.join(ROOT, "ops", "unpaid-outside-answers.py")
        spec = importlib.util.spec_from_file_location("upoa", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertNotIn(PYFILE, mod.KNOWN_OUTSIDE)
        self.assertNotIn(FUNDER, mod.KNOWN_OUTSIDE)


if __name__ == "__main__":
    unittest.main()
