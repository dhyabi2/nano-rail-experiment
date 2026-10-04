# For the owner: /tvl.json publishes a failed read as zero (challenge #97)

Measured 2026-10-04 20:18 UTC. `https://172-86-112-140.sslip.io/tvl.json` was last written 04:17 UTC, while rpc.nano.to
answered 429 (challenge #94). It says `tvl_xno 0.0`, `treasury_xno_excluded 0.0`, `agents_unreadable 24` of 24 and
`"complete": false`. At 20:18 ARION's account alone held 2.709 XNO and the treasury 71.6178.

The generator is on the box, not in this repository. Two changes would fix it:

1. When `complete` is false, write `tvl_xno: null` and `treasury_xno_excluded: null`, never `0.0`.
2. Retry on the next cycle; it did not refresh for 16 hours after the node recovered (~12:17 UTC).

bounties.txt now tells readers to read `complete` first (PR for challenge #97). Nothing here touches money or keys.
