#!/usr/bin/env python3
"""Challenge #295: bounties.txt said every paypercall route costs 0.0001-0.0005 XNO; one costs 0.05.

The live terms (https://extract.paypercall.dev/.well-known/x402, read 10:2x UTC 2026-11-16, saved as
specs/fixtures/vend-x402-manifest-2026-11-16.json) list 24 resources. 23 are 0.0001-0.0005 XNO, but browser-agent
asks 5*10^28 raw = 0.05 XNO, 100 times the ceiling the page printed in STEP 5's operator request and STEP 6. An agent
that sized its cap from the page would hit a 402 it could not pay, or spend 100 times what it planned.

These laws hold the page to the fixture: every price range the page states covers the fixture's highest price, the
most expensive route is named with its amount, and the printed price one-liner reads the fixture correctly.

Run: python3 specs/test_vend_price_range.py
"""
import decimal
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "specs", "fixtures", "vend-x402-manifest-2026-11-16.json")
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


def manifest():
    with open(FIXTURE) as f:
        return json.load(f)


def prices():
    out = {}
    for r in manifest()["resources"]:
        for a in r["accepts"]:
            out[r["url"].split("/")[-1]] = decimal.Decimal(a["amount"]) / 10 ** 30
    return out


def page():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


class VendPriceRange(unittest.TestCase):
    def test_fixture_is_the_vend_terms(self):
        m = manifest()
        self.assertEqual(len(m["resources"]), 24)
        for r in m["resources"]:
            for a in r["accepts"]:
                self.assertEqual(a["asset"], "XNO")
                self.assertEqual(a["network"], "nano:mainnet")
                self.assertEqual(a["payTo"], TREASURY2)

    def test_every_stated_range_covers_the_top_price(self):
        top = max(prices().values())
        s = flat(page())
        ranges = re.findall(r"0\.0001-(0\.\d+) XNO a call", s)
        self.assertTrue(ranges, "the page states no per-call range")
        for hi in ranges:
            covered = decimal.Decimal(hi) >= top
            excepted = "ONE COSTS 100 TIMES MORE: browser-agent, 0.05 XNO" in s
            self.assertTrue(covered or excepted, "range 0.0001-%s XNO hides a %s XNO route" % (hi, top))

    def test_top_route_named_with_its_amount(self):
        p = prices()
        name = max(p, key=p.get)
        self.assertEqual(name, "browser-agent")
        s = flat(page())
        self.assertIn("browser-agent, 0.05 XNO (50000000000000000000000000000 raw", s)
        self.assertIn("23 cost 0.0001-0.0005 XNO a call", s)
        self.assertEqual(sum(1 for v in p.values() if v <= decimal.Decimal("0.0005")), 23)
        self.assertIn("Pay the amount each 402 names, never a price from this page.", s)

    def test_price_one_liner_reads_the_fixture(self):
        line = [l for l in page().splitlines() if "decimal.Decimal(a['amount'])/10**30" in l]
        self.assertEqual(len(line), 1)
        code = line[0].split('python3 -c "', 1)[1].rstrip().rstrip('"')
        import io
        import sys
        old_in, old_out = sys.stdin, sys.stdout
        sys.stdin, sys.stdout = open(FIXTURE), io.StringIO()
        try:
            exec(code, {})
            out = sys.stdout.getvalue()
        finally:
            sys.stdin.close()
            sys.stdin, sys.stdout = old_in, old_out
        self.assertIn("0.05 XNO browser-agent", out)
        self.assertEqual(len(out.splitlines()), 24)


if __name__ == "__main__":
    unittest.main()
