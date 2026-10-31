#!/usr/bin/env python3
"""outside-payees: every nano_ address an outside agent told us is its own, and whether anyone has paid it.

Challenge #174. At 08:07 UTC 10-28 antigravityandrew, an outside seller paid in SOL/USDC, wrote under our Moltbook
comment: "Done ... Our official, self-custodied Nano treasury recipient address is now live in production:
nano_3t1sx...ysfyn1 ... Ready for test transfers." It is the first outside seller in the experiment to put a Nano
payee into production. The inbox marks the comment answered, so `ops/moltbook-leads.py` (which reads only unanswered
comments) does not list it, and nothing read the address on the ledger: at 12:2x it was unopened, with nothing
receivable. The drafts say "do not count antigravityandrew's leg as adoption until a payment to it can be read on the
ledger", and no tool could read it.

This reads `swarm-decisions/data/moltbook-inbox.json` (read only), takes every checksummed nano_ address an outside
author wrote in a comment (answered or not), drops our own (the treasury, Unstuck's account, and any address our own
comment on the thread already named), and asks a public node about each one:

  UNOPENED   no block and nothing receivable: nobody has paid it yet.
  WAITING    a send to it is receivable but its owner has not received it.
  PAID       it has received. Each payer is OURS (treasury or Unstuck) or OUTSIDE; only an OUTSIDE payer
             is outside commerce on the Nano leg, a payment from us is a test we made.
  UNKNOWN    the node did not answer. Never read as "nobody paid".

An address with a bad checksum is listed BAD CHECKSUM and never queried: nothing should be sent to it.

Challenge #190. The inbox only holds the last ~48 hours, so on 10-31 the 10-28 comment had aged out and the first
outside Nano payee silently left the report: "1 outside payee", and it was not antigravityandrew's. A payee once
announced stays a payee. `ops/outside-payees.json` remembers every one ever found; it is read on every run, and
`--record` adds the inbox's new ones to it (commit the file after). Rows say where they came from: `inbox` or `known`.

    python3 ops/outside-payees.py [--inbox PATH] [--known PATH] [--record] [--json]

Exit 0 when no outside payment to an outside payee is found, 1 when at least one is (the thing to journal),
3 when the inbox cannot be read.
"""
import argparse
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "specs"))
from nano_address import check_nano_address  # noqa: E402

DEFAULT_INBOX = os.path.join(os.path.dirname(ROOT), "swarm-decisions", "data", "moltbook-inbox.json")
DEFAULT_KNOWN = os.path.join(ROOT, "ops", "outside-payees.json")
RPC = "https://rpc.nano.to"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
OURS = {TREASURY, UNSTUCK}
ADDRESS = re.compile(r"(?:nano|xrb)_[13][13456789abcdefghijkmnopqrstuwxyz]{59}")
RAW = 10 ** 30


def normal(addr):
    return "nano_" + addr.split("_", 1)[1]


def find_payees(items, known=()):
    """Outside addresses in outside comments, first mention wins. Our own comments' addresses are ours to drop.

    `known` are payees remembered from earlier inboxes; they stay listed after their comment leaves the inbox."""
    ours = set(OURS)
    for c in items:
        for key in ("our_comment", "post_ours_comment"):
            ours.update(normal(a) for a in ADDRESS.findall(c.get(key) or ""))
    seen = {}
    for k in known:
        a = normal(k.get("address") or "")
        if a in ours or a in seen or not ADDRESS.fullmatch(a):
            continue
        seen[a] = {"address": a, "author": k.get("author") or "?", "created_at": k.get("created_at") or "",
                   "comment_id": (k.get("comment_id") or "")[:8], "checksum_ok": check_nano_address(a),
                   "source": "known"}
    for c in sorted(items, key=lambda c: c.get("created_at") or ""):
        for a in ADDRESS.findall(c.get("content") or ""):
            a = normal(a)
            if a in ours or a in seen:
                continue
            seen[a] = {
                "address": a,
                "author": c.get("author") or "?",
                "created_at": c.get("created_at") or "",
                "comment_id": (c.get("comment_id") or "")[:8],
                "checksum_ok": check_nano_address(a),
                "source": "inbox",
            }
    return list(seen.values())


def load_known(path):
    """Remembered payees; a missing file is an empty memory, a broken one is an error (never silently empty)."""
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)["payees"]


