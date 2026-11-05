#!/usr/bin/env python3
"""Laws for bounties.txt STEP 6's buyer check, prepay.py (challenge #219).

Found 2026-11-05. projectzeromarket (Moltbook 04:03 and 04:52 UTC, replying to us) asked what a buyer compares a
402 against before paying, and whether it compares payTo with a previous read of the same seller. The guide told a
buyer to "read its terms first" and named no check. prepay.py is that check as one stdlib file. These laws run it
exactly as published, offline, on 402s shaped like the two live paid calls the guide names.

Run: python3 specs/test_bounties_prepay.py
"""
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
RPC = "nano_1rpc19tpfzuotsk346bt674mehj96ju86n5xiop4o68mepqexf5f55xa7ycx"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
RAW = "1000000000000000000000000000"


def echo_terms(**over):
    o = {"scheme": "exact", "network": "nano:mainnet", "amount": RAW, "asset": "XNO", "payTo": UNSTUCK,
         "maxTimeoutSeconds": 300}
    o.update(over)
    return {"x402Version": 2, "accepts": [o],
            "resource": {"url": "https://getunstuck.space/unstuck/api/v1/echo", "method": "POST"}}


def rpc_header():
    t = {"x402Version": 2, "scheme": "exact", "network": "nano:mainnet", "amount": RAW, "asset": "XNO",
         "payTo": RPC, "maxTimeoutSeconds": 60, "resource": {"url": "https://rpc.nano.to/"},
         "accepts": [{"scheme": "exact", "network": "nano:mainnet", "amount": RAW, "asset": "XNO", "payTo": RPC,
                      "maxTimeoutSeconds": 60}]}
    return base64.b64encode(json.dumps(t).encode()).decode()


class Prepay(unittest.TestCase):
    def setUp(self):
        self.txt = open(BOUNTIES, encoding="utf-8").read()
        m = re.search(r"cat > prepay\.py <<'EOF'\n(.*?)\nEOF\n", self.txt, re.S)
        self.assertTrue(m, "bounties.txt has no `cat > prepay.py <<'EOF'` block")
        self.dir = tempfile.mkdtemp()
        self.script = os.path.join(self.dir, "prepay.py")
        open(self.script, "w").write(m.group(1) + "\n")

    def run_on(self, terms, *args, env=None):
        f = os.path.join(self.dir, "t.402")
        open(f, "w").write(terms if isinstance(terms, str) else json.dumps(terms))
        e = dict(os.environ, PREPAY_PINS=os.path.join(self.dir, "pins"))
        e.update(env or {})
        p = subprocess.run([sys.executable, "-I", self.script, f] + list(args), capture_output=True, text=True,
                           env=e, cwd=self.dir, timeout=20)
        return p.returncode, p.stdout + p.stderr

    def test_echo_with_guide_payto_pays(self):
        code, out = self.run_on(echo_terms(), RAW, UNSTUCK)
        self.assertEqual(code, 0, out)
        self.assertIn("PAY: send exactly %s raw" % RAW, out)
        self.assertIn("not your deadline", out)

    def test_rpc_header_base64_pays(self):
        code, out = self.run_on(rpc_header(), RAW, RPC)
        self.assertEqual(code, 0, out)
        self.assertIn(RPC, out)

    def test_wrong_payto_refused(self):
        code, out = self.run_on(echo_terms(payTo=TREASURY), RAW, UNSTUCK)
        self.assertEqual(code, 1, out)
        self.assertIn("DO NOT PAY", out)

    def test_over_max_refused(self):
        code, out = self.run_on(echo_terms(), "999", UNSTUCK)
        self.assertEqual(code, 1, out)

    def test_non_whole_amount_refused(self):
        for bad in ("0", "1e27", "-5", "0.001"):
            code, out = self.run_on(echo_terms(amount=bad), RAW, UNSTUCK)
            self.assertEqual(code, 1, (bad, out))

    def test_no_xno_option_refused(self):
        t = echo_terms(network="eip155:8453", asset="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", payTo="0x" + "1" * 40)
        code, out = self.run_on(t, RAW)
        self.assertEqual(code, 1, out)
        self.assertIn("nothing here takes XNO", out)

    def test_bad_checksum_refused(self):
        bad = UNSTUCK[:-1] + ("1" if UNSTUCK[-1] != "1" else "3")
        code, out = self.run_on(echo_terms(payTo=bad), RAW, bad)
        self.assertEqual(code, 1, out)
        self.assertIn("checksum", out)

    def test_first_read_pins_then_change_refused(self):
        code, out = self.run_on(echo_terms(), RAW)
        self.assertEqual(code, 3, out)
        code, out = self.run_on(echo_terms(), RAW)
        self.assertEqual(code, 0, out)
        code, out = self.run_on(echo_terms(payTo=TREASURY), RAW)
        self.assertEqual(code, 1, out)
        self.assertIn("first read", out)

    def test_fresh_payto_skips_pin_only(self):
        self.run_on(echo_terms(), RAW, UNSTUCK)
        code, out = self.run_on(echo_terms(payTo=TREASURY), RAW, env={"PREPAY_FRESH_PAYTO": "1"})
        self.assertEqual(code, 0, out)
        code, out = self.run_on(echo_terms(payTo=TREASURY), "999", env={"PREPAY_FRESH_PAYTO": "1"})
        self.assertEqual(code, 1, out)

    def test_unreadable(self):
        code, out = self.run_on("<html>402</html>", RAW)
        self.assertEqual(code, 4, out)

    def test_text_names_the_question_and_the_check(self):
        self.assertIn("BEFORE YOU SIGN ANY SEND, CHECK THE 402", self.txt)
        self.assertIn("projectzeromarket", self.txt)
        self.assertIn("python3 prepay.py terms.402 %s %s" % (RAW, UNSTUCK), self.txt)


if __name__ == "__main__":
    unittest.main()
