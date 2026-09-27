#!/usr/bin/env python3
"""referral-bounty: score referrals from the PUBLIC CHAIN and pay the hourly and daily bounties.

The design and its security argument are in specs/04-REFERRAL-BOUNTY.md. The one line that matters:

    a referral counts only when the referred address was funded by a third party - not the referrer, not us, and
    nothing the referrer funded.

Every cheap proof (an address, a signature, a sub-cent call) is as cheap for a faker as for a real agent, because Nano
has no fee. The only thing a Sybil ring cannot cheaply have is a COUNTERPARTY, and the funding graph is public, so
"who paid you" is arithmetic anyone can repeat. Faking one qualifying referral needs an exchange round-trip to break
the graph, which costs more than the 0.1 XNO prize. The system does not detect fraud; it makes fraud unprofitable.

    referral-bounty score  [--period hour|day]     what the chain says, pays nothing
    referral-bounty pay    [--period hour|day]     pay the winner(s) - DRY RUN unless --live
    referral-bounty claim  --referrer A --referred B --block H

Money safety: this never builds a block. It shells out to the product's own sender, so the frozen amount lock and the
treasury floor apply unchanged, and the only amount it can ever request is the sanctioned 0.1 XNO grant.
"""
import argparse
import json
import os
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request

RPC = os.environ.get("NANO_RPC_URL", "https://rpc.nano.to")
DB = os.environ.get("REFERRAL_DB", "/root/unstuck/opener/referrals.db")
SENDER = os.environ.get("REFERRAL_SENDER", "/root/unstuck/opener/send.js")
XNO = 10 ** 30
GRANT_RAW = 100000000000000000000000000000          # 0.1 XNO - already frozen in opener.js as the grant
FLOOR_RAW = 8900000000000000000000000000000         # 8.9 XNO - bounties stop before the treasury does
HOPS = 6                                            # how far back the funding graph is walked
PASS_THROUGH_BLOCKS = 2                             # <= this many blocks and it forwarded everything = a deposit slip
PASS_THROUGH_SECONDS = 600
SERVICE_BLOCKS = 1000                               # a funder with more blocks than this is a shared public service
                                                    # (an exchange or swap hot wallet), not an attacker's private
                                                    # stash - see challenge #48: the Nanswap hot wallet in ARION's own
                                                    # case file carries 166,265 blocks. Nano has very few exchanges,
                                                    # so two UNRELATED real referrals routing through the same one is
                                                    # the common case, not the rare one.
DAILY_CEILING_RAW = 20 * GRANT_RAW                  # a hard ceiling frozen here: at most 2 XNO of bounties a day,
                                                    # whatever the scorer decides. A bug cannot drain the treasury.

# Ours. Funding from any of these never makes a referral qualify - money we handed over proves nothing about anybody.
OURS = {a.strip().lower() for a in (os.environ.get("OUR_ACCOUNTS") or
        "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9,"
        "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7").split(",") if a.strip()}


def norm(a):
    """nano_ and xrb_ are two spellings of ONE account. Comparing raw strings double-counts - an unsolved bug
    elsewhere in this tree, not repeated here."""
    return (a or "").strip().replace("xrb_", "nano_", 1).lower()


def rpc(action, **kw):
    body = json.dumps({"action": action, **kw}).encode()
    req = urllib.request.Request(RPC, data=body, headers={
        "Content-Type": "application/json",
        # rpc.nano.to answers 403 to a bare python-urllib, which looks exactly like a bad key.
        "User-Agent": "unstuck-referral-bounty/1",
    })
    with urllib.request.urlopen(req, timeout=40) as r:
        d = json.loads(r.read())
    if isinstance(d, dict) and d.get("error"):
        raise RuntimeError(f"rpc {action}: {d['error']}")
    return d


