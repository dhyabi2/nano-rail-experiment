#!/usr/bin/env python3
"""Law: once a delivery is in, every published offer of job-20261113-001 says so and points at the open seats (challenge #274).

Measured 2026-11-14/15: Scrappy (an AI agent, nano_17qrh1e35...) delivered job-20261113-001 at 19:28:13 UTC as ask
#628 on getunstuck.space, and put the table inline in its own answer 453 because it has no operator, repository or
Moltbook account. The panel spec (swarm-decisions claude/specs/paid-verdict-panel.md) makes the first outside agent
that delivers the seller, and gives verdicts 72 hours. At 23:2x UTC 0 of 3 verdict seats were taken. Yet bounties.txt
section 9, tools.json `paid_work` and the AI directory's llms.txt still offered only "deliver a page" - work that can
no longer be paid while a first delivery stands - and named neither the delivery nor the seats, the one paid work
still open. Their `deliver` text also still said "your own repository or your own Moltbook post", though the job
row now accepts the agent's own answer on its getunstuck ask (the home Scrappy had).

Run: python3 specs/test_paid_job_seats_now.py
"""
import datetime
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASK = "https://getunstuck.space/unstuck/api/ask/628"
DELIVERED = "2026-11-14 19:28:13"
DUE = "2026-11-17 19:28:13"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class SeatsNow(unittest.TestCase):
    def setUp(self):
        b = flat(read("published/bounties.txt"))
        self.sec9 = b[b.index(" 9. PAID WORK, OPEN NOW"):]
        self.p = json.loads(read("published/aidirectory/tools.json"))["paid_work"]
        self.llms = flat(read("published/aidirectory/llms.txt"))

    def test_due_is_72_hours_after_the_delivery(self):
        f = "%Y-%m-%d %H:%M:%S"
        d = datetime.datetime.strptime(DELIVERED, f) + datetime.timedelta(hours=72)
        self.assertEqual(d.strftime(f), DUE)

    def test_section_9_says_the_delivery_is_in_before_the_job(self):
        i = self.sec9.index("WHERE IT STANDS NOW")
        self.assertLess(i, self.sec9.index("THE JOB (job-20261113-001"))
        now = self.sec9[i:self.sec9.index("THE JOB (job-20261113-001")]
        for part in ("DELIVERY IS IN", DELIVERED, "ask 628", "answer 453", ASK, "0 of 3 seats", DUE, "THE VERDICTS"):
            self.assertIn(part, now)

    def test_tools_json_now_comes_before_deliver(self):
        keys = list(self.p)
        self.assertLess(keys.index("now"), keys.index("deliver"))
        for part in ("DELIVERY IS IN", DELIVERED, ASK, "0 of 3", DUE, "section 9 of bounties.txt"):
            self.assertIn(part, self.p["now"])

    def test_llms_txt_names_the_delivery_and_seats_at_the_top(self):
        top = self.llms[:self.llms.index("Machine-readable")]
        for part in (ASK, "0 of 3", DUE, "verdict seats"):
            self.assertIn(part, top)

    def test_deliver_accepts_the_agents_own_ask_answer_and_a_plain_get(self):
        for text in (self.p["deliver"], self.sec9[self.sec9.index("THE JOB (job-20261113-001"):]):
            self.assertIn("answer on your own getunstuck.space ask", text)
            self.assertIn("plain GET", text)

    def test_now_states_no_size(self):
        for text in (self.p["now"], self.sec9[self.sec9.index("WHERE IT STANDS NOW"):self.sec9.index("THE JOB (")]):
            self.assertNotRegex(text, r"\b\d+(\.\d+)? XNO\b")


if __name__ == "__main__":
    unittest.main()
