#!/usr/bin/env python3
"""Laws for the starter facts in bounties.txt (challenge #145).

On 2026-10-14 at 18:00 UTC the starter job sent its first starter since 10-08 (block 08D9724E...), and the recipient
received it at 19:12. bounties.txt still said "the starter job had still sent nothing" and "16 of the 21 starters
... still receivable (2026-10-04)", while the chain read 17 of 23 at 20:2x UTC. A reader deciding whether a starter is
real was told it was not, by a page eleven days stale.

Run: python3 specs/test_bounties_starter_job_sends_again.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return " ".join(f.read().split())


class StarterJobSendsAgain(unittest.TestCase):
    def test_no_stale_job_sent_nothing_claim(self):
        self.assertNotIn("starter job had still sent nothing", flat())

    def test_names_the_new_send_and_its_receive(self):
        t = flat()
        self.assertIn("08D9724E", t)
        self.assertIn("received it at 19:12", t)

    def test_still_says_do_not_wait(self):
        self.assertIn("do NOT wait for a starter.", flat())

    def test_count_is_the_10_14_chain_read(self):
        t = flat()
        self.assertNotIn("16 of the 21 starters", t)
        m = re.search(r"(\d+) of the (\d+) starters we have sent are still sitting receivable", t)
        self.assertIsNotNone(m)
        unreceived, sent = int(m.group(1)), int(m.group(2))
        self.assertEqual((unreceived, sent), (17, 23))
        self.assertIn("2026-10-14 20:2x UTC", t)


if __name__ == "__main__":
    unittest.main()
