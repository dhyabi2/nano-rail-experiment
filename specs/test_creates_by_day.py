#!/usr/bin/env python3
"""Laws for ops/creates-by-day.py (challenge #222).

On 2026-11-03 the traffic file counted 12 responses 201 (something created) while the network showed
0 asks and 0 answers that day, and the journal said nobody posted. These laws pin: every 201 not
matched by an ask or answer of that day (ours included) is UNEXPLAINED and printed as such, never
dropped; a day with as many asks/answers as creates prints no remainder; a partial day says so.

Run: python3 specs/test_creates_by_day.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("cbd", os.path.join(ROOT, "ops", "creates-by-day.py"))
cbd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cbd)


def report(asks, answers):
    return {"totals": {"asks": asks, "answers": answers}}


def traffic(n201, complete=True):
    return {"generated_utc": "2026-11-04T00:07:02+00:00", "complete_day": complete, "status": {"200": 900, "201": n201}}


class CreatesByDay(unittest.TestCase):
    def test_1103_twelve_creates_nothing_named(self):
        r = cbd.build("2026-11-03", traffic(12), report(0, 0))
        self.assertEqual(r["unexplained"], 12)
        out = cbd.render(r)
        self.assertIn("UNEXPLAINED 12", out)
        self.assertIn("onramp/self", out)
        self.assertIn("Not zero outside activity", out)

    def test_1104_burst_mostly_named(self):
        r = cbd.build("2026-11-04", traffic(9), report(7, 1))
        self.assertEqual(r["named"], 8)
        self.assertEqual(r["unexplained"], 1)

    def test_all_named_prints_no_remainder(self):
        r = cbd.build("2026-11-01", traffic(2), report(1, 1))
        self.assertEqual(r["unexplained"], 0)
        self.assertEqual(r["possible_creators"], [])
        self.assertIn("Every create is an ask or an answer", cbd.render(r))

    def test_more_named_than_created_is_not_negative(self):
        r = cbd.build("2026-11-02", traffic(1, complete=False), report(2, 1))
        self.assertEqual(r["unexplained"], 0)
        self.assertTrue(r["more_named_than_created"])
        out = cbd.render(r)
        self.assertIn("(partial day)", out)
        self.assertIn("partial or missed", out)

    def test_missing_status_is_unknown_not_zero(self):
        # A file with no status table was not read; "0 creates" from it is a confident false zero.
        with self.assertRaises(cbd.Unknown):
            cbd.build("2026-11-06", {"generated_utc": None, "complete_day": False}, report(0, 0))

    def test_renamed_or_non_object_status_is_unknown(self):
        for bad in ({"statuses": {"201": 3}}, {"status": ["201", 3]}, {"status": None}):
            with self.assertRaises(cbd.Unknown, msg=bad):
                cbd.build("2026-11-06", bad, report(0, 0))

    def test_non_int_201_is_unknown_not_a_traceback(self):
        for bad in (None, "many", 1.5, True, -1):
            with self.assertRaises(cbd.Unknown, msg=repr(bad)):
                cbd.build("2026-11-06", {"status": {"201": bad}}, report(0, 0))

    def test_list_traffic_file_is_unknown_not_attribute_error(self):
        with self.assertRaises(cbd.Unknown):
            cbd.build("2026-11-06", [{"201": 3}], report(0, 0))

    def test_status_without_201_is_a_day_with_no_creates(self):
        r = cbd.build("2026-11-06", {"status": {"200": 40}}, report(0, 0))
        self.assertEqual(r["creates_201"], 0)

    def test_bad_day_exits_2_before_any_fetch(self):
        import subprocess, sys
        p = subprocess.run([sys.executable, os.path.join(ROOT, "ops", "creates-by-day.py"), "2026-11-03/../deploy-status"],
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(p.returncode, 2)
        self.assertIn("UNKNOWN", p.stderr)


if __name__ == "__main__":
    unittest.main()
