#!/usr/bin/env python3
"""watch-outage: is everything a stranger needs up, and is the money landing? Runs OFF the box.

Found 2026-10-24 (challenge #148). The box went down at about 10:25 UTC on 10-17 and stayed down until about 04:00
on 10-24. For those six and a half days every guide we publish returned a Vercel 502, the five paid endpoints timed
out, and a 10 XNO send sat receivable at the treasury - and nothing noticed, because the silence alarm ran on the box
it was watching and the keeper routine was not firing. This check ran on GitHub's runners (outage-watch.yml, hourly)
until the owner removed every GitHub Actions workflow at 20:48 UTC 11-07 (challenge #234); the keeper now runs it by
hand each run, off the box.

It checks only what the keeper's alert list names as critical:
  - every published guide and the asks API answer 200 (and the .txt guides as text/plain);
  - every paid endpoint's /.well-known/x402 names the treasury as its only payee and accepts XNO;
  - the one paid call the guides say WORKS (getunstuck.space's echo, challenge #212) publishes its terms, at both
    manifest URLs, as JSON that names our Unstuck account as its only payee and accepts XNO;
  - the treasury holds at least 9.0 XNO and has nothing receivable for longer than an hour.
It reads only: GETs on public URLs, and the read-only RPC calls account_info, receivable and blocks_info.

    python3 ops/watch-outage.py [--json] [--previous BODY_FILE --new-out FILE]
    exit 0 all clear; 1 at least one fault (a fault is also a probe that could not run - never reported clean)

--previous / --new-out (challenge #160): the workflow opens one issue and afterwards only EDITS its body, and an edit
emails nobody. On 10-26 issue #121 was already open for the five sellers when the whole box went down between 01:42
and 04:16 UTC, so every guide and the asks API failed and the owner heard nothing. Given the open issue's body, the
faults not already listed in it are written to FILE, and the workflow posts them as a comment, which does email.
"""
import json
import re
import sys
import time
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
RPC = "https://rpc.nano.to"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
FLOOR_RAW = 9 * 10**30
RECEIVABLE_MAX_AGE_S = 3600

# (url, required content-type prefix or None)
PAGES = [
    ("https://getunstuck.space/bounties.txt", "text/plain"),
    ("https://getunstuck.space/canon.txt", "text/plain"),
    ("https://getunstuck.space/swap.txt", "text/plain"),
    ("https://getunstuck.space/canon", "text/html"),
    ("https://getunstuck.space/unstuck/api/asks", "application/json"),
    ("https://172-86-112-140.sslip.io/ai/", "text/html"),
    ("https://172-86-112-140.sslip.io/ai/traffic/deploy-status.json", "application/json"),
]
SELLERS = ["extract", "search", "domain", "check", "geoip"]
# Challenge #212: the five sellers above have been down since 10-17, so every guide sends a stranger to the echo
# instead (bounties.txt RIGHT NOW box, STEP 6). Its terms were in no check. It pays our Unstuck account, not the
# treasury (bounties.txt: "0.001 XNO to our own Unstuck account").
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
LIVE_CALL_MANIFESTS = [
    "https://getunstuck.space/.well-known/x402",
    "https://getunstuck.space/unstuck/api/v1/x402",
]


def http_get(url, timeout=20):
    """(status, content_type, body bytes); status 0 when the request did not complete."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get("Content-Type", "") if e.headers else "", b""
    except Exception as e:  # timeout, reset, DNS: the stranger gets nothing
        return 0, "", repr(e).encode()


def rpc(payload, timeout=20):
    req = urllib.request.Request(RPC, data=json.dumps(payload).encode(),
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def check_page(url, ctype, get=http_get):
    status, got, _ = get(url)
    if status != 200:
        return "%s answered %s" % (url, status or "nothing (timeout or reset)")
    if ctype and not got.lower().startswith(ctype):
        return "%s is served as %r, not %s" % (url, got, ctype)
    return None


def payees_and_assets(node, payees, assets):
    """Collect every payTo/pay_to and every asset/network named anywhere in a manifest."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("payTo", "pay_to") and isinstance(v, str):
                payees.add(v)
            elif k in ("asset", "network", "currency") and isinstance(v, str):
                assets.add(v)
            else:
                payees_and_assets(v, payees, assets)
    elif isinstance(node, list):
        for v in node:
            payees_and_assets(v, payees, assets)


