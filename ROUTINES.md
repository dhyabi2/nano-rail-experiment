# What runs by itself

Every automated thing that touches this experiment or the code behind it: when it runs, what it may do, and what it may
never do. **Read this before adding another one** — the failure mode here is not too little automation, it is two
routines doing the same job and a third that nobody remembers scheduling.

Schedules are UTC. Routines are managed at https://claude.ai/code/routines — that is also the **only** place one can be
deleted; the API can disable but not remove.

---

## Cloud routines (Claude, running in Anthropic's cloud)

### 1. Conversion-blocker hunter — `trig_01KzZuSB66ooSpKmu7fc8aTM`

**`15 */4 * * *`** (every 4 hours at :15) · model `claude-sonnet-5` · source: **this repository**

The one routine dedicated to the experiment. Its job is to find what stops AI agents adopting Nano, **move one
blocker**, and record how.

- **Runs `ops/hunter-preflight.sh` first, every time.** Found 2026-09-26: this routine's own cloud session can have
  every measurement host denied by its environment's network egress policy while the services themselves are fine —
  ten `curl` calls came back `exit 56` and every `WebFetch` came back `EGRESS_BLOCKED` in the same run. That is not a
  quiet day, it is a blind one, and the two must never be reported the same way (challenge #48). If the preflight
  exits 2, the run reports the whole measurement phase as **unknown**, says the session was network-blind, and asks
  the owner to broaden this environment's Network access — it does not write "nothing new to report".
- **Measures every run:** the Unstuck network (`/unstuck/api/asks`, `/ledger.json`), the five paid endpoints'
  `/health` and `/.well-known/x402`, the treasury (received and receivable kept apart), directories and listings, and
  the swarm's forge and board.
- **Then does work, not reporting:** picks the blocker with the most conversion leverage and writes the tool, page,
  manifest fix, listing submission or spec. Commits to `hunt/<slug>` and opens a pull request.
- **Records it** in `CHALLENGES-SOLVED.md` in the existing format, with evidence that is a file, command or URL.
- **Escalates** only something genuinely critical, at the top of the PR body under `URGENT FOR THE OWNER`: treasury
  under 9.0 XNO, an endpoint that stopped accepting XNO, a manifest payee that is not the treasury, a site or API down,
  or receivable growing with nothing claimed.
- **May not:** touch money, seeds or keys; push to `main`; create or delete a repository; contact any outside agent or
  maintainer (it drafts into `drafts/` and a human or the swarm sends); claim a number it did not measure. A source it
  could not read must report **unknown**, never zero.

**So the first place to look in a new session is the open pull requests on this repository.**

### 2. Code auditor and fixer — `trig_01Rxu14f8EH94KM621LEVKpE`

**`40 */6 * * *`** (every 6 hours at :40) · model **`claude-opus-5`** · source: `dhyabi2/nano-agent`

The only layer that thinks hard, because the agents on the boxes run cheap models with no reasoning budget. It audits
and fixes **published** code only — public, non-fork, non-archived repositories under `dhyabi2` — at most three a run,
one concern per branch, with a test that fails without the fix. It may squash-merge its own fix when every test passes
and the change touches no credential, release or money path; otherwise it leaves the PR open and says what it could not
verify. A secret found in history stops everything for that repository and emails the owner instead. No machine
signature on anything it writes. Last run succeeded 06:40–06:59 on 2026-09-26.

### 3. Swarm delegate — `trig_01GN1hs3RyUsqfDndmeg2ctk`

**`25 */4 * * *`** (every 4 hours at :25) · source: `dhyabi2/nano-agent`

Acts on the owner's behalf across the three swarm forges, within the owner's fixed rules: answers requests addressed to
the owner, breaks ties, tells a lead to merge or deploy, audits the conversation and keeps the Kanban boards honest. It
holds no forge token — it appends decisions to `dhyabi2/swarm-decisions` and each box applies them with its own token,
refusing anything token-shaped, anything for another swarm, and the whole file if GitHub's events API says the newest
push was not by `dhyabi2`.

### One thing to clean up

**One-shot routines are breeding.** Of the twenty most recent, nineteen are one-shot `Re-check X` jobs, and something
re-creates a fresh one every 30–60 minutes as the last expires. Fifteen are spent and disabled; four are still armed.
**A thing that repeats is a cron, not a chain of one-shots.** Whichever routine creates them should be given a recurring
schedule, and the spent ones cleared at claude.ai/code/routines.

*Note when reading the routine list through the API: it is **paginated at 20**, so a routine's absence from the first
page proves nothing. Fetch it by id before concluding it is gone.*

---

## On the boxes (cron and systemd, not Claude)

These belong to the swarms rather than to the experiment, and are listed so nobody schedules a second one:

| what | where | when |
|---|---|---|
| the run loop | `<swarm>-loop.service` + `<swarm>-member@<name>.service`, 14 units per box | continuously, members resting ~40 min between runs |
| journal collector | cron on each box | every 5 min |
| spend guard | cron | every 5 min — samples real spend and restarts the unit if over the cap |
| money audit | root cron, no model | every 10 min — checks every live manifest's payee against a frozen treasury |
| canon check | cron | every 10 min — verifies `THE-UNOWNED-RAIL.md` against a root-owned sha256 and restores drift |
| delegate applier | cron | every 5 min — applies the delegate's decisions with the box's own token |
| board keeper | one agent per swarm | continuously |
| repo backup | cron | 03:17 daily |
| Gitee publisher | cron | 03:20 daily |
| committee meeting | cron | every 6 hours |

---

## What is still done by a human every few minutes, and should not be

A person currently sweeps all four boxes every five minutes and fixes what is safe — and almost every pass ends
"nothing needed fixing". That is the largest remaining manual cost in the whole system.
**`specs/03-RUNS-WITHOUT-YOU.md`** proposes the hourly self-healing routine that replaces it, plus five others, in order
of how much of the owner's time each returns.

## The rule for any new routine

**It must be able to say "I could not check this."** The costliest failure here has never been a missed problem; it is a
check that could not run and reported a clean result. Fail closed, report unknown rather than zero, and never mark
something solved because it has been written down.
