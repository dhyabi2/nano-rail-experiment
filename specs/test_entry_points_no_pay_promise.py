#!/usr/bin/env python3
"""Laws for the entry points that send readers to bounties.txt (challenge #224).

bounties.txt's RIGHT NOW box says no reward has been sent since 2026-10-13 and no answer earns XNO today (0 of 63
asks settled). The pages a stranger reaches first still said otherwise: canon.txt "Get paid for agreeing", the
AiDirectory asks row "answer one and be paid", swap.txt's footer and canon.html's bounty table with no state at all.
These laws keep every entry point from promising pay without pointing at the RIGHT NOW box.

Run: python3 specs/test_entry_points_no_pay_promise.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENTRY = ["published/canon.txt", "published/canon.html", "published/swap.txt",
         "published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
         "published/aidirectory/index.html", "published/aidirectory.html",
         "published/aidirectory/tools.json"]


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


class EntryPointsNoPayPromise(unittest.TestCase):
    def test_no_entry_point_promises_pay_for_answering_or_agreeing(self):
        for rel in ENTRY:
            t = read(rel)
            self.assertNotIn("answer one and be paid", t, rel)
            self.assertNotIn("Get paid for agreeing", t, rel)
            self.assertNotIn("with bounties settled on chain", t, rel)

    def test_every_entry_point_that_names_the_rewards_points_at_right_now(self):
        for rel in ["published/canon.txt", "published/canon.html", "published/swap.txt"]:
            self.assertIn("RIGHT NOW box", read(rel), rel)

    def test_asks_row_says_an_answer_earns_no_xno_and_names_the_box(self):
        for rel in ENTRY[3:]:
            t = read(rel)
            self.assertIn("an answer earns no XNO today", t, rel)
            self.assertIn("bounties.txt RIGHT NOW box", t, rel)

    def test_bounties_box_still_says_the_same(self):
        b = read("published/bounties.txt")
        box = b[b.index(" RIGHT NOW"):b.index(" 1. THE REWARDS")]
        self.assertIn("AN ANSWER EARNS NO XNO TODAY", box)
        self.assertIn("no 0.1 XNO sent since 10-13", box)

    def test_tools_json_still_parses(self):
        json.loads(read("published/aidirectory/tools.json"))

    def test_mirrors_stay_byte_identical(self):
        self.assertEqual(read("published/aidirectory/llms.txt"), read("published/aidirectory-llms.txt"))
        self.assertEqual(read("published/aidirectory/index.html"), read("published/aidirectory.html"))


if __name__ == "__main__":
    unittest.main()
