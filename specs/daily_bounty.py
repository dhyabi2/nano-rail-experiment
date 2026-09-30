#!/usr/bin/env python3
"""daily-bounty: score and pay the DAILY CONTRIBUTOR bounty (challenge #53).

This is a WHOLLY DIFFERENT mechanism from referral_bounty.py's hourly referral bounty, and it is also not the
same thing as that file's own `--period day` flag - that flag scores REFERRALS over a day-long window (an
existing, tested feature this module does not touch or replace). The daily bounty `bounties.txt` and
specs/04-REFERRAL-BOUNTY.md describe pays for CONTRIBUTION, not referral:

    an answer accepted on an ask, with a settlement block on chain, or
    a paid call you made to a live endpoint (its block), or
    an ask you posted that somebody else answered.
    Posting text does not count. Registering does not count.

Before this file, `referral_bounty.py`'s `score()`/`pay()` only ever read the `claims` table - which only ever
holds referrals - for BOTH `kind="hour"` and `kind="day"`. An agent that did exactly what bounties.txt told it
to do (post an ask that got answered, get an answer accepted, make a paid call) had no code path anywhere in
this repository that would ever credit it. See CHALLENGES-SOLVED.md challenge #53 for the full finding.

Two of the three contribution kinds need no claim at all, because the evidence is already public: an ask and
its answers are visible to anyone on the live network (`GET /unstuck/api/asks`), so `ask_answered` and
`answer_accepted` are read straight off that feed. Only `paid_call` needs a claim - a payment to a seller
leaves no public record anywhere else in this system that names the PAYER, so the payer has to point at the
block, same as referral_bounty.claim() does for a referral link.

    daily-bounty score  [--day YYYY-MM-DD]           what the feed and chain say, pays nothing
    daily-bounty pay    [--day YYYY-MM-DD] [--live]   pay every qualifying winner - DRY RUN unless --live
    daily-bounty claim  --claimant A --block H         claim a paid call

Money safety is identical to referral_bounty.py: this never builds a block, shells out to the product's own
sender, and the only amount it can ever request is the sanctioned 0.1 XNO grant, gated by the same treasury
floor and the same frozen daily ceiling (shared with the referral bounty via the same `paid` table, so the two
bounties cannot together drain more than DAILY_CEILING_RAW between them).
"""
import argparse
import calendar
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request

import referral_bounty as rb

ASKS_URL = os.environ.get("UNSTUCK_ASKS_URL", "https://getunstuck.space/unstuck/api/asks")
MANIFEST_URLS = tuple(u.strip() for u in os.environ.get(
    "X402_MANIFESTS",
    "https://extract.paypercall.dev/.well-known/x402,"
    "https://search.paypercall.dev/.well-known/x402,"
    "https://domain.paypercall.dev/.well-known/x402,"
    "https://check.paypercall.dev/.well-known/x402,"
    "https://geoip.paypercall.dev/.well-known/x402").split(",") if u.strip())


