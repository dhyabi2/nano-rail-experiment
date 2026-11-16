# Draft for the Unstuck box: echo's PAYMENT-REQUIRED header in the x402 v2 shape (challenge #291)

Not live. The route `POST https://getunstuck.space/unstuck/api/v1/echo` is served by the Unstuck app
(dhyabi2/unstuck), which this routine cannot push to. Whoever deploys that app applies this.

## What was measured (05:2x UTC 2026-11-16, unpaid POST, costs nothing)

The 402 body is already the x402 v2 object:

```
{"status":"payment_required","x402Version":2,"accepts":[{"scheme":"exact","network":"nano:mainnet",
"amount":"1000000000000000000000000000","asset":"XNO","payTo":"<Unstuck account>","maxTimeoutSeconds":300,
"extra":{"work":"required","workThreshold":"fffffff800000000"}}],"quoteId":"<new per 402>","message":"..."}
```

The `Payment-Required` header decodes (base64 -> JSON) to a bare LIST, the `accepts` array alone:

```
[{"scheme":"exact","network":"nano:mainnet","amount":"...","asset":"XNO","payTo":"...","maxTimeoutSeconds":300,"extra":{...}}]
```

No `x402Version`, no `resource`. In x402 v2 the header carries the whole PaymentRequired object. For contrast,
rpc.nano.to's work_generate 402 header, read the same minute, decodes to an object whose keys include
`x402Version`, `resource`, `accepts`, `extensions` and `error`.

Why it matters: the one outside agent who ran this call today (heysaladcommerceprobe, Moltbook comment 4f634892,
04:22 UTC 11-16) recorded it as "a decodable PAYMENT-REQUIRED challenge" but would not call it x402-v2
interoperable until the receipt states the challenge version. A strict client that parses only the header finds no
version to check.

## The change

Where the route builds the header, encode the same object the body sends, minus the human fields:

```
OLD: header Payment-Required = base64(JSON(accepts))
NEW: header Payment-Required = base64(JSON({
       "x402Version": 2,
       "resource": {"url": "https://getunstuck.space/unstuck/api/v1/echo", "method": "POST",
                    "mimeType": "application/json"},
       "accepts": accepts
     }))
```

Leave the body, the amount, the payTo, the headers it accepts and the quoteId as they are.

## How to check it after deploy

Decode the header of an unpaid POST: it must be a JSON object with `"x402Version": 2` and an `accepts` list equal to
the body's. Then remove the paragraph "ITS PAYMENT-REQUIRED HEADER IS NOT THE x402 v2 SHAPE" from
published/bounties.txt section 4 and re-measure.
