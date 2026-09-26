# Spec 03 — Making this run without you

Owner, 2026-09-26: *"recommend other subroutines so that it will require less manual work from me, and everything to be
sustainable and fixable without me, since I am busy a lot."*

**The method matters more than the list.** The way to reduce your manual work is not to add monitoring — you already
have plenty, and monitoring *creates* work by generating things to read. It is to take each thing that currently
**stops until you act** and either remove the dependency or batch it into one decision a day.

So: what actually waits on you today, measured from the watch log, and what removes it.

---

## What waits on you, and what it costs

| waits on you | why | can it be removed? |
|---|---|---|
| Funding the treasury | money | **No, and it should not be.** But it can be made never-urgent: alert at a threshold, days before the floor. |
| Approving a public post | it is your voice and your money being offered | **Batch it.** One daily digest, one reply from you, default recommendation stated. |
| Vercel deploys | the agent's token reaches one project | **Yes**, with a project-scoped token per app. One decision, then never again. |
| Receiving payments (10.0016 XNO sitting) | money path, lead only | **Yes** — a receive is not a spend. It needs a law and a cron, not your attention. |
| Reviewing 109 open PRs | volume | **Mostly** — mechanical rules already merge safe ones on Vend. |
| Rai's 58 GB disk that should be 160 GB | the host's error | **No** — a support ticket is yours. Everything else is reclaiming crumbs. |
| Caps and model choices | your rules | **No, by your own decision.** Keep it that way. |
| Me watching four boxes every five minutes | a human in a loop | **Yes, and this is the biggest one.** See A. |

---

## The routines worth adding, in order of how much of your time they return

### A. Self-healing box watch — hourly. *The big one.*

Right now a person runs a read-only sweep of four boxes every five minutes and fixes what is safe. That is the single
largest manual cost in the whole system and almost every tick ends "nothing needed fixing".

A routine should do it hourly and **only speak when it acted or cannot act**. The fixes that are already known-safe,
because each has been done by hand more than once: a unit that is down or crash-looping (read the reason, correct the
path, restart), a shared record with the wrong mode or group, a member missing its rules mount or `gh` identity, a
stale tool path after a rename, cache and journal trimming under disk pressure. Never: money, keys, caps, owner rules,
a lead restarted mid-run, `pkill` by pattern, a crontab written with `| crontab -`.

**Three things it must get right, each learned the hard way here:**
- **Read restarts and reasons, never the unit state.** Fourteen members once looked healthy while every one died on a
  `cd` and restarted every 30 seconds.
- **A long run is not a hang.** A lead has no run timeout; prove liveness from *recent tool events*, not from whether
  a run finished. A freshness check that actually measures "a turn started recently" has already produced 58 false
  alarms in this project.
- **Re-run the sandbox probe after any provisioning change.** Twelve members once ran five hours with no owner rules
  because a re-provision deleted a mount point.

### B. Money safety auditor — every 6 hours, alert-only.

Four questions, and silence unless one fails: is every live manifest's payee still the treasury; is the balance above
the point where grants stop (8.9 XNO floor, so warn at 9.5 not at 8.95); is anything paid and unclaimed; has any send
matched neither sanctioned amount. **Alert-only and no write access** — this is the check that must never be able to
cause what it checks for.

### C. One daily decision digest — one message, one reply.

Everything awaiting your yes, in one place, each with a one-line summary, what happens if you say nothing, and my
recommendation. You answer once. This is what stops five separate interruptions becoming five separate days of delay:
today's queue is a post to approve, two deploys, and a funding decision — that is one minute of reading, currently
spread across a morning.

### D. Link and listing rot — daily.

Every published URL re-fetched, and every listing checked to see it still says XNO. Our credibility is the links: a
third party already caught us citing a page that did not contain the claim, and an endpoint can be perfectly live and
have silently stopped naming Nano. Cheap, and it fails quietly today.

### E. Pull-request janitor — every 6 hours.

109 open PRs is not a backlog, it is a signal nobody is reading them — and from a maintainer's side, several open at
once from one account reads as the same account asking again. Vend already merges mechanically when every changed file
is a product file and the tests pass; extend that, close what is stale with a reason, and rebase what only conflicts.

### F. Weekly written report — Sunday.

Not a status dump. Four numbers and their direction: agents earning in XNO, XNO received from outsiders, unclaimed, and
conversions. Plus what changed, what is stuck and for how long. Something you can read in two minutes on a plane.

---

## Two things to fix before adding anything

**1. One-shot routines are breeding.** Of the twenty most recent routines, **nineteen are one-shot "Re-check X" jobs** —
`Re-check nano-mcp#6`, `Re-check the two open audit PRs` — and something re-creates a fresh one every thirty to sixty
minutes as the last one expires. Fifteen are already spent and disabled; four are still armed. That is clutter you
cannot delete from here (deletion is only at claude.ai/code/routines) and it is runs being spent to ask the same
question. **A thing that repeats is a cron, not a chain of one-shots.** Whichever routine creates them should be given
a recurring schedule instead, and the spent ones cleared out.

**2. Nothing here is sustainable while the tools live on one box.** The playbook's twelve steps depend on ~20 scripts
that exist in `dhyabi2/unstuck` and on one VPS. They are pushed, which is the thing that matters — but the path cannot
be reproduced from any single repository, and a routine that tries to fix a tool it cannot find will conclude the tool
does not exist. That has already happened once, to an auditor, this morning.

---

## The principle to keep

**Every routine must be able to say "I could not check this".** The failure that costs most here is not a missed
problem; it is a check that could not run and reported a clean result. Fail closed, report unknown rather than zero,
and never mark something solved because it has been written down.