def _get_json(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": "unstuck-daily-bounty/1"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def fetch_asks():
    """The live public ask feed. None means it could not be read - the caller must treat that as UNKNOWN, never
    as an empty (and therefore silently zero-scoring) feed. A source that cannot be read must never report a
    clean result."""
    try:
        d = _get_json(ASKS_URL)
        return d.get("asks") or []
    except (urllib.error.URLError, OSError, ValueError, TimeoutError):
        return None


def fetch_payees():
    """The addresses a paid call may legitimately pay, read live from every seller's OWN published x402
    manifest rather than hardcoded - a seller that rotates its payee is picked up automatically instead of
    silently rejecting a real payment to a now-stale address we typed in once. Returns an empty set (not None)
    on total failure; callers already refuse to count any paid_call claim against an empty payee set, which has
    the same never-zero-as-clean effect without a second sentinel value."""
    out = set()
    for url in MANIFEST_URLS:
        try:
            m = _get_json(url)
        except (urllib.error.URLError, OSError, ValueError, TimeoutError):
            continue
        for res in (m.get("resources") or []):
            for acc in (res.get("accepts") or []):
                p = acc.get("payTo")
                if p:
                    out.add(rb.norm(p))
    return out


def ask_activity(asks, ours):
    """`ask_answered` and `answer_accepted` contributions, read straight off the public feed - no claim needed,
    because the evidence (the ask, its answer count, its accepted answer and settlement block) is already
    public and the same for everyone who reads it. Returns a list of
    {contributor, kind, ask_id, (block,) why}."""
    out = []
    for a in asks or []:
        asker = rb.norm(a.get("asker"))
        aid = a.get("id")
        if asker and asker not in ours and int(a.get("answerCount") or 0) > 0:
            out.append({"contributor": asker, "kind": "ask_answered", "ask_id": aid,
                        "why": f"ask #{aid} was posted by this agent and answered by someone else"})
        accepted_id, settlement = a.get("acceptedAnswerId"), a.get("settlementBlock")
        if accepted_id and settlement:
            answerer = None
            for ans in (a.get("answers") or []):
                if ans.get("id") == accepted_id:
                    answerer = rb.norm(ans.get("answerer"))
                    break
            if answerer and answerer not in ours:
                out.append({"contributor": answerer, "kind": "answer_accepted", "ask_id": aid,
                            "block": settlement,
                            "why": f"answer #{accepted_id} on ask #{aid} was accepted with a settlement block"})
    return out


def is_paid_call(block_hash, claimant, payees):
    """A confirmed send, signed by `claimant`, to one of `payees` (a live seller's own published payTo). That is
    the whole check - what was bought and for how much is between the claimant and the seller; this only needs
    to know real money left the claimant's own key and reached a real seller, which is exactly what
    'a paid call you made to a live endpoint (its block)' asks for. Returns (ok, why)."""
    if not payees:
        return False, "no live seller payee could be read this run - reporting unknown, not rejecting"
    b = rb.block(block_hash)
    if not b:
        return False, "the cited block could not be read from the chain"
    if rb.norm(b.get("block_account")) != rb.norm(claimant):
        return False, "the block was not signed by the claimant"
    c = b.get("contents") or {}
    is_send = b.get("subtype") == "send" or c.get("type") == "send"
    dest = rb.norm(c.get("link_as_account") or c.get("destination"))
    if not is_send or dest not in payees:
        return False, "not a send to a live seller's currently-published payTo address"
    try:
        amt = int(b.get("amount") or 0)
    except (TypeError, ValueError):
        amt = 0
    if amt <= 0:
        return False, "the send carried no amount the node could compute"
    if str(b.get("confirmed", "true")).lower() != "true":
        return False, "the block is not confirmed yet"
    return True, "confirmed send to a live seller's published payTo address"


def _ensure_tables(con):
    con.execute("""CREATE TABLE IF NOT EXISTS day_claims(
        block TEXT PRIMARY KEY, claimant TEXT NOT NULL, at REAL NOT NULL)""")
    con.commit()


def day_id():
    return time.strftime("%Y-%m-%d", time.gmtime())


def claim(claimant, block):
    """Only `paid_call` needs this. `ask_answered` and `answer_accepted` are never claimed - they are read
    straight off the public feed in score_day(), the same discipline as 'computed from the chain, never from a
    claim' in specs/04-REFERRAL-BOUNTY.md."""
    import re
    if not re.fullmatch(r"[0-9A-Fa-f]{64}", (block or "").strip()):
        print("refused: --block must be the 64-hex hash of the send YOU made to a live seller.")
        return 1
    con = rb.db()
    _ensure_tables(con)
    try:
        con.execute("INSERT INTO day_claims(block, claimant, at) VALUES(?,?,?)",
                    (block.strip().upper(), rb.norm(claimant), time.time()))
        con.commit()
        print(f"claim recorded: {rb.norm(claimant)[:20]}... cites block {block[:16]}... "
              "(a claim is a POINTER, not a score - the chain and the feed decide)")
    except sqlite3.IntegrityError:
        print("refused: that block has already been claimed.")
        return 1
    return 0


def score_day(day=None, asks=None, payees=None, con=None, verbose=True):
    con = con or rb.db()
    _ensure_tables(con)
    day = day or day_id()
    since = calendar.timegm(time.strptime(day, "%Y-%m-%d"))
    until = since + 86400
    ours = rb.OURS

    if asks is None:
        asks = fetch_asks()
    ask_feed_ok = asks is not None
    detail = []
    winners = {}

    if not ask_feed_ok:
        detail.append({"kind": "ask_feed", "ok": False,
                        "why": "could not read the live ask feed this run - reporting unknown, never zero"})
    else:
        for c in ask_activity(asks, ours):
            winners.setdefault(c["contributor"], []).append(c)
            detail.append({**c, "counted": True})

    payees = fetch_payees() if payees is None else payees
    rows = con.execute("SELECT claimant, block, at FROM day_claims WHERE at >= ? AND at < ?",
                        (since, until)).fetchall()
    for claimant, block, at in rows:
        claimant = rb.norm(claimant)
        if claimant in ours:
            detail.append({"contributor": claimant, "kind": "paid_call", "block": block,
                            "counted": False, "why": "one of our own accounts"})
            continue
        ok, why = is_paid_call(block, claimant, payees)
        entry = {"contributor": claimant, "kind": "paid_call", "block": block, "counted": ok, "why": why}
        detail.append(entry)
        if ok:
            winners.setdefault(claimant, []).append(entry)

    out = {"period": day, "kind": "day_contrib", "ask_feed_read": ask_feed_ok, "payees_read": bool(payees),
           "winners": sorted(winners), "reasons": winners, "detail": detail}
    if verbose:
        print(json.dumps(out, indent=1))
    return out


def pay_day(day=None, live=False):
    con = rb.db()
    _ensure_tables(con)
    s = score_day(day=day, con=con, verbose=False)

    if not s["ask_feed_read"]:
        print("REFUSED: could not read the live ask feed this run. A check that cannot run must never report a "
              "clean result - paying nobody rather than guessing which claims are real.")
        return 1
    if not s["winners"]:
        print(f"{s['period']}: no qualifying daily contribution. Paying nobody - a day that contributed nothing "
              "costs nothing.")
        return 0

    ok, bal = rb.treasury_ok()
    if not ok:
        print(f"REFUSED: treasury {bal / rb.XNO:.4f} XNO would fall below the {rb.FLOOR_RAW / rb.XNO:.4f} floor. "
              "Bounties stop before the treasury does.")
        return 1

    used = rb.spent_today(con)
    for winner in s["winners"]:
        if used + rb.GRANT_RAW > rb.DAILY_CEILING_RAW:
            print(f"REFUSED: the frozen daily bounty ceiling ({rb.DAILY_CEILING_RAW / rb.XNO:.1f} XNO, shared "
                  "with the referral bounty) is reached.")
            break
        try:
            con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                        (s["period"], winner, "day_contrib", str(rb.GRANT_RAW), "reserved", time.time()))
            con.commit()
        except sqlite3.IntegrityError:
            print(f"  {winner[:22]}... already paid for {s['period']} (day_contrib) - skipping, idempotent")
            continue
        reasons = "; ".join(sorted({r["kind"] for r in s["reasons"][winner]}))
        if not live:
            print(f"  DRY RUN would send 0.1 XNO to {winner[:26]}... ({reasons}, period {s['period']})")
            con.execute("DELETE FROM paid WHERE period=? AND winner=? AND kind=?",
                        (s["period"], winner, "day_contrib"))
            con.commit()
            continue
        agreement = f"daily contributor bounty, {s['period']}: {reasons}"
        r = subprocess.run(["node", rb.SENDER, "--grant", winner, "--agent", winner[:24],
                            "--agreement", agreement], capture_output=True, text=True, timeout=300)
        combined = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 and "already" in combined.lower():
            con.execute("UPDATE paid SET state='already_granted' WHERE period=? AND winner=? AND kind=?",
                        (s["period"], winner, "day_contrib"))
            con.commit()
            print(f"  {winner[:26]}... has already had its one grant - nothing sent, recorded, not retried")
            continue
        if r.returncode == 0:
            try:
                blk = (json.loads(r.stdout).get("block") or "")[:64]
            except (json.JSONDecodeError, AttributeError):
                blk = ""
            con.execute("UPDATE paid SET state='confirmed', block=? WHERE period=? AND winner=? AND kind=?",
                        (blk, s["period"], winner, "day_contrib"))
            used += rb.GRANT_RAW
            print(f"  PAID 0.1 XNO to {winner[:26]}... block {blk}")
        else:
            con.execute("UPDATE paid SET state='unknown' WHERE period=? AND winner=? AND kind=?",
                        (s["period"], winner, "day_contrib"))
            print(f"  UNKNOWN for {winner[:26]}...: sender exited {r.returncode}. Left as 'unknown' - a person "
                  f"must read the chain before anything retries. {r.stderr[:160]}")
        con.commit()
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sc = sub.add_parser("score")
    sc.add_argument("--day", default=None)
    pa = sub.add_parser("pay")
    pa.add_argument("--day", default=None)
    pa.add_argument("--live", action="store_true",
                     help="actually send. Without it, nothing moves and the reservation is rolled back.")
    cl = sub.add_parser("claim")
    cl.add_argument("--claimant", required=True)
    cl.add_argument("--block", required=True, help="hash of the send YOU made to a live seller's payTo address")
    a = p.parse_args()
    if a.cmd == "score":
        score_day(day=a.day)
        return 0
    if a.cmd == "pay":
        return pay_day(day=a.day, live=a.live)
    return claim(a.claimant, a.block)


if __name__ == "__main__":
    sys.exit(main())
