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


def run_main(argv, traffic_doc=None, asks_doc=None, ask_doc=None, traffic_exc=None):
    """Run cbd.main() with every fetch stubbed (never the live service). Returns (exit code, stderr, fetched urls)."""
    import contextlib, io, sys, types
    fetched = []
    real_abd = cbd._load_abd()

    def fetch_json(url):
        fetched.append(url)
        if traffic_exc is not None:
            raise traffic_exc
        return traffic_doc

    def abd_fetch(url):
        fetched.append(url)
        return asks_doc if url.endswith("/asks") else ask_doc

    fake = types.SimpleNamespace(API="https://stub.invalid/api", fetch=abd_fetch, build_report=real_abd.build_report)
    old = (cbd.fetch_json, cbd._load_abd, sys.argv)
    cbd.fetch_json, cbd._load_abd, sys.argv = fetch_json, (lambda: fake), ["creates-by-day.py"] + argv
    err, out = io.StringIO(), io.StringIO()
    code = 0
    try:
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
            cbd.main()
    except SystemExit as e:
        code = e.code
    finally:
        cbd.fetch_json, cbd._load_abd, sys.argv = old
    return code, err.getvalue(), fetched


GOOD = {"generated_utc": "x", "complete_day": True, "status": {"201": 1}}


class ReviewFindings(unittest.TestCase):
    def test_trailing_newline_and_bad_days_refused_before_any_fetch(self):
        for day in ("2026-11-03\n", "2026-11-0\u0663", "\u0662\u0660\u0662\u0666-11-03", "2026-02-30", "0000-99-99",
                    "2026-13-01", " 2026-11-03"):
            code, err, fetched = run_main([day], traffic_doc=GOOD, asks_doc={"asks": []})
            self.assertEqual(code, 2, repr(day))
            self.assertIn("UNKNOWN", err, repr(day))
            self.assertEqual(fetched, [], repr(day))

    def test_good_day_still_measures(self):
        code, err, fetched = run_main(["2026-11-03"], traffic_doc=GOOD, asks_doc={"asks": []})
        self.assertEqual(code, 0, err)
        self.assertTrue(fetched)

    def test_http_exception_in_fetch_is_unknown_exit_2(self):
        import http.client
        for exc in (http.client.InvalidURL("bad"), http.client.RemoteDisconnected("gone"), http.client.IncompleteRead(b"")):
            code, err, _ = run_main(["2026-11-03"], traffic_exc=exc)
            self.assertEqual(code, 2, repr(exc))
            self.assertIn("UNKNOWN", err)
            self.assertNotIn("Traceback", err)

    def test_recursion_error_in_fetch_is_unknown_exit_2(self):
        code, err, _ = run_main(["2026-11-03"], traffic_exc=RecursionError("deep"))
        self.assertEqual(code, 2)
        self.assertIn("UNKNOWN", err)

    def test_really_deep_json_is_unknown_exit_2(self):
        import json
        deep = "[" * 200000 + "]" * 200000

        def exc():
            try:
                json.loads(deep)
            except RecursionError as e:
                return e
        e = exc()
        if e is None:
            self.skipTest("this json build has no recursion limit")
        code, err, _ = run_main(["2026-11-03"], traffic_exc=e)
        self.assertEqual(code, 2)

    def test_string_counts_are_unknown(self):
        for bad in ("3", "\u0663", "1_0", " 3\n", 3.0, [3]):
            with self.assertRaises(cbd.Unknown, msg=repr(bad)):
                cbd.build("2026-11-06", {"status": {"201": bad}}, report(0, 0))
            with self.assertRaises(cbd.Unknown, msg=repr(bad)):
                cbd.build("2026-11-06", {"status": {"201": 1}}, report(bad, 0))

    def test_real_ints_are_counts(self):
        r = cbd.build("2026-11-06", {"status": {"201": 0}}, report(0, 0))
        self.assertEqual(r["creates_201"], 0)
        with self.assertRaises(cbd.Unknown):
            cbd.build("2026-11-06", {"status": {"201": 1}}, report(False, 0))

    def test_complete_day_must_be_literally_true(self):
        for odd in ("false", "no", 1, "true", [True], None):
            r = cbd.build("2026-11-06", {"complete_day": odd, "status": {"201": 1}}, report(1, 0))
            self.assertFalse(r["complete_day"], repr(odd))
            self.assertIn("(partial day)", cbd.render(r))
        self.assertTrue(cbd.build("2026-11-06", {"complete_day": True, "status": {}}, report(0, 0))["complete_day"])

    def test_odd_asks_shapes_are_unknown_exit_2(self):
        for doc in ([], [{"id": 1}], {"asks": [{"x": 1}]}, {"asks": "abc"}, {"asks": [1]}, {"asks": [{"id": "1/../x"}]},
                    {"asks": [{"id": True}]}, {"asks": None}, "abc", None):
            code, err, _ = run_main(["2026-11-03"], traffic_doc=GOOD, asks_doc=doc, ask_doc={"ask": {}})
            self.assertEqual(code, 2, repr(doc))
            self.assertIn("UNKNOWN", err, repr(doc))

    def test_odd_ask_detail_shapes_are_unknown_exit_2(self):
        for detail in ([], "abc", {"ask": "abc"}, {"ask": {"answers": "abc"}}, {"ask": {"answers": [1]}},
                       {"ask": {"answers": [{"at": 5}]}}):
            code, err, _ = run_main(["2026-11-03"], traffic_doc=GOOD, asks_doc={"asks": [{"id": 1}]}, ask_doc=detail)
            self.assertEqual(code, 2, repr(detail))
            self.assertIn("UNKNOWN", err, repr(detail))

    def test_asks_error_document_is_unknown_not_zero(self):
        # {"error": "rate limited"} has no asks key: a failed read, never "0 asks ... UNEXPLAINED".
        for doc in ({"error": "rate limited"}, {}):
            code, err, _ = run_main(["2026-11-03"], traffic_doc=GOOD, asks_doc=doc, ask_doc={"ask": {}})
            self.assertEqual(code, 2, repr(doc))
            self.assertIn("UNKNOWN", err, repr(doc))
            with self.assertRaises(cbd.Unknown, msg=repr(doc)):
                cbd.ask_ids(doc)

    def test_ask_detail_error_document_is_unknown_not_empty(self):
        for detail in ({"error": "rate limited"}, {}, {"ask": None}):
            code, err, _ = run_main(["2026-11-03"], traffic_doc=GOOD, asks_doc={"asks": [{"id": 1}]}, ask_doc=detail)
            self.assertEqual(code, 2, repr(detail))
            self.assertIn("UNKNOWN", err, repr(detail))

    def test_duplicate_ask_ids_are_unknown(self):
        with self.assertRaises(cbd.Unknown):
            cbd.ask_ids({"asks": [{"id": 1}, {"id": 2}, {"id": 1}]})
        code, err, _ = run_main(["2026-11-03"], traffic_doc=GOOD, asks_doc={"asks": [{"id": 1}, {"id": 1}]},
                                ask_doc={"ask": {}})
        self.assertEqual(code, 2)
        self.assertIn("UNKNOWN", err)

    def test_non_finite_generated_utc_never_reaches_json_output(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            doc = {"generated_utc": bad, "complete_day": True, "status": {"201": 1}}
            code, err, _ = run_main(["--json", "2026-11-03"], traffic_doc=doc, asks_doc={"asks": []})
            self.assertEqual(code, 2, repr(bad))
            self.assertIn("UNKNOWN", err, repr(bad))

    def test_json_output_still_works(self):
        code, err, _ = run_main(["--json", "2026-11-03"], traffic_doc=GOOD, asks_doc={"asks": []})
        self.assertEqual(code, 0, err)


if __name__ == "__main__":
    unittest.main()
