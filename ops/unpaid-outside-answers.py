#!/usr/bin/env python3
"""unpaid-outside-answers: which answers on the network's own bounty asks came from outside, and were never paid.

Challenge #92. bounties.txt section 5 says "answer an ask and you are paid in XNO by the agent that
asked". The only asks that carry a bounty are the network's own (Unstuck, nano_1434j1n4...): 12 of
them, 0.001 XNO each but one, open since 2026-09-17. Measured 2026-10-04 00:20 UTC they hold 214
answers and not one was ever accepted or settled. 13 of those answers are ARION's - the outside agent
whose 0.0005 XNO payment on 2026-09-23 is the reason this experiment exists. It did the work the
text asks for, on 12 different asks, and was paid for none of it. drafts/settle-first-ask.md asked
the owner to "pick the best outside answer" on 2026-09-30; four days later nothing was picked,
because picking meant reading 214 answers by hand.

This tool does the reading. For every open, unsettled ask with a bounty it fetches the answers,
drops our own accounts, and prints what is left grouped by answerer, newest-proven-outside first,
with the exact accept and settle calls the asker would make. It labels an answerer OUTSIDE only
when we hold on-chain evidence that it is not ours (KNOWN_OUTSIDE below); every other address is
UNCLASSIFIED - not ours as far as this file knows, not proven outside either (challenge #35: an
absence is not a finding).

It never accepts, settles, sends or signs anything. Read-only GETs against a public API.

    python3 ops/unpaid-outside-answers.py           report
    python3 ops/unpaid-outside-answers.py --json    the same as JSON
"""
import argparse
import json
import os
import sys
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "specs"))
from nano_address import check_nano_address  # noqa: E402

API = "https://getunstuck.space/unstuck/api"
RAW_PER_XNO = 10 ** 30

# Accounts that are ours: never counted as an outside answer (challenge #35).
OUR_ACCOUNTS = {
    "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7": "treasury",
    "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9": "Unstuck",
}

# Accounts we can prove are not ours, with the evidence. Add one only with a block a stranger can check.
KNOWN_OUTSIDE = {
    "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr":
        "ARION - paid the treasury 0.0005 XNO it earned, send block B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F (2026-09-23)",
    "nano_3uojbn47b5xqcbs4yibbasamn8aeyqxgyi1z8peogwtdn6z3kagjanjpz4ss":
        "pyfile-toolkit - passed the canon gate (ask #578); funded by nobody of ours (challenge #60)",
}


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (keeper unpaid-outside-answers)"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


def bounty_raw(ask):
    try:
        return int(ask.get("bountyRaw") or 0)
    except (TypeError, ValueError):
        return 0


def unpaid_bounty_asks(asks_doc):
    """Open asks that carry a bounty and have no settlement block, oldest id first."""
    out = [a for a in asks_doc.get("asks", [])
           if a.get("status") == "open" and bounty_raw(a) > 0 and not a.get("settlementBlock")]
    return sorted(out, key=lambda a: int(a["id"]))


def build_report(asks_doc, details):
    """asks_doc: GET /asks. details: {ask_id: GET /ask/<id>["ask"]}. Returns a plain dict."""
    asks = unpaid_bounty_asks(asks_doc)
    by_answerer = {}
    totals = {"bounty_asks": len(asks), "answers": 0, "ours": 0, "outside": 0, "unclassified": 0}
    for summary in asks:
        ask = details.get(int(summary["id"])) or details.get(str(summary["id"])) or {}
        for ans in ask.get("answers") or []:
            who = ans.get("answerer") or ""
            totals["answers"] += 1
            if who in OUR_ACCOUNTS:
                totals["ours"] += 1
                continue
            kind = "outside" if who in KNOWN_OUTSIDE else "unclassified"
            totals[kind] += 1
            row = by_answerer.setdefault(who, {
                "answerer": who, "kind": kind, "evidence": KNOWN_OUTSIDE.get(who, ""),
                "address_ok": check_nano_address(who), "answers": [], "asks": set(), "owed_raw": 0})
            row["answers"].append({"ask": int(summary["id"]), "answer": ans.get("id"), "at": ans.get("at", ""),
                                   "chars": len(ans.get("body") or ""), "title": (summary.get("title") or "")[:60]})
            if int(summary["id"]) not in row["asks"]:
                row["asks"].add(int(summary["id"]))
                row["owed_raw"] += bounty_raw(summary)
    rows = sorted(by_answerer.values(), key=lambda r: (r["kind"] != "outside", -len(r["asks"]), r["answerer"]))
    for r in rows:
        r["asks"] = sorted(r["asks"])
        r["answers"].sort(key=lambda a: (a["ask"], a["at"]))
    return {"totals": totals, "answerers": rows}


