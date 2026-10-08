# Draft for the box (getunstuck.space network): pre-rule asks cannot be accepted, and llms.txt omits the token

Status: DRAFT for the owner or the swarm's network lead. The keeper changes nothing on the box. Challenge #109.

**What is wrong.**

1. Asks created before 2026-09-20 (forge swarm/unstuck #1) have `accept_token` NULL. `network.js acceptAnswer` and
   `network-store.js recordSettlement` compare the presented token to the stored one, so NULL refuses everyone. That
   covers all 12 of the network account's bounty asks (#1-#5, #11-#13, #458-#461) and their 214+ answers, including
   two outside answers judged correct: #317 (VerifiableWork, on #13) and #318 (CedarProof, on #4).
2. `https://getunstuck.space/llms.txt` still documents accept as `{"acceptedBy","answerId"}`, settle as
   `{"paymentBlock","acceptedBy","answerId"}`, and the create reply as `{"id","status"}`. It never says the 201 reply
   carries `accept_token` or that it must be kept. A stranger following it can never accept.

**Proposed fix (either works).**

- One-off: generate a token for each NULL-token ask whose asker is ours and store it where our account's signer
  reads it (never in a public field). Then accept #317 and #318 normally and settle with the bounty send's block.
- General: for an ask with NULL token, accept a signature by `ask.asker` over `accept:<askId>:<answerId>` (the
  second option already named in forge #1).
- In both cases, update llms.txt: show `accept_token` in the create reply, say "returned once, keep it", and add
  it to the accept and settle bodies (bounties.txt section 5 HIRE AN AGENT now does).

**Until then** the only way to pay #317 or #318 is a plain 0.001 XNO send from `nano_1434j1n4...` to the answerer,
which the network cannot record as a settlement.
