#!/usr/bin/env python3
"""check-traffic-window: does the day's traffic file actually cover the day it names? Run before quoting it.

Found 2026-11-13 (challenge #264). At 04:07 UTC the box's `/ai/traffic/2026-11-13.json` counted 258 outside
requests from 50 clients for 00:00-04:00. At 08:07 the same file counted 103 requests from 24 clients, and its
`outside.first_utc` was 06:00:05: the six hours before it had left the file (every complete day before it,
11-10 to 11-12, starts at 00:00:0x). Nothing in the file says it is short. At 00:12 the next day the generator
marks the day `complete_day: true`, and the keeper copies that file's totals into the closed journal - so a day
whose early hours were dropped would be published as a full day with a third of its visits, read as "fewer
agents came", with no error anywhere. The generator and the access log are on the box (drafts/
box-traffic-file-drops-hours.md); this check is the part a keeper run can do: say which hours the file covers,
and refuse to call it the day's count when it does not cover the day.

It reads only `outside.first_utc`, `outside.last_utc`, `outside.requests`, `complete_day` and `generated_utc`.
A file starting more than GAP_HOURS after 00:00 (or, when complete, ending more than GAP_HOURS before 24:00) is
SHORT: the uncovered hours are UNKNOWN, never zero. A quiet hour can also start a file late; the file cannot
tell the two apart, so the verdict names both. `--previous N` is an earlier read of the same day's
`outside.requests` (the running journal records one each run): a day's count can only grow, so a smaller
number now is SHRANK.

    python3 ops/check-traffic-window.py [--json] [--previous N] [YYYY-MM-DD]   (default: today, UTC)
    python3 ops/check-traffic-window.py --file saved.json [--previous N]
    exit 0 covered; 1 SHORT or SHRANK; 2 UNKNOWN (unreadable file or fields)
"""
import argparse
import datetime
import json
import re
import sys
import urllib.request

TRAFFIC = "https://172-86-112-140.sslip.io/ai/traffic/%s.json"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
GAP_HOURS = 1.0
DAY = re.compile(r"\d{4}-\d{2}-\d{2}", re.ASCII)


class Unknown(Exception):
    """The file answered in a shape we cannot read: coverage is UNKNOWN, never 'covered'."""


def valid_day(day):
    if not isinstance(day, str) or not DAY.fullmatch(day):
        return False
    try:
        datetime.date.fromisoformat(day)
    except ValueError:
        return False
    return True


def _ts(value, what):
    if not isinstance(value, str):
        raise Unknown(f"{what} missing or not a string: {value!r}")
    try:
        t = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        raise Unknown(f"{what} is not an ISO time: {value!r}")
    if t.tzinfo is None:
        raise Unknown(f"{what} has no time zone: {value!r}")
    return t.astimezone(datetime.timezone.utc)


def build(traffic, previous=None):
    if not isinstance(traffic, dict):
        raise Unknown("traffic file is not a JSON object")
    day = traffic.get("date")
    if not valid_day(day):
        raise Unknown(f"date missing or malformed: {day!r}")
    out = traffic.get("outside")
    if not isinstance(out, dict):
        raise Unknown("outside block missing")
    req = out.get("requests")
    if not isinstance(req, int) or isinstance(req, bool) or req < 0:
        raise Unknown(f"outside.requests not a count: {req!r}")
    complete = traffic.get("complete_day") is True
    start = datetime.datetime.fromisoformat(day + "T00:00:00+00:00")
    end = start + datetime.timedelta(days=1)
    faults = []
    if req == 0:
        first = last = None
        if complete:
            faults.append("SHORT: a complete day with 0 outside requests - no hour is shown covered")
    else:
        first = _ts(out.get("first_utc"), "outside.first_utc")
        last = _ts(out.get("last_utc"), "outside.last_utc")
        if not (start <= first <= last < end):
            raise Unknown(f"first/last outside the day {day}: {first.isoformat()} .. {last.isoformat()}")
        lead = (first - start).total_seconds() / 3600
        if lead > GAP_HOURS:
            faults.append(f"SHORT: the file starts at {first.strftime('%H:%M:%S')} UTC; 00:00-{first.strftime('%H:%M')} "
                          "is UNKNOWN, not zero (dropped from the file, or nobody came - the file cannot tell)")
        if complete:
            tail = (end - last).total_seconds() / 3600
            if tail > GAP_HOURS:
                faults.append(f"SHORT: a complete day that ends at {last.strftime('%H:%M:%S')} UTC; the rest is UNKNOWN")
    if previous is not None and req < previous:
        faults.append(f"SHRANK: {previous} outside requests at an earlier read, {req} now - a day's count only grows, "
                      "so hours were dropped")
    return {"day": day, "generated_utc": traffic.get("generated_utc"), "complete_day": complete,
            "requests": req, "first_utc": first.isoformat() if first else None,
            "last_utc": last.isoformat() if last else None, "previous": previous, "faults": faults}


def render(r):
    span = f"{r['first_utc']} .. {r['last_utc']}" if r["first_utc"] else "no outside request"
    head = (f"{r['day']} ({'complete' if r['complete_day'] else 'partial'} day, file {r['generated_utc']}): "
            f"{r['requests']} outside requests, covering {span}")
    if not r["faults"]:
        return head + "\ncovered: the file's numbers can be quoted as the day's (so far)"
    return "\n".join([head] + ["- " + f for f in r["faults"]] +
                     ["Quote these numbers only with the window they cover; never as the whole day's."])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("day", nargs="?")
    ap.add_argument("--file")
    ap.add_argument("--previous", type=int)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        if a.file:
            with open(a.file) as f:
                traffic = json.load(f)
        else:
            day = a.day or datetime.datetime.now(datetime.timezone.utc).date().isoformat()
            if not valid_day(day):
                raise Unknown(f"not a day: {day!r}")
            req = urllib.request.Request(TRAFFIC % day, headers={"User-Agent": UA, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                traffic = json.load(resp)
        r = build(traffic, a.previous)
    except (Unknown, OSError, ValueError) as e:
        print(f"UNKNOWN: {e}")
        return 2
    print(json.dumps(r, indent=1) if a.json else render(r))
    return 1 if r["faults"] else 0


if __name__ == "__main__":
    sys.exit(main())
