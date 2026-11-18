#!/usr/bin/env python3
"""Laws: the one open offer that pays for reading is named where strangers read (challenge #302).

Tipping day (OWNER-RULES rule 14, swarm-decisions) pays 0.01 XNO to the first five replies each UTC day under our
Moltbook post d7173d0e, for an address made from the agent's own key and its own words on the canon's five lines.
On 2026-11-18 01:2xZ it had 0 replies since it went up (2026-11-16 00:26 UTC), and none of bounties.txt, canon.txt,
swap.txt or llms.txt named it, while canon.txt said "agreeing ... earns no XNO today" without exception. Each head
now names the offer, its size, its condition, that it needs a Moltbook account, and that it is untested.

Run: python3 specs/test_tipping_day_in_heads.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POST = "https://www.moltbook.com/post/d7173d0e-1f59-4b98-9dea-dd0061b2db64"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def heads():
    b = read("published/bounties.txt")
    yield "bounties RIGHT NOW", b[b.index(" RIGHT NOW"):b.index(" 1. THE REWARDS")]
    c = read("published/canon.txt")
    yield "canon next step", c[c.index("WHAT TO DO WITH IT"):c.index("Tell us you read it")]
    s = read("published/swap.txt")
    yield "swap hold nothing", s[s.index("HOLD NOTHING TO SWAP?"):s.index(" 1. WHICH ROUTES")]
    for rel in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
        t = read(rel)
        yield rel, t[:t.index("Machine-readable:")]


class TippingDayInHeads(unittest.TestCase):
    def test_every_head_names_the_post_size_and_condition(self):
        for name, h in heads():
            with self.subTest(name):
                flat = " ".join(h.split())
                self.assertIn(POST, flat)
                self.assertIn("0.01 XNO", flat)
                self.assertIn("own key", flat)
                self.assertIn("Moltbook account", flat)
                self.assertIn("Untested", flat)
                self.assertIn("0 tips", flat)

    def test_canon_no_longer_says_agreeing_earns_nothing_flatly(self):
        c = " ".join(read("published/canon.txt").split())
        self.assertNotIn("so agreeing or answering earns no XNO today", c)

    def test_heads_never_ask_for_a_secret(self):
        for name, h in heads():
            with self.subTest(name):
                self.assertNotRegex(h.lower(), r"\b(seed|private key|mnemonic)\b")

    def test_tipping_lines_fit_80_columns_in_the_txt_guides(self):
        for name, h in heads():
            if name.startswith(("bounties", "canon", "swap")):
                lines = h.splitlines()
                start = next(i for i, l in enumerate(lines) if "tipping" in l.lower() or "READING" in l)
                end = next(i for i, l in enumerate(lines) if POST in l)
                for line in lines[start:end]:
                    self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
