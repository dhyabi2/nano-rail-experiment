# Box: the Vend sellers' X-BALANCE route is keyed by a public address (challenge #262)

For the owner / operator of the Unstuck box, where the Vend API (all five paypercall.dev sellers) runs. Nothing
here was sent anywhere; the keeper does not change seller code.

## What was measured (00:2x UTC 2026-11-13, from the cloud)

- Every unpaid seller call answers 402 with: "Pay ... and retry with X-PAYMENT header, or use X-BALANCE with a
  nano_ account that holds a prepaid balance".
- `POST /api/v1/balance/top-up` (no body) -> 402 "Provide a Nano block hash via X-PAYMENT header to fund your balance".
- `GET /api/v1/balance?account=nano_...` -> 200 with balance_raw, topup_count and recent_topups for ANY address,
  no key or signature asked.
- `X-BALANCE: <address>` on a paid route -> 402 when the address has no balance. Neither the 402 nor the manifest
  names any proof that the caller holds that address's key.

## Why it matters

If the spend path checks nothing but the address in the header, then once any agent prepays, anyone who reads that
agent's address (it is on the public ledger, in the top-up's own block) can spend its balance. Not proved: no
balance was funded, and the keeper never sends.

## What would close it (pick one)

1. Require a signature over the request (or a nonce the server issues) by the account's key with X-BALANCE; or
2. Return an opaque balance token from top-up, and accept that instead of an address; or
3. Drop X-BALANCE from the 402 message until one of the above exists.

Until then the AI directory tells strangers to skip X-BALANCE and pay each call with X-PAYMENT (#262).
