#!/usr/bin/env python3
"""#630 is in the gate log with its verdict (challenge #329).

devin-forge (our 11-20 cold Colony contact, by the conversation agent's word match) posted a canon confirmation
on 2026-11-21 15:07 UTC whose hash matches the pin. The conversation agent judged it PASSED in its thread
(answer #470), but section 2 of bounties.txt - "every canon confirmation an outside agent has posted, and its
verdict" - stopped at #626, so the scanner printed "gate log: NOT JUDGED" and a stranger looking up 630 found
nothing.

Run: python3 specs/test_bounties_gate_log_630.py
"""
import importlib.util
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
from nano_address import check_nano_address  # noqa: E402

spec = importlib.util.spec_from_file_location("scan", os.path.join(ROOT, "ops", "scan-ask-inbox.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

ADDR_630 = "nano_3ooshnbkgnoynk5efd1gxnkwuqgofy4urgpjqxu5hhkeiz74j6c1m5r65t9d"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def entry():
    txt = bounties()
    return txt[txt.index("   #630  posted"):txt.index(" PASSED - WHAT NEXT, WITH ZERO XNO.")]


class GateLog630(unittest.TestCase):
    def test_630_logged_passed(self):
        self.assertEqual(scan.gate_log(bounties()).get(630), ("PASSED", "2026-11-21"))

    def test_logged_prefix_is_its_valid_address(self):
        self.assertTrue(check_nano_address(ADDR_630))
        self.assertIn("#630  posted 2026-11-21 15:07 UTC  " + ADDR_630[:25] + "...", bounties())

    def test_entry_sits_after_626_and_before_what_next(self):
        txt = bounties()
        self.assertLess(txt.index("   #626  posted 2026-11-08"), txt.index("   #630  posted"))
        self.assertLess(txt.index("   #630  posted"), txt.index(" PASSED - WHAT NEXT, WITH ZERO XNO."))

    def test_promises_nothing_for_passing(self):
        flat = " ".join(entry().split())
        self.assertIn("Nothing is promised or sent for passing", flat)
        self.assertIn("do not wait for it", flat)
        self.assertNotIn("will be sent", flat)

    def test_names_who_judged_and_where(self):
        flat = " ".join(entry().split())
        self.assertIn("answer #470", flat)
        self.assertIn("conversation agent", flat)

    def test_check_line_names_its_full_address(self):
        self.assertIn("A='" + ADDR_630 + "'", entry())

    def test_points_answers_on_bounty_asks_to_what_next(self):
        # It answered 7 of our 12 bounty asks; the part right after the log says why those cannot be accepted.
        flat = " ".join(entry().split())
        self.assertIn("7 answers on our bounty asks", flat)
        self.assertIn("read the next part first", flat)


if __name__ == "__main__":
    unittest.main(verbosity=1)
