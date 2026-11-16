"""Challenge #286 (2026-11-16): the first line a reader sees offers the work that is open.

The delivery of job-20261113-001 has been in since 2026-11-14 19:28:13 UTC (ask 628), so the only paid
work a new reader can take is a verdict seat (0.1 XNO each, until 2026-11-17 19:28:13 UTC). Yet the
RIGHT NOW box of bounties.txt and line 5 of both llms.txt copies opened with "open until 11-20" and
"1 XNO for the delivery" - a date and a size nobody can earn - and named the seats, the 72-hour clock
and the one free ask only after. These laws keep the open seats, their deadline, their size and the
one action ahead of the delivery pay in each head.
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DUE = "2026-11-17 19:28"
VERDICT = "0.1 XNO for each verdict, pass or fail"
DELIVERY = "1 XNO for the delivery, once it passes"
ASK_TITLE = '"job-20261113-001 verdict"'


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def heads():
    b = read("published/bounties.txt")
    box = flat(b[b.index(" RIGHT NOW - measured "):b.index("WORKS, FREE")])
    out = [("bounties.txt", box)]
    for p in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
        t = read(p)
        out.append((p, flat(t[t.index("Paid work"):t.index("A delivery is in")])))
    return out


class HeadLeadsWithOpenSeats(unittest.TestCase):
    def test_seats_deadline_size_and_action_come_before_the_delivery_pay(self):
        for name, h in heads():
            with self.subTest(name):
                d = h.index(DELIVERY)
                for part in ("0 of 3", DUE, VERDICT, ASK_TITLE, "no account"):
                    self.assertIn(part, h)
                    self.assertLess(h.index(part), d, part)

    def test_head_says_the_delivery_is_already_in(self):
        for name, h in heads():
            with self.subTest(name):
                self.assertIn("one is in, under review", h)

    def test_the_head_does_not_open_on_the_job_date(self):
        for name, h in heads():
            with self.subTest(name):
                self.assertNotIn("OPEN UNTIL 11-20", h)
                self.assertFalse(h.split("Paid work", 1)[-1].lstrip(", :").startswith("open until"))

    def test_llms_copies_identical(self):
        self.assertEqual(read("published/aidirectory/llms.txt"), read("published/aidirectory-llms.txt"))

    def test_law_fails_on_the_old_head(self):
        old = flat("Paid work, open until 2026-11-20 23:59 UTC: job-20261113-001 (untested; 1 XNO for the "
                   "delivery, once it passes; 0.1 XNO for each verdict, pass or fail). Section 9.")
        self.assertLess(old.index(DELIVERY), old.index(VERDICT))
        self.assertNotIn(ASK_TITLE, old)


if __name__ == "__main__":
    unittest.main()
