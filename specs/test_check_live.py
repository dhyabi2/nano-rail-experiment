#!/usr/bin/env python3
"""Laws for ops/check-live.py (challenge #162).

A file is live only when the live bytes equal main's; a file that could not be fetched is UNKNOWN and never live; a
deploy-status CONFLICT or an unreadable deploy-status keeps the run from passing; every mapped file exists on main;
and the 10-26 outage replays as all UNKNOWN.

Run: python3 specs/test_check_live.py
"""
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("cl", os.path.join(ROOT, "ops", "check-live.py"))
cl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cl)

MAIN = {p: ("main copy of %s\nline two\n" % p).encode() for p in cl.LIVE}
URL_TO_FILE = {u: p for p, u in cl.LIVE.items()}
DEPLOY_OK = json.dumps({"main_commit": "8835790", "checked_utc": "2026-10-26T12:15:03Z", "conflicts": [],
                        "deployed": [], "errors": []}).encode()


def read(path):
    return MAIN[path]


def site(overrides=None, deploy=DEPLOY_OK):
    overrides = overrides or {}

    def get(url):
        if url == cl.DEPLOY_STATUS:
            return (200, deploy) if deploy is not None else (0, b"reset")
        path = URL_TO_FILE[url]
        return overrides.get(path, (200, MAIN[path]))
    return get


class CheckLive(unittest.TestCase):
    def test_all_identical_passes(self):
        r = cl.run(read=read, get=site())
        self.assertTrue(r["ok"])
        self.assertEqual({f["verdict"] for f in r["files"]}, {"live"})

    def test_one_byte_off_is_not_live(self):
        p = "published/bounties.txt"
        r = cl.run(read=read, get=site({p: (200, MAIN[p].replace(b"two", b"2"))}))
        self.assertFalse(r["ok"])
        row = next(f for f in r["files"] if f["file"] == p)
        self.assertEqual(row["verdict"], "differs")
        self.assertIn("first differing line 2", row["why"])

    def test_unreachable_is_unknown_never_live(self):
        p = "published/canon.html"
        r = cl.run(read=read, get=site({p: (502, b"")}))
        self.assertFalse(r["ok"])
        row = next(f for f in r["files"] if f["file"] == p)
        self.assertEqual(row["verdict"], "UNKNOWN")
        self.assertIn("502", row["why"])

    def test_outage_of_10_26_is_all_unknown(self):
        def down(url):  # what every URL did at 12:24 UTC 10-26
            return 0, b"timeout"
        r = cl.run(read=read, get=down)
        self.assertFalse(r["ok"])
        self.assertEqual({f["verdict"] for f in r["files"]}, {"UNKNOWN"})
        self.assertEqual(r["deploy"]["verdict"], "UNKNOWN")

    def test_deploy_conflict_fails_even_when_files_match(self):
        conflict = json.dumps({"main_commit": "d919e71", "conflicts": ["published/bounties.txt"],
                               "deployed": [], "errors": []}).encode()
        r = cl.run(read=read, get=site(deploy=conflict))
        self.assertFalse(r["ok"])
        self.assertEqual(r["deploy"]["verdict"], "CONFLICT")
        self.assertEqual(r["deploy"]["conflicts"], ["published/bounties.txt"])

    def test_unreadable_deploy_status_fails(self):
        self.assertFalse(cl.run(read=read, get=site(deploy=None))["ok"])
        self.assertEqual(cl.run(read=read, get=site(deploy=b"<html>"))["deploy"]["verdict"], "UNKNOWN")

    def test_subset_and_unknown_path(self):
        r = cl.run(["published/swap.txt"], read=read, get=site())
        self.assertEqual([f["file"] for f in r["files"]], ["published/swap.txt"])
        with self.assertRaises(SystemExit):
            cl.run(["published/nope.txt"], read=read, get=site())

    def test_every_mapped_file_exists_on_main(self):
        for p in cl.LIVE:
            self.assertTrue(os.path.isfile(os.path.join(ROOT, p)), p)


if __name__ == "__main__":
    unittest.main()
