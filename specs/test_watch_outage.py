#!/usr/bin/env python3
"""Laws for ops/watch-outage.py (challenge #148).

The off-box watcher must report the 10-17 outage as it was measured (a 502 on every guide, timeouts on every seller,
10 XNO receivable for days); must call a seller that names another payee or no XNO a fault; must never report a check
that could not run as clean; must send only read-only RPC actions; and the workflow must run on a schedule and open,
update and close one issue rather than mail the owner every hour.

Run: python3 specs/test_watch_outage.py
"""
import importlib.util
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("wo", os.path.join(ROOT, "ops", "watch-outage.py"))
wo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wo)

NOW = 1792800000
GOOD_MANIFEST = json.dumps({"x402Version": 2, "resources": [{"resource": "/v1/extract", "accepts": [
    {"scheme": "exact", "network": "nano:mainnet", "asset": "XNO", "amount": "100000000000000000000000000",
     "payTo": wo.TREASURY}]}]}).encode()


def ctype_for(url):
    if url.endswith(".txt"):
        return "text/plain; charset=utf-8"
    if url.endswith(".json") or "/api/" in url:
        return "application/json"
    return "text/html; charset=utf-8"


def healthy_get(url):
    if url.endswith("/.well-known/x402"):
        return 200, "application/json", GOOD_MANIFEST
    return 200, ctype_for(url), b"ok"


def outage_get(url):  # what every URL did on 10-23: Vercel 502 on getunstuck, nothing at all from the box
    return (502, "text/plain", b"") if "getunstuck.space" in url else (0, "", b"timeout")


def chain(balance="71617800000000000000000000000000", receivable=None, ts=None, seen=None):
    def call(payload):
        if seen is not None:
            seen.append(payload["action"])
        if payload["action"] == "account_info":
            return {"balance": balance, "balance_nano": str(int(balance) / 10**30)}
        if payload["action"] == "receivable":
            return {"blocks": {h: "1" for h in (receivable or [])} or ""}
        if payload["action"] == "blocks_info":
            return {"blocks": {h: {"local_timestamp": str(ts)} for h in payload["hashes"]}}
        raise AssertionError(payload)
    return call


class WatchOutage(unittest.TestCase):
    def test_all_clear(self):
        self.assertEqual(wo.run(healthy_get, chain(), lambda: NOW), [])

    def test_the_10_17_outage_is_loud(self):
        faults = wo.run(outage_get, chain(receivable=["5EE71904AA"], ts=NOW - 5 * 86400), lambda: NOW)
        self.assertEqual(len(faults), len(wo.PAGES) + len(wo.SELLERS) + 1)
        self.assertTrue(any("502" in f and "bounties.txt" in f for f in faults))
        self.assertTrue(any("5EE71904" in f and "120.0 hours" in f for f in faults))

    def test_fresh_receivable_is_not_a_fault(self):
        self.assertEqual(wo.check_treasury(chain(receivable=["AB"], ts=NOW - 600), lambda: NOW), [])

    def test_under_floor(self):
        self.assertIn("floor", wo.check_treasury(chain(balance=str(8 * 10**30)), lambda: NOW)[0])

    def test_unreadable_chain_is_never_clean(self):
        def boom(payload):
            raise OSError("reset")
        self.assertIn("could not be read", wo.check_treasury(boom, lambda: NOW)[0])

    def test_only_read_only_rpc(self):
        seen = []
        wo.check_treasury(chain(receivable=["AB"], ts=NOW, seen=seen), lambda: NOW)
        self.assertEqual(set(seen), {"account_info", "receivable", "blocks_info"})
        src = open(os.path.join(ROOT, "ops", "watch-outage.py")).read()
        for word in ('"send"', '"process"', '"receive"', "seed", "private"):
            self.assertNotIn(word, src.split('"""', 2)[2])

    def test_wrong_payee_or_no_xno(self):
        other = GOOD_MANIFEST.replace(wo.TREASURY.encode(), b"nano_3someoneelse")
        self.assertIn("other than the treasury", wo.check_manifest("extract", lambda u: (200, "", other)))
        usdc = GOOD_MANIFEST.replace(b'"XNO"', b'"USDC"').replace(b"nano:mainnet", b"eip155:8453")
        self.assertIn("does not accept XNO", wo.check_manifest("extract", lambda u: (200, "", usdc)))
        self.assertIn("no payTo", wo.check_manifest("extract", lambda u: (200, "", b'{"accepts": []}')))
        self.assertIn("not JSON", wo.check_manifest("extract", lambda u: (200, "", b"<html>")))

    def test_txt_guide_served_as_html_is_a_fault(self):
        f = wo.check_page("https://getunstuck.space/bounties.txt", "text/plain", lambda u: (200, "text/html", b""))
        self.assertIn("text/plain", f)

    def test_workflow_is_scheduled_and_quiet(self):
        wf = open(os.path.join(ROOT, ".github", "workflows", "outage-watch.yml")).read()
        self.assertIn("schedule:", wf)
        self.assertIn("ops/watch-outage.py", wf)
        self.assertIn("issues: write", wf)
        for step in ("gh issue create", "gh issue edit", "gh issue close"):
            self.assertIn(step, wf)
        self.assertNotIn("secrets.", wf.replace("secrets.GITHUB_TOKEN", ""))


if __name__ == "__main__":
    unittest.main()
