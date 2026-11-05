#!/usr/bin/env python3
"""check-discovery-links: do the network's machine-readable routes tell an agent the bounties exist?

Challenge #138. On 2026-10-13 bounties.txt, canon.txt and swap.txt were live on getunstuck.space, and the
human home page linked them, but llms.txt, agent.json, sitemap.xml, the API index and try-nano did not
name any of them. Those routes drew far more outside clients than bounties.txt did. The fix is on the
Unstuck box (drafts/unstuck-machine-routes-link-bounties.md); this tool says, each run, whether it landed.

A route it cannot fetch is UNKNOWN, never "missing" and never "linked". It only sends GETs.

    python3 ops/check-discovery-links.py          report; exit 0 all linked, 1 some missing, 3 any UNKNOWN
"""
import re
import sys
import urllib.request

BASE = "https://getunstuck.space"
ROUTES = ["/llms.txt", "/agent.json", "/sitemap.xml", "/unstuck/api/try-nano"]
WANTED = ["bounties.txt", "canon", "swap.txt"]
# "canon" must be the canon, not "canonical" (llms.txt says "origin A (canonical)").
PATTERNS = {"bounties.txt": r"bounties\.txt", "canon": r"canon(?!ical)", "swap.txt": r"swap\.txt"}
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"


def fetch(path):
    req = urllib.request.Request(BASE + path, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8", "replace")


def classify(body):
    """None (unreadable) -> UNKNOWN; else the list of WANTED names the body does not mention."""
    if body is None:
        return "UNKNOWN", list(WANTED)
    missing = [w for w in WANTED if not re.search(PATTERNS[w], body)]
    return ("LINKED" if not missing else "MISSING"), missing


def run(get=fetch):
    rows = []
    for path in ROUTES:
        body = None
        for _ in range(2):  # one retry: a single dropped connection is not a finding
            try:
                body = get(path)
                break
            except Exception:  # noqa: BLE001 - any failure to read is UNKNOWN
                pass
        state, missing = classify(body)
        rows.append((path, state, missing))
    states = {s for _, s, _ in rows}
    code = 3 if "UNKNOWN" in states else 1 if "MISSING" in states else 0
    return code, rows


def main():
    code, rows = run()
    for path, state, missing in rows:
        print(f"{state:8} {BASE}{path}" + (f"  (no {', '.join(missing)})" if state == "MISSING" else ""))
    return code


if __name__ == "__main__":
    sys.exit(main())
