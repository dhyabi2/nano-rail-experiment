#!/usr/bin/env python3
"""Laws for tools/nano-x402-facilitator/facilitator.py (challenge #175).

A facilitator a seller points accepts[] at must accept exactly one thing: a confirmed, fresh send
of the exact amount to the seller's payTo, settled once. It must hold no key and send nothing.

Fixture: the real public send block 5EE71904... (10 XNO to the treasury, block_info read from
rpc.nano.to 2026-10-28 16:3x UTC). It is a public block hash, not a secret.

Run: python3 specs/test_nano_x402_facilitator.py
"""
import base64
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
import threading
import unittest
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, "tools", "nano-x402-facilitator", "facilitator.py")
spec = importlib.util.spec_from_file_location("fac", PATH)
fac = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fac)

H = "5EE719043E7CF1F276DF2DA475440A85652F80EDCA5F469E8280E9D4EAA70E44"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
PAYER = "nano_3kaf7r9n3ixpjao14z1h18i7mjdkzb55k74qka67dngpiswaadyiu3otq7pp"
TEN = "10000000000000000000000000000000"
SEEN = 1792312097
INFO = {
    "block_account": PAYER, "amount": TEN, "local_timestamp": str(SEEN), "confirmed": "true",
    "subtype": "send",
    "contents": {"type": "state", "account": PAYER, "link_as_account": TREASURY},
}
REQ = {"scheme": "exact", "network": "nano:mainnet", "payTo": TREASURY, "amount": TEN,
       "maxTimeoutSeconds": 300}


def body(payload=None, **req):
    r = dict(REQ, **req)
    return {"paymentPayload": payload if payload is not None else
            {"x402Version": 1, "scheme": "exact", "network": "nano:mainnet", "payload": {"hash": H}},
            "paymentRequirements": r}


class Nodes:
    """Stub nodes: url -> block_info answer (dict) or an exception to raise."""

    def __init__(self, answers):
        self.answers, self.calls = answers, []

    def __call__(self, url, req):
        self.calls.append((url, req))
        a = self.answers[url]
        if isinstance(a, Exception):
            raise a
        return copy.deepcopy(a)


def make(answers=None, quorum=1, store=None, now=SEEN + 30):
    answers = answers or {"n1": INFO}
    nodes = Nodes(answers)
    return fac.Facilitator(list(answers), store or fac.Store(None), quorum, nodes, lambda: now), nodes


