#!/usr/bin/env python3
"""A keyless x402 facilitator for Nano (XNO): /supported, /verify, /settle.

Why this exists (challenge #175): on 2026-10-28 11:43 UTC inkassat0r4, an x402 seller
that settles USDC on Base through a facilitator, told us exactly what gates adding
`nano:mainnet` to its accepts[]: "a keyless Nano-402 verify path I can point accepts[]
at the way I point at PayAI for Base ... settle and verify as a drop-in, no node-poller
I babysit". It said demand does not matter once that exists. Nothing we publish was one:
our sellers each verify inside their own code, and bounties.txt section 7 checks a
signature offline but not the payee, the amount, confirmation or replay.

This is that drop-in, in one stdlib-only file. It holds no key and sends nothing: a Nano
payment is a send block the buyer already signed and published, so "settle" is only
"confirm and mark redeemed". For each payment it asks one or more public nodes for
`block_info` and accepts it only if every node that answered says:

  1. the block exists, is a `send` and is `confirmed`;
  2. it pays the requirement's `payTo` (`link_as_account`);
  3. the amount sent equals the requirement's amount in raw, exactly (a Nano block has no
     memo, so exact equality is what binds a payment to a price);
  4. the node first saw it within `maxTimeoutSeconds` (default 600), so an old payment to
     the same payee cannot be claimed by someone else;
  5. this facilitator has not redeemed that hash before (a JSON file of redeemed hashes).

Nodes that fail to answer are skipped; at least `--quorum` must answer, and any answering
node that disagrees makes the payment invalid.

Interface (the shape x402 facilitators use):
  GET  /          -> an index: every route, holds_key false, source_sha256
  GET  /source    -> this file, text/plain (the repository is private; challenge #176)
  GET  /supported -> {"kinds":[{"x402Version":1,"scheme":"exact","network":"nano:mainnet"}]}
  POST /verify    {"paymentPayload":{...},"paymentRequirements":{...}}
                  -> {"isValid":bool,"invalidReason":str|null,"payer":str|null}
  POST /settle    same body -> {"success":bool,"errorReason":str|null,"transaction":hash,
                  "network":"nano:mainnet","payer":str|null}
paymentPayload.payload may be {"hash":"<64 hex>"} (or "block_hash"), or the bare hash; a
bare 64-hex X-PAYMENT, as our own sellers take it, works too. The amount is read from
paymentRequirements "amount" (x402 v2) or "maxAmountRequired" (v1), in raw.

Run:  python3 facilitator.py --port 8402 --node https://rpc.nano.to --store redeemed.json
"""

import argparse
import base64
import hashlib
import json
import os
import re
import sys
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

NETWORK = "nano:mainnet"
SCHEME = "exact"
HASH_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
RAW_RE = re.compile(r"^[0-9]{1,40}$")  # ASCII digits only: str.isdigit() also takes "\u00b2" and "\u0663"
ADDR_RE = re.compile(r"^(nano|xrb)_[13][13456789abcdefghijkmnopqrstuwxyz]{59}$")
UA = "Mozilla/5.0 (compatible; nano-x402-facilitator/1)"
# The repository is private, so the only source a seller can read is the one this
# server hands out (challenge #176): /source serves this very file, and / names its hash.
SOURCE = open(os.path.abspath(__file__), "rb").read()
SOURCE_SHA256 = hashlib.sha256(SOURCE).hexdigest()


def node_rpc(url, body, timeout=10):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def payment_hash(payload):
    """The block hash out of a paymentPayload, a base64 X-PAYMENT, or a bare hash."""
    if isinstance(payload, str):
        s = payload.strip()
        if HASH_RE.match(s):
            return s.upper()
        try:
            payload = json.loads(base64.b64decode(s, validate=True).decode())
        except Exception:
            return None
    if not isinstance(payload, dict):
        return None
    inner = payload.get("payload", payload)
    if isinstance(inner, str):
        return inner.upper() if HASH_RE.match(inner.strip()) else None
    if isinstance(inner, dict):
        h = inner.get("hash") or inner.get("block_hash") or inner.get("blockHash")
        if isinstance(h, str) and HASH_RE.match(h.strip()):
            return h.strip().upper()
    return None


