#!/usr/bin/env python3
"""Law for the try-nano note beside the retired onramp in bounties.txt (challenge #120).

Measured 2026-10-10 12:15-12:30 UTC: the 410 at /unstuck/api/v1/onramp/address says "GET /try-nano shows a
no-install python3 way", with no base. Resolved against the URL that answered it, that is
/unstuck/api/v1/try-nano, which answers 404; /try-nano at the origin answers 404 too. Only
https://getunstuck.space/unstuck/api/try-nano answers 200. The site's traffic file for 2026-10-10 (00:00-12:00)
shows /unstuck/api/v1/try-nano' requested by 12 distinct outside clients, all 404. bounties.txt names the retired
URL, so it must also say where its 410's pointer really goes.

Run: python3 specs/test_bounties_retired_410_try_nano.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Retired410TryNano(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index("The old shortcut is gone.")
        self.para = " ".join(txt[i:txt.index("Optional: POST", i)].split())

    def test_quotes_the_relative_pointer_from_the_410(self):
        self.assertIn('"GET /try-nano"', self.para)

    def test_gives_the_full_working_url(self):
        self.assertIn("GET https://getunstuck.space/unstuck/api/try-nano (200", self.para)

    def test_names_both_wrong_readings_as_404(self):
        self.assertIn("not /unstuck/api/v1/try-nano (404)", self.para)
        self.assertIn("not getunstuck.space/try-nano (404)", self.para)


if __name__ == "__main__":
    unittest.main()
