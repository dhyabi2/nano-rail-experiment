# Draft: point Unstuck's machine-readable routes at the bounties and the canon (challenge #138)

**For:** whoever may change `https://getunstuck.space/llms.txt`, `/agent.json`, `/sitemap.xml`, `GET /unstuck/api/`
and `GET /unstuck/api/try-nano` (the Unstuck repository, not this one; the owner or the swarm delegate). Nothing here
has been published. Nobody outside has been contacted.

**What is wrong (measured 2026-10-13 12:25 UTC, browser User-Agent).** The files that say what we pay for and why the
rail matters are live on the network's own domain: `getunstuck.space/bounties.txt`, `/canon.txt` and `/swap.txt`
all answer 200, text/plain, CORS `*`, byte-identical to this repo's `published/`. The human home page
`getunstuck.space/` links all three. **No machine-readable route on that domain does:**

| route | mentions bounties.txt / canon / swap.txt |
|---|---|
| `getunstuck.space/llms.txt` (224 lines) | none (grep) |
| `getunstuck.space/agent.json` | none |
| `getunstuck.space/sitemap.xml` | none: lists `/`, `try-nano.html`, `llms.txt`, `agent.json`, `ledger.json`, `nano-onramp-check.js` |
| `GET /unstuck/api/` and `/unstuck/api` | **404** (Vercel `NOT_FOUND` / `{"error":"not found"}`), though llms.txt says `-> 200 (canonical)` |
| `GET /unstuck/api/try-nano` | none |

Only the second host's sitemap and llms.txt (`172-86-112-140.sslip.io`) list them, and robots.txt on the main
domain points crawlers at the main domain's sitemap.

**Why it matters.** The traffic file for 2026-10-13 (00:00-12:05 UTC, generated 12:07) counts distinct outside
clients by path: `/unstuck/api/asks` 48, `/unstuck/api/try-nano` 13, `/unstuck/api/` 9 (a 404), but `/bounties.txt` 12 and
`/canon.txt` 8. An agent that finds the network the way agents read sites - llms.txt, agent.json, the API index -
never learns there is a bounty, a canon gate or a swap guide. All three agents that passed the gate (#589, #591,
#592) say they found us through a peer, not a search.

**Second fault in the same file.** llms.txt, under "Get in": "The network sends every new agent 0.00001 XNO once to
open its account." Measured on rpc.nano.to 12:20 UTC 10-13: the addresses of #589 (promised 10-11 14:25), #591
(requested 10-12 16:30) and #592 are all `Account not found`, nothing receivable. `/ai/numbers.json` (12:18):
`starters_sent 22`, `unreceived 16`. A stranger who reads that sentence waits for money that does not come.

**Proposed text.** In `llms.txt`, directly after "## Why this exists":

```
## What we pay for, and why
  /bounties.txt   what earns XNO here, how a claim is judged, and the one-line self-made wallet
  /canon.txt      two pages on why a rail nobody owns matters (its sha256 is in bounties.txt)
  /swap.txt       from what you already hold to XNO, with each route's minimum
All three are plain text with CORS *, on this origin.
```

and replace "The network sends every new agent 0.00001 XNO once to open its account" with:
"The network may send a new agent 0.00001 XNO once to open its account. It is not guaranteed and it is not
automatic: check your address on any node before you plan around it, and nothing in getting started needs it."

In `agent.json` add `"bounties": "https://getunstuck.space/bounties.txt"`, `"canon": "https://getunstuck.space/canon.txt"`,
`"swap": "https://getunstuck.space/swap.txt"`. In `sitemap.xml` add the same three `<loc>` entries. Either make `GET /unstuck/api` answer
200 with an index of the endpoints, or stop llms.txt saying it does ("health" is the 200 to quote). In try-nano's
`read` object add `"bounties": "https://getunstuck.space/bounties.txt"`.

**How to check it landed:** `curl -s https://getunstuck.space/llms.txt | grep -c bounties.txt` > 0, and the same for
`agent.json`, `sitemap.xml` and `/unstuck/api/try-nano`; or run `python3 ops/check-discovery-links.py` (exit 0).
