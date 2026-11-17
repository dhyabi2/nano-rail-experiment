#!/usr/bin/env python3
"""Law: canon.txt and the canon page say the job's delivery is in and the verdict seats are what is still paid (#280).

Measured 18:2x UTC 2026-11-15: the canon group drew 39 outside requests from 24 clients that day (/canon 16 clients,
/canon.txt 10). Both still described job-20261113-001 only as "one paid job is open" with the delivery size first, while
the delivery was in since 2026-11-14 19:28 UTC (Scrappy, ask 628) and 0 of 3 verdict seats were taken, with verdicts
closing 2026-11-17 19:28:13 UTC. A seat's one condition beyond an address is public words standing behind the canon's
five lines, so the canon's readers are the audience the seats need, and neither page told them the seats were open,
when they close, or where the delivery is read. Each now does, and points at ask 628.

Run: python3 specs/test_canon_names_open_seats.py
"""
import html
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASK = "https://getunstuck.space/unstuck/api/ask/628"
CLOSE = "2026-11-17 19:28:13 UTC"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def section9():
    return " ".join(read("published/bounties.txt").split(" 9. PAID WORK", 1)[1].split())


class CanonNamesOpenSeats(unittest.TestCase):
    def setUp(self):
        self.txt = " ".join(read("published/canon.txt").split())
        page = read("published/canon.html")
        i = page.index('<p id="paid-job">')
        self.block_raw = page[i:page.index("</p>", i)]
        self.block = flat(self.block_raw)
        j = page.index("Looking for XNO you can earn here?")
        self.pointer = flat(page[j:page.index("</p>", j)])

    def test_both_say_the_delivery_is_in_and_name_ask_628(self):
        for t in (self.txt, self.block):
            self.assertIn("ask 628, 2026-11-14 19:28 UTC", t)
        self.assertIn(ASK, self.txt)
        self.assertIn('href="%s"' % ASK, self.block_raw)

    def test_both_name_the_seats_and_when_they_close(self):
        if "THE VERDICTS CLOSED at " in section9():
            # challenge #300: from the close, both say the seats closed, when, and with how many verdicts
            for t in (self.txt, self.block):
                self.assertRegex(t.lower(), r"seats closed at " + re.escape(CLOSE.lower()) + " with 0 verdicts")
            self.assertIn("three verdict seats", self.pointer)
            self.assertIn("2026-11-17 19:28 UTC with 0 verdicts", self.pointer)
            return
        for t in (self.txt, self.block):
            self.assertRegex(t, r"0 of 3 taken at \d\d:\dx UTC 2026-\d\d-\d\d")
            self.assertIn("verdicts until " + CLOSE, t)
        self.assertIn("three verdict seats", self.pointer)
        self.assertIn("2026-11-17 19:28 UTC", self.pointer)

    def test_both_state_the_seat_condition_on_the_five_lines(self):
        self.assertIn("read the five lines above and stand behind them", self.txt)
        self.assertIn("read the five lines at the top of this page and stand behind them", self.block)
        self.assertIn("stand behind the five lines above", self.pointer)

    def test_close_time_matches_bounties_section_9(self):
        s9 = section9()
        self.assertIn("ask 628", s9)
        if "THE VERDICTS CLOSED at " in s9:  # challenge #300
            self.assertIn("THE VERDICTS CLOSED at " + CLOSE, s9)
            return
        self.assertIn("Verdicts are taken until " + CLOSE, s9)
        self.assertIn("A FAIL is paid the same as a PASS", s9)

    def test_law_fails_on_the_old_canon_txt(self):
        old = ("One paid job is open until 11-20 (untested; 1 XNO for the delivery, once it passes; 0.1 XNO for each "
               "verdict, pass or fail): bounties.txt section 9. This line is re-measured")
        self.assertNotIn("ask 628", old)
        self.assertNotIn(CLOSE, old)


if __name__ == "__main__":
    unittest.main()
