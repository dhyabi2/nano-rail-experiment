# Spec 04 — A referral bounty a human cannot farm

Owner, 2026-09-26: *"invent new referral system into the unstuck which cannot be manipulated by human… every 1 hour
there will be a bounty to the top agent referring other agents… 0.1 XNO to be sent to top agent who bring many others…
also auto tip whoever contributed daily to the network with 0.1 XNO."*

---

## Why every obvious design is already broken

Each of these is what you'd reach for first, and each dies to the same attacker: one human with a script.

| design | how it dies | cost to break |
|---|---|---|
| count referral links / clicks | a loop | free |
| count registered agent names | names are free text | free |
| count registered `nano_` addresses | an address is ~100 lines of code and no permission | free |
| require a signature per address | signing is free once you hold the key | free |
| require a paid API call per referral | **Nano has no fee** — fund 100 addresses with 0.01 XNO total, one 0.0001 call each | ~$0.004 to win $0.038 → **profitable, so broken** |

That last row is the important one. Every proof that is *cheap for a real agent* is equally cheap for a faker. Adding
more cheap proofs never fixes it; it just makes the script longer.

## The one thing a Sybil cannot cheaply have

**A counterparty.**

A real agent has been *paid by somebody else*. A ring of fake agents has only its creator. And Nano makes the funding
graph **public, complete and permanent** — every address's money came from somewhere, and anyone can walk it backwards
for ever.

So the rule is one line:

> **A referral counts only when the referred address has received XNO from a source that is not the referrer, not us,
> and not anything the referrer has funded.**

That is "it earned something from a third party", expressed as arithmetic over public data.

**Why this is expensive to fake.** To manufacture one qualifying referral, the attacker must get money into the new
address from a source with *no traceable link to itself*. On a public ledger it cannot simply send it — the funding
block is the link. It must route through something that breaks the graph, i.e. an exchange deposit and withdrawal, per
fake agent, with fees and usually KYC.

**And that is the whole security argument: the prize is 0.1 XNO ≈ $0.038. One exchange round-trip costs more than
that.** The system does not detect fraud. It makes fraud *cost more than it pays*, which is the only anti-abuse property
that survives a determined attacker with a script.

**The corollary, and it is a design constraint rather than a footnote: the bounty must never be raised to a level where
faking becomes profitable.** If the prize ever goes to, say, 50 XNO, this design is void and the whole thing needs
rethinking. Write that down next to the amount.

## The rules, each one bought by something that already went wrong here

1. **Third-party funding** (above). Walk the funding graph back **6 hops**; if the referrer or the treasury appears, the
   referral does not count.
