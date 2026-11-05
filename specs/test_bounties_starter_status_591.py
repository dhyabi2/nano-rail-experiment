#!/usr/bin/env python3
"""Laws for the #591 starter line in bounties.txt's gate log (challenge #134).

The keeper logged #591 at 16:25 UTC on 2026-10-12 with "No starter has been promised to it by us". At 16:30 the
swarm's conversation agent told #591 in its own thread (answer #383) that it had requested one. The published line was
false five minutes after it was written. The entry now says what the thread said and carries the same node-reading
one-liner as #589's (challenge #131), counting from the request. This runs it offline against a stubbed node.

Run: python3 specs/test_bounties_starter_status_591.py
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import test_bounties_starter_status_live as live  # noqa: E402

ELLA = "nano_1z6u7c1h4sd4dpuui6izzh4396s581x6cdord4i6k46mmsnyen7ed3fkg53d"


def entry():
    txt = live.entry()
    return txt[txt.index("   #591  posted"):]


def one_liner():
    m = re.search(r'^   python3 -c "(.*)"$', entry(), re.M)
    if m is None:
        raise AssertionError("the #591 status one-liner is missing or changed shape")
    return m.group(1)


class Starter591(unittest.TestCase):
    def setUp(self):
        self._saved = live.one_liner
        live.one_liner = one_liner

    def tearDown(self):
        live.one_liner = self._saved

    def test_no_longer_says_none_was_promised(self):
        flat = " ".join(entry().split())
        self.assertNotIn("No starter has been promised", flat)
        self.assertIn("answer #383", flat)
        self.assertIn("REQUESTED", flat)

    def test_names_591s_own_address_and_request_time(self):
        self.assertIn("A='%s'" % ELLA, one_liner())
        self.assertIn("D.datetime(2026,10,12,16,30", one_liner())

    def test_not_sent(self):
        out, asked = live.run({"receivable": {"blocks": []},
                               "account_info": {"error": "Account not found", "balance": "0"}})
        self.assertRegex(out, r"^NOT SENT, \d+ h after the request$")
        self.assertEqual({a["account"] for a in asked}, {ELLA})

    def test_sent_waiting(self):
        out, _ = live.run({"receivable": {"blocks": ["AB" * 32]}})
        self.assertEqual(out, "SENT - waiting for you to receive it")

    def test_sent_and_received(self):
        out, _ = live.run({"receivable": {"blocks": []}, "account_info": {"balance": "10000000000000000000000000"}})
        self.assertEqual(out, "SENT and received - account open")

    def test_589_line_still_first_and_its_own(self):
        self.assertIn("A='%s'" % live.HERMES, self._saved())


if __name__ == "__main__":
    unittest.main(verbosity=2)
