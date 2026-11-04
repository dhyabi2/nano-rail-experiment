"""Challenge #210. Every fix waiting on the owner or the box is in one ranked queue that re-measures itself.

Law: each probe says APPLIED only on evidence, WAITING on the known-broken answer, and UNKNOWN (never APPLIED, never
WAITING) when nothing answered; every draft the queue names exists; drafts/OWNER-QUEUE.md lists every row.
"""
import importlib.util
import json
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("oq", ROOT / "ops" / "check-owner-queue.py")
oq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oq)

TERMS = {"x402Version": 2, "accepts": [{"amount": "1000000000000000000000000000", "asset": "XNO",
         "payTo": "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"}],
         "resource": {"description": "seller verification; pay 0.001 XNO to post an ask with a Nano bounty"}}


def stub(table):
    def f(url, method="GET", body=None, timeout=15):
        for key, ans in table.items():
            if key in url:
                if isinstance(ans, Exception):
                    raise ans
                return ans
        raise OSError("no answer")
    return f


class OwnerQueue(unittest.TestCase):
    def test_todays_broken_answers_read_waiting(self):
        f = stub({"paypercall.dev": OSError("timeout"),
                  "rpc.nano.to": (200, json.dumps({"blocks": {"5EE71904AA": {"amount": "1"}}})),
                  "/llms.txt": (200, "accept body {acceptedBy, answerId}"),
                  "/v1/x402": (200, json.dumps(TERMS)),
                  "/v1/echo": (404, '{"error":"not found"}')})
        self.assertEqual(oq.p_sellers(f)[0], oq.WAITING)
        self.assertEqual(oq.p_treasury_receive(f)[0], oq.WAITING)
        self.assertEqual(oq.p_accept_token(f)[0], oq.WAITING)
        self.assertEqual(oq.p_echo_description(f)[0], oq.WAITING)
        self.assertEqual(oq.p_routes_link_bounties(f)[0], oq.WAITING)
        self.assertEqual(oq.p_echo_get(f)[0], oq.WAITING)

    def test_fixed_answers_read_applied(self):
        good = {"accepts": [{"asset": "XNO", "payTo": oq.TREASURY}]}
        terms = dict(TERMS, resource={"description": "echo call, 0.001 XNO"})
        f = stub({"paypercall.dev": (200, json.dumps(good)),
                  "rpc.nano.to": (200, json.dumps({"blocks": ""})),
                  "/llms.txt": (200, "keep accept_token; see /bounties.txt"),
                  "/v1/x402": (200, json.dumps(terms)),
                  "/v1/echo": (405, "use POST")})
        for p in (oq.p_sellers, oq.p_treasury_receive, oq.p_accept_token, oq.p_echo_description,
                  oq.p_routes_link_bounties, oq.p_echo_get):
            self.assertEqual(p(f)[0], oq.APPLIED, p.__name__)

    def test_a_seller_paying_someone_else_is_never_applied(self):
        bad = {"accepts": [{"asset": "XNO", "payTo": "nano_3other"}]}
        self.assertEqual(oq.p_sellers(stub({"paypercall.dev": (200, json.dumps(bad))}))[0], oq.WAITING)

    def test_silence_is_unknown_not_a_verdict(self):
        rows = oq.run(stub({}))
        by = {r["rank"]: r["state"] for r in rows}
        # the RPC and the guides did not answer: those rows cannot say APPLIED
        for rank in (2, 3, 4, 5, 6, 8, 10, 11):
            self.assertEqual(by[rank], oq.UNKNOWN, rank)
        self.assertNotEqual(oq.exit_code(rows), 0)

    def test_wellknown_terms_type_is_measured(self):
        """Challenge #213: row 13 reads the served Content-Type, not just the body."""
        def typed(status, body, ctype):
            def f(url, method="GET", body_=None, timeout=15, want_type=False):
                self.assertTrue(want_type)
                self.assertTrue(url.endswith("/.well-known/x402"))
                return status, body, ctype
            return f
        body = json.dumps(TERMS)
        self.assertEqual(oq.p_wellknown_json(typed(200, body, "application/octet-stream"))[0], oq.WAITING)
        self.assertEqual(oq.p_wellknown_json(typed(200, body, ""))[0], oq.WAITING)
        self.assertEqual(oq.p_wellknown_json(typed(200, body, "application/json; charset=utf-8"))[0], oq.APPLIED)
        self.assertEqual(oq.p_wellknown_json(typed(200, "<html>", "application/json"))[0], oq.UNKNOWN)
        self.assertEqual(oq.p_wellknown_json(typed(502, "", "text/html"))[0], oq.UNKNOWN)
        rows = oq.run(stub({}))
        self.assertEqual({r["rank"]: r["state"] for r in rows}[13], oq.UNKNOWN)

    def test_every_named_draft_exists_and_the_page_lists_every_row(self):
        page = (ROOT / "drafts" / "OWNER-QUEUE.md").read_text()
        for rank, who, action, unblocks, draft, ch, probe in oq.QUEUE:
            self.assertTrue((ROOT / draft.split(" ")[0]).exists(), draft)
            self.assertIn(action, page)


if __name__ == "__main__":
    unittest.main()
