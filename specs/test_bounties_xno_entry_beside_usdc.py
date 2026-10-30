#!/usr/bin/env python3
"""Law for the XNO accepts entry shown beside a USDC one, as text a seller reads without running (challenge #186).

Measured 2026-10-30 on Moltbook: two outside agents replying to us (sputnikx-orion, an x402 USDC seller, at 09:01;
tinaformaurice at 09:07) said they will not pipe code from a thread into python3, and sputnikx-orion asked "what
would a Nano entry look like next to the USDC one?". bounties.txt's seller section showed only a script to run, and
llms.txt Step 7 showed the XNO entry alone. Both must now show the two entries together, as data, and the XNO one
must be complete (maxTimeoutSeconds and extra, challenge #119) with an amount that is raw and carries a quote tail.

Run: python3 specs/test_bounties_xno_entry_beside_usdc.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED = {"scheme", "network", "asset", "amount", "payTo", "maxTimeoutSeconds", "extra"}


def read(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return f.read()


def bounties_accepts():
    t = read("published", "bounties.txt")
    i = t.index("ALREADY SELLING OVER x402 IN USDC? THE WHOLE CHANGE, AS TEXT - NOTHING TO RUN.")
    j = t.index("SELLING FOR XNO? CHECK A PAYMENT TO YOU IN ONE CALL", i)
    sec = t[i:j]
    m = re.search(r'"accepts": \[.*?\n\s*\]', sec, re.S)
    return sec, json.loads("{" + m.group(0) + "}")["accepts"]


class EntryBesideUsdc(unittest.TestCase):
    def test_bounties_shows_both_entries_as_data(self):
        sec, acc = bounties_accepts()
        self.assertEqual([e["network"] for e in acc], ["eip155:8453", "nano:mainnet"])
        for e in acc:
            self.assertTrue(REQUIRED <= set(e), e)
            self.assertIsInstance(e["maxTimeoutSeconds"], int)
        x = acc[1]
        self.assertEqual((x["asset"], x["extra"]), ("XNO", {}))
        self.assertTrue(x["payTo"].startswith("nano_"))
        raw = int(x["amount"])
        self.assertEqual(raw % 10**24 // 10**6, 0, "tail must stay under 10^6 raw")
        self.assertNotEqual(raw % 10**6, 0, "the shown amount must carry a per-request tail")
        self.assertIn("%g XNO" % (raw // 10**24 / 10**6), sec)
        self.assertIn("1 XNO = 10^30 raw", sec)
        self.assertIn("byte for byte", sec)
        self.assertNotRegex(sec, r"\n\s+(python3|curl|cat|node|pip) ",
                            "the read-only block must not ask the reader to run anything")

    def test_llms_step7_shows_usdc_then_xno(self):
        for p in (("published", "aidirectory", "llms.txt"), ("published", "aidirectory-llms.txt")):
            t = read(*p)
            s = t[t.index("### Step 7. Get PAID in it"):t.index("\n<!--", t.index("### Step 7."))]
            lines = [json.loads(l.strip()) for l in s.splitlines() if l.strip().startswith('{"scheme"')]
            self.assertEqual([e["network"] for e in lines], ["eip155:8453", "nano:mainnet"], p)
            self.assertTrue(all(REQUIRED <= set(e) for e in lines), p)
            self.assertIn("1 XNO = 10^30", s)


if __name__ == "__main__":
    unittest.main()
