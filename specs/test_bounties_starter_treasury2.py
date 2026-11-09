#!/usr/bin/env python3
"""Law: bounties.txt knows the account starters now come from (challenge #239).

Measured 00:20 UTC 2026-11-09 (rpc.nano.to): since 20:25 UTC 11-08 the starter job sends from TREASURY2,
nano_3z335ug5... (owner rule 2), six sends of exactly 10^25 raw, all six still receivable. bounties.txt still said
"STARTER: none since 2026-10-14. Plan on none." and its section 4 read only the Unstuck account. The FROM US one-liners
it gives Nano Receipt Lab (#593, starter B8B59250) and Muse (#626, starter DFCD32FA) listed our accounts without
treasury2, so both printed "received: 0 | waiting: 0" while a starter from us sat receivable at their address.

Run: python3 specs/test_bounties_starter_treasury2.py
"""
import io
import json
import os
import sys
import unittest
import urllib.request
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def from_us_lines(txt):
    return [l.strip() for l in txt.splitlines() if "FROM US, received:" in l]


def run_one_liner(line, history, receivable):
    """Run a published FROM-US one-liner against a stub node; return what it prints."""
    code = line[len('python3 -c "'):-1]

    def fake(req, *a, **k):
        body = json.loads(req.data)
        out = {"history": history} if body["action"] == "account_history" else {"blocks": receivable}
        return io.BytesIO(json.dumps(out).encode())

    buf = io.StringIO()
    with mock.patch.object(urllib.request, "urlopen", fake), mock.patch("sys.stdout", buf):
        exec(code, {})
    return buf.getvalue().strip()


class StarterTreasury2(unittest.TestCase):
    def test_treasury2_address_is_valid_and_named(self):
        import nano_address
        self.assertTrue(nano_address.check_nano_address(TREASURY2))
        self.assertIn(TREASURY2, bounties())

    def test_every_from_us_line_counts_a_treasury2_starter(self):
        lines = from_us_lines(bounties())
        self.assertGreaterEqual(len(lines), 2)
        for line in lines:
            self.assertIn("'nano_3z335ug5'", line)
            got = run_one_liner(line, [], {"DFCD32FA" + "0" * 56: {"amount": "10000000000000000000000000", "source": TREASURY2}})
            self.assertEqual(got, "FROM US, received: 0 | FROM US, waiting: 1", line[:90])
            got = run_one_liner(line, [{"account": TREASURY2, "type": "receive"}], {})
            self.assertEqual(got, "FROM US, received: 1 | FROM US, waiting: 0")

    def test_right_now_box_no_longer_says_none_since_10_14(self):
        txt = bounties()
        box = " ".join(txt[txt.index(" RIGHT NOW - measured "):txt.index(" 1. THE REWARDS")].split())
        self.assertNotIn("none since 2026-10-14", box)
        self.assertIn("nano_3z335ug5", box)

    def test_section_4_reads_treasury2(self):
        txt = bounties()
        sec = txt[txt.index("\n BEFORE STEP 6 - YOUR FIRST XNO"):txt.index("\n STEP 6 - ")]
        cmd = [l for l in sec.splitlines() if "account_history" in l and TREASURY2 in l]
        self.assertEqual(len(cmd), 1)
        self.assertIn("https://rpc.nano.to", cmd[0])
        self.assertNotIn("work_generate", cmd[0])


if __name__ == "__main__":
    unittest.main()
