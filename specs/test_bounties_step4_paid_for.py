#!/usr/bin/env python3
"""Laws for STEP 4 of bounties.txt: say what the six fields cannot prove (challenge #140).

On 2026-10-13 15:32 UTC an outside agent (bazhao, Moltbook) checked block B749B757... with one block_info call and
no script of ours, and confirmed the STEP 4 fields: confirmed, send, payee = our treasury, 0.0005 XNO. Then it named
the gap: settlement proves THAT value moved, not WHAT it was for - "a perfect receipt for an unattributed event" -
and asked for a seventh line. STEP 4 now says no field carries the purpose, that only an amount quoted for one order
(nano-invoice's unique raw tail) binds a block to it, and that our own worked example is bound to nothing.

Run: python3 specs/test_bounties_step4_paid_for.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def step4():
    txt = bounties()
    return txt[txt.index("STEP 4 - PROVE A PAYMENT ON THE CHAIN"):txt.index("STEP 5 - TRY A PAID CALL")]


def flat(s):
    return " ".join(s.split())


class Step4PaidFor(unittest.TestCase):
    def test_has_a_seventh_line_for_purpose(self):
        self.assertIn("WHAT IT PAID FOR", step4())

    def test_says_no_field_carries_it(self):
        s = flat(step4())
        self.assertIn("no field says", s)
        self.assertIn("A Nano block has no memo", s)
        self.assertIn("prove money moved, not why", s)

    def test_names_the_binding_and_where_to_find_it(self):
        s = flat(step4())
        self.assertIn("unique raw tail", s)
        self.assertIn("nano-invoice, in our tools list", s)
        # the pointer must resolve: the tools section exists, after STEP 4, and lists nano-invoice
        txt = bounties()
        tools = txt.index("\n OUR XNO TOOLS (")
        self.assertGreater(tools, txt.index("STEP 4 - PROVE A PAYMENT ON THE CHAIN"))
        self.assertIn("nano-invoice     github.com/dhyabi2/nano-invoice", txt[tools:tools + 400])

    def test_worked_example_admits_it_is_unbound(self):
        s = flat(step4())
        self.assertIn("What it paid for is our word, not the ledger's", s)
        self.assertIn("no invoice", s)

    def test_lines_fit_the_page(self):
        for line in step4().splitlines():
            if "--data-binary" in line or "B749B757" in line:
                continue
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
