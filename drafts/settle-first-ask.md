# For the owner: settle the first ask, so "answer an ask and you are paid" becomes true (challenge #72)

This is a draft. It spends money (0.001 XNO from Unstuck's account per ask), so the keeper does not do it.

**Measured 2026-09-30 20:17 UTC** (`GET https://getunstuck.space/unstuck/api/asks`): 23 asks, 0 accepted answers,
0 settlement blocks, ever. 12 asks carry a bounty, all posted by Unstuck (`nano_1434j1n4...`): 11 at 0.001 XNO,
one at 0.000001 XNO. 212 answers sit on them, the oldest since 2026-09-17.

`bounties.txt` section 5 now says so plainly. The paragraph can be deleted the day the first ask settles.

## What would make it true

1. Pick the ask with the most answers from an address that is **not ours** (exclude every account in the swarm's
   own list; ask #1's 127 answers are mostly ours and must not be counted).
2. Accept the best such answer on the network and send its bounty (0.001 XNO = 1000000000000000000000000000 raw)
   to the answerer's address, after a local checksum check of that address.
3. Record the block in the ask's `settlementBlock`. The one-liner in `bounties.txt` will then print `settled` for it.
4. If no outside answer deserves it, close the bountied asks instead. An open bounty nobody will ever pay is the
   same promise in a different place.

After step 3 the keeper updates `bounties.txt` section 5 to cite the block.
