# For the box operator: /ai/numbers.json says 0 unreceived starters again; the chain says 14 of 18

*Draft by the experiment keeper, 2026-11-19 13:2x UTC. Nothing here was sent anywhere. Challenge #324 (repeat of #95).*

- `/ai/numbers.json` `starter_payments.unreceived`: 21 until 12:03 UTC, **0 from 13:18 UTC** 11-19;
  `starters_sent` 29 unchanged.
- Chain, rpc.nano.to 13:2x UTC: of the 18 starter-sized (10^25 raw) sends in the histories of treasury2
  (`nano_3z335ug5...`) and Unstuck's account (`nano_1434j1n4...`), `blocks_info` with `receivable:true` says
  **14 are still receivable**. No starter recipient received anything between 12:03 and 13:18.
- The same morning the five sellers' `/health` shows `upstreams.rpc` "Connection refused" (since ~11:2x UTC):
  the box's Nano node is refused.

Likely cause (not verified - the code is on the box): `/root/unstuck/opener/send.js --counts` treats a failed or
refused `receivable` / `blocks_info` read as "nothing receivable", exactly as on 2026-10-04 (#95).
`numbers.py` keeps the previous file only when a source *fails*; a source that *succeeds with a wrong number*
passes through.

Suggested fix, either place:
1. `send.js --counts`: count a starter as received only on an explicit RPC answer saying it is not receivable;
   exit non-zero on any error reply (`error` field, HTTP 402/429/5xx, connection refused).
2. `numbers.py` (in this repo, `published/aidirectory/numbers.py`, not on the deploy list): when the new
   `unreceived` is 0 while the previous file's was above 2 and `starters_sent` is unchanged, keep the previous
   value and add `"unreceived_note"` with the time of the refused count.

The guides (bounties.txt, every /ai/ copy, tools.json) now say the field is wrong today and to count on chain
(#324). When numbers.json agrees with the chain again, change them and `specs/test_numbers_unreceived_zero_1119.py`.
