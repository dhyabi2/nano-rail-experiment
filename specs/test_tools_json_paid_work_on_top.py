#!/usr/bin/env python3
"""Law: tools.json names the open paid job in a top-level key, before its long lists (challenge #268).

Measured 2026-11-13 (/ai/traffic/2026-11-13.json, 06:00-24:00 UTC): /ai/tools.json was the most-read published
file by distinct clients (14, beside bounties.txt's 15), and the AI directory drew 269 outside requests from 51
clients. The only XNO an outside agent can earn here (job-20261113-001, OWNER-RULES rule 12) sat in tools.json at
onboarding[5].first_xno, about 1,600 lines down, after 13 KB of callable_now and 30 KB of catalogue; its top-level
keys named no job, and "updated" still read 2026-11-09 though #266 and #267 had changed the file on 11-13. A program
that reads the top keys of the JSON never met the paid work. The job, its pay words, the payer, a free way to
check the payer and a way to take it without any account now sit in "paid_work", right after "updated".

Run: python3 specs/test_tools_json_paid_work_on_top.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class PaidWorkOnTop(unittest.TestCase):
    def setUp(self):
        self.d = json.loads(read("published/aidirectory/tools.json"))
        self.p = self.d["paid_work"]
        b = flat(read("published/bounties.txt"))
        self.sec9 = b[b.index(" 9. PAID WORK, OPEN NOW"):]

    def test_paid_work_comes_before_the_long_lists(self):
        keys = list(self.d)
        i = keys.index("paid_work")
        for later in ("path", "callable_now", "catalogue", "onboarding"):
            self.assertLess(i, keys.index(later), later)
        self.assertLessEqual(i, 3, keys)

    def test_job_deadline_and_pay_match_bounties_section_9(self):
        self.assertIn("THE JOB (%s, open until %s)" % (self.p["job"], self.p["open_until"]), self.sec9)
        for sentence in self.p["pay"].split(". "):
            self.assertIn(sentence.rstrip("."), self.sec9)
        self.assertIn("Untested", self.sec9)
        self.assertTrue(self.p["status"].startswith("untested"))

    def test_deliver_says_what_section_9_says(self):
        for part in ("at least three agent job or escrow venues", "stays silent past the deadline",
                     "who that default favours", "a public link where that rule can be read"):
            self.assertIn(part, self.p["deliver"])
            self.assertIn(part, self.sec9)

    def test_payer_is_treasury2_and_the_check_reads_it(self):
        self.assertEqual(self.p["payer"], TREASURY2)
        self.assertIn(TREASURY2, self.sec9)
        cmd = self.p["check_payer"]
        self.assertIn("https://rpc.nano.to", cmd)
        body = re.search(r"--data-binary '([^']+)'", cmd).group(1)
        self.assertEqual(json.loads(body), {"action": "account_info", "account": TREASURY2})

    def test_way_in_needs_no_account_and_matches_section_9(self):
        t = self.p["take_it"]
        self.assertIn("POST https://getunstuck.space/unstuck/api/ask", t)
        self.assertIn("https://getunstuck.space/unstuck/api/ask ", self.sec9)
        for title in ("job-20261113-001 delivery", "job-20261113-001 seat", "job-20261113-001 verdict"):
            self.assertIn(title, t)
            self.assertIn(title, self.sec9)
        self.assertIn("5d0c07fe-9ad3-4bd2-8a93-7227dcdd0a5d", t)
        self.assertIn("5d0c07fe-9ad3-4bd2-8a93-7227dcdd0a5d", self.sec9)
        self.assertIn("section 9 of https://172-86-112-140.sslip.io/bounties.txt", self.p["terms"])

    def test_no_other_size_is_stated(self):
        rest = json.dumps(self.p).replace("1 XNO for the delivery", "").replace("0.1 XNO for each verdict", "")
        self.assertNotRegex(rest, r"\b\d+(\.\d+)? XNO\b")

    def test_updated_is_not_older_than_the_job(self):
        self.assertGreaterEqual(self.d["updated"], "2026-11-13")


if __name__ == "__main__":
    unittest.main()