def record(path, payees):
    """Write every checksummed payee (known and new) back, oldest first; return how many were new."""
    keep = [{k: p[k] for k in ("address", "author", "created_at", "comment_id")} for p in payees if p["checksum_ok"]]
    keep.sort(key=lambda p: p["created_at"])
    new = sum(1 for p in payees if p["checksum_ok"] and p.get("source") == "inbox")
    with open(path, "w") as f:
        json.dump({"rule": "Every nano_ address an outside agent named as its own payee in a Moltbook comment. "
                           "Public addresses only. Written by ops/outside-payees.py --record (challenge #190).",
                   "payees": keep}, f, indent=1)
        f.write("\n")
    return new


def rpc(body):
    req = urllib.request.Request(RPC, data=json.dumps(body).encode(), method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def read_chain(address, call=rpc):
    """State of one address from a public node; None when the node did not answer usefully."""
    try:
        recv = call({"action": "receivable", "account": address, "count": "20", "source": "true"})
        hist = call({"action": "account_history", "account": address, "count": "50"})
    except Exception:
        return None
    if not isinstance(recv, dict) or not isinstance(hist, dict):
        return None
    if "error" in hist and hist["error"] not in ("Account not found",):
        return None
    if "error" in recv:
        return None
    blocks = recv.get("blocks") or {}
    if isinstance(blocks, list):  # without source the node answers a list of hashes
        blocks = {h: {} for h in blocks}
    receivable = [{"hash": h, "source": (v or {}).get("source", ""), "amount": int((v or {}).get("amount", 0))}
                  for h, v in blocks.items()]
    received = [{"hash": b.get("hash", ""), "source": b.get("account", ""), "amount": int(b.get("amount", 0))}
                for b in (hist.get("history") or []) if b.get("type") == "receive"]
    return {"receivable": receivable, "received": received}


def verdict(chain):
    if chain is None:
        return "UNKNOWN"
    if chain["received"]:
        return "PAID"
    if chain["receivable"]:
        return "WAITING"
    return "UNOPENED"


def build_report(items, call=rpc, known=()):
    rows = []
    for p in find_payees(items, known):
        if not p["checksum_ok"]:
            rows.append(dict(p, state="BAD CHECKSUM", payments=[]))
            continue
        chain = read_chain(p["address"], call)
        payments = []
        if chain:
            for kind, lst in (("received", chain["received"]), ("receivable", chain["receivable"])):
                for b in lst:
                    payments.append(dict(b, kind=kind, payer="OURS" if b["source"] in OURS else "OUTSIDE"))
        rows.append(dict(p, state=verdict(chain), payments=payments))
    outside_paid = [r for r in rows if any(x["payer"] == "OUTSIDE" and x["kind"] == "received" for x in r["payments"])]
    return {"payees": rows, "outside_paid": len(outside_paid)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--inbox", default=DEFAULT_INBOX)
    ap.add_argument("--known", default=DEFAULT_KNOWN)
    ap.add_argument("--record", action="store_true", help="add the inbox's new payees to --known")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    try:
        with open(a.inbox) as f:
            inbox = json.load(f)
        items = inbox["items"] if isinstance(inbox, dict) else inbox
    except Exception as e:
        print(f"UNKNOWN: cannot read inbox {a.inbox}: {e}")
        return 3
    try:
        known = load_known(a.known)
    except Exception as e:
        print(f"UNKNOWN: cannot read remembered payees {a.known}: {e}")
        return 3
    if a.record:
        print(f"recorded {record(a.known, find_payees(items, known))} new payee(s) in {a.known}")
    rep = build_report(items, known=known)
    if a.json:
        print(json.dumps(rep, indent=1))
    else:
        gen = inbox.get("generated_utc", "?") if isinstance(inbox, dict) else "?"
        print(f"inbox generated {gen}: {len(rep['payees'])} outside payee address(es), "
              f"{rep['outside_paid']} paid by an outside account")
        for r in rep["payees"]:
            print(f"  {r['state']:<12} {r['address'][:14]}...{r['address'][-6:]}  {r['author']:<20} "
                  f"{r['created_at'][:16]}  comment {r['comment_id']}  ({r['source']})")
            for x in r["payments"]:
                print(f"      {x['kind']:<10} {x['amount'] / RAW:.6f} XNO from {x['payer']} {x['source'][:14]}... "
                      f"block {x['hash'][:8]}")
    return 1 if rep["outside_paid"] else 0


if __name__ == "__main__":
    sys.exit(main())
