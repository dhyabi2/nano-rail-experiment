#!/usr/bin/env python3
"""Law for challenge #287: every "read at" stamp on the open paid work is no older than the page's Updated date.

Measured 01:2x UTC 2026-11-16, 42 hours before the verdict clock of job-20261113-001 ends (2026-11-17 19:28:13 UTC):
the page said "Updated 2026-11-15" and its RIGHT NOW box "measured 00:28 UTC 2026-11-15", while section 9 gave the
seat count as of 16:2x UTC 11-15 and the treasury's balance as of 12:1x UTC 11-13 - three days old - under the
heading "CHECK THE MONEY EXISTS BEFORE YOU WORK". llms.txt, edited by #286, already said 00:2x UTC 11-16. So a
stranger deciding whether a seat is still free read three different "now"s, a day apart, on the only work that
pays. Every claim still held when re-run (0 of 3 seats, treasury2 10.99994 XNO, the Moltbook post's one comment),
so the text was right and only looked abandoned. This law keeps the open-work stamps at least as new as the page.

Run: python3 specs/test_seat_reads_not_older_than_page.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def stamps(txt):
    """The page's Updated date and the dates of every 'read at' stamp on the open paid work, as YYYY-MM-DD."""
    head = "\n".join(txt.splitlines()[:8])
    m = re.search(r"Updated (2026-\d\d-\d\d)\.", head)
    updated = m.group(1) if m else None
    sec = flat(txt[txt.index(" 9. PAID WORK"):]) if " 9. PAID WORK" in txt else ""
    found = {}
    pats = {
        "where it stands": r"WHERE IT STANDS NOW \((2026-\d\d-\d\d) ",
        # while the seats were open, the dated count; from the close (challenge #300), the dated close itself
        "seat count": r"(?:0 of 3 seats taken \(|THE VERDICTS CLOSED at )(2026-\d\d-\d\d) ",
        "treasury read": r"which held [\d.]+ XNO at \d\d:\d[\dx] UTC (2026-\d\d-\d\d)",
        "post read": r"THAT POST IS BEHIND THE DELIVERY \(read \d\d:\d[\dx] UTC (2026-\d\d-\d\d)\)",
    }
    for k, p in pats.items():
        m = re.search(p, sec)
        found[k] = m.group(1) if m else None
    return updated, found


class SeatReadsNotOlderThanPage(unittest.TestCase):
    def test_every_open_work_stamp_is_current(self):
        updated, found = stamps(read("published/bounties.txt"))
        self.assertIsNotNone(updated)
        for k, d in found.items():
            self.assertIsNotNone(d, "section 9 lost its %s stamp" % k)
            self.assertGreaterEqual(d, updated, "page updated %s but section 9's %s is %s: re-read it" % (updated, k, d))

    def test_llms_and_tools_carry_the_same_seat_day(self):
        _, found = stamps(read("published/bounties.txt"))
        day = found["seat count"]
        if "THE VERDICTS CLOSED at " in flat(read("published/bounties.txt")):
            # challenge #300: no live count is left; llms.txt and tools.json name the same close day and count
            for rel in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
                t = flat(read(rel))
                self.assertIn("closed at %s 19:28:13 UTC with 0 verdicts" % day, t, rel)
            now = json.loads(read("published/aidirectory/tools.json"))["paid_work"]["now"]
            self.assertIn("CLOSED at %s 19:28:13 UTC" % day, now)
            return
        for rel in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
            m = re.search(r"0 of 3 taken \(\d\d:\d[\dx] UTC (2026-\d\d-\d\d)\)", read(rel))
            self.assertIsNotNone(m, rel)
            self.assertEqual(m.group(1), day, rel)
        now = json.loads(read("published/aidirectory/tools.json"))["paid_work"]["now"]
        self.assertIn("0 of 3 taken (%s " % day, now)

    def test_law_fails_on_the_old_shape(self):
        old = ("x\n Plain text so you do not have to parse anything. Updated 2026-11-15.\n"
               " 9. PAID WORK, OPEN NOW\n WHERE IT STANDS NOW (2026-11-15 00:2x UTC). 0 of 3 seats taken\n"
               " (2026-11-15 16:2x UTC). which held 10.99994 XNO at 12:1x UTC 2026-11-13 (rpc.nano.to).\n"
               " THAT POST IS BEHIND THE DELIVERY (read 16:2x UTC 2026-11-15): x\n")
        updated, found = stamps(old)
        self.assertEqual(found["treasury read"], "2026-11-13")
        self.assertLess(found["treasury read"], updated)


if __name__ == "__main__":
    unittest.main()
