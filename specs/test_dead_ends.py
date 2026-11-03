#!/usr/bin/env python3
"""Laws for ops/check-dead-ends.py (challenge #76).

The checker must call a 404/426/5xx a dead end and a 400 (a usage error that says what is missing) not one; must
never probe a path that mints a seed or moves money; must take only paths at or above the client threshold; and the
box draft must cover every dead end measured on 2026-10-01 without capturing websocket upgrades or POSTs.

Run: python3 specs/test_dead_ends.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("cde", os.path.join(ROOT, "ops", "check-dead-ends.py"))
cde = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cde)

# From /ai/traffic/2026-10-01.json (generated 12:07 UTC), top_paths_by_clients, abridged.
TRAFFIC = {"top_paths_by_clients": [
    {"path": "/unstuck/api/asks", "distinct_clients": 19},
    {"path": "/unstuck/api/v1/onramp/address", "distinct_clients": 17},
    {"path": "/unstuck/api/", "distinct_clients": 8},
    {"path": "/unstuck/api/ask", "distinct_clients": 7},
    {"path": "/canon.html", "distinct_clients": 6},
    {"path": "/", "distinct_clients": 5},
    {"path": "/unstuck/api/asks/500", "distinct_clients": 3},
    {"path": "/rare", "distinct_clients": 2},
]}
DEAD_2026_10_01 = ["/unstuck/api/", "/unstuck/api/ask", "/canon.html", "/", "/unstuck/api/asks/500"]


class DeadEnds(unittest.TestCase):
    def test_statuses(self):
        for s in (404, 410, 426, 500, 502, 503):
            self.assertTrue(cde.is_dead(s), s)
        for s in (200, 301, 302, 400, 402, 405):
            self.assertFalse(cde.is_dead(s), s)

    def test_never_probes_the_onramp(self):
        paths = [p for p, _ in cde.candidates(TRAFFIC, 1)]
        self.assertNotIn("/unstuck/api/v1/onramp/address", paths)
        self.assertFalse(cde.probe_safe("/unstuck/api/v1/onramp/address?x=1"))
        self.assertFalse(cde.probe_safe("https://elsewhere/"))

    def test_threshold_and_order(self):
        got = cde.candidates(TRAFFIC, 3)
        self.assertEqual([p for p, _ in got], ["/unstuck/api/asks"] + DEAD_2026_10_01)
        self.assertNotIn("/rare", [p for p, _ in got])

    def test_draft_covers_every_measured_dead_end(self):
        with open(os.path.join(ROOT, "drafts", "box-dead-ends.md")) as f:
            d = f.read()
        caddy = d[d.index("```\n") + 4:d.index("```", d.index("```\n") + 4)]
        self.assertIn("redir /canon.html /canon 301", caddy)
        self.assertIn("path /unstuck/api /unstuck/api/", caddy)
        self.assertIn("path /unstuck/api/ask\n", caddy)
        self.assertIn(r"^/unstuck/api/asks/(\d+)$", caddy)
        self.assertIn("redir @plain_root", caddy)
        # The root redirect must leave websocket upgrades alone, and the 405 must not swallow POSTs.
        self.assertIn("not header_regexp Upgrade (?i)websocket", caddy)
        ask_block = caddy[caddy.index("@ask_get {"):caddy.index("}", caddy.index("@ask_get {"))]
        self.assertIn("method GET HEAD", ask_block)
        self.assertNotIn("POST", ask_block)
        for p in DEAD_2026_10_01:
            self.assertIn(f"`{p}`", d, f"draft does not record measured dead end {p}")

    def test_draft_does_not_send_strangers_to_the_onramp(self):
        with open(os.path.join(ROOT, "drafts", "box-dead-ends.md")) as f:
            d = f.read()
        caddy = d[d.index("```\n") + 4:d.index("```", d.index("```\n") + 4)]
        self.assertNotIn("onramp", caddy)
        # try-nano still sells the onramp seed as "yours" (#75), so it is listed but never where to start.
        self.assertIn('"start_here":"https://172-86-112-140.sslip.io/bounties.txt"', caddy)


    def test_echo_get_answers_405_with_the_post(self):
        """#204: 13 outside clients GET the paid echo on 11-02 and got a bare 404."""
        with open(os.path.join(ROOT, "drafts", "box-dead-ends.md")) as f:
            d = f.read()
        caddy = d[d.index("```\n") + 4:d.index("```", d.index("```\n") + 4)]
        i = caddy.index("@echo_get {")
        matcher = caddy[i:caddy.index("}", i)]
        self.assertIn("path /unstuck/api/v1/echo", matcher)
        self.assertIn("method GET HEAD", matcher)
        self.assertNotIn("POST", matcher)  # the paid POST must still reach the backend
        h = caddy.index("handle @echo_get {")
        handler = caddy[h:caddy.index("\n}\n", h)]
        self.assertIn('header Allow "POST"', handler)
        self.assertIn("/unstuck/api/v1/x402", handler)
        self.assertIn("-X POST https://getunstuck.space/unstuck/api/v1/echo", handler)
        self.assertIn("X-Nano-Payment", handler)
        self.assertTrue(handler.rstrip().endswith("405"))
        self.assertIn("`/unstuck/api/v1/echo`", d)

    def test_known_dead_ends_name_their_draft(self):
        for p in DEAD_2026_10_01 + ["/unstuck/api/v1/echo", "/unstuck/api/asks/617"]:
            self.assertTrue(cde.drafted_fix(p), p)
        self.assertIsNone(cde.drafted_fix("/unstuck/api/never-seen"))


    # Challenge #208: the checker must not be the visitor it counts.
    def test_listed_asks_are_not_probed(self):
        self.assertEqual(cde.plan("/unstuck/api/ask/12", {1, 12, 618}, False), "listed")
        self.assertEqual(cde.plan("/unstuck/api/ask/9999", {1, 12, 618}, False), "probe")
        self.assertEqual(cde.plan("/unstuck/api/ask/12", None, False), "probe")  # list unreadable: probe

    def test_drafted_dead_ends_probed_once_a_day(self):
        import datetime as dt
        utc = dt.timezone.utc
        self.assertEqual(cde.plan("/unstuck/api/v1/echo", set(), False), "drafted")
        self.assertEqual(cde.plan("/unstuck/api/v1/echo", set(), True), "probe")
        self.assertTrue(cde.should_recheck([], dt.datetime(2026, 11, 3, 0, 20, tzinfo=utc)))
        self.assertFalse(cde.should_recheck([], dt.datetime(2026, 11, 3, 4, 20, tzinfo=utc)))
        self.assertTrue(cde.should_recheck(["--recheck"], dt.datetime(2026, 11, 3, 16, 0, tzinfo=utc)))

    def test_our_own_files_never_probed(self):
        self.assertEqual(cde.plan("/ai/traffic/deploy-status.json", None, True), "ours")
        self.assertEqual(cde.plan("/ai/", None, True), "probe")

    def test_drafted_still_counts_as_dead(self):
        src = open(os.path.join(ROOT, "ops", "check-dead-ends.py")).read()
        self.assertIn('if dead or any(r["verdict"] == "DRAFTED" for r in report):', src)


if __name__ == "__main__":
    unittest.main()