class Laws(unittest.TestCase):
    def test_a_good_payment_verifies_and_names_the_payer(self):
        f, nodes = make()
        self.assertEqual(f.verify(body()), {"isValid": True, "invalidReason": None, "payer": PAYER})
        self.assertEqual(nodes.calls[0][1], {"action": "block_info", "json_block": "true", "hash": H})

    def test_settle_succeeds_once_and_a_replay_fails(self):
        f, _ = make()
        s = f.settle(body())
        self.assertTrue(s["success"])
        self.assertEqual((s["transaction"], s["network"], s["payer"]), (H, "nano:mainnet", PAYER))
        again = f.settle(body())
        self.assertFalse(again["success"])
        self.assertEqual(again["errorReason"], "payment_already_redeemed")
        self.assertEqual(f.verify(body())["invalidReason"], "payment_already_redeemed")

    def test_redeemed_hashes_survive_a_restart(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "redeemed.json")
            f, _ = make(store=fac.Store(p))
            self.assertTrue(f.settle(body())["success"])
            f2, _ = make(store=fac.Store(p))
            self.assertEqual(f2.verify(body())["invalidReason"], "payment_already_redeemed")

    def test_only_the_exact_payment_is_accepted(self):
        cases = [
            (dict(INFO, amount=str(int(TEN) - 1)), "wrong_amount"),
            (dict(INFO, amount=str(int(TEN) + 1)), "wrong_amount"),
            (dict(INFO, contents=dict(INFO["contents"], link_as_account=PAYER)), "wrong_payee"),
            (dict(INFO, subtype="receive"), "not_a_send"),
            (dict(INFO, confirmed="false"), "not_confirmed"),
            (dict(INFO, local_timestamp="0"), "payment_age_unknown"),
        ]
        for info, reason in cases:
            f, _ = make({"n1": info})
            self.assertEqual(f.verify(body())["invalidReason"], reason)
            self.assertFalse(f.settle(body())["success"], reason)

    def test_an_old_payment_to_the_same_payee_cannot_be_claimed(self):
        f, _ = make(now=SEEN + 301)
        self.assertEqual(f.verify(body())["invalidReason"], "payment_too_old")
        f, _ = make(now=SEEN + 599)  # 600 s is the default when maxTimeoutSeconds is absent
        r = dict(REQ)
        del r["maxTimeoutSeconds"]
        self.assertTrue(f.verify({"paymentPayload": H, "paymentRequirements": r})["isValid"])

    def test_requirements_it_cannot_honour_are_refused_before_any_node_call(self):
        for req, reason in [({"network": "base"}, "invalid_network"),
                            ({"scheme": "upto"}, "unsupported_scheme"),
                            ({"payTo": "0xabc"}, "invalid_pay_to"),
                            ({"amount": "0"}, "invalid_amount_required"),
                            ({"amount": "1.5"}, "invalid_amount_required")]:
            f, nodes = make()
            self.assertEqual(f.verify(body(**req))["invalidReason"], reason)
            self.assertEqual(nodes.calls, [])
        f, nodes = make()
        self.assertEqual(f.verify(body({"payload": {"hash": "xyz"}}))["invalidReason"], "invalid_payload")

    def test_only_ascii_digits_are_an_amount_and_a_timeout(self):
        # challenge #191: str.isdigit() took "\u00b2" (int() then raised, the connection dropped) and
        # "\u0663\u0660" (Arabic-Indic 30); a seller's malformed requirement must be a named refusal.
        for req, reason in [({"amount": "\u00b2"}, "invalid_amount_required"),
                            ({"amount": "\u0661\u0660"}, "invalid_amount_required"),
                            ({"amount": " 10"}, "invalid_amount_required"),
                            ({"amount": "1e30"}, "invalid_amount_required"),
                            ({"maxTimeoutSeconds": "\u00b2"}, "invalid_max_timeout"),
                            ({"maxTimeoutSeconds": "abc"}, "invalid_max_timeout"),
                            ({"maxTimeoutSeconds": -5}, "invalid_max_timeout"),
                            ({"maxTimeoutSeconds": True}, "invalid_max_timeout")]:
            f, nodes = make()
            self.assertEqual(f.verify(body(**req))["invalidReason"], reason, req)
            self.assertEqual(nodes.calls, [], req)

    def test_leading_zeros_name_the_same_amount(self):
        f, _ = make()
        self.assertTrue(f.verify(body(amount="000" + TEN))["isValid"])
        f, _ = make()
        self.assertTrue(f.verify(body(maxTimeoutSeconds="300"))["isValid"])

    def test_http_never_drops_a_malformed_requirement(self):
        f, _ = make()
        srv = fac.ThreadingHTTPServer(("127.0.0.1", 0), fac.make_handler(f))
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            url = "http://127.0.0.1:%d/verify" % srv.server_address[1]
            data = json.dumps(body(amount="\u00b2")).encode()
            r = urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST"), timeout=5)
            self.assertEqual(json.loads(r.read())["invalidReason"], "invalid_amount_required")
        finally:
            srv.shutdown()
            srv.server_close()

    def test_v1_amount_field_and_every_payload_shape(self):
        r = dict(REQ)
        r["maxAmountRequired"] = r.pop("amount")
        b64 = base64.b64encode(json.dumps({"x402Version": 1, "payload": {"hash": H.lower()}}).encode()).decode()
        for pay in [H, H.lower(), {"payload": H}, {"payload": {"block_hash": H}}, b64]:
            f, _ = make()
            self.assertTrue(f.verify({"paymentPayload": pay, "paymentRequirements": r})["isValid"], pay)

    def test_every_answering_node_must_agree(self):
        f, _ = make({"n1": INFO, "n2": dict(INFO, amount="1")})
        self.assertEqual(f.verify(body())["invalidReason"], "wrong_amount")
        f, _ = make({"n1": INFO, "n2": {"error": "Block not found"}})
        self.assertEqual(f.verify(body())["invalidReason"], "block_not_found")

    def test_quorum_counts_only_nodes_that_answered(self):
        f, _ = make({"n1": INFO, "n2": OSError("down")}, quorum=2)
        self.assertEqual(f.verify(body())["invalidReason"], "nodes_unreachable")
        f, _ = make({"n1": INFO, "n2": OSError("down")}, quorum=1)
        self.assertTrue(f.verify(body())["isValid"])
        f, _ = make({"n1": OSError("down")})
        self.assertFalse(f.settle(body())["success"])

    def test_a_node_that_said_nothing_usable_is_not_an_answer(self):
        # challenge #194: a non-dict reply, or a 200 that is not a block_info reply (a quota
        # notice without "error"), must not become not_a_send / node_answer_unreadable.
        for junk in (["x"], "rate limited", {"message": "Free public RPC limit reached"}):
            f, _ = make({"n1": junk})
            self.assertEqual(f.verify(body())["invalidReason"], "nodes_unreachable", junk)
            f, _ = make({"n1": junk, "n2": INFO})
            self.assertTrue(f.verify(body())["isValid"], junk)

    def test_a_final_refusal_wins_over_a_pending_one(self):
        f, _ = make({"n1": dict(INFO, confirmed="false"), "n2": dict(INFO, amount="1")})
        self.assertEqual(f.verify(body())["invalidReason"], "wrong_amount")
        f, _ = make({"n1": dict(INFO, confirmed="false"), "n2": INFO})
        self.assertEqual(f.verify(body())["invalidReason"], "not_confirmed")

    def test_pending_is_a_503_never_a_200_that_asks_a_payer_to_pay_again(self):
        # challenge #194 (after #189, #193): an x402 seller turns a 200 isValid:false into a new
        # 402. Unreachable nodes and an unconfirmed send are not known to be unpaid, so the HTTP
        # answer is 503 + Retry-After + retryable, and settle records nothing.
        cases = [({"n1": OSError("down")}, "nodes_unreachable"),
                 ({"n1": dict(INFO, confirmed="false")}, "not_confirmed")]
        for answers, reason in cases:
            f, _ = make(answers)
            srv = fac.ThreadingHTTPServer(("127.0.0.1", 0), fac.make_handler(f))
            threading.Thread(target=srv.serve_forever, daemon=True).start()
            base = "http://127.0.0.1:%d" % srv.server_address[1]
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            try:
                for route, key in (("/verify", "invalidReason"), ("/settle", "errorReason")):
                    with self.assertRaises(urllib.error.HTTPError) as cm:
                        opener.open(urllib.request.Request(base + route, data=json.dumps(body()).encode(),
                                                           headers={"Content-Type": "application/json"}))
                    e = cm.exception
                    self.assertEqual(e.code, 503, (reason, route))
                    self.assertEqual(e.headers.get("Retry-After"), fac.RETRY_AFTER)
                    out = json.loads(e.read())
                    self.assertEqual(out[key], reason)
                    self.assertTrue(out["retryable"])
                self.assertFalse(f.store.has(H))
            finally:
                srv.shutdown()
                srv.server_close()
        # a final refusal stays a 200 with a reason: the seller may answer that one 402
        f, _ = make({"n1": dict(INFO, amount="1")})
        srv = fac.ThreadingHTTPServer(("127.0.0.1", 0), fac.make_handler(f))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            r = opener.open(urllib.request.Request("http://127.0.0.1:%d/verify" % srv.server_address[1],
                                                   data=json.dumps(body()).encode()))
            self.assertEqual(r.status, 200)
            self.assertEqual(json.loads(r.read())["invalidReason"], "wrong_amount")
        finally:
            srv.shutdown()
            srv.server_close()

    def test_it_holds_no_key_and_sends_nothing(self):
        with open(PATH) as fh:
            src = fh.read()
        for word in ("seed", "private_key", "\"process\"", "'process'", "send_block", "block_create", "\"sign\""):
            self.assertNotIn(word, src)
        f, nodes = make()
        f.settle(body())
        self.assertEqual({c[1]["action"] for c in nodes.calls}, {"block_info"})

    def test_http_interface(self):
        f, _ = make()
        srv = fac.ThreadingHTTPServer(("127.0.0.1", 0), fac.make_handler(f))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % srv.server_address[1]
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            sup = json.loads(opener.open(base + "/supported").read())
            self.assertIn({"x402Version": 1, "scheme": "exact", "network": "nano:mainnet"}, sup["kinds"])
            post = lambda p: json.loads(opener.open(urllib.request.Request(
                base + p, data=json.dumps(body()).encode(), headers={"Content-Type": "application/json"})).read())
            self.assertTrue(post("/verify")["isValid"])
            self.assertTrue(post("/settle")["success"])
            self.assertFalse(post("/settle")["success"])
        finally:
            srv.shutdown()
            srv.server_close()

    def test_a_stranger_can_read_what_it_is_and_its_source(self):
        # challenge #176: the repository is private, so the root and /source are the only
        # description and the only code a seller can read before pointing accepts[] here.
        f, nodes = make()
        srv = fac.ThreadingHTTPServer(("127.0.0.1", 0), fac.make_handler(f))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % srv.server_address[1]
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            r = opener.open(base + "/")
            idx = json.loads(r.read())
            self.assertEqual(r.headers["Access-Control-Allow-Origin"], "*")
            self.assertIs(idx["holds_key"], False)
            self.assertIs(idx["sends"], False)
            self.assertEqual(idx["network"], "nano:mainnet")
            self.assertIn("POST verify", idx["routes"])
            r = opener.open(base + "/source")
            src = r.read()
            with open(PATH, "rb") as fh:
                self.assertEqual(src, fh.read())
            self.assertTrue(r.headers["Content-Type"].startswith("text/plain"))
            self.assertEqual(hashlib.sha256(src).hexdigest(), idx["source_sha256"])
            self.assertEqual(r.headers["X-Source-SHA256"], idx["source_sha256"])
            with self.assertRaises(urllib.error.HTTPError) as e:
                opener.open(base + "/nope")
            self.assertIn("/source", json.loads(e.exception.read())["routes"])
            self.assertEqual(nodes.calls, [])  # describing itself reads no node

            chk = load_checker()
            code, lines = chk.check(base, opener=opener, main_source=PATH)
            self.assertEqual(code, 0, lines)
            self.assertTrue(any("MATCHES" in l for l in lines), lines)
            code, lines = chk.check(base, opener=opener, main_source=__file__)
            self.assertEqual(code, 0)
            self.assertTrue(any("DIFFERS FROM" in l for l in lines), lines)
        finally:
            srv.shutdown()
            srv.server_close()

    def test_the_checker_says_not_hosted_when_nothing_or_something_else_answers(self):
        chk = load_checker()
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        code, lines = chk.check("http://127.0.0.1:9", opener=opener)
        self.assertEqual(code, 2)
        self.assertIn("NOT HOSTED", lines[0])


def load_checker():
    sp = importlib.util.spec_from_file_location(
        "chk", os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "ops", "check-facilitator.py"))
    m = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(m)
    return m


if __name__ == "__main__":
    unittest.main()