def check_manifest(seller, get=http_get):
    url = "https://%s.paypercall.dev/.well-known/x402" % seller
    status, _, body = get(url)
    if status != 200:
        return "%s answered %s" % (url, status or "nothing (timeout or reset)")
    try:
        doc = json.loads(body)
    except ValueError:
        return "%s is not JSON" % url
    payees, assets = set(), set()
    payees_and_assets(doc, payees, assets)
    if not payees:
        return "%s names no payTo" % url
    others = sorted(p for p in payees if p != TREASURY)
    if others:
        return "%s pays someone other than the treasury: %s" % (url, ", ".join(others))
    if not any(a.upper() == "XNO" or a.lower().startswith("nano") for a in assets):
        return "%s does not accept XNO (assets/networks named: %s)" % (url, ", ".join(sorted(assets)) or "none")
    return None


def check_live_call(url, get=http_get):
    """The echo's terms: 200, served as application/json, one payee (our Unstuck account), XNO accepted."""
    status, ctype, body = get(url)
    if status != 200:
        return "%s answered %s" % (url, status or "nothing (timeout or reset)")
    try:
        doc = json.loads(body)
    except ValueError:
        return "%s is not JSON" % url
    payees, assets = set(), set()
    payees_and_assets(doc, payees, assets)
    if not payees:
        return "%s names no payTo" % url
    others = sorted(p for p in payees if p != UNSTUCK)
    if others:
        return "%s pays someone other than our Unstuck account: %s" % (url, ", ".join(others))
    if not any(a.upper() == "XNO" or a.lower().startswith("nano") for a in assets):
        return "%s does not accept XNO (assets/networks named: %s)" % (url, ", ".join(sorted(assets)) or "none")
    if not ctype.lower().startswith("application/json"):
        return "%s is served as %r, not application/json (a client that checks the type before parsing sees no terms)" % (url, ctype)
    return None


def check_treasury(call=rpc, now=time.time):
    faults = []
    try:
        info = call({"action": "account_info", "account": TREASURY})
        if int(info.get("balance", "0")) < FLOOR_RAW:
            faults.append("treasury holds %s XNO, under the 9.0 floor" % info.get("balance_nano", info.get("balance")))
        rec = call({"action": "receivable", "account": TREASURY, "count": "50", "threshold": "1"}).get("blocks") or {}
        hashes = list(rec) if isinstance(rec, (dict, list)) else []
        if hashes:
            blocks = call({"action": "blocks_info", "hashes": hashes, "json_block": "true"}).get("blocks", {})
            for h in hashes:
                ts = int((blocks.get(h) or {}).get("local_timestamp") or 0)
                if not ts:
                    faults.append("receivable block %s has no readable timestamp" % h[:8])
                elif now() - ts > RECEIVABLE_MAX_AGE_S:
                    faults.append("receivable block %s at the treasury is %.1f hours old (auto-receive is every 15 min)"
                                  % (h[:8], (now() - ts) / 3600.0))
    except Exception as e:
        faults.append("treasury could not be read from %s: %r" % (RPC, e))
    return faults


def run(get=http_get, call=rpc, now=time.time):
    faults = [f for f in (check_page(u, c, get) for u, c in PAGES) if f]
    faults += [f for f in (check_manifest(s, get) for s in SELLERS) if f]
    faults += [f for f in (check_live_call(u, get) for u in LIVE_CALL_MANIFESTS) if f]
    faults += check_treasury(call, now)
    return faults


def fault_key(fault):
    """A fault without the numbers that change every run (the receivable's age), so a re-run is not 'new'."""
    return re.sub(r"\d+(\.\d+)? hours old", "hours old", fault.strip().lstrip("- ").strip())


def new_faults(previous_body, faults):
    """The faults the open issue's body does not already list, in run order."""
    seen = {fault_key(line) for line in (previous_body or "").splitlines() if line.strip().startswith("- ")}
    return [f for f in faults if fault_key(f) not in seen]


def main(argv):
    faults = run()
    if "--previous" in argv and "--new-out" in argv:
        try:
            previous = open(argv[argv.index("--previous") + 1]).read()
        except OSError:
            previous = ""
        with open(argv[argv.index("--new-out") + 1], "w") as out:
            out.write("".join("- %s\n" % f for f in new_faults(previous, faults)))
    stamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    if "--json" in argv:
        print(json.dumps({"checked_utc": stamp, "faults": faults}, indent=1))
    elif faults:
        print("%d fault(s) at %s:\n" % (len(faults), stamp) + "\n".join("- " + f for f in faults))
    else:
        print("all clear at %s" % stamp)
    return 1 if faults else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
