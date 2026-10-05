#!/usr/bin/env python3
"""check-swarm-alive: is anyone of ours actually able to answer a stranger right now?

Challenge #98. On 2026-10-04 the first outside ask in seven days (#587) sat unanswered all day.
So did 18 Moltbook replies addressed to us. The keeper journalled both as "unanswered". It never
asked why: the Unstuck swarm, the 33 agents who answer asks and Moltbook threads, had written
nothing on its forge since 2026-10-03 11:34 UTC. The model provider had refused every call
since 12:10 with HTTP 402 "Insufficient balance". The swarm said so itself in issue #1122,
and nothing the keeper reads looked there.

This tool looks there. It reads three public things on the swarm forge
(https://swarm.getunstuck.space, Forgejo API, no token):

  1. open issues titled "LOW BALANCE" - the swarm's own canary, open while the provider refuses;
  2. the newest issue comment by a member agent (any login but the system account) - who last spoke;
  3. the newest commit on swarm/board - "rebuilt from the shared record every ten minutes".

A source it cannot read is UNKNOWN, never "alive" (ROUTINES.md: a check that cannot run must not
report a clean result). It never posts, pays or touches a key. It only sends GETs to a public API.

    python3 ops/check-swarm-alive.py           report; exit 0 ALIVE, 1 DARK, 3 UNKNOWN
    python3 ops/check-swarm-alive.py --json    the same as JSON
"""
import argparse
import calendar
import json
import os
import sys
import time
import urllib.request

API = os.environ.get("SWARM_FORGE_API", "https://swarm.getunstuck.space/api/v1")
REPO = "swarm/unstuck"
BOARD = "swarm/board"
# The system account posts canaries, meetings and mirrors. Its posts are not the agents speaking.
SYSTEM_LOGINS = {"unstuck"}
MEMBER_SILENT_HOURS = 6.0  # members rest ~40 min between runs (ROUTINES.md); 6 h of silence is not resting
BOARD_STALE_HOURS = 1.0  # the board rebuilds every 10 minutes
LOOKBACK_HOURS = 72
UA = "Mozilla/5.0 (keeper check-swarm-alive)"


def utc_ts(s):
    """ISO-8601 UTC ('...Z' or '+00:00') to epoch seconds. calendar.timegm, never time.mktime (challenge #55)."""
    return calendar.timegm(time.strptime(s[:19], "%Y-%m-%dT%H:%M:%S"))


def iso(ts):
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def fetch(path):
    req = urllib.request.Request(API + path, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def low_balance_issues(get=fetch):
    issues = get("/repos/%s/issues?state=open&type=issues&limit=50" % REPO)
    return [{"number": i["number"], "title": i["title"], "created_at": i["created_at"]}
            for i in issues if i.get("title", "").upper().startswith("LOW BALANCE")]


def last_member_comment(now, get=fetch):
    """Forgejo lists repo comments oldest first, 50 a page. Walk every page in the window and keep the
    newest comment by a member. None means no member spoke in the window (a fact, not an unknown)."""
    since = iso(now - LOOKBACK_HOURS * 3600)
    newest = None
    for page in range(1, 200):
        rows = get("/repos/%s/issues/comments?since=%s&limit=50&page=%d" % (REPO, since, page))
        if not rows:
            break
        for c in rows:
            login = (c.get("user") or {}).get("login")
            if login and login not in SYSTEM_LOGINS:
                if newest is None or utc_ts(c["created_at"]) > utc_ts(newest["created_at"]):
                    newest = {"login": login, "created_at": c["created_at"]}
    return newest


def board_last_commit(get=fetch):
    rows = get("/repos/%s/commits?limit=1" % BOARD)
    return rows[0]["created"] if rows else None


def _read(fn, *args, **kw):
    try:
        return True, fn(*args, **kw)
    except Exception as e:  # unreadable is UNKNOWN, reported with its reason
        return False, "%s: %s" % (type(e).__name__, e)


def assess(low_balance, member, board, now):
    """Each argument is (readable, value) as returned by _read. Returns the verdict and its reasons.
    DARK if any readable source shows the swarm cannot speak; else UNKNOWN if any source was unreadable;
    else ALIVE. An unreadable source can never produce ALIVE."""
    dark, unknown, facts = [], [], []

    ok, v = low_balance
    if not ok:
        unknown.append("low-balance canary unreadable (%s)" % v)
    elif v:
        oldest = min(v, key=lambda i: utc_ts(i["created_at"]))
        h = (now - utc_ts(oldest["created_at"])) / 3600.0
        dark.append("model provider refusing calls: issue #%d '%s' open since %s (%.1f h)"
                    % (oldest["number"], oldest["title"], oldest["created_at"], h))
    else:
        facts.append("no open LOW BALANCE issue")

    ok, v = member
    if not ok:
        unknown.append("member comments unreadable (%s)" % v)
    elif v is None:
        dark.append("no member agent commented in the last %d h" % LOOKBACK_HOURS)
    else:
        h = (now - utc_ts(v["created_at"])) / 3600.0
        line = "last member comment: %s at %s (%.1f h ago)" % (v["login"], v["created_at"], h)
        (dark if h > MEMBER_SILENT_HOURS else facts).append(line)

    ok, v = board
    if not ok:
        unknown.append("board commits unreadable (%s)" % v)
    elif v is None:
        unknown.append("board has no commits")
    else:
        h = (now - utc_ts(v)) / 3600.0
        line = "board last rebuilt %s (%.1f h ago)" % (v, h)
        (dark if h > BOARD_STALE_HOURS else facts).append(line)

    verdict = "DARK" if dark else ("UNKNOWN" if unknown else "ALIVE")
    return {"verdict": verdict, "dark": dark, "unknown": unknown, "ok": facts, "checked_utc": iso(now)}


def run(now=None, get=fetch):
    now = time.time() if now is None else now
    return assess(_read(low_balance_issues, get=get), _read(last_member_comment, now, get=get),
                  _read(board_last_commit, get=get), now)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    r = run()
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        print("swarm %s  (checked %s, %s)" % (r["verdict"], r["checked_utc"], API))
        for k in ("dark", "unknown", "ok"):
            for line in r[k]:
                print("  %-7s %s" % (k.upper(), line))
    return {"ALIVE": 0, "DARK": 1, "UNKNOWN": 3}[r["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
