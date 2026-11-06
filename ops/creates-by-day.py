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
import http.client
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


DAY = re.compile(r"\d{4}-\d{2}-\d{2}", re.ASCII)


def valid_day(day):
    """True only for an exact ASCII YYYY-MM-DD that is a real calendar date. fullmatch, not `$`: `$` lets a
    trailing newline through and urllib then raises InvalidURL. re.ASCII: \\d would otherwise accept other
    scripts' digits. fromisoformat refuses 2026-02-30 and 0000-99-99."""
    if not isinstance(day, str) or not DAY.fullmatch(day):
        return False
    try:
        datetime.date.fromisoformat(day)
    except ValueError:
        return False
    return True


class Unknown(Exception):
    """A source answered in a shape we cannot read: the result is UNKNOWN, never a count of zero."""


def _count(value, what):
    """A count is a JSON integer >= 0 and nothing else. Strings are refused, because int() reads " 3\\n", "1_0"
    and Arabic-Indic digits as numbers a JSON writer never meant; bool is refused although it is an int subclass.
    No upper bound: any non-negative integer is a well-formed count, and a cap would be a guess that turns a
    real (if alarming) number into UNKNOWN."""
    if isinstance(value, bool) or not isinstance(value, int):
        raise Unknown(f"{what} is {value!r}, not a count")
    if value < 0:
        raise Unknown(f"{what} is {value}, a negative count")
    return value


def ask_ids(asks_doc):
    """The ask ids of GET /asks, or Unknown if the document is not {"asks": [{"id": <int>, ...}, ...]}."""
    if not isinstance(asks_doc, dict):
        raise Unknown(f"asks list is a {type(asks_doc).__name__}, not an object")
    # The key is required: {"error": "rate limited"} has no asks key and is a failed read, not a day of 0 asks.
    if "asks" not in asks_doc:
        raise Unknown(f"asks list has no asks key ({asks_doc!r:.80})")
    asks = asks_doc["asks"]
    if not isinstance(asks, list):
        raise Unknown(f"asks list has asks={asks!r:.80}, not a list")
    counts = asks_doc.get("counts")
    if isinstance(counts, dict) and "total" in counts:
        # A list shorter than its own total is truncated: the missing asks' answers would be silent zeros.
        total = _count(counts["total"], "asks counts.total")
        if total != len(asks):
            raise Unknown(f"asks list has {len(asks)} asks but counts.total={total} (truncated list)")
    ids = []
    for a in asks:
        if not isinstance(a, dict) or isinstance(a.get("id"), bool) or not isinstance(a.get("id"), int):
            raise Unknown(f"asks list has an entry {a!r:.80} without an integer id")
        if a["id"] in ids:
            # The same ask twice would be counted twice; a list that repeats itself is not one we can read.
            raise Unknown(f"asks list has ask id {a['id']} more than once")
        ids.append(a["id"])
    return ids


def answers_of(i, ask, seen):
    """The answers of one ask object, or Unknown. `answers` must be a list of objects with integer ids:
    {"error": "rate limited"} inside "ask" is a failed read, not 0 answers. `seen` holds every answer id read so far;
    an id listed twice (on this ask or another) would be counted twice."""
    answers = ask.get("answers")
    if not isinstance(answers, list):
        raise Unknown(f"ask {i} has answers={answers!r:.80}, not a list")
    for a in answers:
        aid = a.get("id") if isinstance(a, dict) else None
        if isinstance(aid, bool) or not isinstance(aid, int):
            raise Unknown(f"ask {i} has an answer {a!r:.80} without an integer id")
        if aid in seen:
            raise Unknown(f"answer id {aid} is listed more than once")
        seen.add(aid)
    return answers


def build(day, traffic, answers_report):
    """traffic: the day's /ai/traffic file. answers_report: answers-by-day.build_report(...) for the same day.

    Raises Unknown when the traffic file has no `status` table (missing, renamed, not an object) or a count is not
    an integer: a confident "0 creates" from a file we could not read is the one wrong answer this tool can give.
    A status table without a "201" key is a day with no creates (0)."""
    if not isinstance(traffic, dict):
        raise Unknown(f"traffic file is a {type(traffic).__name__}, not an object")
    if "date" in traffic and traffic["date"] != day:
        raise Unknown(f"traffic file is dated {traffic['date']!r:.40}, not {day}")
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
    # complete_day counts as complete only when it is literally true: "false", 1, null or a missing key are a
    # partial day. Saying "partial" of a complete day costs a caveat; the reverse would hide missing requests.
    return {"day": day, "traffic_generated": traffic.get("generated_utc"), "complete_day": traffic.get("complete_day") is True,
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
    if not valid_day(args.day):
        print(f"UNKNOWN: day {args.day!r} is not YYYY-MM-DD. Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    abd = _load_abd()
    try:
        traffic = fetch_json(TRAFFIC % args.day)
        asks_doc = abd.fetch(f"{abd.API}/asks")
        details, seen_answers = {}, set()
        for i in ask_ids(asks_doc):
            doc = abd.fetch(f"{abd.API}/ask/{i}")
            # Required, like "asks": an error document without "ask" is a failed read, never an empty ask.
            ask = doc.get("ask") if isinstance(doc, dict) else None
            if not isinstance(ask, dict):
                raise Unknown(f"ask {i} has no ask object ({doc!r:.80})")
            answers_of(i, ask, seen_answers)
            details[i] = ask
    except Unknown as e:
        print(f"UNKNOWN: {e}. Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    except (OSError, ValueError, http.client.HTTPException, RecursionError) as e:
        print(f"UNKNOWN: could not read a source ({type(e).__name__}: {e!s:.200}). Nothing is measured - not zero.",
              file=sys.stderr)
        sys.exit(2)
    try:
        r = build(args.day, traffic, abd.build_report(args.day, asks_doc, details))
    except Unknown as e:
        print(f"UNKNOWN: {e}. Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    except (TypeError, ValueError, KeyError, AttributeError, RecursionError) as e:
        # build_report assumes the network's shapes; an answer that is not an object, say, lands here.
        print(f"UNKNOWN: a source has a shape this tool cannot read ({type(e).__name__}: {e!s:.200}). Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    if args.json:
        try:
            # Strict JSON: NaN/Infinity from a source (say generated_utc) is not JSON and no reader should get it.
            out = json.dumps(r, indent=1, allow_nan=False)
        except ValueError as e:
            print(f"UNKNOWN: a source holds a non-finite number ({e!s:.200}). Nothing is measured - not zero.", file=sys.stderr)
            sys.exit(2)
        print(out)
    else:
        print(render(r))


if __name__ == "__main__":
    main()
