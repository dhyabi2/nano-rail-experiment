"""Vercel Python function: GET /api/paid. 402 with a nano:mainnet accepts[], 200 after a verified send."""
import json, os, sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nano_seller as core

_seller = None


def get_seller():
    global _seller
    if _seller is None:
        nodes = [n.strip() for n in os.environ.get("NANO_RPC_NODES", "").split(",") if n.strip()]
        _seller = core.Seller(os.environ.get("SELLER_NANO_ACCOUNT", ""), nodes=nodes or None)
    return _seller


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q = parse_qs(urlparse(self.path).query)
        try:
            code, body, hdr = get_seller().respond(self.headers.get("X-PAYMENT"), q)
        except ValueError as e:
            code, body, hdr = 500, {"error": "seller_misconfigured", "message": str(e)}, {}
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in hdr.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass
