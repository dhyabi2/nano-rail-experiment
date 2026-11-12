#!/usr/bin/env python3
"""Law: the AI directory says how its paid step 6 is paid (challenge #256).

Measured 2026-11-12 00:18 UTC: the AI directory had 51 distinct outside clients on 11-11 (/ai/traffic), bounties.txt
11 - it is the guide strangers read. Its onboarding step 6 runs `curl -s https://extract.paypercall.dev/api/v1/nano-info`,
which answers HTTP 402 "Pay 0.0005 XNO to nano_3z335ug5oz... and retry with X-PAYMENT header". No copy of the
directory (two llms.txt, two index.html, tools.json) contained the string X-PAYMENT, or said that the header carries
the 64-hex hash of the send: an agent that had XNO still stopped at the 402. bounties.txt section 4 ("HOW A CALL IS
PAID") has said it since October.

This law: every copy carries "HOW STEP 6 IS PAID" inside step 6, after its command and before the next section, with
the X-PAYMENT header on step 6's own URL, "64-hex", "send EXACTLY", "payment_invalid", the amount in raw that the
manifest names for nano-info, the pointer to bounties.txt's "HOW A CALL IS PAID" (which must still exist and use the
same header), and the echo exception (X-Nano-Payment).

Run: python3 specs/test_aidirectory_how_to_pay.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ["published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html"]
HEAD = "HOW STEP 6 IS PAID"
URL = "https://extract.paypercall.dev/api/v1/nano-info"
RAW = "500000000000000000000000000"


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        s = f.read()
    if rel.endswith(".html"):
        s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&quot;", '"').replace("&#x27;", "'").replace("&gt;", ">").replace("&lt;", "<")
    return " ".join(s.split())


class HowStep6IsPaid(unittest.TestCase):
    def check(self, rel, b):
        self.assertIn("X-PAYMENT: <BLOCK_HASH>", b, rel)
        self.assertIn(URL, b, rel)
        self.assertIn("64-hex", b, rel)
        self.assertIn("send EXACTLY", b, rel)
        self.assertIn(RAW + " raw (0.0005 XNO)", b, rel)
        self.assertIn('"payment_invalid"', b, rel)
        self.assertIn("the payTo the live 402 names", b, rel)
        self.assertIn('"HOW A CALL IS PAID"', b, rel)
        self.assertIn("prepay.py", b, rel)
        self.assertIn("X-Nano-Payment", b, rel)

    def test_every_copy_inside_step6(self):
        for rel in COPIES:
            s = flat(rel)
            i6 = s.index("Spend it on something real")
            i = s.index(HEAD)
            end = s.index("CHECK THEY ANSWER BEFORE YOU SEND ANY XNO", i6)
            self.assertLess(i6, i, rel)
            self.assertLess(i, end, rel)
            self.assertLess(s.index(URL, i6), i, rel)
            self.check(rel, s[i:end])

    def test_tools_json_step6(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            d = json.load(f)
        six = [x for x in d["onboarding"] if x["n"] == "6"][0]
        self.assertEqual(six["cmd"], "curl -s '%s'" % URL)
        h = six["how_to_pay"]
        self.assertTrue(h["why"].startswith(HEAD))
        self.assertEqual(h["cmd"], "curl -s -H 'X-PAYMENT: <BLOCK_HASH>' '%s'" % URL)
        self.check("tools.json", " ".join([h["why"], h["cmd"], h["then"]]))

    def test_bounties_section_named_uses_same_header(self):
        s = flat("published/bounties.txt")
        i = s.index("HOW A CALL IS PAID")
        self.assertLess(s.index(" 4. OPEN YOUR ACCOUNT"), i)
        self.assertLess(i, s.index(" 5. THE NETWORK"))
        part = s[i:i + 1500]
        self.assertIn("X-PAYMENT: <BLOCK_HASH>", part)
        self.assertIn("64-hex block hash", part)
        self.assertIn("payment_invalid", part)
        self.assertIn("prepay.py", s)

    def test_raw_matches_manifest_snapshot(self):
        # the directory's own listing names nano-info at 0.0005 XNO; 0.0005 * 10^30 raw
        self.assertEqual(int(RAW), 5 * 10 ** 26)
        s = flat("published/aidirectory/llms.txt")
        self.assertIn("ccount intelligence for 0.0005 XNO", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
