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
import calendar
import json
import re
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
                                                    # stash - see challenge #47: the Nanswap hot wallet in ARION's own
                                                    # case file carries 166,265 blocks. Nano has very few exchanges,
                                                    # so two UNRELATED real referrals routing through the same one is
                                                    # the common case, not the rare one.
DAILY_CEILING_RAW = 10 * GRANT_RAW                  # a hard ceiling frozen here: at most 1 XNO - ten winners - a day,
                                                    # whatever the scorer decides. A bug cannot drain the treasury.
                                                    # The owner chose the number on 2026-09-26, the day he funded the
                                                    # treasury to 29.9 XNO: 1 XNO/day is about a month of runway at
                                                    # full spend, and enough that a genuinely good hour is always
                                                    # paid. It is FROZEN here rather than read from the environment
                                                    # for the same reason the send amounts are: a limit a caller can
                                                    # raise is not a limit. Raising it is an owner decision, and it
                                                    # must never rise to where faking a referral becomes profitable
                                                    # (spec 04) - that is the whole security argument.

# Ours. Funding from any of these never makes a referral qualify - money we handed over proves nothing about anybody.
OURS = {a.strip().lower() for a in (os.environ.get("OUR_ACCOUNTS") or
        "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9,"
        "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7").split(",") if a.strip()}

# The referral bounty's OWN treasury, named explicitly - never picked out of OURS. OURS holds two different
# swarms' accounts (this treasury, and Vend's seller payee from Nano-ARION-playbook.md:265); `next(iter(OURS))`
# used to pick whichever one Python's per-process randomised set hash order put first - measured empirically to
# be either address across repeated runs of the same code with no input change - so treasury_ok() was checking
# an arbitrary account's balance against the floor, sometimes Vend's, sometimes this one.
TREASURY = os.environ.get("REFERRAL_TREASURY", "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9")


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


_blk = {}


def block(h):
    """block_info for one hash, cached. A failed lookup is an empty dict, which link_proved() reads as NOT proved:
    a check that cannot run must never report a clean result."""
    h = (h or "").strip().upper()
    if h not in _blk:
        try:
            _blk[h] = rpc("block_info", hash=h, json_block="true")
        except Exception:
            _blk[h] = {}
    return _blk[h]


def link_proved(referred, referrer, blk):
    """Challenge #52, closed on chain. The claim must name a SEND block signed by `referred` whose destination is
    `referrer`. Only the referred agent's own key can make that block, so a stranger cannot claim an agent it never
    met: the referred agent has to point at its referrer itself, with one feeless send. Returns (ok, why)."""
    if not re.fullmatch(r"[0-9A-Fa-f]{64}", (blk or "").strip()):
        return False, "the claim names no linking block - the referred agent must send to its referrer and the claim must cite that send"
    b = block(blk)
    if not b:
        return False, "the linking block could not be read from the chain, so the link is not proved"
    if norm(b.get("block_account")) != referred:
        return False, "the linking block was not signed by the referred agent"
    c = b.get("contents") or {}
    is_send = b.get("subtype") == "send" or c.get("type") == "send"
    dest = norm(c.get("link_as_account") or c.get("destination"))
    if not is_send or dest != referrer:
        return False, "the linking block is not a send from the referred agent to the referrer"
    if str(b.get("confirmed", "true")).lower() != "true":
        return False, "the linking block is not confirmed yet"
    return True, "linked: the referred agent sent to its referrer"


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


