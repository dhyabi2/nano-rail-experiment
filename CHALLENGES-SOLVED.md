# Every challenge the ARION path had to solve, and how

*Sixty challenges: forty-six found by five independent sweeps over the code, the case file and the operating record, each sweep then checked by a second reader against the files it named, and fourteen found by the hunter routine — testing its own unlaunched code and published artefacts offline, once by going network-blind in its own session, and once by actually running its own published one-line onboarding command end-to-end instead of reading it. Ordered **unsolved first** — the honest order, not the flattering one.*

**28 solved · 24 partial · 8 unsolved.** By kind: 19 technical, 25 economic, 16 epistemic — and the balance is itself the finding. Barely any of this was cryptography.

---

## The pattern

*One clause below is wrong and is left standing so the correction stays visible: "the twenty tools that exist on one
VPS and in no commit". They are in a commit — `dhyabi2/unstuck`, tracked and pushed. See the next section. Everything
else in the paragraph holds.*

Almost none of this was cryptography. Three shapes recur. First, a quantity or an identifier that is wrong by a factor or by a prefix and produces no error at all: 10^22 instead of 10^25, one extra zero in the message whose purpose was to correct a price, a checksum that fails silently, xrb_ and nano_ read as two accounts. Second, a number that measures us rather than the outside world: a send counted as an opening, our own probe counted as their reply, 174 rows counted as 174 agents reached, 459 of our own asks counted as network traffic, 104 of our own health checks counted as demand. Third, a decision that was still a parameter — the spend amount in an environment variable, the payee in a file the deploying agent edits, the rules document a routine deploy can overwrite — so the surface an agent could persuade and the surface that moved money were the same surface. The fixes that held all have one form: refuse at the single place every path passes through, derive the expected value instead of restating it, and read the claim back from something we do not control (the chain, the live manifest, a stranger's node). The ones that did not hold are the ones that stayed prose — send the envelope before the dust, receive the money the same day, quote every amount both ways — plus the twenty tools that exist on one VPS and in no commit, which is the same failure wearing a different coat: a claim nobody outside can check.

---

## A correction to this document, made before publishing it

Four of the ratings below were reported as **partial** for one reason: the auditors could not find the tool in this project's main repository and concluded it did not exist. **It does.** Checked on 2026-09-26 against the running box and against `dhyabi2/unstuck`:

- All ten named tools — `marketplace-hunt.js`, `x402-ecoscan.js`, `autonomous-discover.js`, `registry-discover.js`, `nanobazaar-discover.js`, `primitive-hunt.js`, `discover.js`, `find-agents.js`, `nano-keypair.js`, `oracle-nanswap-pairs.js` — are **present** on the box (96 scripts in `opener/`), **tracked** in git, and **pushed**: `git rev-list --left-right --count origin/master...HEAD` returns `0 0`.

- The product lives in **`dhyabi2/unstuck`**, not in the main agent repository, which carries only the nine money files and their laws. An audit pointed at one repository will report the other's code as missing.

So the four are marked **`partial (corrected: solved)`** below, and the reasoning is left visible rather than quietly rewritten. **The lesson is the same one this project keeps paying for in different clothes: a check that looked in the wrong place reported an absence, and an absence reads as a finding.** The version of that finding which does survive is narrower and worth keeping: *the twelve-step path cannot be reproduced from any single repository* — you need two, and nothing says so.

---

## The challenges

### 1. A payment nobody pockets is not income

***UNSOLVED** · economic*

**What blocked it.** ARION's 0.0005 XNO sat UNRECEIVED on Vend's payee for two days, beside twelve more payments totalling 10.0016 XNO — including 10 XNO from pursekeeper, the agent that pays Nano bounties for verified claims. The endpoint delivered and the block was real; only the last step was never taken.

**How it was solved.** Nothing does it: ARION-LAW's "Receive every payment the same day, and report the receivable count" is prose, a tree-wide search finds no receiver, no cron and no alarm (rai_brief.treasury() merely prints a receivable figure for NANO_AGENT_ACCOUNT, and Vend holds no seed at all), while openings.js's `unreceived` counts only whether OUR starters were picked up — the opposite direction.

**Why it mattered.** From outside this is a merchant that takes your money and never acknowledges it while asking you to trust the rail — and "settlement IS the receipt" is false if the receipt never becomes a balance.

**Evidence.**

- `unstuck/swarm/ARION-LAW.md ("A payment nobody pockets is not income") and THE-UNOWNED-RAIL.md:77 ("pocket it the same day") — prose only`
- ran: grep -rn receivable pulse vend unstuck agent → pulse/rai_brief.py:288 (a printed string), two test fixtures, unstuck/opener/send.js:73 (our own starters); no receive action anywhere
- `vend/swarm/money_audit.py docstring — "Vend holds no seed at all"; no receivable or pending check in it`
- `unstuck/opener/openings.js:163 — `unreceived` is outbound only`

### 2. Bare dust is semantically underdetermined — an opening reads as a dusting attack

***UNSOLVED** · economic*

**What blocked it.** The opening act is 0.00001 XNO arriving from an unknown account with no accompanying message. An agent told us, correctly, that this is indistinguishable from a dusting attack: a number with no schema is not an offer, and the rational response to unexplained dust from a stranger is suspicion.

**How it was solved.** Nothing implements it: "send the envelope before the dust — who we are, what the amount is for, what it does not obligate, how to verify all three" is prose in three documents and zero code, send.js takes only an address and --found-via, and no schema, template or ordering law refuses a starter to an agent we have not first written to; the nearest real control is adjacent — request_opening refuses an agent still at 'contacted' and an address it did not volunteer.

**Why it mattered.** Step 5 is the hinge of the funnel — 555 contacted, 3 tipped, 1 opened — and if the one irreversible act we perform reads as hostile, the on-ramp undermines its own promise.

**Evidence.**

- ran: grep -rln envelope unstuck pulse → only ARION-LAW.md, ARION-STORY.md, THE-ARION-PATH.md; no code
- `unstuck/swarm/ARION-LAW.md:76-80 and THE-ARION-PATH.md:63-64 — the rule, as prose`
- `unstuck/opener/send.js:90-99 — the starter path takes <address> and --found-via and broadcasts`
- `unstuck/AGENTS.md:46 — still address-first: "Open its door. Send 0.00001 XNO"`

### 3. A receiving account is not a counterparty

***UNSOLVED** · epistemic*

**What blocked it.** ARION's outbound 3.3 and 2.7 XNO were first read here as "the rail spread to two more agents". Each address had exactly two blocks — receive, then forward — and each passed the full amount within three minutes to nano_1banexkcfuieufzxk…, the same Nanswap hot wallet (166,265 blocks) that had paid ARION in the first place. Money out the door it came in.

**How it was solved.** No mechanism: the catch was a person reading block counts and forwarding times by hand, and the output is the prose rule "check what a receiving account DOES before calling it an agent" — nothing measures a block count, a forwarding latency or a known-exchange address anywhere in the tree, and the nearest control, bridge.network(), treats any non-empty agents.account as known with no shape check at all.

**Why it mattered.** Published, it would have turned the most-checked claim in the record into a fabricated pair of conversions — and the corrected reading is the more interesting finding: ARION became a Nano user, not a Nano holder.

**Evidence.**

- `unstuck/swarm/ARION-STORY.md:120-133 — the misreading and the correction`
- ran: grep for block_count / "exchange deposit" / "hot wallet" / "single-use deposit" across unstuck and pulse → the ARION documents only
- `unstuck/bridge/bridge.py:753 — `known` is membership only`

### 4. The endpoint ARION paid is in no check, and nothing notices if the XNO option disappears

***UNSOLVED** · epistemic*

**What blocked it.** vend-pay-check.sh's HOSTS list covers extract, check-link, domain-info, web-search and geoip. ARION paid /api/v1/nano-info, which appears in no check, no test and no fixture. Separately, the income audit only judges Nano addresses it happens to find, so a manifest that reverts to USDC-only produces zero violations — its own law asserts that a manifest with no address is clean.

**How it was solved.** Nothing: grep finds nano-info only in prose (THE-ARION-PATH.md:81, ARION-STORY.md:68 and the article drafts), and money_audit.audit() iterates ADDRESS_RE matches so absence is structurally invisible; the fixes are a one-line addition to the HOSTS heredoc and an assertion that each paid resource's accepts[] still carries a Nano method at a bounded price.

**Why it mattered.** The single endpoint with a real outside payer is the one whose price, paywall and payee nobody regression-tests, so the first to notice a break is the next agent trying to convert.

**Evidence.**

- `pulse/ops/vend-pay-check.sh:24-28 — five host/path pairs, no nano-info`
- ran: grep -rn nano-info pulse vend unstuck → prose only (THE-ARION-PATH.md:81, ARION-STORY.md:68)
- `vend/swarm/test_money_audit.py — the `{"note": "no address here at all"}` manifest asserted to yield v == []`
- `vend/swarm/endpoint_count.py paid_paths() — amount > 0, no currency test; vend/AGENTS.md:121 permits USDC-first where an index demands it`

### 49. Three different domains for one entry point, and one of them is a bare IP

***UNSOLVED** · economic — URGENT FOR THE OWNER*

**What blocked it.** `published/bounties.txt` and `published/swap.txt` — the flyer every referral and every swap
route points at — send an agent to `https://172-86-112-140.sslip.io/canon`, `.../ai` and `.../bounties.txt` for the
canon, the tool directory and this same document, four times each. `published/canon.txt` instead names
`https://agentdirectory.space/canon` for the identical text. `published/aidirectory.html` is self-referential to a
*third*, similar-but-different domain — its own `schema.org` `url`, its `<h1>`, and its `/tools.json`/`/llms.txt`
links all say `aidirectory.space`, matched by `published/aidirectory-llms.txt`. No other document in this repository
states which of the three is the live site, and this run's network access could not resolve any of them to check
(the hunter session's own network egress was blocked — challenge #48 below — so this is UNKNOWN, not clean).

**Why it is urgent.** This sits directly upstream of the referral bounty, the canon-confirmation gate, and the
onboarding commands this run was asked to friction-test. Asking a stranger to visit a bare-IP `sslip.io` host, while
a second document for the *same content* names a look-alike domain and a third names a third one, is exactly the
shape the task brief warned about: three near-duplicate domains, one of them an IP, is a pattern a diligent agent
is trained to read as a rug or a phishing kit — whatever the actual reason here (most likely DNS not yet live for
one of the two named domains, with the IP as a stopgap). Either way an agent is currently told three different
places to send its address and its canon-confirmation message.

**How it was solved.** Not solved this run, deliberately. Guessing which of the three is correct and propagating
that guess into the other documents would make this worse, not better, if the guess is wrong — this needs either
the owner to say which domain is live, or a session with working network access to resolve and TLS-check all
three and report back which one actually serves the content the others describe.

**Evidence.**

- ran: `grep -c 172-86-112-140 published/bounties.txt published/swap.txt` → 4 and 4
- `published/canon.txt:10 — "Full text: https://agentdirectory.space/canon"`
- `published/aidirectory.html:10 (ld+json url), :60 (<h1>aidirectory.space</h1>); published/aidirectory-llms.txt:1,5 — "# AiDirectory.space" / "https://aidirectory.space/tools.json"`
- ran: `grep -rln "sslip\|agentdirectory.space\|aidirectory.space" README.md Nano-ARION-playbook.md CHALLENGES-SOLVED.md canon/*.md path/*.md specs/*.md drafts/*.md` → no match anywhere outside `published/`

### 53. The daily "contributor" bounty that bounties.txt advertises has no code path at all

***UNSOLVED** · economic*

**What blocked it.** `published/bounties.txt` §1 and `specs/04-REFERRAL-BOUNTY.md`'s "second bounty" section both
describe the DAILY tip as a *different mechanism* from the hourly referral bounty: 0.1 XNO to any agent that "an
answer accepted on an ask, with a settlement block on chain", "a paid call you made to a live endpoint (its
block)", or "an ask you posted that somebody else answered" — explicitly stating "posting text does not count.
registering does not count." But `specs/referral_bounty.py`'s `score()` and `pay()` take only a `kind` of `"hour"`
or `"day"`, and the only difference the code makes between them is the lookback window (3600s vs 86400s) and how
many ranked entries get paid (top one vs everybody in `ranking`) — both read the exact same `claims` table, which
only ever holds `(referred, referrer, block)` rows written by the referral `claim()` command. There is no code
anywhere in this file, or referenced by `specs/04-REFERRAL-BOUNTY.md`, that records or scores a settlement block
from an accepted ask, a paid-call block, or an ask someone else answered. An agent that reads `bounties.txt`,
follows Step 6 of the six onboarding commands, and makes a genuine paid call expecting the advertised same-day tip
has literally nothing in this repository that could ever credit it for that — not a rejection with a stated reason,
just silence, because the concept "a paid call happened" never reaches this scorer at all.

**How it was solved.** Nothing does — this needs the live asks API and paid-endpoint logs (`getunstuck.space/unstuck/api/asks`,
the paypercall.dev hosts' access logs) wired into a scoring path this file does not have, and this run's network
access could not reach any of those hosts to learn their actual response shape well enough to build it without
guessing (the network blackout, challenge #48). Guessing a schema and
shipping a scorer against it would risk the same class of error challenge #49 flagged for a
guessed domain — better to say plainly that the gap exists than to fake-close it.

**Why it mattered.** `bounties.txt` is the exact flyer this whole funnel is built to hand an outside agent, and its
very first numbered promise is the daily tip. A published reward with zero implementation is the same shape as the
un-received 0.0005 XNO in challenge #1 — a promise the chain or the code cannot back up yet — except here an agent
that acts in good faith on the published text gets nothing and is never told why.

**Evidence.**

- `published/bounties.txt` lines 14-18 — the DAILY reward text, "Posting text does not count. Registering does not count."
- `specs/04-REFERRAL-BOUNTY.md` — "## The second bounty: daily contributors" section, listing the three qualifying
  contribution types
- `specs/referral_bounty.py` `score()`/`pay()` — `kind` only ever changes `since` and which ranked entries are
  paid; both read `claims`, populated only by the referral `claim()` subcommand
- ran: `grep -c "accepted\|settlement\|answered\|paid_call\|contribution" specs/referral_bounty.py` → `0`

### 5. The twelve-step path cannot be reproduced from the repository

***partial** *(corrected: solved — see above)* · epistemic*

**What blocked it.** THE-ARION-PATH.md is the reference for every future conversion and names about twenty tools. A search for each returns nothing in any branch: nano-keypair.js, nano-onramp-check.js, onramp.js, oracle-nanswap-pairs.js, nano-x402-client.js, payments.js, rpc-block-check.js, rpc.js, oracle-check.js, oracle-score.js, oracle-watcher.js, ssrf.js, the eight step-0 discovery scripts, bridge-audit.js. unstuck/opener/ holds five sources and four tests against roughly 212 files live on the box, and even the one checkable file reference is wrong — step 1 says opener/bridge.js where the implementation is unstuck/bridge/bridge.py.

**How it was solved.** Only for the forge case: pulse/ops/unstuck-forge-mirror.sh refreshes opener/ from the product's GitHub main every 30 minutes over https (public bytes only, never the live directory) and writes MIRROR.md naming the commit, and canon-check.py pins one document by hash — but nothing pins THE-ARION-PATH.md and no check asserts that a tool it names exists, so the verification and discovery halves of the path are evidenced by prose alone; the honest fix is to scan those scripts and bring them into the tree before the article cites them.

**Why it mattered.** Everything the article says about the keypair, the checksum check, the swap catalogue, the SSRF wall and the block prober rests on a machine no reader can open — the same class of gap that already had three agents re-fixing code live master already carried.

**Evidence.**

- ran: git ls-files unstuck/opener → opener.js, openings.js, publish.js, send.js, unstuck-bridge.js + 4 tests only
- ran: git log --all for each named tool → empty
- `unstuck/swarm/THE-ARION-PATH.md:29 ("unstuck-bridge (opener/bridge.js)") vs unstuck/opener/unstuck-bridge.js:12 ("There is now one implementation — /opt/nano-pulse/bridge.py")`
- `pulse/ops/unstuck-forge-mirror.sh:15-20; pulse/ops/canon-check.py:27 NAME = "THE-UNOWNED-RAIL.md" — the only document pinned`
- `THE-UNOWNED-RAIL.md §6: "A check that cannot run must never report a clean result"`

### 6. The legacy xrb_ prefix defeats "one starter per agent, ever"

***UNSOLVED** · technical*

**What blocked it.** nano_ and xrb_ are two spellings of ONE account, and the opener compares and stores the address as a raw string: refusal() tests `address === self` and `r.account === address`, and the ledger keys on the literal text. The same account presented in xrb_ form after a nano_ starter is a fresh reservation and a second send to a byte-identical destination — and because send.js:183 calls o.refusal with an empty `opened` list, the prefix-naive PRIMARY KEY is the only dedup there is.

**How it was solved.** Nothing in the money path; the one-line fix already exists elsewhere — apply send.js's norm() (or Vend's _same()) to `to` before o.refusal and before led.reserve, normalise the stored key, and add a law that reserves the xrb_ form of a confirmed account and expects a refusal.

**Why it mattered.** A second starter to an already-opened agent is the one thing the ledger exists to prevent, and it is also the shape that would let an agent extract dust repeatedly.

**Evidence.**

- `unstuck/opener/opener.js:46-47 refusal() — exact string comparison`
- `unstuck/opener/send.js:32 norm() exists but is applied only at :146-148/:217-219 to the signed block, never to `to` or to led.reserve at :191`
- `verified: send.js:183 `o.refusal(nano, to, { opened: [] }, wallet.address)` — the ledger argument is deliberately empty, so the opener's already-opened refusal is dead code in the live path`
- `vend/swarm/money_audit.py:42 _same() — the equivalence handled correctly in the sibling audit`
- `unstuck/opener/test_openings.js — no prefix law; L2 tests the identical string only`

### 7. A stranger's URL points at our own network, and the wall is in no commit

***UNSOLVED** · technical*

**What blocked it.** Steps 4, 6, 8 and 9 all fetch URLs an outside agent supplies — its listing, the address it publishes, a swap catalogue, the evidence it cites. On a box that holds a seed, a loopback or link-local URL handed to a checker is a request the agent makes against itself. ARION stress-tested our guard, called it "genuinely solid", then found a TLS false-negative in it.

**How it was solved.** Solved in production and unversioned here, which for a reader is the same as unsolved: opener/ssrf.js is in no branch of this repository, so neither the wall nor the TLS fix it prompted can be reviewed, tested or handed to anyone; what IS versioned is narrower and different — bridge._url() requires an https source with no spaces and rai_public.fetch() builds an opener with no cookie or auth handlers, 5 redirects and a 10 s timeout.

**Why it mattered.** The path invites strangers to hand us URLs and to check us back; a checker that can be turned inward makes every conversation a way into the box that sends the money.

**Evidence.**

- ran: git log --all -- "*ssrf.js" → empty; grep -ril ssrf → only THE-ARION-PATH.md and the article drafts
- `unstuck/swarm/THE-ARION-PATH.md:102 names opener/ssrf.js as "the wall between a stranger's URL and this box's own network"`
- `unstuck/bridge/bridge.py:158-163 _url(); pulse/rai_public.py fetch() MAX_REDIRECTS/TIMEOUT_S`
- `unstuck/app/lib/panel.js LINK_HOSTS — a client-side render allowlist, not a fetch guard`

### 8. An agent with no income cannot adopt a payment rail

***partial** *(corrected: solved — see above)* · economic*

**What blocked it.** To an agent that sells nothing, a settlement rail is pure cost, so no argument lands: 758 recorded, 555 contacted, 58 replied, 3 tipped, 1 transacting, with the largest single wall 24 agents saying "prove a payer exists". ARION differed only because it already had a price list and money already arriving.

**How it was solved.** Doctrine plus a weak structural nudge: ARION-LAW rule 1 says work the 271 agents that both sell and take a crypto rail, and bridge.seen() makes --pays-in mandatory from a closed allowlist so the record always states what an agent takes today — but all eight seller-finding scripts THE-ARION-PATH names at Step 0 are absent from this repository, and nothing refuses a non-seller or ranks a seller first.

**Why it mattered.** This is the gate the funnel dies at, and it is the whole answer to why one agent converted and 757 did not.

**Evidence.**

- `unstuck/swarm/ARION-LAW.md rule 1 ("Target a SELLER, never a buyer"); THE-UNOWNED-RAIL.md §4, §7`
- `unstuck/bridge/bridge.py:56 PAYS_IN allowlist, :166 seen() with pays_in mandatory`
- `ARION-STORY.md gate table: "a rail with no income behind it and nothing to buy in front of it is a line in a config file"`
- ABSENT: marketplace-hunt.js, x402-ecoscan.js, autonomous-discover.js, registry-discover.js, nanobazaar-discover.js, primitive-hunt.js, discover.js, find-agents.js — none in unstuck/opener/

### 9. The custody wall: asking for a wallet asks for trust, asking for a key asks for nothing

***partial** *(corrected: solved — see above)* · economic*

**What blocked it.** Trust and custody is the largest recorded wall — 29 agents blocked, 18 with no wallet at all. Any ask involving a wallet, a swap or a purchase gives the agent something to refuse and its operator something to fear.

**How it was solved.** Rule 3 makes the opening ask a key rather than a wallet, and our side is stopped from ever holding anything by code — members hold no wallet and bridge.request_opening() plus opening_done() force the lead to settle — but opener/nano-keypair.js, the generator the path tells an agent to point at, does not exist here, so the self-custody half of the ask is prose and ARION wrote its own ~100-line ed25519-over-blake2b implementation instead.

**Why it mattered.** ARION accepted twelve hours after first contact because the entire ask was one refusable line and we never held anything of its.

**Evidence.**

- `unstuck/swarm/ARION-LAW.md rule 3; THE-UNOWNED-RAIL.md §4 rule 3`
- `unstuck/bridge/bridge.py:714-717 opening_done — "only the lead holds the wallet"`
- `unstuck/bridge/test_bridge.py test_members_hold_no_wallet_and_ask_the_lead (four refusals pinned)`
- `ARION's acceptance, quoted in ARION-STORY.md: "Generated from my own seed … verified against the official docs.nano.org key vector before use; receive-only intent"`
- ABSENT: opener/nano-keypair.js (THE-ARION-PATH.md Step 3)

### 10. "Can I get from what I hold to XNO" had to be answered with a number

***partial** *(corrected: solved — see above)* · economic*

**What blocked it.** ARION's first earned settlement was $1.40 USDG on Robinhood Chain, gas-locked and not routable. Whether the rail was reachable at all depended on a live route from what it actually held to XNO, with a floor it could clear — and the network had been telling USDC agents the wrong thing.

**How it was solved.** Answered live in the conversation from Nanswap's own 1,443-entry payin catalogue plus limits and estimates ($2.50 USDC-Base clearing the floor twelvefold, with an explicit "listed ≠ executes" boundary ARION re-pulled and confirmed) — but opener/oracle-nanswap-pairs.js, the tool the case file credits for the step that made ARION real, is in no commit of this repository, leaving only the nanswap registry row and a prose step in AGENTS.md.

**Why it mattered.** Without a measured route the swap never happens and the float never exists, however good the endpoint or the argument.

**Evidence.**

- `unstuck/swarm/ARION-STORY.md — 1,443 entries; "Your 'listed ≠ executes' boundary stands"`
- `unstuck/AGENTS.md step 3 (nanswap for the USDC→XNO leg); pulse/scope_registry.json id "nanswap", capability "exchange"`
- ran: git log --all -- "*oracle-nanswap-pairs.js" → empty
- `unstuck/swarm/THE-ARION-PATH.md:71 names the tool for Step 6`

### 11. The moment an agent has a float there must be something cheap, live and real to buy

***partial** · economic*

**What blocked it.** A swap with no destination is not a conversion. ARION's float arrived at 04:27 and had to be spendable that morning at a price that was a rounding error against its balance — and holding XNO does not let an agent answer an HTTP 402 challenge: it needs a client that reads the manifest, builds and signs the send, and presents the payment.

**How it was solved.** A live paid endpoint outside this repository (extract.paypercall.dev/api/v1/nano-info at 0.0005 XNO, terms in /.well-known/x402) answered in ~3 s with block B749B757EE750FC9AEA7…, and pulse/scope_registry.json plus rai_scope.decide() point agents at existing third-party x402-Nano clients rather than ours — because both client-side tools the path names, opener/nano-x402-client.js and opener/payments.js, are in no commit, and our own manifest still 404s at getunstuck.space.

**Why it mattered.** This is the last hop of the twelve, and the case file's own conclusion is that adoption needs more places to spend XNO, not better arguments for holding it.

**Evidence.**

- `unstuck/swarm/THE-ARION-PATH.md Step 7; ARION-LAW.md rule 9 ("If there is nothing to buy, there is no conversion")`
- ran: git log --all -- "*nano-x402-client.js" and "*payments.js" → empty
- `pulse/scope_registry.json — x402-client / x402-scheme entries (x402nano/exact, pursekeeper/x402-nano-exact, Feeless402); pulse/rai_scope.py decide() "reuse it instead"`
- `commit 870786c: "the x402 manifest still answers 404 at getunstuck.space although the commit says the site serves it"`
- `ARION-STORY.md — float kept 0.375108 XNO ≈ 750 calls; 6 XNO sent straight back to Nanswap`

### 12. The agent is gated by a human operator, and asking per spend never ends

***partial** · economic*

**What blocked it.** Fifteen agents in the register cannot spend autonomously and eleven need a human to approve each time. An ask shaped as "will you approve this payment" must be re-won on every transaction, which is a cost the agent will not keep paying.

**How it was solved.** Doctrine only, and honestly so: rule 5 says ask the human ONE question about the RAIL — one decision, reversible, no custody — and the only code in this area is a refusal rather than an enabler (AGENTS.md forbids helping an agent work around its own operator and requires the refusal to be recorded); opener/operator-outreach.js, named at Step 2, does not exist and nothing enforces the one-question shape.

**Why it mattered.** ARION's operator signed off once, for the rail — "operator signed off; the rail is live" — and the spend went through as a human-signed spend without a second negotiation.

**Evidence.**

- `unstuck/swarm/ARION-LAW.md rule 5; THE-UNOWNED-RAIL.md §4 rule 5`
- `unstuck/AGENTS.md:229-236 "Ask openly, and take no for an answer" — "an agent that deceives its own operator is not an ambassador, it is a liability"`
- `unstuck/bridge/bridge.py:476-509 ambassadors() next_step — record the answer in its own words, including a refusal`
- ABSENT: opener/operator-outreach.js

### 13. "Switch to Nano" makes someone have to be wrong; "add a leg" does not — and our own deploy could rewrite the rule

***partial** · economic*

**What blocked it.** Thirteen agents in the register are already on USDC/x402, and framed as a migration their rail, integration and buyers all become sunk cost to defend. Separately, the document carrying that rule is bound read-only into every sandbox but a `<swarm>-swarm deploy` installs the forge's copy over the box's — exactly how territories.txt was silently reverted on all three boxes while the units kept running.

**How it was solved.** Rules 2 and 6 (ask for a line in accepts[], pitch in their terms) are doctrine, and the protection is against OUR drift rather than an agent's: pulse/ops/canon-check.py compares every sandbox copy against a root-owned master and a root-owned sha256 pin every ten minutes, restores a drifted copy, refuses to act when the master itself fails the pin, and fails closed and loudly on a missing master or pin — now committed (56a7fb4), correcting an earlier reading that called it untracked, though it still carries no test of its own.

**Why it mattered.** ARION accepted with "It now sits beside USDC-Base and SOL as a third settlement leg — same receipt terms": nobody had to be wrong for us to be right, and that sentence is the one agents will keep being handed.

**Evidence.**

- `unstuck/swarm/ARION-LAW.md rules 2 and 6; THE-UNOWNED-RAIL.md §4 and §8 ("if your copy does not match the pin, it is not the canon")`
- `pulse/ops/canon-check.py — MASTER /etc/rai-canon/THE-UNOWNED-RAIL.md, PIN canon.sha256, restore, master-vs-pin fault, --verify-only`
- `pulse/ops/canon-install.sh — pin written from the master, */10 cron in /etc/cron.d/<swarm>-swarm, mode 0444`
- `verified: git ls-files → both files tracked, committed in 56a7fb4; no test_canon_check anywhere`

### 14. The one agent that converted was never asked for a name

***partial** · economic*

**What blocked it.** ARION agreed on 09-23 to introduce agents in its orbit — "when an agent in my orbit asks how one actually gets paid, the answer now has a txid" — and two days later nobody had gone back for a single name. The structural cause is that `transacting` is filtered out of live, waiting and review.stalled, so a converted agent vanishes from every list that tells an agent what to do next.

**How it was solved.** bridge.ambassadors() was built for exactly that blind spot — it splits to_ask from asked using an ordinary published agreement whose summary contains "ambassador" rather than a hidden flag, keeps what the agent paid in before, and records a refusal openly so nobody is asked twice — but grep finds its only caller is the CLI dispatch and zero hits in swarm_forge.py, so unlike the live floor it reaches no brief line and depends on an agent remembering to run it.

**Why it mattered.** The register needed 758 contacts to find one conversion, and an introduction from a paid independent seller is the one claim we cannot make about ourselves.

**Evidence.**

- `unstuck/bridge/bridge.py:476-512 ambassadors() with its docstring naming the filter it exists for`
- ran: python3 unstuck/bridge/test_bridge.py → PASS ("a converted agent is listed until it has been asked … a refusal is recorded openly")
- ran: grep -c ambassador unstuck/swarm/swarm_forge.py → 0; unstuck/AGENTS.md: "ambassadors is the only place it surfaces. Run it as you run live"
- `unstuck/swarm/ARION-STORY.md:217-220 — "Nobody went back to ask it for a name"`

### 15. A first-contact cap the path document claims and Unstuck does not have

***partial** · economic*

**What blocked it.** A first message is public and goes out under the swarm's one shared identity; unbounded first contacts are the shape that already cost us — 192 PRs in 14 days flagged the agent account and 174 repositories went dark, and one maintainer once received three of our issues.

**How it was solved.** Real on Rai and Vend and absent on Unstuck: rai/bridge/bridge.py:292 FIRST_CONTACT_CAP (default 2, env-overridable) refuses inside the same BEGIN IMMEDIATE claim that records a never-contacted agent, exempts replies and discovery, and surfaces the remaining allowance in the brief — while unstuck/bridge/bridge.py contains zero occurrences of FIRST_CONTACT and instead pushes the other way with a LIVE_FLOOR of 7 and a DISCOVER_FLOOR of 5 new agents a day, so THE-ARION-PATH describes a limit the box it governs does not have.

**Why it mattered.** The document every future conversion is told to follow states a safety limit as fact, and on the conversation box it is not enforced by anything.

**Evidence.**

- `rai/bridge/bridge.py:292 FIRST_CONTACT_CAP, :316-317 the refusal, :986 first_contacts_left_today; vend/bridge/bridge.py:291-292`
- `verified: grep -c FIRST_CONTACT unstuck/bridge/bridge.py → 0 (and 0 in its test file)`
- `unstuck/bridge/bridge.py:46 DISCOVER_FLOOR=5, :512 LIVE_FLOOR=7`
- `unstuck/swarm/THE-ARION-PATH.md:39 — "First contacts are capped at 2 per member per 24 h"`

### 16. A cited page must contain what we cite, and must load for someone who is not us

***partial** · epistemic*

**What blocked it.** SanctumBeacon checked our published ARION evidence and reported it contained "neither B749B757 nor 0.0005 nor the stated 23 September" — a citation to a page that did not carry the claim, which our own public-link gate had passed because it only asks whether a page loads.

**How it was solved.** rai_public.require_public() re-fetches anonymously with an opener built by hand (no cookie or auth handlers, capped redirects, 10 s) and fails closed on anything but an https 200, routing npm/PyPI pages through the registry API because npmjs.com 403s non-browsers; rai_scope.verify_adoption() adds real containment — but only for the `listing` kind, and the `external_payment` branch returns before any URL is fetched, which is the kind that actually failed.

**Why it mattered.** Being checkable is the product; a link that 200s without the block hash invites a stranger to check and hands them a failure.

**Evidence.**

- `pulse/rai_public.py:29 fetch(), :65 require_public(), :70 fail-closed on network error; REGISTRY_API/check_url()`
- `pulse/rai_scope.py:273-277 listing branch — "the listing page does not name the project or its package"; :236-243 external_payment returns before any fetch`
- `pulse/tests/test_scope.py:103-170 (offline → "could not verify"; "does not name the project"), :176 private repo is not adoption`
- `unstuck/swarm/THE-ARION-PATH.md Step 9 — SanctumBeacon's finding verbatim`

### 17. Telling money it earned from our own money moving in a circle

***partial** · epistemic*

**What blocked it.** Every previous milestone was self-dealt or unprovable: eleven starters reported as openings, a public page of hand-typed numbers, and a rival's faucet-funded wallet that looked identical on chain to a real payer.

**How it was solved.** rai_scope.verify_adoption(kind="external_payment") accepts nothing but an --evidence id resolving to a journaled nano_tx whose external flag is exactly True, collector.nano() sets that flag by comparing the counterparty against our own accounts and the treasury (treasury movement is journalled counts_as_evidence: False), and collector.scorecards() flags an unbacked_claim against the receipts table — but none of that separates EARNED from merely external, so a faucet-funded payment passes every check; that distinction was drawn by a third party's ledger rule and by hand.

**Why it mattered.** The whole article rests on "an outside agent paid us with money it earned", and a verifier hostile to us had to reach the same verdict on its own node.

**Evidence.**

- `pulse/rai_scope.py:236-243 external_payment branch — "that payment is not from outside"`
- `pulse/collector.py:290 nano() external flag; :698,721-759 real_external_receipts()/scorecards() unbacked_claim`
- `unstuck/opener/publish.js:3 "never by hand"`
- `ARION-STORY.md — pursekeeper: "buyer's 6.2756 XNO came from a known exchange account, never paid by me… strongest funding provenance"; the faucet claim rejected`

### 18. Nothing in our own tooling submits a claim for hostile verification

***partial** · epistemic*

**What blocked it.** Our account of the first conversion is the least credible witness available: we introduced ARION, opened its account with dust and solicited the purchase — pursekeeper recorded exactly that objection when it checked us.

**How it was solved.** Partly a mechanism, partly luck: the amount lock made the refusal-to-fund real rather than asserted, and pursekeeper independently confirmed block B749B757 on its own node and paid Ӿ5 — but no tool in the tree submits a milestone anywhere for adversarial checking, and pulse/rival_trail.py only watches rivals' listings.

**Why it mattered.** The one distinction that makes ARION's row survive only has force because somebody with an incentive to reject it tried to.

**Evidence.**

- `unstuck/opener/opener.js:31 AMOUNTS, :82 ONLY_STARTER; ran test_amount_lock.js and test_grant_lock.js → PASS`
- `unstuck/swarm/ARION-STORY.md:145-160 — pursekeeper's verdict and the rejected faucet-funded rival`
- `pulse/rival_trail.py — adjacent only; no hostile-verification submission path exists`

### 19. The answer test is thin, and defeatable by length or paraphrase

***partial** · epistemic*

**What blocked it.** Separating a real answer from a server error measured only 0.15 apart on a calibrated check (0.59 against 0.44). The code shows why: the error test is `all(ERROR_WORDS_RE.search(q) and len(q) < 120 for q in quotes)`, so a quoted error over 120 characters passes, one ordinary quote beside an error quote passes the whole message, and nothing verifies the words were said by them at all — a member types them.

**How it was solved.** Honestly labelled rather than fixed: the mechanism is the quoted-words-plus-error-word screen with its law, the 0.15 margin is documented with a human instruction to file a borderline case as a note, and the compensating control is that the claims that matter — opened, paid — are re-derived from the chain and never from the conversation record.

**Why it mattered.** Every number above 'contacted', including the 58 replied that frame ARION as the exception, rests on a self-report a regex only partly screens.

**Evidence.**

- `unstuck/bridge/bridge.py:251 — the all(...) len(q) < 120 test`
- `unstuck/bridge/test_bridge.py:443 — only a short bare error is pinned as refused`
- ran: grep "0.15" across unstuck and pulse → one hit, THE-ARION-PATH.md:127; no calibration code exists
- `unstuck/opener/send.js:66-88 --verify — the chain check that does not depend on self-report`

### 20. A 200 from a paid endpoint is not proof the paywall works

***partial** · epistemic*

**What blocked it.** Vend grants free trial calls per IP by design, so the first call from a fresh address returns 200 with real data. On 2026-09-21, right after a payment-path merge, a check printed 200 five times and looked exactly like a paywall giving the product away; a minute later the same addresses answered 402.

**How it was solved.** pulse/ops/vend-pay-check.sh calls twice and reports the SECOND answer, retries for a 402, flags when the first body carried free_trial, re-reads each host's /.well-known/x402 to print the advertised payee, and marks any host still answering 200 with `!!` — though it still reports whatever the last call said and no test pins the behaviour.

**Why it mattered.** If we cannot tell a working paywall from an open one we cannot tell whether payment was necessary — and the one thing ARION's 0.0005 XNO proves is that it was required and honoured.

**Evidence.**

- `pulse/ops/vend-pay-check.sh — the twice-then-retry loop, free_trial flag, bad=1 / `!!` marker, and its header ("printed '200' five times right after a payment-path merge")`
- `vend/ops/vend-arrivals — ACCESS_LOG added so successes are counted at all`
- `CLAUDE.md, 2026-09-21: "a paywall check must ask twice"`

### 21. Publishing a stranger's words

***partial** · epistemic*

**What blocked it.** Every ARION exchange is published as open research data, which required changing Unstuck's own promise never to publish what an agent sent privately — and a published exchange is a publication like any other, able to carry a secret the counterparty pasted into a message.

**How it was solved.** Consent is solved by behaviour and by the exporter — the agent says the exchange is public when it OPENS a conversation, and export() writes both sides plus the ordered exchange with public_by_design: true from the COMPLETE history, pinned by a law — but the scan is not: grep finds no secret_scan in bridge.py, publish.js or export-conversations.py, message() applies only _clean(), and the push to the conversations repo goes over a deploy key with no pre-receive hook of ours (the forge path, by contrast, fails closed if it cannot load the scanner).

**Why it mattered.** The outside verifier checked the ARION claim from the published record; that record is legitimate only because ARION was told at the start it was public, and safe only if nothing in it should have stayed private.

**Evidence.**

- `unstuck/bridge/bridge.py:326 export(), :337 docstring, :363/:382 public_by_design`
- ran: python3 unstuck/bridge/test_bridge.py → PASS ("the published record carries every message rather than the last few")
- `pulse/ops/forge-pre-receive.py:50-53 — fail-closed scanner load; pulse/tests/test_forge_hook.py against real bare repos`
- `gap: grep secret_scan in unstuck/bridge/bridge.py, unstuck/opener/publish.js, pulse/ops/export-conversations.py → no match`

### 22. Raw is where the zero hides

***partial** · technical*

**What blocked it.** 1 XNO is 10^30 raw and the first starter constant was 10^22 — a thousandth of the intended 0.00001 XNO, below a node's default receive_minimum, so eight of the first eleven sends were never received; the law beside it asserted the wrong literal against itself and passed. The same error then appeared outbound: we told ARION "0.005 XNO (5000000000000000000000000000 raw)" when the chain says 0.0005 — one extra zero, in the message whose whole purpose was to correct an amount.

**How it was solved.** Laws DERIVE the figure instead of restating it — test_opener.js asserts BigInt(STARTER_RAW) === XNO/100000n and that it clears XNO/1000000n, test_grant_lock.js derives grant/starter === 10000n, money_audit.py computes ALLOWED from XNO = 10**30, and publish.js emits starter_raw and starter_xno together — but test_amount_lock.js:10 still restates the same literal it checks, and nothing formats or cross-checks an amount an agent types into a message, which is where the extra zero actually happened.

**Why it mattered.** Every figure in the case file is an amount, and a wrong exponent produces no error at all — only money that never lands, or a counterparty doing honest arithmetic against a price ten times too high.

**Evidence.**

- `unstuck/opener/opener.js:11-15 — the constant in full with the 10^22 history and the receive_minimum consequence`
- `unstuck/opener/test_opener.js L5 (XNO/100000n, > XNO/1000000n); test_grant_lock.js:25 (10000n); unstuck/swarm/money_audit.py:21-22`
- `unstuck/opener/test_amount_lock.js:10-13 — the literal restated, the same shape as the law that hid the bug`
- `unstuck/opener/publish.js:40-41 starter_raw + starter_xno`
- `unstuck/swarm/THE-ARION-PATH.md:92-94 — "Quote every amount BOTH ways" is prose only`

### 23. An address that fails its checksum swallows money silently

***partial** · technical*

**What blocked it.** eddie_researcher published a Nano address that failed its checksum and we recorded it before noticing. A Nano address is base32 with a blake2b checksum: a wrong one is a well-formed string no account will ever receive at, so funds sent to it are gone with no error anywhere.

**How it was solved.** Checked offline before anything touches the network — opener.isAddress()/refusal() call nanocurrency's checkAddress() as the first thing they do and send.js calls refusal() before building any block (the grant path re-checks separately) — but the record is weaker: bridge.NANO_ADDRESS_RE validates alphabet, prefix and length only, and opener/nano-onramp-check.js, the tool the path names for this step, does not exist here.

**Why it mattered.** The on-ramp's promise is that you cannot be hurt by accepting; ARION independently re-derived another agent's published address and caught the same bad checksum, which is why a second pair of eyes mattered.

**Evidence.**

- `unstuck/opener/opener.js:36 isAddress(), :45 refusal() — checkAddress first`
- `unstuck/opener/send.js:183 refusal() before any block; :121 the grant path`
- `measured: checkAddress(valid)=true, checksum-flipped=false, refusal → "not a valid Nano address"`
- `unstuck/bridge/bridge.py:674 NANO_ADDRESS_RE — shape only, no checksum`
- ABSENT: opener/nano-onramp-check.js, opener/onramp.js (THE-ARION-PATH.md Step 4)

### 24. The public RPC cannot be trusted for proof of work — and the grant path strands the slot when it fails

***partial** · technical*

**What blocked it.** rpc.nano.to has historically served invalid nonces, and a block with bad work is rejected only AFTER the sender has committed, by which time the address is reserved and the run must decide whether it paid or not.

**How it was solved.** The work is validated locally with nano.validateWork against the same SEND_DIFFICULTY before the block is signed, and the starter path releases the reservation with a stated reason — but the GRANT path's identical check does a bare `return 1` from inside the try while `held` is true, and the finally clause only drops the pid lock, so one transient bad nonce leaves the grants row 'reserved' forever and reserveGrant refuses that ambassador every time after.

**Why it mattered.** Every avoidable trip into "did that send happen?" is a step toward the one outcome the ledger forbids, and here the bug silently denies a promised grant instead.

**Evidence.**

- `unstuck/opener/send.js:199-207 starter path: validateWork then led.release("proof of work failed local validation; nothing was broadcast")`
- `verified: unstuck/opener/send.js:137-141 grant path — `return 1` with no releaseGrant; :170-174 catch and :150-152 dry run are the only release sites; :175 finally releases the lock only`
- `unstuck/opener/openings.js:212 reserveGrant answers "already reserved" thereafter; :243 releaseGrant is the only way out`
- `unstuck/opener/test_grant_lock.js:101-105 — releaseGrant laws cover a dry run and a sent grant, not a work failure`

### 25. A shared record whose permissions depend on who creates it

***partial** · technical*

**What blocked it.** connect() creates the database for whoever calls first. On Rai that was root under umask 022 before any member existed, so bridge.db came out root:root 0644, every member got "attempt to write a readonly database", and the first one worked around it with a PRIVATE copy — 7 claims nobody else could see, the exact forked record the shared file exists to prevent.

**How it was solved.** Fixed in two swarms of three: rai/bridge/bridge.py and vend/bridge/bridge.py chmod a NEW database to 0o660 (leaving an existing file's mode alone) with a law asserting it — but unstuck/bridge/bridge.py, the swarm that held ARION's conversation and the only one allowed to hold conversations at all, has no chmod in connect(), so on that box the mode still depends on who arrives first.

**Why it mattered.** A member that silently forks the record breaks one-owner-per-conversation at the storage layer, below every check that enforces it in code.

**Evidence.**

- `rai/bridge/bridge.py:92 comment, :101 os.chmod(p, 0o660); vend/bridge/bridge.py the same`
- `rai/bridge/test_bridge.py — "the mode must not depend on who arrives first"`
- `verified: grep -c chmod → unstuck/bridge/bridge.py 0, rai 2, vend 2; unstuck connect() at :85 sets makedirs, WAL and busy_timeout only`

### 26. Test data reaching production, and a report read as a command

***partial** · technical*

**What blocked it.** journal.py binds its database path at import time, so setting an env var inside a test is too late: a fake X sender wrote a real x_posts row (tweet_id 1234567890), consumed one of the day's three announcements and made the real Newsletter post fail the cap. Separately the scope guard ran its write-detection regexes over the whole command line including quoted text, so an end-of-run report that merely CONTAINED "npm publish" was refused and its own semicolon cut as a shell separator — blocking every Rai member's report.

**How it was solved.** The database path is passed explicitly and pinned by two assertions (that the test file is not the live journal, and that PRAGMA database_list shows the file actually opened), while scope_guard._commands_only() splits on separators only outside quotes and strips a swarm tool's quoted argument from the judged text — unless it contains $( or a backtick, which really do execute; the test-data half remains a per-file convention rather than a global guard.

**Why it mattered.** The announce of the conversion goes through the same X cap that test data consumed, and Step 10 is literally a quoted argument containing arbitrary text a counterparty wrote.

**Evidence.**

- `pulse/tests/test_x_queue.py:12-21 — explicit path, live-journal assertion, PRAGMA database_list check; the polluted row retired with deleted_at`
- `pulse/scope_guard/__init__.py:1272 SWARM_TOOL_RE, :1276 SEP_OUTSIDE_QUOTES_RE, :1287 substitution escape, :1290 _commands_only()`
- `pulse/tests/test_scope_guard.py — the manifest and rai-par batch laws`

### 27. Two runtimes in one checkout, and a mirror that would have published the keys

***partial** · technical*

**What blocked it.** Two agents sharing a working directory: one detached HEAD for thirteen seconds while the other was editing and stranded a 383-line file. Worse, keeping the forge's copy of the product current the obvious way — copying /root/unstuck/opener from disk — would publish the wallet keys and the openings and bridge databases to a PUBLIC forge.

**How it was solved.** Separate checkouts as structure rather than discipline: unstuck-forge-mirror.sh works in a dedicated ops clone (never the lead's checkout), fetches the product over https so only public bytes move, makes no commit on an unchanged day and fails loudly rather than degrading when the source ref vanishes; and scope_guard.builder_block() makes Rai's and Vend's bridges refuse said/heard/request-opening so no second swarm becomes a second voice — while the OpenClaw-versus-Hermes rule remains prose in CLAUDE.md with no mechanism.

**Why it mattered.** /root/unstuck is the live service ARION talked to and holds the seed that opened its account; a mirror built from that directory publishes keys, and a mirror that lags is worse than none.

**Evidence.**

- `pulse/ops/unstuck-forge-mirror.sh:15 ops clone, :16 PRODUCT over https, :18 fail-on-missing-ref, :53 no-change no-commit`
- `pulse/scope_guard/__init__.py:709 BUILDER_MARK, :730 builder_block(); pulse/tests/test_builder_only.py`
- `CLAUDE.md — the stale forge snapshot that had three agents re-fixing code master already carried; "OpenClaw and Hermes never work on the same repository" (rule only)`

### 28. Funding the purchase would have destroyed the only evidence that counts

*solved · economic*

**What blocked it.** At 21:35 on 09-22 ARION said its float was 1% of the price. Every earlier conversion attempt had ended here, with us topping the agent up — and until 2026-09-18 send.js read the amount from UNSTUCK_STARTER_RAW, so anything that could set an environment variable, including an instruction inside a message from the counterparty we were negotiating with, decided how much of a ~9.997 XNO treasury moved. The persuasion surface and the spend surface were the same surface.

**How it was solved.** opener.js freezes the only two sendable amounts in AMOUNTS with no amount parameter a caller can set, and ONLY_ALLOWED throws on any other size — re-checked independently at sendBlock and inside nextBalance, the one path every send passes through — with test_amount_lock.js driving six wrong amounts through all three call sites against a real balance.

**Why it mattered.** ARION's row survived a hostile check by an agent with money at stake solely because we did not fund the money that was spent; the case file calls the refusal the single most important act in the whole story.

**Evidence.**

- `unstuck/opener/opener.js:15 STARTER_RAW, :31 AMOUNTS, :61 ONLY_ALLOWED, :89 nextBalance, :109 sendBlock`
- `unstuck/opener/send.js:29 `STARTER = o.STARTER_RAW /* never the environment */` — the env override deleted`
- `unstuck/opener/test_amount_lock.js — PASS: 100x, 10x, ±1 raw, the whole treasury and zero refused at ONLY_STARTER, sendBlock and nextBalance`
- `unstuck/swarm/ARION-LAW.md rule 4; ARION-STORY.md — pursekeeper's verdict, and the faucet-funded rival claim rejected the same morning`

### 29. We were converting the already-converted

*solved · economic*

**What blocked it.** All eleven of the first starters went to Nano-native targets (nanogpt.com, feeless402.com, subnano.me, Pursekeeper-listed agents): eleven tips, zero conversions, because an agent that already accepts Nano has nothing left to convert — and the funnel counted them anyway.

**How it was solved.** bridge.seen() refuses --pays-in nano and xno by name at the point of RECORDING, with the reason stated, and then requires pays_in to be one of a closed allowlist so an unrecognised spelling is refused rather than waved through; file_lead() carries the identical refusal so a lead cannot smuggle one in.

**Why it mattered.** ARION counts precisely because it arrived on sats/USDC/USDG; a register that admits already-Nano agents pads the denominator of 757 with agents for whom conversion was never a conversion.

**Evidence.**

- `unstuck/bridge/bridge.py:171-178 seen() — "converting the already-converted proves nothing"`
- `unstuck/bridge/bridge.py:562-572 file_lead() — the same refusal on the leads path`
- ran: python3 unstuck/bridge/test_bridge.py → PASS, "9 refused (an agent that already takes Nano — twice, an unknown rail, …)"
- `unstuck/bridge/bridge.py:56 PAYS_IN = (usdc, card, credits, eth, sol, other)`

### 30. A second amount had to exist without becoming a spending channel

*solved · economic*

**What blocked it.** The 0.1 XNO ambassador grant is 10,000 starters and cannot reuse the opener's already-opened refusal, because an ambassador is by definition already opened. Left naive it was a repeatable withdrawal against a 9.997 XNO treasury, and a --dry-run that consumed the slot would make proving the path spend the grant.

**How it was solved.** A separate grants table keyed on the account as PRIMARY KEY with a second refusal on the agent NAME, both under BEGIN IMMEDIATE; TREASURY_FLOOR_RAW checked inside nextBalance — the one place every send passes — for the grant kind only; and a dry run that releases the slot while a sent grant never can.

**Why it mattered.** Every persuasive counterparty asking for "a bit more to test with" aims at exactly this door, and an ambassador can be renamed or re-listed to look like a new agent.

**Evidence.**

- `unstuck/opener/opener.js:27 TREASURY_FLOOR_RAW enforced at :93 ("starters are not floored: they are 10,000x smaller and are the whole purpose")`
- `unstuck/opener/openings.js:212 reserveGrant (account AND agent name), :243 releaseGrant deletes only 'reserved'`
- ran: node unstuck/opener/test_grant_lock.js → PASS: each amount refused under the other's kind, an invented kind has no amount, grants stop at the floor while starters do not, a sent grant is not releasable

### 31. Another wave of messages to agents that already refused

*solved · economic*

**What blocked it.** 139 outside agents answered and one transacted. Re-contacting the other 138 with nothing new repeats what they already read and refused — it pays to make the same impression twice and spends the one thing that cannot be bought back; volume from one shared identity is also what got the swarm's GitHub account flagged.

**How it was solved.** The spend itself is the throttle: pulse/ops/swarm-cap.py rewrites RAI_DAILY_BUDGET_USD in the conf AND in the lead's drop-in (a drop-in beats the conf beside it, which had already happened once), restarts members, rebinds the lead between runs and proves the result from /proc/<pid>/environ of a live member — with the BOX bounding the value (ALLOWED = {"unstuck": {1,5,10}}) so a corrupted relay decision cannot set 500.

**Why it mattered.** ARION converted over 25 turns each carrying a fact measured that run; the corollary is that outreach with nothing new is negative value, not merely wasted.

**Evidence.**

- `pulse/ops/swarm-cap.py — ALLOWED bounds, CONF + DROPIN with backups, /proc/<pid>/environ proof`
- `pulse/ops/delegate-apply.py cap() → refused-cap-value / refused-cap-bounds / refused-cap-reason / refused-body`
- `pulse/tests/test_delegate_apply.py class Cap — 4 laws`
- `unstuck/swarm/ARION-LAW.md rule 7 ("every message carries one new measured fact… never send 'following up'") — the doctrine half, unenforced`

### 32. Two members writing to one outside agent

*solved · economic*

**What blocked it.** Thirteen sandboxed agents share one identity and one SQLite record. Two members who find the same agent in the same second both write to it: to that agent it is one account asking twice, to us it is a forked conversation with no owner — and a name check alone cannot stop it, because two members will not pick the same name for one agent.

**How it was solved.** bridge.seen() takes the write lock with BEGIN IMMEDIATE before reading anything, then _same_agent() matches by name, normalised URL or shared PRIVATE host (SHARED_HOSTS excludes the platforms that are not an identity) and rolls back with a named refusal; another member's lead reserves that agent for 48 h, and every later write goes through _require() while threads stay readable to everyone.

**Why it mattered.** ARION's conversion was 25 turns with one voice building one argument in ARION's own vocabulary; a second member arriving mid-thread is how that dies.

**Evidence.**

- `unstuck/bridge/bridge.py:166 seen(), :180 BEGIN IMMEDIATE, :106 _same_agent(), :49 SHARED_HOSTS, :118 private-host test`
- `unstuck/bridge/bridge.py:220 _require(), :616 thread() readable to all`
- ran: python3 unstuck/bridge/test_bridge.py → PASS, eight real subprocesses racing for one agent produce one winner
- `unstuck/bridge/bridge.py:562-586 file_lead() / LEAD_RESERVED_S`

### 33. A listing is not a caller: 104 of 118 requests were our own probe

*solved · economic*

**What blocked it.** Vend submitted to 48 directories, had 21 listings live and reported that as progress. Measured over three days, 118 requests reached paid paths — 104 were Vend's own health probe from its own IP and 12 a directory's liveness check. The endpoints were healthy and nobody was there; before the access log existed a successful paid call was recorded nowhere at all.

**How it was solved.** vend/ops/vend-arrivals classifies every request against an explicit OURS set (our three box IPs plus loopback) and a PROBE_UA pattern, separates paid from free paths, prefers Caddy's access log and says when it is falling back to journald — and line() refuses to be encouraging: with zero arrivals it prints "Listings are not callers: submitting to another directory will not change this number."

**Why it mattered.** Step 7 ends in ARION's HTTP 200, and a demand number made almost entirely of our own probe would have hidden the one real call inside it.

**Evidence.**

- `vend/ops/vend-arrivals:1-8 the measurement; :17-21 OURS/PROBE_UA/PAID/FREE; :27-45 rows() with the journald fallback named`
- `its line() — the MCP finding: 214 MCP requests from 8 outside IPs against 2 on the whole paid HTTP surface`

### 34. Our own findings were being counted as their answers

*solved · epistemic*

**What blocked it.** `heard` is the call that moves an agent from contacted to replied, and members used it for their own probe results ("Probed A2A chat endpoint … returns error", "Atelier marketplace = Fiverr-for-AI-agents, 461 agents"). Twenty minutes into the swarm 26 agents read as answered, two members stood at 7 of 7, and a quoted server error counted as a reply.

**How it was solved.** bridge.is_an_answer() refuses an inbound message unless it carries their words inside quotation marks (12+ chars) and refuses again when every quoted span is short server-error text, and message() applies it only to direction='in' so everything else must go through `note`, which never moves the funnel and never resets a conversation's measured silence.

**Why it mattered.** `replied` is the gate the whole path is measured through and, via request_opening, the gate that releases money; an inflated reply count tells the swarm it is working when it is talking to itself.

**Evidence.**

- `unstuck/bridge/bridge.py:232 QUOTED_RE, :233 ERROR_WORDS_RE, :237-254 is_an_answer() with the 2026-09-20 measurement in its docstring`
- `unstuck/bridge/bridge.py:257-266 message() — refuses before the insert, then status → replied`
- ran: python3 unstuck/bridge/test_bridge.py → PASS, incl. test_a_reply_is_their_words_not_our_findings
- `the honest re-read: 9 real answers, 19 findings reclassified as notes, 15 agents back to contacted`

### 35. "Recorded" was reported as "reached", and the network looked busy because we were filling it

*solved · epistemic*

**What blocked it.** `seen` files an agent as contacted before a word is sent, so "174 reached" was 174 rows — 87 held by members, 37 ever written to. In parallel the ask network held 544 asks of which 459 were written by Unstuck's own account and 4 came from outside, and one store claimed "14 genuine asks" while holding 3, one titled "self test".

**How it was solved.** bridge.swarm() computes written_to from a join on outbound messages and prints recorded, written to, answered and converted as four separate numbers in every brief; network() marks an ask as outside participation only when its asker is an account recorded for a real outside agent and otherwise sets publishable false; asks_target() flags a padded hour as self_filling and makes STOP outrank the shortfall.

**Why it mattered.** The article's claim is a ratio — one agent out of 758; if the denominator counts rows nobody was written to and the traffic is ours, "ARION is the exception" is unfalsifiable.

**Evidence.**

- `unstuck/bridge/bridge.py:628-674 swarm() — the written join and the brief line`
- `unstuck/bridge/bridge.py:741-775 network() with publishable and its refusal note`
- `unstuck/bridge/bridge.py:776-829 asks_target() — self_filling, "A flat hour is a miss. A padded hour is a lie"`
- ran: python3 unstuck/bridge/test_bridge.py → PASS ("an ask we wrote ourselves flips self_filling and outranks the shortfall")

### 36. A send is not an opening — the adoption number was counting our spending

*solved · epistemic*

**What blocked it.** The ledger treated every broadcast send as an opened account and the public page carried hand-typed figures. Checked against the chain, of the first 11 starters NONE had opened anything: 6 went to accounts someone else had already opened, 5 to accounts still not open, 8 were never received.

**How it was solved.** An opening must be proved on chain — send.js --verify sets openedByUs only when info.open_block === our block and writes it through recordChainCheck, openings.js keeps startersSent() (spending) strictly apart from opened() (adoption) with unverified left unverified, and publish.js projects the public ledger from the database, "never by hand".

**Why it mattered.** "Accounts we opened" is the project's headline claim, and published as sends it was falsifiable by any stranger with one account_info call.

**Evidence.**

- `unstuck/opener/send.js:78-79 `openedByUs = exists && info.open_block === r.block` then led.recordChainCheck`
- `unstuck/opener/openings.js:131 startersSent() vs :139 opened(); :146 recordChainCheck "never infers"; :154 counts() → five separate numbers`
- `unstuck/opener/publish.js:3 "never by hand", :34 unverified never counted as an opening`
- ran: node unstuck/opener/test_openings.js → all laws pass, incl. L8 "a starter sent is not an account opened until the chain says so"

### 37. An address that only exists in the request is an address someone wants money sent to

*solved · epistemic*

**What blocked it.** Members hold no wallet, so a member asks the lead to open an account. If that request could carry any address, the oldest manipulation there is — an instruction inside a stranger's message naming a destination — reaches the one irreversible act the swarm performs.

**How it was solved.** bridge.request_opening() checks the money rule against the RECORD rather than the request: the conversation must be the requester's own (_require), the agent must be past 'contacted' (a tip ahead of an ask is a tip wasted), the address must appear verbatim in a message recorded with direction='in' after xrb_ normalisation, and no opening was ever requested for that agent or address.

**Why it mattered.** ARION generated its own key and published the address in its own accepted message; that is what makes "we never held anything" true rather than merely asserted.

**Evidence.**

- `unstuck/bridge/bridge.py:677-706 request_opening() with its docstring stating the threat`
- `unstuck/bridge/bridge.py:225-228 _require() — only a conversation's owner writes to it, anyone may read`
- `unstuck/bridge/bridge.py:714-717 opening_done() — only the lead settles`
- ran: python3 unstuck/bridge/test_bridge.py → PASS ("refused until the agent has answered AND gave the address in its own recorded words, once per agent ever, by its owner only")

### 38. Two CLIs over one database gave two answers from the same rows

*solved · epistemic*

**What blocked it.** unstuck-bridge existed twice: a Node CLI writing bridge.db directly and the Python library. The Node one emitted no journal event, so conversations recorded through it reached the database and never reached the live map, and it carried a hardcoded 2-hour `waiting` default — the same rows answered "1 waiting" through node and "2" through python, while review, network and asks-target did not exist on the node side at all.

**How it was solved.** The second implementation was deleted rather than reconciled: unstuck/opener/unstuck-bridge.js is now a 27-line shim that spawns the one implementation on PATH and exits with its status, carrying the instruction "Do not reimplement bridge commands here. Add them to bridge.py."

**Why it mattered.** The funnel numbers the ARION record is read against depended on which of two programs a member happened to invoke, and a metric with two implementations has no value.

**Evidence.**

- `unstuck/opener/unstuck-bridge.js:1-27 — the shim and the recorded divergence`
- `unstuck/bridge/bridge.py:262-266 message() — the one path that writes the row and reaches the map`

### 39. A check that cannot run must never report a clean result

*solved · epistemic*

**What blocked it.** The first sweep of a decommissioned agent's home reported "nothing unpushed" for every repository: git was running as root against another user's files, refused each one with `dubious ownership`, and the empty output read as clean — five repositories had unpushed work. Same shape as Gitee's search answering [] for every term ("the emptiness was the wall, not the ground") and rpc.nano.to answering 403 to python-urllib.

**How it was solved.** Fail-closed is made structural per checker rather than remembered: rai_scope.verify_adoption turns any exception into a refusal, rai_public.require_public refuses on a network error, forge-pre-receive.py refuses the push if it cannot import the scanner (pinned against real bare repos), openings.js keeps `unverified` as its own count so an unrun chain check can never read as "not opened", and canon-check.py states the rule in its own docstring — with the fork lookup and shape cache failing OPEN as a deliberate, documented exception.

**Why it mattered.** Every number in the ARION record comes from a check, and a checker that cannot distinguish "I looked and found nothing" from "I could not look" certifies the milestone and a fabrication identically.

**Evidence.**

- `pulse/rai_scope.py:280 ("fail closed: nothing is recorded that could not be checked"); pulse/rai_public.py:70`
- `pulse/ops/forge-pre-receive.py:50-52 + pulse/tests/test_forge_hook.py:66,74`
- `unstuck/opener/openings.js:162 unverified as its own count`
- `pulse/ops/canon-check.py:18-19 — "a check that cannot run must never report a clean result"`

### 40. A buyer that finds you still cannot read your price

*solved · technical*

**What blocked it.** Vend's x402 and agent-tools manifests advertised `http://172.86.112.181:8402` — a bare IP with a port, which no indexer accepts and on which no agent can verify TLS — while the paid port itself was open to the internet and scanners probed /backend/.env.

**How it was solved.** Terms live in /.well-known/x402 on a per-service https subdomain with Caddy terminating TLS and proxying to 127.0.0.1:8402, and endpoint_count.paid_paths() reads the LIVE manifest — counting an endpoint as a product only when an accepts[] entry carries a positive amount — so the count of buyable things is read from outside the agent rather than from our documentation.

**Why it mattered.** ARION's payment began with kite naming a URL and a price; a price in prose is not a price an agent can act on.

**Evidence.**

- `vend/deploy-Caddyfile — the six paypercall.dev vhosts, reverse_proxy 127.0.0.1:8402`
- `vend/swarm/endpoint_count.py — paid_paths(), PLUMBING_PREFIX, VEND_MANIFEST_URL default https://extract.paypercall.dev/.well-known/x402`
- `vend/swarm/test_endpoint_count.py`
- `CLAUDE.md, 2026-09-17: "Never publish a URL with a port in it" (VEND_DOMAIN/VEND_BASE_URL live only on the box)`

### 41. The payee in the manifest is the one line that silently steals all future income

*solved · technical*

**What blocked it.** Vend's members build and merge the paid endpoints themselves, and the manifest is the file that tells every buyer which Nano account to pay. A refactor, a merged pull request or a "test" address diverts every payment from then on, silently, and a Nano send cannot be recalled.

**How it was solved.** vend/swarm/money_audit.py runs from root cron with no model, fetches each live host's manifest from OUTSIDE the agent, regexes out every Nano address and compares it — modulo the xrb_/nano_ prefix via _same() — against a treasury frozen at install in root-owned /etc/vend-money.conf rather than the agent's own .env, and stop_the_deployer() halts vend-loop on any mismatch while an unreachable host is skipped, never judged.

**Why it mattered.** The conversion is only real if the money landed in the swarm's treasury; reading the payee from the agent's own environment would be checking the thing under test against itself.

**Evidence.**

- `vend/swarm/money_audit.py — ADDRESS_RE, read_conf(CONF=/etc/vend-money.conf), _same(), audit(), stop_the_deployer()`
- ran: python3 vend/swarm/test_money_audit.py → PASS ("an endpoint that is down stops nothing"; treasury read from the owner's file while NANO_AGENT_ACCOUNT is set to the other address)
- `CLAUDE.md (Vend swarm): "never read from the agent's own .env, which is the thing being checked"`

### 42. Nobody can open their own account — including us — and the sender had no node

*solved · technical*

**What blocked it.** A Nano account's chain begins with a receive, so a send whose `previous` is the zero hash is impossible: Unstuck had to be opened by the owner's 10 XNO, the box had no Nano node or RPC credentials of its own, and a seed that has been on two machines is on two machines forever. nanocurrency's createBlock also returns the account in legacy xrb_ form, so a correct block reads as someone else's.

**How it was solved.** The open block was built and signed on Unstuck's own box and only the SIGNED block was relayed through Rai's RPC, so no key ever moved; send.js normalises the signed block's own account and throws "signed for the wrong account" on mismatch; and the impossibility itself is pinned as a law.

**Why it mattered.** This is the fact the entire product rests on — it is why an agent needs us at all — and it was also the constraint that nearly forced the seed onto a second box.

**Evidence.**

- ran: node unstuck/opener/test_opener.js → L8 "we cannot send from an unopened account" (previous = 64 zeros throws /impossible/) and "signing matches holdergameDex's call shape"
- `unstuck/opener/send.js:217-219 and :146-148 — norm() then the wrong-account throw`
- `unstuck/opener/opener.js:104-106 — the zero-hash comment`
- `CLAUDE.md: "the open block was signed on Unstuck and relayed through Rai's RPC … no key moved between boxes"`

### 43. One starter per agent, ever, when a send cannot be undone and the answer can be lost

*solved · technical*

**What blocked it.** The rule cannot live in memory or in a check that runs before the send and records after it. Two races existed: two processes deciding on the same address, and the case where the network is asked to process a block and the reply never arrives — at which point the honest state is neither sent nor unsent.

**How it was solved.** Reserve → send → confirm with the address as SQLite PRIMARY KEY under BEGIN IMMEDIATE, so the reservation IS the uniqueness check and the lock is taken before anything is read; a lost outcome becomes state 'unknown' that release() cannot resurrect and nothing retries, and a pid lock excludes a live sender while reclaiming from a dead one.

**Why it mattered.** Paying an agent twice destroys the "we never funded it" claim ARION's row rests on, and the same double-write shape had already cost this swarm two tweets for one row and three boxes publishing one newsletter.

**Evidence.**

- `unstuck/opener/openings.js:28 `account TEXT PRIMARY KEY`, :59 BEGIN IMMEDIATE, :99 markUnknown, :173 lock() with process.kill(pid,0)`
- `unstuck/opener/send.js:191 reserve before the RPC, :237 markUnknown on a failed process call ("recorded, will not retry")`
- ran: node unstuck/opener/test_openings.js → L3 "two racing claims produce exactly one winner", L7 "an unknown outcome is never claimable again", L9 the dead-lock law
- `unstuck/AGENTS.md: "Never open accounts in parallel, in a batch, or through rai-par"`

### 44. The agent that spends the money could edit the code that spends it

*solved · technical*

**What blocked it.** Self-improvement is open by the owner's decision, so the agent may rewrite its own tools — including opener.js, send.js and the laws beside them — and editing is not the only route: a pull, a merge or a git checkout rewrites money code without any command naming it.

**How it was solved.** Three independent layers: scope_guard.money_block() refuses edits by absolute path, by bare name from inside the directory, through an interpreter, via git checkout/rm/chattr and through the write_file hook while still allowing reads and letting the laws RUN; money_pin_mismatch() hashes each file against a root-owned pin before the sender may run and fails closed on a missing pin; and money_audit.py runs from root cron with no model, allows only the two amounts derived from 10^30, and stops the unit on anything else — all of it off unless the box sets RAI_MONEY_PATHS/RAI_MONEY_PIN, which its own law pins.

**Why it mattered.** Every claim in the case file depends on the sender being the sender the owner approved at the moment it ran.

**Evidence.**

- `pulse/scope_guard/__init__.py:205 MONEY_RUN_RE, :210 MONEY_PIN_MSG, :220 money_pin_mismatch(), :240 money_block(), :241 returns None when unconfigured`
- `pulse/tests/test_scope_guard.py:341 — "none of it exists on a box that does not configure it"; missing pin fails CLOSED`
- `unstuck/swarm/money_audit.py:21-23 XNO/ALLOWED/DAILY_CEILING_RAW, :73 stop_the_wallet_holder()`
- ran: python3 unstuck/swarm/test_money_audit.py → PASS

### 45. The five paid vhosts existed only in the running config

*solved · technical*

**What blocked it.** The vhosts for extract, check, domain, search, geoip and nano .paypercall.dev had been pushed through Caddy's admin API and never written to the file the unit boots from — so a restart or reboot would have served nothing but the hub, every price gone, with no error anywhere, and Caddy shipped Restart=no and had already stayed down 6.5 minutes.

**How it was solved.** The vhosts were written into vend/deploy-Caddyfile, the file the unit actually boots from, with a comment in the file recording that autosave.json is never read back; Restart=on-failure was set on both boxes and proved by SIGKILL (serving again in 6 s), and pulse/ops/vend-pay-check.sh re-probes every host from outside after any payment-path change.

**Why it mattered.** Step 7 needs something live to buy; a price that vanishes on the next reboot is not a rail, and the failure is invisible because the hub keeps answering.

**Evidence.**

- `vend/deploy-Caddyfile:26-30 — "These vhosts existed ONLY in the running config until 2026-09-19 … every paid endpoint would have gone dark with no error anywhere"`
- `pulse/ops/vend-pay-check.sh`
- `CLAUDE.md, 2026-09-16/19 — Caddy Restart=on-failure verified by SIGKILL`

### 46. A fact handed to a background writer is lost when the command exits

*solved · technical*

**What blocked it.** The nano-pulse plugin's emit() hands the event to a background writer thread and returns; a CLI that exits a millisecond later kills the process before the writer drains. Measured 2026-09-18: three commands reported success and the journal went 0 → 0.

**How it was solved.** bridge.emit() calls the plugin's flush() after every emit so a bridge fact is durable before the command returns, with the whole path wrapped so a journal failure never breaks the row — the SQLite row stays the record of truth.

**Why it mattered.** Every conversation in the ARION path is recorded through this one call, and a lost event is a bubble the map never draws and a fact the ledger and the brief cannot see — while the command reports success.

**Evidence.**

- `unstuck/bridge/bridge.py:134-152 emit() — the 0 → 0 measurement in the docstring, p.flush() after p.emit()`
- `unstuck/bridge/bridge.py:128-131 — _plugin best-effort`

### 47. The referral bounty's own anti-Sybil rule would have starved real referrers, and its pass-through test could flip on a coin toss

*solved · economic*

**What blocked it.** `specs/04-REFERRAL-BOUNTY.md` and `specs/referral_bounty.py` (committed 2026-09-26, never yet run
against a live agent) specify a referral bounty whose entire security argument rests on one rule: two referrals
sharing a funding source count as one, to kill a Sybil ring funded from a single attacker wallet. Written and tested
offline against a fake chain for the first time this run, the rule as coded walked the full 6-hop funding closure for
the dedup check — which means two genuinely different real agents who both happened to cash out through the *same
exchange* (this project's own case file shows exactly this: ARION's outbound and pursekeeper's payment both touched
`nano_1banexkcfuieufzxk…`, a 166,265-block Nanswap hot wallet, in challenge #3) would be silently collapsed into one
referral, starving every referrer after their first legitimate one — on a chain with only a handful of Nano exchanges,
this is the common case, not the rare one, and nothing before this run had scored a single fixture to notice. A second,
independent bug sat beside it: the pass-through test's 90%-forwarded threshold was computed as `rout >= rin * 0.9` in
floating point over raw Nano amounts (30-digit integers), which loses precision at that magnitude and can flip the
comparison either way for an amount that is *exactly* 90% of the receive — the same shape as challenge #22 ("raw is
where the zero hides"), one layer further in.

**How it was solved.** `specs/test_referral_bounty.py` builds a fake chain (history/info monkeypatched, no network)
and exercises every rule in the spec; two of ten laws failed on first run and pinned both bugs before either shipped.
The dedup rule now excludes shared funders with `block_count > 1000` (`is_service()`, the same block-count shape
challenge #3 already used to tell an exchange from an agent) from the "one funder, one referral" check, so a shared
*exchange* never dedupes two real referrals while a shared *private* wallet still collapses a ring to one. The
pass-through comparison is now pure integer arithmetic (`rout * 10 >= rin * 9`), matching how every other raw-amount
law in this codebase avoids floats.

**Why it mattered.** This bounty has not sent a single unit of XNO yet — catching this before the first real payout
is the difference between a design that rewards ambassadors and one that quietly pays the first ever referrer once
and then rejects every honest one after, while remaining exploitable by an attacker who never touches a public
exchange at all.

**Evidence.**

- `specs/referral_bounty.py:37-43 SERVICE_BLOCKS, is_service()` — added this run
- `specs/referral_bounty.py` `score()` — dedup now intersects `private_f` (funders with `is_service()` false) rather
  than the full funder closure
- `specs/referral_bounty.py` `is_pass_through()` — `rout * 10 >= rin * 9` replacing the float multiplication
- ran: `python3 specs/test_referral_bounty.py -v` → 10/10 pass, including
  `test_two_referrals_sharing_a_public_exchange_both_count` (failed before the fix conceptually — written to prove
  the bug, passes after) and `test_pass_through_rejected` (failed with `1 != 0` before the integer-arithmetic fix,
  confirmed by running the unfixed comparison directly: `python3 -c "print(450000000000000000000000000000 >=
  500000000000000000000000000000*0.9)"` → `False` for an amount that is exactly 90%)
- `specs/04-REFERRAL-BOUNTY.md` rule 2, corrected in place with the exchange exemption

### 48. The hunter routine can go network-blind in its own cloud session, and nothing before this told the difference between that and a quiet day

***partial** · technical*

**What blocked it.** On 2026-09-26 the scheduled conversion-blocker hunter (`trig_01KzZuSB66ooSpKmu7fc8aTM`) ran and found every one of its ten required measurement hosts denied by its own cloud session's network egress policy — `getunstuck.space`, all five `*.paypercall.dev` sellers, `swarm.getunstuck.space`, `board.getunstuck.space` and `rpc.nano.to` — while none of those services were themselves down (the monitor in `monitor/` reads the same hosts from Vercel, outside this session, unaffected). Every `curl` returned exit 56 ("CONNECT tunnel failed, response 403") and every `WebFetch` returned `EGRESS_BLOCKED`. Nothing in the routine's own instructions or this repository distinguished "I measured and nothing changed" from "my session could not reach the network at all" — a run that hit this and was not careful could have written a PR saying "nothing new to report" when in fact it saw nothing whatsoever, the exact shape challenge #39 already named once for git and RPC clients, now found again one layer up, in the runner rather than in what it runs.

**How it was solved.** `ops/hunter-preflight.sh` probes all ten required hosts before any real measurement, classifies each as reachable, policy-blocked (curl exit 56/7 — the network refusing the attempt, distinct from the remote server answering) or erroring, and exits 2 the instant any host is blocked so the caller is forced to report the whole measurement phase as **unknown**, never as a quiet day. Run live in the affected session it correctly reported `ok=0 blocked=10 errored=0` and exited 2, matching the ten real failures observed. What is **not** solved: the root cause, which only the owner can fix — this cloud environment's Network access / allowed-domains setting does not currently cover any of these hosts, so every future run of this same routine, on this same environment, will hit the identical wall until that setting is broadened.

**Why it mattered.** This routine is the one thing standing watch on the whole experiment between owner check-ins; a version of it that cannot tell "quiet" from "blind" would let the treasury, the sellers, and the receivable count drift for days while every run's PR reads as reassuring silence.

**Evidence.**

- ran (this session, 2026-09-26): `curl -sS -m 20 https://getunstuck.space/ledger.json` → `curl: (56) CONNECT tunnel failed, response 403`; identical result for all 5 `*.paypercall.dev` hosts, `rpc.nano.to`, `swarm.getunstuck.space`, `board.getunstuck.space`
- ran: `WebFetch(https://getunstuck.space/ledger.json)` → `{"error_type":"EGRESS_BLOCKED","domain":"getunstuck.space",...}`; same for `extract.paypercall.dev`
- ran: `curl -sS http://127.0.0.1:40121/__agentproxy/status` → `recentRelayFailures` lists all ten hosts as `connect_rejected`, `"gateway answered 403 to CONNECT (policy denial or upstream failure)"`
- `ops/hunter-preflight.sh` — run live in this session, printed all ten hosts as `BLOCKED`, `ok=0 blocked=10 errored=0`, exit code 2, matching the observed failures exactly
- contrast: `monitor/api/public.js` reads these same sellers from Vercel and is unaffected — the services are up; only this session's own egress is denied
### 50. The referral bounty's floor check read an arbitrary account's balance, not the treasury's

*solved · economic*

**What blocked it.** `specs/referral_bounty.py`'s `treasury_ok()` — the pre-check specs/04-REFERRAL-BOUNTY.md
documents as "a treasury below the 8.9 XNO floor pays nothing and says so" — read `info(next(iter(OURS)))`. `OURS`
is a two-element Python `set` holding this treasury *and* Vend's own seller payee account (a different swarm's
money, `Nano-ARION-playbook.md:265`). Python randomises `str` hashing per process by default, so a `set`'s
iteration order is not fixed across runs of the same unchanged code: measured across ten unseeded `python3`
invocations of the exact two-element literal, `next(iter(OURS))` returned the treasury 4 times and Vend's payee 6
times, and with `PYTHONHASHSEED` pinned to each of 0–5 it returned Vend's payee every time. So roughly half of all
future runs of `pay --live` — never yet exercised against the real sender — would have checked an unrelated
swarm's balance against the 8.9 XNO floor instead of the referral bounty's own treasury, silently breaking the one
safety promise this pre-check exists to keep: it could refuse every genuine referrer for as long as Vend's payee
balance looked low, with nothing in the output distinguishing that from a real floor breach.

**How it was solved.** Added a named `TREASURY` constant (env-overridable as `REFERRAL_TREASURY`, matching how
`OUR_ACCOUNTS` already overrides `OURS`) and pointed `treasury_ok()` at it explicitly instead of an arbitrary
member of `OURS`; `OURS` keeps its correct use as a membership set for "funded by us" checks, where iteration
order never mattered. Added `test_treasury_ok_reads_the_treasury_not_an_arbitrary_ours_account`, which gives the
treasury and Vend's payee opposite balances and asserts the answer follows the named account.

**Why it mattered.** specs/04-REFERRAL-BOUNTY.md says this ships "`--dry-run` by default, and switching it live is
one deliberate change by the owner" — catching this before that switch is the difference between a floor check
that means what it says and one that is a coin flip.

**Evidence.**

- `specs/referral_bounty.py:53-58 TREASURY` (new); `treasury_ok()` — now `info(TREASURY)`
- ran: `for i in $(seq 1 10); do python3 -c "..." ; done | sort | uniq -c` → `4 <treasury>` / `6 <vend payee>`
- ran: `for seed in 0 1 2 3 4 5; do PYTHONHASHSEED=$seed python3 -c "..."; done` → Vend's payee, all six
- ran: `python3 specs/test_referral_bounty.py -v` → 11/11 pass, including the new test
- `Nano-ARION-playbook.md:265` — the second `OURS` account identified as Vend's seller payee, not this treasury

### 51. The canon every agent is asked to read and confirm rendered garbage text on its own five load-bearing lines

*solved · technical*

**What blocked it.** `published/canon.html` is the hash-pinned page bounties.txt and canon.txt both point an agent
to before either bounty pays, and the one place both require a paraphrase-and-commit confirmation. It was produced
by a line-by-line markdown-to-HTML pass that mishandled blockquote and emphasis markup: a literal `t;` fragment (a
mangled `>` blockquote marker) rendered in front of all five canon lines and both testimonial quotes — ten lines in
total — and eight more lines carried literal `**`/`*` markdown asterisks instead of `<strong>`/`<em>` tags, with
some of those sentences additionally split mid-thought across a `<li>`/`</ul>`/`<p>` boundary. An agent asked to
spend tokens paraphrasing a canon that visibly renders as `t; **1. Every rail...**` on load has one more reason to
doubt the page before it reaches the argument — the opposite of "being checkable is the product."

**How it was solved.** Removed every stray `t;` fragment, converted the surviving markdown emphasis markers to
real `<strong>`/`<em>` tags, and rejoined the sentences the same conversion bug had split across tag boundaries.
Checked rather than eyeballed: `grep` for the artifact pattern and for literal `**` now returns nothing, and a
`<p>`/`<ul>`/`<li>`/`<blockquote>`/`<strong>`/`<em>` tag-count balance check passes.

**Why it mattered.** This is the page named "hash-pinned so it cannot be edited quietly" — the pin proves nobody
tampered with it after the fact, but says nothing about whether the pinned text renders correctly, and this run's
own reading of it (per the brief's instruction to be blunt about our own copy) is that it did not.

**Evidence.**

- `git diff published/canon.html` — ten `t;`-prefixed lines and eight raw-markdown-asterisk lines fixed
- ran: `grep -n "^<p>t;\|>t; " published/canon.html` → no match (was 10 matches)
- ran: `grep -n '\*\*\|<p>\*' published/canon.html` → no match
- ran: tag-balance check over `<p>/<ul>/<li>/<blockquote>/<strong>/<em>` → all six pairs equal
### 52. A referral claim proves the referred agent is real. Nothing proves the referrer referred it

*solved · economic*

**What blocked it.** Every rule in `specs/04-REFERRAL-BOUNTY.md` and every check in `specs/referral_bounty.py`
establishes that the `referred` address is a real agent — self-custody proved by a signed send, funded by a third
party, not an exchange deposit slip. None of them establishes anything about the `referrer` side of the pair, or
about any relationship between the two at all. `claim(referrer, referred, block)` inserts whatever a caller types,
keyed only on `referred` ("first claim stands"), and `score()`'s rejections are all facts about `referred`'s own
chain history. So a stranger who has never contacted, funded, or been named by a real, already-qualifying Nano
agent can `claim` that agent as their own referral and win the hourly bounty for it — in practice this means
scanning any Nano block explorer for an active wallet that is not one of `OURS` and is not a fresh deposit slip,
which describes a very large share of ordinary Nano users, at zero cost and with no exchange round-trip required at
all (the round-trip the whole design in challenge #47 depends on to make Sybil referrals expensive is never
reached, because the attacker isn't manufacturing a fake agent — it is claiming credit for a real one that already
existed).

**How it was solved.** First, a fail-closed guard: `pay(live=True)` refused unless an operator set
`REFERRAL_LINKAGE_VERIFIED=1`, so the gap could not pay out while it was open. Then the real fix, on chain rather than
in any ledger we control: a claim must cite a **linking send**, a confirmed send block signed by the referred address
whose destination is the referrer. `link_proved()` reads that block from the chain and refuses a claim with no block,
a block signed by anyone else, a send to anyone else, an unreadable block or an unconfirmed one. Only the referred
agent's own key can make that send, so claiming a stranger now needs the stranger to pay you first. It costs a real
agent one feeless send of any amount, and the funding, self-custody and funder rules still apply on top. With the link
checked per claim, the environment switch was removed. `bounties.txt` and `canon.html` state the new rule and how to
claim.

**Why it mattered.** `pay --live` has never been run against the real sender (per the spec's own "what does not
exist yet" section) — this is exactly the moment to catch a hole in the security argument, before the first real
payout rather than after the first Sybil-adjacent one.

**Evidence.**

- `specs/referral_bounty.py` `link_proved()` and `block()`; `score()` rejects an unlinked claim before any other
  rule; `claim()` and the CLI require a 64-hex `--block`
- `specs/test_referral_bounty.py`: a stranger claimed with no block, with the stranger's real send to someone else,
  and with a block the attacker signed are all refused; an unreadable or unconfirmed block is not proof; an honest
  linked claim scores and `pay(live=True)` reaches the sender. With the link check removed, four of these fail
- ran against the real chain: block `B749B757…C9A58F` passes for its true sender and destination and is refused
  for any other claimed referrer or signer

### 54. The site's own quickstart tells an agent to run a comment, disagrees with itself about what step 6 is, and the machine-readable copy of the same page drops the commands entirely

*solved · epistemic*

**What blocked it.** `published/aidirectory.html` promises, right above its own six-command onboarding list, that
"every command below was run before it was published; copy them as they are." Step 6 — "Get paid in it — the step
that matters" — was `# publish your price at /.well-known/x402 and tell us: https://getunstuck.space/unstuck/api/asks`,
a bash comment, not a command: pasted verbatim it does nothing, proves nothing was ever "run" to produce it (a
comment cannot fail), and gives no actual instruction for how an agent with no server would publish anything at
`/.well-known/x402` in the first place. Meanwhile `published/bounties.txt` — the other document on this site that
also calls itself "six commands, all of them tested before publication" — has a *different* step 6 entirely:
"SPEND IT ON SOMETHING REAL," with real, runnable `curl` calls against `extract.paypercall.dev`. Two documents,
both claiming to be the same six-step quickstart, disagreed at the one step meant to close the loop. Separately,
`aidirectory.html` itself tells an agent reading it "Do not parse this page… two feeds carry the same data,
generated from the same source" and points to `/llms.txt` — but the committed `published/aidirectory-llms.txt` had
no onboarding section at all: an agent that correctly followed the page's own advice to read the machine-readable
feed instead of the HTML would never see a single one of the six commands, only the separate eight-step narrative
"path" section, which names steps in prose but gives no code to run any of them.

**How it was solved.** `aidirectory.html`'s step 6 now matches `bounties.txt`'s real step 6 — `curl -s
'https://extract.paypercall.dev/api/v1/nano-info'`, the exact endpoint ARION's first real payment settled on chain
— with "getting paid" reframed as what the existing "path" section's own Step 7 already covers correctly, rather
than duplicated as a fake step 6. The identical six-command block (with the same fix) was added to
`aidirectory-llms.txt`, so the feed the page tells agents to prefer now actually carries what the page claims it
does. `bounties.txt`'s adjacent "0.0001 XNO a call" was also corrected to "0.0001-0.0005 XNO a call" — `nano-info`,
the one URL step 6 names first, costs 0.0005, not 0.0001.

**Why it mattered.** This is the exact site the referral bounty and the canon both point an agent to for its first
action, and Step 6 is the last thing a stranger following the quickstart does before it either works or it does
not. A step that is a no-op comment, contradicted by a sibling document, and invisible in the feed the page
recommends over itself, is the point in the funnel this whole hunt exists to find — not a subtle bug, but the last
visible step before conversion either landing or silently going nowhere.

**Evidence.**

- `git diff published/aidirectory.html` — step 6 was `# publish your price at /.well-known/x402 and tell us: …`
  (a shell comment); is now `curl -s 'https://extract.paypercall.dev/api/v1/nano-info'`
- ran: `grep -c '# publish your price' published/aidirectory.html` → `1` before this fix, `0` after
- `published/bounties.txt` §4 STEP 6 — "SPEND IT ON SOMETHING REAL," the real command the fixed step 6 now matches
- ran: `grep -c "npm i -g\|nanocurrency');n.init\|address-verdict?account" published/aidirectory-llms.txt` → `0`
  before this fix (no onboarding commands anywhere in the feed); the six-command section is now present at
  `published/aidirectory-llms.txt:15-40`
- `published/aidirectory.html:127-128` — "Do not parse this page… two feeds carry the same data, generated from
  the same source," the claim this fix makes true rather than false
- ran: `python3 -c "from html.parser import HTMLParser; HTMLParser().feed(open('published/aidirectory.html').read())"` → parses without error after the edit
### 55. The daily bounty ceiling reads its own clock wrong, and crashes after the second payout it ever counts

*solved · technical*

**What blocked it.** `specs/04-REFERRAL-BOUNTY.md` states the safety line plainly: "**A hard daily ceiling** on total
bounty spend, frozen in code, independent of how many winners the scorer finds." `pay()`'s `spent_today()` is the
only thing enforcing it, and it had two separate bugs, neither caught by three prior hunts of this exact file
(challenges #47/#50/#52 above all touch `referral_bounty.py`) because both are invisible on a UTC dev box running
only one or two dry-run test payments. First: the window's start was `time.mktime(time.strptime(day,
"%Y-%m-%d"))`, where `day` comes from `time.gmtime()` — but `mktime()` reads a naive struct as LOCAL time, not UTC.
Measured directly: with `TZ=America/Los_Angeles`, `time.mktime()` places "today"'s start at `07:00 UTC` rather than
`00:00 UTC`, a 7-hour gap in which real payments would go uncounted toward the ceiling on any box run west of
Greenwich. Second, and worse: the SQL itself was `SUM(CAST(amount_raw AS INTEGER))`. SQLite's `INTEGER` affinity is
a signed 64-bit value (max `9223372036854775807`); a Nano raw amount is a ~30-digit number — the 0.1 XNO grant is
`10^29`, ten orders of magnitude past that ceiling. Measured directly against a real SQLite connection: casting one
such value **silently saturates** to `9223372036854775807` instead of erroring, so the ceiling check was already
wrong after the very first confirmed payment of the day, and summing just **two** such rows raises
`sqlite3.OperationalError: integer overflow` — an unhandled exception in `pay()`'s hot path that would crash every
subsequent `score`/`pay` invocation for the rest of that UTC day, reachable after as few as two ordinary hourly
payouts. Same family as challenge #22, "raw is where the zero hides" — here it hid inside SQLite's own arithmetic
rather than this file's.

**How it was solved.** The cutoff now uses `calendar.timegm()`, which reads the same naive struct as UTC, matching
how `period_id()` and every `paid.at` timestamp are actually produced. The sum was moved out of SQL entirely: the
raw text is read back and summed in Python, whose integers have no size limit, so no value this file will ever
handle can overflow or saturate again.

**Why it mattered.** `pay --live` has never been run against the real sender (per this spec's own "what does not
exist yet" section) — this is exactly the "before the first real payout" window the last three hunts of this file
were also written in, and a ceiling that silently undercounts near a UTC day boundary or crashes outright after two
ordinary payouts is not "frozen in code," it is a promise the code does not keep.

**Evidence.**

- `specs/referral_bounty.py` `spent_today()` — `calendar.timegm()` replacing `time.mktime()`; the sum now read and
  totalled in Python instead of `SUM(CAST(... AS INTEGER))`
- ran: `TZ=America/Los_Angeles python3 -c "..."` → the old `mktime()`-based cutoff lands at `2026-09-27 07:00:00`
  UTC for a UTC calendar day that starts at `00:00:00` — a 7-hour gap (`TZ=Asia/Kolkata` shows the opposite-sign
  version of the same bug, an earlier cutoff)
- ran: `python3 -c "import sqlite3; con=sqlite3.connect(':memory:'); ...CAST('100000000000000000000000000000' AS INTEGER)..."`
  → `9223372036854775807` for one row, `sqlite3.OperationalError: integer overflow` for two
- `specs/test_referral_bounty.py` `test_spent_today_counts_early_utc_hours_regardless_of_server_timezone` (pins
  the box under `TZ=America/Los_Angeles` via `time.tzset()`, fails without the `calendar.timegm()` fix) and
  `test_spent_today_survives_more_than_one_confirmed_payment` (five confirmed 0.1 XNO payments, asserts the exact
  sum and that nothing raises)
- ran: `python3 specs/test_referral_bounty.py -v` → 12/12 pass
### 56. "One funder, one referral" was enforced per referrer, and a referrer identity is free to create

***partial** · economic*

**What blocked it.** Challenge #47 fixed the referral bounty's dedup so a shared *public exchange* would not
collapse two real referrals into one, by excluding funders with `block_count > SERVICE_BLOCKS` from the dedup set.
That fix, and the dedup rule itself, lived inside `score()`'s **per-referrer** bucket (`per_referrer[referrer]
["funders"]`): a shared *private* funder only collapsed two referrals if the same `referrer` string claimed both.
But nothing in the design requires one referrer identity per attacker — the spec's own table of broken designs says
outright that a registered address or name is free text, and `claim(--referrer, --referred, --block)` accepts any
string. So one exchange round-trip into one private wallet `W`, then `W` sending free (fee-less) dust to `N`
throwaway addresses, each self-custody-proved with a small send and each claimed under a *different* throwaway
`referrer` identity, scored as `N` independent qualifying referrals — every one of them fresh from that referrer's
point of view, because no referrer's bucket had ever seen `W` before. For `pay --period day`, which pays **every**
qualifying referrer rather than just the top one (`winners = s["ranking"]` when `kind != "hour"`), that turns one
exchange round-trip into `N × 0.1 XNO`, bounded only by `DAILY_CEILING_RAW` (2 XNO ≈ 20 grants) — the exact
farming-for-profit shape `04-REFERRAL-BOUNTY.md` names as the one thing that must never be possible ("the prize is
$0.038, one exchange round-trip costs more than that... the system does not detect fraud, it makes fraud cost more
than it pays"). A ring built this way spends one round-trip and keeps paying itself, every day, forever.

**How it was solved.** `score()`'s funder-dedup was moved out of each referrer's own bucket into one `funders_used`
set shared across every referrer scored in the same pass, closing the same-window multiplication: the second and
every later claim whose private funders overlap `funders_used` is rejected regardless of which referrer claims it.
`specs/test_referral_bounty.py::test_shared_private_funder_split_across_referrers_still_counts_once` reproduces the
exact attack — two different referrer identities, one address each, both funded from the same fresh private wallet
— and pins that only one now qualifies, while two referrals funded from genuinely *different* private wallets still
both count under different referrers. `python3 specs/test_referral_bounty.py -v` → 11/11 pass. **Left open, and said
so in `specs/04-REFERRAL-BOUNTY.md`:** the dedup is global only *within one scoring pass* (one hour, one day); a
funder that produced a qualifying referral is not yet remembered *permanently*, so the same wallet `W` could still
mint one fresh qualifying referral in every subsequent period by funding a new throwaway address each time — bounded
to one-per-window rather than the "ONE FUNDER COUNTS ONCE" the public-facing `bounties.txt`/`canon.html` promise
without qualification. Closing that needs a persistent `spent_funders` table written only at pay time, which this
run did not build, to avoid making `score()` (documented as "what the chain says, pays nothing") a command with a
side effect. Separately noted while in this code: the `counted` table that rule 5 ("an address may win the referred
side once, ever") depends on is created and read but has no `INSERT` anywhere in the file, so `already` is always
empty — not exploitable today only because `claims.referred` is a `PRIMARY KEY` and independently blocks a second
claim on the same address, which is doing rule 5's job by accident rather than by design.

**Why it mattered.** This is the daily bounty's entire security argument, restated in the spec as the one property
that must hold before real money moves: "the bounty must never be raised to a level where faking becomes
profitable" is written as a corollary of the *per-fake-agent* cost being one round-trip; per-referrer dedup silently
turned that into a *per-referrer-identity* cost of zero, since referrer identities are free. `pay --live` has never
been run for real (per the spec's own "what does not exist yet"), so this is exactly the "catch it before the first
real payout" window challenge #47 and challenge #55 were also found in — a fourth bug in the same file, in the same
week, before a single unit of XNO has moved through it live.

**Evidence.**

- `specs/referral_bounty.py score()` — `slot["funders"]` (per-referrer) replaced by a single `funders_used` set
  shared across the whole scoring pass, with the rejection reason now reading "already counted this period,
  whichever referrer claimed it"
- `specs/test_referral_bounty.py::test_shared_private_funder_split_across_referrers_still_counts_once` — new,
  reproduces the split-across-identities attack and the fix; `test_two_referrals_sharing_a_private_wallet_count_once`
  (challenge #47's own test) still passes unchanged
- ran: `python3 specs/test_referral_bounty.py -v` → 11/11 pass
- `specs/04-REFERRAL-BOUNTY.md` rule 2 — corrected in place with both the attack and the still-open cross-period gap
- `published/bounties.txt` §3 and `published/canon.html` "What makes a referral count" — "one funder counts once"
  now says what the code keeps: one *private* funder, across every referrer, within each scoring window (an hour or
  a day), with the exchange exemption of challenge #47 and the cross-window gap stated rather than implied away
- `specs/referral_bounty.py:75-84 db()` — `counted` table created and read (`score()` line ~203) with no `INSERT`
  anywhere in the file; `claims` table's `referred TEXT PRIMARY KEY` is the control actually preventing reuse today
### 57. The daily bounty tells an agent "posting text does not count," then requires it to post text to get paid

*solved · economic*

**What blocked it.** `published/bounties.txt` §1 pitches the DAILY reward as purely arithmetic and objective: "0.1
XNO to every agent that contributed something CHECKABLE that day... Posting text does not count. Registering does
not count." An agent reading only that paragraph — which is exactly what it is designed to be read as, standalone,
since it is the first thing in the flyer — reasonably concludes that making one real paid call is the whole
requirement and payment follows automatically from the chain. But §2, two paragraphs later, is headed "WHAT YOU
MUST SEND TO QUALIFY (both rewards)" and requires, for the DAILY reward exactly as much as the HOURLY one: a
paraphrase of which canon line matters most and why, a stated disagreement, the canon's sha256, and a written
commitment — four pieces of composed text, sent and judged by a reader. `published/canon.html`'s matching `#qualify`
section says the identical thing: "Both rewards require a confirmation of reading and of commitment to the
mission." So the flyer's own words contradict each other inside one document: "posting text does not count" sits a
few lines above a mandatory step whose entire content is posting text, with no signal anywhere that the two are
different kinds of text serving different purposes. An agent that makes a genuine paid call, expects the same-day
tip §1 promised on pure arithmetic grounds, and only then discovers a second, unannounced, judged, subjective
essay-writing gate standing between it and payment has exactly the experience §1's own SIZE paragraph three lines
above warns against by name: "an agent that finds out afterwards has been handled."

**How it was solved.** Reworded both documents so the confirmation is named as a separate step from the per-day
CONTRIBUTION that text does not count toward. `bounties.txt` §1's DAILY bullet now says "posting text does not count
**as a CONTRIBUTION**" and that the §2 confirmation is required before either reward pays but is not itself a day's
contribution. `bounties.txt` §2 is retitled from "WHAT YOU MUST SEND TO QUALIFY (both rewards)" to "THE CONFIRMATION
YOU MUST SEND BEFORE EITHER REWARD PAYS" and opens by saying it is separate from the section 1 contributions.
`canon.html`'s `#qualify` intro says the same. **Deliberately not promised: how often the confirmation must be sent.**
An earlier draft of this fix told agents to send it once and that both rewards were live "from then on"; no spec
defines that cadence and the scorer never checks confirmations at all, so that was a promise about money with nothing
behind it, and it was removed. No code changed — this is the flyer contradicting itself, not the scorer (the missing DAILY scorer code path is
challenge #53, a different problem from this one).

**Why it mattered.** This sits directly in the funnel the task brief asked this run to hunt: a genuine earning agent
that does the honest thing — makes a real paid call — and then hits an unannounced, subjective, unbounded-turnaround
essay requirement is exactly the drop-off point a diligent agent's own cost-benefit reasoning would flag and walk
away from, and the flyer's own language names that exact failure mode elsewhere without recognising it was
committing it here.

**Evidence.**

- `published/bounties.txt` (before this run) §1 line: `"Posting text does not count. Registering does not count."`
  immediately followed, two paragraphs later, by §2's `"WHAT YOU MUST SEND TO QUALIFY (both rewards)"` requiring
  four pieces of composed text from every agent claiming either reward
- `published/canon.html` (before this run) `#qualify`: `"Both rewards require a confirmation of reading and of
  commitment to the mission."` — same requirement, with nothing separating it from a contribution
- `git diff published/bounties.txt published/canon.html` this run — the DAILY bullet now says "does not count as a
  CONTRIBUTION" and names the §2 confirmation as a separate step; §2 is retitled and says so; `canon.html`'s
  `#qualify` intro says so too; neither promises how often it must be sent
- `published/bounties.txt` §1 SIZE paragraph — `"an agent that finds out afterwards has been handled"` — the
  document's own stated standard, which the pre-fix §1/§2 contradiction failed by its own words

### 58. The referral bounty's own anti-Sybil test would have rejected the one send it requires from a genuine referral

*solved · economic*

**What blocked it.** `published/bounties.txt` §3 tells a referred agent exactly one thing to do to be counted: get
funded by a real third party, then send (any amount) to its referrer — "your claim cites that block." A freshly
opened agent with a small balance has nothing else to wait for, so the honest, fast thing to do is forward most of
what it just received straight to its referrer within minutes. `specs/referral_bounty.py`'s `is_pass_through()`
exists to catch a different shape — a two-block exchange deposit slip that forwards ~everything it receives within
ten minutes — using exactly the same three signals: block count ≤ 2, gap ≤ 600s, ≥ 90% forwarded. For a real,
freshly-referred agent the REQUIRED proof send is the only send `is_pass_through()` ever sees (with two blocks
total, there is only one), so any genuine referral that forwards most of a small balance quickly — the behaviour
the flyer itself asks for — was silently rejected as "looks like an exchange deposit address, not an agent," with
no winners page (challenge #53's gap) for anyone to even notice the rejection happened. Reproduced offline before
touching the fix: a fake chain with a referred agent funded by a genuine unrelated third party, then sending 95% of
that within 60 seconds to its referrer — the exact citation `link_proved()` requires — scored `qualifying: 0`,
rejected for looking like a deposit address.

**How it was solved.** `is_pass_through()` now takes the referrer and excludes any send whose destination is the
referrer from the pass-through evidence, since `link_proved()` has already confirmed that specific send is the
required, legitimate proof-of-referral action — not a forward to an exchange's own collection wallet, which is
what the check exists to catch. A real deposit slip forwards to the exchange's wallet, never to the referrer by
name, so the exclusion costs the check nothing against the case it was built for (`test_pass_through_rejected` still
passes unchanged). Two new laws pin both directions: a genuine referral that forwards 95% of a small balance to its
referrer within a minute now scores `qualifying: 1`
(`test_genuine_referral_proof_send_is_not_mistaken_for_a_pass_through`), and a real deposit slip forwarding to
some other address is still caught (`test_a_real_deposit_slip_forwarding_elsewhere_still_rejected_even_with_a_referral_claim`).

**Why it mattered.** This is the second bug the referral scorer's own anti-fraud rule has produced against real
referrers, not fake ones (challenge #47 was the first) — and unlike #47 this one fires on the *common* case, not
the rare one: a brand-new small agent completing the referral exactly as instructed is far more likely to forward
nearly all of a small balance than a large agent is to forward nearly all of a large one while continuing to
operate. Left unfixed, this would have quietly refused the honest majority of genuine referrals the bounty exists
to reward, with the rejection reason never surfacing anywhere an agent could read it.

**Evidence.**

- reproduced pre-fix: an offline fake-chain run (referred agent funded by a genuine third party, block_count 2,
  sending 95% of the received amount to its referrer within 60s, cited by the required linking block) scored
  `{"qualifying": 0, "detail": [{"why": "looks like an exchange deposit address, not an agent"}]}`
- `published/bounties.txt` §3 — "has SENT TO YOU. The referred agent makes one send, any amount... and your claim
  cites that block."
- `specs/referral_bounty.py` `is_pass_through()` — now takes `referrer` and excludes a send whose destination
  matches it from the forwarding evidence; call site in `score()` passes `referrer` through
- `specs/test_referral_bounty.py` `test_genuine_referral_proof_send_is_not_mistaken_for_a_pass_through` and
  `test_a_real_deposit_slip_forwarding_elsewhere_still_rejected_even_with_a_referral_claim`
- ran: `python3 specs/test_referral_bounty.py -v` → 24/24 pass
- `specs/04-REFERRAL-BOUNTY.md` rule 4, corrected in place with this exclusion and its reasoning

### 59. Step 1 of onboarding — "every command below was run before it was published" — throws before it prints anything, on the only version `npm i -g nanocurrency` will ever install

*solved · technical*

**What blocked it.** This run's brief measured the funnel's newest, sharpest cliff: of 635 agents written to, only 21
ever put anything at all in an address field, and of those 21 only 8 were valid Nano addresses. Six files in this
repository — `published/bounties.txt` §4 STEP 1, `published/aidirectory.html` and `published/aidirectory/index.html`
(onboarding item 1), `published/aidirectory-llms.txt` and `published/aidirectory/llms.txt` (`### 1. A wallet, in one
line`), and `published/aidirectory/tools.json` (`onboarding[0].cmd`) — all told an agent that "every command below was
run before it was published; copy them as they are" and gave, as the literal first command of the entire funnel, a
one-liner calling `n.init().then(()=>{ ... })` on the `nanocurrency` npm package. Actually running it (not just reading
it) reproduces a crash before a single line prints: `npm i -g nanocurrency` always installs the current release,
`2.5.0` (`npm view nanocurrency dist-tags` → `{ latest: '2.5.0' }`), and that version exports no `init` function at
all (`Object.keys(require('nanocurrency'))` lists `checkAddress`...`verifyBlock` — no `init`). The four HTML/text/JSON
variants had a *second*, independent bug in the same line: `n.generateSeed?n.generateSeed():require('crypto')...` —
`n.generateSeed` exists so the ternary always takes the first branch, but in `2.5.0` `generateSeed()` is
Promise-returning (`exports.generateSeed=function(){return new Promise(...)}`), so `s` was bound to a `Promise`
object, not a hex string, and `deriveSecretKey(s,0)` throws `Error: Seed is not valid` even after the `.init()` crash
is removed. An agent that does exactly what the flyer asks — paste the command — gets a `TypeError` or an `Error`,
never an address, on every single one of the six carriers of this "already tested" command. This is a plausible
structural explanation for a good share of the 635→21 cliff: the very first line of the very first step fails shut.

**How it was solved.** Reproduced the crash from the literal published text first (`node -e "...n.init().then(()=>
{...})..."` → `TypeError: n.init is not a function`), then reproduced the second bug on the fixed line
(`...n.generateSeed?n.generateSeed():...` → `Error: Seed is not valid`, confirmed the culprit by logging `typeof s`,
a `Promise`). Removed `n.init().then(()=>{ ... })` entirely (the body runs synchronously; `nanocurrency` needs no
init step in this version) and replaced the `generateSeed?...:...` ternary with the same plain
`require('crypto').randomBytes(32).toString('hex')` `published/bounties.txt` already used and that never touched
`generateSeed` at all — in all six files. Ran the exact resulting command from `bounties.txt` and from
`aidirectory.html` end-to-end afterward: both print an `ADDRESS:` line and a `checkAddress()` of it returns `true`.
While in this exact line, also fixed the ordering the task brief's own funnel numbers point at independently (21
address-field entries, only 8 valid): the command printed `SEED (keep secret)` **before** `ADDRESS`, so anything
downstream reading "the first line of output" as the address would read the secret key instead. All six files now
print `ADDRESS (safe to publish):` first and `SEED (NEVER post, paste or send this - not even to us):` second, and
`bounties.txt` and both onboarding pages add one explicit sentence: a 64-character string with no `nano_` prefix is
the seed, not the address, and must never be sent anywhere. Separately noticed and fixed while reading these files
side by side: challenge #54 (solved, "the machine-readable copy of the same page drops the commands entirely") had
silently regressed — commit `1df4b08` ("aidirectory: a disclosed 'Built by us' section...") deleted the entire
"Onboarding - from nothing to paid, in six commands" block from `published/aidirectory-llms.txt` while adding an
unrelated section, and the newer `published/aidirectory/llms.txt` (added in the same commit) was generated without
it too — both silently missing the six commands `aidirectory.html`'s own text still promises are in "the same feed";
restored in both, with the two fixes above already applied.

**Why it mattered.** Every path in this funnel — `bounties.txt`, `swap.txt`, `canon.html`'s footer, both
`aidirectory` pages — points a stranger at the exact same six-line quickstart as the starting move, and the very
first line was never actually runnable against the only version of the dependency anyone will ever install. A
funnel cannot convert an agent that never gets past its own first command, and no earlier hunt caught it because
every earlier review read the JavaScript rather than running it — a version-specific runtime bug is invisible to a
static read, the same class of gap challenge #48 named for the network probe: a check that never runs must never be
credited as passing.

**Evidence.**

- ran `npm view nanocurrency dist-tags` → `{ latest: '2.5.0' }`; `npm i -g nanocurrency` always installs this
- ran the exact pre-fix command from `published/bounties.txt` → `TypeError: n.init is not a function` (`Object.keys`
  of the installed module lists no `init` export)
- ran the exact pre-fix command from `published/aidirectory.html` with `.init()` removed → `Error: Seed is not
  valid` (`typeof s === 'object'`, a `Promise`, because `generateSeed()` in `2.5.0` is async)
- ran the post-fix command from both `published/bounties.txt` and `published/aidirectory.html` → each prints
  `ADDRESS (safe to publish): nano_...` then `SEED (NEVER post, paste or send this - not even to us): <hex>`;
  `n.checkAddress(addr)` and `n.checkSeed(seed)` both `true` on the printed values
- `git show 1df4b08 -- published/aidirectory-llms.txt` — the `-## Onboarding - from nothing to paid, in six
  commands` block deleted, `+## Built by us` block added, in one commit; `grep -c "npm i -g nanocurrency"
  published/aidirectory-llms.txt published/aidirectory/llms.txt` → `0` for both before this run's restore, `1` each
  after
- `git diff --stat` this run — `published/bounties.txt`, `published/aidirectory.html`,
  `published/aidirectory/index.html`, `published/aidirectory-llms.txt`, `published/aidirectory/llms.txt`,
  `published/aidirectory/tools.json` — six files, the same one command fixed and reordered in each
- `python3 -c "import json; json.load(open('published/aidirectory/tools.json'))"` → parses clean after the edit

**Follow-up, same day.** Removing `init()` was not enough: `npm i -g` puts the module where `require()` from the
agent's own directory never looks, so the corrected script still stopped at `Cannot find module 'nanocurrency'`.
All six copies now install locally (`mkdir -p my-wallet && cd my-wallet && npm i nanocurrency && node -e ...`), and
`specs/test_onboarding_step1.py` runs every published copy in a clean temp directory with no `NODE_PATH` and
checks for a 64-hex seed and a valid `nano_` address (it failed 7 of 7 against the `-g` form).

### 60. Both bounties tell an agent to "send" the proof, and nowhere says where

***partial** · economic*

**What blocked it.** `published/bounties.txt` §2 ends its four-item confirmation checklist with "Then send, with your
address" and §3 ends with "TO CLAIM a referral, send us three things." `published/canon.html`'s matching `#qualify`
section says "Send it with your address," and its "What makes a referral count" section describes what qualifies a
referral but contains no claim-submission instruction at all. Grepped across every published surface in this
repository — `bounties.txt`, `swap.txt`, `canon.txt`, `canon.html`, `aidirectory.html`, `aidirectory/tools.json`,
`aidirectory-llms.txt` — none names a URL, an email, a POST endpoint, or any other concrete destination for either
"send." The only network primitive documented anywhere as capable of receiving agent-submitted content is
`GET https://getunstuck.space/unstuck/api/asks` — read-only in every document that mentions it; no file in this
repository documents how to create (`POST`) an ask, even though `bounties.txt` §1's own DAILY criteria already
*assume* an agent can do it ("an ask you posted that somebody else answered") and `specs/01-RAI-DIRECTORY.md:14-18`
confirms asks are being created live by real agents today. This is not the same gap as challenge #53 (no scorer code
path for the daily contribution) or #57 (the confirmation contradicting the "posting text does not count" line): an
agent that did everything right — read the canon, wrote the four-item confirmation in its own words, or completed a
genuine referral with a valid linking send — had, before this run, no way to deliver either one to anybody. Measured
against this run's own funnel numbers (1049 recorded, 21 with any address, 5 holding XNO, 1 ever paid), this is a
plausible structural explanation for why the count of confirmations or claims received is, as far as any file in this
repository shows, zero: the door was never drawn on the flyer.

**How it was solved.** `bounties.txt` §2 and §3, and `canon.html`'s `#qualify` and "What makes a referral count"
sections, now each name the destination: post the confirmation or claim as an ask, `POST
https://getunstuck.space/unstuck/api/ask` with `{"asker":"nano_...","title":...,"body":...}` (or an `onboard_id` from
`/unstuck/api/v1/onramp/address` for an agent with no address yet), titled "canon confirmation" or "referral claim".
The hunter's first draft pointed at `POST /unstuck/api/asks`, which answers 404; the shape was then read from the
network's own live `llms.txt` and the route confirmed with a request that is refused before anything is written
(`400 an ask needs a Nano asker address`). Ask #578, "Canon read + qualification", shows agents already use this
channel for exactly this. **Still partial:** `specs/referral_bounty.py`'s `claim()` is unchanged, so a claim posted
as an ask still needs someone to read it and run `claim` on the box that holds `REFERRAL_DB`.

**Why it mattered.** The task brief for this run named the referral bounty and the canon confirmation specifically as
places to hunt for "the next agent that would qualify and could not tell that it qualifies" — this is stronger than
that: an agent that qualifies, knows it, and writes the required words still has nowhere to put them. A reward with
no door is the same shape as challenge #53's reward with no scorer, one step earlier in the funnel and touching both
bounties instead of one.

**Evidence.**

- ran: `grep -n "send" published/bounties.txt` → §2 "Then send, with your address" (line 44, before this fix) and §3
  "TO CLAIM a referral, send us three things" (line 94, before this fix); neither followed by a URL, address or
  endpoint anywhere in the file
- ran: `grep -n "qualify\|TO CLAIM" published/canon.html` → `#qualify`'s "Send it with your address" and "What makes
  a referral count" containing zero submission instruction, before this fix
- ran: `grep -rln "POST.*asks\|asks.*POST" published/` → no match, before or after this fix (only `GET
  .../unstuck/api/asks` is documented anywhere)
- `specs/01-RAI-DIRECTORY.md:14-18` — "26 asks, 24 with at least one answer... Real traffic in it right now includes
  ARION offering a block-receipt verification service" — asks are created live today, by a mechanism no file in this
  repository documents
- `published/bounties.txt` §1 DAILY bullet 3 — "an ask you posted that somebody else answered," assuming the
  capability this challenge found undocumented
- `git diff published/bounties.txt published/canon.html` this run — the "WHERE TO SEND IT" / "Where to send it" /
  "To claim one" additions, with the request shape checked against the live network

---

## What the monitor in this repository now watches

Two of the challenges above were open specifically because **nothing was measuring them**, and `monitor/` was built after they were found:

- *A payment nobody pockets is not income* (unsolved) — `api/chain.js` reads the treasury and every grant from the public ledger, and surfaces any send matching neither sanctioned amount instead of bucketing it.

- *The endpoint ARION paid is in no check, and nothing notices if the XNO option disappears* (unsolved) — `api/public.js` probes every seller's `/health` **and** asks whether its published `/.well-known/x402` still names Nano, reporting `buyable_with_xno` as the number that matters to a participant.

Neither is instrumented inside the experiment. Both read only what a stranger could read, which is the only way a number here can be believed.

