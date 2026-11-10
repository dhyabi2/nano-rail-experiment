#!/usr/bin/env python3
"""check-owner-queue: which of the fixes waiting on the owner or the box are live, measured now (challenge #210).

Why this exists. By 11-03 the keeper had moved every blocker it can move itself (209 challenges), and what still stops
an outside agent from earning or paying here is box- or owner-side: five sellers silent since 10-17, a treasury
receiver that has left 10 XNO unreceived for 16 days, and eleven drafts in drafts/ that nobody has applied. Each draft
sat in its own file with its own "check after" line; nothing re-measured them, so nobody (the owner included) could
see in one place what is still waiting, what it costs, or which one to apply first. A queue nobody can see is a queue
nobody works.

This tool is that one place. Each row is one owner/box action, ranked by how much conversion it unblocks, with a
free public probe that says APPLIED, WAITING or UNKNOWN (a probe that could not run is UNKNOWN, never APPLIED and never
WAITING). It sends only GETs, unpaid POSTs that cost nothing, and read-only RPC calls; never a send, never a seed.

    python3 ops/check-owner-queue.py            table; exit 1 while anything is WAITING, 3 if only UNKNOWNs remain
    python3 ops/check-owner-queue.py --md       the same as the markdown table drafts/OWNER-QUEUE.md carries
    python3 ops/check-owner-queue.py --json
"""
import datetime
import json
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
SELLERS = ["extract", "search", "domain", "check", "geoip"]
GU = "https://getunstuck.space"
BOX = "https://172-86-112-140.sslip.io"
ROOT = Path(__file__).resolve().parent.parent

APPLIED, WAITING, UNKNOWN = "APPLIED", "WAITING", "UNKNOWN"


def fetch(url, method="GET", body=None, timeout=15, want_type=False, limit=400000):
    """(status, text) for any HTTP answer, or (status, text, content_type) with want_type; raises OSError when nothing
    answered. At most `limit` bytes are read (the asks list is 1.39 MB on 11-10, so its probe asks for more)."""
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            out = (r.status, r.read(limit).decode("utf-8", "replace"), r.headers.get("Content-Type", ""))
    except urllib.error.HTTPError as e:
        out = (e.code, e.read(limit).decode("utf-8", "replace"), e.headers.get("Content-Type", ""))
    return out if want_type else out[:2]


def _json(text):
    try:
        return json.loads(text)
    except ValueError:
        return None


# Each probe(fetch) -> (state, measured detail). Any exception in a probe becomes UNKNOWN.

def p_sellers(f):
    answered, wrong = [], []
    for s in SELLERS:
        try:
            st, t = f("https://%s.paypercall.dev/.well-known/x402" % s, timeout=10)
        except OSError:
            continue
        j = _json(t) if st == 200 else None
        if j is None:
            continue
        acc = j.get("accepts") or []
        if any(a.get("payTo", a.get("pay_to")) == TREASURY and "XNO" in json.dumps(a) for a in acc):
            answered.append(s)
        else:
            wrong.append(s)
    if wrong:
        return WAITING, "answering but not paying the treasury in XNO: " + ", ".join(wrong)
    if answered:
        return (APPLIED if len(answered) == len(SELLERS) else WAITING), "%d of 5 answer: %s" % (
            len(answered), ", ".join(answered))
    return WAITING, "0 of 5 sellers' /.well-known/x402 answered"


def p_treasury_receive(f):
    st, t = f("https://rpc.nano.to", "POST", {"action": "receivable", "account": TREASURY, "source": "true"})
    j = _json(t)
    if st != 200 or not isinstance(j, dict) or "blocks" not in j:
        return UNKNOWN, "receivable unreadable (http %s)" % st
    blocks = j["blocks"] or {}
    if not blocks:
        return APPLIED, "nothing receivable at the treasury"
    return WAITING, "%d block(s) receivable: %s" % (len(blocks), ", ".join(h[:8] for h in blocks))


def p_accept_token(f):
    st, t = f(GU + "/llms.txt")
    if st != 200:
        return UNKNOWN, "llms.txt http %s" % st
    return (APPLIED, "llms.txt names accept_token") if "accept_token" in t else (
        WAITING, "llms.txt never names accept_token")


def p_echo_description(f):
    st, t = f(GU + "/unstuck/api/v1/x402")
    j = _json(t)
    if st != 200 or not isinstance(j, dict):
        return UNKNOWN, "x402 terms http %s" % st
    d = (j.get("resource") or {}).get("description", "")
    return (WAITING, "description still says '...post an ask...'") if "post an ask" in d else (
        APPLIED, "description no longer says asking costs XNO")


def p_routes_link_bounties(f):
    st, t = f(GU + "/llms.txt")
    if st != 200:
        return UNKNOWN, "llms.txt http %s" % st
    return (APPLIED, "llms.txt links bounties.txt") if "bounties.txt" in t else (
        WAITING, "llms.txt does not link bounties.txt")


