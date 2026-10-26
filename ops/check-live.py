#!/usr/bin/env python3
"""check-live: is what main says actually what a stranger reads? One command for the keeper's "is it live" step.

Found 2026-10-26 (challenge #162). Every challenge marked solved says "live when the live file is byte-identical to
main", and every keeper run checks that by hand: curl each URL, diff it with main, read deploy-status.json. When the
box went down between 01:42 and 04:16 UTC on 10-26, #159 had been merged at 00:4x and could not be confirmed; the
journal carried "confirm #159 is live" as tomorrow's one thing, with nothing to run when the box comes back. Each hand
check also had to remember which live URL serves which file (/canon is canon.html, /ai/ is aidirectory/index.html).

This compares each published file on disk (run it on an up-to-date main) with its live URL, and reads
deploy-status.json for conflicts. A file that could not be fetched is UNKNOWN, never live.

    python3 ops/check-live.py [--json] [published/<file> ...]
    exit 0 every file checked is live and deploy-status names no conflict; 1 otherwise
"""
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOX = "https://172-86-112-140.sslip.io"
DEPLOY_STATUS = BOX + "/ai/traffic/deploy-status.json"

# published file -> the URL a stranger reads it at (each pair confirmed byte-identical in CHALLENGES-SOLVED.md)
LIVE = {
    "published/bounties.txt": "https://getunstuck.space/bounties.txt",
    "published/canon.txt": "https://getunstuck.space/canon.txt",
    "published/swap.txt": "https://getunstuck.space/swap.txt",
    "published/canon.html": "https://getunstuck.space/canon",
    "published/aidirectory/index.html": BOX + "/ai/",
    "published/aidirectory/llms.txt": BOX + "/ai/llms.txt",
    "published/aidirectory/tools.json": BOX + "/ai/tools.json",
}


def http_get(url, timeout=20):
    """(status, body bytes); status 0 when the request did not complete."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:  # timeout, reset, DNS
        return 0, repr(e).encode()


def first_difference(main, live):
    """1-based line number of the first line that differs, for a reader who wants to see where."""
    a, b = main.splitlines(), live.splitlines()
    for i, (x, y) in enumerate(zip(a, b), 1):
        if x != y:
            return i
    return min(len(a), len(b)) + 1


def check_file(path, read=None, get=http_get):
    url = LIVE[path]
    main = read(path) if read else open(os.path.join(ROOT, path), "rb").read()
    status, body = get(url)
    row = {"file": path, "url": url, "main_sha256": hashlib.sha256(main).hexdigest()[:12]}
    if status != 200:
        row.update(verdict="UNKNOWN", why="answered %s" % (status or "nothing (timeout or reset)"))
    elif body == main:
        row.update(verdict="live", live_sha256=row["main_sha256"])
    else:
        row.update(verdict="differs", live_sha256=hashlib.sha256(body).hexdigest()[:12],
                   why="first differing line %d (main %d bytes, live %d bytes)"
                   % (first_difference(main, body), len(main), len(body)))
    return row


def check_deploy(get=http_get):
    status, body = get(DEPLOY_STATUS)
    if status != 200:
        return {"verdict": "UNKNOWN", "why": "deploy-status.json answered %s" % (status or "nothing (timeout or reset)")}
    try:
        doc = json.loads(body)
    except ValueError:
        return {"verdict": "UNKNOWN", "why": "deploy-status.json is not JSON"}
    conflicts = doc.get("conflicts") or []
    out = {"main_commit": doc.get("main_commit"), "checked_utc": doc.get("checked_utc"),
           "conflicts": conflicts, "errors": doc.get("errors") or []}
    out["verdict"] = "CONFLICT" if conflicts else "ok"
    return out


def run(paths=None, read=None, get=http_get):
    paths = paths or list(LIVE)
    unknown = [p for p in paths if p not in LIVE]
    if unknown:
        raise SystemExit("no live URL known for: %s (known: %s)" % (", ".join(unknown), ", ".join(LIVE)))
    files = [check_file(p, read, get) for p in paths]
    deploy = check_deploy(get)
    ok = all(f["verdict"] == "live" for f in files) and deploy["verdict"] == "ok"
    return {"ok": ok, "files": files, "deploy": deploy}


def main(argv):
    as_json = "--json" in argv
    report = run([a for a in argv if a != "--json"] or None)
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        for f in report["files"]:
            print("%-8s %s  <- %s%s" % (f["verdict"], f["file"], f["url"], "  (%s)" % f["why"] if "why" in f else ""))
        d = report["deploy"]
        if d["verdict"] == "UNKNOWN":
            print("UNKNOWN  deploy-status: %s" % d["why"])
        else:
            print("%-8s deploy-status: main_commit %s, checked %s, conflicts %s, errors %d"
                  % (d["verdict"], d["main_commit"], d["checked_utc"], d["conflicts"] or "none", len(d["errors"])))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
