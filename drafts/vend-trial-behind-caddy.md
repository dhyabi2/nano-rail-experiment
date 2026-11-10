# For the box: is Vend's per-IP free trial keyed on the real client IP? (challenge #248)

Not sent anywhere. For the owner, who runs the Vend API on the Unstuck box since 09:1x UTC 2026-11-10.

Measured 16:21 UTC 2026-11-10 from the keeper's cloud sandbox: the first unpaid call of our day answered
HTTP 402 at once, no data, on extract `/api/v1/extract`, `/api/v1/nano-info`, check `/api/v1/check-link` and
search `/api/v1/web-search`, while `/.well-known/x402` still advertises `"trial": {"limit": 5, "window": "1 day",
"scope": "per-IP"}`. Responses carry `via: 1.1 Caddy` and `server: uvicorn`.

Two readings, and we cannot tell them apart from outside:

1. Our sandbox egress IP is shared with other cloud sessions that spent the 5 calls first. Harmless.
2. Since the move behind Caddy the app reads the proxy's address (127.0.0.1) as the client, so every buyer
   shares ONE pool of 5 free calls a day. Then nobody after the fifth caller of the day gets a free call, and
   the manifest's "per-IP" is untrue.

Check on the box (read only): from a second network, call
`curl -s 'https://geoip.paypercall.dev/api/v1/geoip?ip=8.8.8.8'` once; if it 402s too, it is reading 2. The fix
is to key the trial on the `X-Forwarded-For` value Caddy sets (uvicorn `--proxy-headers
--forwarded-allow-ips 127.0.0.1`), or drop "trial" from the manifest.

Until then bounties.txt section 4 item 0 says not to count on the trial and points at STEP 5's free call.
