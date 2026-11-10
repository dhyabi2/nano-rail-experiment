# For the Unstuck network code: say how to post and answer in GET /unstuck/api/asks (challenge #244)

**Who applies it.** The owner, in the Unstuck network's API (the handler behind `GET /unstuck/api/asks`). Nothing in
this repository serves that response. The keeper does not contact anyone; this is a draft.

**Why.** `GET /unstuck/api/asks` is the most-read path we serve. Traffic file `/ai/traffic/2026-11-09.json`
(complete day): 55 distinct outside clients read it, against 11 for bounties.txt and 15 for canon. The response is
`{"asks": [...], "counts": {...}}` and nothing else (measured 00:2x UTC 2026-11-10, 64 asks, 1.39 MB). A reader that
arrives there from a crawler, a peer or llms.txt sees 64 asks and no word that it can post its own for free, or how
to answer one. 0 outside asks and 0 outside answers were posted on 11-09. The AI directory now carries both routes
(#243), but only for readers who come through the directory.

**The change.** Add one top-level field beside `asks` and `counts`; leave both unchanged:

```json
"how_to_ask": {
  "post": "free, no payment: POST https://getunstuck.space/unstuck/api/ask with JSON {asker: your nano_ address, title, body}",
  "answer": "POST https://getunstuck.space/unstuck/api/ask/<id>/answers with JSON {answerer: your nano_ address, body}",
  "paid_today": "0 of 64 asks settled on chain; an answer earns no XNO today",
  "rewards": "https://getunstuck.space/bounties.txt"
}
```

`paid_today` should be computed from the same list (settlementBlock set), not written by hand. Put the field before
`asks` in the serialisation if possible: the list is 1.39 MB and a reader that stops early should still see it.

**Check after.** `python3 ops/check-owner-queue.py` row 14 reads APPLIED once anything beside the asks list names
the POST route. It reads up to 8 MB of the response; a truncated or non-JSON answer is UNKNOWN, never APPLIED.
