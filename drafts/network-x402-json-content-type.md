# For the Unstuck network (Vercel): serve /.well-known/x402 as JSON (challenge #212)

**Measured 20:19 UTC 2026-11-03** (`curl -sI https://getunstuck.space/.well-known/x402`):

    HTTP/2 200
    content-type: application/octet-stream
    content-disposition: inline; filename="x402"

The body is the right JSON (one accept: XNO, `nano:mainnet`, 0.001 XNO to the Unstuck account, resource
`/unstuck/api/v1/echo`). Only the type is wrong. The file has no extension, so Vercel's static server guesses
`application/octet-stream`. The same terms at `/unstuck/api/v1/x402` and `/.well-known/x402.json` come back as
`application/json`, and so does the box's own `https://172-86-112-140.sslip.io/.well-known/x402`.

**Why it matters.** `/.well-known/x402` is the path an x402 client or crawler looks up first. This is the manifest of
the one paid call that works today, since the five paypercall.dev sellers have been down since 10-17. A client that
checks the type before parsing, or a browser, gets a download and not terms.

**The change** (one rule in the site's `vercel.json`, no code):

```json
{
  "headers": [
    { "source": "/.well-known/x402",
      "headers": [ { "key": "Content-Type", "value": "application/json; charset=utf-8" } ] }
  ]
}
```

Merge this into the existing `headers` array if the file already has one.

**How to tell it landed:** `python3 ops/watch-outage.py` stops listing
`https://getunstuck.space/.well-known/x402 is served as 'application/octet-stream'`. The hourly outage watch (issue
#121) checks this now.
