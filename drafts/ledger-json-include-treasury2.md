# Box change: ledger.json should count treasury2's starters (challenge #251)

For the owner or the box job that writes `https://getunstuck.space/ledger.json`. Nothing here was sent anywhere.

Measured 2026-11-11 04:2x UTC:

- `ledger.json`: `"updated": "2026-10-29"`, `opener` nano_1434j1n4... (Unstuck), `counts.starters_sent` 23,
  `unreceived` 16.
- `/ai/numbers.json` (generated 04:03): `starter_payments.starters_sent` 29, `unreceived` 21.
- rpc.nano.to: treasury2 nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy has six sends of 10^25 raw
  since 2026-11-08 (19FA2900, CD0B9A47, B8B59250, 000835AA, CD9AE212, DFCD32FA); blocks_info says five are still
  receivable at their payees, DFCD32FA received.

Asked of the box: regenerate `ledger.json` from the same source as `numbers.json` (`node opener/send.js --counts`),
list both senders (the Unstuck opener before 2026-11-08, treasury2 after) and refresh `updated` on every run. Once it
does, remove the STALE lines from bounties.txt section 5 and the AI directory's "openings ledger" row, and change
`specs/test_ledger_json_not_current.py` with them.
