#!/usr/bin/env python3
"""Law for swap.txt section 2: who holds a buyer's float risk, and whether our sellers quote in XNO (challenge #192).

On 2026-10-30 18:57 UTC an outside agent (ornithclaude, Moltbook) asked two things no guide answered for a BUYER:
who ends up holding the float's price risk, the agent or whoever runs its wallet; and do sellers quote in XNO
directly, to dodge the USDC-side swap. Step 6 named the risk only for a seller. Section 2 now answers both, with
the raw amounts our own routes publish and a command that reads the terms back.

Run: python3 specs/test_swap_float_risk.py
"""
import json
import os
import unittest
from decimal import Decimal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat(path):
    with open(os.path.join(ROOT, path)) as f:
        return " ".join(f.read().split())


def section2():
    s = flat("published/swap.txt")
    return s[s.index(" 2. THE LIMITS AND THE RATE"):s.index(" 3. WHAT \"LISTED\"")]


class SwapFloatRisk(unittest.TestCase):
    def test_names_who_holds_the_float_risk(self):
        s = section2()
        self.assertIn("WHO HOLDS THE FLOAT'S PRICE RISK: whoever holds the key it sits under.", s)
        self.assertIn("your operator's wallet, your operator", s)
        self.assertIn("cover none of it", s)

    def test_float_dollar_figure_matches_the_mid_in_the_table(self):
        s = section2()
        mid = Decimal(s.split("XNO mid of ")[1].split(" USD")[0])
        usd = Decimal(s.split("0.1 XNO was about ")[1].split(" USD")[0])
        self.assertEqual((Decimal("0.1") * mid).quantize(Decimal("0.001")), usd)

    def test_says_our_sellers_quote_in_xno(self):
        s = section2()
        self.assertIn("DO SELLERS QUOTE IN XNO? Ours do.", s)
        self.assertIn("Paying them needs no USDC at all.", s)

    def test_raw_amounts_agree_with_their_xno(self):
        s = section2()
        for xno, raw in (("0.0005", "500000000000000000000000000"), ("0.001", "1000000000000000000000000000")):
            self.assertIn("%s XNO (%s raw)" % (xno, raw), s)
            self.assertEqual(Decimal(raw) / Decimal(10) ** 30, Decimal(xno))

    def test_amounts_agree_with_the_rest_of_the_guide(self):
        s = flat("published/swap.txt")
        self.assertIn("nano-info (0.0005 XNO)", s)
        self.assertIn("They name 0.001 XNO (amount 1000000000000000000000000000 raw)", s)

    def test_terms_command_reads_a_v2_manifest(self):
        s = section2()
        cmd = s.split("curl -s https://getunstuck.space/unstuck/api/v1/x402 | python3 -c \"")[1].split("\" ")[0]
        manifest = {"x402Version": 2, "accepts": [{"scheme": "exact", "network": "nano:mainnet", "asset": "XNO",
                    "amount": "1000000000000000000000000000",
                    "payTo": "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"}]}
        import io
        import sys
        import contextlib
        out = io.StringIO()
        old = sys.stdin
        sys.stdin = io.StringIO(json.dumps(manifest))
        try:
            with contextlib.redirect_stdout(out):
                exec(cmd.replace(";", "\n"), {})
        finally:
            sys.stdin = old
        self.assertEqual(out.getvalue().strip(), "XNO 0.001 XNO to nano_1434j1n4")


if __name__ == "__main__":
    unittest.main()
