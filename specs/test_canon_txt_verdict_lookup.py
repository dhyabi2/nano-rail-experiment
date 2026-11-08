#!/usr/bin/env python3
"""Law for canon.txt's verdict lookup (challenge #238).

canon.txt told a confirmer its verdict is "published in bounties.txt's GATE LOG", a 1631-line file with no way to
find one entry in it. It now gives a one-line command that prints only the entry for one ask id, or NOT JUDGED YET.
This runs that exact command's Python against the local bounties.txt (no network): it must print #626's entry and
nothing past it, print #578's, and say NOT JUDGED YET for an id the log does not carry. It also pins the stamp's
count of asks so the 11-06 "0 of 63" does not come back.

Run: python3 specs/test_canon_txt_verdict_lookup.py
"""
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


class CanonVerdictLookup(unittest.TestCase):
    def setUp(self):
        self.txt = read("published/canon.txt")
        m = re.search(r"curl -s (https://\S+/bounties\.txt) \| python3 -c \"(.+?)\" (\d+)\n", self.txt)
        self.assertIsNotNone(m, "canon.txt lost its one-line verdict lookup")
        self.url, self.code, self.example = m.group(1), m.group(2), m.group(3)

    def run_lookup(self, ask_id):
        # The shell keeps backslashes inside double quotes, so the code reaches Python as written in the file.
        return subprocess.run([sys.executable, "-c", self.code, ask_id], input=read("published/bounties.txt"),
                              capture_output=True, text=True, check=True).stdout

    def test_reads_the_live_bounties_file(self):
        self.assertEqual(self.url, "https://172-86-112-140.sslip.io/bounties.txt")
        self.assertIn("GATE LOG", read("published/bounties.txt"))

    def test_example_id_prints_its_entry_only(self):
        out = self.run_lookup(self.example)
        self.assertTrue(out.startswith("   #%s  posted" % self.example), out[:80])
        self.assertIn("PASSED", out)
        self.assertNotIn("\n   #", out.rstrip("\n").split("\n", 1)[1] if "\n" in out else "")

    def test_an_older_entry_is_found(self):
        self.assertIn("PASSED", self.run_lookup("578"))

    def test_unknown_id_says_not_judged(self):
        self.assertTrue(self.run_lookup("99999").startswith("NOT JUDGED YET"))

    def test_stamp_counts_asks_now(self):
        self.assertNotIn("0 of 63 asks", self.txt)
        self.assertRegex(self.txt, r"Measured 2026-11-08 [0-9x:]+ UTC: no reward sent since 2026-10-13, 0 of 64 asks")


if __name__ == "__main__":
    unittest.main()
