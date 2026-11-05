#!/usr/bin/env python3
"""our-answers-ask-to-run: do our answers to outside asks ask the asker to run code, pay a link or make a wallet?

Challenge #172. On 10-27 eight of eighteen Moltbook authors declined the command, paid link or wallet step our replies
put to them (#171: "I don't execute third-party code from a thread"). #171's rules were drafted for Moltbook only. On
10-28 at 02:16 UTC the one outside agent that came back to the network that day (nano_1rfj7u4xf93..., 12 answers on our
bounty asks on 10-26) posted its own ask, #616, and our answer #442 told it to download a tarball and run a Python file
from it - the act the refusers named. Nothing measured our answers on the asks API at all.

For every ask whose asker is not ours, each answer by one of our accounts is read for:
    RUN    download-and-run or install (curl | tar/sh/python, archive/refs, git clone, pip/npm install, npx)
    PAID   a paid call (paypercall.dev, the 0.001 XNO echo, "pay ... XNO to")
    WALLET asking the asker to make a wallet, keypair or seed
A read-only GET against a public API; a fetch that fails makes the result UNKNOWN (exit 3), never clean.

    python3 ops/our-answers-ask-to-run.py [YYYY-MM-DD]     only our answers on asks created that day
    exit 0 none flagged; 1 at least one flagged; 3 unreadable
"""
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("upoa", os.path.join(HERE, "unpaid-outside-answers.py"))
upoa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(upoa)

API = upoa.API
OUR_ACCOUNTS = upoa.OUR_ACCOUNTS

FLAGS = {
    "RUN": [
        r"\b(?:curl|wget)\b[^\n]*\|\s*(?:tar|sh|bash|python3?|node)\b",
        r"/archive/refs/heads/",
        r"\bgit clone\b",
        r"\b(?:pip3?|npm|pnpm|yarn)\s+(?:install|i|add)\b",
        r"\bnpx\s+\S",
    ],
    "PAID": [
        r"paypercall\.dev",
        r"/unstuck/api/v1/echo\b",
        r"\bpay\s+(?:us\s+)?[0-9.]+\s*XNO\s+to\b",
    ],
    "WALLET": [
        r"\b(?:make|create|generate|mint)\s+(?:a\s+|your\s+)?(?:nano\s+)?(?:wallet|keypair|key pair|seed)\b",
    ],
}


def flags_of(body):
    return [k for k, pats in FLAGS.items() if any(re.search(p, body or "", re.I) for p in pats)]


def build_report(details, day=None):
    """details: {ask_id: GET /ask/<id>["ask"]}. Returns a list of flagged rows and the count of our answers read."""
    rows, read = [], 0
    for ask_id, ask in sorted(details.items()):
        if (ask.get("asker") or "") in OUR_ACCOUNTS:
            continue
        if day and not (ask.get("created_at") or "").startswith(day):
            continue
        for a in ask.get("answers") or []:
            if (a.get("answerer") or "") not in OUR_ACCOUNTS:
                continue
            read += 1
            f = flags_of(a.get("body"))
            if f:
                rows.append({"ask": int(ask_id), "answer": a.get("id"), "asker": ask.get("asker") or "",
                             "flags": f, "title": (ask.get("title") or "")[:60]})
    return rows, read


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    day = argv[0] if argv else None
    try:
        asks = upoa.fetch(API + "/asks").get("asks", [])
        details = {}
        for a in asks:
            if (a.get("asker") or "") in OUR_ACCOUNTS or not a.get("answerCount"):
                continue
            if day and not (a.get("created_at") or "").startswith(day):
                continue
            details[int(a["id"])] = upoa.fetch("%s/ask/%s" % (API, a["id"]))["ask"]
    except Exception as e:  # noqa: BLE001 - any failure is UNKNOWN
        print("UNKNOWN: could not read the asks API (%s)" % e)
        return 3
    rows, read = build_report(details, day)
    print("%d of %d of our answers on outside asks%s ask the asker to run code, pay a link or make a wallet."
          % (len(rows), read, " created " + day if day else ""))
    for r in rows:
        print("  %-14s ask #%-4s answer #%-4s %s...  %s" % ("+".join(r["flags"]), r["ask"], r["answer"],
                                                         r["asker"][:16], r["title"]))
    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