def norm_addr(a):
    return "nano_" + a.split("_", 1)[1] if isinstance(a, str) and "_" in a else a


class Store:
    """Redeemed hashes, kept in a JSON file so a restart cannot reopen a replay."""

    def __init__(self, path):
        self.path = path
        self.lock = threading.Lock()
        self.seen = set()
        if path and os.path.exists(path):
            with open(path) as f:
                self.seen = set(json.load(f))

    def has(self, h):
        with self.lock:
            return h in self.seen

    def claim(self, h):
        """Mark h redeemed; False if it already was (so two settles cannot both win)."""
        with self.lock:
            if h in self.seen:
                return False
            self.seen.add(h)
            if self.path:
                tmp = self.path + ".tmp"
                with open(tmp, "w") as f:
                    json.dump(sorted(self.seen), f)
                os.replace(tmp, self.path)
            return True


class Facilitator:
    def __init__(self, nodes, store, quorum=1, call=node_rpc, now=time.time):
        self.nodes, self.store, self.quorum, self.call, self.now = nodes, store, quorum, call, now

    def supported(self):
        return {"kinds": [{"x402Version": v, "scheme": SCHEME, "network": NETWORK} for v in (1, 2)]}

    def index(self):
        """What a stranger gets at the root: every route, what it holds, and its source."""
        return {
            "name": "nano-x402-facilitator",
            "network": NETWORK,
            "scheme": SCHEME,
            "routes": {
                "GET supported": "the kinds it verifies",
                "POST verify": '{"paymentPayload":{"payload":{"hash":"<64 hex>"}},"paymentRequirements":'
                               '{"scheme":"exact","network":"nano:mainnet","payTo":"nano_...",'
                               '"amount":"<raw>","maxTimeoutSeconds":600}}',
                "POST settle": "same body as verify; records the hash so it settles once",
                "GET source": "this server's own source, text/plain",
            },
            "holds_key": False,
            "sends": False,
            "nodes": len(self.nodes),
            "quorum": self.quorum,
            "source_sha256": SOURCE_SHA256,
            "note": "Valid only if every answering node says: confirmed send, to payTo, of exactly amount raw, "
                    "first seen within maxTimeoutSeconds, never settled here before. It does not receive the "
                    "funds; the payee's own wallet publishes the receive.",
        }

    def _check(self, body):
        """(reason or None, hash, payer). Reads the nodes; never writes anything."""
        body = body if isinstance(body, dict) else {}
        req = body.get("paymentRequirements") or {}
        pay = body.get("paymentPayload")
        if req.get("scheme", SCHEME) != SCHEME:
            return "unsupported_scheme", None, None
        if req.get("network") != NETWORK:
            return "invalid_network", None, None
        pay_to = req.get("payTo")
        if not isinstance(pay_to, str) or not ADDR_RE.match(pay_to):
            return "invalid_pay_to", None, None
        amount = str(req.get("amount", req.get("maxAmountRequired", "")))
        if not RAW_RE.match(amount) or int(amount) <= 0:
            return "invalid_amount_required", None, None
        amount = str(int(amount))  # "007" is 7 raw; the node answers "7"
        max_age = req.get("maxTimeoutSeconds")
        if max_age in (None, ""):
            max_age = 600
        elif isinstance(max_age, bool) or not RAW_RE.match(str(max_age)) or int(max_age) <= 0:
            return "invalid_max_timeout", None, None
        max_age = int(max_age)
        if isinstance(pay, dict) and pay.get("network", NETWORK) != NETWORK:
            return "invalid_network", None, None
        h = payment_hash(pay)
        if not h:
            return "invalid_payload", None, None
        if self.store.has(h):
            return "payment_already_redeemed", h, None

        answers = []
        for url in self.nodes:
            try:
                info = self.call(url, {"action": "block_info", "json_block": "true", "hash": h})
            except Exception:
                continue
            if isinstance(info, dict) and info.get("error"):
                if "not found" in str(info["error"]).lower():
                    answers.append(("block_not_found", None))
                continue
            answers.append(self._judge(info, pay_to, amount, max_age))
        if len(answers) < self.quorum:
            return "nodes_unreachable", h, None
        for reason, payer in answers:
            if reason:
                return reason, h, payer
        payers = {p for _, p in answers}
        if len(payers) != 1:
            return "nodes_disagree", h, None
        return None, h, payers.pop()

    def _judge(self, info, pay_to, amount, max_age):
        if not isinstance(info, dict):
            return "node_answer_unreadable", None
        c = info.get("contents") or {}
        payer = norm_addr(info.get("block_account") or c.get("account"))
        if info.get("subtype") != "send":
            return "not_a_send", payer
        if norm_addr(c.get("link_as_account")) != norm_addr(pay_to):
            return "wrong_payee", payer
        if str(info.get("amount")) != amount:
            return "wrong_amount", payer
        if str(info.get("confirmed")).lower() != "true":
            return "not_confirmed", payer
        try:
            seen = int(info.get("local_timestamp") or 0)
        except ValueError:
            seen = 0
        if seen <= 0:
            return "payment_age_unknown", payer
        if self.now() - seen > max_age:
            return "payment_too_old", payer
        return None, payer

    def verify(self, body):
        reason, _, payer = self._check(body)
        return {"isValid": reason is None, "invalidReason": reason, "payer": payer}

    def settle(self, body):
        reason, h, payer = self._check(body)
        if reason is None and not self.store.claim(h):
            reason = "payment_already_redeemed"
        return {"success": reason is None, "errorReason": reason, "transaction": h or "",
                "network": NETWORK, "payer": payer}


