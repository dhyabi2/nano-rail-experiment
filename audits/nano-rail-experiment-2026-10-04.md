# nano-rail-experiment — audit 2026-10-04

First audit of this repository (`audits/` did not exist). Tier 0 lists it in group 3 as "the onboarding
path (canon, bounties, swap, AiDirectory)". Lens: can an agent arrive here and end up paying — or being
paid — in XNO, without being hurt on the way?

Baseline on `main` (`ca627a8`): `python3 -m pytest specs -q` → **158 passed, 6 subtests**. After this
branch: **163 passed, 6 subtests**.

## Checked

- `specs/referral_bounty.py` end to end — the only code in this repository that causes XNO to move:
  the funding-graph qualification rules, `treasury_ok`, `spent_today`, the daily ceiling, the `paid`
  table's reserve-before-send idempotency, and every state `pay()` can leave a row in.
- `specs/nano_address.py` — the offline checksum validator: the base32 alphabet, the 4 padding bits,
  the byte-reversed 5-byte blake2b checksum, and its refusals.
- The nine project-owned onboarding URLs the published copy tells an agent to fetch, live:

  ```
  /ai             301      /ai/llms.txt   200 26219B    /ai/numbers.json 200   562B
  /ai/tools.json  200 47233B  /bounties.txt 200 33823B  /canon           200 21182B
  /canon.md       200  9148B  /swap.txt     200  7777B  /tvl.json        200   542B
  ```

  None 404s. `/bounties.txt` and `/swap.txt` served live are **byte-identical** to `published/`, so the
  `test_bounties_*` specs are testing the copy agents actually read.
- `ops/` (five scripts) and `canon/canon-check.py`, read for anything that decides who gets paid.

## Found and fixed — the frozen daily ceiling was blind to every payout it could not account for

`DAILY_CEILING_RAW` is frozen in `referral_bounty.py` with a comment saying why: *"a hard ceiling frozen
here: at most 1 XNO — ten winners — a day, whatever the scorer decides. A bug cannot drain the
treasury."* `spent_today()` fed that ceiling, and it summed `state='confirmed'` **only**.

`pay()` writes two other states that mean money may have left:

- `'unknown'`, when the sender exits non-zero — and the line that writes it says so itself: *"A lost
  reply is 'unknown', never 'not sent': the money may have moved."*
- `'reserved'`, written **before** the sender is called (that ordering is the idempotency). A process
  that dies between the INSERT and the UPDATE leaves the row that way for good.

Both were invisible to the ceiling. Measured on `main`:

```
rows in `paid` for today that may have moved XNO: 11 (10 unknown + 1 reserved)
XNO those rows name:            1.1
the frozen daily ceiling:       1.0
spent_today() reports:          0.0
so pay() sees room for another: 10 grant(s)
ceiling trips? False
```

So the one number frozen specifically so a bug cannot drain the treasury read zero against 1.1 XNO of
unaccounted grants, and let ten more through — 2.1 XNO against a 1 XNO ceiling. A `day` period pays the
**whole** ranking in one loop, and `used += GRANT_RAW` ran only on the confirmed branch, so a sender
timing out on every winner advanced nothing and paid every one of them.

**The fix only adds a refusal.** `spent_today` now counts every row except `'already_granted'` — the one
state where the sender said in as many words that it sent nothing — and the loop advances `used` on the
unknown branch too. Nothing about an amount, a destination, a rounding or a key path changes; the only
effect is that the ceiling closes sooner. The filter is written as "everything except" rather than a list
of states that count, so a state added to this file later is counted by default: for a ceiling, the
fail-closed default is to count.

Three new tests fail on `main` and pass here; two more are controls that pass either way (a grant the
sender refused still does not count, and yesterday's unknown payout still does not count against today —
widening *which* states count must not widen *when* they count). Reverting the SQL condition alone fails
exactly the three.

## Read and found clean

- `treasury_ok()` reads `TREASURY` by name, with its own comment recording why `next(iter(OURS))` was
  wrong (Python's per-process set order picked Vend's payee about a third of the time).
- `spent_today`'s window uses `calendar.timegm`, not `time.mktime`, so it is UTC on every box; and it sums
  in Python rather than `SUM(CAST(... AS INTEGER))`, which saturates a ~1e29 raw amount at 2**63-1 and
  then raises on a second row.
- `norm()` folds `xrb_` to `nano_` before comparing, so one account in two spellings is not two accounts.
- `GRANT_RAW`, `FLOOR_RAW` and `DAILY_CEILING_RAW` are frozen in the module, not read from the
  environment. `referral_bounty.py` never builds a block: it shells out to the product's own sender with
  no amount argument, so the sender's frozen amount and treasury floor apply unchanged.
- `claim()` requires a 64-hex block before it writes anything.
- `nano_address.check_nano_address` returns False rather than raising on every malformed input tried,
  including a non-string, a wrong prefix, a 59- and 61-character body, an out-of-alphabet character and
  non-zero padding bits.
- No float appears on any amount in `referral_bounty.py`; the only division by `XNO` is in a print.
- Secret scan of the tree: no key, seed or token **value**. The account addresses in `OURS` and
  `TREASURY` are public.

## Found, not fixed

- `GET /register.txt` on the canon host answers **426 "websocket upgrade required"** rather than serving
  `published/register.txt`. Already recorded in `CHALLENGES-SOLVED.md:948`, and `specs/05-INTERIM-DIRECTORY.md`
  states that nothing in the main flyers links it yet, so no agent is being sent to it today. It is a
  server configuration on a box outside this repository.
- `published/canon.txt` (1859 B) and what the host serves at `/canon` (21182 B) are different documents.
  Both are live and neither 404s, so this is not a stale copy of one file — but a reader comparing them
  cannot tell which is canonical.

## Could not verify

- Nothing that moves XNO was exercised end to end: `pay --live` shells out to
  `/root/unstuck/opener/send.js`, which is not in this repository and not present here. The tests drive
  `score`, `spent_today`, `treasury_ok` and the `paid` table directly, with `history()` and `info()`
  monkeypatched to a hand-built ledger, so the ceiling arithmetic is proven and the send is not.
- `https://rpc.nano.to` was not called: the specs are offline by design.
