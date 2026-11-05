#!/usr/bin/env python3
"""Law for what bounties.txt says about receiving payments at our treasury (challenge #165).

Measured 2026-10-27 00:20 UTC: bounties.txt said "new payments are now received automatically every 15 minutes" while
block 5EE71904 (10 XNO, 10-18 08:28) had sat RECEIVABLE at the treasury for 207.9 hours, because the job that receives
runs on the box and the box was down. The sentence sits in the paragraph headed "One thing against us", which is the
one a sceptic re-checks on the chain, so the text must never promise automatic receiving without handing the reader the
command that shows what is waiting right now.

Run: python3 specs/test_bounties_receive_claim.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"


class ReceiveClaim(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()

    def test_no_bare_promise(self):
        flat = re.sub(r"\s+", " ", self.txt)
        self.assertNotIn("new payments are now received automatically", flat)

    def test_against_us_paragraph_carries_a_live_check(self):
        i = self.txt.index("One thing against us")
        para = self.txt[i:self.txt.index("One more against us", i)]
        self.assertIn("5EE71904", para, "the unreceived 10-18 block must be named")
        cmd = [l for l in para.splitlines() if "python3 -c" in l]
        self.assertEqual(len(cmd), 1, "one command that prints what is waiting at the treasury")
        self.assertIn("'action':'receivable'", cmd[0])
        self.assertIn(TREASURY, cmd[0])
        self.assertIn("rpc.nano.to", cmd[0])


if __name__ == "__main__":
    unittest.main()
