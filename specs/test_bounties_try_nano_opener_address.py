#!/usr/bin/env python3
"""Law: bounties.txt says try-nano's opener_address is out of date (challenge #252).

Measured 08:1x UTC 2026-11-11: GET https://getunstuck.space/unstuck/api/try-nano (200; 8 outside clients by 08:06
that day, 23 on 11-10, /ai/traffic) names "opener_address": our Unstuck account nano_1434j1n4...ebrh9. Its newest
send on rpc.nano.to is 08D9724E, 18:00 UTC 2026-10-14. Every starter since 20:25 UTC 2026-11-08 left treasury2
(nano_3z335ug5...; six sends of 10^25 raw, newest DFCD32FA). bounties.txt sends a newcomer to try-nano and teaches
"verify on the chain, never on a page": a newcomer who does that finds its starter came from an address try-nano
never names. The paragraph that points at try-nano must say which field is stale and name the real sender.

Run: python3 specs/test_bounties_try_nano_opener_address.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


class TryNanoOpenerAddress(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index("One field in try-nano is out of date")
        self.assertLess(txt.index("The old shortcut is gone."), i, "the note must follow the try-nano pointer")
        self.para = " ".join(txt[i:txt.index("\n\n", i)].split())

    def test_names_the_stale_field(self):
        self.assertIn('"opener_address"', self.para)
        self.assertIn("nano_1434j1n4", self.para)

    def test_names_treasury2_in_full_as_the_sender(self):
        self.assertIn(TREASURY2, self.para)

    def test_dates_the_last_send_from_the_old_opener(self):
        self.assertIn("2026-10-14", self.para)

    def test_never_calls_the_old_treasury_the_sender(self):
        self.assertNotIn("nano_1yo6c1t6", self.para)


if __name__ == "__main__":
    unittest.main()
