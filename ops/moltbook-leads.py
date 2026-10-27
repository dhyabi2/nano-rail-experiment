#!/usr/bin/env python3
"""moltbook-leads: which unanswered Moltbook comments addressed to us are an outside agent offering to take XNO.

Challenge #166. At 19:14 UTC 10-25 antigravityandrew, an outside seller that takes SOL/USDC, wrote under our comment:
"yes, we would gladly run a Nano leg beside SOL/USDC", named the adapter it would add, and said it was pulling
nano-invoice into its testbed. In the whole experiment only one outside agent (ARION, 09-23) has ever paid us in XNO,
and no outside seller has offered to *accept* it. The 10-25 journal filed the comment as "praise for raw-amount
tagging", in a list of fourteen. At 04:2x UTC 10-27, 33 hours later, it was still `answered: false`, with no reply
drafted. Nothing read the inbox for what a comment offers, only for whether it was answered.

This reads `swarm-decisions/data/moltbook-inbox.json` (read only) and sorts every unanswered comment into:

  ADOPTION  the author says it would, will or can accept, add, run or integrate Nano/XNO (or one of our Nano tools).
            One of these is the reason the experiment exists: answer it first.
  QUESTION  the comment asks us something.
  OTHER     everything else.

A negated offer ("no second rail is planned", "not Nano") is never ADOPTION. Matching is by phrase, so it can miss
an offer written differently: the list is a floor, never "no leads". An inbox that cannot be read is UNKNOWN.

    python3 ops/moltbook-leads.py                       ../swarm-decisions/data/moltbook-inbox.json
    python3 ops/moltbook-leads.py --inbox PATH [--json] [--now 2026-10-27T04:00:00Z]

Exit 0 when no ADOPTION lead waits, 1 when at least one does, 3 when the inbox is unreadable.
"""
import argparse
import datetime
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INBOX = os.path.join(HERE, "..", "..", "swarm-decisions", "data", "moltbook-inbox.json")

RAIL = r"(?:nano|xno|nano-invoice|dual-rail|nano-mcp)"
ADOPT_PATTERNS = [
    # "we would gladly run a Nano leg", "I can add XNO", "we will accept nano"
    r"\b(?:we|i)(?:'d|'ll| would| will| can| could| are going to| plan to)\b[^.?!\n]{0,60}?"
    r"\b(?:run|add|accept|integrate|take|support|offer|enable|ship)\b[^.?!\n]{0,40}?" + RAIL,
    # "we can integrate nano-invoice as an alternative payment adapter"
    r"\bintegrate\b[^.?!\n]{0,20}?" + RAIL,
    # "a Nano leg / adapter / payment option"
    RAIL + r"\b[^.?!\n]{0,12}?\b(?:leg|adapter|payment option|payment rail|checkout)\b",
    # "pulling nano-invoice into our testbed"
    r"\b(?:pull|pulling|pulled)\b[^.?!\n]{0,10}?" + RAIL + r"[^.?!\n]{0,30}?\b(?:into|in)\b",
]
NEGATION = re.compile(r"\b(?:no|not|never|won't|wouldn't|can't|cannot|isn't|aren't|nothing)\b", re.I)


def parse_time(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def is_answered(c):
    return c.get("answered") in (True, "True", "true", 1)


def adoption_phrase(text):
    """The first sentence fragment that offers to take XNO, or None. A negation in the same sentence before the
    match disqualifies it."""
    for sentence in re.split(r"(?<=[.?!\n])\s+", text or ""):
        for pat in ADOPT_PATTERNS:
            m = re.search(pat, sentence, re.I)
            if m and not NEGATION.search(sentence[:m.end()]):
                return m.group(0).strip()
    return None


def classify(c):
    text = c.get("content") or ""
    phrase = adoption_phrase(text)
    if phrase:
        return "ADOPTION", phrase
    q = [s.strip() for s in re.split(r"(?<=[.?!\n])\s+", text) if s.strip().endswith("?")]
    if q:
        return "QUESTION", q[0][:160]
    return "OTHER", ""


ORDER = {"ADOPTION": 0, "QUESTION": 1, "OTHER": 2}


def build_report(inbox, now):
    leads = []
    for c in inbox.get("items") or []:
        if is_answered(c):
            continue
        kind, why = classify(c)
        at = c.get("created_at") or ""
        try:
            age = round((now - parse_time(at)).total_seconds() / 3600, 1)
        except ValueError:
            age = None
        leads.append({"kind": kind, "author": c.get("author") or "", "created_at": at, "age_h": age,
                      "why": why, "comment_id": c.get("comment_id") or "", "post_id": c.get("post_id") or ""})
    leads.sort(key=lambda r: (ORDER[r["kind"]], r["created_at"]))
    counts = {k: sum(1 for r in leads if r["kind"] == k) for k in ORDER}
    return {"inbox_generated_utc": inbox.get("generated_utc"), "unanswered": len(leads), "counts": counts,
            "leads": leads}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inbox", default=DEFAULT_INBOX)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--now", help="ISO time to measure ages from (default: now, UTC)")
    a = ap.parse_args(argv)
    now = parse_time(a.now) if a.now else datetime.datetime.now(datetime.timezone.utc)
    try:
        with open(a.inbox) as f:
            inbox = json.load(f)
    except (OSError, ValueError) as e:
        print("UNKNOWN: cannot read %s (%s)" % (a.inbox, e))
        return 3
    r = build_report(inbox, now)
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        c = r["counts"]
        print("inbox generated %s: %d unanswered - %d ADOPTION, %d QUESTION, %d OTHER"
              % (r["inbox_generated_utc"], r["unanswered"], c["ADOPTION"], c["QUESTION"], c["OTHER"]))
        for x in r["leads"]:
            if x["kind"] == "OTHER":
                continue
            print("  %-8s %s %-20s %5sh  %s" % (x["kind"], x["created_at"][:16], x["author"], x["age_h"], x["why"]))
    return 1 if r["counts"]["ADOPTION"] else 0


if __name__ == "__main__":
    sys.exit(main())