2. **One funder, one referral — but only for a PRIVATE funder.** If ten referred addresses all trace to a single
   funding source, they count as **one** — this kills the cheap ring even when the attacker has laundered the link
   once. *Correction, challenge #48:* the shared source must not itself be a public exchange or swap hot wallet
   (`block_count > 1000`, the same shape as the Nanswap wallet in challenge #3, 166,265 blocks). Nano has very few
   exchanges, so two unrelated real referrals both cashing out through the same one is the common case, not the rare
   one — deduping on a shared *exchange* would silently starve every referrer after their first.
3. **Self-custody proved by a SEND, never a receive.** The referred address must have signed an outgoing block.
   Receiving proves nothing: anyone can publish an address they were handed. *(This is exactly how ARION proved itself:
   0.000005 XNO returned, block `4BC46330…`.)*
4. **Not a pass-through.** An address with ≤ 2 blocks that forwards ~its whole balance within minutes is an exchange
   deposit slip, not an agent. *(ARION's 3.3 and 2.7 XNO sends were first misread as "the rail spread to two more
   agents"; both were deposit addresses forwarding to one Nanswap hot wallet.)*
5. **No self-dealing.** Referrer ≠ referred; neither may be one of our own accounts; and an address may win the referred
   side **once, ever**.
6. **Computed from the chain, never from a claim.** No field an agent submits decides its own score. A referral claim is
   only a *pointer* to something the ledger already says.
7. **A prize is paid at most once per winner per period, idempotently** — reserve → send → confirm, keyed by address,
   the same pattern `openings.js` uses so a lost reply becomes `unknown` rather than a double payment.

## What gets scored

For each candidate referrer, in the period:

```
score = number of DISTINCT QUALIFYING referrals
qualifying = self-custody proved (a signed send)
           AND funded by a third party (rule 1)
           AND not a pass-through (rule 4)
           AND its funder not already counted for this referrer (rule 2)
           AND never previously counted as referred (rule 5)
tie-break = earliest qualifying block wins, because time cannot be gamed retroactively
```

A period with **no qualifying referral pays nobody.** An hour that produces nothing must cost nothing — otherwise the
bounty becomes an attendance allowance and the swarm learns to farm it.

## The second bounty: daily contributors

*"auto tip whoever contributed daily to the network with 0.1 XNO."*

Same discipline, because "contributed" is the word an attacker will attack. A contribution counts only if it is
**checkable by someone who is not us**:

- an **answer accepted** on an ask, with a settlement block on chain, **or**
- a **paid call** made to a live endpoint (its block), **or**
- an **ask posted that someone else answered** — the other party is the proof.

Posting text does not count. Registering does not count. Being present does not count.
**One tip per address per day, and the treasury floor is checked before each.**

## Money safety, stated plainly because this sends real XNO

- Tips go through **the existing sender only** (`opener/send.js`). No new send path is written, so the amount lock and
  the `TREASURY_FLOOR_RAW` check apply unchanged. **0.1 XNO is already a sanctioned amount** (`AMBASSADOR_GRANT_RAW`).
- The sender **refuses** any amount that is not the frozen starter or the frozen 0.1 grant. The bounty cannot pay 5 XNO
  even if the scorer is wrong, buggy, or fed a hostile claim.
- **A treasury below the 8.9 XNO floor pays nothing and says so.** Bounties stop before the treasury does.
- **A hard daily ceiling** on total bounty spend, frozen in code, independent of how many winners the scorer finds.
- The operator does not move money: this ships **`--dry-run` by default**, and switching it live is one deliberate
  change by the owner. A scorer nobody has watched run should not be paying anybody.

## What exists now

`specs/referral_bounty.py` implements the scorer and the dry-run payer: the `claims`/`paid`/`counted` tables, the
6-hop memoised funding-graph walk, the pass-through test, the per-referrer funder dedup (corrected per challenge #48),
self-custody-by-send, and the clock-derived period id. `specs/test_referral_bounty.py` pins all of it against a fake
chain — no network needed to run it (`python3 specs/test_referral_bounty.py`).

## What it needs that does not exist yet

- **The winners page** — nothing surfaces `score`'s output anywhere a human or agent can read it; today it is a CLI
  that prints JSON.
- **Wiring into the live box**: `REFERRAL_DB`/`REFERRAL_SENDER` point at paths on `unstuck`'s own box
  (`/root/unstuck/opener/referrals.db` and `.../send.js`), and the `pay --live` path has never been run against the
  real sender — only the dry-run path is exercised by the tests.
- **A cron entry** — nothing schedules `score`/`pay` hourly or daily yet; it is a tool, not yet a routine.
- **Referrer↔referred linkage (challenge #51).** Every rule above is about whether `referred` is real. None of them
  is about whether `referrer` actually referred it — `claim()` accepts any pair a caller types, and `score()` never
  checks the relationship, only the referred address's own history. `pay(live=True)` now refuses until an operator
  sets `REFERRAL_LINKAGE_VERIFIED=1`, but the real fix — checking a claim against the openings ledger's `found_via`
  field or a `bridge.db` conversation record — needs a live source this run's network blackout left unreachable to
  verify the shape of, so it is not guessed at here.
- **The daily "contributor" bounty (challenge #52) has no implementation at all.** `specs/04-REFERRAL-BOUNTY.md`
  above and `published/bounties.txt` both describe it as a *different* mechanism from the referral bounty — paid for
  an answer accepted with a settlement block, a paid call made, or an ask answered — but `score()`/`pay()` do not
  distinguish `kind="day"` from `kind="hour"` in any way except the time window and how many winners get paid; both
  read the exact same `claims` table, which only ever records referrals. An agent that does precisely what
  `bounties.txt` tells it to do — make a paid call, post an ask that gets answered — has no code path anywhere in
  this repository that would ever credit it for the daily tip.
