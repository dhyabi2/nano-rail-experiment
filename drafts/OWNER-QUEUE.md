# For the owner: everything waiting on you or the box, in one ranked list (challenge #210)

The keeper has moved every blocker it can move from this repository. What still stops an outside agent from earning
or paying here is in this list: things only the owner, the Unstuck network's code (Vercel) or the box's Caddy and cron
can change. Each row links the draft with the exact change. **Work it top to bottom; row 1 and 2 are most of the value.**

Re-measure any time, free and read-only: `python3 ops/check-owner-queue.py` (exit 1 while anything is WAITING). Every
keeper run re-runs it and copies the result into that day's journal. UNKNOWN means the probe could not run, never "fine".

Also waiting on the owner, not probed: PR #89 and PR #118 (seed and wallet paths, which the keeper may not merge).

| # | state | who | action | unblocks | measured 08:22 UTC 2026-11-04 | draft |
|---|---|---|---|---|---|---|
| 1 | **WAITING** | owner | restart the five paid sellers | every paid call but the echo; STEP 6 of every guide | 0 of 5 sellers' /.well-known/x402 answered | `drafts/owner-box-down-2026-10-23.md` (#197) |
| 2 | **WAITING** | owner | restart the treasury auto-receive | a payment to us is income only once received | 1 block(s) receivable: 5EE71904 | `drafts/owner-box-down-2026-10-23.md` (#148) |
| 3 | **WAITING** | network | accept token for pre-rule asks, and in llms.txt | paying outside answers #317, #318; any stranger accepting | llms.txt never names accept_token | `drafts/box-accept-token-legacy-asks.md` (#109) |
| 4 | **WAITING** | network | fix the echo's description (asking is free) | the cheapest conversion: posting an ask | description still says '...post an ask...' | `CHALLENGES-SOLVED.md #199` (#199) |
| 5 | **WAITING** | network | link bounties and canon from llms.txt, agent.json, sitemap | machine readers finding the offer at all | llms.txt does not link bounties.txt | `drafts/unstuck-machine-routes-link-bounties.md` (#138) |
| 6 | **WAITING** | box | answer GET on the echo with 405 + the POST | the most-knocked dead end | GET echo -> 404 | `drafts/box-dead-ends.md` (#204) |
| 7 | **WAITING** | network | stop calling the onramp's server-made seed 'yours' | trust in the first wallet step | a live guide still calls the onramp's server-made seed yours | `drafts/unstuck-llms-onramp-seed.md` (#75) |
| 8 | **WAITING** | network | quote a fresh amount per echo 402 | a buyer's payment being claimed by a watcher | two 402s quote the same amount 1000000000000000000000000000 raw | `drafts/box-echo-per-request-quote.md` (#179) |
| 9 | **WAITING** | box | host the keyless Nano x402 facilitator | the x402 seller that asked for one (10-28) | /x402/facilitator/supported -> 426 | `drafts/box-nano-x402-facilitator.md` (#175) |
| 10 | **WAITING** | box | count our probes as ours in the traffic file | an honest 'did anybody come' every day | ours_requests 0 although our probes ran today | `drafts/box-count-our-probes.md` (#207) |
| 11 | **UNKNOWN** | box | publish a failed TVL read as null, not 0 | a true TVL number | read was complete; the fault only shows on a failed read | `drafts/box-tvl-unknown-not-zero.md` (#97) |
| 12 | **APPLIED** | box | serve robots.txt, llms.txt, sitemap at the box root | crawlers finding /ai/ | /robots.txt -> 200 | `drafts/box-root-crawler-files.md` (#71) |
| 13 | **WAITING** | network | serve /.well-known/x402 as JSON | x402 clients reading the one live paid call's terms | /.well-known/x402 served as application/octet-stream | `drafts/network-x402-json-content-type.md` (#212) |
