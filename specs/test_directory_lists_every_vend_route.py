#!/usr/bin/env python3
"""Challenge #296: the /ai/ directory listed 22 of Vend's 23 paid routes; browser-agent (0.05 XNO) was missing.

The live terms (https://extract.paypercall.dev/.well-known/x402, read 10:2x UTC 2026-11-16, saved as
specs/fixtures/vend-x402-manifest-2026-11-16.json) list 24 resources: 23 GET routes and the POST balance top-up,
which the page tells buyers to skip. #295 fixed bounties.txt's price range, but the directory (83 outside clients on
11-16 by 11:07 UTC; tools.json read by 20) still showed no route above 0.0005 XNO, so a reader of the directory
alone never learnt that the most capable route exists, or that it costs 100 times the rest.

These laws hold every directory copy to the fixture: each GET route in the manifest appears with its URL and its
price, and the counts in tools.json match its callable_now list.

Run: python3 specs/test_directory_lists_every_vend_route.py
"""
import decimal
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "specs", "fixtures", "vend-x402-manifest-2026-11-16.json")
COPIES = ("published/aidirectory/index.html", "published/aidirectory.html",
          "published/aidirectory/llms.txt", "published/aidirectory-llms.txt", "published/aidirectory/tools.json")


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def routes():
    with open(FIXTURE) as f:
        m = json.load(f)
    out = {}
    for r in m["resources"]:
        if r["method"] != "GET":
            continue
        amount = decimal.Decimal(r["accepts"][0]["amount"]) / 10 ** 30
        out[r["url"]] = "%s XNO" % format(amount.normalize(), "f")
    return out


def tools():
    return json.loads(read("published/aidirectory/tools.json"))


class EveryRouteListed(unittest.TestCase):
    def test_fixture_has_the_route_that_was_missing(self):
        self.assertEqual(routes()["https://extract.paypercall.dev/api/v1/browser-agent"], "0.05 XNO")
        self.assertEqual(len(routes()), 23)

    def test_every_route_in_every_copy(self):
        for rel in COPIES:
            s = read(rel)
            for url in routes():
                self.assertIn(url, s, "%s does not list %s" % (rel, url))

    def test_tools_json_prices_match_the_manifest(self):
        listed = {e["url"]: e["price"] for e in tools()["callable_now"]}
        for url, price in routes().items():
            self.assertEqual(listed.get(url), price, url)

    def test_text_copies_show_the_price_next_to_the_route(self):
        for rel in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
            s = read(rel)
            for url, price in routes().items():
                self.assertIn("](%s) - %s - " % (url, price), s, "%s: %s" % (rel, url))
        for rel in ("published/aidirectory/index.html", "published/aidirectory.html"):
            s = read(rel)
            for url, price in routes().items():
                name = url.rsplit("/", 1)[1]
                self.assertIn('<a href="%s">%s</a></td><td class="p">%s</td>' % (url, name, price), s,
                              "%s: %s" % (rel, url))

    def test_counts_match_the_list(self):
        t = tools()
        self.assertEqual(t["counts"]["callable_now"], len(t["callable_now"]))
        self.assertEqual(t["counts"]["total"], t["counts"]["callable_now"] + t["counts"]["referenced"])
        n = t["counts"]["callable_now"]
        for rel in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"):
            self.assertIn("(%d callable now, " % n, read(rel))
        for rel in ("published/aidirectory/index.html", "published/aidirectory.html"):
            s = read(rel)
            self.assertIn("<b>%d</b>callable now" % n, s)
            self.assertIn("<b>%d</b>total" % t["counts"]["total"], s)
            self.assertIn("%d callable without signup" % n, s)


if __name__ == "__main__":
    unittest.main()
