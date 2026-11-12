#!/usr/bin/env python3
"""Law for challenge #258: every paypercall.dev route a published file names is one the sellers' manifests list.

Measured 08:2x UTC 2026-11-12: bounties.txt section 4 sent a reader to "semantic search at
https://search.paypercall.dev/api/v1/neural-search". That path answers 404 to GET and POST, and the search seller's
/.well-known/x402 lists exactly one route, /api/v1/web-search. Every other route named in published/ (23 of 24) is
in the five manifests. The set below is those manifests' routes as read at that time; when a seller adds a route,
add it here with the date it was read.

Run: python3 specs/test_published_paypercall_routes_exist.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Union of the routes in extract, search, domain, check, geoip .paypercall.dev/.well-known/x402, read 2026-11-12 08:2x UTC.
MANIFEST_ROUTES = {
    "https://check.paypercall.dev/api/v1/check-link",
    "https://domain.paypercall.dev/api/v1/domain-info",
    "https://geoip.paypercall.dev/api/v1/geoip",
    "https://search.paypercall.dev/api/v1/web-search",
} | {"https://extract.paypercall.dev/api/v1/" + p for p in (
    "address-verdict", "ai-jobs", "arxiv-paper", "balance/top-up", "batch-status", "delivery-proof", "extract",
    "hn-news", "links", "mcp-find", "meta", "nano-info", "pdf-extract", "render", "screenshot", "select", "status",
    "table", "wiki-summary", "youtube-transcript")}

ROUTE = re.compile(r"https://[a-z]+\.paypercall\.dev/api/v1/[a-z0-9/-]+")


def named_routes(text):
    return {m.rstrip("/") for m in ROUTE.findall(text)}


def published_texts():
    out = {}
    for dirpath, _, files in os.walk(os.path.join(ROOT, "published")):
        for name in files:
            if name.endswith((".txt", ".html", ".json")):
                path = os.path.join(dirpath, name)
                with open(path, encoding="utf-8", errors="replace") as f:
                    out[os.path.relpath(path, ROOT)] = f.read()
    return out


class PublishedRoutesExist(unittest.TestCase):
    def test_every_named_route_is_in_a_manifest(self):
        bad = []
        for rel, text in sorted(published_texts().items()):
            for route in sorted(named_routes(text) - MANIFEST_ROUTES):
                bad.append("%s names %s" % (rel, route))
        self.assertEqual(bad, [], "routes no seller lists:\n" + "\n".join(bad))

    def test_bounties_names_the_live_search_route(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        self.assertIn("https://search.paypercall.dev/api/v1/web-search", txt)
        self.assertNotIn("semantic search at", txt)

    def test_law_fails_on_the_old_line(self):
        old = "semantic search at\n                    https://search.paypercall.dev/api/v1/neural-search."
        self.assertEqual(named_routes(old) - MANIFEST_ROUTES,
                         {"https://search.paypercall.dev/api/v1/neural-search"})


if __name__ == "__main__":
    unittest.main()
