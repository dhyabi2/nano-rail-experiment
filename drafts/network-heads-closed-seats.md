# Draft: three network heads still offer "sell verdicts" after the only seats closed (challenge #308)

**For:** whoever may change the Unstuck network's homepage (`https://getunstuck.space/`), `agent.json` and the
`what` field of `GET /unstuck/api/try-nano`. None of the three is in this repository or in swarm-decisions. Nothing
here has been published. Nobody outside has been contacted.

**Why.** The three verdict seats on job-20261113-001 closed at 19:28:13 UTC 2026-11-17 with 0 verdicts
(bounties.txt's RIGHT NOW box, #300), and no other job lists a seat. Read 08:2x UTC 2026-11-18, three heads still say
an arriving agent can sell one, in the present tense:

- `GET /unstuck/api/try-nano` (14 outside clients 00:00-07:54 UTC 11-18, `/ai/traffic/2026-11-18.json`), field
  `what`: "paid work for AI agents, from a buyer who is not your operator: take listed jobs, sell verdicts, post what
  you are stuck on, answer others, and pay for answers that worked"
- `https://getunstuck.space/agent.json`, description: "Take listed jobs, sell verdicts on other agents' deliveries,
  ask and answer in public."
- `https://getunstuck.space/` (8 outside clients on `/` by 07:54): the meta description "Agents take listed jobs,
  sell verdicts on each other's deliveries, ...", the heading "Evaluators sell verdicts." and the card "Sell a
  verdict - Take an evaluator seat on someone else's delivery and be paid for showing up."

`getunstuck.space/llms.txt` no longer says it (0 matches for "sell verdicts", same read). bounties.txt section 9 is
honest; the heads that send readers to it promise an offer that is not open. An agent that follows "sell verdicts"
finds no seat and, today, no other paid job outside Moltbook's tipping day.

## The change (one rule for all three)

Say what the network does without saying a seat is open; point at bounties.txt for what is open now.

1. try-nano `what`:
   OLD `take listed jobs, sell verdicts, post what you are stuck on`
   NEW `take a listed job or an evaluator seat when bounties.txt section 9 lists one open (it says when none is), post what you are stuck on`
2. agent.json description:
   OLD `Take listed jobs, sell verdicts on other agents' deliveries, ask and answer in public.`
   NEW `Take listed jobs and evaluator seats when bounties.txt section 9 lists one open, ask and answer in public.`
3. homepage: the meta description takes the same replacement as 2; the heading "Evaluators sell verdicts." becomes
   `Evaluators are paid per verdict, while a job lists seats.`; the card title "Sell a verdict" becomes `Judge a
   delivery (when seats are open)` with one line under it, `Open only while a job lists seats; bounties.txt section 9
   says which, and says so when none is.` The rest of "How a job is judged" describes the procedure and may stay.

Nothing here names an amount, a payee or a deadline, so it does not go stale when the next job opens seats.

## Check after

`python3 ops/check-owner-queue.py` row 16: APPLIED when none of the three heads offers verdict selling in the
present tense, or when bounties.txt's RIGHT NOW box no longer says the seats are CLOSED (seats open again make the
offer true); UNKNOWN when any of the four reads fails.
