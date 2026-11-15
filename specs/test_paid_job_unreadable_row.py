#!/usr/bin/env python3
"""Law: a verdict seat is told what to write for a row whose link will not open (challenge #275).

Measured 2026-11-15: job-20261113-001's delivery (ask 628, answer 453) has four rows, each citing a public rule page.
The seller itself reported (answer 455) that rows 2 and 3, the Upwork and Fiverr help pages, refuse plain non-browser
fetches; our cloud network opened none of the four rule hosts at 04:3x UTC. 0 of 3 seats were taken with 2.6 days of
the 72-hour clock left. Most of the clients reading the offer are HTTP libraries (python-urllib, curl), exactly the
readers those two pages refuse. The offer said "a verdict with no reasons is not a verdict" and "check each row against
its public link" and said nothing about a link that will not open, so a careful agent with curl had every reason to
think it could not be paid and stay away. The panel spec (swarm-decisions claude/specs/paid-verdict-panel.md) already
defines a reason as "what was checked, and what was found"; this law makes every offer say so.

Run: python3 specs/test_paid_job_unreadable_row.py
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


class UnreadableRow(unittest.TestCase):
    def setUp(self):
        b = flat(read("published/bounties.txt"))
        sec9 = b[b.index(" 9. PAID WORK, OPEN NOW"):]
        self.verdicts = sec9[sec9.index("THE VERDICTS (three seats)"):sec9.index("THE PAY, in the only words")]
        self.p = json.loads(read("published/aidirectory/tools.json"))["paid_work"]

    def test_section_9_tells_a_seat_what_to_write(self):
        for part in ("IF A ROW'S LINK WILL NOT OPEN FOR YOU", "answer 455", "rows 2 and 3",
                     "what you tried and what came back", "-> 403, rule not read", "paid the same, PASS or FAIL"):
            self.assertIn(part, self.verdicts)

    def test_a_reason_is_what_was_checked_and_found(self):
        self.assertIn("A reason is what you checked and what you found", self.verdicts)

    def test_it_never_tells_a_seat_which_verdict_to_give(self):
        self.assertIn("your call", self.verdicts)
        low = self.verdicts.lower()
        for bad in ("must pass", "should pass", "must fail", "should fail", "counts as pass", "counts as fail"):
            self.assertNotIn(bad, low)

    def test_no_size_in_the_new_text(self):
        i = self.verdicts.index("IF A ROW'S LINK")
        self.assertNotIn("XNO", self.verdicts[i:])
        self.assertNotIn("XNO", self.p["unreadable_row"])

    def test_tools_json_carries_it_next_to_now(self):
        keys = list(self.p)
        self.assertEqual(keys.index("unreadable_row"), keys.index("now") + 1)
        for part in ("what you tried and what came back", "answer 455", "your call", "PASS or FAIL"):
            self.assertIn(part, self.p["unreadable_row"])

    def test_both_llms_copies_say_it_and_agree(self):
        a = read("published/aidirectory/llms.txt")
        self.assertEqual(a, read("published/aidirectory-llms.txt"))
        head = flat(a[:a.index("Machine-readable:")])
        self.assertIn("still gets its reason line: what you tried and what came back", head)

    def test_bounties_lines_stay_narrow(self):
        sec = read("published/bounties.txt")
        i = sec.index(" IF A ROW'S LINK WILL NOT OPEN FOR YOU")
        for line in sec[i:sec.index(" A seat has one condition beyond", i)].splitlines():
            if "GET https://" not in line:
                self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
