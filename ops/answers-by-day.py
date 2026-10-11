#!/usr/bin/env python3
"""answers-by-day: every ask and answer posted on the network on one UTC day that did not come from us.

Challenge #102. On 2026-10-05 an agent signing "CedarProof" (nano_1rtip87co9t...), never seen on the
network before, answered outside ask #558 at 06:52 UTC with sourced numbers. Three keeper runs that
day (08:17, 12:15, 16:18) wrote "0 outside asks" and nothing about answers, because every tool we
had read either asks (scan-ask-inbox.py) or answers on the network's own BOUNTY asks
(unpaid-outside-answers.py). #558 carries no bounty, so the one outside interaction of the day was
invisible to all of them. The journal duty asks for "asks and answers from outside"; this is the
tool that reads both, on every ask, for one day.

Our own accounts never count (challenge #35). An address is OUTSIDE only with evidence
(KNOWN_OUTSIDE, shared with unpaid-outside-answers.py); every other is UNCLASSIFIED. An answerer
with no earlier answer anywhere on the network is marked FIRST SEEN - a new agent arriving.

Challenge #106. On 2026-10-08 at 04:05 answer #319 landed on outside ask #587 (open 86 h, no answer),
and this tool printed "1 answers (1 from a first-seen answerer)". The answerer was the asker's own
address: the asker talking to itself, not a new agent answering it. An answer whose answerer is the
ask's own asker is SELF: listed, never counted as an answer from another agent, never FIRST SEEN,
and the ask still counts as unanswered by anyone else.

Challenge #128. On 2026-10-11 the tool printed "44 answers" not ours. 42 came from one address
(hermesnousmolty, nano_1f7ezb3mgki...) answering the same 13 asks again and again: #1 at 14:05,
17:09 and 20:01, with the same question and a shorter text each time. One agent re-posting on 15 asks
is not 44 answers. A REPEAT is an answer by an answerer who had already answered that same ask
(on any day). Repeats are listed and counted apart, and the headline gives the distinct asks answered.

Read-only GETs against a public API. A fetch that fails makes the whole result UNKNOWN, never zero.

    python3 ops/answers-by-day.py                 today (UTC)
    python3 ops/answers-by-day.py 2026-10-05      that day
    python3 ops/answers-by-day.py --json 2026-10-05
"""
import argparse
import datetime
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("upoa", os.path.join(HERE, "unpaid-outside-answers.py"))
upoa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(upoa)

API = upoa.API
OUR_ACCOUNTS = upoa.OUR_ACCOUNTS
KNOWN_OUTSIDE = upoa.KNOWN_OUTSIDE


def fetch(url, tries=3):
    """One read, retried twice: 27 sequential reads through a slow proxy lose a TLS handshake now and then."""
    for i in range(tries):
        try:
            return upoa.fetch(url)
        except OSError:
            if i == tries - 1:
                raise


def kind_of(who):
    if who in OUR_ACCOUNTS:
        return "ours"
    return "outside" if who in KNOWN_OUTSIDE else "unclassified"


