"""Law for challenge #298: an agent that met the DAILY terms is named, with its blocks, and called unpaid.

On 2026-11-16 KGNINJA (nano_1edjtwsjn1p..., confirmation #626 passed) made two paid calls to live endpoints:
send 675C14A6 to our treasury2 (one Vend mcp-find call) and send B55BF592 to NanoGPT. bounties.txt section 1's
DAILY reward says "0.1 XNO to every agent that contributed something CHECKABLE that day: ... a paid call you made to
a live endpoint (its block)". At 00:2x UTC 11-17 our four accounts had sent it nothing but its starter. The page
said only "no 0.1 XNO sent since 10-13": the first agent to meet a reward's terms could not see that we know.

These laws hold the page to the measured state: section 1 names the agent, both blocks and that it is unpaid; the
RIGHT NOW box points at it; and the page's own check one-liner, run on the measured history, prints "none".
When a 0.1 XNO block is sent, the text and the fixture change together.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
FIXTURE = os.path.join(ROOT, "specs", "fixtures", "kgninja-history-2026-11-17.json")
GRANT_RAW = "100000000000000000000000000000"  # 0.1 XNO
KG = "nano_1edjtwsjn1ptew5tg3915q6sm6jwzryj7t7frsn4rmu31ujripc5c9nw6aqz"


def flat(s):
    return " ".join(s.split())


class DailyQualifierNamed(unittest.TestCase):
    def setUp(self):
        with open(BOUNTIES, encoding="utf-8") as f:
            self.txt = f.read()
        self.box = flat(self.txt[self.txt.index(" RIGHT NOW - measured "):self.txt.index(" 1. THE REWARDS")])
        self.sec1 = self.txt[self.txt.index(" 1. THE REWARDS"):self.txt.index(" 2. THE CONFIRMATION")]
        self.flat1 = flat(self.sec1)
        with open(FIXTURE, encoding="utf-8") as f:
            self.hist = json.load(f)

    def test_section_one_names_the_qualifier_and_both_blocks(self):
        self.assertIn("MET THE DAILY TERMS, NOT PAID", self.flat1)
        self.assertIn("KGNINJA (nano_1edjtwsjn1p...", self.flat1)
        self.assertIn("#626 passed", self.flat1)
        self.assertIn("send 675C14A6...", self.flat1)
        self.assertIn("send B55BF592...", self.flat1)
        self.assertIn("until a 0.1 XNO block from us exists, it is unpaid", self.flat1)

    def test_box_points_at_it(self):
        self.assertIn("one agent met the DAILY terms on 11-16, unpaid (section 1)", self.box)
        self.assertIn("MET THE DAILY TERMS", self.sec1)

    def test_box_lines_fit_eighty_columns(self):
        box = self.txt[self.txt.index(" RIGHT NOW - measured "):self.txt.index(" 1. THE REWARDS")]
        for line in box.splitlines():
            if "curl " in line or "for h in" in line:
                continue  # copy-paste commands stay on one line
            self.assertLessEqual(len(line), 80, line)

    def test_blocks_named_are_in_the_measured_history(self):
        hashes = {h["hash"]: h for h in self.hist["history"]}
        self.assertEqual(self.hist["account"], KG)
        self.assertEqual(hashes["675C14A6"]["type"], "send")
        self.assertTrue(hashes["675C14A6"]["account"].startswith("nano_3z335ug5"))
        self.assertEqual(hashes["675C14A6"]["amount"], str(10 ** 26))  # 0.0001 XNO
        self.assertEqual(hashes["B55BF592"]["type"], "send")
        self.assertEqual(hashes["B55BF592"]["amount"], str(10322 * 10 ** 22))  # 0.00010322 XNO

    def test_page_one_liner_prints_none_on_the_measured_history(self):
        line = [l for l in self.sec1.splitlines() if "0.1 XNO from us:" in l]
        self.assertEqual(len(line), 1)
        cmd = line[0]
        self.assertIn("A='%s'" % KG, cmd)
        self.assertIn("x['amount']=='%s'" % GRANT_RAW, cmd)
        o = re.search(r"O=\(([^)]*)\)", cmd).group(1)
        ours = tuple(p.strip().strip("'") for p in o.split(","))
        self.assertEqual(set(ours), {"nano_1434j1n4", "nano_3saqoz5q", "nano_1yo6c1t6", "nano_3z335ug5"})
        h = self.hist["history"]
        got = [x["hash"][:8] for x in h if x["account"][:13] in ours and x["amount"] == GRANT_RAW] or "none"
        self.assertEqual(got, "none")
        # and the filter does catch a grant when one exists
        h2 = h + [{"type": "receive", "account": "nano_3z335ug5x", "amount": GRANT_RAW, "hash": "AAAABBBB"}]
        self.assertEqual([x["hash"][:8] for x in h2 if x["account"][:13] in ours and x["amount"] == GRANT_RAW], ["AAAABBBB"])


if __name__ == "__main__":
    unittest.main()
