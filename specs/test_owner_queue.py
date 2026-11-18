"""Challenge #210. Every fix waiting on the owner or the box is in one ranked queue that re-measures itself.

Law: each probe says APPLIED only on evidence, WAITING on the known-broken answer, and UNKNOWN (never APPLIED, never
WAITING) when nothing answered; every draft the queue names exists; drafts/OWNER-QUEUE.md lists every row.
"""
import importlib.util
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("oq", ROOT / "ops" / "check-owner-queue.py")
oq = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oq)

TERMS = {"x402Version": 2, "accepts": [{"amount": "1000000000000000000000000000", "asset": "XNO",
         "payTo": "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"}],
         "resource": {"description": "seller verification; pay 0.001 XNO to post an ask with a Nano bounty"}}


def stub(table):
    def f(url, method="GET", body=None, timeout=15, limit=400000):
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

    def test_api_index_row_needs_both_dead_ends_closed(self):
        """#229: row 6 is APPLIED only when /unstuck/api/ answers an index AND a GET on the echo answers 405."""
        index = json.dumps({"start_here": "https://172-86-112-140.sslip.io/bounties.txt"})
        both = stub({"/v1/echo": (405, "use POST"), "sslip.io/unstuck/api/": (200, index)})
        self.assertEqual(oq.p_box_dead_ends(both)[0], oq.APPLIED)
        only_echo = stub({"/v1/echo": (405, "use POST"), "sslip.io/unstuck/api/": (404, '{"error":"not found"}')})
        self.assertEqual(oq.p_box_dead_ends(only_echo)[0], oq.WAITING)
        html = stub({"/v1/echo": (405, "use POST"), "sslip.io/unstuck/api/": (200, "<!doctype html>")})
        self.assertEqual(oq.p_api_index(html)[0], oq.WAITING)
        self.assertIs(dict((r[0], r[6]) for r in oq.QUEUE)[6], oq.p_box_dead_ends)

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

    def test_the_treasury_is_treasury2_and_the_old_one_is_not_applied(self):
        """#273: both rows probed the dead old treasury; row 1 read WAITING for sellers paying treasury2."""
        self.assertEqual(oq.TREASURY, "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy")
        t2 = {"accepts": [{"asset": "XNO", "payTo": oq.TREASURY}]}
        self.assertEqual(oq.p_sellers(stub({"paypercall.dev": (200, json.dumps(t2))}))[0], oq.APPLIED)
        old = {"accepts": [{"asset": "XNO", "payTo": oq.OLD_TREASURY}]}
        self.assertEqual(oq.p_sellers(stub({"paypercall.dev": (200, json.dumps(old))}))[0], oq.WAITING)
        # the live shape: accepts under each resource; one stray payee among them is WAITING
        live = {"x402Version": 2, "resources": [{"url": "u1", "accepts": t2["accepts"]},
                                                {"url": "u2", "accepts": t2["accepts"]}]}
        self.assertEqual(oq.p_sellers(stub({"paypercall.dev": (200, json.dumps(live))}))[0], oq.APPLIED)
        live["resources"].append({"url": "u3", "accepts": old["accepts"]})
        self.assertEqual(oq.p_sellers(stub({"paypercall.dev": (200, json.dumps(live))}))[0], oq.WAITING)
        usdc = {"resources": [{"accepts": [{"asset": "USDC", "payTo": oq.TREASURY}]}]}
        self.assertEqual(oq.p_sellers(stub({"paypercall.dev": (200, json.dumps(usdc))}))[0], oq.WAITING)
        seen = []

        def f(url, method="GET", body=None, timeout=15, limit=400000):
            seen.append(body)
            return 200, json.dumps({"blocks": ""})
        self.assertEqual(oq.p_treasury_receive(f)[0], oq.APPLIED)
        self.assertEqual(seen[0]["account"], oq.TREASURY)

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

    def test_asks_list_names_how_to_post(self):
        """Challenge #244: row 14 is APPLIED only when the asks response names the POST route beside the list."""
        asks = [{"id": 626, "title": "x", "body": "POST /unstuck/api/ask inside an ask body does not count"}]
        today = json.dumps({"asks": asks, "counts": {"total": 64}})
        self.assertEqual(oq.p_asks_how_to_ask(stub({"/unstuck/api/asks": (200, today)}))[0], oq.WAITING)
        fixed = json.dumps({"asks": asks, "counts": {"total": 64},
                            "how_to_ask": "free: POST https://getunstuck.space/unstuck/api/ask {asker,title,body}"})
        self.assertEqual(oq.p_asks_how_to_ask(stub({"/unstuck/api/asks": (200, fixed)}))[0], oq.APPLIED)
        truncated = today[:40]
        self.assertEqual(oq.p_asks_how_to_ask(stub({"/unstuck/api/asks": (200, truncated)}))[0], oq.UNKNOWN)
        self.assertEqual(oq.p_asks_how_to_ask(stub({"/unstuck/api/asks": (502, "bad gateway")}))[0], oq.UNKNOWN)
        self.assertEqual({r["rank"]: r["state"] for r in oq.run(stub({}))}[14], oq.UNKNOWN)

    def test_root_llms_names_the_paid_job(self):
        """Challenge #271: row 15 is APPLIED only when the box root's llms.txt names a job id, no longer offers the
        referral bounty, and a plain GET / answers anything but 426."""
        today = "# The Unowned Rail\n> ... and earn a bounty for bringing another agent.\n- [Bounties](...)"
        draft = (ROOT / "drafts" / "box-root-llms-paid-job.md").read_text()
        fixed = draft.split("```\n", 2)[1]
        self.assertIn("job-20261113-001", fixed)
        self.assertNotIn("bounty for bringing another agent", fixed)
        ws = (426, "websocket upgrade required")
        self.assertEqual(oq.p_root_llms_paid_job(stub({"/llms.txt": (200, today), "sslip.io/": ws}))[0], oq.WAITING)
        self.assertEqual(oq.p_root_llms_paid_job(stub({"/llms.txt": (200, fixed), "sslip.io/": ws}))[0], oq.WAITING)
        self.assertEqual(oq.p_root_llms_paid_job(stub({"/llms.txt": (200, fixed), "sslip.io/": (302, "")}))[0],
                         oq.APPLIED)
        self.assertEqual(oq.p_root_llms_paid_job(stub({"/llms.txt": (200, today), "sslip.io/": (302, "")}))[0],
                         oq.WAITING)
        self.assertEqual(oq.p_root_llms_paid_job(stub({"/llms.txt": (502, "")}))[0], oq.UNKNOWN)
        self.assertEqual({r["rank"]: r["state"] for r in oq.run(stub({}))}[15], oq.UNKNOWN)

    def test_heads_stop_selling_verdicts_while_seats_are_closed(self):
        """Challenge #308: row 16 is WAITING while bounties.txt says the seats are CLOSED and any of try-nano,
        agent.json or the homepage still offers verdict selling; APPLIED when none does or the seats reopen."""
        live = (ROOT / "published" / "bounties.txt").read_text()[:8000]
        self.assertTrue(oq.seats_closed(live), "bounties.txt's box no longer says CLOSED: re-read row 16")
        reopened = " RIGHT NOW\n   PAID WORK: 3 VERDICT SEATS OPEN until 12-01\n 1. THE REWARDS\n CLOSED later"
        self.assertFalse(oq.seats_closed(reopened))
        draft = (ROOT / "drafts" / "network-heads-closed-seats.md").read_text()
        new_texts = re.findall(r"(?:NEW|becomes)\s+`([^`]*)`", draft.split("## The change", 1)[1])
        self.assertGreaterEqual(len(new_texts), 4)
        for text in new_texts:
            self.assertIsNone(oq.SELL_VERDICT.search(text), text)
        old_try = '{"what":"... take listed jobs, sell verdicts, post what you are stuck on"}'
        new_try = '{"what":"... take a listed job or an evaluator seat when bounties.txt section 9 lists one open"}'
        home_old = "<h2>How a job is judged</h2><p>Evaluators sell verdicts.</p><h3>Sell a verdict</h3>"
        home_new = "<p>Evaluators are paid per verdict, while a job lists seats.</p><h3>Judge a delivery</h3>"
        agent_new = '{"description":"Take listed jobs and evaluator seats when bounties.txt section 9 lists one open"}'

        def table(try_nano, agent, home, bounties=(200, live)):
            return {"bounties.txt": bounties, "try-nano": try_nano, "agent.json": agent, "getunstuck.space/": home}

        self.assertEqual(oq.p_heads_closed_seats(stub(table((200, old_try), (200, agent_new), (200, home_new)))),
                         (oq.WAITING, "seats closed, still offering verdict selling: try-nano"))
        self.assertEqual(oq.p_heads_closed_seats(stub(table((200, new_try), (200, agent_new), (200, home_old))))[0],
                         oq.WAITING)
        self.assertEqual(oq.p_heads_closed_seats(stub(table((200, new_try), (200, agent_new), (200, home_new))))[0],
                         oq.APPLIED)
        self.assertEqual(oq.p_heads_closed_seats(stub(table((200, old_try), (200, agent_new), (200, home_old),
                                                            (200, reopened))))[0], oq.APPLIED)
        self.assertEqual(oq.p_heads_closed_seats(stub(table((502, ""), (200, agent_new), (200, home_new))))[0],
                         oq.UNKNOWN)
        self.assertEqual(oq.p_heads_closed_seats(stub(table((200, new_try), (200, agent_new), (200, home_new),
                                                            (200, "Bad Gateway"))))[0], oq.UNKNOWN)
        self.assertEqual({r["rank"]: r["state"] for r in oq.run(stub({}))}[16], oq.UNKNOWN)

    def test_every_named_draft_exists_and_the_page_lists_every_row(self):
        page = (ROOT / "drafts" / "OWNER-QUEUE.md").read_text()
        for rank, who, action, unblocks, draft, ch, probe in oq.QUEUE:
            self.assertTrue((ROOT / draft.split(" ")[0]).exists(), draft)
            self.assertIn(action, page)


if __name__ == "__main__":
    unittest.main()
