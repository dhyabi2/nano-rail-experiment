#!/usr/bin/env python3
"""scan-ask-inbox: read the live ask network and surface what needs a human or the swarm to act on.

Challenge #60 gave every canon confirmation and referral claim a door to knock on: POST an ask
titled "canon confirmation" or "referral claim" to https://getunstuck.space/unstuck/api/ask.
Nothing on our side ever reads that door. Measured live on 2026-09-28: ask #578, a genuine,
correctly-formed canon confirmation from an independent, financially active agent
(nano_3uojbn47b5xqcbs..., 89 chain blocks, ~29.8 XNO balance - not one of ours, never funded by
us), has sat open with zero answers for 37+ hours. Its own ask #577, a real paid-service offer,
sat beside it just as unanswered. The door works. Nobody is reading what comes through it.

This tool is the read: it fetches every ask, throws out our own (the treasury account asks
questions on this network too, and those are not outside activity - see challenge #35, "our own
findings were being counted as their answers"), classifies what is left, checks a cited canon
hash against the pinned value, and prints a plain report of what is waiting - oldest first - so
a human or the swarm's next pass has something to act on instead of a JSON blob nobody opens.

It never pays anything, never posts anything, never touches a key or a seed. It is a read-only
GET against a public API, safe to run as often as anyone likes.

    python3 ops/scan-ask-inbox.py            human-readable report, oldest-pending first
    python3 ops/scan-ask-inbox.py --json     the same data as JSON, for a future automated pass
"""
import argparse
import calendar
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ASKS_URL = os.environ.get("UNSTUCK_ASKS_URL", "https://getunstuck.space/unstuck/api/asks")
TREASURY = os.environ.get(
    "TREASURY_ACCOUNT",
    "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9",
)
CANON_SHA256 = "a18d406e312aab6af7471eb1f3a4d18e27b1a2fd1e42c84eef3c233350edbb6c"
SHA256_RE = re.compile(r"\b[0-9a-f]{64}\b")
BOUNTIES_TXT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "published", "bounties.txt")
# One gate-log entry in bounties.txt section 2: "#578  posted ..." then "PASSED, judged 2026-10-01 ..."
GATE_ENTRY_RE = re.compile(r"^\s+#(\d+)\s+posted .*\n\s+(PASSED|REFUSED), judged (\d{4}-\d{2}-\d{2})", re.M)


def gate_log(text=None):
    """The verdicts we have published (challenge #73). {ask_id: (verdict, judged_date)}.
    A confirmation is only off the pending list once its verdict is in the file a stranger reads."""
    if text is None:
        with open(BOUNTIES_TXT) as f:
            text = f.read()
    return {int(m.group(1)): (m.group(2), m.group(3)) for m in GATE_ENTRY_RE.finditer(text)}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "hunter-ask-scan/1"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def age_hours(created_at):
    """UTC always - the same calendar.timegm() discipline challenge #55 had to add to
    referral_bounty.py after time.mktime() silently read a naive struct as local time."""
    if not created_at:
        return None
    t = time.strptime(created_at[:19], "%Y-%m-%dT%H:%M:%S")
    return (time.time() - calendar.timegm(t)) / 3600.0


def classify(ask):
    title = (ask.get("title") or "").lower()
    if "canon confirmation" in title or "canon read" in title:
        return "canon_confirmation"
    if "referral claim" in title:
        return "referral_claim"
    bounty = ask.get("bountyRaw") or "0"
    if bounty not in ("0", 0) and ask.get("asker") != TREASURY:
        return "paid_service_ask"
    return "other"


def canon_hash_status(body):
    hashes = set(SHA256_RE.findall(body or ""))
    if not hashes:
        return "no_hash_cited"
    if CANON_SHA256 in hashes:
        return "matches_pin"
    return "mismatch(" + ",".join(sorted(h[:12] + "…" for h in hashes)) + ")"


def confirmation_parts_present(body):
    """Rough, honest check only - this never decides anything, it just tells a human reader
    what to look for. a)-d) as specified in published/bounties.txt section 2."""
    b = (body or "").lower()
    return {
        "a_which_line": bool(re.search(r"\bline\s*[1-5]\b|matters most", b)),
        "b_disagree": bool(re.search(r"disagree|change|rewrite", b)),
        "c_hash": bool(SHA256_RE.search(body or "")),
        "d_commits": bool(re.search(r"commit|own key|never hand", b)),
    }


def is_pending(ask):
    return (
        ask.get("status") == "open"
        and not ask.get("acceptedAnswerId")
        and not ask.get("settlementBlock")
        and int(ask.get("answerCount") or 0) == 0
    )


def build_report(data=None, judged=None):
    if data is None:
        data = fetch(ASKS_URL)
    if judged is None:
        judged = gate_log()
    asks = data.get("asks", data if isinstance(data, list) else [])
    rows = []
    for ask in asks:
        if ask.get("asker") == TREASURY:
            continue  # ours - see challenge #35, never count our own asks as outside activity
        kind = classify(ask)
        if kind == "other":
            continue
        row = {
            "id": ask.get("id"),
            "kind": kind,
            "asker": ask.get("asker"),
            "title": ask.get("title"),
            "status": ask.get("status"),
            "answer_count": ask.get("answerCount"),
            "settlement_block": ask.get("settlementBlock"),
            "age_hours": round(age_hours(ask.get("created_at")) or -1, 1),
            "pending": is_pending(ask),
        }
        if kind == "canon_confirmation":
            row["hash"] = canon_hash_status(ask.get("body"))
            row["parts"] = confirmation_parts_present(ask.get("body"))
            verdict = judged.get(ask.get("id"))
            row["verdict"] = verdict[0] if verdict else None
            if verdict:
                row["pending"] = False  # judged in public; no reply on the ask is needed for that
        rows.append(row)
    rows.sort(key=lambda r: (-r["pending"], -(r["age_hours"] or 0)))
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    try:
        rows = build_report()
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # a source that cannot be read reports unknown, never zero - challenge #39
        print(json.dumps({"error": "unreachable", "detail": str(e)}))
        return 1

    if args.json:
        print(json.dumps(rows, indent=2))
        return 0

    pending = [r for r in rows if r["pending"]]
    print(f"{len(rows)} outside canon/referral/paid-service ask(s), {len(pending)} pending (open, unanswered, unsettled)\n")
    for r in rows:
        flag = "PENDING" if r["pending"] else (r.get("verdict") or "handled")
        print(f"#{r['id']:<5} {flag:<8} {r['age_hours']:>6.1f}h  {r['kind']:<18} {r['asker'][:24]}  {r['title'][:60]}")
        if r["kind"] == "canon_confirmation":
            print(f"       hash: {r['hash']}  parts: {r['parts']}  gate log: {r.get('verdict') or 'NOT JUDGED'}")
    if pending:
        print(f"\n{len(pending)} item(s) above have had zero response since they were posted. "
              "Nothing in this repository reads this inbox automatically - see challenge #60's "
              "'still partial' note. A human or the swarm should read the oldest ones first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
