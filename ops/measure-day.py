#!/usr/bin/env python3
"""measure-day: the keeper's per-run read of one UTC day, sent with our marked User-Agent (challenge #318).

Found 2026-11-19 07:1x. Challenge #207 marked every ops/ tool's requests `unowned-rail-probe/1` so the box can count
them as ours. But the keeper's own per-run measurement - the traffic file, deploy-status.json, numbers.json and the
three accounts on rpc.nano.to - was never an ops/ tool: each run wrote a fresh scratch script with a plain browser
User-Agent (the 07:1x run's did). The keeper runs about once an hour, from a cloud address that changes, so each run
added one more unmarked "outside" client to /ai/traffic/, deploy-status.json and numbers.json - the aidirectory group
duty 3 reads - and nothing could ever subtract it, even after the box applies drafts/box-count-our-probes.md. At
07:07 UTC 11-19, deploy-status.json (read only by our tools) had 14 "outside" clients, numbers.json 13, the day's
traffic file 15.

This is that read as one tool, marked, so every keeper run measures the same way and the box can tell it is us.
It sends GETs and three read-only RPC actions (account_info, receivable, account_history) and nothing else: no
send, no work, no seed. A source it could not read prints UNKNOWN, never zero. A 402 or 429 from the node is UNKNOWN.

    python3 ops/measure-day.py [YYYY-MM-DD]      default: today UTC
"""
import datetime
import json
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
BOX = "https://172-86-112-140.sslip.io"
RPC = "https://rpc.nano.to"
READ_ONLY_ACTIONS = ("account_info", "receivable", "account_history")
RAW_PER_XNO = 10 ** 30
ACCOUNTS = [
    ("treasury2", "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"),
    ("unstuck", "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"),
    ("old-treasury", "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"),
]
# Paths only our own tools read: their client count is the floor of our share of the day's "outside" clients.
OURS_ONLY_PATHS = ("/ai/traffic/deploy-status.json",)


def http_json(url, body=None):
    """(status, parsed JSON or None). Network failure -> (None, None)."""
    data = None if body is None else json.dumps(body).encode()
    headers = {"User-Agent": UA}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except Exception:
        return None, None


def rpc(action, account, fetch=http_json, **extra):
    if action not in READ_ONLY_ACTIONS:
        raise ValueError("measure-day reads only: %s refused" % action)
    body = dict(action=action, account=account, **extra)
    st, js = fetch(RPC, body)
    if st != 200 or not isinstance(js, dict) or "error" in js:
        return None
    return js


def xno(raw):
    raw = int(raw)
    whole, frac = divmod(raw, RAW_PER_XNO)
    return ("%d.%030d" % (whole, frac)).rstrip("0").rstrip(".")


def traffic_lines(t):
    if not isinstance(t, dict):
        return ["traffic: UNKNOWN (not readable)"]
    o = t.get("outside", {})
    out = ["traffic: generated %s, %s..%s, complete_day %s: %s outside requests, %s clients, ours %s" % (
        t.get("generated_utc"), o.get("first_utc"), o.get("last_utc"), t.get("complete_day"),
        o.get("requests"), o.get("distinct_clients"), t.get("ours_requests"))]
    def fmt(d):
        rows = sorted(d.items(), key=lambda kv: -kv[1].get("requests", 0))
        return ", ".join("%s %s/%s" % (k, v.get("requests"), v.get("distinct_clients")) for k, v in rows)
    out.append("groups: " + fmt(t.get("by_group", {})))
    out.append("families: " + fmt(t.get("by_client_family", {})))
    ai = {k: v for k, v in t.get("by_client_family", {}).items() if k.startswith("ai:")}
    out.append("named AI crawlers: " + (fmt(ai) if ai else "none"))
    st = t.get("status", {})
    out.append("status: " + ", ".join("%s x%s" % (k, v) for k, v in sorted(st.items()) if k not in ("200",)))
    paths = {p.get("path"): p.get("distinct_clients") for p in t.get("top_paths_by_clients", [])}
    floor = max([paths.get(p) or 0 for p in OURS_ONLY_PATHS])
    out.append("our share floor: %s clients on %s (read only by our tools; unmarked runs before #318 counted there)"
               % (floor if paths else "UNKNOWN", ", ".join(OURS_ONLY_PATHS)))
    return out


def account_lines(name, account, fetch=http_json):
    info = rpc("account_info", account, fetch)
    recv = rpc("receivable", account, fetch, count="20", source="true")
    hist = rpc("account_history", account, fetch, count="3")
    if info is None:
        line = "%s: balance UNKNOWN" % name
    else:
        line = "%s: balance %s XNO, frontier %s, %s blocks" % (
            name, xno(info.get("balance", 0)), str(info.get("frontier", ""))[:8], info.get("block_count", "?"))
    if recv is None:
        line += ", receivable UNKNOWN"
    else:
        blocks = recv.get("blocks") or {}
        line += ", receivable %d (%s)" % (len(blocks), " ".join(h[:8] for h in blocks) or "none")
    out = [line]
    if hist is not None:
        for h in hist.get("history", []):
            when = datetime.datetime.fromtimestamp(int(h.get("local_timestamp", 0)), datetime.timezone.utc)
            out.append("  %s %s XNO %s %s %s" % (h.get("type"), xno(h.get("amount", 0)), h.get("account", "")[:14],
                                                  h.get("hash", "")[:8], when.strftime("%m-%d %H:%MZ")))
    return out


def run(day, fetch=http_json):
    lines = []
    st, t = fetch("%s/ai/traffic/%s.json" % (BOX, day))
    lines += traffic_lines(t if st == 200 else None)
    st, d = fetch(BOX + "/ai/traffic/deploy-status.json")
    if st == 200 and isinstance(d, dict):
        lines.append("deploy: checked %s, main_commit %s, conflicts %s, errors %d" % (
            d.get("checked_utc"), d.get("main_commit"), d.get("conflicts") or "none", len(d.get("errors") or [])))
    else:
        lines.append("deploy: UNKNOWN")
    st, n = fetch(BOX + "/ai/numbers.json")
    if st == 200 and isinstance(n, dict):
        oa, sp = n.get("outside_agents", {}), n.get("starter_payments", {})
        lines.append("numbers: generated %s, recorded %s, converted %s, starters_sent %s, unreceived %s" % (
            n.get("generated_utc"), oa.get("recorded"), oa.get("converted"), sp.get("starters_sent"),
            sp.get("unreceived")))
    else:
        lines.append("numbers: UNKNOWN")
    for name, account in ACCOUNTS:
        lines += account_lines(name, account, fetch)
    return lines


if __name__ == "__main__":
    day = sys.argv[1] if len(sys.argv) > 1 else datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    print("\n".join(run(day)))
