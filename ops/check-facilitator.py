#!/usr/bin/env python3
"""Is the Nano x402 facilitator hosted, and is what is hosted the code on main? (challenge #176)

inkassat0r4 (Moltbook, 2026-10-28 11:43) will add nano:mainnet to its accepts[] once a keyless
verify path exists that it can point at. #175 built one; it helps nobody until it answers at a
public URL, and the reply draft may not be posted before that. This reads the URL as a seller
would, so the keeper can say each run, from a measurement, whether the gate is open:

  GET  /           an index (JSON) that says holds_key false and names source_sha256
  GET  /source     the served source; its sha256 must equal the index's, and is compared to main
  GET  /supported  must list scheme exact on nano:mainnet
  POST /verify     a zero hash must come back 200 with isValid false (a refusal, not a crash)
  CORS             Access-Control-Allow-Origin on the answers, so a browser-side seller can call it

Usage: ops/check-facilitator.py [BASE_URL]   (default: the URL drafts/box-nano-x402-facilitator.md proposes)
Exit 0 hosted and every check passed; 1 a check failed; 2 nothing answers there (NOT HOSTED).
"""

import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

DEFAULT = "https://172-86-112-140.sslip.io/x402/facilitator"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
MAIN_SOURCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tools", "nano-x402-facilitator",
                           "facilitator.py")
ZERO = "0" * 64


def fetch(url, data=None, opener=None, timeout=15):
    """(status, headers, body bytes); status 0 when nothing answered."""
    req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, "Content-Type": "application/json"})
    try:
        with (opener.open if opener else urllib.request.urlopen)(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except Exception:
        return 0, {}, b""


def check(base, opener=None, main_source=MAIN_SOURCE):
    """(exit code, [lines])."""
    base = base.rstrip("/")
    out, bad = [], 0

    def line(ok, what):
        nonlocal bad
        bad += 0 if ok else 1
        out.append("%-5s %s" % ("ok" if ok else "FAIL", what))

    st, hd, raw = fetch(base + "/", opener=opener)
    try:
        index = json.loads(raw.decode())
    except Exception:
        index = None
    if st == 0 or not isinstance(index, dict) or index.get("network") != "nano:mainnet":
        return 2, ["NOT HOSTED  %s/ answered %s, not the facilitator's index" % (base, st or "nothing")]
    line(index.get("holds_key") is False and index.get("sends") is False, "index says holds_key false, sends false")
    line(hd.get("Access-Control-Allow-Origin") == "*", "CORS on the index")

    st, hd, src = fetch(base + "/source", opener=opener)
    served = hashlib.sha256(src).hexdigest() if st == 200 else None
    line(served is not None and served == index.get("source_sha256") == hd.get("X-Source-SHA256"),
         "/source sha256 %s matches the index and its header" % (served or "-")[:16])
    try:
        with open(main_source, "rb") as f:
            on_main = hashlib.sha256(f.read()).hexdigest()
        out.append("info  served source %s main (%s)" % ("MATCHES" if served == on_main else "DIFFERS FROM",
                                                        on_main[:16]))
    except OSError:
        out.append("info  main's source not readable here; served source not compared")

    st, _, raw = fetch(base + "/supported", opener=opener)
    try:
        kinds = json.loads(raw.decode()).get("kinds", [])
    except Exception:
        kinds = []
    line(any(k.get("scheme") == "exact" and k.get("network") == "nano:mainnet" for k in kinds),
         "/supported lists exact on nano:mainnet")

    probe = {"paymentPayload": {"payload": {"hash": ZERO}},
             "paymentRequirements": {"scheme": "exact", "network": "nano:mainnet", "amount": "1",
                                     "payTo": "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"}}
    st, _, raw = fetch(base + "/verify", data=json.dumps(probe).encode(), opener=opener)
    try:
        v = json.loads(raw.decode())
    except Exception:
        v = {}
    line(st == 200 and v.get("isValid") is False and bool(v.get("invalidReason")),
         "/verify refuses a zero hash with a reason (%s %s)" % (st, v.get("invalidReason")))
    return (1 if bad else 0), out


def main(argv):
    base = argv[1] if len(argv) > 1 else DEFAULT
    code, lines = check(base)
    print("\n".join(lines))
    print({0: "HOSTED: every check passed at %s", 1: "HOSTED BUT FAULTY at %s",
           2: "NOT HOSTED at %s - the inkassat0r4 reply draft stays unposted"}[code] % base)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv))
