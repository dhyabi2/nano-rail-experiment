# nano-rail-experiment — audit 2026-10-11

Lens: can an agent pay or get paid in XNO through this onboarding path today, without being hurt.

## Checked

- Baseline on `main` (`3eddc69`): `python3 -m unittest discover -s specs -t specs -p "test_*.py"`
  **236 passed**, and every `specs/test_*.py` also exits 0 when run on its own, the way its own
  header tells a reader to run it.
- `specs/referral_bounty.py` end to end — the only file here that can make XNO move. Read under
  three questions: can it pay a Sybil ring, can it pay twice, can it overrun a bound.
  - Amounts are integer raw throughout. `GRANT_RAW`, `FLOOR_RAW` and `DAILY_CEILING_RAW` are
    integer literals; a `grep` for `float`, `round(`, `Decimal` and division by `XNO` across
    `specs/`, `ops/`, `canon/` and `published/` finds no float on an amount — the two hits are a
    comment at `referral_bounty.py:220` explaining why a float is *not* used, and an age in hours
    in `ops/scan-ask-inbox.py`. Division by `XNO` appears only inside display strings.
  - Idempotency: the `paid` table's key is (period, winner, kind) and an `IntegrityError` on
    insert skips the winner, so a repeated run cannot pay twice. A lost sender reply is recorded
    `unknown`, never "not sent", and nothing retries it automatically.
  - `spent_today()` sums the raw text in Python rather than through SQLite's 64-bit `CAST`, counts
    every state except `already_granted`, and opens the window with `calendar.timegm` so a box
    west of UTC cannot hide the day's first hours. All three were earlier defects and all three
    are closed, with the measurements in the docstring.
  - `score()` dedups private funders **globally** rather than per referrer, which is what stops one
    exchange round-trip being split across N throwaway referrer identities.
  - The treasury floor was the one bound that did not hold. See below.
- `link_proved` / `third_party_funded` / `is_pass_through` / `is_service`: a claim is a pointer and
  the chain decides; the cited block must be confirmed, a `send`, signed by the referred agent and
  addressed to the referrer. The attack cases (claim-jacking a stranger, citing a real send made to
  somebody else, citing a self-signed block) each have a law in `specs/test_referral_bounty.py`.
- `published/bounties.txt`, the page an outside agent actually starts from: STEP 1's stdlib-Python
  wallet is exercised by `specs/test_bounties_step1_python.py` against the docs.nano.org
  seed-of-zeros test vector, and that suite passes. STEP 2's warning that
  `extract.paypercall.dev`'s `address_valid` is a prefix-and-length check rather than a checksum is
  still in the text, with the local `checkAddress` call beside it.
- `specs/nano_address.py` and its tests: base32 decode plus the little-endian blake2b-5 checksum,
  one-character-off addresses refused.
- No secret in the working tree: `GRANT_RAW` and the treasury address are public; `REFERRAL_DB`,
  `REFERRAL_SENDER`, `NANO_RPC_URL` and `OUR_ACCOUNTS` all come from the environment, and the
  sender itself (`send.js`) lives outside this repository with the amount frozen in it.

## Found and fixed

**`referral-bounty pay --period day` paid past the treasury floor.** `pay()` calls `treasury_ok()`
once, before the loop, and `treasury_ok()` asks a single question: does **one** grant still leave
the 8.9 XNO floor standing. For `--period hour` that is the whole question, because an hour pays one
winner. `--period day` pays the **entire ranking** — `score()`'s own `funders_used` comment says so
in as many words — and from the second winner on nothing asked again.

Measured against the fake chain, with the treasury at 9 XNO (one grant of room above the floor) and
three qualifying referrers:

```
PAID 0.1 XNO to nano_1refone...
PAID 0.1 XNO to nano_1reftwo...
PAID 0.1 XNO to nano_1refthree...
total granted:  0.3000 XNO
treasury after: 8.7000 XNO   floor: 8.9000 XNO   -> BELOW THE FLOOR
```

The daily ceiling cannot catch this: it bounds ten grants (1 XNO), and the floor can have room for
one. `FLOOR_RAW`'s own comment is "bounties stop before the treasury does".

The fix re-asks the floor per grant, against the balance read before any send minus what this run
has already granted, and stops the loop when the next grant would cross it. **It only ever
refuses:** no amount, destination, rounding, key path or sender argument changes, nothing passes an
amount to `send.js` (which still holds the frozen 0.1 and its own floor), and a run that was within
the floor before behaves exactly as it did. A reservation consumes floor room in a dry run as in a
live one, so the dry run now predicts what the live run will do rather than promising three sends
where one happens.

Two laws, both failing before the change and passing after:
`test_a_day_run_stops_at_the_treasury_floor_not_one_grant_short_of_it` (3 sends → 1, treasury not
below the floor) and `test_a_dry_day_run_promises_only_what_the_floor_allows`. Suite after:
**238 passed**.

## Could not verify

- `send.js` is not in this repository, so its own treasury floor and its "one grant per account,
  ever" ledger rule were read only through `referral_bounty.py`'s comments, not exercised. The fix
  above is a second line of defence in front of them, not a replacement.
- STEP 1's wallet script was not executed by hand this run: generating a seed is a credential the
  auditor is not permitted to materialise, so the derivation is trusted to the repository's own
  test-vector law rather than re-run here.
- The live URLs on `published/bounties.txt` were not fetched this run. The 4-hourly conversion
  blocker hunter owns that check and `journal/2026-10-11.md` records its latest find (the
  directory's own JSON link answering 426, fixed in #126).
- `dhyabi2/nano-rail-experiment#89` is left open: it changes `nanokey.py`, the published key
  generation script, and a key path is the owner's, not a routine's.
