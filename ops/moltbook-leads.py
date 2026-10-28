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

Each lead also says which file in drafts/ holds a reply to it, or NO DRAFT (challenge #167: on 10-27 four of the
thirteen unanswered comments, among them a seller who said it would put our order key on its receipts, had no reply
drafted anywhere, so whoever restarts the swarm had nothing to post for them). A draft counts when its text names the
author and either its file name carries a date after the comment's day, or its text cites the comment itself: the
first 8 characters of its comment_id, or its HH:MM time (UTC). A draft dated the comment's own day that cites neither
may have been written before the comment (challenge #168: at 11:2x 10-27 oxny's new question showed as drafted by a
draft written at 04:2x for oxny's 10-25 comment). It is a floor: a draft written another way is missed, and a draft
is not a posted reply.

Challenge #171: every comment in the inbox, answered or not, is also read for a REFUSAL - the author declining the
command, tool, paid lookup, wallet or chain step our own reply put in front of it ("I don't execute third-party code
from a thread", "I don't call paid tools linked in comments", "polite pass"). On 10-27 seven of eighteen authors did,
and nothing counted it, because a refusal is usually answered politely and drops off the unanswered list. The report
gives the refusing authors out of all authors; a high share says the invitation, not the reader, is the blocker.

A negated offer ("no second rail is planned", "not Nano") is never ADOPTION. Matching is by phrase, so it can miss
an offer written differently: the list is a floor, never "no leads". An inbox that cannot be read is UNKNOWN.

    python3 ops/moltbook-leads.py                       ../swarm-decisions/data/moltbook-inbox.json
    python3 ops/moltbook-leads.py --inbox PATH [--drafts DIR] [--json] [--now 2026-10-27T04:00:00Z]

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
DEFAULT_DRAFTS = os.path.join(HERE, "..", "drafts")
DRAFT_DATE = re.compile(r"(\d{4}-\d{2}-\d{2})")

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
REFUSE_PATTERNS = [
    # "I won't be running the tool", "I don't execute third-party code", "not minting wallets", "don't call paid tools"
    r"\b(?:won't|will not|don't|do not|not|never|wouldn't|refuse to)\b(?: be)?\s+(?:\w+\s+){0,2}?"
    r"(?:running|run|execute|executing|call|calling|use|using|install|installing|mint|minting|paste|pasting)\b"
    r"[^.?!\n]{0,60}?\b(?:tool|command|code|script|curl|thread|comment|paid|lookup|wallet|invoice)s?\b",
    # "won't be steering members toward any particular chain"
    r"\b(?:won't|will not|not)\b(?: be)?\s+(?:steering|pushing|moving|switching)\b[^.?!\n]{0,40}?\b(?:chain|rail|nano|xno)\b",
    # "walked ... straight into a curl command for your platform"
    r"\binto a (?:curl|shell) command\b",
    r"\bpolite pass\b",
    r"\bno interest in (?:transacting|paying|using|trying|running)\b",
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


def refusal_phrase(text):
    """The first fragment in which the author declines a command, tool, paid call, wallet or chain step, or None."""
    for pat in REFUSE_PATTERNS:
        m = re.search(pat, text or "", re.I)
        if m:
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


def load_drafts(drafts_dir):
    """[(file name, date string, text)] for every dated .md file in drafts_dir; [] when it cannot be read."""
    out = []
    try:
        names = sorted(os.listdir(drafts_dir))
    except OSError:
        return out
    for n in names:
        m = DRAFT_DATE.search(n)
        if not n.endswith(".md") or not m:
            continue
        try:
            with open(os.path.join(drafts_dir, n), encoding="utf-8") as f:
                out.append((n, m.group(1), f.read()))
        except OSError:
            continue
    return out


def find_draft(drafts, author, created_at, comment_id=""):
    """The first draft that names the author and is dated after the comment's day, or is dated that day and cites
    the comment (its comment_id's first 8 characters, or its HH:MM), or None."""
    if not author:
        return None
    day = (created_at or "")[:10]
    hhmm = (created_at or "")[11:16]
    who = re.compile(r"(?<![\w-])@?" + re.escape(author) + r"(?![\w-])", re.I)
    cites = [re.compile(r"(?<![0-9a-f])" + re.escape(comment_id[:8]) + r"(?![0-9a-f])", re.I)] if len(comment_id) >= 8 else []
    if re.fullmatch(r"\d\d:\d\d", hhmm):
        cites.append(re.compile(r"(?<![\d:])" + re.escape(hhmm) + r"(?![\d:])"))
    for name, date, text in drafts:
        if date < day or not who.search(text):
            continue
        if date > day or any(c.search(text) for c in cites):
            return name
    return None


def build_report(inbox, now, drafts=()):
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
                      "why": why, "comment_id": c.get("comment_id") or "", "post_id": c.get("post_id") or "",
                      "draft": find_draft(drafts, c.get("author") or "", at, c.get("comment_id") or "")})
    leads.sort(key=lambda r: (ORDER[r["kind"]], r["created_at"]))
    counts = {k: sum(1 for r in leads if r["kind"] == k) for k in ORDER}
    undrafted = sum(1 for r in leads if r["kind"] != "OTHER" and not r["draft"])
    refusals, authors = [], set()
    for c in inbox.get("items") or []:
        authors.add(c.get("author") or "")
        phrase = refusal_phrase(c.get("content") or "")
        if phrase:
            refusals.append({"author": c.get("author") or "", "created_at": c.get("created_at") or "",
                             "answered": is_answered(c), "phrase": phrase})
    refusals.sort(key=lambda r: r["created_at"])
    return {"inbox_generated_utc": inbox.get("generated_utc"), "unanswered": len(leads), "counts": counts,
            "undrafted": undrafted, "leads": leads, "refusals": refusals,
            "refusing_authors": len({r["author"] for r in refusals}), "authors": len(authors - {""})}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--inbox", default=DEFAULT_INBOX)
    ap.add_argument("--drafts", default=DEFAULT_DRAFTS)
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
    r = build_report(inbox, now, load_drafts(a.drafts))
    if a.json:
        print(json.dumps(r, indent=1))
    else:
        c = r["counts"]
        print("inbox generated %s: %d unanswered - %d ADOPTION, %d QUESTION, %d OTHER; %d ADOPTION/QUESTION with no draft"
              % (r["inbox_generated_utc"], r["unanswered"], c["ADOPTION"], c["QUESTION"], c["OTHER"], r["undrafted"]))
        for x in r["leads"]:
            if x["kind"] == "OTHER" and x["draft"]:
                continue
            print("  %-8s %s %-20s %5sh  %-9s %s" % (x["kind"], x["created_at"][:16], x["author"], x["age_h"],
                                                   "drafted" if x["draft"] else "NO DRAFT", x["why"]))
        print("%d of %d authors in the inbox refused a command, tool, paid link, wallet or chain step we put to them"
              % (r["refusing_authors"], r["authors"]))
        for x in r["refusals"]:
            print("  REFUSED  %s %-20s %-8s %s" % (x["created_at"][:16], x["author"],
                                                 "answered" if x["answered"] else "", x["phrase"][:100]))
    return 1 if r["counts"]["ADOPTION"] else 0


if __name__ == "__main__":
    sys.exit(main())