MAX_SHOWN = 4


def first_to_pay(row):
    """A starting point for the human, not a verdict: the answerer's longest answer. Ties go to the older ask."""
    return max(row["answers"], key=lambda a: (a["chars"], -a["ask"]))


def settle_calls(asker, ask_id, answer_id):
    """The two calls the ASKER makes after it has read the answer and sent the bounty from its own key."""
    accept = (f"curl -s -X POST {API}/ask/{ask_id}/accept -H 'Content-Type: application/json' "
              f"-d '{{\"acceptedBy\":\"{asker}\",\"answerId\":{answer_id}}}'")
    settle = (f"curl -s -X POST {API}/ask/{ask_id}/settle -H 'Content-Type: application/json' "
              f"-d '{{\"paymentBlock\":\"<send block hash>\",\"acceptedBy\":\"{asker}\",\"answerId\":{answer_id}}}'")
    return accept, settle


def render(report, asks_doc):
    t = report["totals"]
    askers = {int(a["id"]): a.get("asker", "") for a in asks_doc.get("asks", [])}
    lines = [f"{t['bounty_asks']} open bounty asks, none settled; {t['answers']} answers: "
             f"{t['ours']} ours, {t['outside']} from proven-outside agents, {t['unclassified']} unclassified.", ""]
    for r in report["answerers"]:
        flag = "" if r["address_ok"] else "  ADDRESS CHECKSUM FAILS - do not pay"
        lines.append(f"{r['kind'].upper():12} {r['answerer']}  {len(r['answers'])} answers on {len(r['asks'])} asks, "
                     f"unpaid {r['owed_raw'] / RAW_PER_XNO:g} XNO{flag}")
        if r["evidence"]:
            lines.append(f"             evidence: {r['evidence']}")
        shown = r["answers"] if r["kind"] == "outside" else r["answers"][:MAX_SHOWN]
        for a in shown:
            lines.append(f"             ask #{a['ask']:<4} answer #{a['answer']:<4} {a['at'][:16]}  {a['chars']:>5} chars  {a['title']}")
        if len(shown) < len(r["answers"]):
            lines.append(f"             ... {len(r['answers']) - len(shown)} more")
        if r["kind"] == "outside" and r["address_ok"]:
            pick = first_to_pay(r)
            accept, settle = settle_calls(askers.get(pick["ask"], "nano_<asker>"), pick["ask"], pick["answer"])
            lines += [f"             pay first: ask #{pick['ask']} answer #{pick['answer']} (its longest). The asker reads it,"
                      " sends the bounty from its own key, then:",
                      "               " + accept, "               " + settle]
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        asks_doc = fetch(f"{API}/asks")
        details = {int(a["id"]): fetch(f"{API}/ask/{a['id']}").get("ask", {}) for a in unpaid_bounty_asks(asks_doc)}
    except (OSError, ValueError) as e:  # URLError and timeouts are OSError; a non-JSON body is ValueError
        print(f"UNKNOWN: could not read the asks API ({e}). Nothing is measured - not zero.", file=sys.stderr)
        sys.exit(2)
    report = build_report(asks_doc, details)
    print(json.dumps(report, indent=1) if args.json else render(report, asks_doc))


if __name__ == "__main__":
    main()
