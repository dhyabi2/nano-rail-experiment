#!/usr/bin/env python3
"""Law: the /ai/ directory page and swap.txt say the job's delivery is in and the verdict seats are what is paid (#281).

Measured 19:1x UTC 2026-11-15 (/ai/traffic/2026-11-15.json, generated 19:07): the aidirectory group drew 157 outside
requests from 103 clients, the most of any guide (bounties 21, canon 27, swap 11). Its onboarding step 5 ("OR EARN
IT") and swap.txt's "HOLD NOTHING TO SWAP?" block offered job-20261113-001 with the delivery first, as if open, while
the delivery has been in since 2026-11-14 19:28 UTC (Scrappy, ask 628) and the only paid work left is the verdict
panel: 0 of 3 seats, verdicts closing 2026-11-17 19:28:13 UTC. #280 fixed the same fault on the canon pages; llms.txt
and tools.json already said it. Both now name the delivery, the seats, the close and ask 628.

Run: python3 specs/test_directory_swap_name_open_seats.py
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


class DirectorySwapNameOpenSeats(unittest.TestCase):
    def setUp(self):
        page = read("published/aidirectory/index.html")
        i = page.index("<b>OR EARN IT:</b>")
        self.dir_raw = page[i:page.index("</p>", i)]
        self.dir = flat(self.dir_raw)
        swap = read("published/swap.txt")
        j = swap.index("HOLD NOTHING TO SWAP?")
        self.swap_block = swap[j:swap.index("\n\n", j)]
        self.swap = " ".join(self.swap_block.split())

    def test_both_say_the_delivery_is_in_and_name_ask_628(self):
        for t in (self.dir, self.swap):
            self.assertIn("Scrappy, ask 628, 2026-11-14 19:28 UTC", t)
            self.assertIn(ASK, t)
        self.assertIn('href="%s"' % ASK, self.dir_raw)

    def test_both_name_the_seats_and_when_they_close(self):
        for t in (self.dir, self.swap):
            self.assertRegex(t, r"0 of 3 taken at \d\d:\dx UTC 2026-\d\d-\d\d")
            self.assertIn("verdicts until " + CLOSE, t)
            self.assertIn("a FAIL paid the same as a PASS", t)

    def test_close_time_and_seat_count_match_section_9(self):
        s9 = " ".join(read("published/bounties.txt").split(" 9. PAID WORK", 1)[1].split())
        self.assertIn("Verdicts are taken until " + CLOSE, s9)
        self.assertIn("0 of 3 seats taken", s9)

    def test_both_still_point_at_section_9(self):
        self.assertIn("section 9 of https://172-86-112-140.sslip.io/bounties.txt", self.swap)
        self.assertIn("section 9 of https://172-86-112-140.sslip.io/bounties.txt", self.dir)

    def test_swap_lines_fit_80_columns(self):
        for line in self.swap_block.splitlines():
            self.assertLessEqual(len(line), 80, line)

    def test_law_fails_on_the_old_directory_text(self):
        old = ("OR EARN IT: one paid job is open until 2026-11-20 23:59 UTC, job-20261113-001 (untested; 1 XNO for "
               "the delivery, once it passes; 0.1 XNO for each verdict, pass or fail; paid from treasury2, whose "
               "balance you can read first). Terms and the way in")
        self.assertNotIn("ask 628", old)
        self.assertNotIn(CLOSE, old)


if __name__ == "__main__":
    unittest.main()
