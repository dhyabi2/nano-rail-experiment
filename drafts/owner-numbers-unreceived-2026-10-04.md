# For the owner: /ai/numbers.json says 0 unreceived starters; the chain says 16 of 21

*Draft by the experiment keeper, 2026-10-04 ~12:40 UTC. Nothing here was sent anywhere. Challenge #95.*

- `/ai/numbers.json` `starter_payments.unreceived`: 15 at 04:03 UTC, **0 from 08:03** (still 0 at 12:03).
- Chain, rpc.nano.to 12:30 UTC: Unstuck's account `nano_1434j1n4...` made 21 starter sends (11 x 10^22 raw, 10 x 10^25 raw);
  `blocks_info` with `receivable:true` says **16 are still receivable**.
- getunstuck.space/ledger.json (updated 2026-10-03) says 15.
- Between ~08:00 and ~08:30 rpc.nano.to answered every POST with 429 `api_key_required_for_heavy_usage` (#94).

Likely cause, not verified (the code is in `dhyabi2/unstuck`, outside this routine's reach): `opener/send.js --counts`
treats a failed or refused `receivable` read as "nothing receivable", so a 429 reads as "all received".
`published/aidirectory/numbers.py` already keeps the old file when a source *fails*, but a source that *succeeds with
a wrong number* passes through.

Suggested fix: in `--counts`, count an account as received only on an explicit RPC answer with no matching block, and
exit non-zero on any error reply (`error`, HTTP 429/5xx), so numbers.py keeps the previous, dated file.

Re-count from anywhere:

    python3 -c "import json,urllib.request as u;R=lambda d:json.load(u.urlopen(u.Request('https://rpc.nano.to',json.dumps(d).encode(),{'Content-Type':'application/json','User-Agent':'my-agent/1'})));h=[x['hash'] for x in R({'action':'account_history','account':'nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9','count':-1})['history'] if x['type']=='send' and x['amount'] in ('10000000000000000000000','10000000000000000000000000')];b=R({'action':'blocks_info','hashes':h,'receivable':'true'})['blocks'];print(sum(b[k]['receivable']=='1' for k in h),'of',len(h),'starters still receivable')"
