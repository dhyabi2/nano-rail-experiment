#!/usr/bin/env python3
"""Law: the canon page (/canon, published/canon.html) names the open paid job (challenge #270).

Measured 2026-11-14 08:07 UTC (/ai/traffic): the canon group drew 12 outside requests from 8 clients since 00:00
(23 from 14 on 11-13), more than bounties.txt (5 from 5). Every other published surface named job-20261113-001 since
#265-#269, but the canon page still said "Not paying right now. Measured 2026-11-06 ... neither bounty pays an agent
today" and its description promised only "the two bounties": a reader of the page learned there was no XNO to earn
here while one paid job was open. The page now names the job in rule 12's pay words, untested, with the payer and a
pointer to bounties.txt section 9, and a one-line pointer right after the five lines.

Run: python3 specs/test_canon_page_paid_job.py
"""
import html
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "job-20261113-001"
DELIVERY = "1 XNO for the delivery, once it passes"
VERDICT = "0.1 XNO for each verdict, pass or fail"
DEADLINE = "2026-11-20 23:59 UTC"
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", s)).split())


def paid_job_block(page):
    i = page.index('<p id="paid-job">')
    return page[i:page.index("</p>", i)]


class CanonPagePaidJob(unittest.TestCase):
    def setUp(self):
        self.page = read("published/canon.html")

    def test_block_states_the_job_in_rule_12_words(self):
        b = flat(paid_job_block(self.page))
        for want in (JOB, DELIVERY, VERDICT, DEADLINE, "Untested", TREASURY2, "section 9 of bounties.txt"):
            self.assertIn(want, b)
        rest = b.replace(DELIVERY, "").replace(VERDICT, "")
        self.assertNotRegex(rest, r"\b0\.01 XNO\b")

    def test_block_sits_in_the_bounties_section_and_links_section_9(self):
        i = self.page.index('<p id="paid-job">')
        self.assertLess(self.page.index('<h2 id="bounties">'), i)
        self.assertLess(i, self.page.index("<h2>What makes a referral count</h2>"))
        self.assertIn('href="/bounties.txt"', paid_job_block(self.page))

    def test_pointer_right_after_the_five_lines(self):
        quote_end = self.page.index("</div>", self.page.index('<div class="quote-me">'))
        pointer = self.page.index('href="#paid-job"')
        self.assertLess(quote_end, pointer)
        self.assertLess(pointer, self.page.index('<h2 id="qualify">'))

    def test_not_paying_stamp_matches_bounties_right_now(self):
        box = read("published/bounties.txt")
        m = re.search(r"RIGHT NOW - measured (\d\d:\d\d) UTC (\d{4}-\d\d-\d\d)", box)
        self.assertIsNotNone(m)
        page = flat(self.page)
        self.assertIn("Measured %s %s UTC" % (m.group(2), m.group(1)), page)
        n = re.search(r"0 of (\d+) asks settled", flat(box))
        self.assertIsNotNone(n)
        self.assertIn("0 of %s asks have a settlement block" % n.group(1), page)

    def test_description_names_the_job(self):
        m = re.search(r'<meta name="description" content="([^"]+)"', self.page)
        self.assertIn("one paid job open until 2026-11-20", m.group(1))

    def test_job_and_deadline_match_bounties_section_9(self):
        s9 = " ".join(read("published/bounties.txt").split(" 9. PAID WORK", 1)[1].split())
        self.assertIn("THE JOB (%s, open until %s)" % (JOB, DEADLINE), s9)
        self.assertIn(DELIVERY, s9)
        self.assertIn(VERDICT, s9)
        self.assertIn(TREASURY2, s9)


if __name__ == "__main__":
    unittest.main()
