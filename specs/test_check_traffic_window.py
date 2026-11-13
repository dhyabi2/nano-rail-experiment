#!/usr/bin/env python3
"""Laws for ops/check-traffic-window.py (challenge #264).

On 2026-11-13 the day's traffic file held 258 outside requests at 04:07 and 103 at 08:07, starting 06:00:05:
six hours had left it, and nothing in the file said so. These laws pin: a file starting more than an hour
after midnight is SHORT; a complete day ending early is SHORT; a smaller count than an earlier read is SHRANK;
unreadable fields are UNKNOWN, never 'covered'; a normal day is covered.

Run: python3 specs/test_check_traffic_window.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("ctw", os.path.join(ROOT, "ops", "check-traffic-window.py"))
ctw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ctw)


def tf(day, req, first, last, complete):
    return {"date": day, "generated_utc": day + "T08:07:01+00:00", "complete_day": complete,
            "outside": {"requests": req, "distinct_clients": 1, "first_utc": first, "last_utc": last}}


class TrafficWindow(unittest.TestCase):
    def test_1113_0807_file_is_short_and_shrank(self):
        r = ctw.build(tf("2026-11-13", 103, "2026-11-13T06:00:05+00:00", "2026-11-13T07:49:59+00:00", False), previous=258)
        kinds = [f.split(":")[0] for f in r["faults"]]
        self.assertEqual(kinds, ["SHORT", "SHRANK"])
        out = ctw.render(r)
        self.assertIn("00:00-06:00", out)
        self.assertIn("UNKNOWN, not zero", out)
        self.assertIn("never as the whole day's", out)

    def test_1112_complete_day_is_covered(self):
        r = ctw.build(tf("2026-11-12", 1632, "2026-11-12T00:00:03+00:00", "2026-11-12T23:38:47+00:00", True))
        self.assertEqual(r["faults"], [])
        self.assertIn("covered", ctw.render(r))

    def test_complete_day_ending_early_is_short(self):
        r = ctw.build(tf("2026-11-14", 500, "2026-11-14T00:00:03+00:00", "2026-11-14T18:00:00+00:00", True))
        self.assertTrue(r["faults"][0].startswith("SHORT"))
        self.assertIn("18:00:00", r["faults"][0])

    def test_partial_day_ending_early_is_not_a_fault(self):
        r = ctw.build(tf("2026-11-14", 40, "2026-11-14T00:01:00+00:00", "2026-11-14T00:20:00+00:00", False))
        self.assertEqual(r["faults"], [])

    def test_growth_is_not_shrank(self):
        r = ctw.build(tf("2026-11-14", 300, "2026-11-14T00:00:10+00:00", "2026-11-14T08:00:00+00:00", False), previous=258)
        self.assertEqual(r["faults"], [])

    def test_complete_day_with_zero_requests_is_short(self):
        r = ctw.build({"date": "2026-11-14", "complete_day": True, "outside": {"requests": 0}})
        self.assertTrue(r["faults"][0].startswith("SHORT"))

    def test_unreadable_is_unknown_never_covered(self):
        bad = [None, [], {"date": "2026-11-14"},
               {"date": "2026-11-14", "outside": {"requests": "103"}},
               {"date": "2026-11-14", "outside": {"requests": True}},
               {"date": "2026-11-14", "outside": {"requests": 5, "first_utc": None, "last_utc": None}},
               {"date": "2026-11-14", "outside": {"requests": 5, "first_utc": "2026-11-14T01:00:00", "last_utc": "2026-11-14T02:00:00"}},
               tf("2026-11-14", 5, "2026-11-13T23:00:00+00:00", "2026-11-14T02:00:00+00:00", False),
               tf("2026-11-14\n", 5, "2026-11-14T00:00:00+00:00", "2026-11-14T02:00:00+00:00", False)]
        for b in bad:
            with self.assertRaises(ctw.Unknown, msg=repr(b)):
                ctw.build(b)

    def test_z_suffix_accepted(self):
        r = ctw.build(tf("2026-11-14", 5, "2026-11-14T00:10:00Z", "2026-11-14T02:00:00Z", False))
        self.assertEqual(r["faults"], [])


if __name__ == "__main__":
    unittest.main()