def p_echo_get(f):
    st, _ = f(GU + "/unstuck/api/v1/echo")
    return (WAITING, "GET echo -> 404") if st == 404 else (APPLIED, "GET echo -> %s" % st)


def p_api_index(f):
    """#229: GET /unstuck/api/ on the box was the most-requested path on 11-07 (59 outside clients) and 404s."""
    st, t = f(BOX + "/unstuck/api/")
    if st == 200:
        try:
            if "start_here" in json.loads(t):
                return APPLIED, "GET /unstuck/api/ -> 200 index"
        except ValueError:
            pass
    return WAITING, "GET /unstuck/api/ -> %s" % st


def p_box_dead_ends(f):
    a, b = p_api_index(f), p_echo_get(f)
    state = APPLIED if a[0] == b[0] == APPLIED else WAITING
    return state, "%s; %s" % (a[1], b[1])


def p_custody(f):
    script = ROOT / "ops" / "check-custody-claims.py"
    r = subprocess.run([sys.executable, str(script)], capture_output=True, text=True, timeout=60)
    if r.returncode == 0:
        return APPLIED, "no live guide calls the onramp's seed yours"
    if r.returncode == 1:
        return WAITING, "a live guide still calls the onramp's server-made seed yours"
    return UNKNOWN, "check-custody-claims exit %s" % r.returncode


def p_per_request_quote(f):
    amts = []
    for _ in range(2):
        st, t = f(GU + "/unstuck/api/v1/echo", "POST", {})
        j = _json(t)
        if st != 402 or not isinstance(j, dict):
            return UNKNOWN, "unpaid POST echo -> %s" % st
        amts.append(((j.get("accepts") or [{}])[0]).get("amount"))
    return (WAITING, "two 402s quote the same amount %s raw" % amts[0]) if amts[0] == amts[1] else (
        APPLIED, "two 402s quote different amounts")


def p_facilitator(f):
    st, t = f(BOX + "/x402/facilitator/supported")
    if st == 200 and _json(t) is not None:
        return APPLIED, "/x402/facilitator/supported -> 200 JSON"
    return WAITING, "/x402/facilitator/supported -> %s" % st


def p_count_probes(f):
    day = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    st, t = f(BOX + "/ai/traffic/%s.json" % day)
    j = _json(t)
    if st != 200 or not isinstance(j, dict):
        return UNKNOWN, "traffic file http %s" % st
    if "ours_probe_requests" in j:
        return APPLIED, "traffic file counts our probes (ours_probe_requests %s)" % j["ours_probe_requests"]
    if (j.get("ours_requests") or 0) == 0:
        return WAITING, "ours_requests 0 although our probes ran today"
    return UNKNOWN, "ours_requests %s (could be the boxes)" % j.get("ours_requests")


def p_tvl(f):
    st, t = f(BOX + "/tvl.json")
    j = _json(t)
    if st != 200 or not isinstance(j, dict):
        return UNKNOWN, "tvl.json http %s" % st
    if j.get("complete") is False:
        return (APPLIED, "incomplete read published as null") if j.get("tvl_xno") is None else (
            WAITING, "incomplete read published as tvl_xno %s" % j.get("tvl_xno"))
    return UNKNOWN, "read was complete; the fault only shows on a failed read"


def p_root_crawler(f):
    st, _ = f(BOX + "/robots.txt")
    return (APPLIED, "/robots.txt -> 200") if st == 200 else (WAITING, "/robots.txt -> %s" % st)


def p_wellknown_json(f):
    """Challenge #213: the one live paid call's terms at the path x402 clients look up first must be served as JSON.
    The body was right on 11-03 but came back application/octet-stream (a download, not terms)."""
    st, t, ctype = f(GU + "/.well-known/x402", want_type=True)
    if st != 200 or _json(t) is None:
        return UNKNOWN, "/.well-known/x402 http %s, body JSON %s" % (st, _json(t) is not None)
    ctype = (ctype or "").split(";")[0].strip().lower()
    if ctype == "application/json":
        return APPLIED, "/.well-known/x402 served as application/json"
    return WAITING, "/.well-known/x402 served as %s" % (ctype or "no content-type")


def p_asks_how_to_ask(f):
    """Challenge #244: GET /unstuck/api/asks is the most-read path (55 outside clients on 11-09, bounties.txt 11) and
    answers only `asks` and `counts`. APPLIED when something beside the asks list names the POST route to post one."""
    st, t = f(GU + "/unstuck/api/asks", limit=8000000)
    j = _json(t)
    if st != 200 or not isinstance(j, dict) or not isinstance(j.get("asks"), list):
        return UNKNOWN, "GET /unstuck/api/asks http %s, asks list %s" % (st, isinstance(j, dict) and "asks" in j)
    rest = json.dumps({k: v for k, v in j.items() if k != "asks"})
    if "POST" in rest and "/unstuck/api/ask" in rest:
        return APPLIED, "GET /unstuck/api/asks names the POST route beside the list"
    return WAITING, "GET /unstuck/api/asks answers only %s, no route to post" % "+".join(sorted(j))


