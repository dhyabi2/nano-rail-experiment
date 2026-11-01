"""Stateless Nano (XNO) pay-per-call seller core. Standard library only.

Holds no key, signs nothing, sends nothing: it only READS a public node. The receiving
account comes from the SELLER_NANO_ACCOUNT environment variable.

A payment is accepted if a public node says the proof block is a confirmed `send` to the
seller's account of at least PRICE_RAW, first seen within MAX_AGE seconds, and this
instance has not accepted that hash before.

HONEST LIMIT (replay): a serverless function has no disk and instances do not share
memory, so "used before" is remembered per warm instance only. Two things bound the
damage: (1) the chain-derived freshness window - the node's own timestamp must be within
MAX_AGE seconds, so a proof dies by itself; (2) the per-instance set refuses repeats on
the same instance. A replay that lands on a different/cold instance inside the window
is NOT caught. Worst case: a few repeat calls of a 0.00001 XNO result per payment, for
MAX_AGE seconds. For hard once-only, put the hash in a shared store (KV) - not done here.
"""
import base64, hashlib, json, re, threading, time, urllib.request

NETWORK, SCHEME, ASSET = "nano:mainnet", "exact", "XNO"
PRICE_RAW = 10 ** 30 // 100000          # 0.00001 XNO, derived from 1 XNO = 10^30 raw
MAX_AGE = 120
HASH_RE = re.compile(r"^[0-9A-Fa-f]{64}$")
ADDR_RE = re.compile(r"^(nano|xrb)_[13][13456789abcdefghijkmnopqrstuwxyz]{59}$")
ALPHA = "13456789abcdefghijkmnopqrstuwxyz"
RETRYABLE = ("nodes_unreachable", "not_confirmed")
UA = "Mozilla/5.0 (compatible; nano-seller-demo/1)"
DEFAULT_NODES = ["https://rpc.nano.to"]


def node_rpc(url, body, timeout=8):
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def payment_hash(proof):
    """Block hash from a bare hash, JSON, or base64 JSON x402 payload; None if unreadable."""
    if isinstance(proof, str):
        t = proof.strip()
        if HASH_RE.match(t):
            return t.upper()
        try:
            proof = json.loads(t)
        except Exception:
            try:
                proof = json.loads(base64.b64decode(t, validate=True).decode())
            except Exception:
                return None
    if not isinstance(proof, dict):
        return None
    inner = proof.get("payload", proof)
    if isinstance(inner, dict):
        h = inner.get("hash") or inner.get("block_hash") or inner.get("blockHash")
        if isinstance(h, str) and HASH_RE.match(h.strip()):
            return h.strip().upper()
    return None


def _norm(a):
    return "nano_" + a.split("_", 1)[1] if isinstance(a, str) and "_" in a else a


def check_account(addr):
    """Offline address check: base32 + blake2b-5 checksum. Returns {valid, public_key}."""
    if not isinstance(addr, str) or not ADDR_RE.match(addr):
        return {"valid": False}
    body = addr.split("_", 1)[1]
    n = 0
    for ch in body:
        n = (n << 5) | ALPHA.index(ch)
    checksum = n & ((1 << 40) - 1)
    key = (n >> 40).to_bytes(32, "big")
    want = int.from_bytes(hashlib.blake2b(key, digest_size=5).digest()[::-1], "big")
    return {"valid": checksum == want, "public_key": key.hex().upper() if checksum == want else None}


class Seller:
    def __init__(self, account, nodes=None, call=node_rpc, now=time.time, price=PRICE_RAW):
        if not isinstance(account, str) or not ADDR_RE.match(account) or not check_account(account)["valid"]:
            raise ValueError("SELLER_NANO_ACCOUNT must be a valid nano_ address")
        self.account, self.nodes, self.call, self.now, self.price = account, list(nodes or DEFAULT_NODES), call, now, price
        self.used, self.lock = set(), threading.Lock()

    def requirements(self, resource="/api/paid"):
        return {"x402Version": 2,
                "resource": {"url": resource, "mimeType": "application/json"},
                "accepts": [{"scheme": SCHEME, "network": NETWORK, "asset": ASSET, "amount": str(self.price),
                             "payTo": self.account, "maxTimeoutSeconds": MAX_AGE}]}

    def _challenge(self, reason=None):
        body = self.requirements()
        body["error"] = "payment_required"
        body["message"] = ("Send %s raw (0.00001 XNO) to payTo on nano:mainnet, then retry with the send block "
                           "hash in the X-PAYMENT header." % self.price)
        hdr = {"payment-required": base64.b64encode(json.dumps(self.requirements()).encode()).decode(),
               "x-402-version": "2"}
        if reason:
            body["reason"] = reason
        return 402, body, hdr

    def _judge(self, info):
        c = info.get("contents") or {}
        if info.get("subtype") != "send":
            return "not_a_send"
        if _norm(c.get("link_as_account")) != _norm(self.account):
            return "wrong_payee"
        try:
            if int(info.get("amount")) < self.price:
                return "wrong_amount"
        except (TypeError, ValueError):
            return "wrong_amount"
        if str(info.get("confirmed")).lower() != "true":
            return "not_confirmed"
        try:
            ts = int(info.get("local_timestamp") or 0)
        except ValueError:
            ts = 0
        if ts <= 0:
            return "payment_age_unknown"
        if self.now() - ts > MAX_AGE:
            return "payment_too_old"
        return None

    def _read(self, h):
        """(reason or None, info). Reads public nodes; first definite answer wins."""
        for url in self.nodes:
            try:
                info = self.call(url, {"action": "block_info", "json_block": "true", "hash": h})
            except Exception:
                continue
            if not isinstance(info, dict):
                continue
            if info.get("error"):
                if "not found" in str(info["error"]).lower():
                    return "block_not_found", None
                continue
            if "contents" not in info and "subtype" not in info:
                continue
            return self._judge(info), info
        return "nodes_unreachable", None

    def respond(self, proof, query):
        """-> (status, json body, extra headers). Pure apart from node reads and the per-instance set."""
        if proof is None or not str(proof).strip():
            return self._challenge()
        h = payment_hash(proof)
        if not h:
            return self._challenge("invalid_payload")
        if h in self.used:
            return self._challenge("payment_already_redeemed")
        reason, info = self._read(h)
        if reason in RETRYABLE:  # pending, not invalid: a buyer who paid must not be told to pay again
            return 503, {"error": "payment_pending", "reason": reason, "retryable": True}, {"Retry-After": "5"}
        if reason:
            return self._challenge(reason)
        with self.lock:
            if h in self.used:
                return self._challenge("payment_already_redeemed")
            self.used.add(h)
        acct = (query.get("account") or [SELLER_DEFAULT_PROBE])[0]
        return 200, {"result": {"account": acct, "account_valid": check_account(acct)["valid"],
                                "public_key": check_account(acct).get("public_key")},
                     "receipt": {"block_hash": h, "payer": _norm(info.get("block_account")),
                                 "paid_raw": str(info.get("amount")), "payTo": self.account}}, {}


SELLER_DEFAULT_PROBE = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
