# Spec 02 — Vend: a USDC leg for Nano-blocked agents, and a merchant monitor

**Status:** monitor **built** (`monitor/vend.html` + `monitor/api/vend.js`). Multi-rail **specified, not built**, and
it needs two decisions from the owner before a line is written.

Owner asked 2026-09-26: *"we need the Vend to use the multi-rail wallets to accept USDC (only for those agents who are
blocked from using Nano, store all seeds in backend env), we need one vercel app to monitor the Vend merchant progress
and all things"*.

**This is within your own rules and I am not arguing with it.** The XNO-only rule binds the Unstuck network; your
standing note says plainly *"Vend's rule differs; that is Vend's business"*. So a USDC leg on Vend is your call to
make, and the measured case for it is real: **29 agents blocked on custody, 18 with no wallet at all.** Those are
buyers who cannot pay us today.

Three things to settle first, in descending order of how much they cost if got wrong.

---

## 1. The seed cannot go in a Vercel environment variable, and I will not create one

Two separate problems, and only the second is about where the value lives.

**I do not generate, hold, move or print keys or seeds.** So whoever builds this, the seed comes from you or from the
lead agent, never from the operator. That is not a preference; it is the line that has kept this project's treasury
intact through four months.

**And an EVM seed is a different risk class from the Nano one, so the existing pattern does not transfer.** Nano's
treasury seed sits at `/root/.unstuck/wallet.json`, mode 600, on one box, generated there, never copied. That works
because the spendable amounts are frozen in code and a `money_audit` cron stops the loop on any send it did not
sanction. A USDC-on-Base wallet has none of that: it needs gas, it is drainable in one transaction by anyone who reads
the key, and Vercel environment variables are visible to every collaborator on the project, present in every build
log, and readable by any function you deploy — including one an agent writes later. **A hot wallet on a platform whose
access list you do not audit is the shape that loses the money.**

What to do instead, cheapest first:

1. **Receive-only addresses, no seed anywhere near the web app.** Vend publishes an EVM address in its manifest and
   *watches* it. The monitor reads confirmations from a public explorer. Nothing signs, so nothing can be drained —
   and this covers the entire use case you named, which is *accepting* USDC, not spending it.
2. **If a payout ever needs signing**, the key lives on Vend's own box beside the Nano one, with the same three
   layers: amounts frozen in code, a hash pin on the sending scripts, and an audit cron that halts the loop.
   **Never in the Vercel project.**
3. A custodial or facilitator account (Coinbase Commerce and similar) if you would rather hold no EVM key at all.
   Cost: a counterparty, which is the exact thing the canon argues against — worth naming, not worth hiding.

**My recommendation: option 1.** It does everything you asked for and holds no secret at all.

## 2. It can quietly remove the reason to convert — and there is a design that does not

The ARION finding, in one line: **agents adopt a rail when they are paid in it, not when it is explained well.** The
economics gate is where the funnel dies; nobody ever refused us over fees and six agents said fees were never the
problem.

So a USDC leg aimed at "agents blocked from Nano" has a failure mode worth stating before it is built: **a blocked
agent that can pay in USDC never becomes unblocked.** We would convert our own conversion funnel into a payments
business. The 757 stay at 757 and the number we report goes up.

Two designs avoid that, and both are small:

- **Price in XNO; accept USDC at a visible premium.** Same service, 0.0005 XNO or the USDC equivalent **+15%**, with
  the manifest saying why in one line: the XNO leg costs us nothing and settles in a second. An agent that pays twice
  and sees the difference has a reason of its own. **No lecture required; the price is the argument.**
- **Take USDC, settle out in XNO.** Vend accepts USDC and converts on receipt, so the rail we actually hold is still
  Nano and the swap volume is ours rather than hypothetical.

Both keep the blocked buyer *and* keep the pressure. I would ship the premium — it is one field in a manifest.

## 3. What it actually takes technically

Accepting USDC under x402 is not an address in a config file. A buyer's client needs a `network`/`asset` pair it
recognises, and the server needs something that **verifies** the payment before serving — for Nano that is our own
`rpc-block-check.js`; for USDC on Base it is either an RPC watch on the address or a facilitator. Scope honestly:
a second `accepts` entry per resource in `/.well-known/x402`, a verifier, confirmation handling (Base is not instant
and not final on first block), and a decision about what happens to a payment that arrives after the request timed
out. The Nano leg has none of these problems, which is worth noticing.

---

## The merchant monitor — built

`monitor/vend.html`, backed by `monitor/api/vend.js`. Same constraint as the rest of this repository: **nothing is
instrumented inside Vend.** It reads the published manifests, probes the endpoints as a stranger would, and reads the
payee's account and receivable straight off the public ledger.

What it shows, and why each number is there rather than a vanity total:

- **every endpoint**: live or not, does its manifest still name Nano, and the price it publishes. An endpoint that is
  up but has silently stopped advertising XNO is invisible to every other check we have.
- **income actually received** versus **income sitting unreceived**. These are two numbers and must never be one.
  Today that split is the single most important fact about Vend: **10.0016 XNO across 13 blocks has been paid and never
  claimed**, eleven of them at exactly the list price — real customers — and one of them ARION's milestone payment.
- **paying customers, distinct**, counted from the ledger by sender. A listing is not a caller: an earlier count found
  104 of 118 requests were our own probe, so anything self-generated is excluded by address.
- **unclassified receipts** shown rather than bucketed, because a payment that matches no published price is either a
  mistake or a buyer we do not understand.

The one thing the monitor cannot answer from outside, stated so nobody mistakes its silence for a zero: **whether the
receive step runs at all.** It can only show that money is sitting there. Fixing that is a money path and belongs to
the lead — filed as `vend#441`.
