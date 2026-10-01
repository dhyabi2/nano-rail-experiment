#!/usr/bin/env python3
"""Laws for the address advice on the canon page (/canon, served from published/canon.html).

Found 2026-10-01 (challenge #74): challenge #69 stopped bounties.txt from offering the server-generated onramp seed,
but the canon page still said "No address yet? Take one from GET /unstuck/api/v1/onramp/address" with no warning.
The same day the onramp was the most-requested path on the host (10 distinct clients).

Laws: no published file names the onramp endpoint without saying its seed is compromised; the canon page carries
the same one-line wallet command as bounties.txt Step 1; the canon page points at the gate log.

Run: python3 specs/test_canon_page_self_custody.py
"""
import html
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
ONRAMP = "/unstuck/api/v1/onramp/address"


def read(rel):
    with open(os.path.join(PUB, rel)) as f:
        return f.read()


def published_files():
    for d, _, files in os.walk(PUB):
        for name in files:
            if name.endswith((".txt", ".html", ".json", ".md")):
                yield os.path.relpath(os.path.join(d, name), PUB)


class CanonPageSelfCustody(unittest.TestCase):
    def test_onramp_never_named_without_warning(self):
        for rel in published_files():
            txt = read(rel)
            for m in re.finditer(re.escape(ONRAMP), txt):
                window = txt[max(0, m.start() - 600): m.end() + 1200].lower()
                self.assertIn("compromised", window, f"{rel}: names the onramp seed without the warning")

    def test_canon_page_does_not_offer_onramp_address(self):
        page = read("canon.html")
        self.assertNotRegex(page, r"(?i)take one from\s*<code>GET /unstuck/api/v1/onramp")

    def test_canon_page_wallet_command_matches_bounties_step1(self):
        b = read("bounties.txt")
        block = b[b.index("STEP 1 - "):b.index("STEP 2 - ")]
        cmds = [ln.strip() for ln in block.splitlines() if ln.strip().startswith(("mkdir ", "node "))]
        self.assertEqual(len(cmds), 2)
        page = html.unescape(read("canon.html"))
        for c in cmds:
            self.assertIn(c, page)

    def test_canon_page_points_at_gate_log(self):
        page = read("canon.html")
        self.assertIn("GATE LOG", page)
        self.assertIn('href="/bounties.txt"', page)


if __name__ == "__main__":
    unittest.main(verbosity=2)
