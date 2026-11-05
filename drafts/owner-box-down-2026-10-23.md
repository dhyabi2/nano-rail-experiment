# For the owner: the Unstuck box has been down since 2026-10-17. What to restart, then what to check

*Drafted by the experiment keeper, 2026-10-23 20:3x UTC. Not sent anywhere. Every number below was measured in that run.*

## What is down (measured 20:2x UTC 10-23)

| what | how it answered |
|---|---|
| getunstuck.space/bounties.txt, /canon.txt, /canon, /swap.txt, /unstuck/api/asks | Vercel **502** `ROUTER_EXTERNAL_TARGET_CONNECTION_ERROR`. Vercel cannot reach the box. |
| 172-86-112-140.sslip.io (traffic files, deploy-status, numbers.json) | https: TLS reset. http: **503** upstream connect timeout. |
| extract, search, domain, check and geoip .paypercall.dev (172.86.112.181) | timeout on /health and /.well-known/x402 |
| swarm.getunstuck.space | timeout |
| still up: getunstuck.space/, /llms.txt, /robots.txt, /ledger.json (static on Vercel; ledger last updated 10-03) | 200 |

According to `swarm-decisions/NEEDS-OWNER.md` (row 2026-10-23), the box's last exports were at 10-17 10:11Z
(claude-results) and 10:25Z (agent-conversations).

## What the outage has cost so far

- **Treasury: one block receivable for about 5.5 days.** Block `5EE719043E7CF1F276DF2DA475440A85652F80EDCA5F469E8280E9D4EAA70E44`
  (10 XNO, sent 10-18 08:28:17 UTC from nano_3kaf7r9n...). That is one of the funding accounts you were asked on
  10-08 to confirm as ours. The auto-receive runs on the box. The balance is 71.6178 XNO, so it is not under the 9.0
  floor.
- **Every reader since 10-17 met a 502** on all four guides and on the API. Nobody could post an ask, pay an
  endpoint, or read the bounties.
- **There are no visit counts for 10-16 to 10-23 yet.** The traffic files are on the box. The keeper routine was also
  silent from 10-15 04:30 to 10-23 20:15.

## Restart

Both hosts: 172.86.112.140 (Unstuck: backend, asks API, nginx/sslip, experiment-deploy, auto-receive, traffic
exporter, relay) and 172.86.112.181 (the five paypercall sellers).

## After it is back, check in this order (the keeper will do the same at its next run)

1. `rpc.nano.to receivable` for nano_1yo6c1t6...: block 5EE71904 has been received and the balance reads 81.6178.
2. `/.well-known/x402` on all five sellers: every payTo is the treasury and every accept names XNO.
3. `/ai/traffic/deploy-status.json`: main is the current head and there is no CONFLICT.
4. bounties.txt, canon.txt and swap.txt return 200, text/plain, CORS `*`, and are byte-identical to main.
5. `/ai/traffic/2026-10-16.json` to `2026-10-23.json`: if the log kept running while the site was unreachable, these
   exist. The keeper backfills the journals from them.

## One thing worth deciding

Nothing outside the box noticed for six days. The 130-minute silence alarm lives on the box itself, and the keeper
routine was not running. A watcher that does not run on the box (a cloud routine, or an uptime check on
getunstuck.space/canon.txt) would have caught this on 10-17.
