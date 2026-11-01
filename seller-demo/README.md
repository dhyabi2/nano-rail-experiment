# seller-demo: a Nano (XNO) pay-per-call seller with no always-on box

One Vercel Python function, `GET /api/paid`, standard library only. It holds **no seed or key, signs nothing, sends
nothing**: it only reads a public Nano node. Price: 0.00001 XNO (10^25 raw) per call. Result: an offline Nano
address check (`?account=nano_...`) plus a receipt.

**See the 402** (replace the host with your deployment):

```
curl -si https://YOUR-DEPLOYMENT.vercel.app/api/paid
```

It answers HTTP 402 with `accepts[0]` = `{"scheme":"exact","network":"nano:mainnet","asset":"XNO","amount":"10000000000000000000000000","payTo":"<SELLER_NANO_ACCOUNT>","maxTimeoutSeconds":120}` (also base64 in the `payment-required` header).

**Pay and verify**: send exactly (or more than) `amount` raw to `payTo` from your own wallet, then:

```
curl -s https://YOUR-DEPLOYMENT.vercel.app/api/paid?account=nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7 -H "X-PAYMENT: <64-hex send block hash>"
```

Independent check with no seller involved (stdlib verifier, `dhyabi2/nano-settlement-verify`):
`python3 verify_cli.py <hash> 10000000000000000000000000 <payTo>`.

## What is checked (against a public node, `block_info`)
confirmed `send`; `link_as_account` equals the seller account; amount >= price; node timestamp within 120 s; hash not
already accepted by this instance. Wrong amount / wrong payee / unknown block / too old / replay / missing or garbage
proof: HTTP 402 with a `reason`. Unconfirmed block or unreachable nodes: HTTP **503 + Retry-After** (pending is not
invalid: a buyer who paid must not be told to pay again); the hash is not burned, retry the same one.

## Honest limit: replay protection
Serverless has no disk and instances share no memory. "Used before" is therefore remembered **per warm instance**,
and bounded by a chain-derived freshness window (the node's own timestamp must be within 120 s, so a proof expires
by itself). A replay that reaches a *different or cold* instance inside the window is **not** caught: worst case a few
repeat calls of a 0.00001 XNO result per payment, for two minutes. Hard once-only needs a shared store (Vercel KV);
not included. The block also pays *anyone* who sees the hash: it is a bearer proof for the window, not bound to a caller.

## Deploy
Env var `SELLER_NANO_ACCOUNT` = your own `nano_` receiving address (a missing or invalid one makes the function answer
500, never guess). Optional `NANO_RPC_NODES` = comma-separated node URLs (default `https://rpc.nano.to`).
Then from this folder: `vercel deploy --prod`. The account must receive the funds itself with its own wallet; this code never does.

## Test
`python3 -m unittest discover -s seller-demo/tests -v` (no network; node is stubbed).
