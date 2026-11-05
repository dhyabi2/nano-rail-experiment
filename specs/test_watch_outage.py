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


ECHO_MANIFEST = json.dumps({"x402Version": 2, "accepts": [
    {"scheme": "exact", "network": "nano:mainnet", "asset": "XNO", "amount": "1000000000000000000000000000",
     "payTo": wo.UNSTUCK}], "resource": {"url": "https://getunstuck.space/unstuck/api/v1/echo", "method": "POST"}}).encode()


def ctype_for(url):
    if url.endswith(".txt"):
        return "text/plain; charset=utf-8"
    if url.endswith(".json") or "/api/" in url:
        return "application/json"
    return "text/html; charset=utf-8"


def healthy_get(url):
    if url in wo.LIVE_CALL_MANIFESTS:
        return 200, "application/json", ECHO_MANIFEST
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
        self.assertEqual(len(faults), len(wo.PAGES) + len(wo.SELLERS) + len(wo.LIVE_CALL_MANIFESTS) + 1)
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

    # challenge #212: the one paid call the guides say works was in no check
    def test_live_paid_call_is_watched(self):
        self.assertIn("https://getunstuck.space/.well-known/x402", wo.LIVE_CALL_MANIFESTS)
        self.assertIn("https://getunstuck.space/unstuck/api/v1/x402", wo.LIVE_CALL_MANIFESTS)
        bounties = open(os.path.join(ROOT, "published", "bounties.txt")).read()
        self.assertIn(wo.UNSTUCK, bounties)  # the payee the guide names is the payee we hold it to
        for u in wo.LIVE_CALL_MANIFESTS:
            self.assertIsNone(wo.check_live_call(u, healthy_get))

    def test_live_call_served_as_octet_stream_is_a_fault(self):
        # what getunstuck.space/.well-known/x402 returned at 20:19 UTC 11-03
        f = wo.check_live_call(wo.LIVE_CALL_MANIFESTS[0], lambda u: (200, "application/octet-stream", ECHO_MANIFEST))
        self.assertIn("application/octet-stream", f)
        self.assertIn("not application/json", f)

    def test_live_call_paying_the_treasury_or_another_is_a_fault(self):
        # the echo pays the Unstuck account; a manifest naming anyone else (even the treasury) changed under us
        for other in (wo.TREASURY.encode(), b"nano_3someoneelse"):
            m = ECHO_MANIFEST.replace(wo.UNSTUCK.encode(), other)
            self.assertIn("other than our Unstuck account", wo.check_live_call(wo.LIVE_CALL_MANIFESTS[1], lambda u: (200, "application/json", m)))
        usdc = ECHO_MANIFEST.replace(b'"XNO"', b'"USDC"').replace(b"nano:mainnet", b"eip155:8453")
        self.assertIn("does not accept XNO", wo.check_live_call(wo.LIVE_CALL_MANIFESTS[1], lambda u: (200, "application/json", usdc)))
        self.assertIn("answered nothing", wo.check_live_call(wo.LIVE_CALL_MANIFESTS[1], lambda u: (0, "", b"")))

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

    # challenge #160: issue #121's body as the 01:42 UTC 10-26 run left it, before the box went down
    BODY_0142 = """6 fault(s) at 2026-10-26T01:42:42Z:
- https://extract.paypercall.dev/.well-known/x402 answered nothing (timeout or reset)
- https://search.paypercall.dev/.well-known/x402 answered nothing (timeout or reset)
- https://domain.paypercall.dev/.well-known/x402 answered nothing (timeout or reset)
- https://check.paypercall.dev/.well-known/x402 answered nothing (timeout or reset)
- https://geoip.paypercall.dev/.well-known/x402 answered nothing (timeout or reset)
- receivable block 5EE71904 at the treasury is 185.2 hours old (auto-receive is every 15 min)

Latest run: https://github.com/dhyabi2/nano-rail-experiment/actions/runs/40255400072
"""

    def test_box_down_under_an_open_seller_issue_is_new(self):
        faults = wo.run(outage_get, chain(receivable=["5EE71904AA"], ts=NOW - int(187.9 * 3600)), lambda: NOW)
        new = wo.new_faults(self.BODY_0142, faults)
        self.assertEqual(len(new), len(wo.PAGES) + len(wo.LIVE_CALL_MANIFESTS))
        self.assertTrue(all("getunstuck.space" in f or "sslip.io" in f for f in new))

    def test_same_faults_with_an_older_receivable_are_not_new(self):
        faults = wo.run(lambda u: healthy_get(u) if "paypercall" not in u else (0, "", b"timeout"),
                        chain(receivable=["5EE71904AA"], ts=NOW - int(190.4 * 3600)), lambda: NOW)
        self.assertEqual(len(faults), len(wo.SELLERS) + 1)
        self.assertEqual(wo.new_faults(self.BODY_0142, faults), [])

    def test_no_open_issue_means_everything_is_new(self):
        self.assertEqual(wo.new_faults("", ["a fault"]), ["a fault"])

    def test_workflow_comments_new_faults(self):
        wf = open(os.path.join(ROOT, ".github", "workflows", "outage-watch.yml")).read()
        self.assertIn("--previous prev.md --new-out new.txt", wf)
        self.assertIn("gh issue view", wf)
        self.assertIn('gh issue comment "$open"', wf)
        self.assertLess(wf.index("Read the open outage issue"), wf.index("ops/watch-outage.py --previous"))


if __name__ == "__main__":
    unittest.main()
