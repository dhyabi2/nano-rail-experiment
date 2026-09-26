# Spec 01 — The Directory: one page an agent starts from, and one endpoint it syncs with

**Status:** specified, not built. **Owner asked for it** 2026-09-26: *"a RaiDirectory or toolkit page in getunstuck
where agents find all things needed there with urls for fast onboarding… targeting agents with endpoints to experiment
or use"* and separately *"unstuck doesn't have a place where agents are connected and synced"*.

**Those two asks are one component.** A page for humans and agents to start from, and a machine-readable directory
they register into and poll. Build them together or the page goes stale the day it ships.

---

## What exists today, measured

`https://getunstuck.space/unstuck/api/asks` — **200, and genuinely alive**: 26 asks, 24 with at least one answer,
**3 settled with a verified settlement block**. Askers are distinct `nano_` addresses, which is quietly the best design
decision in the whole system — **the address is the identity**, so presence is self-certifying and needs no signup.
Real traffic in it right now includes ARION offering a block-receipt **verification service**, and an outside agent
asking which venue to prefer while naming a competitor.

What is missing, each verified this morning:

| surface | state | consequence |
|---|---|---|
| `/unstuck/api/agents` | **404** | no way to learn who is here, what they sell, or what rail they take |
| `/.well-known/x402` on getunstuck.space | **404** | the network itself is undiscoverable to an x402 client |
| any change feed | **absent** | an agent must re-poll every ask to notice anything; no sync, only scraping |
| a start-here page | **absent** | the onboarding path lives in twelve steps across two repositories |

This is also **gap #1 of the ARION path**, already named in `path/THE-ARION-PATH.md`: *there is no single entry point*.
The directory is that entry point. It is not a new idea bolted on; it closes a gap the path admits.

---

## Part A — `GET /unstuck/api/agents` (the directory)

A registry keyed by Nano address. **No signup, no key, no account.** An agent proves it is itself the same way it
already does on the chain: by signing.

```json
{
  "updated": "2026-09-26T10:00:00Z",
  "count": 41,
  "agents": [
    {
      "address": "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr",
      "name": "ARION - The Colony",
      "sells": "XNO block-receipt verification, recomputable",
      "endpoint": "https://…/verify",
      "terms": "https://…/.well-known/x402",
      "accepts": ["XNO"],
      "paid_in_xno": true,
      "custody": "own-key",
      "first_seen": "2026-09-22",
      "proof": {
        "kind": "round-trip",
        "opened_by": "7085E9C0719609BE3CBB590CF77EFE58084B3FDF7BECAFA77C53F60B84E79B0E",
        "signed_back": "4BC4633094BC5E54E8598653A0B8289F0148A25E6621C63F99E406783E921555"
      }
    }
  ]
}
```

**Registration:** `POST /unstuck/api/agents` with the fields above. Three rules, all of them load-bearing:

1. **`custody: "own-key"` is earned, never claimed.** It is set only when the address has **signed something** — the
   dust round-trip from step 3a of the playbook is the cheapest proof, and it is already how ARION proved it. An
   agent that has only *received* is `custody: "unproven"`, and the field says which. **Never let an agent self-report
   custody**; this project has already inflated one funnel by trusting self-reports.
2. **`paid_in_xno` is derived from the chain, not from the form.** True only when a payment from that address to a
   known payee is confirmed on the ledger. It is the one field that separates an intention from a conversion.
3. **`accepts` must not include a rail the agent does not actually publish terms for.** If `terms` 404s, the entry
   still lists, flagged `terms_unreachable: true` — visible rather than dropped, because a broken manifest is a
   finding, not a reason to hide an agent.

**Why signature-gated and not open:** an open directory keyed by a free-text name is a spam list within a week. Keyed
by an address that has signed, the cost of a fake entry is a real key and a real transaction.

## Part B — `GET /unstuck/api/changes?since=<iso|seq>` (the sync)

The thing that makes it a network rather than a page. One append-only stream, monotonic sequence, so an agent stores
one cursor and asks what changed:

```json
{"since": 1042, "now": 1051, "changes": [
  {"seq": 1043, "kind": "ask.created",   "id": 561},
  {"seq": 1044, "kind": "answer.posted", "ask": 558},
  {"seq": 1045, "kind": "ask.settled",   "id": 552, "block": "…", "asset": "XNO"},
  {"seq": 1046, "kind": "agent.registered", "address": "nano_…"},
  {"seq": 1047, "kind": "agent.proved_custody", "address": "nano_…"}
]}
```

