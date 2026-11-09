#!/usr/bin/env python3
"""#626 is in the gate log with its verdict (challenge #236).

Muse posted a canon confirmation on 2026-11-08 11:55 UTC whose hash matches the pin. Nobody answered in
its thread, so until this entry the scanner said "gate log: NOT JUDGED" and the only place a stranger
learns its verdict - section 2 of bounties.txt - said nothing.

Run: python3 specs/test_bounties_gate_log_626.py
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

ADDR_626 = "nano_1edjtwsjn1ptew5tg3915q6sm6jwzryj7t7frsn4rmu31ujripc5c9nw6aqz"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def entry():
    txt = bounties()
    return txt[txt.index("   #626  posted"):txt.index(" PASSED - WHAT NEXT, WITH ZERO XNO.")]


class GateLog626(unittest.TestCase):
    def test_626_logged_passed(self):
        self.assertEqual(scan.gate_log(bounties()).get(626), ("PASSED", "2026-11-08"))

    def test_logged_prefix_is_its_valid_address(self):
        self.assertTrue(check_nano_address(ADDR_626))
        self.assertIn("#626  posted 2026-11-08 11:55 UTC  " + ADDR_626[:25] + "...", bounties())

    def test_entry_sits_after_593_and_before_what_next(self):
        txt = bounties()
        self.assertLess(txt.index("   #593  posted"), txt.index("   #626  posted"))

    def test_promises_nothing_for_passing(self):
        flat = " ".join(entry().split())
        self.assertIn("Nothing is promised or sent for passing", flat)
        self.assertIn("do not wait for it", flat)

    def test_check_line_names_its_full_address(self):
        self.assertIn("A='" + ADDR_626 + "'", entry())


if __name__ == "__main__":
    unittest.main(verbosity=1)
