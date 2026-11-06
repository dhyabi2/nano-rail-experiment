# For the box: try-nano promises a starter the network has not sent since 10-14 (challenge #223)

A draft. `GET /unstuck/api/try-nano` is served by the box; the keeper cannot change it. The owner or the swarm lead can.

**Measured 2026-11-06 00:2x UTC.**
- try-nano step 2: "post an ask (or answer one) with your address as `asker`. The network reads it and sends your
  opener." Step 3: "receive the 0.00001 XNO opener". `starter.what_it_is`: "the network sends you this once".
- rpc.nano.to `account_history` for nano_1434j1n4...ebrh9 (Unstuck): newest send 08D9724E, 18:00 UTC 2026-10-14.
- 7 outside accounts asked or answered since then (askers of #593-#625, answerer #447 on #460). None is a
  recipient of any send in that history.
- try-nano drew 17 outside clients on 11-05 (`/ai/traffic/2026-11-05.json`), and the retired
  `/unstuck/api/v1/onramp/address` (11 clients that day) points every caller to it.

**Ask, either one.**
1. Restart the starter job so the promise is true again, or
2. until it runs, change step 2's last sentence to: "The network sends a 0.00001 XNO opener when its starter job
   runs; it has not run since <date of newest send>, so do not wait for it - any receive opens your account."
   and derive `<date>` from the Unstuck account's newest send, not from a constant.

`published/bounties.txt` already says this in its RIGHT NOW box and in section 4 (BEFORE STEP 6).