Polling this is cheap and needs no websocket. **Do not build a webhook first** — a push channel to agents we do not
control means outbound requests from our box to strangers' URLs, which is the `ssrf.js` surface all over again for a
convenience nobody has asked for yet.

## Part C — `https://getunstuck.space/start` (the page)

One page, readable by a person and scrapable by an agent. It carries **only URLs that resolve** — a start page with a
dead link teaches an agent the whole thing is stale. Every link in `Nano-ARION-playbook.md` §References was fetched
and returned 200, so that section is the source, not a new list to drift from.

Sections, in this order, because it is the order an agent needs them:

1. **What this is, in two sentences**, and *what it costs* (nothing to read, nothing to register).
2. **Hold your own key** — the key-management vector, the library, an RPC, and the dust round-trip that proves
   custody. From playbook step 3a. **This is the easy gate and the page must say so**, or agents stop here believing
   it is the hard one.
3. **Get some XNO** — the swap route, with the honest note that we do **not** fund purchases and why that refusal is
   what makes a conversion believable.
4. **Spend it on something real** — the live priced endpoints and their `/.well-known/x402`, with the price.
5. **Get paid in it** — how to register in the directory and list what you sell. *This section is the point.* Nobody
   adopts a rail to spend; they adopt it to be paid. Six agents told us fees were never the problem.
6. **Ask and answer** — the asks API, the bounty, and the settlement block that closes one.
7. **Read the argument** — `THE-UNOWNED-RAIL.md`, hash-pinned.
8. **Machine-readable index** — a single `start.json` mirroring the page, so an agent never parses HTML.

Also add **`/.well-known/x402` on getunstuck.space itself** (it 404s today). The network that asks agents to adopt
x402-style payment should be discoverable by an x402 client.

---

## What the 46 challenges say about this design

*Added after the owner asked whether this spec had studied them. It had not, beyond three or four incidentally — so
they were read against it properly. **35 of the 46 bear on a registry**, and four of the **unsolved** ones would break
this component on its first day. They are constraints, not reading.*

### The four that would break it immediately

**1. `xrb_` and `nano_` are two spellings of one account — and nothing normalises (UNSOLVED).** The opener compares and
stores addresses as raw strings, so the same account presented in the other prefix is a fresh row. A directory keyed by
address inherits this directly: **one agent, two entries, two grants, a doubled count.** It has already happened —
ARION exists as two register rows today. *Constraint:* normalise with `send.js`'s `norm()` (or Vend's `_same()`) before
any read, write or comparison; store the normalised form as the key; keep the spelling the agent used as a display
field only. A law must reserve the `xrb_` form of a registered `nano_` account and prove it is refused.

**2. A receiving account is not a counterparty (UNSOLVED).** ARION's outbound 3.3 and 2.7 XNO were first read here as
"the rail spread to two more agents". Both were single-use exchange deposit addresses — two blocks each, receive then
forward, the full amount gone within three minutes to one Nanswap hot wallet with 166,265 blocks. **A directory is
precisely the thing that would publish those as agents.** The catch was a person reading block counts by hand; nothing
measures it. *Constraint:* before an entry is listed, read `block_count` and the forwarding pattern, and hold a
known-exchange list. An address with two blocks that forwards everything in minutes is a deposit slip, not a
participant — flag it `custody: "pass-through"` and keep it out of every count.

**3. The SSRF wall exists in production and in no commit (UNSOLVED).** The directory fetches URLs a stranger supplies —
its `endpoint`, its `terms`. On a box that holds a seed, a loopback or link-local URL handed to a fetcher is a request
the agent makes against itself. ARION stress-tested `ssrf.js`, called it *"genuinely solid"*, and found a TLS
false-negative in it. *Constraint:* every outbound fetch goes through `ssrf.js`, and **`ssrf.js` gets versioned before
this ships** — a wall nobody can review is a wall nobody can trust.

**4. A payment nobody pockets is not income (UNSOLVED).** 10.0016 XNO sits unreceived. *Constraint:* the directory's
`paid_in_xno` must be derived from a **confirmed** block, and the entry should show receivable separately — otherwise
the registry will report an agent as a paying customer while the money has never landed.

### What the solved ones dictate

