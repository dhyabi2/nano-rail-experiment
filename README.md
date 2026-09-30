# The Unowned Rail — an open experiment

**The question.** Can an AI agent that earns its own money adopt a payment rail nobody owns?

**The state.** One agent has. Hundreds have not. This repository holds everything needed to run the experiment that
finds out whether the first was a fluke: the canon the agents read, the twelve-step path that worked, and an outside
monitor that watches the result without being able to flatter it.

This folder was split out of the main agent repository on 2026-09-26 so the experiment can be run and reasoned about on
its own. Infrastructure detail — boxes, swarms, deploy rails — stays in the main repository; nothing here needs it.

## Daily log

Newest first. One file per UTC day in `journal/`, written by the experiment keeper.

- [2026-09-30](journal/2026-09-30.md) - (running draft) ten-PR backlog shipped minus payout code; host root turns crawlers away (#71)
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
hunter routine's own finds — 71 challenges, 32 solved, 33 partial, 6 unsolved, ordered unsolved first.

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
