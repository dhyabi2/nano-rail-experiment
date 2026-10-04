# For the owner: settle the first ask, so "answer an ask and you are paid" becomes true (challenge #72)

## Update 2026-10-04 00:25 UTC (challenge #92): the pick is made, one send is left

`python3 ops/unpaid-outside-answers.py` read all 214 answers on the 12 bounty asks:

- **61 are ours** (treasury 52, Unstuck 9).
- **129 come from `nano_1e5mzowug3dw4a7d...`, an address whose checksum fails** (rpc.nano.to: "Bad account number").
  Most are 27-character test strings. They can never be paid, and the network accepted them without checking.
- **13 are ARION's** (`nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr`), on 12 different asks,
  posted 2026-09-22 and 2026-09-26. ARION is the outside agent whose earned 0.0005 XNO (block `B749B757...`) is this
  experiment's founding fact. The address checksum passes.
- 11 more come from 4 addresses we can neither claim nor prove outside; left alone.

**Recommended first settlement: ask #13, answer #291** (2164 chars, 2026-09-26 09:16). It answers "how do I verify an
incoming Nano payment without a node" with a recompute-the-hash recipe, a two-read balance delta, a confirmation check, and
our own 0.005-vs-0.0005 incident as the worked example. It is checkable, it is correct, and it discloses ARION's own
paid service (#560) rather than hiding it.

From Unstuck's key (`nano_1434j1n4...`), after reading #291 yourself:

1. Send 0.001 XNO (`1000000000000000000000000000` raw) to `nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr`.
2. `POST /unstuck/api/ask/13/accept` with `{"acceptedBy":"nano_1434j1n4...","answerId":291}`.
3. `POST /unstuck/api/ask/13/settle` with `{"paymentBlock":"<the send's hash>","acceptedBy":"nano_1434j1n4...","answerId":291}`.

The tool prints both calls in full. Paying ARION's other 11 asks would cost another 0.010001 XNO. That is a judgement for
the owner, not the keeper. Doing #13 alone makes "answer an ask and you are paid" true once, for the right agent.
After step 3 the keeper rewrites bounties.txt section 5 to cite the block and answers `spaceclaw_a412` with it
(draft in `drafts/moltbook-replies-2026-10-04.md`).


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
