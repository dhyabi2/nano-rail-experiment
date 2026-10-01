#!/usr/bin/env python3
"""check-dead-ends: which doors that outside clients actually knocked on today lead nowhere?

Found 2026-10-01 (challenge #76). The traffic file counts distinct outside clients per path. On 2026-10-01
00:00-12:03 UTC more of them hit dead ends on our host than read bounties.txt (8 clients):

    /unstuck/api/          8 clients  -> 404 {"error":"not found"}
    /unstuck/api/ask       7 clients  -> 404 {"error":"not found"}   (a GET on the URL every text says to POST to)
    /canon.html            6 clients  -> 426 "websocket upgrade required"   (the published file's own name)
    /                      5 clients  -> 426 "websocket upgrade required"   (the host every flyer names)
    /unstuck/api/asks/500  3 clients  -> 404 {"error":"not found"}   (plural form of /unstuck/api/ask/<id>)

An agent that guesses a door and gets "not found" or a websocket error concludes the thing does not exist. These paths
are served by the box's Caddy config and the Unstuck backend, not by this repository; the fix is drafted for the box in
drafts/box-dead-ends.md. This tool measures whether the dead ends are still live, so each keeper run reports it.

It reads the day's traffic file, takes every path with at least --min distinct outside clients, and GETs each once.
A path is a DEAD END when it answers 404, 426 or any 5xx. It never probes a path that mints something (the onramp
issues a fresh seed and onboard_id per call) or that is a paid endpoint. Each probe is one request from this session,
which the traffic file counts as outside (it only knows the swarm's boxes as ours): say so when quoting the numbers.

    python3 ops/check-dead-ends.py [YYYY-MM-DD] [--min N] [--json]
    exit 0 no dead ends; 1 at least one; 3 the traffic file or a probe was unreadable (UNKNOWN, never clean)
"""
import datetime
import json
import re
import sys
import urllib.error
import urllib.request

HOST = "https://172-86-112-140.sslip.io"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"

# Never GET these: each call mints a seed/onboard_id, spends, or writes.
NEVER_PROBE = [
    r"/onramp\b",
    r"/v1/pay\b",
    r"/settle\b",
    r"/accept\b",
]
DEAD_STATUSES = {404, 410, 426}


def is_dead(status):
    """A status a stranger reads as 'this does not exist' (or a broken server)."""
    return status in DEAD_STATUSES or status >= 500


def probe_safe(path):
    return path.startswith("/") and not any(re.search(p, path) for p in NEVER_PROBE)


def candidates(traffic, min_clients):
    """Paths from the traffic file with at least min_clients outside clients, safe to probe, busiest first."""
    rows = traffic.get("top_paths_by_clients") or []
    out = [(r["path"], r["distinct_clients"]) for r in rows
           if r.get("distinct_clients", 0) >= min_clients and probe_safe(r.get("path", ""))]
    return sorted(out, key=lambda x: -x[1])


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, r.read(200).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read(200).decode("utf-8", "replace")


def main(argv):
    day = next((a for a in argv if re.fullmatch(r"\d{4}-\d{2}-\d{2}", a)),
               datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    min_clients = int(argv[argv.index("--min") + 1]) if "--min" in argv else 3
    try:
        req = urllib.request.Request(f"{HOST}/ai/traffic/{day}.json", headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=30) as r:
            traffic = json.loads(r.read())
    except Exception as e:
        print(f"UNKNOWN    traffic file for {day} unreadable: {str(e)[:200]}")
        return 3
    report, unreadable = [], False
    for path, clients in candidates(traffic, min_clients):
        try:
            status, snippet = fetch(HOST + path)
        except Exception as e:
            unreadable = True
            report.append({"path": path, "clients": clients, "status": None, "verdict": "UNKNOWN",
                           "body": str(e)[:120]})
            continue
        report.append({"path": path, "clients": clients, "status": status,
                       "verdict": "DEAD END" if is_dead(status) else "ok", "body": snippet.strip()[:60]})
    dead = [r for r in report if r["verdict"] == "DEAD END"]
    if "--json" in argv:
        print(json.dumps({"date": day, "generated_utc": traffic.get("generated_utc"), "paths": report}, indent=1))
    else:
        print(f"traffic {day} generated {traffic.get('generated_utc')}; paths with >= {min_clients} outside clients")
        for r in report:
            print(f"{r['verdict']:9} {str(r['status']):4} {r['clients']:3} clients  {r['path']}"
                  + (f"  -> {r['body']!r}" if r["verdict"] != "ok" else ""))
        print(f"{len(dead)} dead end(s), {sum(r['clients'] for r in dead)} client-path hits on them")
    if dead:
        return 1
    return 3 if unreadable else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
