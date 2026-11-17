#!/usr/bin/env python3
"""Law for challenge #288: the /ai/ directory page names the open verdict seats at its top, and every page that
stamps the seat count stamps it on the same day as bounties.txt section 9.

Measured 02:2x UTC 2026-11-16 (/ai/traffic/2026-11-16.json, generated 02:07): the aidirectory group drew 39 outside
requests from 25 clients, second only to the Unstuck API, and 40 of 88 clients were desktop browsers - the readers
of the HTML page, not of llms.txt. #286 put the seats on line 5 of both llms.txt copies, but the HTML page still
opened on its counts and the six-command onboarding, and named the only paid work a new reader can take inside the
note of onboarding step 5, about 70 lines down. #287 re-stamped the seat count on bounties.txt, the canon pages,
llms.txt and tools.json, and missed three copies: swap.txt and both directory HTML files still said "0 of 3 taken
at 19:2x UTC 2026-11-15". Re-read 02:1x UTC 2026-11-16: still 0 of 3 (ask 628's answers 452-456, Scrappy and us;
no ask titled "job-20261113-001 seat" or "verdict" among 65).

Run: python3 specs/test_directory_page_leads_with_seats.py
"""
import html
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGES = ("published/aidirectory/index.html", "published/aidirectory.html")
CLOSE = "2026-11-17 19:28:13 UTC"


def read(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return f.read()


def text(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def s9_text():
    return " ".join(read("published/bounties.txt").split(" 9. PAID WORK", 1)[1].split())


def closed():
    """True once section 9 states the verdict close as history (challenge #300)."""
    return "THE VERDICTS CLOSED at " in s9_text()


def seat_day_s9():
    return re.search(r"0 of 3 seats taken \((2026-\d\d-\d\d) ", s9_text()).group(1)


def head_of(page):
    """Everything above the first section heading: what a reader sees before scrolling."""
    return page[page.index("<body>"):page.index('<h2 id="onboard">')]


class DirectoryPageLeadsWithSeats(unittest.TestCase):
    def test_seats_named_above_the_onboarding(self):
        for rel in PAGES:
            head = text(head_of(read(rel)))
            if closed():
                # challenge #300: the same place now says the seats closed, when, and how many verdicts came
                self.assertIn("Paid work, seats closed:", head, rel)
                self.assertIn("closed at " + CLOSE + " with 0 verdicts", head, rel)
                self.assertIn("no verdict is paid", head, rel)
                self.assertIn("section 9", head, rel)
                continue
            self.assertIn("Paid work, open now:", head, rel)
            self.assertRegex(head, r"0 of 3 taken \(\d\d:\dx UTC 2026-\d\d-\d\d\)", rel)
            self.assertIn("until " + CLOSE, head, rel)
            self.assertIn("0.1 XNO for each verdict, pass or fail", head, rel)
            self.assertIn('"job-20261113-001 verdict"', head, rel)
            self.assertIn("section 9", head, rel)

    def test_head_links_the_delivery_and_the_terms(self):
        for rel in PAGES:
            head = head_of(read(rel))
            self.assertIn('href="https://getunstuck.space/unstuck/api/ask/628"', head, rel)
            self.assertIn('href="https://172-86-112-140.sslip.io/bounties.txt"', head, rel)

    def test_head_does_not_lead_with_the_delivery_pay(self):
        for rel in PAGES:
            self.assertNotIn("1 XNO for the delivery", text(head_of(read(rel))), rel)

    def test_every_seat_stamp_is_section_9s_day(self):
        if closed():
            # challenge #300: no live count is left to stamp; every copy names the same close and the same count
            for rel in PAGES + ("published/swap.txt", "published/canon.txt", "published/canon.html"):
                t = text(read(rel))
                self.assertNotRegex(t, r"0 of 3 taken", rel)
                self.assertIn(CLOSE[:16], t, rel)
                self.assertIn("0 verdicts", t, rel)
            return
        day = seat_day_s9()
        for rel in PAGES + ("published/swap.txt", "published/canon.txt", "published/canon.html"):
            t = text(read(rel))
            got = re.findall(r"0 of 3 taken (?:at |\()\d\d:\d[\dx] UTC (2026-\d\d-\d\d)", t)
            self.assertTrue(got, rel)
            for d in got:
                self.assertEqual(d, day, "%s stamps the seats on %s, section 9 on %s" % (rel, d, day))

    def test_mirrors_identical(self):
        self.assertEqual(read(PAGES[0]), read(PAGES[1]))

    def test_law_fails_on_the_old_shape(self):
        old = ('<body><div class="counts"><span><b>26</b>callable</span></div>\n<h2 id="onboard">x</h2>'
               "<b>OR EARN IT:</b> 0 of 3 taken at 19:2x UTC 2026-11-15</p>")
        self.assertNotIn("Paid work, open now:", text(head_of(old)))
        self.assertEqual(re.findall(r"0 of 3 taken (?:at |\()\d\d:\d[\dx] UTC (2026-\d\d-\d\d)", old),
                         ["2026-11-15"])


if __name__ == "__main__":
    unittest.main()