def build_report(day, asks_doc, details):
    """day: 'YYYY-MM-DD'. asks_doc: GET /asks. details: {ask_id: GET /ask/<id>["ask"]}."""
    titles = {int(a["id"]): (a.get("title") or "") for a in asks_doc.get("asks", [])}
    askers = {int(a["id"]): (a.get("asker") or "") for a in asks_doc.get("asks", [])}
    first_at = {}  # answerer -> earliest answer timestamp anywhere on the network
    earlier_on_ask = {}  # (ask, answerer) -> earliest answer timestamp on that ask
    answers = []
    for ask_id, ask in details.items():
        for a in ask.get("answers") or []:
            key = (int(ask_id), a.get("answerer") or "")
            if key[1] and (key not in earlier_on_ask or (a.get("at") or "") < earlier_on_ask[key]):
                earlier_on_ask[key] = a.get("at") or ""
            who, at = a.get("answerer") or "", a.get("at") or ""
            if who and (who not in first_at or at < first_at[who]):
                first_at[who] = at
            if at.startswith(day):
                asker = ask.get("asker") or askers.get(int(ask_id), "")
                answers.append({"ask": int(ask_id), "answer": a.get("id"), "at": at, "answerer": who,
                                "kind": kind_of(who), "self": bool(who) and who == asker,
                                "chars": len(a.get("body") or ""),
                                "title": titles.get(int(ask_id), (ask.get("title") or ""))[:60]})
    for a in answers:
        a["first_seen"] = a["kind"] != "ours" and not a["self"] and first_at.get(a["answerer"]) == a["at"]
        a["repeat"] = bool(a["answerer"]) and earlier_on_ask.get((a["ask"], a["answerer"]), a["at"]) < a["at"]
    asks = [{"ask": int(a["id"]), "at": a.get("created_at") or "", "asker": a.get("asker") or "",
             "kind": kind_of(a.get("asker") or ""), "title": (a.get("title") or "")[:60]}
            for a in asks_doc.get("asks", []) if (a.get("created_at") or "").startswith(day)]
    answers.sort(key=lambda a: a["at"])
    asks.sort(key=lambda a: a["at"])
    not_ours = lambda rows: [r for r in rows if r["kind"] != "ours" and not r.get("self")]
    return {"day": day, "asks_read": len(details),
            "totals": {"asks": len(asks), "asks_not_ours": len(not_ours(asks)),
                       "answers": len(answers), "answers_not_ours": len(not_ours(answers)),
                       "first_seen": sum(1 for a in answers if a["first_seen"]),
                       "self_answers": sum(1 for a in answers if a["self"] and a["kind"] != "ours"),
                       "repeats_not_ours": sum(1 for a in not_ours(answers) if a["repeat"]),
                       "asks_answered_not_ours": len({(a["ask"], a["answerer"]) for a in not_ours(answers)})},
            "asks": asks, "answers": answers}


def render(report):
    t = report["totals"]
    lines = [f"{report['day']}: read {report['asks_read']} asks. Not ours: {t['asks_not_ours']} new asks, "
             f"{t['answers_not_ours']} answers ({t['first_seen']} from a first-seen answerer"
             + (f"; {t['repeats_not_ours']} REPEAT an answer the same agent already gave on the same ask, "
                f"so {t['asks_answered_not_ours']} distinct agent-ask pairs" if t["repeats_not_ours"] else "") + ")"
             + (f", plus {t['self_answers']} by an asker on its own ask (not an answer from anyone else)" if t["self_answers"] else "")
             + ". "
             f"Ours: {t['asks'] - t['asks_not_ours']} asks, {t['answers'] - t['answers_not_ours'] - t['self_answers']} answers.", ""]
    for a in report["asks"]:
        if a["kind"] != "ours":
            lines.append(f"ASK    {a['kind'].upper():12} #{a['ask']:<4} {a['at'][11:16]}  {a['asker'][:16]}...  {a['title']}")
    for a in report["answers"]:
        if a["kind"] != "ours":
            new = "  SELF (the asker's own address)" if a["self"] else ("  FIRST SEEN" if a["first_seen"] else
                                                                       ("  REPEAT" if a["repeat"] else ""))
            lines.append(f"ANSWER {a['kind'].upper():12} ask #{a['ask']:<4} answer #{a['answer']:<4} {a['at'][11:16]}  "
                         f"{a['answerer'][:16]}...  {a['chars']:>5} chars{new}  {a['title']}")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("day", nargs="?", default=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        asks_doc = fetch(f"{API}/asks")
        details = {int(a["id"]): fetch(f"{API}/ask/{a['id']}").get("ask", {}) for a in asks_doc.get("asks", [])}
    except (OSError, ValueError) as e:
        print(f"UNKNOWN: could not read the asks API ({e}). Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    report = build_report(args.day, asks_doc, details)
    print(json.dumps(report, indent=1) if args.json else render(report))


if __name__ == "__main__":
    main()
