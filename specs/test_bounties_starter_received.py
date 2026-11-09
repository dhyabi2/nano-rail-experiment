#!/usr/bin/env python3
"""Law: bounties.txt says a treasury2 starter was received, and its recount reads treasury2 (challenge #241).

Measured 12:30 UTC 2026-11-09 (rpc.nano.to): treasury2 starter DFCD32FA (sent 00:05) was received at 04:18 UTC by
nano_1edjtwsj..., whose account it opened (its only block, 6EE4F76C). bounties.txt still said "6 sent, 0 received
yet" in the RIGHT NOW box and "0 of the 6 received yet" in section 4, and section 4's "Re-count it" one-liner read
only the old Unstuck account, so a stranger who re-counted saw 17 of 23 and never the new treasury's 5 of 6.

Run: python3 specs/test_bounties_starter_received.py
"""
import io
import json
import os
import unittest
import urllib.request
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OLD = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"
STARTER = "10000000000000000000000000"


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


def section4(txt):
    return txt[txt.index("\n BEFORE STEP 6 - YOUR FIRST XNO"):txt.index("\n STEP 6 - ")]


def recount_line(txt):
    lines = [l.strip() for l in section4(txt).splitlines()
             if "treasury2 starters still receivable" in l and l.strip().startswith("python3 -c")]
    assert len(lines) == 1, lines
    return lines[0]


class StarterReceived(unittest.TestCase):
    def test_box_and_section_4_no_longer_say_none_received(self):
        txt = bounties()
        flat = " ".join(txt.split())
        self.assertNotIn("0 received yet", flat)
        self.assertNotIn("0 of the 6 received", flat)
        box = " ".join(txt[txt.index(" RIGHT NOW - measured "):txt.index(" 1. THE REWARDS")].split())
        self.assertIn("6 sent, 1 received", box)
        self.assertIn("Plan on none", box)
        sec = " ".join(section4(txt).split())
        self.assertIn("1 of the 6 received", sec)
        self.assertIn("DFCD32FA", sec)
        self.assertIn("6EE4F76C", sec)

    def test_recount_reads_treasury2(self):
        line = recount_line(bounties())
        self.assertIn(TREASURY2, line)
        self.assertIn("https://rpc.nano.to", line)
        self.assertNotIn("work_generate", line)
        self.assertNotIn("process", line)

    def test_recount_against_a_stub_node(self):
        code = recount_line(bounties())[len('python3 -c "'):-1]
        hist = {TREASURY2: [{"type": "send", "amount": STARTER, "hash": "B1"},
                            {"type": "send", "amount": STARTER, "hash": "B2"},
                            {"type": "send", "amount": "5", "hash": "B3"},
                            {"type": "receive", "amount": STARTER, "hash": "B4"}]}
        recv = {"B1": "0", "B2": "1"}
        seen = []

        def fake(req, *a, **k):
            body = json.loads(req.data)
            seen.append(body["action"])
            if body["action"] == "account_history":
                out = {"history": hist[body["account"]]}
            else:
                out = {"blocks": {h: {"receivable": recv[h]} for h in body["hashes"]}}
            return io.BytesIO(json.dumps(out).encode())

        buf = io.StringIO()
        with mock.patch.object(urllib.request, "urlopen", fake), mock.patch("sys.stdout", buf):
            exec(code, {})
        self.assertEqual(buf.getvalue().strip(), "1 of 2 treasury2 starters still receivable")
        self.assertEqual(set(seen), {"account_history", "blocks_info"})


if __name__ == "__main__":
    unittest.main()
