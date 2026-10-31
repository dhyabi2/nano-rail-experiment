# nano-x402-facilitator

A keyless x402 facilitator for Nano (XNO). It is one Python file, standard library only. It holds no key and sends
nothing. A seller points its `nano:mainnet` accepts entry at it the way it points a USDC entry at PayAI or Coinbase.
Built for challenge #175.

```
python3 facilitator.py --port 8402 --node https://rpc.nano.to --node <second node> --quorum 1 --store redeemed.json
```

| Route | Body | Answer |
|---|---|---|
| `GET /` | - | an index: every route and body, `holds_key: false`, `sends: false`, `source_sha256` |
| `GET /source` | - | this file, text/plain, `X-Source-SHA256` header (the repository is private, #176) |
| `GET /supported` | - | `{"kinds":[{"x402Version":1,"scheme":"exact","network":"nano:mainnet"}, ...v2]}` |
| `POST /verify` | `{"paymentPayload":..., "paymentRequirements":...}` | `{"isValid":bool,"invalidReason":str\|null,"payer":"nano_..."}` |
| `POST /settle` | same | `{"success":bool,"errorReason":...,"transaction":"<hash>","network":"nano:mainnet","payer":...}` |

`paymentRequirements`: `scheme` `exact`, `network` `nano:mainnet`, `payTo` a nano_ address, `amount` (v2) or
`maxAmountRequired` (v1) in raw, optional `maxTimeoutSeconds` (default 600). Both are ASCII digits only (`"²"` or `"٣"` is
`invalid_amount_required` / `invalid_max_timeout`, not a dropped connection); `"007"` is 7 raw. `paymentPayload`: the x402 payload
with `payload.hash` (or `block_hash`), its base64 header form, or the bare 64-hex block hash.

A payment is valid only if every node that answered `block_info` says it is a confirmed `send` to `payTo` of exactly
`amount` raw, first seen within `maxTimeoutSeconds`, and this facilitator has never settled that hash. `/settle`
does the same checks and then records the hash, so a hash settles once, across restarts.

What it does not do: it does not receive the funds into the seller's wallet. A Nano send is final when it is
confirmed, but the payee's wallet still has to publish a receive block to spend it. That is the seller's own wallet,
holding the seller's own key, and nothing here touches it.

Hosting on the box: `drafts/box-nano-x402-facilitator.md`. Is it up, and is it main's code: `python3 ops/check-facilitator.py <url>`.

Tests: `python3 specs/test_nano_x402_facilitator.py` (stub nodes, plus the HTTP interface on a local port).
Measured live 2026-10-28 16:2x UTC against rpc.nano.to with public block 5EE71904...: correct payee and amount is
valid with a wide window, `payment_too_old` with the default window, `wrong_amount` for a different amount.