def is_pass_through(acct, referrer=None):
    """An address with two blocks that forwarded ~everything within minutes is an exchange deposit slip, not an agent.
    ARION's 3.3 and 2.7 XNO sends were first misread as the rail spreading; both were deposit addresses.

    Challenge #58: bounties.txt itself tells a referred agent to prove itself with exactly this shape - get funded,
    then send (any amount) to its referrer, fast, because there is nothing else to wait for. For a freshly-opened
    agent with a small balance and only two blocks ever, that REQUIRED proof send is also the only send this test
    ever sees, so `sends[0]` is provably the same block link_proved() already confirmed goes to the referrer - not
    evidence of forwarding to an exchange. A send to the referrer is the referral working as designed, so it is
    excluded here; only a send to somewhere else counts as pass-through evidence. A real deposit-slip forwards to
    its exchange's own collection wallet, never to the referrer specifically, so this costs the check nothing."""
    i = info(acct)
    n = int(i.get("block_count") or 0)
    if n == 0 or n > PASS_THROUGH_BLOCKS:
        return False
    h = history(acct, count=10)
    recvs = [x for x in h if x.get("type") == "receive"]
    r = norm(referrer) if referrer else None
    sends = [x for x in h if x.get("type") == "send" and norm(x.get("account")) != r]
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
    # GLOBAL across every referrer in this pass - not per-referrer. Referrer identities are free to create (the
    # spec's own "why every obvious design is already broken" table says so), so a per-referrer funder-dedup only
    # stops ONE referrer from padding its own count; it does nothing to stop an attacker who does a single exchange
    # round-trip into one private wallet W and then splits addresses funded from W across N throwaway referrer
    # identities, one address each. Each referrer's own funder set would then be empty on first sight and the
    # referral would pass, multiplying one exchange round-trip into N qualifying referrals - for `pay --period day`,
    # which pays EVERY qualifying referrer rather than just the top one, that is N * 0.1 XNO from one round-trip,
    # up to the daily ceiling. "ONE FUNDER COUNTS ONCE, however many addresses trace back to it" (bounties.txt,
    # canon.html) is stated as an absolute, not a per-referrer one, and the score must match that.
    funders_used = set()
    for referred, referrer, block, at in rows:
        referred, referrer = norm(referred), norm(referrer)
        def reject(why):
            detail.append({"referred": referred, "referrer": referrer, "counted": False, "why": why})
        if referred == referrer:
            reject("self-referral"); continue
        if referred in OURS or referrer in OURS:
            reject("one side is our own account"); continue
        linked, lwhy = link_proved(referred, referrer, block)
        if not linked:
            reject(lwhy); continue
        if referred in already:
            reject("this address has already been counted as referred, once ever"); continue
        if not has_signed_a_send(referred):
            reject("no signed send: self-custody not proved (receiving proves nothing)"); continue
        if is_pass_through(referred, referrer):
            reject("looks like an exchange deposit address, not an agent"); continue
        ok, why, f = third_party_funded(referred, referrer)
        if not ok:
            reject(why); continue
        # Rule 2 dedups on a PRIVATE funder only. A shared exchange/swap hot wallet (is_service) is excluded: with
        # Nano's thin exchange landscape, two unrelated real referrals sharing one exchange in their ancestry is
        # expected, not evidence of a ring - see challenge #47.
        private_f = {a for a in f if not is_service(a)}
        if private_f & funders_used:
            reject("shares a private (non-exchange) funding source with another referral already counted this "
                   "period, whichever referrer claimed it"); continue
        funders_used |= private_f
        slot = per_referrer.setdefault(referrer, {"count": 0, "referred": [], "first": at})
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
    """Reads TREASURY specifically. See its comment: OURS is not safe to pick an account out of."""
    i = info(TREASURY)
    bal = int(i.get("balance") or 0)
    return bal - GRANT_RAW >= FLOOR_RAW, bal