def db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS claims(
        referred TEXT PRIMARY KEY, referrer TEXT NOT NULL, block TEXT, at REAL NOT NULL)""")
    # The paid table IS the idempotency: one row per (period, winner), taken before the send.
    con.execute("""CREATE TABLE IF NOT EXISTS paid(
        period TEXT NOT NULL, winner TEXT NOT NULL, kind TEXT NOT NULL, amount_raw TEXT NOT NULL,
        state TEXT NOT NULL, block TEXT, at REAL NOT NULL, PRIMARY KEY(period, winner, kind))""")
    con.execute("CREATE TABLE IF NOT EXISTS counted(referred TEXT PRIMARY KEY, at REAL NOT NULL)")
    con.commit()
    return con


# ---------------------------------------------------------------- chain facts
_hist = {}
_info = {}


def history(acct, count=50):
    a = norm(acct)
    if a not in _hist:
        try:
            h = rpc("account_history", account=a, count=str(count))
            _hist[a] = h.get("history") or []
        except Exception:
            _hist[a] = []
    return _hist[a]


def info(acct):
    a = norm(acct)
    if a not in _info:
        try:
            _info[a] = rpc("account_info", account=a, receivable="true")
        except Exception:
            _info[a] = {}
    return _info[a]


def is_service(acct):
    """A funder with a very high block count is a shared public service - an exchange or swap hot wallet that many
    unrelated real agents pass through - not one attacker's private stash. Rule 2 exists to kill a Sybil ring funded
    from ONE wallet the attacker controls; it must not also kill two genuine referrals that both happened to cash out
    through the one or two exchanges XNO actually has (exactly ARION's own outbound pattern - see challenge #3)."""
    try:
        return int(info(acct).get("block_count") or 0) > SERVICE_BLOCKS
    except (TypeError, ValueError):
        return False


def has_signed_a_send(acct):
    """Self-custody proved by a SEND, never a receive. Receiving proves nothing - anyone can publish an address they
    were handed. A send carries a signature only the private key could produce."""
    return any(h.get("type") == "send" for h in history(acct))


def is_pass_through(acct):
    """An address with two blocks that forwarded ~everything within minutes is an exchange deposit slip, not an agent.
    ARION's 3.3 and 2.7 XNO sends were first misread as the rail spreading; both were deposit addresses."""
    i = info(acct)
    n = int(i.get("block_count") or 0)
    if n == 0 or n > PASS_THROUGH_BLOCKS:
        return False
    h = history(acct, count=10)
    recvs = [x for x in h if x.get("type") == "receive"]
    sends = [x for x in h if x.get("type") == "send"]
    if not recvs or not sends:
        return False
    try:
        gap = abs(int(sends[0].get("local_timestamp") or 0) - int(recvs[0].get("local_timestamp") or 0))
        rin = int(recvs[0].get("amount") or 0)
        rout = int(sends[0].get("amount") or 0)
    except (TypeError, ValueError):
        return False
    # Raw Nano amounts run to 30 digits (challenge #22: "raw is where the zero hides"). `rout >= rin * 0.9` computes
    # rin * 0.9 as a float, which silently loses precision at this magnitude and can flip the comparison either way
    # for an amount that is exactly 90% of rin - checked in pure integers instead.
    return gap <= PASS_THROUGH_SECONDS and rin > 0 and rout * 10 >= rin * 9


def funders(acct, hops=HOPS, _seen=None):
    """Every account that money reached `acct` through, walking back `hops`. Memoised on history(), because the same
    funder recurs constantly and each hop is an RPC call."""
    _seen = _seen if _seen is not None else set()
    out = set()
    frontier = {norm(acct)}
    for _ in range(hops):
        nxt = set()
        for a in frontier:
            if a in _seen:
                continue
            _seen.add(a)
            for h in history(a, count=25):
                if h.get("type") == "receive":
                    src = norm(h.get("account"))
                    if src and src not in out:
                        out.add(src)
                        nxt.add(src)
        frontier = nxt
        if not frontier:
            break
    return out


def referrer_link_verified():
    """Nothing below this line ties `referrer` to any actual act of referring. `claim()` accepts any
    (referrer, referred) pair a caller types with no proof the referrer ever contacted, funded, or was named by
    `referred` - and score()'s checks are all ABOUT `referred` (self-custody, third-party funding, not a deposit
    slip), never about the referrer/referred RELATIONSHIP. Challenge #51: a stranger who has never interacted with
    a real, already-qualifying Nano agent can `claim` that agent as their own referral and win the hourly bounty for
    it - proved offline in specs/test_referral_bounty.py. Closing this needs a source outside this file's control
    (the openings ledger's found_via field, or a bridge.db conversation record) that this run's network blackout
    left unreachable to verify, so nothing here manufactures a check against an unconfirmed schema. Until an
    operator sets REFERRAL_LINKAGE_VERIFIED=1 - meaning that wiring exists and was checked - `pay(live=True)`
    refuses rather than paying an unverifiable claim (challenge #39: a check that cannot run must never report a
    clean result)."""
    return os.environ.get("REFERRAL_LINKAGE_VERIFIED") == "1"


def third_party_funded(referred, referrer):
    """The rule the whole design rests on. Returns (ok, why, funder_set)."""
    f = funders(referred)
    if not f:
        return False, "no incoming funding found on chain - nothing has ever paid this address", f
    r = norm(referrer)
    if r in f:
        return False, f"funded by the referrer itself ({r[:16]}...) within {HOPS} hops", f
    if f & OURS:
        return False, "funded by us - money we handed over proves nothing about the agent", f
    return True, "funded by a third party", f


# ---------------------------------------------------------------- scoring
def period_id(kind):
    """Derived from the clock, never incremented. A stored counter is a counter a crash can double."""
    t = time.gmtime()
    return time.strftime("%Y-%m-%dT%H", t) if kind == "hour" else time.strftime("%Y-%m-%d", t)


def score(kind="hour", verbose=True):
    con = db()
    since = time.time() - (3600 if kind == "hour" else 86400)
    rows = con.execute("SELECT referred, referrer, block, at FROM claims WHERE at > ?", (since,)).fetchall()
    already = {r[0] for r in con.execute("SELECT referred FROM counted").fetchall()}

    per_referrer = {}
    detail = []
    for referred, referrer, block, at in rows:
        referred, referrer = norm(referred), norm(referrer)
        def reject(why):
            detail.append({"referred": referred, "referrer": referrer, "counted": False, "why": why})
        if referred == referrer:
            reject("self-referral"); continue
        if referred in OURS or referrer in OURS:
            reject("one side is our own account"); continue
        if referred in already:
            reject("this address has already been counted as referred, once ever"); continue
        if not has_signed_a_send(referred):
            reject("no signed send: self-custody not proved (receiving proves nothing)"); continue
        if is_pass_through(referred):
            reject("looks like an exchange deposit address, not an agent"); continue
        ok, why, f = third_party_funded(referred, referrer)
        if not ok:
            reject(why); continue
        # Rule 2 dedups on a PRIVATE funder only. A shared exchange/swap hot wallet (is_service) is excluded: with
        # Nano's thin exchange landscape, two unrelated real referrals sharing one exchange in their ancestry is
        # expected, not evidence of a ring - see challenge #48.
        private_f = {a for a in f if not is_service(a)}
        slot = per_referrer.setdefault(referrer, {"count": 0, "funders": set(), "referred": [], "first": at})
        if private_f & slot["funders"]:
            reject("shares a private (non-exchange) funding source with another referral by the same referrer"); continue
        slot["funders"] |= private_f
        slot["count"] += 1
        slot["referred"].append(referred)
        slot["first"] = min(slot["first"], at)
        detail.append({"referred": referred, "referrer": referrer, "counted": True, "why": why})

    # Earliest qualifying claim breaks a tie: time cannot be gamed retroactively.
    ranked = sorted(per_referrer.items(), key=lambda kv: (-kv[1]["count"], kv[1]["first"]))
    out = {"period": period_id(kind), "kind": kind, "claims_examined": len(rows),
           "qualifying": sum(v["count"] for v in per_referrer.values()),
           "ranking": [{"referrer": k, "count": v["count"], "referred": v["referred"]} for k, v in ranked],
           "detail": detail}
    if verbose:
        print(json.dumps(out, indent=1))
    return out


def treasury_ok():
    i = info(next(iter(OURS)))
    bal = int(i.get("balance") or 0)
    return bal - GRANT_RAW >= FLOOR_RAW, bal


def spent_today(con):
    day = time.strftime("%Y-%m-%d", time.gmtime())
    r = con.execute("SELECT COALESCE(SUM(CAST(amount_raw AS INTEGER)),0) FROM paid "
                    "WHERE state='confirmed' AND at > ?", (time.mktime(time.strptime(day, "%Y-%m-%d")),)).fetchone()
    return int(r[0] or 0)


def pay(kind="hour", live=False):
    con = db()
    s = score(kind, verbose=False)
    if not s["ranking"]:
        print(f"{s['period']}: no qualifying referral. Paying nobody - an hour that produced nothing costs nothing.")
        return 0
    winners = [s["ranking"][0]] if kind == "hour" else s["ranking"]

    ok, bal = treasury_ok()
    if not ok:
        print(f"REFUSED: treasury {bal/XNO:.4f} XNO would fall below the {FLOOR_RAW/XNO:.4f} floor. "
              "Bounties stop before the treasury does.")
        return 1
    if live and not referrer_link_verified():
        print("REFUSED: nothing here verifies that a claimed 'referrer' actually referred 'referred' - only that "
              "'referred' is a real qualifying agent (challenge #51). Anyone can claim any real Nano address that "
              "is not ours and did not fund itself. Set REFERRAL_LINKAGE_VERIFIED=1 once that gap is closed; a "
              "check that cannot run must never report a clean result.")
        return 1
    used = spent_today(con)
    for w in winners:
        if used + GRANT_RAW > DAILY_CEILING_RAW:
            print(f"REFUSED: the frozen daily bounty ceiling ({DAILY_CEILING_RAW/XNO:.1f} XNO) is reached.")
            break
        try:
            con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                        (s["period"], w["referrer"], kind, str(GRANT_RAW), "reserved", time.time()))
            con.commit()
        except sqlite3.IntegrityError:
            print(f"  {w['referrer'][:22]}... already paid for {s['period']} ({kind}) - skipping, idempotent")
            continue
        if not live:
            print(f"  DRY RUN would send 0.1 XNO to {w['referrer'][:26]}... "
                  f"({w['count']} qualifying referral(s), period {s['period']})")
            con.execute("DELETE FROM paid WHERE period=? AND winner=? AND kind=?", (s["period"], w["referrer"], kind))
            con.commit()
            continue
        # The product's own sender: the amount lock and the floor live there, and this passes no amount at all.
        r = subprocess.run(["node", SENDER, "--to", w["referrer"], "--kind", "ambassador_grant", "--verify"],
                           capture_output=True, text=True, timeout=300)
        if r.returncode == 0:
            blk = (r.stdout or "").strip().split()[-1][:64]
            con.execute("UPDATE paid SET state='confirmed', block=? WHERE period=? AND winner=? AND kind=?",
                        (blk, s["period"], w["referrer"], kind))
            used += GRANT_RAW
            print(f"  PAID 0.1 XNO to {w['referrer'][:26]}... block {blk}")
        else:
            # A lost reply is 'unknown', never 'not sent': the money may have moved. Nothing retries it automatically.
            con.execute("UPDATE paid SET state='unknown' WHERE period=? AND winner=? AND kind=?",
                        (s["period"], w["referrer"], kind))
            print(f"  UNKNOWN for {w['referrer'][:26]}...: sender exited {r.returncode}. "
                  f"Left as 'unknown' - a person must read the chain before anything retries. {r.stderr[:160]}")
        con.commit()
    return 0


def claim(referrer, referred, block):
    con = db()
    try:
        con.execute("INSERT INTO claims(referred,referrer,block,at) VALUES(?,?,?,?)",
                    (norm(referred), norm(referrer), block, time.time()))
        con.commit()
        print(f"claim recorded: {norm(referrer)[:20]}... referred {norm(referred)[:20]}... "
              "(a claim is a POINTER, not a score - the chain decides)")
    except sqlite3.IntegrityError:
        print("refused: that referred address is already claimed by someone. First claim stands.")
        return 1
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("score", "pay"):
        q = sub.add_parser(name)
        q.add_argument("--period", choices=["hour", "day"], default="hour")
        if name == "pay":
            q.add_argument("--live", action="store_true",
                           help="actually send. Without it, nothing moves and the reservation is rolled back.")
    c = sub.add_parser("claim")
    c.add_argument("--referrer", required=True)
    c.add_argument("--referred", required=True)
    c.add_argument("--block", default="")
    a = p.parse_args()
    if a.cmd == "score":
        score(a.period)
        return 0
    if a.cmd == "pay":
        return pay(a.period, a.live)
    return claim(a.referrer, a.referred, a.block)


if __name__ == "__main__":
    sys.exit(main())
