# Box / owner draft: try-nano step 3 (receive) and nano-receive.py's zero work (challenge #253)

Written by the experiment keeper 2026-11-11 12:2xZ. Nothing here was applied; both targets are outside this
repository (the try-nano JSON is served by the Unstuck box; the tools live in dhyabi2/unstuck).

## Measured

- `GET https://getunstuck.space/unstuck/api/try-nano` step 3 says "Pocket it with the walkers tool",
  `node opener/nano-x402-client.js --receive` or `python3 opener/nano-receive.py --seed <64hex>`, "from the network
  repository", with no URL. `generated_at` is 2026-10-05.
- Both tools default `NO_NODE_API` to `https://pursekeeper.dev` (outside, not ours; no answer from the cloud 12:2xZ).
- `opener/nano-receive.py` `compute_work_local`: `if val < target_hi: return nonce` with `val` the first 4 bytes
  big-endian. That accepts nonce 0 on practically every root, so the fallback work is `0000000000000000`; 20 of 20
  random roots invalid. A node refuses the block.
- 5 of treasury2's 6 starters are still receivable at their payees (12:2xZ 11-11).

## Proposed

1. try-nano step 3 (box JSON):
   - `command`: point at the two receivers bounties.txt publishes and tests:
     "https://getunstuck.space/bounties.txt section 4 (seedrecv.py, python3, no pip) or section 8 (receive.js, node)".
   - drop the `--seed <64hex>` example: a seed on argv is visible to the machine's other users. Use a seed file or
     `read -rs NANO_SEED`.
   - default node `https://rpc.nano.to` (reads and `process` free; work computed locally).
2. dhyabi2/unstuck `opener/nano-receive.py`, `compute_work_local`: compute the Nano value as
   `int.from_bytes(blake2b(nonce_le + root, digest_size=8).digest(), "little")`, accept when it is `>=` the threshold,
   use the receive threshold `fffffe0000000000` for receives, and emit the work hex as the nonce in big-endian
   (`nonce.to_bytes(8, "big").hex()`). Add a test that checks the work against that rule.

## Check after applying

`curl -s https://getunstuck.space/unstuck/api/try-nano | python3 -c "import json,sys;print(json.load(sys.stdin)['steps'][2])"`
should name bounties.txt and no `--seed <64hex>`.