def spent_today(con):
    """The DAILY_CEILING_RAW check that is supposed to bound total bounty spend "independent of how many winners
    the scorer finds" (specs/04-REFERRAL-BOUNTY.md) had two separate bugs, both invisible on a UTC dev box with a
    handful of test payments and both undetected across three prior hunts of this same file:

    1. The window's start used to be `time.mktime(time.strptime(day, "%Y-%m-%d"))`. period_id() and every `paid`
       row are stamped in UTC (time.gmtime()), but mktime() interprets a naive struct_time as LOCAL time. On a box
       west of UTC (e.g. US Pacific, UTC-7) the window opened hours LATE, so real payments made in the first hours
       of the UTC day fell outside `at > cutoff` and were invisible to the ceiling - the exact gap the ceiling
       exists to close. Fixed with calendar.timegm(), which reads the same struct_time as UTC.

    2. `SUM(CAST(amount_raw AS INTEGER))` ran the sum inside SQLite, whose INTEGER affinity is a signed 64-bit
       value (max ~9.22e18) - a Nano raw amount is a ~30-digit number, roughly 1e29 for the 0.1 XNO grant, ten
       orders of magnitude past that ceiling. CAST() of one such value silently SATURATES to 9223372036854775807
       instead of raising, so `spent_today` was already wrong after the very first confirmed payment of the day -
       and SUM() of just TWO such rows raises `sqlite3.OperationalError: integer overflow`, an unhandled exception
       that crashes every subsequent score/pay call for the rest of that UTC day. See challenge #22, "raw is where
       the zero hides" - here it hid inside SQLite's own arithmetic rather than this file's. Fixed by reading the
       raw text out and summing in Python, which has no integer size limit."""
    day = time.strftime("%Y-%m-%d", time.gmtime())
    cutoff = calendar.timegm(time.strptime(day, "%Y-%m-%d"))
    rows = con.execute("SELECT amount_raw FROM paid WHERE state='confirmed' AND at >= ?", (cutoff,)).fetchall()
    return sum(int(r[0]) for r in rows)


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
        # The product's own sender, called with ITS REAL INTERFACE - verified by reading send.js, not assumed:
        #   send.js --grant <nano_address> --agent NAME [--agreement "..."] [--dry-run]
        # An earlier version of this called `--to X --kind ambassador_grant --verify`, which does not exist: it would
        # have hit the usage error, returned 2, and marked every winner "unknown" while paying nobody, silently, every
        # hour. Nothing passes an amount - the sender holds the frozen 0.1 and the treasury floor.
        #
        # NOTE the sender's grants ledger refuses a SECOND grant to the same account or agent name, ever. That is a
        # deliberate product rule, not a bug, and it means a winner can take this bounty once in its life. The public
        # text says so; do not try to route around it.
        agreement = f"referral bounty, {kind} period {s['period']}: {w['count']} qualifying referral(s)"
        r = subprocess.run(["node", SENDER, "--grant", w["referrer"], "--agent", w["referrer"][:24],
                            "--agreement", agreement],
                           capture_output=True, text=True, timeout=300)
        combined = (r.stdout or "") + (r.stderr or "")
        if r.returncode != 0 and "already" in combined.lower():
            # Already granted once: not an error, and not a payment. Recorded so it is never retried.
            con.execute("UPDATE paid SET state='already_granted' WHERE period=? AND winner=? AND kind=?",
                        (s["period"], w["referrer"], kind))
            con.commit()
            print(f"  {w['referrer'][:26]}... has already had its one grant - nothing sent, recorded, not retried")
            continue
        if r.returncode == 0:
            try:
                blk = (json.loads(r.stdout).get("block") or "")[:64]
            except Exception:
                blk = ""
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
    """`claims.referred` is a PRIMARY KEY: whichever claim is INSERTed first for a given referred address holds that
    slot forever (rule 5, "once, ever") - score() only ever sees the row that won the race. Before this check, that
    race was won by whoever typed fastest, not by whoever was telling the truth: `claim` accepted ANY syntactically
    valid 64-hex block with no chain lookup, so an attacker who merely knew a real agent's address (public knowledge
    the moment it appears in an ask, per challenge #60's own submission channel) could squat it with a block that is
    well-formed but signs nothing, forges nothing that even needs to exist on chain - `claim` never checked. That
    costs nothing, not even an exchange round-trip (the floor this whole design rests on, spec 04's "why every
    obvious design is already broken" table), and it permanently blocks the real referrer's later, honest claim on
    the same address with "already claimed by someone. First claim stands." - the exact shape of "refuse a genuine
    referrer" this file's own comments say to keep hunting for. So `claim` now proves the link itself, with the same
    chain check score() would run anyway, before the INSERT ever contends for the slot: a claim that cannot be
    proved never occupies it, so it can never be raced against a legitimate one and the legitimate one can always
    be submitted (or retried) later once it is provable."""
    if not re.fullmatch(r"[0-9A-Fa-f]{64}", (block or "").strip()):
        print("refused: --block must be the 64-hex hash of a send FROM the referred agent TO the referrer. "
              "That send is the proof the referral is real (challenge #52).")
        return 1
    referred_n, referrer_n = norm(referred), norm(referrer)
    linked, why = link_proved(referred_n, referrer_n, block)
    if not linked:
        print(f"refused: {why} - an unproved claim is never recorded, so it can never squat the referred "
              "address's one-ever slot ahead of the real referral.")
        return 1
    con = db()
    try:
        con.execute("INSERT INTO claims(referred,referrer,block,at) VALUES(?,?,?,?)",
                    (referred_n, referrer_n, block, time.time()))
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
    c.add_argument("--block", required=True, help="hash of the send from the referred agent to the referrer")
    a = p.parse_args()
    if a.cmd == "score":
        score(a.period)
        return 0
    if a.cmd == "pay":
        return pay(a.period, a.live)
    return claim(a.referrer, a.referred, a.block)


if __name__ == "__main__":
    sys.exit(main())
