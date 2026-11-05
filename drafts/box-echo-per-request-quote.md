# For the owner: make /unstuck/api/v1/echo quote a new amount per 402 (challenge #179)

**Measured 2026-10-29 08:24 UTC.** `GET https://getunstuck.space/unstuck/api/v1/x402` and two unpaid
`POST /unstuck/api/v1/echo` calls all named `amount 1000000000000000000000000000` (0.001 XNO) to
nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9. The paid retry carries only
`X-Nano-Payment: <BLOCK_HASH>`.

**Why it matters.** A Nano block has no memo. With one price for everyone, anyone watching that account's
public history can see a buyer's send land and present the hash first. They are served on the buyer's
payment. This is the exact shape bounties.txt section 7 (#178) tells outside
sellers to avoid. The guides now warn buyers to send and present at once (#179). That shrinks the window
but does not close it.

**The change (server-side, in the Unstuck API on Vercel; not in this repo):**
1. On each unpaid POST, quote `price + 1 + secrets.randbelow(10**6)` raw (or the JS equivalent with
   `crypto.randomInt`), keep it with an id for 300 s (`maxTimeoutSeconds`), and return that amount and id
   in the 402 and in `payment-required`.
2. On the paid retry, accept the hash only when the block's amount equals that id's quote. Mark the
   hash used.
3. Keep `GET /v1/x402` naming the base price, and say that each 402 adds a tail of at most 10^6 raw.

Once that is live, the buyer warning in the seven guides can change to "pay the 402's own amount", and
`specs/test_paid_call_race_warning.py` changes with it.