# rank, who, action, what it unblocks, draft, challenge, probe
QUEUE = [
    (1, "owner", "restart the five paid sellers", "every paid call but the echo; STEP 6 of every guide",
     "drafts/owner-box-down-2026-10-23.md", "#197", p_sellers),
    (2, "owner", "restart the treasury auto-receive", "a payment to us is income only once received",
     "drafts/owner-box-down-2026-10-23.md", "#148", p_treasury_receive),
    (3, "network", "accept token for pre-rule asks, and in llms.txt", "paying outside answers #317, #318; any stranger accepting",
     "drafts/box-accept-token-legacy-asks.md", "#109", p_accept_token),
    (4, "network", "fix the echo's description (asking is free)", "the cheapest conversion: posting an ask",
     "CHALLENGES-SOLVED.md #199", "#199", p_echo_description),
    (5, "network", "link bounties and canon from llms.txt, agent.json, sitemap", "machine readers finding the offer at all",
     "drafts/unstuck-machine-routes-link-bounties.md", "#138", p_routes_link_bounties),
    (6, "box", "answer GET /unstuck/api/ with an index and GET on the echo with 405 + the POST",
     "the two most-knocked dead ends (59 and 6 outside clients, 11-07 00:00-03:55)",
     "drafts/box-dead-ends.md", "#204, #229", p_box_dead_ends),
    (7, "network", "stop calling the onramp's server-made seed 'yours'", "trust in the first wallet step",
     "drafts/unstuck-llms-onramp-seed.md", "#75", p_custody),
    (8, "network", "quote a fresh amount per echo 402", "a buyer's payment being claimed by a watcher",
     "drafts/box-echo-per-request-quote.md", "#179", p_per_request_quote),
    (9, "box", "host the keyless Nano x402 facilitator", "the x402 seller that asked for one (10-28)",
     "drafts/box-nano-x402-facilitator.md", "#175", p_facilitator),
    (10, "box", "count our probes as ours in the traffic file", "an honest 'did anybody come' every day",
     "drafts/box-count-our-probes.md", "#207", p_count_probes),
    (11, "box", "publish a failed TVL read as null, not 0", "a true TVL number",
     "drafts/box-tvl-unknown-not-zero.md", "#97", p_tvl),
    (12, "box", "serve robots.txt, llms.txt, sitemap at the box root", "crawlers finding /ai/",
     "drafts/box-root-crawler-files.md", "#71", p_root_crawler),
    (13, "network", "serve /.well-known/x402 as JSON", "x402 clients reading the one live paid call's terms",
     "drafts/network-x402-json-content-type.md", "#212", p_wellknown_json),
    (14, "network", "say how to post (free) and answer in GET /unstuck/api/asks",
     "the most-read path (55 outside clients 11-09) reaching a first outside ask",
     "drafts/network-asks-how-to-ask.md", "#244", p_asks_how_to_ask),
]


def run(f=fetch):
    rows = []
    for rank, who, action, unblocks, draft, ch, probe in QUEUE:
        try:
            state, detail = probe(f)
        except Exception as e:  # a probe that could not run says so
            state, detail = UNKNOWN, "probe failed: %s" % type(e).__name__
        rows.append({"rank": rank, "who": who, "action": action, "unblocks": unblocks, "draft": draft,
                     "challenge": ch, "state": state, "measured": detail})
    return rows


def exit_code(rows):
    states = {r["state"] for r in rows}
    if WAITING in states:
        return 1
    if UNKNOWN in states:
        return 3
    return 0


def markdown(rows, when):
    out = ["| # | state | who | action | unblocks | measured %s | draft |" % when,
           "|---|---|---|---|---|---|---|"]
    for r in rows:
        out.append("| %d | **%s** | %s | %s | %s | %s | `%s` (%s) |" % (
            r["rank"], r["state"], r["who"], r["action"], r["unblocks"], r["measured"], r["draft"], r["challenge"]))
    return "\n".join(out)


def main(argv):
    rows = run()
    when = datetime.datetime.now(datetime.timezone.utc).strftime("%H:%M UTC %Y-%m-%d")
    if "--json" in argv:
        print(json.dumps({"measured_utc": when, "rows": rows}, indent=1))
    elif "--md" in argv:
        print(markdown(rows, when))
    else:
        for r in rows:
            print("%-2d %-8s %-8s %s -- %s" % (r["rank"], r["state"], r["who"], r["action"], r["measured"]))
        n = sum(r["state"] == WAITING for r in rows)
        print("%d waiting, %d applied, %d unknown (%s)" % (
            n, sum(r["state"] == APPLIED for r in rows), sum(r["state"] == UNKNOWN for r in rows), when))
    return exit_code(rows)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
