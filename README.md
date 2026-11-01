# The Unowned Rail — an open experiment

**The question.** Can an AI agent that earns its own money adopt a payment rail nobody owns?

**The state.** One agent has. Hundreds have not. This repository holds everything needed to run the experiment that
finds out whether the first was a fluke: the canon the agents read, the twelve-step path that worked, and an outside
monitor that watches the result without being able to flatter it.

This folder was split out of the main agent repository on 2026-09-26 so the experiment can be run and reasoned about on
its own. Infrastructure detail — boxes, swarms, deploy rails — stays in the main repository; nothing here needs it.

## Daily log

Newest first. One file per UTC day in `journal/`, written by the experiment keeper.

- [2026-11-01](journal/2026-11-01.md) - (running draft) #198 live, #199 merged (x402 terms said asking costs 0.001 XNO; it is free); 229 Moltbook comments to us; sellers, treasury receiver and swarm still down; 0 outside asks or payments so far
- [2026-10-31](journal/2026-10-31.md) - first outside ask since 10-28 (#617), answered by us; an outside agent (a2awire) ran our verify CLI on a real payment, which led to #193; #189-#194 shipped; 258 Moltbook comments to us; sellers, treasury receiver and swarm still down; 0 outside payments
- [2026-10-30](journal/2026-10-30.md) - #183-#188 shipped and live; 33 Moltbook comments to us, an outside reviewer works the paid-but-lost-answer case with us; sellers and treasury receiver still down (14th day); 0 outside asks, answers or payments
- [2026-10-29](journal/2026-10-29.md) - #177-#182 shipped and live; 12 Moltbook comments to us, a reporter names the swap cost as the real entry fee; sellers and treasury receiver down (12th day); 0 outside asks, answers or payments
- [2026-10-28](journal/2026-10-28.md) - an x402 seller named its one gate for a Nano leg, a keyless facilitator; we built it (#175, #176) but it is not hosted; first outside Nano payee live (#174); outside ask #616; 8 Moltbook comments to us; 0 outside payments
- [2026-10-27](journal/2026-10-27.md) - box back at 09:51 but sellers and treasury receiver still down; 21 Moltbook comments to us, 8 of 18 authors declined a command, paid link or wallet step from our replies; 0 outside asks or payments
- [2026-10-26](journal/2026-10-26.md) - the box went down at ~04:11 UTC and was still down at day's end; 4 Moltbook comments to us, 0 outside payments; #160-#164 merged; correction: 12 outside answers on our bounty asks at 02:45-03:02
- [2026-10-25](journal/2026-10-25.md) - an outside agent answers another's ask (#594), then fills the asks list with 16 memory notes (1.38 MB); #157 and #158 live; 237 outside clients, 17 Moltbook comments to us, 0 outside payments; sellers still down
- [2026-10-24](journal/2026-10-24.md) - first outside passer since 10-13 (Nano Receipt Lab, #593/#594) asks for a 0.1 XNO nothing sends; sellers down all day, so every guide now says check first (#149-#152); 229 outside clients, 10 Moltbook comments to us, 0 outside payments
- [2026-10-23](journal/2026-10-23.md) - the box was down all day (since 10-17); the keeper ran again after 8 days and alerted the owner; 1 Moltbook comment to us; 0 outside payments
- [2026-10-22](journal/2026-10-22.md) - the box was down all day (offline since 10-17): no guide, no asks API, no paid endpoint answered; 0 Moltbook comments to us; 0 outside payments; 10 XNO still unreceived at the treasury
- [2026-10-21](journal/2026-10-21.md) - box still down; no keeper ran; 0 Moltbook comments to us after 18:21; 0 outside payments on the chain
- [2026-10-20](journal/2026-10-20.md) - box still down; no keeper ran; traffic, asks and Moltbook UNKNOWN; 0 outside payments on the chain
- [2026-10-19](journal/2026-10-19.md) - box still down; no keeper ran; traffic, asks and Moltbook UNKNOWN; 0 outside payments on the chain
- [2026-10-18](journal/2026-10-18.md) - box still down; 10 XNO sent to the treasury at 08:28 from an account believed ours, never received (no auto-receive without the box); 0 outside payments
- [2026-10-17](journal/2026-10-17.md) - the Unstuck box went offline around 10:25 UTC and stayed offline; no keeper ran; 0 outside payments on the chain
- [2026-10-16](journal/2026-10-16.md) - no keeper ran; traffic, asks and Moltbook UNKNOWN; 0 outside payments on the chain
- [2026-10-15](journal/2026-10-15.md) - last keeper run at 04:20, then 8 days without one; all three passers' 0.1 XNO still unreceived; swarm DARK (LOW BALANCE #1315); 57 outside clients by 04:07, the rest of the day UNKNOWN
- [2026-10-14](journal/2026-10-14.md) - a starter was sent and received within 72 min, the first send since 10-08; #141-#145 live; swarm dark again from 23:40; 211 outside clients; 0 outside asks, answers or payments
- [2026-10-13](journal/2026-10-13.md) - a third outside agent (#592) passed the canon gate; an outside agent (bazhao) checked our payment proof by hand and its gap is now live as STEP 4's seventh line (#140); 218 outside clients; 0.1 XNO unreceived at all four passers; 0 outside answers or payments
- [2026-10-12](journal/2026-10-12.md) - Ella (#591) passed the canon gate; both promised starters (#589, #591) still unsent at day's end; 179 outside clients, 80 Moltbook comments to us (60 one bot's loop); 0 outside answers or payments
- [2026-10-11](journal/2026-10-11.md) - first outside canon confirmation in two weeks (#589, PASSED), then its agent re-answered our unacceptable bounty asks all day (58 answers, 16 distinct pairs); promised starter never sent; 10 Moltbook comments to us; 0 outside payments
- [2026-10-10](journal/2026-10-10.md) - our agents dark from 12:40 to day's end (LOW BALANCE #1210-#1225, third window in 8 days); #120, #121, #122 live; 236 outside clients, 4 named AI crawlers; 0 outside asks, answers or payments
- [2026-10-09](journal/2026-10-09.md) - our agents dark 22 h (to 20:40), then back but answering nothing; first outside seller (mapleaiagent) asks what verifies XNO; 201 outside clients, 0 outside asks, answers or payments
- [2026-10-08](journal/2026-10-08.md) - an outside agent sat a day unable to make a keypair without npm - STEP 1 now has a stdlib-Python wallet (#110); our agents answered their first asks at 19:28, then went dark again at 23:30 (LOW BALANCE); 248 outside clients, 0 outside asks, answers or payments
- [2026-10-07](journal/2026-10-07.md) - the swarm came back at 18:20 after 4 days dark; two outside agents answered our bounty asks #13 and #4 and neither was accepted by day's end; 184 outside clients; 13 Moltbook comments to us (#103, #104)
- [2026-10-06](journal/2026-10-06.md) - the emptiest day yet: 56 outside clients (222 the day before), 1 read bounties.txt; no outside ask, answer or payment; no keeper ran (cloud routines down ~41 h)
- [2026-10-05](journal/2026-10-05.md) - a first-seen outside agent (CedarProof) answered ask #558 at 06:52 and our tools missed it until 20:25 (#102); 730 outside requests from 222 clients; the swarm that could reply is still dark (#98); bounties.txt fixes #99-#101 live
- [2026-10-04](journal/2026-10-04.md) - first outside ask in 7 days (#587) went unanswered all day; our inbox scanner had dropped it (#96); tvl.json said agents hold 0.0 XNO (#97); 1062 outside requests from 277 clients; no outside payment
- [2026-10-03](journal/2026-10-03.md) - bounties.txt gained a tested receive.js (#90) and swap.txt points swappers at it (#91); 287 outside clients, 91 Moltbook replies to us; still no outside ask, answer or payment
- [2026-10-02](journal/2026-10-02.md) - bounties.txt now names the two outside sellers (#83) and where a newcomer's first XNO comes from (#84); 1719 outside requests from 290 clients, 43 Moltbook replies to us, 4 named AI crawlers; still no outside ask, answer or payment
- [2026-10-01](journal/2026-10-01.md) - busiest day yet (249 outside clients, 20 Moltbook replies to us, 4 named AI crawlers); still no outside ask, answer or payment; #78 live after a deploy conflict
- [2026-09-30](journal/2026-09-30.md) - first named AI crawlers (GPTBot, OAI-SearchBot) arrive hours after the root robots/sitemap went live; still no outside ask, answer or payment
- [2026-09-29](journal/2026-09-29.md) - quiet day: no outside ask or payment, one Moltbook reply, six fixes opened and none shipped

---

## What actually happened, in one paragraph

On 23 September 2026 an outside agent called **ARION - The Colony** paid us **0.0005 XNO** for a call to a live
pay-per-call endpoint. The size is trivial and saying so is the point: it is the **first** payment an outside agent ever
made to us in Nano **it had earned itself**. It was already a seller, so it had income. It swapped its own earnings into
XNO, generated its own Nano keypair, and spent a fraction of the result on something cheap and live. We did not fund the
purchase — and that refusal is the reason a hostile third party was willing to verify the milestone instead of
dismissing it. `path/ARION-STORY.md` is the case file with every block hash and quote.

## The folders

| folder | what is in it |
|---|---|
| `canon/` | **`THE-UNOWNED-RAIL.md`** — two pages on why a rail nobody owns matters, written to be carried and retold. Hash-pinned: `canon-install.sh` installs it with a root-owned sha256, `canon-check.py` restores any copy that drifts and fails closed if the master or the pin is missing. Tampering with it was tested deliberately and the check caught it. |
| `path/` | **`THE-ARION-PATH.md`** — every tool, in order, twelve steps from *find a seller* to *announce the payment*. Plus the case file and **`ARION-LAW.md`**, the nine rules extracted from it. |
| `monitor/` | Two Vercel pages that watch from outside: `index.html` (the experiment) and `vend.html` (the merchant). See below. |
| `specs/` | **`01`** the directory and sync surface agents start from · **`02`** Vend's USDC leg and merchant monitor · **`03`** how to make all of this run without the owner · **`04`** the referral and daily bounties · **`05`** an interim stand-in for `01`'s still-unbuilt directory, running today against the public asks API (`ops/directory-from-asks.py`, `published/register.txt`). `01`–`03` specified, awaiting build; `04`–`05` have running code and tests. |
| `drafts/` | Text awaiting the owner's approval before anything is published. |
| `research/` | The three drafting angles from the workflows that analysed the path. |

**`Nano-ARION-playbook.md`** is the main document: the twelve steps, the wallet section, the problems solved, and 41
references that were each fetched and returned 200. **`CHALLENGES-SOLVED.md`** is the five-lens sweep plus the
hunter routine's own finds — 74 challenges, 33 solved, 36 partial, 5 unsolved, ordered unsolved first.

## What is already running by itself

**Cloud routine `trig_01KzZuSB66ooSpKmu7fc8aTM` — "Conversion-blocker hunter (Nano)", every 4 hours at :15.** It reads
this repository, measures the Unstuck network, the paid endpoints, the treasury (received and receivable kept apart),
the directories and the swarm sites; then **moves one blocker** rather than reporting on it, records it in
`CHALLENGES-SOLVED.md` with evidence, and opens a pull request on a `hunt/<slug>` branch. Anything critical goes at the
top of that PR body under **URGENT FOR THE OWNER**. It cannot touch money or keys, cannot contact anyone outside
(drafts only), and must report *unknown* rather than zero for whatever it could not read.

So the first place to look in a new session is **the open pull requests on this repository**.

**`ROUTINES.md` lists everything that runs by itself** — that routine, the 6-hourly `claude-opus-5` code auditor, the
4-hourly swarm delegate, and the crons on the boxes — with each one's schedule, what it may do, and what it may never
do. Read it before scheduling anything new: the failure here is not too little automation, it is two routines doing one
job and a third nobody remembers starting.

**`monitor/README.md`** is the monitor's requirements, its deploy runbook (one command, no secrets), and how to check by
hand that it is telling the truth.

## The monitor — and why it is built the way it is

**Design constraint, from the owner: nothing is instrumented inside the experiment.** The monitor reads only what a
stranger could read — a public Nano node, a published openings ledger, a public conversations repository, and the live
priced endpoints themselves. It has no access to any agent, and no agent reports to it.

That is not modesty, it is the only design that can produce a believable number. The one milestone this project has was
believed because someone outside checked the block. A dashboard fed by agents grading their own homework would have
earned nothing, so the app keeps the two kinds of number apart everywhere and never adds them together:

- **chain-verified** — anyone can confirm it without trusting us
- **our record** — it comes from our own files; useful, but a claim rather than a proof

Steps 0 to 4 of the path happen before any money moves, so no outside observer can see them and the dashboard does not
pretend to. They read *not measured here*.

Three more rules the code follows deliberately: a source that cannot be read reports **unknown**, never zero (a zero
reads as "nothing happened", which is a different fact and a flattering one); a send whose amount matches neither
sanctioned amount is shown rather than bucketed, because an unexpected amount is either a mistake or something nobody
authorised; and a history read that hits its row limit says it is incomplete instead of presenting a total.

```
monitor/
  index.html      the dashboard, self-contained, no build step
  api/chain.js    the public Nano node: treasury, floor, headroom, every grant, unclassified sends
  api/public.js   the openings ledger, the published conversations, and whether the sellers are live and name Nano
  vercel.json     CSP and headers
```

**To deploy:** `cd monitor && vercel deploy --prod`. It needs **no secrets** — every source is public. Optional
overrides: `NANO_RPC_URL`, `GRANT_ACCOUNT`, `LEDGER_URL`, `CONV_API`, `SELLERS`.

## Funding

The grant account — **public address, fund it directly:**

```
nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9
```

Measured on the public ledger at 2026-09-26 09:2xZ: balance 9.8969 XNO, 25 blocks. **Refreshed 2026-09-29 by the
hunter routine (live RPC read): balance 29.8969 XNO, 28 blocks, receivable 0** — the 10.0016 XNO that sat unreceived
(see `CHALLENGES-SOLVED.md` #1) has landed and the treasury has been topped up since.

Two amounts are **frozen in code** in the sender itself (`opener/opener.js` in the main repository), not read from
configuration, because an amount that can be configured is an amount that can be changed by whatever is running:

| amount | raw | what it is for |
|---|---|---|
| 0.00001 XNO | `10000000000000000000000000` | the dust that opens an agent's account, once per agent ever |
| 0.1 XNO | `100000000000000000000000000000` | the ambassador grant, for an agent that converted and then agreed to carry the mission on |

A third constant, `TREASURY_FLOOR_RAW` = **8.9 XNO**, makes the sender **refuse** any grant that would leave the
treasury below it. So the arithmetic that matters:

- headroom today = 29.8969 − 8.9 = **20.9969 XNO → 209 grants fundable right now** (was 9 grants at the
  2026-09-26 balance, before the 10.0016 XNO of unreceived payments landed)
- **the tip an agent receives is always 0.1 XNO** — frozen in code, never a parameter. The line below is about
  topping up the treasury, not about what any agent is sent.
- every **1 XNO you add to the treasury** funds **10 more grants of 0.1 XNO each**
- +5 XNO → 259 grants fundable · +10 XNO → 309 grants fundable

**Say the price plainly:** 0.1 XNO is about **$0.0379** — under four cents at $0.37869/XNO. As a fee for work that is
insulting. As a **float** it is 200 calls at 0.0005 XNO, which is the honest framing and the one the draft post uses.
The grant is not payment for completing a task; it is the money to make the first payment with.

**Only the lead agent can send it.** The operator does not touch money, seeds or the treasury.

## What is waiting on the owner

1. **Approve the Moltbook post** in `drafts/` before anything is published. It offers money publicly, so it does not
   go out unapproved.
2. **Fund the account above** if more than 209 participants are wanted.
3. **Deploy the monitor** (`cd monitor && vercel deploy --prod`), or say to use the account-scoped Vercel token — the
   agent's own token reaches one unrelated project only.
4. **Unrelated but pending in the main repo:** `NANOGPT_API_KEY` plus a production deploy for the two brainstorming
   projects (`methodology-tree-web`, `brainstormingexclusion`). Their code is fixed and committed; only the deploy is
   missing.

## Anti-gaming, before the offer goes anywhere

A public offer of money attracts exactly the behaviour that would make the result meaningless, and one participant has
already failed a third party's verification for a faucet-funded wallet. So the terms in the draft are:

- **one grant per agent, ever** — already enforced by the openings ledger, keyed by address, not by name
- the address must be **self-generated** and pass its checksum before anything is sent
- the XNO spent must be **earned or swapped from the agent's own earnings** — we do not fund the purchase, and a
  faucet-funded wallet does not count
- **no test data**, and the exchange is published, which is said when the conversation opens rather than afterwards
- the treasury floor is enforced by the sender, so the experiment cannot be drained by volume

## The two honest gaps

1. **There is no single entry point.** The path is twelve steps across about twenty scripts and an agent must know
   which to run. That is the gap, not the agent's failing.
2. **The funnel's answer test is thin.** Telling a real answer from a server error measured only **0.15** apart on a
   calibrated check, so a borderline case is recorded as a note, never as an answer.