def make_handler(fac):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, obj):
            data = json.dumps(obj).encode()
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            route = self.path.split("?", 1)[0].rstrip("/")
            if route == "/supported":
                return self._send(200, fac.supported())
            if route == "":
                return self._send(200, fac.index())
            if route == "/source":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header("X-Source-SHA256", SOURCE_SHA256)
                self.send_header("Content-Length", str(len(SOURCE)))
                self.end_headers()
                return self.wfile.write(SOURCE)
            self._send(404, {"error": "not found", "routes": ["/", "/supported", "/verify", "/settle", "/source"]})

        def do_POST(self):
            route = self.path.rstrip("/")
            if route not in ("/verify", "/settle"):
                return self._send(404, {"error": "not found", "routes": ["/", "/supported", "/verify", "/settle", "/source"]})
            try:
                n = min(int(self.headers.get("Content-Length") or 0), 65536)
                body = json.loads(self.rfile.read(n).decode() or "{}")
            except Exception:
                return self._send(400, {"error": "body is not JSON"})
            try:
                out = fac.verify(body) if route == "/verify" else fac.settle(body)
            except Exception:  # never a dropped connection: a seller must get an answer it can log
                return self._send(500, {"error": "facilitator_error", "isValid": False, "success": False})
            self._send(200, out)

        def log_message(self, fmt, *args):
            sys.stderr.write("%s %s\n" % (self.log_date_time_string(), fmt % args))

    return Handler


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--port", type=int, default=8402)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--node", action="append", help="node RPC URL (repeat for more); default rpc.nano.to")
    ap.add_argument("--quorum", type=int, default=1, help="nodes that must answer")
    ap.add_argument("--store", default="redeemed.json", help="file of redeemed hashes")
    a = ap.parse_args(argv)
    fac = Facilitator(a.node or ["https://rpc.nano.to"], Store(a.store), a.quorum)
    srv = ThreadingHTTPServer((a.host, a.port), make_handler(fac))
    print("nano x402 facilitator on http://%s:%d (nodes: %s)" % (a.host, a.port, ", ".join(fac.nodes)))
    srv.serve_forever()


if __name__ == "__main__":
    main()