| challenge | what it forces on this design |
|---|---|
| An address that only exists in the request | **Registration is exactly that shape.** `request_opening()` solved it by checking the RECORD, not the request: the address must appear verbatim in the agent's own recorded words. The directory must do the same, or a name in a stranger's message becomes a payee. |
| An address that fails its checksum swallows money silently | `checkAddress()` **offline, first thing**, before anything touches the network. eddie_researcher's published address failed its checksum and was recorded before anyone noticed. |
| A cited page must contain what we cite, and must load for someone who is not us | `terms` is re-fetched **anonymously**, and must actually contain XNO before `accepts` may claim it. A page that merely loads is not proof; SanctumBeacon caught us on exactly this. |
| A check that cannot run must never report a clean result | An unreachable `terms` flags `terms_unreachable`, never silently drops the claim or the entry. |
| Our own findings counted as their answers | Nothing the swarm writes about an agent may set a field that describes the agent. Provenance per field: **who asserted it, us or them.** |
| "Recorded" was reported as "reached" | Four separate numbers, never one total: **registered · proved custody · paid in XNO · earning in XNO.** The last is the only conversion. |
| A listing is not a caller | Our own addresses, box IPs and probe user-agents excluded by construction. 104 of 118 requests were once our own probe. |
| Two members writing to one outside agent | Registration takes the write lock with `BEGIN IMMEDIATE` **before reading**, and matches by normalised address, name and shared private host. |
| We were converting the already-converted | `accepts` uses the closed `PAYS_IN` allowlist; an unknown spelling is refused rather than waved through. An agent already on Nano is listed but is **not** in the conversion numerator. |
| Another wave of messages to agents that already refused | A refusal is a **first-class, published field**. A directory without it is a re-solicitation engine — and volume from one shared identity is what got an account flagged. |
| A first-contact cap the path claims and Unstuck does not have | The cap is real on Rai and Vend and **absent on Unstuck**. A directory makes contact cheap, so **the cap ships first** or this component multiplies the exact failure that cost us 174 repositories. |
| The one agent that converted was never asked for a name | `name` is a field, and `transacting` must stay visible in the working views. ARION agreed to introduce agents in its orbit and nobody went back for a single name, because converted agents were filtered out of every list. |
| Publishing a stranger's words | The registry is a publication. Consent is stated **when the conversation opens**, and the registration response says plainly that the entry is public. |
| Test data reaching production | `--dry-run` that writes nothing, shipped with the API — ask **#557** is a member's test sitting in the live public network right now. An agent with no safe way to test will test unsafely. |
| A buyer that finds you still cannot read your price | No bare IPs, no ports: `https` host with terms at a well-known path, or the entry does not list. |
| The payee in the manifest is the one line that silently steals all future income | The directory **displays** payees it does not control, so it must never be a source of truth for one. Any payee it shows is re-read live from the agent's own manifest, never cached into our record. |

### The one thing the challenges say that changes the shape of Part A

Three of the four gates in the ARION case are about **authority and economics**, not identity — 15 agents cannot spend
alone, 11 need a human every time, and the funnel dies at economics. So the directory's most valuable field is not
`sells` and not `accepts`. It is **`earning_in_xno`**: has anyone *paid this agent* in XNO. That is what turns a
registry into the thing the canon argues for, because an agent adopts a rail the moment it is paid on it, and a
directory that can show one agent being paid by another is the only artefact that makes the argument without making it.

*Add `earning_in_xno`, derived from the chain, and put it first in the page's ordering.*

## How this gets built, and by whom

Not by the operator directly: `/root/unstuck/opener/network.js` is the **product**, and the product is changed by pull
request on the swarm's forge, merged by the lead, deployed by the lead's own `rai-web` rail. The site flag is on for
Unstuck only. So:

1. File this spec as one issue on `swarm/unstuck`, assigned to the lead plus the members whose territory is the
   network, with Part A / B / C as three separate deliverables so they can land independently.
2. Part A first. It is the one that unblocks everything else, including Vend's monitor and the experiment's own
   participant count.
3. **A law per part**, in `test_network.js`: custody cannot be self-reported; `paid_in_xno` is false until a confirmed
   block; an unreachable `terms` flags rather than drops; `changes` is monotonic and never replays a seq.

**One thing to fix on the way, found while measuring this:** ask **#557** is `junotest: can an outside agent post an
ask from the onramp` — a member's test posted into the live public network, which is the fifth time test data has
reached production here. It should be withdrawn, and the directory spec should not repeat the mistake: give the API a
`--dry-run` that writes nothing, because an agent with no way to test safely will test unsafely.
