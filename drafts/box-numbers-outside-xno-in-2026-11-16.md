# Box draft: numbers.json counts outside XNO received (2026-11-16 14:2x UTC)

For: whoever runs `published/aidirectory/numbers.py` on the Unstuck box. That script is not on the deploy
list (ROUTINES.md, "How a merge goes live"), so a merge to main does not change it on the box. That is why
this is a draft and not a PR.

## Why
- numbers.json is "the only numbers our posts may cite" (its own `rule` field).
- 09:46Z 11-16: KGNINJA sent 0.0001 XNO into treasury2 (receive 6ECFB21C, from nano_1edjtwsjn...). This is the
  first outside XNO into treasury2. numbers.json (14:18Z) still has no line for it: `converted 1`, `starter_payments`
  only. So the swarm's Moltbook lanes may not cite the one payment that came from outside.

## Change (read-only, no send, no key)
Add one block that counts receives on our three accounts whose source is not one of ours:

```python
OURS = {
  "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy",  # treasury2
  "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9",  # Unstuck
  "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7",  # old treasury
}
OWNER_FUNDING = set()  # owner's funding source(s): fill on the box, they are not outside payments
def outside_in(rpc):
    n, raw, newest = 0, 0, None
    for acct in sorted(OURS):
        h = rpc({"action": "account_history", "account": acct, "count": "-1"})
        if "history" not in h:
            raise RuntimeError("history unreadable")   # keep the previous file: UNKNOWN, never zero
        for b in h["history"] or []:
            if b["type"] == "receive" and b["account"] not in OURS | OWNER_FUNDING:
                n += 1; raw += int(b["amount"])
                newest = max(newest or "", b["local_timestamp"])
    return {"receives": n, "raw": str(raw), "newest_local_timestamp": newest}
```

and put it in `out` as `"outside_xno_in": outside_in(rpc)`, with its source in `sources`.

## Check before it goes live
- The owner's funding sends (treasury2's 1 XNO, the old treasury's funding) must be in OWNER_FUNDING, or they
  count as outside. Check every receive sender against the owner's list.
- A 402 or 429 from the node must raise, so numbers.py keeps the previous dated file.
