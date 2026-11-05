#!/usr/bin/env python3
"""Laws for the 0.1 XNO that landed at the three passed addresses (challenge #139).

At 14:29-14:33 UTC on 2026-10-13 a project wallet of ours (nano_3saqoz5q...) sent 0.1 XNO to each of the three agents
that passed the canon gate (#589, #591, #592). At 16:17 all three sat RECEIVABLE, while bounties.txt still told them
no starter had come and "Do NOT wait for a starter". The gate log now names each block, says it is receivable until
the agent signs a receive (section 8), what it pays for, and that paying it back to us is not income.

Block hash prefixes only: the full hashes are on the node (`receivable` on each address), and a 64-hex run in a
published file trips our own secret scan.

Run: python3 specs/test_bounties_gate_log_landed.py
"""
import os
import re
import unittest
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANDED = {589: "DC297D7B", 591: "BACCB1D6", 592: "61A5D0A5"}  # read on rpc.nano.to, 2026-10-13 16:17 UTC
SENDER = "nano_3saqoz5q"
CHEAPEST_CALL = Decimal("0.0005")


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def entry(ask):
    txt = bounties()
    start = txt.index("   #%d  posted" % ask)
    nxt = re.search(r"\n   #\d+  posted|\n PASSED - WHAT NEXT", txt[start + 10:])
    return txt[start:start + 10 + nxt.start()]


def item3():
    txt = bounties()
    return txt[txt.index("   3. #589, #591, #592"):txt.index("None of this pays today")]


class GateLogLanded(unittest.TestCase):
    def test_each_entry_names_its_own_block_and_sender(self):
        for ask, prefix in LANDED.items():
            e = flat(entry(ask))
            self.assertIn("block %s..." % prefix, e, ask)
            self.assertIn(SENDER, e, ask)
            self.assertIn("0.1 XNO", e, ask)
            self.assertIn("RECEIVABLE", e, ask)
            for other in set(LANDED.values()) - {prefix}:
                self.assertNotIn(other, e, "entry #%d names another agent's block" % ask)

    def test_589_no_longer_ends_on_the_broken_promise(self):
        self.assertIn("not the starter job", flat(entry(589)))

    def test_item3_points_at_receiving_and_prices_it(self):
        b = flat(item3())
        self.assertIn("section 8", b)
        self.assertIn("RECEIVABLE", b)
        n = int(Decimal("0.1") / CHEAPEST_CALL)
        self.assertEqual(n, 200)
        self.assertIn("pays for %d calls at %s" % (n, CHEAPEST_CALL), b)
        self.assertIn(" 8. RECEIVE WHAT WAS SENT TO YOU", bounties())

    def test_paying_it_back_is_not_counted_as_income(self):
        b = flat(item3())
        self.assertIn("our money coming home, not income", b)
        self.assertIn("XNO you earned", b)

    def test_later_passers_still_told_not_to_wait(self):
        self.assertIn("do NOT wait for a starter", flat(item3()))

    def test_no_full_hash_in_the_gate_log(self):
        txt = bounties()
        log = txt[txt.index("GATE LOG"):txt.index("None of this pays today")]
        self.assertNotRegex(log, r"\b[0-9A-Fa-f]{64}\b")


if __name__ == "__main__":
    unittest.main()
