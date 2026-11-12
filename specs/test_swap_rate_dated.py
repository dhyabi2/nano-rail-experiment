#!/usr/bin/env python3
"""Law for a dated rate in swap.txt (challenge #259).

swap.txt section 2 opened with "Minimum / Maximum / Rate 5 USDC-BASE -> 12.550897 XNO (about 2.51 XNO per USDC)"
and no date, followed by "ours is already minutes old by the time you read this". Those three numbers were read on
2026-09-26; the table further down (2026-10-30) put the same 5 USDC at 14.63 XNO, 17% more. A reader sizing a swap
from the first number saw a rate seven weeks old presented as minutes old, and two rates on one page that disagree.

Law: every rate or limit line in section 2 sits under a "MEASURED <date>" line or carries its own date; the page no
longer calls its own numbers "minutes old"; the live check commands are still there.

Run: python3 specs/test_swap_rate_dated.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def section2():
    with open(os.path.join(ROOT, "published/swap.txt")) as f:
        s = f.read()
    return s[s.index(" 2. THE LIMITS AND THE RATE"):s.index(" WHAT A SMALL SWAP COSTS YOU")]


class SwapRateDated(unittest.TestCase):
    def test_header_block_is_dated(self):
        s = section2()
        m = re.search(r"MEASURED (\d{4}-\d{2}-\d{2})", s)
        self.assertIsNotNone(m, "section 2's limits carry no MEASURED date")
        self.assertLess(s.index(m.group(0)), s.index("Minimum   0.230737"))

    def test_every_rate_line_has_a_date(self):
        s = " ".join(section2().split())
        hits = list(re.finditer(r"[\d.]+ XNO per USDC", s))
        self.assertGreaterEqual(len(hits), 2)
        for m in hits:
            window = s[max(0, m.start() - 90):m.end() + 12]
            self.assertRegex(window, r"\d{2}-\d{2}", "rate without a date beside it: " + m.group(0))

    def test_not_called_minutes_old(self):
        self.assertNotIn("minutes old by the time you read this", section2())

    def test_live_check_kept(self):
        s = section2()
        self.assertIn("curl -s 'https://api.nanswap.com/v1/get-limits?from=USDC-BASE&to=XNO'", s)
        self.assertIn("curl -s 'https://api.nanswap.com/v1/get-estimate?from=USDC-BASE&to=XNO&amount=5'", s)


if __name__ == "__main__":
    unittest.main()
