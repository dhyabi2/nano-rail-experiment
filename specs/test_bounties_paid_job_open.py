#!/usr/bin/env python3
"""Laws for the open paid job in bounties.txt and canon.txt (challenge #265).

On 2026-11-13 the owner approved paid work from treasury2 (OWNER-RULES rule 12: "1 XNO for the delivery, once it
passes" and "0.1 XNO for each verdict, pass or fail") and put 10 XNO on treasury2 (receive 437CBC88, 09:42Z). Job
job-20261113-001 was open. Every published guide still told a stranger the opposite: bounties.txt's RIGHT NOW box
said "AN ANSWER EARNS NO XNO TODAY ... Plan on none" and nothing else, canon.txt "agreeing or answering earns no XNO
today". A sceptical earning agent reading either left with "nothing here pays". These laws keep the one paid offer
in the box, worded only as rule 12 words its sizes, with its untested status, the payer to check, and a way in.

Run: python3 specs/test_bounties_paid_job_open.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"
DELIVERY = "1 XNO for the delivery, once it passes"
VERDICT = "0.1 XNO for each verdict, pass or fail"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(t):
    return " ".join(t.split())


class PaidJobOpen(unittest.TestCase):
    def setUp(self):
        self.txt = read("published/bounties.txt")
        i = self.txt.index(" RIGHT NOW - measured ")
        self.box = flat(self.txt[i:self.txt.index(" 1. THE REWARDS")])
        self.sec = flat(self.txt[self.txt.index(" 9. PAID WORK, OPEN NOW"):])

    def test_box_leads_with_the_paid_job(self):
        self.assertIn("PAID WORK, OPEN UNTIL 11-20: job-20261113-001", self.box)
        self.assertLess(self.box.index("PAID WORK"), self.box.index("WORKS, FREE"))
        self.assertIn("section 9", self.box)

    def test_sizes_only_in_rule_12_words(self):
        for t in (self.box, self.sec, flat(read("published/canon.txt"))):
            self.assertIn(DELIVERY, t)
            self.assertIn(VERDICT, t)
        # no other size is attached to the job anywhere in section 9
        rest = self.sec.replace(DELIVERY, "").replace(VERDICT, "")
        self.assertNotRegex(rest, r"\b0\.01 XNO\b")
        self.assertNotRegex(rest, r"\b(?:2|5|10) XNO for\b")

    def test_says_untested_and_names_payer_to_check(self):
        for t in (self.box, self.sec):
            self.assertIn("Untested", t)
        self.assertIn(TREASURY2, self.sec)
        self.assertIn("CHECK THE MONEY EXISTS BEFORE YOU WORK", self.sec)
        self.assertIn("STEP 3 - READ ANY ACCOUNT", self.txt)

    def test_has_a_way_in_and_the_seat_condition(self):
        self.assertIn("https://www.moltbook.com/post/5d0c07fe-9ad3-4bd2-8a93-7227dcdd0a5d", self.sec)
        self.assertIn("nano_ address made from your own key", self.sec)
        self.assertIn("independent on the job, not on the rail", self.sec)
        self.assertRegex(self.sec, r"open until 2026-11-20 23:59 UTC")

    def test_payout_is_not_counted_as_a_sale(self):
        self.assertIn("it is not a sale", self.sec)

    def test_answers_still_earn_nothing(self):
        # the paid job must not blur the truth about asks
        self.assertIn("AN ANSWER EARNS NO XNO TODAY", self.box)
        self.assertIn("agreeing or answering earns no XNO today", flat(read("published/canon.txt")))

    def test_canon_points_at_section_9(self):
        self.assertIn("bounties.txt section 9", flat(read("published/canon.txt")))

    def test_law_fails_on_the_old_box(self):
        old = " RIGHT NOW - measured 04:20 UTC 2026-11-12. WORKS, FREE (no XNO): AN ANSWER EARNS NO XNO TODAY"
        self.assertNotIn("PAID WORK", old)
        self.assertIsNone(re.search(re.escape(DELIVERY), old))


if __name__ == "__main__":
    unittest.main()
