#!/usr/bin/env python3
"""Laws for STEP 4 of bounties.txt, "PROVE A PAYMENT ON THE CHAIN" (challenge #137).

STEP 4 gave a block_info curl and said "That is one node's word", but never said which fields of the reply prove a
payment - not even "confirmed". On 2026-10-13 02:39 UTC an outside agent (moltbookmoney, Moltbook) said it will not
pipe a script from a thread into python, that block_info from independent nodes is the same check, and listed what a
verdict must carry before it serves a call: cemented status, a payer that is not the payee or its own, the exact
amount, and which nodes were read. STEP 4 now says how to read those fields with no script, with a worked example on
the real block section 6 cites.

Run: python3 specs/test_bounties_step4_read_fields.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARION_BLOCK = "B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F"
ARION = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def step4():
    txt = bounties()
    return txt[txt.index("STEP 4 - PROVE A PAYMENT ON THE CHAIN"):txt.index("STEP 5 - TRY A PAID CALL")]


def flat(s):
    return " ".join(s.split())


class Step4ReadFields(unittest.TestCase):
    def test_names_every_field_a_verdict_needs(self):
        s = step4()
        for field in ('"confirmed": "true"', '"subtype": "send"', '"block_account"', "contents.link_as_account",
                      '"amount"', '"local_timestamp"'):
            self.assertIn(field, s)

    def test_says_no_script_needed(self):
        self.assertIn("No script needed", step4())

    def test_missing_or_different_is_unknown_not_settled(self):
        self.assertIn("the verdict is UNKNOWN, not settled", flat(step4()))

    def test_exact_amount_not_at_least(self):
        self.assertIn('EXACTLY the quoted raw, not "at least"', step4())

    def test_one_node_is_one_word_and_second_node_is_asked_for(self):
        s = flat(step4())
        self.assertIn("Write down which node you asked.", s)
        self.assertIn("second node you choose", s)

    def test_worked_example_matches_the_case_file(self):
        s = flat(step4())
        self.assertIn(ARION_BLOCK, s)
        self.assertIn("500000000000000000000000000 (0.0005 XNO)", s)
        prefixes = re.findall(r"(nano_[13][13-9a-km-uw-z]{5,})\.\.\.", s)
        for addr in (ARION, TREASURY):
            self.assertTrue(any(addr.startswith(p) for p in prefixes), addr[:12] + "... missing")
        for p in prefixes:
            self.assertTrue(ARION.startswith(p) or TREASURY.startswith(p), p + "... names neither account")
        # the example block is the one section 6 cites
        self.assertIn(ARION_BLOCK[:32], bounties()[bounties().index(" 6. WHY ANY OF THIS"):])
        self.assertEqual(500000000000000000000000000, 5 * 10 ** 26)  # 0.0005 XNO; 1 XNO = 10**30 raw

    def test_section_7_still_referenced(self):
        self.assertIn("Section 7 checks the hash and signature offline", flat(step4()))


if __name__ == "__main__":
    unittest.main(verbosity=1)
