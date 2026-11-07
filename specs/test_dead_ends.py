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
        self.assertIn("path /unstuck/api/\n", caddy)  # #229: /unstuck/api (no slash) already answers 200
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

    def _caddy(self):
        with open(os.path.join(ROOT, "drafts", "box-dead-ends.md")) as f:
            d = f.read()
        return d[d.index("```\n") + 4:d.index("```", d.index("```\n") + 4)]

    def test_caddy_block_is_well_formed(self):
        """#229: the #204 edit left a handle holding matcher lines and a matcher defined twice, so
        `caddy validate` rejected the whole draft. Every matcher is defined once and holds only matcher
        lines; every handle names a defined matcher and holds no matcher lines; braces balance."""
        import re
        caddy = self._caddy()
        blocks = re.findall(r"^(@\w+|handle @\w+) \{\n(.*?)^\}$", caddy, re.S | re.M)
        matcher_words = {"path", "method", "not", "header_regexp", "path_regexp", "header"}
        defined = []
        for head, body in blocks:
            words = [l.split()[0] for l in body.splitlines() if l.strip()]
            if head.startswith("@"):
                defined.append(head)
                self.assertTrue(words and set(words) <= matcher_words, head + " holds " + str(words))
                self.assertNotIn("respond", words)
            else:
                name = head.split()[1]
                self.assertIn(name, defined, head + " names a matcher not defined above it")
                self.assertFalse({"path", "method", "not"} & set(words), head + " holds matcher lines")
                self.assertIn("respond", words)
        self.assertEqual(len(defined), len(set(defined)), "a matcher is defined twice: " + str(defined))
        handled = [h.split()[1] for h, _ in blocks if h.startswith("handle")]
        self.assertEqual(len(handled), len(set(handled)), "a matcher is handled twice: " + str(handled))
        inline = re.findall(r"^(@\w+) (?!\{)", caddy, re.M)  # one-line matchers, e.g. @asks_by_id path_regexp ...
        self.assertEqual(len(defined + inline), len(set(defined + inline)), "a matcher is defined twice")
        for m in re.findall(r"^(?:redir|handle) (@\w+)", caddy, re.M):
            self.assertIn(m, defined + inline, m + " is used but never defined")
        depth = 0
        for line in caddy.splitlines():
            if "`" in line:
                continue  # a respond body's braces are JSON, not Caddy
            depth += line.count("{") - line.count("}")
            self.assertGreaterEqual(depth, 0)
        self.assertEqual(depth, 0)

    def test_api_index_answers_the_slash_with_json(self):
        """#229: /unstuck/api/ was the most-requested path on 11-07 (59 outside clients) and 404s."""
        import json
        caddy = self._caddy()
        i = caddy.index("@api_index {")
        self.assertIn("path /unstuck/api/\n", caddy[i:caddy.index("}", i)])
        h = caddy.index("handle @api_index {")
        handler = caddy[h:caddy.index("\n}\n", h)]
        body = handler[handler.index("respond `") + 9:handler.rindex("`")]
        index = json.loads(body)
        self.assertEqual(index["start_here"], "https://172-86-112-140.sslip.io/bounties.txt")
        self.assertIn("GET /unstuck/api/asks", index["endpoints"])
        self.assertNotIn("try-nano", index["start_here"])
        self.assertTrue(handler.rstrip().endswith("200"))

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
