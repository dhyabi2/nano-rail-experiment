#!/usr/bin/env python3
"""Law for the "Updated" stamp at the top of bounties.txt (challenge #164).

Measured 2026-10-26 20:3x UTC: the header said "Updated 2026-10-24" while the body already cited events of 10-25 and
10-26 (the #594/#393 answer, the 1.38 MB asks list, challenge #159's pay-an-answer note), changed by three merges on
10-25 and 10-26. A sceptical reader checks the stamp first and takes the text as two days stale, or takes the newer
lines as made up. The stamp must be no older than the newest date the text itself cites.

Run: python3 specs/test_bounties_updated_stamp.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
YEAR = 2026


def cited_dates(txt):
    """Every date the text cites: 2026-MM-DD, and the short MM-DD form for the experiment's months (09-12).
    A deadline ("until 2026-11-20", "UNTIL 11-20", challenge #265) is a future date, not a citation: skipped."""
    out = {(int(m), int(d)) for m, d in re.findall(r"(?<!until )(?<!UNTIL )\b2026-(\d{2})-(\d{2})\b", txt)}
    for m, d in re.findall(r"(?<![\d:\-])(?<!until )(?<!UNTIL )(09|1[0-2])-([0-3]\d)\b(?!-)", txt):
        if 1 <= int(d) <= 31:
            out.add((int(m), int(d)))
    return out


class UpdatedStamp(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()

    def stamp(self, txt):
        m = re.search(r"Updated (\d{4})-(\d{2})-(\d{2})\.", "\n".join(txt.splitlines()[:6]))
        self.assertIsNotNone(m, "the header must carry 'Updated YYYY-MM-DD.' in its first lines")
        self.assertEqual(int(m.group(1)), YEAR)
        return int(m.group(2)), int(m.group(3))

    def test_stamp_not_older_than_any_cited_date(self):
        stamp = self.stamp(self.txt)
        newest = max(cited_dates(self.txt))
        self.assertGreaterEqual(stamp, newest, "header says Updated %02d-%02d but the text cites %02d-%02d" % (stamp + newest))

    def test_the_law_catches_the_stale_header_it_was_written_for(self):
        stale = self.txt.replace(self.txt.splitlines()[3], " Plain text so you do not have to parse anything. Updated 2026-10-24.", 1)
        self.assertLess(self.stamp(stale), max(cited_dates(stale)))

    def test_times_and_ranges_are_not_read_as_dates(self):
        self.assertEqual(cited_dates("14:29-14:33 UTC, #1-#5, 01-RAI, 10-13 and 2026-09-28"), {(10, 13), (9, 28)})


if __name__ == "__main__":
    unittest.main()
