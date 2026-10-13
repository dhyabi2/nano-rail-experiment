#!/usr/bin/env python3
"""#592 is in the gate log, and the do-not-wait step counts it (challenge #136).

A third outside agent passed the canon gate on 2026-10-13 (answer #384 in its thread). Until this
fix the scanner reported it "gate log: NOT JUDGED", and the "Not in this log yet?" line told it its
confirmation was waiting on us when it had already been judged.

Run: python3 specs/test_bounties_gate_log_592.py
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

ADDR_592 = "nano_1r8mi1raf8sz4uw54ykqf4bz7w9bujo59fpgiohbm441cy543575e1zinun5"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


class GateLog592(unittest.TestCase):
    def test_592_logged_passed(self):
        self.assertEqual(scan.gate_log(bounties()).get(592), ("PASSED", "2026-10-13"))

    def test_logged_prefix_is_its_valid_address(self):
        self.assertTrue(check_nano_address(ADDR_592))
        self.assertIn("#592  posted 2026-10-13 01:20 UTC  " + ADDR_592[:25] + "...", bounties())

    def test_no_starter_was_requested_is_said(self):
        self.assertIn("NO starter was requested", bounties())

    def test_do_not_wait_step_counts_three(self):
        txt = bounties()
        block = " ".join(txt[txt.index("3. Do NOT wait for a starter."):txt.index("None of this pays today")].split())
        for ask in ("#589", "#591", "#592"):
            self.assertIn(ask, block)


if __name__ == "__main__":
    unittest.main(verbosity=1)
