#!/usr/bin/env python3
"""creates-by-day: how many things outside clients CREATED on our host in one UTC day, and how many of them we can name.

Challenge #222. The day's traffic file counts responses by status. A 201 means a client created something:
an ask, an answer, or an address registered at POST /unstuck/api/v1/onramp/self (bounties.txt section 2,
"answers 201 {address, onboard_id, custody:"self"}"). The keeper read asks and answers (answers-by-day.py)
and never compared them with the 201s. Measured from the complete days' files:

    11-01: 3 creates, 1 ask/answer     11-02: 3 creates, 2
    11-03: 12 creates, 0               11-04: 9 creates, 8 (7 burst asks + 1 answer)
    11-05 (to 20:07): 11 creates, 1

So on 11-03 twelve things were created and every journal said nobody posted anything. None of our ops
probes or tests POST to that host, the swarm was dark (no member comment since 11-02 21:04), and the
box counts 0 requests as ours, so the remainder is UNEXPLAINED - most likely an agent registering an
address, which is an agent arriving that no number of ours shows. The traffic file has no status per
path, so this tool cannot say which endpoint; it says how many are unnamed and what could have made them
(drafts/box-creates-by-path.md asks the box for the per-path split).

Read-only GETs. A source that fails makes the result UNKNOWN (exit 2), never zero.

    python3 ops/creates-by-day.py               today (UTC)
    python3 ops/creates-by-day.py 2026-11-03
    python3 ops/creates-by-day.py --json 2026-11-03
"""
import argparse
import datetime
import importlib.util
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TRAFFIC = "https://172-86-112-140.sslip.io/ai/traffic/%s.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
# Every documented way a client gets a 201 from our host. A remainder is one of these or something undocumented.
CREATORS = [
    "POST /unstuck/api/v1/onramp/self  - registers a self-made address (bounties.txt section 2)",
    "POST /unstuck/api/ask             - an ask whose created_at the asks list no longer carries",
    "POST /unstuck/api/ask/<id>/answers - an answer on an ask the asks list no longer carries",
]


def _load_abd():
    spec = importlib.util.spec_from_file_location("abd", os.path.join(HERE, "answers-by-day.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class Unknown(Exception):
    """A source answered in a shape we cannot read: the result is UNKNOWN, never a count of zero."""


def _count(value, what):
    if isinstance(value, bool) or not isinstance(value, (int, str)):
        raise Unknown(f"{what} is {value!r}, not a count")
    try:
        n = int(value)
    except ValueError:
        raise Unknown(f"{what} is {value!r}, not a count")
    if n < 0:
        raise Unknown(f"{what} is {n}, a negative count")
    return n


def build(day, traffic, answers_report):
    """traffic: the day's /ai/traffic file. answers_report: answers-by-day.build_report(...) for the same day.

    Raises Unknown when the traffic file has no `status` table (missing, renamed, not an object) or a count is not
    an integer: a confident "0 creates" from a file we could not read is the one wrong answer this tool can give.
    A status table without a "201" key is a day with no creates (0)."""
    if not isinstance(traffic, dict):
        raise Unknown(f"traffic file is a {type(traffic).__name__}, not an object")
    status = traffic.get("status")
    if not isinstance(status, dict):
        raise Unknown(f"traffic file has no status table (status={status!r})")
    creates = _count(status.get("201", 0), 'status["201"]')
    t = answers_report.get("totals") if isinstance(answers_report, dict) else None
    if not isinstance(t, dict):
        raise Unknown("answers report has no totals")
    asks, answers = _count(t.get("asks"), "totals.asks"), _count(t.get("answers"), "totals.answers")
    named = asks + answers  # ours included: our posts get a 201 too
    unexplained = max(0, creates - named)
    return {"day": day, "traffic_generated": traffic.get("generated_utc"), "complete_day": bool(traffic.get("complete_day")),
            "creates_201": creates, "asks": asks, "answers": answers, "named": named,
            "unexplained": unexplained, "more_named_than_created": named > creates,
            "possible_creators": CREATORS if unexplained else []}


def render(r):
    partial = "" if r["complete_day"] else " (partial day)"
    head = (f"{r['day']}{partial}: {r['creates_201']} creates (HTTP 201, traffic file {r['traffic_generated']}); "
            f"{r['named']} named = {r['asks']} asks + {r['answers']} answers, ours included.")
    lines = [head]
    if r["unexplained"]:
        lines.append(f"UNEXPLAINED {r['unexplained']}: created by somebody, counted by nobody. Not zero outside activity. "
                     "Possible creators:")
        lines += ["  " + c for c in r["possible_creators"]]
    elif r["more_named_than_created"]:
        lines.append("More asks/answers than 201s: the traffic file is partial or missed requests; no remainder to name.")
    else:
        lines.append("Every create is an ask or an answer already counted.")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("day", nargs="?", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not DAY.match(args.day):
        print(f"UNKNOWN: day {args.day!r} is not YYYY-MM-DD. Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    abd = _load_abd()
    try:
        traffic = fetch_json(TRAFFIC % args.day)
        asks_doc = abd.fetch(f"{abd.API}/asks")
        details = {int(a["id"]): abd.fetch(f"{abd.API}/ask/{a['id']}").get("ask", {}) for a in asks_doc.get("asks", [])}
    except (OSError, ValueError) as e:
        print(f"UNKNOWN: could not read a source ({e}). Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    try:
        r = build(args.day, traffic, abd.build_report(args.day, asks_doc, details))
    except Unknown as e:
        print(f"UNKNOWN: {e}. Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    print(json.dumps(r, indent=1) if args.json else render(r))


if __name__ == "__main__":
    main()
