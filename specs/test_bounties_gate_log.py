#!/usr/bin/env python3
"""Laws for the canon-confirmation gate log in bounties.txt section 2 (challenge #73).

bounties.txt promises the confirmation gate is "judged openly ... and a refusal comes with its
reason". The gate log is where that verdict is published. These tests pin three things: every log
entry is machine-readable with a verdict and a date (so ops/scan-ask-inbox.py can read it); a
judged confirmation leaves the scanner's pending list while an unjudged one stays on it; and the
published "not in this log yet?" one-liner runs and lists only canon asks.

Run: python3 specs/test_bounties_gate_log.py
"""
import importlib.util
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"

spec = importlib.util.spec_from_file_location("scan", os.path.join(ROOT, "ops", "scan-ask-inbox.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

FIXTURE = {"asks": [
    {"id": 578, "asker": "nano_3uojbn47b5xqcbs4yibbasamn8aeyqxgyi1z8peogwtdn6z3kagjanjpz4ss",
     "title": "Canon read + qualification: which line, one disagreement, hash, commitment",
     "body": "line 2 ... disagree ... " + scan.CANON_SHA256 + " ... I hold my own key",
     "status": "open", "answerCount": 0, "bountyRaw": "0", "acceptedAnswerId": None,
     "settlementBlock": None, "created_at": "2026-09-27T02:39:10.770Z"},
    {"id": 900, "asker": "nano_1outsider", "title": "canon confirmation", "body": "a) line 3",
     "status": "open", "answerCount": 0, "bountyRaw": "0", "acceptedAnswerId": None,
     "settlementBlock": None, "created_at": "2026-10-01T00:00:00.000Z"},
    {"id": 1, "asker": TREASURY, "title": "How do I detect an abandoned Nano account", "body": "",
     "status": "open", "answerCount": 127, "bountyRaw": "1" + "0" * 27, "acceptedAnswerId": None,
     "settlementBlock": None, "created_at": "2026-09-17T00:00:00.000Z"},
]}


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


class GateLog(unittest.TestCase):
    def test_every_entry_parses_with_verdict_and_date(self):
        txt = bounties()
        section = txt[txt.index("GATE LOG"):txt.index("Not in this log yet?")]
        ids_written = set(int(i) for i in re.findall(r"^\s+#(\d+)\s+posted", section, re.M))
        log = scan.gate_log(txt)
        self.assertTrue(ids_written, "gate log has no entries")
        self.assertEqual(ids_written, set(log), "an entry is written in a shape the scanner cannot read")
        for verdict, date in log.values():
            self.assertIn(verdict, ("PASSED", "REFUSED"))
            self.assertRegex(date, r"^2\d{3}-\d{2}-\d{2}$")

    def test_a_refusal_carries_a_reason(self):
        # "a refusal comes with its reason": a REFUSED line must be followed by more text than the verdict.
        for m in re.finditer(r"REFUSED, judged \S+ (.*)\n(.*)\n", bounties()):
            self.assertGreater(len((m.group(1) + m.group(2)).strip()), 20)

    def test_judged_leaves_pending_unjudged_stays(self):
        rows = {r["id"]: r for r in scan.build_report(FIXTURE, scan.gate_log(bounties()))}
        self.assertNotIn(1, rows, "our own ask must never be counted as outside")
        self.assertEqual(rows[578]["verdict"], "PASSED")
        self.assertFalse(rows[578]["pending"])
        self.assertIsNone(rows[900]["verdict"])
        self.assertTrue(rows[900]["pending"], "an unjudged confirmation must stay on the pending list")

    def test_published_one_liner_lists_only_canon_asks(self):
        m = re.search(r"Not in this log yet\?.*?\n\s+curl -s https://getunstuck\.space/unstuck/api/asks \| python3 -c \"(.*?)\"\n",
                      bounties(), re.S)
        self.assertIsNotNone(m, "the one-liner is missing or changed shape")
        out = subprocess.run([sys.executable, "-c", m.group(1)], input=json.dumps(FIXTURE),
                             capture_output=True, text=True, check=True).stdout.split("\n")
        ids = sorted(int(line.split()[0]) for line in out if line.strip())
        self.assertEqual(ids, [578, 900])


if __name__ == "__main__":
    unittest.main(verbosity=2)
