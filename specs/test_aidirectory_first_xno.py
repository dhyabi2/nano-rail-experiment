#!/usr/bin/env python3
"""Law: the AI directory says where the first XNO comes from before its first paid step (challenge #255).

Measured 2026-11-11 20:07 UTC (/ai/traffic): the AI directory had 42 distinct outside clients, bounties.txt 9 - it is
the most-read guide. Its onboarding, "from nothing to paid, in six commands", goes from step 5 (free, no wallet) to
step 6 (a paid call, 0.0001-0.0005 XNO) and no step between puts XNO in the wallet: an agent that follows it to the
letter gets HTTP 402 at step 6 and the page names no way forward. Challenge #84 (2026-10) closed the same gap in
bounties.txt with a "BEFORE STEP 6 - YOUR FIRST XNO" block (swap route, minimum, operator request); the directory
never carried it.

This law: every copy of the directory has the block between step 5 and step 6, its swap minimum equals the one in
bounties.txt and swap.txt, it links both guides, names the bounties.txt section it sends the reader to, never
promises that we fund the reader, and says the starter pays for no call.

Run: python3 specs/test_aidirectory_first_xno.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ["published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html"]
HEAD = "BEFORE STEP 6 - YOUR FIRST XNO."


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        s = f.read()
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&quot;", '"').replace("&#x27;", "'").replace("&gt;", ">").replace("&lt;", "<")
    return " ".join(s.split())


def block_of(s):
    i = s.index(HEAD)
    return s[i:i + 1400]


def bounties_minimum():
    s = flat("published/bounties.txt")
    i = s.index(" BEFORE STEP 6 - YOUR FIRST XNO.")
    return re.search(r"minimum ([0-9.]+) USDC", s[i:]).group(1)


class FirstXnoInDirectory(unittest.TestCase):
    def check(self, rel, b):
        self.assertIn("HTTP 402", b, rel)
        self.assertIn("Nobody here funds it", b, rel)
        self.assertNotRegex(b, r"(?i)we (will )?(send|fund|top up) you", rel)
        self.assertEqual(re.search(r"minimum ([0-9.]+) USDC", b).group(1), bounties_minimum(), rel)
        self.assertIn("https://172-86-112-140.sslip.io/swap.txt", b, rel)
        self.assertIn("https://172-86-112-140.sslip.io/bounties.txt", b, rel)
        self.assertIn('section 4, "BEFORE STEP 6 - YOUR FIRST XNO"', b, rel)
        self.assertIn("pays for no call", b, rel)
        self.assertIn("nano_3z335ug5", b, rel)

    def test_every_copy_between_step5_and_step6(self):
        for rel in COPIES:
            s = flat(rel)
            i5 = s.index("Try a paid call with nothing at stake")
            i = s.index(HEAD)
            i6 = s.index("Spend it on something real", i5)
            self.assertLess(i5, i, rel)
            self.assertLess(i, i6, rel)
            self.check(rel, block_of(s))

    def test_tools_json_step6(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            d = json.load(f)
        six = [x for x in d["onboarding"] if x["n"] == "6"][0]
        self.check("tools.json", six["first_xno"])

    def test_minimum_matches_swap_txt(self):
        swap = flat("published/swap.txt")
        theirs = re.search(r"Minimum ([0-9.]+) USDC-BASE", swap).group(1)
        self.assertEqual(bounties_minimum(), theirs)

    def test_bounties_has_the_section_named(self):
        s = flat("published/bounties.txt")
        i = s.index(" BEFORE STEP 6 - YOUR FIRST XNO.")
        part = s[i:s.index(" STEP 6 - ", i + 10)]
        self.assertIn('"Authorise me to spend up to', part)
        self.assertIn("seedrecv.py", s)
        self.assertIn("receive.js", s)


if __name__ == "__main__":
    unittest.main(verbosity=2)
