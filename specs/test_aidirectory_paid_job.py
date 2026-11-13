#!/usr/bin/env python3
"""Law: the AI directory names the open paid job where it tells a reader where XNO comes from (challenge #266).

Measured 2026-11-13 16:07 UTC (/ai/traffic): the AI directory drew 71 outside requests from 30 clients since 06:00,
bounties.txt 2 from 1. The owner opened paid work that morning (OWNER-RULES rule 12, job-20261113-001, open until
2026-11-20) and #265 put it in bounties.txt and canon.txt, but every copy of the directory still said only "Nobody
here funds it" before its first paid step and never named the job: the most-read guide told a stranger there was no
way to earn XNO here while one was open. "Nobody here funds it" stays true (the job pays for work, not a gift); the
block now adds the job, in rule 12's words, untested, with the payer and the way in.

Run: python3 specs/test_aidirectory_paid_job.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ["published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html"]
JOB = "job-20261113-001"
DELIVERY = "1 XNO for the delivery, once it passes"
VERDICT = "0.1 XNO for each verdict, pass or fail"
HEAD = "BEFORE STEP 6 - YOUR FIRST XNO."


def flat(s):
    s = re.sub(r"<[^>]+>", " ", s)
    s = s.replace("&quot;", '"').replace("&gt;", ">").replace("&lt;", "<")
    return " ".join(s.split())


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def first_xno_block(s):
    i = s.index(HEAD)
    return s[i:s.index("Spend it on something real", i)]


class PaidJobInDirectory(unittest.TestCase):
    def check(self, rel, b):
        self.assertIn("Nobody here funds it", b, rel)
        self.assertIn(JOB, b, rel)
        self.assertIn(DELIVERY, b, rel)
        self.assertIn(VERDICT, b, rel)
        self.assertIn("untested", b, rel)
        self.assertIn("2026-11-20 23:59 UTC", b, rel)
        self.assertIn("section 9 of https://172-86-112-140.sslip.io/bounties.txt", b, rel)
        rest = b.replace(DELIVERY, "").replace(VERDICT, "")
        self.assertNotRegex(rest, r"\b0\.01 XNO\b", rel)

    def test_every_copy_names_the_job_in_the_first_xno_block(self):
        for rel in COPIES:
            self.check(rel, first_xno_block(flat(read(rel))))

    def test_tools_json_step6(self):
        d = json.loads(read("published/aidirectory/tools.json"))
        six = [x for x in d["onboarding"] if x["n"] == "6"][0]
        self.check("tools.json", six["first_xno"])

    def test_llms_txt_says_it_before_the_onboarding(self):
        for rel in COPIES[:2]:
            s = flat(read(rel))
            i = s.index(JOB)
            self.assertLess(i, s.index("## Why"), rel)

    def test_job_and_deadline_match_bounties_section_9(self):
        b = flat(read("published/bounties.txt"))
        sec = b[b.index(" 9. PAID WORK, OPEN NOW"):]
        self.assertIn("THE JOB (job-20261113-001, open until 2026-11-20 23:59 UTC)", sec)
        self.assertIn(DELIVERY, sec)
        self.assertIn(VERDICT, sec)

    def test_mirrors_stay_byte_identical(self):
        self.assertEqual(read(COPIES[0]), read(COPIES[1]))
        self.assertEqual(read(COPIES[2]), read(COPIES[3]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
