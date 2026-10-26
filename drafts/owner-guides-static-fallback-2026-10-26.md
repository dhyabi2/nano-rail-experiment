# For the owner: serve the four guides from Vercel's static tier, so a dead box stops turning every reader away

*Drafted by the experiment keeper, 2026-10-26 16:3x UTC (challenge #163). Not sent anywhere. Every number below was
measured in this run or is cited from a journal.*

## What a stranger meets right now (measured 16:2x UTC 10-26)

getunstuck.space is a Vercel project. Part of it is static files that Vercel serves itself; the rest is a rewrite
to the box (172.86.112.140). Today the box is down (since about 04:11 UTC, `swarm-decisions/NEEDS-OWNER.md` row
2026-10-26), and the split is:

| URL | answers | served by |
|---|---|---|
| `/` (home page) | 200 text/html | Vercel static |
| `/llms.txt`, `/robots.txt`, `/sitemap.xml`, `/agent.json`, `/ledger.json`, `/try-nano.html`, `/nano-onramp-check.js`, `/.well-known/x402` | 200 | Vercel static |
| `/canon`, `/canon.txt`, `/canon.md`, `/bounties.txt`, `/swap.txt` | nothing (timeout) or 502 `ROUTER_EXTERNAL_TARGET_CONNECTION_ERROR` | rewrite to the box |

The static home page links to exactly the dead half: "Read THE CANON" (`/canon`), "plain text" (`/canon.txt`),
"Both rewards, every rule and URL" (`/bounties.txt`), "USDC -> XNO instructions" (`/swap.txt`), and the gate's own
"I have read THE CANON" (`/canon`). So a reader who arrives while the box is down reads the pitch and then hits an
error on every next step.

## What it has cost

- 10-17 ~10:25 to 10-24 ~04:00: six and a half days of 502 on all four guides (challenge #147).
- 10-26 since 01:42-04:16: about 12 hours so far, and counting.
- On an ordinary day before this outage, 237 distinct outside clients came (journal 10-25). None of the guides
  depends on the box: all four are plain files from this repository's `published/` (bounties.txt 78,386 bytes,
  canon.txt 1,859, swap.txt 10,971, canon.html 21,182 on main today).

## The change (in the Unstuck repository, which this keeper cannot reach)

1. Put four files into the Vercel project's static output, next to `llms.txt`, copied from
   `dhyabi2/nano-rail-experiment` main:
   - `published/bounties.txt` -> `bounties.txt`
   - `published/canon.txt` -> `canon.txt`
   - `published/swap.txt` -> `swap.txt`
   - `published/canon.html` -> `canon.html` (served as `/canon` if `cleanUrls` is on, or add a rewrite `/canon -> /canon.html`)
   - and `canon/THE-UNOWNED-RAIL.md` -> `canon.md` (the hash-pinned canon; copy it byte for byte, never edit it)
2. Vercel serves a file from the static output before it applies a rewrite, so these paths stop going to the box at
   all. Remove the box rewrites for these five paths if they are explicit.
3. Keep the headers the box sends today: `Content-Type: text/plain; charset=utf-8` on the three .txt files and
   `text/markdown; charset=utf-8` on canon.md, and `Access-Control-Allow-Origin: *` on all four text files (the
   keeper checks CORS on the .txt guides).
4. Keep them current: whatever job deploys the Vercel project copies these files from this repository's main at
   deploy time (or a 15-minute job, like the box's experiment-deploy, triggers a Vercel deploy when main's copies
   change). `ops/check-live.py` already compares each live URL with main byte for byte, so drift shows up at the
   next keeper run.

What stays on the box, unchanged: the asks API, the paid endpoints, the traffic files. A dead box still blocks
posting an ask or paying, but a reader can at least read the offer, the canon and the gate, and come back.

## Trade-off

The box's experiment-deploy job would stop being the thing that puts these four files live; the Vercel deploy would
be. That moves the deploy (and its CONFLICT reporting in deploy-status.json) off the box. If you would rather keep
the box as the source, the smaller version is: keep the box rewrite, and only add the static copies as the fallback
the home page links to (for example `/offline/bounties.txt`), which is weaker because nobody follows a fallback link
they were not given.

## How the keeper will confirm it

- `python3 ops/check-live.py` -> bounties.txt, canon.txt, swap.txt and `/canon` LIVE while the box is still down.
- `python3 ops/watch-outage.py` -> the five guide URLs leave its fault list during the next box outage.
