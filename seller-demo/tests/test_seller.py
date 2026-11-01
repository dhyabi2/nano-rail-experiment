"""Laws for the serverless Nano seller. Run: python3 -m unittest discover -s seller-demo/tests -v
No network: the node is a stub passed in."""
import base64, io, json, os, sys, unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "api"))
import _nano_seller as s  # noqa: E402

SELLER = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
OTHER = "nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3"
H1 = "B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F"
H2 = "A" * 64
NOW = 1790150200
PRICE = s.PRICE_RAW


def block(to=SELLER, amount=PRICE, ts=NOW - 10, confirmed="true", subtype="send"):
    return {"block_account": OTHER, "amount": str(amount), "confirmed": confirmed, "subtype": subtype,
            "local_timestamp": str(ts), "contents": {"type": "state", "link_as_account": to}}


def seller(blocks, nodes=("n1",), fail=False):
    def call(url, body):
        if fail:
            raise OSError("down")
        return blocks.get(body["hash"], {"error": "Block not found"})
    return s.Seller(SELLER, nodes=list(nodes), call=call, now=lambda: NOW)


class Laws(unittest.TestCase):
    def test_price_is_derived_not_restated(self):
        self.assertEqual(s.PRICE_RAW, 10 ** 30 // 100000)  # 0.00001 XNO

    def test_missing_proof_gets_402_with_nano_accepts(self):
        code, body, hdr = seller({}).respond(None, {})
        self.assertEqual(code, 402)
        a = body["accepts"][0]
        self.assertEqual((a["scheme"], a["network"], a["asset"], a["payTo"]), ("exact", "nano:mainnet", "XNO", SELLER))
        self.assertEqual(a["amount"], str(PRICE))
        self.assertEqual(body["x402Version"], 2)
        self.assertEqual(json.loads(base64.b64decode(hdr["payment-required"]))["accepts"], body["accepts"])

    def test_garbage_proof_is_402(self):
        code, body, _ = seller({}).respond("not a hash", {})
        self.assertEqual((code, body["reason"]), (402, "invalid_payload"))

    def test_good_payment_returns_result(self):
        code, body, _ = seller({H1: block()}).respond(H1, {"account": [SELLER]})
        self.assertEqual(code, 200)
        self.assertEqual(body["receipt"]["block_hash"], H1)
        self.assertTrue(body["result"]["account_valid"])

    def test_overpay_accepted(self):
        self.assertEqual(seller({H1: block(amount=PRICE * 3)}).respond(H1, {})[0], 200)

    def test_wrong_amount_underpay(self):
        code, body, _ = seller({H1: block(amount=PRICE - 1)}).respond(H1, {})
        self.assertEqual((code, body["reason"]), (402, "wrong_amount"))

    def test_wrong_destination(self):
        code, body, _ = seller({H1: block(to=OTHER)}).respond(H1, {})
        self.assertEqual((code, body["reason"]), (402, "wrong_payee"))

    def test_not_a_send(self):
        self.assertEqual(seller({H1: block(subtype="receive")}).respond(H1, {})[1]["reason"], "not_a_send")

    def test_unknown_block(self):
        self.assertEqual(seller({}).respond(H1, {})[1]["reason"], "block_not_found")

    def test_too_old(self):
        self.assertEqual(seller({H1: block(ts=NOW - 100000)}).respond(H1, {})[1]["reason"], "payment_too_old")

    def test_replay_refused(self):
        sv = seller({H1: block()})
        self.assertEqual(sv.respond(H1, {})[0], 200)
        code, body, _ = sv.respond(H1.lower(), {})
        self.assertEqual((code, body["reason"]), (402, "payment_already_redeemed"))

    def test_refused_payment_is_not_burned(self):
        blocks = {H1: block(confirmed="false")}
        sv = seller(blocks)
        self.assertEqual(sv.respond(H1, {})[0], 503)
        blocks[H1] = block()
        self.assertEqual(sv.respond(H1, {})[0], 200)

    def test_pending_is_503_not_402(self):
        code, body, hdr = seller({H1: block(confirmed="false")}).respond(H1, {})
        self.assertEqual((code, body["retryable"], hdr["Retry-After"]), (503, True, "5"))
        self.assertEqual(seller({}, fail=True).respond(H1, {})[0], 503)

    def test_proof_forms(self):
        b64 = base64.b64encode(json.dumps({"scheme": "exact", "network": "nano:mainnet",
                                           "payload": {"blockHash": H2}}).encode()).decode()
        self.assertEqual(s.payment_hash(b64), H2)
        self.assertEqual(s.payment_hash(json.dumps({"payload": {"hash": H2}})), H2)

    def test_no_secrets_anywhere(self):
        src = open(os.path.join(HERE, "..", "api", "_nano_seller.py")).read().lower()
        for bad in ("seed", "private_key", "privkey", "secret_key", "sign("):
            self.assertNotIn(bad, src.replace("seeds", ""))

    def test_address_check(self):
        self.assertTrue(s.check_account(SELLER)["valid"])
        bad = SELLER[:-1] + ("a" if SELLER[-1] != "a" else "b")
        self.assertFalse(s.check_account(bad)["valid"])

    def test_missing_env_is_refused(self):
        with self.assertRaises(ValueError):
            s.Seller("", nodes=["n"])
        with self.assertRaises(ValueError):
            s.Seller("nano_notanaddress", nodes=["n"])


class Http(unittest.TestCase):
    def test_handler_402_over_http(self):
        import threading, urllib.request, urllib.error
        from http.server import HTTPServer
        os.environ["SELLER_NANO_ACCOUNT"] = SELLER
        import paid
        srv = HTTPServer(("127.0.0.1", 0), paid.handler)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            urllib.request.urlopen("http://127.0.0.1:%d/api/paid" % srv.server_port)
            self.fail("expected 402")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 402)
            self.assertEqual(json.loads(e.read())["accepts"][0]["network"], "nano:mainnet")
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
