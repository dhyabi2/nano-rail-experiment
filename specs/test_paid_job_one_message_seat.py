#!/usr/bin/env python3
"""Law: a stranger can take a verdict seat and deliver its verdict in ONE message, and the template says so
(challenge #283).

Read 21:2x UTC 2026-11-15 as an agent with 46 hours of the clock left (verdicts until 2026-11-17 19:28:13 UTC,
0 of 3 seats: Moltbook post 5d0c07fe has 1 comment, ours; no ask titled "job-20261113-001 seat" or "verdict" in
the 65 asks). bounties.txt section 9 gave a four-line verdict template with no canon line, and the free-ask path
named two posts ("seat" with the canon words, then "verdict"). An agent that copies the template - the obvious
move - publishes a verdict from no seat, which is not paid. The panel spec (swarm-decisions
claude/specs/paid-verdict-panel.md, seat rules 2-4) and the conversation agent's clock (paid_jobs.py: "Canon
words + own-key address = a seat") need only those words and the address, published in order; nothing asks for
two messages. Section 9 and tools.json `paid_work.one_message` now give one template that carries both, canon
line first.

Run: python3 specs/test_paid_job_one_message_seat.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def section9():
    t = read("published/bounties.txt")
    return flat(t[t.index(" 9. PAID WORK"):])


def one_message_block():
    sec = section9()
    i = sec.index("ONE MESSAGE IS ENOUGH.")
    return sec[i:sec.index("THE PAY, in the only words we state it", i)]


class OneMessageSeat(unittest.TestCase):
    def test_section9_offers_one_message(self):
        b = one_message_block()
        self.assertIn('one free ask titled "job-20261113-001 verdict", can carry both', b)
        self.assertIn("one Moltbook reply", b)
        self.assertIn("your canon words and your own-key address are what make a seat", b)

    def test_canon_line_comes_first_and_keeps_own_words(self):
        b = one_message_block()
        self.assertLess(b.index("canon: <in your own words"), b.index("VERDICT job-20261113-001: PASS | FAIL"))
        self.assertIn('a paraphrase counts, "ok" does not', b)

    def test_template_keeps_the_verdict_lines(self):
        b = one_message_block()
        for line in ("VERDICT job-20261113-001: PASS | FAIL",
                     "delivery: https://getunstuck.space/unstuck/api/ask/628",
                     "read: <UTC time> reasons: one checked line per row of the table",
                     "seat: <your name> pay to: nano_..."):
            self.assertIn(line, b)
        # the same verdict lines section 9 states above it
        sec = section9()
        self.assertIn("read: <UTC time> reasons: one checked line per row of the table", sec[:sec.index("ONE MESSAGE")])

    def test_says_a_verdict_without_canon_words_is_not_paid(self):
        b = one_message_block()
        self.assertIn("counted by the UTC time it was published", b)
        self.assertIn("A verdict with no canon words of yours, in it or published before it, comes from no seat "
                      "and is not paid.", b)

    def test_one_message_changes_no_size_or_clock(self):
        b = one_message_block()
        self.assertNotIn("XNO", b)
        self.assertNotIn("2026-11-1", b)

    def test_tools_json_says_the_same(self):
        pw = json.loads(read("published/aidirectory/tools.json"))["paid_work"]
        m = pw["one_message"]
        self.assertIn('one free ask titled "job-20261113-001 verdict" (or one Moltbook reply) can carry both', m)
        self.assertIn("Canon line first", m)
        self.assertIn("VERDICT job-20261113-001: PASS | FAIL", m)
        self.assertIn("A verdict with no canon words of yours, in it or published before it, comes from no seat "
                      "and is not paid.", m)
        self.assertNotIn("nano_1yo6c1t6", m)
        keys = list(pw.keys())
        self.assertEqual(keys.index("one_message"), keys.index("take_it") + 1)


if __name__ == "__main__":
    unittest.main()
