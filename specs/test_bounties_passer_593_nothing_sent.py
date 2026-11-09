#!/usr/bin/env python3
"""Laws for passer #593 and the 0.1 XNO promise in bounties.txt (challenge #150).

On 2026-10-24 Nano Receipt Lab (nano_1mx64gbrj3t...) passed the canon confirmation (#593, answer #387) and then
asked for the DAILY grant in ask #594. Section 1 still said "So pass section 2 and a 0.1 XNO is sent; plan on it".
No 0.1 XNO had gone to anyone since 10-13, nothing sends one on its own, and at 12:2x UTC its account held nothing
from the reward account, the project wallet or the treasury (rpc.nano.to). The gate log stopped at #592.

Run: python3 specs/test_bounties_passer_593_nothing_sent.py
"""
import importlib.util
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDR = "nano_1mx64gbrj3t8frxgp75y9sxxh17njcf67tmyqktubqsd7inwmkw9din7k9nt"
OURS = {"nano_1434j1n4", "nano_3saqoz5q", "nano_1yo6c1t6", "nano_3z335ug5"}  # treasury2 sends starters since 11-08 (#239)

spec = importlib.util.spec_from_file_location("nano_address", os.path.join(ROOT, "specs", "nano_address.py"))
nano_address = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nano_address)


def bounties():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        return f.read()


class Passer593(unittest.TestCase):
    def setUp(self):
        self.txt = bounties()
        self.flat = " ".join(self.txt.split())

    def test_no_promise_that_passing_sends_a_grant(self):
        self.assertNotIn("So pass section 2 and a 0.1 XNO is sent", self.flat)
        self.assertNotIn("plan on it once you have received yours", self.flat)
        self.assertIn("Do NOT plan on a 0.1 XNO for passing section 2", self.flat)
        self.assertIn("Nothing sends one on its own", self.flat)

    def test_gate_log_has_593_before_the_end_marker(self):
        section = self.txt[self.txt.index("GATE LOG"):self.txt.index("Not in this log yet?")]
        m = re.search(r"^\s+#593\s+posted (\S+) .*\n\s+PASSED, judged (\S+)", section, re.M)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(2), "2026-10-24")
        spec = importlib.util.spec_from_file_location("scan", os.path.join(ROOT, "ops", "scan-ask-inbox.py"))
        scan = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scan)
        self.assertEqual(scan.gate_log(self.txt).get(593), ("PASSED", "2026-10-24"))

    def test_the_one_liner_names_a_valid_address_and_our_accounts(self):
        line = next(l for l in self.txt.splitlines() if ADDR in l and l.strip().startswith("python3 -c"))
        self.assertTrue(nano_address.check_nano_address(ADDR))
        o = re.search(r"O=\(([^)]*)\)", line).group(1)
        self.assertEqual({s.strip("'") for s in o.split(",")}, OURS)

    def test_the_one_liner_counts_only_our_accounts_against_a_stub(self):
        line = next(l for l in self.txt.splitlines() if ADDR in l and l.strip().startswith("python3 -c"))
        code = re.search(r'python3 -c "(.*)"$', line.strip()).group(1)
        hist = {"history": [
            {"account": "nano_3top1ao59iks4hdctz5jyn5hr7d6zr3wogyxj9qzc1wc7e8w9gotr6unwr4p"},
            {"account": "nano_1hk1cu3773u5r39e75mtqrauzro75j3hwdzyewz8izokzur66semy739w14h"},
            {"account": "nano_3saqoz5qfgmohfz3dg5ywwmxj7dwdp3g6xfbspt11g7gyrxgbupi1w9"}]}
        recv = {"blocks": {"AB": {"source": "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"},
                           "CD": {"source": "nano_3top1ao59iks4hdctz5jyn5hr7d6zr3wogyxj9qzc1wc7e8w9gotr6unwr4p"}}}
        import io
        import contextlib
        import urllib.request

        class Resp(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

        def fake(req, *a, **k):
            body = json.loads(req.data)
            self.assertEqual(body["account"], ADDR)
            return Resp(json.dumps(hist if body["action"] == "account_history" else recv).encode())

        real = urllib.request.urlopen
        urllib.request.urlopen = fake
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                exec(code, {})
        finally:
            urllib.request.urlopen = real
        self.assertEqual(out.getvalue().strip(), "FROM US, received: 1 | FROM US, waiting: 1")


if __name__ == "__main__":
    unittest.main()
