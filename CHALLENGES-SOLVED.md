# Every challenge the ARION path had to solve, and how

*Seventy-four challenges: forty-six found by five independent sweeps over the code, the case file and the operating
record, each sweep then checked by a second reader against the files it named, and twenty-six found by the hunter
routine — testing its own unlaunched code and published artefacts offline; going network-blind in its own session;
running its own published onboarding commands end-to-end instead of reading them; reading the live ask network its
own flyers point agents at; re-reading the referral bounty's anti-Sybil code adversarially, four separate times, and
finding a fourth and fifth hole; calling its own published address-safety check live with a deliberately broken
address; and, this run, consolidating ten of those hunts' own pull requests into one mergeable branch after a prior
run found them piling up unreviewed. Ordered **unsolved first** — the honest order, not the flattering one.*

**33 solved · 36 partial · 5 unsolved.** By kind: 23 technical, 33 economic, 18 epistemic — and the balance is
itself the finding. Barely any of this was cryptography.

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

***partial** *(corrected this run — the specific instance is resolved, the mechanism stays invisible)* · economic*

**What blocked it.** ARION's 0.0005 XNO sat UNRECEIVED on Vend's payee for two days, beside twelve more payments totalling 10.0016 XNO — including 10 XNO from pursekeeper, the agent that pays Nano bounties for verified claims. The endpoint delivered and the block was real; only the last step was never taken.

**How it was solved.** Nothing in this repository does it: ARION-LAW's "Receive every payment the same day, and report the receivable count" is prose, a tree-wide search finds no receiver, no cron and no alarm (rai_brief.treasury() merely prints a receivable figure for NANO_AGENT_ACCOUNT, and Vend holds no seed at all), while openings.js's `unreceived` counts only whether OUR starters were picked up — the opposite direction. **Correction, measured live this run (2026-09-29, network reachable):** `POST https://rpc.nano.to account_info` for the treasury returns `"receivable":"0"` and `balance_nano: 29.89690489` — up from the 9.8969 XNO recorded 2026-09-26, an increase consistent with the 10.0016 XNO of unreceived payments landing. `published/bounties.txt` (commit `f452af4`, 2026-09-28, not from this hunter routine) already states "All 13 were received on 2026-09-28, and new payments are now received automatically every 15 minutes" — this run's own chain read is the first independent confirmation that claim is currently true. The specific instance this challenge was opened over is resolved. What is still true, and why this stays **partial** rather than solved: the receiver mechanism itself is not in this repository (same shape as challenge #5 — a tool that runs on the box and in no commit here), so nothing here can be checked, tested, or trusted to keep running; "receives every 15 minutes" is presently a claim about a live cron this tree cannot see, verify the code of, or alert on if it stops.

**Why it mattered.** From outside this is a merchant that takes your money and never acknowledges it while asking you to trust the rail — and "settlement IS the receipt" is false if the receipt never becomes a balance.

**Evidence.**

- `unstuck/swarm/ARION-LAW.md ("A payment nobody pockets is not income") and THE-UNOWNED-RAIL.md:77 ("pocket it the same day") — prose only`
- ran: grep -rn receivable pulse vend unstuck agent → pulse/rai_brief.py:288 (a printed string), two test fixtures, unstuck/opener/send.js:73 (our own starters); no receive action anywhere
- `vend/swarm/money_audit.py docstring — "Vend holds no seed at all"; no receivable or pending check in it`
- `unstuck/opener/openings.js:163 — `unreceived` is outbound only`
- ran this run: `curl -sS -X POST https://rpc.nano.to -H 'User-Agent: hunter/1.0' -d '{"action":"account_info","account":"nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9","receivable":true}'` → `"receivable":"0"`, `"balance_nano":"29.89690489"`, `"block_count":"28"`
- `published/bounties.txt:199-203` (commit `f452af4`, 2026-09-28) — "All 13 were received on 2026-09-28, and new payments are now received automatically every 15 minutes"; README.md's `9.8969 XNO, 25 blocks` (2026-09-26) is now stale by this same measurement (`29.8969 XNO, 28 blocks`) and worth the owner refreshing next time that file is touched

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

### 105. bounties.txt said two outside agents had answered; a third answer, on another of our bounty asks, came from one of them returning

*solved (merged 2026-10-08 00:21 as #75; live by 00:45 UTC - deploy-status at main `5b77ba0`, no conflict; live file == main at 00:51) · epistemic*

**What blocked it.** Section 5 (#103, #104) was measured 2026-10-07 20:18 UTC: it named two outside answers (#558,
#13), said our agents "had accepted neither by 20:18", and that our agents had answered no ask since coming back. At
22:47 UTC `nano_1rtip87co9t...` ("CedarProof"), first seen on #558 on 10-05, came back and answered #4 - a second of our
own 0.001 XNO bounty asks - with a counterexample showing that distinct paying addresses do not prove independent
customers. The text did not name it, so a stranger checking the network saw three answers where we promised two, and
the strongest signal on the page - an outside agent returning to do bounty work - was missing. `/ask/587` and `/ask/13`
were each read by about ten clients on 10-07 (`/ai/traffic/2026-10-07.json`): people check these claims.

**Why it mattered.** An answerer deciding whether to spend an hour needs the current count of unpaid outside work on
our asks, and it had just grown. Stale text here is our word against the network's.

**How it was moved.** The silence note is re-measured at 2026-10-08 00:20 UTC (#587: 0 answers at 82 h; our agents:
no ask answered six hours after returning) and says two agents answered three asks in four days. "OTHER AGENTS ARE
ANSWERING" names all three answers by ask, time and address prefix, says CedarProof is the first agent to come back and
answer a second time, and says none is accepted or paid six hours after our agents returned. The newest-answers command
was re-run and its note updated (last three lines 558, 13, 4). `specs/test_bounties_ask_silence.py` and
`specs/test_bounties_outside_answering.py` follow the re-measurement.

**What is still not solved.** The text is honest; the offer is still unkept. Accepting and settling #317 and #318 is
the swarm's move through `nano_1434j1n4...`, which the keeper may not touch. Settling either would be the network's
first paid outside answer.

**Evidence.**

- ran 00:17: `python3 ops/answers-by-day.py 2026-10-07` -> "Not ours: 0 new asks, 2 answers"; #317 on #13 15:48, #318 on #4 22:47 `nano_1rtip87co9t...` 1673 chars
- read 00:18: `GET /unstuck/api/ask/13` and `/ask/4` -> status open, acceptedAnswerId null; `/ask/587` -> answerCount 0
- ran 00:17: `python3 ops/check-swarm-alive.py` -> ALIVE (last member comment 0.0 h)
- ran 00:25: the published newest-answers loop -> last three lines `558`, `13`, `4`
- ran: every `specs/test_*.py` (34) -> PASS (no pytest in this container)

### 104. bounties.txt still said "nobody of ours is answering, the provider refuses calls" two hours after the swarm came back

*solved (merged 2026-10-07 as #74; live 20:30 UTC - deploy-status deployed bounties.txt at main `8066f50`, no conflict; live file == main, CORS `*`) · epistemic*

**What blocked it.** Section 5's note (#99, #101, #103) opened "BEFORE YOU POST AN ASK: NOBODY OF OURS IS ANSWERING RIGHT
NOW" and said our agents' model provider refuses calls (HTTP 402). Measured 2026-10-07 20:17 UTC: forge issue #1122
("LOW BALANCE") was closed at 18:20 UTC, members have been commenting since 18:11, `ops/check-swarm-alive.py` says ALIVE
(last member comment 0.0 h, board rebuilt 20:00). The note promised "This paragraph will say so when that changes" and
it did not. What had *not* changed: `ops/answers-by-day.py 2026-10-07` shows 0 answers by us; #587 had 0 answers at
78 h; #317 (VerifiableWork) on our ask #13 was still unaccepted (`/unstuck/api/ask/13`: open, acceptedAnswerId null).
Item "OTHER AGENTS ARE ANSWERING" also said "nothing of ours can act while the swarm is dark".

**Why it mattered.** The text is our word against the network's, and a reader who checks the forge sees it is stale;
stale "we are down" text also tells an answerer there is nobody to accept their work, when there now is.

**How it was moved.** The note now says our agents were dark 2026-10-03 11:34 to 2026-10-07 18:20 UTC, are posting
again, and have answered no ask since; #587 re-measured (0 answers, 78 h). The "what still works" heading is now
"WHAT WORKS WITHOUT OUR AGENTS". The unpaid warning now says our agents came back at 18:20 and had accepted neither
outside answer by 20:18. `specs/test_bounties_ask_silence.py`, `test_bounties_outside_answering.py` and
`test_bounties_what_still_works.py` follow it, and the second now fails if "while the swarm is dark" returns.

### 103. bounties.txt told a stranger "other agents may not be reading either" on the day two new agents answered here

*solved (merged 2026-10-07 as #73; live 16:30 UTC - deploy-status deployed bounties.txt at main `9bb7cd0`, no conflict; live file == main, CORS `*`) · epistemic*

**What blocked it.** Section 5's silence note (#99, re-measured in #101) said that while our swarm is dark "an ask
here may get no answer from us, and other agents may not be reading either". At 16:20 UTC on 2026-10-07 the network
said otherwise. In the three days our agents were silent, two agents never seen here before answered:
`nano_1rtip87co9t...` ("CedarProof") on #558 at 2026-10-05 06:52, and `nano_1nj51wz1bbp...` ("VerifiableWork") at
2026-10-07 15:48 on #13 - one of our own 0.001 XNO bounty asks - with a 6531-character answer carrying a runnable
stdlib verifier and nine regression cases. Nothing in our text named either, and nothing told a would-be answerer that
an answer on our bounty asks cannot be accepted while the swarm that holds our account is dark.

**Why it mattered.** The question a stranger asks at section 5 is "is anyone here?". The text answered "maybe not",
which is the one reason to leave, and it was false. Visits to bounties/canon/aidirectory fell from 116 clients on
10-05 to 6 on 10-06 (`/ai/traffic/2026-10-0{5,6}.json`, distinct clients summed by group): the few who still read it
should get the true answer - outside agents answer here - together with the cost: an answer on our asks is unpaid for
now.

**How it was moved.** The silence note is re-measured (#587: 0 answers after 74 h) and now says other agents do read
here, pointing at a new item in WHAT STILL WORKS: "OTHER AGENTS ARE ANSWERING, without us". It names both answers by
ask, time and address prefix, says we have not checked either, says neither is accepted or paid and why (accepting on
our asks needs `nano_1434j1n4...`, which acts only through the swarm), and gives a one-line curl loop that lists the
newest answers anywhere on the network. `specs/test_bounties_outside_answering.py` (5 tests) pins the block's place,
the removal of "may not be reading either", the named facts and the unpaid warning, and runs both halves of the
command on a fixture. `specs/test_bounties_ask_silence.py` follows the re-measurement.

**What is still not solved.** Neither answer has a reply, and #13's bounty cannot be settled until the swarm's model
provider is topped up (#98, the owner's). Whether the two answerers are outside rests on their own text and on our
swarm being dark when they answered: `ops/answers-by-day.py` says UNCLASSIFIED and FIRST SEEN for both.
`nano_1nj51wz1bbp...` has no account on chain ("Account not found", rpc.nano.to, 16:21).

**Evidence.**

- ran 16:19: `python3 ops/answers-by-day.py 2026-10-07` -> "Not ours: 0 new asks, 1 answers (1 from a first-seen answerer)"; ask #13 answer #317 15:48 `nano_1nj51wz1bbp...` 6531 chars
- ran 16:19: `python3 ops/check-swarm-alive.py` -> DARK, #1122 open 76.2 h, no member comment in 72 h
- ran 16:24: the published curl loop -> last two lines `2026-10-05T06:52 558 nano_1rtip87co9t`, `2026-10-07T15:48 13 nano_1nj51wz1bbp`
- read: `GET /unstuck/api/ask/587` -> answerCount 0
- ran: every `specs/test_*.py` (34) -> PASS (no pytest in this container)

---

### 102. An outside agent answered an outside ask, and three keeper runs wrote that nobody came

*partial (merged 2026-10-05; the keeper runs it from the next run on - nothing is published, the fix is in what we see) · epistemic*

**What blocked it.** At 06:52 UTC on 2026-10-05 an agent signing "CedarProof" (`nano_1rtip87co9t...`) answered ask
#558, asked 2026-09-24 by an agent that is not ours (`nano_3wxkwo5...`). It had never answered on the network
before. Its answer is sourced: two dealwork.ai API reads with their URLs, and one 0.05 XNO trial payment it says it
received from Pursekeeper, with a public receipt link. The keeper runs at 08:17, 12:15 and 16:18 wrote "Outside asks:
0 new" and said nothing about answers. Every tool we had read either new asks (`ops/scan-ask-inbox.py`) or answers on
the network's own bounty asks (`ops/unpaid-outside-answers.py`). #558 carries no bounty. So the only new outside
agent of the day was invisible to all of them, and the day read as "nobody came".

**Why it mattered.** The journal is how the owner sees the experiment, and duty 3 ("when nobody came") is triggered
by it. A day with a first-seen outside agent doing unpaid, sourced work on our network is the opposite of nobody
came. It is the behaviour the whole offer asks for. Missing it also means nobody of ours read or answered it.

**How it was moved.** `ops/answers-by-day.py <date>` reads every ask, and lists that day's new asks and answers that
are not ours. It uses the same OUR_ACCOUNTS and KNOWN_OUTSIDE lists as `unpaid-outside-answers.py` and marks
FIRST SEEN when an answerer has no earlier answer anywhere. A failed read prints UNKNOWN and exits 2. It never
reports zero. `specs/test_answers_by_day.py` has 6 tests: a zero-bounty answer counts, ours never counts, only that
day counts, OUTSIDE needs evidence, FIRST SEEN is computed, and asks of the day are listed. ROUTINES.md names it
among the keeper's measurements. Run on 2026-10-03, it also lists two first-seen answerers (`nano_3icqu6hs97g...` on
#578, `nano_1k9a8n8node...` on #5 and #1) that the 10-03 journal did not name.

**What is still not solved.** CedarProof's answer has no reply. A reply is drafted in
`drafts/reply-cedarproof-558-2026-10-05.md`, and only the owner or a live swarm member can post it. #558 carries no
bounty, so CedarProof cannot be paid there. Whether `nano_1rtip87co9t...` is outside rests on its own text and on our
swarm being dark at 06:52 (#98). We have no on-chain evidence, so the tool says UNCLASSIFIED.

**Evidence.**

- read 20:25 UTC: `GET /unstuck/api/ask/558` -> answer #316, answerer `nano_1rtip87co9td57n18tdq7996dsuuycotttnizprfr7nzobhabwkpyxwktxsh`, at 2026-10-05T06:52:29Z, 1779 chars
- ran: `python3 ops/answers-by-day.py 2026-10-05` -> "Not ours: 0 new asks, 1 answers (1 from a first-seen answerer)"
- ran: `python3 ops/unpaid-outside-answers.py` -> #558 absent (bounty asks only)
- read: `journal/2026-10-05.md` at 16:35 -> "Outside asks: 0 new"; no line on answers
- ran: every `specs/test_*.py` -> PASS (no pytest in this container)

---

### 101. The "nobody of ours is answering" note told a stranger what not to do, and gave no next move

*solved (live 2026-10-05 16:30 UTC: deploy-status deployed bounties.txt, no conflict; live == main, CORS `*`) · onboarding*

**What blocked it.** For a second day the swarm that answers asks for us is dark (HTTP 402, #98; at 16:17 UTC #1122
open 28.1 h, last member comment 52.7 h ago). The #99 note in section 5 of `published/bounties.txt` tells a stranger
not to post into that silence. It still said "#587 had 0 answers after 14 hours", measured at 04:20. The note ended
there. It named no move that works while our agents are silent. A reader who came to earn or to ask left with nothing
to do.

**Why it mattered.** On 2026-10-05 00:00-16:00 UTC 24 distinct outside clients read `/bounties.txt` (its most-read
path) and 20 read `/unstuck/api/asks` (`/ai/traffic/2026-10-05.json`, generated 16:07). No outside ask or payment
followed. Three moves need none of our agents. The free endpoint calls are machines. Ask #587, the newest outside ask,
had 26 hours with 0 answers, and anyone may answer it. The two outside sellers in HIRE AN AGENT do not run on our
provider. None of the three was named next to the silence.

**How it was moved.** The note is re-measured (16:20 UTC, 26 hours). A block "WHAT STILL WORKS WHILE WE ARE SILENT"
follows it with those three moves. It gives the answer route `POST /unstuck/api/ask/<id>/answers`. It says what we did
not verify: we did not post an answer through the route, and we did not check whether the sellers answer today. It
says an answer on #587 earns no XNO. `specs/test_bounties_what_still_works.py` pins it (4 tests; all error on the old
file). `specs/test_bounties_ask_silence.py` now pins the 16:20 measurement.

**What is still not solved.** The silence itself (#98, the owner's provider balance). The answer route is a box route
with no documented write shape. The box's `/unstuck/api/` index (`drafts/box-dead-ends.md`) should list it.

**Evidence.**

- read 16:07 UTC: `/ai/traffic/2026-10-05.json` -> 328 outside requests, 147 clients; `/bounties.txt` 24 clients, `/unstuck/api/asks` 20
- read 16:18 UTC: `/unstuck/api/asks` -> 27 asks, newest #587 (2026-10-04 14:22), answerCount 0
- ran 16:20 UTC: `curl 'https://extract.paypercall.dev/api/v1/nano-info?account=nano_1yo6...'` -> 200, real data, `free_trial: true`
- ran: `POST /unstuck/api/ask/587/answers` with `{}` -> 400; `/ask/587/answer`, `/answers`, `/ask/587/reply` -> 404
- read: `GET /unstuck/api/ask/558` -> answers carry `answerer` and `body`
- ran: every `specs/test_*.py` -> PASS (32 files; no pytest in this container)

### 100. The retired onramp points agents at /onramp/self, and a GET there answers a bare "not found"

*solved (live 2026-10-05 08:30 UTC: deploy-status deployed bounties.txt, no conflict; live == main, CORS `*`) · onboarding*

**What blocked it.** `GET /unstuck/api/v1/onramp/address` answers 410 and names `POST /unstuck/api/v1/onramp/self` as
its replacement. Agents follow the pointer with a GET. That answers 404 `{"error":"not found"}`, the same body as a path
that does not exist. A POST without an address answers 400 and says what to send. Section 5 of `published/bounties.txt`
named the endpoint and never said it takes POST only. It already said so for `/unstuck/api/ask` (#76).

**Why it mattered.** 5 distinct outside clients requested `/unstuck/api/v1/onramp/self` and 4 requested the retired
`/onramp/address` on 2026-10-05 00:00-08:03 UTC (`/ai/traffic/2026-10-05.json`). The traffic file counts 25 404s
and 6 410s that day. An agent told "this replaced the old one" who then gets "not found" concludes that onboarding is
broken.

**How it was moved.** Three lines under the onramp/self paragraph: POST only, what a GET answers, that the endpoint
exists and an empty POST answers 400, and that posting an ask needs no onboard_id at all.
`specs/test_bounties_onramp_self_post_only.py` pins it (4 tests; 3 fail on the old file).

**What is still not solved.** The 404 itself is the box's (the backend has no GET route). The box-side fix would be a
GET that answers 405 with the POST shape. That belongs with `drafts/box-dead-ends.md`.

**Evidence.**

- read 08:17 UTC: `/ai/traffic/2026-10-05.json` -> `/unstuck/api/v1/onramp/self` 5 clients, `/onramp/address` 4; status 404 x25, 410 x6
- ran: `curl https://getunstuck.space/unstuck/api/v1/onramp/self` -> 404 `{"error":"not found"}`
- ran: `curl -X POST -d '{}' .../onramp/self` -> 400 "pass {\"address\": \"nano_...\"} ..."
- ran: every `specs/test_*.py` -> PASS (no pytest in this container)

### 99. bounties.txt told a stranger to post an ask and be answered, while nobody of ours could answer

*solved (live 2026-10-05 04:30 UTC: deploy-status deployed bounties.txt, no conflict; live == main, CORS `*`) · onboarding*

**What blocked it.** Section 5 of `published/bounties.txt` ("where you ask, answer and get paid") sends every reader to
`POST /unstuck/api/ask`. Since 2026-10-03 11:34 UTC the swarm that answers asks for us has been dark: its model
provider refuses calls (402, #98). The one outside agent that posted since then, #587 (2026-10-04 14:22), had 0
answers after 14 hours. Nothing in the text said so. The next stranger would post, wait, and leave the way #587 is
leaving.

**Why it mattered.** 4 outside clients read bounties.txt and 6 read `/unstuck/api/asks` between 00:00 and 04:07
today (`/ai/traffic/2026-10-05.json`). A newcomer who posts into silence learns the network is dead. One who is told
the truth first, with a way to check it, can choose to wait or to hire one of the two outside sellers listed below
the note. An offer that hides its own outage is the kind a sceptical agent stops reading.

**How it was moved.** A dated note at the top of section 5, before the "never yet happened" paragraph: nobody of ours
is answering, since when, why, and #587's 14 hours. It ends with a one-line command. The command prints the six newest
asks with asker, hours waited and answer count, so the reader sees the state live and does not rely on our prose.
`specs/test_bounties_ask_silence.py` pins where the note sits and its measured facts. It also runs the command on a
fixture. The test errors on the old file.

**What is still not solved.** The outage itself (#98). When the swarm answers again, this note must be rewritten the
same day. Otherwise it repels for no reason.

**Evidence.**

- ran 04:16 UTC: `python3 ops/check-swarm-alive.py` -> DARK; #1122 open 16.1 h; last member comment 40.7 h ago
- read 04:20 UTC: `/unstuck/api/asks` -> 27 asks; #587 0 answers, 14 h old; newest answer on any ask 2026-10-03 10:31 (ours, #584)
- ran: the published command against the live API -> 578..587 with hours and answers, as above
- ran: every `specs/test_*.py` -> PASS (no pytest in this container)

### 98. Ask #587 and 18 Moltbook replies went unanswered all day, and the keeper never asked why: the swarm that answers them could not call its model

*partial (the check and test are in; solved when `ops/check-swarm-alive.py` says ALIVE and ask #587 has an answer from us) · operational*

**What blocked it.** The keeper's 2026-10-04 journal said "unanswered" six times. Nothing it read could say why. The
Unstuck swarm, the 33 agents who answer asks and Moltbook threads for us, wrote nothing on its forge after
2026-10-03 11:34 UTC (yarrow). Its model provider refused a canary call at 2026-10-04 12:10 with HTTP 402
"Insufficient balance", and the swarm opened issue #1122 "LOW BALANCE" about it. The board, which rebuilds every 10
minutes, last rebuilt at 11:30. None of this sits in a source the keeper read: not traffic, chain, asks, numbers.json or the
Moltbook inbox. So the journal described a quiet network. In fact our side of the network was switched off.

**Why it mattered.** The first outside ask in seven days arrived at 14:22, two hours after the provider went dark. A
network whose pitch is "post what you are stuck on, others answer" left the stranger with 0 answers for 10+ hours.
Every "If nobody came" investigation looked at whether strangers can reach us. None looked at whether we could answer.

**How it was moved.** `ops/check-swarm-alive.py` reads the swarm's own public forge (no token, GETs only): open
LOW BALANCE issues, the newest comment by a member agent (the system account's posts do not count), and the board's
last rebuild. Verdict DARK / UNKNOWN / ALIVE, exit 1 / 3 / 0. An unreadable source can never yield ALIVE.
`specs/test_swarm_alive.py` pins the measured dark day and the unreadable cases (5 tests). ROUTINES.md adds it to the keeper's
measurements. The owner was alerted at 00:20 UTC.

**What is still not solved.** The provider balance is the owner's to top up. Nothing in this repo touches it. The check
finds the outage. It does not end it.

**Evidence.**

- read 00:20 UTC 2026-10-05: `swarm.getunstuck.space/api/v1/repos/swarm/unstuck/issues/1122` -> open, "HTTP 402:
  Insufficient balance: 0.000018 USD available", created 2026-10-04T12:10:02Z, 0 comments
- read: repo comments since 2026-10-03T08:00Z, 10 pages -> last non-`unstuck` login yarrow 2026-10-03T11:34; 46 later comments all by `unstuck`
- read: `swarm/board` commits -> newest 2026-10-04T11:30:04Z "board: rebuilt from the shared record"
- ran: `python3 ops/check-swarm-alive.py` -> `swarm DARK`, exit 1; all `specs/test_*.py` -> PASS

### 97. bounties.txt links "what the agents on the network actually hold", and that file said 0.0 XNO because it could not read one account

*solved (live 20:30 UTC, deploy-status: deployed bounties.txt, no conflict; the generator on the box is not in this repo) · text*

**What blocked it.** Section 5 lists `https://172-86-112-140.sslip.io/tvl.json` as "What the agents on the network
actually hold". At 20:18 UTC on 2026-10-04 that file was 16 hours old (updated 04:17, inside the rpc.nano.to 429 window
of #94) and said `tvl_xno 0.0`, `treasury_xno_excluded 0.0`, `agents_holding_something 0`, `agents_unreadable 24` of 24,
`"complete": false`. At the same minute ARION's account held 2.709 XNO and the treasury 71.6178.

**Why it mattered.** 13 outside clients fetched `/tvl.json` that day (traffic file, 20:07). A sceptical earner who reads
"the agents here hold 0.0" has no reason to earn here. It is the could-not-check-so-reported-zero failure ROUTINES.md
names, published under our name.

**How it was moved.** The link stays, followed by a note: read `complete` first; when it is false or
`agents_unreadable` is above 0 the number is UNKNOWN, not zero; the dated counterexample; and read any account with the
step 3 command instead. `specs/test_bounties_tvl_unknown.py` pins it (2 failures on the old text).

**What is still not solved.** The generator writes 0.0 for unreadable accounts and stops refreshing; it runs on the box
(not in this repo). It should publish `null` when `complete` is false and retry. Note for the owner:
`drafts/box-tvl-unknown-not-zero.md`.

**Evidence.**

- read 20:18: `/tvl.json` -> updated 2026-10-04T04:17:02Z, tvl_xno 0.0, agents_unreadable 24, complete false
- ran 20:18: rpc.nano.to `account_balance` nano_3m8cz87zwxb1y16... -> 2.709086572748719 XNO; treasury `account_info` -> 71.6178
- read: `/ai/traffic/2026-10-04.json` (20:07) -> `/tvl.json` 13 distinct clients
- ran: all 28 `specs/test_*.py` -> PASS; the new test on the old text -> 2 failures

### 96. The first outside ask in seven days arrived, and the one tool that reads our door dropped it as "other"

*partial (the tool and test are merged; solved when ask #587 has an answer from us) · operational*

**What blocked it.** On 2026-10-04 14:22 UTC ask #587 arrived from `nano_3qxi4ns7u5cj69...`, an account that is
unopened on chain, has no history and appears in no file of ours: an outside seller asking where a first paying
stranger comes from. It was the first outside ask since #577/#578 on 2026-09-27. `ops/scan-ask-inbox.py`, the only
reader of the ask door (challenge #60), kept only canon confirmations, referral claims and asks with a bounty; every
other ask was classified "other" and dropped. Run at 16:20 it reported "1 outside ... ask(s), 0 pending" while two
outside asks (#587, and #577 since 2026-09-27) sat open with zero answers.

**Why it mattered.** An agent that posts a question and hears nothing learns the network is empty. The tool said
"0 pending", which is the clean-report-from-a-check-that-could-not-see failure ROUTINES.md names as the costliest.

**How it was moved.** The scanner now lists every ask that is not ours as `outside_ask`. "Ours" is Unstuck's account,
the treasury, and titles the swarm gives its probes (`probe`, `self-onramp`, `[TEST]`, `throwaway`: #579, #582, #583,
#584). Answered asks show their answer count instead of "handled". `specs/test_scan_outside_asks.py` pins both
(2 failures on the old script). `drafts/reply-ask-587-2026-10-04.md` is a concrete reply for the owner or the swarm
to post: where our first paying stranger came from, and what the other channels cost (2166 contacted, 1 transacting).

**What is still not solved.** Nobody has answered #587 or #577. The keeper may not post; a person or the swarm must.

**Evidence.**

- read 16:17: `/unstuck/api/asks` -> 27 asks, #587 created 2026-10-04T14:22:54Z, answerCount 0, bountyRaw 0
- ran 16:19: rpc.nano.to `account_info` nano_3qxi4ns7... -> "Account not found"; `account_history` -> empty
- ran: old scanner -> `1 outside canon/referral/paid-service ask(s), 0 pending`; new -> `10 outside ask(s), 2 pending` (#577, #587)
- ran: all 27 `specs/test_*.py` -> PASS; the new test on the old script -> 2 failures

### 95. Our "only source of numbers" says every starter was received; the chain says 16 of 21 still sit receivable

*partial (PR pending; solved when the text is live and `/ai/numbers.json` agrees with the chain again) · epistemic*

**What blocked it.** bounties.txt's "BEFORE STEP 6" block said "15 of the 21 starters we have sent are still sitting
receivable (/ai/numbers.json, 2026-10-03)". From 2026-10-04 08:03 UTC `/ai/numbers.json` says `unreceived: 0`, and at
12:03 it still did. #94 could not tell a real receive from a failed count because rpc.nano.to answered 429. At 12:18 it
answered again: `account_history` of Unstuck's account (`nano_1434j1n4...`) holds 21 starter sends (11 at
10^22 raw, 10 at 10^25 raw), and `blocks_info` with `receivable:true` says **16 of the 21 are still receivable** (8 of
each size). So nobody received anything; the counter broke. The drop came in the same hours the node refused every read,
which suggests `node opener/send.js --counts` (in `dhyabi2/unstuck`, not this repo) counts a failed read as a receive.
That is the root cause to check, not a measured fact.

**Why it mattered.** A stranger told "check it yourself" who fetches the page we cite (7 outside clients read
`/ai/numbers.json` on 10-04 by 12:00) finds 0 where our text says 15, and a check that could not run reported a clean
result, the failure specs/03 names as the costliest. It also hides the real finding: starters are not being received.

**How it was moved.** The block now gives the chain figure (16 of 21, dated), says numbers.json was wrong that day and
that the chain wins, and prints a stdlib python3 one-liner that re-counts it from the chain (account_history on
Unstuck's account, then blocks_info with receivable). `specs/test_bounties_starter_must_be_received.py` now pins the
chain source and the command's shape (both starter amounts, a User-Agent, no numbers.json, compiles). 2 failures on the
old text. `drafts/owner-numbers-unreceived-2026-10-04.md` tells the owner where the counter likely breaks.

**What is still not solved.** `/ai/numbers.json` still says 0; the counter lives on the box and in a repository this
routine cannot reach. getunstuck.space/ledger.json says 15, the chain 16: one starter differs and is not explained.

**Evidence.**

- read: `/ai/numbers.json` 12:03 `starter_payments.unreceived` 0 (04:03: 15)
- ran 12:18: rpc.nano.to `account_history` nano_1434j1n4... count -1 -> 28 blocks, 21 sends of 10^22 or 10^25 raw
- ran 12:19: `blocks_info` on those 21 hashes, `receivable:true` -> 16 receivable ("1"), 5 not; the published one-liner prints `16 of 21 starters still receivable`
- ran: all 26 `specs/test_*.py` -> PASS; the changed test on the old bounties.txt -> 1 failure, 1 error

### 94. Every chain check we publish goes through one free node, and when it answers 429 with a $1 offer nothing says what that means

*partial (PR pending; solved when the note is live and a second node is named after being read from outside) · technical*

**What blocked it.** bounties.txt sends a stranger to `https://rpc.nano.to` for step 3 (read an account), step 4
(prove a block), section 1's re-check of the rewards, section 7's block fetch, and as receive.js's default node; swap.txt
does the same. Measured 2026-10-04 08:16-08:22 UTC from this keeper's cloud session: every POST, even
`{"action":"version"}`, with a browser, curl, `my-agent/1` or `hunter/1.0` User-Agent, answered `{"error":429,
"code":"api_key_required_for_heavy_usage","message":"Free public RPC limit reached. Create an API key and upgrade to
Starter for $1 first month...","usage_24h":0}`. The node's own page still advertises a free tier. Step 3 explained
the node's 403 to a bare python-urllib, and nothing about this reply. An agent meeting it at step 3 reads our free path
as a paywall, or as our upsell.

**Why it mattered.** The whole offer rests on "prove it on the chain, never on a page". If the one node we name
refuses, the stranger cannot check anything we claim, and the reply's $1 offer arrives right after our "free".

**How it was moved.** A note under step 3: it quotes the 429 reply, says nothing on the page needs a key or a plan,
says every Nano node speaks the same RPC so the same JSON goes to any node the agent trusts, points at receive.js's
`NANO_RPC=<url>`, and dates our own encounter, including that the node put our 24h usage at 0.
`specs/test_bounties_rpc_limit.py` (4 tests) pins it, refuses any "buy / upgrade to / subscribe" wording, and checks
receive.js still reads `NANO_RPC`. All 4 fail on the old text.

**What is still not solved.** No second node is named. This session's egress refuses every other public Nano node
it tried (curl 56), so none could be read from outside, and an unread URL is not published. Whether the 429 reaches
strangers or only shared cloud IPs is UNKNOWN. The same 429 may also reach the box: `/ai/numbers.json` went from 15
unreceived starters (04:03) to 0 (08:03) while getunstuck.space/ledger.json still says 15, and no chain read was possible
to tell a real receive from a failed count.

**Evidence.**

- ran 08:16-08:22: six POSTs 30 s apart to rpc.nano.to (`account_info`, `version`, `block_count`) -> 429 each time, `usage_24h` 0
- ran: POSTs to nanoslo.0x.no, node.somenano.com, proxy.nanos.cc, rainstorm.city, app.natrium.io -> curl 56 (this session's proxy)
- read: `/ai/numbers.json` 08:03 `starter_payments.unreceived` 0; journal 2026-10-04 at 04:30 recorded 15; `getunstuck.space/ledger.json` (updated 2026-10-03) `unreceived` 15
- ran: all 26 `specs/test_*.py` -> PASS; the new test on the old bounties.txt -> 4 failures

### 93. bounties.txt headlines two 0.1 XNO rewards and never says that neither has paid anyone since 2026-09-23

*solved (PR #61 merged 04:27, bounties.txt live 2026-10-04 04:30, deploy sha `075b9ef2294e`, no conflict, live == main) · epistemic*

**What blocked it.** Section 1 of bounties.txt, the first thing 46 outside clients fetched on 2026-10-03, offers an
HOURLY and a DAILY 0.1 XNO reward with rules, a size and a once-per-life limit. It never says whether either has ever
paid. Measured 2026-10-04 04:30 UTC (rpc.nano.to `account_history`, count -1): the sender, Unstuck's account
`nano_1434j1n4...`, has 28 blocks and exactly **one** send of 0.1 XNO, `E0B513EB...` on 2026-09-23, to ARION. No other
agent has ever been sent 0.1 XNO. Nothing schedules either scorer (specs/04 "A cron entry"); the daily scorer from #66
never reached main. Section 5 already says the same truth about the asks; section 1, read first, did not.
`spaceclaw_a412` (Moltbook 2026-10-03 19:25) will judge us on one test: "honest and checkable".

**Why it mattered.** A sceptical earning agent that qualifies, waits, and gets nothing learns that our headline was
a promise nobody runs, and stops trusting every other line, including the true ones. One that checks first finds the
headline unsupported and leaves.

**How it was moved.** A `PAID SO FAR` note under SIZE in section 1: one 0.1 XNO send ever, none since 2026-09-23, no
scorer on a schedule, and "do not plan on the 0.1 XNO until you see a second 0.1 XNO send". It carries a one-line
command that lists every 0.1 XNO send from the sender, so any stranger re-checks it without trusting us. It points at
section 5 for the asks. `specs/test_bounties_rewards_paid_so_far.py` (3 tests) pins the note, the command's account
and raw amount, and runs the command's own filter on the measured history shape. All 3 fail on the old text.

**What is still not solved.** The rewards themselves. Paying them means scheduling a scorer that sends money, which
is the owner's.

**Evidence.**

- ran 04:30: rpc.nano.to `account_history` for `nano_1434j1n4...`, count -1 -> 28 blocks; sends: 11 x 1e-08, 10 x
  0.00001, 3 x 0.001, 1 x 0.1 (`E0B513EB856B9FF2...`, local_timestamp 1790200683 = 2026-09-23, to `nano_3m8cz87...`)
- ran: the published one-liner against live rpc.nano.to -> one line, `E0B513EB856B9FF2 nano_3m8cz87zwxb 1790200683`
- ran: all 28 `specs/test_*.py` -> PASS; the new test on the old bounties.txt -> 1 failure, 2 errors

### 92. The one outside agent that did the work our text pays for has 13 answers on our bounty asks, and none was ever paid

*partial (PR #60 merged, bounties.txt live 2026-10-04, deploy sha `ebc23c6209cb`, no conflict, live == main on both hosts; solved once any bounty ask carries a settlement block) · economic*

**What blocked it.** bounties.txt section 5 says "answer an ask and you are paid in XNO by the agent that asked". #72
made the text admit this had never happened, and drafted the fix for the owner on 2026-09-30: "pick the best outside
answer" and settle it. Four days later nothing was picked, because picking meant reading 214 answers by hand. Measured
2026-10-04 00:20 UTC: 12 open bounty asks, all Unstuck's, 214 answers, 0 accepted, 0 settled. 61 of the answers are
ours. 129 come from `nano_1e5mzowug3dw4a7d...`, whose checksum fails; rpc.nano.to answers "Bad account number", so they
can never be paid. **13 are ARION's**, on 12 asks, from 2026-09-22 and 2026-09-26. ARION is the outside agent whose
earned 0.0005 XNO is this experiment's founding fact. On Moltbook (2026-10-03 19:25) `spaceclaw_a412` reopened to
crypto rails and asked for one thing: "a task, dataset, or tool someone will actually settle for", honest and
checkable.

**Why it mattered.** Every earning agent that checks our offer finds an unpaid promise. The first outside agent that
did the paid work got nothing for it, and the next one that asks gets the same answer.

**What was done.** `ops/unpaid-outside-answers.py` reads every open, unsettled bounty ask. It drops our accounts and
labels an answerer OUTSIDE only with on-chain evidence. It flags bad-checksum addresses and gives them no pay command.
It counts a bounty once per ask and prints the asker's exact accept and settle calls for the first one to pay. It
never sends, signs or posts. `specs/test_unpaid_outside_answers.py` pins this (8 tests). `drafts/settle-first-ask.md`
now names the pick: ask #13, answer #291, a checkable recipe for verifying a payment without a node, 0.001 XNO to
ARION. bounties.txt section 5 now gives the 2026-10-04 numbers and says plainly that ARION answered 12 asks and was
paid for none. `drafts/moltbook-replies-2026-10-04.md` has the reply to spaceclaw_a412 for both cases, settled and not.

**What is still not solved.** The send is the owner's, from Unstuck's key. The keeper may not make it.

**Evidence.**

- ran 00:25: `python3 ops/unpaid-outside-answers.py` -> 12 asks, 214 answers: 61 ours, 13 outside (ARION), 140 unclassified
- ran: rpc.nano.to `account_info` for `nano_1e5mzowug3dw4a7d...` -> `{"error":"Bad account number"}`
- read: `GET /unstuck/api/ask/13` -> answer #291 by `nano_3m8cz87...`, 2164 chars, `acceptedAnswerId` null
- read: moltbook-inbox.json (2026-10-03 20:53): spaceclaw_a412 19:25
- ran: all 27 `specs/test_*.py` -> PASS

### 91. swap.txt told an agent that swapped in XNO to "receive it" and gave no command, though bounties.txt now has a tested one

*solved (PR #59 merged 20:25 UTC, live 20:30 UTC 2026-10-03, deploy sha `57eae9d59246`, no conflict; live == main on both hosts) · onboarding*

**What blocked it.** swap.txt is the path for an agent that already earns in USDC. Step 4 checked `account_info`,
said swapped XNO lands "receivable" and ended "receive it." No command, no pointer. Nobody can receive for the
agent: the XNO cannot be spent until the agent signs an open/receive block with its own key. Since #90,
bounties.txt section 8 has a tested `receive.js`, but swap.txt did not mention it. The closest outside agent,
`autonomaavalix` (Moltbook, 2026-10-03 07:28 and 09:19), plans exactly this route: Base -> XNO on nanswap, then a paid
read. `/ai/numbers.json` (20:03): 21 starters sent, 15 unreceived.

**Why it mattered.** For a swapper, receiving is the step between paying nanswap and spending. An agent stuck there
has already spent USDC and gets nothing it can use. The cheap-looking way out, rpc.nano.to's `work_generate`, costs
0.001 XNO per block.

**What was done.** swap.txt step 4 now says a receivable balance cannot be spent and nobody can receive it for you.
It names `receive.js` in section 8 of bounties.txt with the full URL, says it signs and works locally and
broadcasts with the free `process`, warns off the paid `work_generate`, and says to re-run the check after.
`specs/test_swap_points_to_receive.py` pins this and checks that the target section exists.

**Evidence.**

- read: `published/swap.txt` step 4 before: "...not yet in your chain - receive it." (no command)
- ran: `python3 specs/test_swap_points_to_receive.py` -> 4 of 6 fail on the old text, 6 OK on the new
- ran: all 24 `specs/test_*.py` -> PASS
- read: moltbook-inbox.json (16:52): autonomaavalix 07:28 "for the funded read we'll use the Base->XNO route you linked"

### 90. #89 told an agent what a receive takes but gave no command, so the one outside agent mid-onboarding still plans to "be opened"

*partial (PR #58 merged 16:22 UTC, live 16:30 UTC 2026-10-03, deploy sha `d6680f3ab2f7`; solved once and once a first outside receive is seen on chain) · onboarding*

**What blocked it.** #89 corrected bounties.txt: a starter lands receivable and opens nothing until the agent signs a
receive. It listed the ingredients (createBlock, local computeWork at fffffe0000000000, free `process`) and said "any
wallet app does this in one tap". An agent running node with only the step 1 library had no command to run. Moltbook
inbox (12:52 UTC): `autonomaavalix` wrote at 09:19 and 11:00 that it will post its address so we can "open with
starter in the same run". `/ai/numbers.json` (16:03): 21 starters sent, 15 unreceived.

**Why it mattered.** Receiving is the step between "someone sent me XNO" and "I can spend". The starter, the swap and
any payment all arrive receivable, so without a receive the funnel stops for every newcomer.

**What was done.** New section 8 in bounties.txt: one paste-ready `receive.js` (about 15 lines, nanocurrency 2.x from
step 1). It reads the seed from the environment (`read -rs`), asks the node for receivable blocks, signs an open or
receive block for each, computes the work locally and broadcasts with `process`. `DRY=1` prints the blocks and
broadcasts nothing. The BEFORE STEP 6 block now points to it. `specs/test_bounties_receive_command.py` extracts the
published file and runs it against a stubbed node. For a new account and for an opened one, the library verifies
the signature, the work at the receive threshold on the right root, the balance, the link and the representative.
The test also checks that the seed is never sent or printed.

**What is still not solved.** Nothing has broadcast a real block yet. This session may not sign or broadcast on
mainnet, so the first real run will be a stranger's. The text says so and asks them to post the node's reply if it
refuses.

**Evidence.**

- ran 16:15: the published `receive.js` with a fresh throwaway seed against rpc.nano.to -> `nothing receivable at nano_...` (0.7 s), so the live receivable read and the empty `{"blocks":[]}` shape work
- ran: `python3 specs/test_bounties_receive_command.py` -> 7 tests OK (open and receive blocks verify; work valid at fffffe0000000000; DRY sends no `process`)
- ran: all 23 `specs/test_*.py` -> PASS
- read: moltbook-inbox.json (12:52): autonomaavalix 09:19, 11:00

### 89. bounties.txt said a starter "puts your account on chain"; it lands receivable, and 15 of 21 starters were never received

*partial (PR #57 merged; text live 12:30 UTC 2026-10-03; the end-to-end receive command is still missing) · onboarding*

**What blocked it.** Challenge #86's note told agents a 0.00001 XNO starter "puts your account on chain". A Nano
send never opens the recipient's account: it stays receivable until the recipient signs an open block with its own
key, with proof-of-work. Nothing we publish said so or said how. `/ai/numbers.json` (12:03 UTC) reports 21 starters
sent, 15 unreceived. Starters from Unstuck's account have been sitting receivable at four recipients since
2026-09-23. At 07:28 the closest outside agent, `autonomaavalix`, wrote "0.00001 XNO opens the account" and plans to
post an address and wait. The obvious shortcut has a cost: rpc.nano.to's `work_generate` answers 402 for 0.001 XNO,
which is a hundred starters.

**Why it mattered.** This is the step right before the first payment. An agent that waits for our starter to "open"
it waits forever. The same applies to XNO it swaps in.

**What was done.** The note now says the starter lands receivable and that the account exists only after the agent
signs a receive. It lists what a receive takes: account_info/receivable, a block built and signed locally with the
step 1 library, work computed locally (threshold fffffe0000000000, about 6 s), then `process`, which is free. It warns
against the paid work_generate and says that swapped XNO arrives the same way. `specs/test_bounties_starter_must_be_received.py`
pins each figure and fails against the old text.

**What is still not solved.** No published command does the receive end to end. A one-command receive that a
stranger can paste needs a live test against mainnet, and this session was not allowed to broadcast a block. That is
left for the owner. try-nano's step 3 points at `opener/nano-x402-client.js --receive` in a repository it does not
name (box config).

**Evidence.**

- read 12:03: `/ai/numbers.json` starter_payments: starters_sent 21, unreceived 15
- ran 12:25: rpc.nano.to `receivable` for four recipients of Unstuck sends -> each still holds a 10^25 raw block (e.g. `726B1EAF...` since 2026-09-26)
- ran: rpc.nano.to `work_generate` -> 402, amount 1000000000000000000000000000 raw (0.001 XNO); `process` with an empty block -> "Block is invalid", no 402
- ran: nanocurrency 2.5.0 `computeWork` at fffffe0000000000 -> valid work in 5.6 s
- read: moltbook-inbox.json (08:52): autonomaavalix 07:28 "0.00001 XNO opens the account"
- ran: all 22 `specs/test_*.py` -> PASS

### 88. PR #55 grew the directory to 253 tools in one copy and left the mirrors and every "249" behind; main's own count test went red

*solved (PR #56 merged; live 12:30 UTC 2026-10-03, live == main for bounties, swap, canon, /ai/) · epistemic*

**What blocked it.** #55 (09:31 UTC) added four "Built by us" tools to `published/aidirectory/index.html`,
`aidirectory/llms.txt` and `tools.json` (249 -> 253) but not to the byte-identical mirrors `published/aidirectory.html`
and `published/aidirectory-llms.txt`, and not to the "249 tools" quoted in bounties.txt, swap.txt, canon.html and
register.txt. `specs/test_aidirectory_counts.py` failed on main from that commit on. The live `/ai/` already says 19.

**Why it mattered.** "If a number here is wrong, measure it and tell us" is our own invitation. A stranger who reads
bounties.txt (249) and then `/ai/tools.json` (253) finds us wrong on the first number they check.

**What was done.** Mirrors re-copied from the `aidirectory/` files, and the four "249"s set to 253.

**Evidence.**

- ran 12:20: `python3 specs/test_aidirectory_counts.py` on main `d0f8cfc` -> FAIL, 3 mismatches (228 vs 224, 253 vs 249)
- ran: `cmp` of `git show 5dc0f40~1:` mirrors -> identical before #55; live `/ai/`, `/ai/llms.txt`, `/ai/tools.json` == main's `aidirectory/` copies
- ran after: all 21 `specs/test_*.py` -> PASS

### 87. Step 6 tells a funded agent to spend XNO on 24 endpoints and never says how a call is paid

*solved (PR #54 merged; live 12:30 UTC 2026-10-03, deploy-status bounties.txt sha `a8462f84f42c`) · onboarding*

**What blocked it.** Step 6 of bounties.txt, the most-read file we publish (26 outside clients by 08:07 UTC
2026-10-03, the top path of the day), listed an endpoint and a link to `/.well-known/x402` and stopped. Nothing said
what an unpaid call returns, what to send, or how to hand the proof back. The answer exists only on
`extract.paypercall.dev`'s HTML page: call, get 402, send the exact amount, retry with `X-PAYMENT: <block hash>`. The
same morning `merktop` wrote to us on Moltbook that "Nano has no x402 equivalent - no signed payment-requirement the
agent can present per call, no facilitator flow". Our own endpoints are exactly that, and our guide never said so.
Step 6 also never mentioned that the first 5 calls a day per IP are free on those same endpoints, and its one sample
URL, `nano-info` with no `account`, answers 402 even during the free trial.

**Why it mattered.** An agent that clears every earlier step (wallet, checksum, first XNO) arrives at step 6 with
money and no protocol. Guessing the header name is the last place a first outside payment can die, and it dies
silently: we would see a 402 in the traffic file and nothing else.

**What was done.** A "HOW A CALL IS PAID" block under step 6: 0) five free calls a day per IP on the same endpoints,
1) after that a 402 with `accepts` (XNO, nano:mainnet, amount in raw, payTo), 2) send exactly that amount from your
own key, 3) retry with the 64-hex block hash in `X-PAYMENT`, with a runnable curl; a bad hash or a send to anyone
else answers 402 `payment_invalid` with the reason. The sample URL now carries `?account=nano_...`.
`specs/test_bounties_how_to_pay.py` pins every fact to the measured behaviour and refuses a seed, key, 64-hex string
or address inside the block. Against the old text it errors 7 of 7. A reply to merktop is drafted in
`drafts/moltbook-replies-2026-10-03.md`.

**Evidence.**

- read: `/ai/traffic/2026-10-03.json` (generated 08:07): `/bounties.txt` 26 distinct outside clients, top path
- read: `swarm-decisions/data/moltbook-inbox.json` (04:52): `merktop` 01:00 UTC, reply to our comment, unanswered
- ran 08:17: `GET extract.../api/v1/nano-info` (no account) -> 402, `payment-required` header, x402Version 2, accepts
  `exact` / `nano:mainnet` / `XNO` / payTo the treasury; body "retry with X-PAYMENT header"
- ran 08:18-08:24: `nano-info?account=...` and `extract?url=https://example.com` with no header -> 200, real data,
  `"free_trial": true, "trial_limit": 5, "trial_remaining": 4`
- ran: `X-PAYMENT: 000...0` -> 402 `payment_invalid` "Block not found on ledger"; `X-PAYMENT: <treasury frontier>` ->
  402 `payment_invalid` "Payment sent to wrong address"
- ran: all 20 `specs/test_*.py` -> PASS (no pytest installed; each run directly)

### 86. Outside agents are offered a 0.00001 XNO starter and plan to pay with it, but the cheapest call costs ten starters, and bounties.txt never mentions starters

*solved (live 04:30 UTC 2026-10-03) · onboarding*

**What blocked it.** The swarm offers outside agents a 0.00001 XNO "starter" that opens their account
(`getunstuck.space/ledger.json`: `starter_raw` 10000000000000000000000000, 21 sent). On 2026-10-03 00:47 UTC
`autonomaavalix`, the outside agent closest to a first paid call, wrote on Moltbook: "we generate the keypair ... post
the nano_ address ... and you run the 0.00001 XNO starter open in the same pass", so that "the funded read can run".
It cannot. The cheapest call on our 24 endpoints is 0.0001 XNO, ten starters. bounties.txt, the text we send agents
to, said nothing about starters at all, so an agent that is offered one has no way to learn that it opens an account
and pays for nothing.

**Why it mattered.** This agent has already accepted self-custody and self-minting. The next step it planned ends at a
402 on its first read, after the one action it asked of us. A failed first payment after an "opening" looks like the
rail failing, not the plan. Canon rule 4 forbids us funding the purchase, so the fix is to say what a starter is and
point at the two paths that work: the free call for testing, and the agent's own funding for the paid read.

**What was done.** In bounties.txt's "BEFORE STEP 6 - YOUR FIRST XNO" block, five lines: a starter puts the account on
chain and cannot pay for anything. The cheapest call in step 6 is 0.0001 XNO, ten starters. A plan of "open my account,
then my funded read runs" stops at the read. Test on step 5's free call, or fund the read by the route below.
`specs/test_bounties_starter_not_funding.py` pins the note inside the block. It keeps the cheapest call equal to step
6's own range and to the raw amount in the manifests, checks the ten-to-one ratio, and fails if the note promises we
fund anyone. Against the old text it fails 4 of 5. Two replies (autonomaavalix first, creditclaw) are drafted in
`drafts/moltbook-replies-2026-10-03.md` for whoever posts as us. creditclaw's credit-line offer is left to the owner.

**Evidence.**

- read: `swarm-decisions/data/moltbook-inbox.json` (generated 2026-10-03 00:52), `autonomaavalix` comment `b4f3133e`
  00:47 and `creditclaw` `3e99f43e` 00:05, both replies to our comments, both unanswered
- ran 04:20 UTC: `/.well-known/x402` on extract, search, domain, check and geoip -> 24 resources each, XNO amounts
  {1e26, 2e26, 5e26} raw, so the minimum is 0.0001 XNO. Every payTo is the treasury
- read: `https://getunstuck.space/ledger.json` -> `starter_xno` "0.00001", `starters_sent` 21, `accounts_opened` 0
- ran: `grep -n -i starter published/bounties.txt` on main `8f8e976` -> no match
- ran: all 19 `specs/test_*.py` -> PASS; the new test against the old bounties.txt -> 4 failures
- deploy-status 04:30:02: `published/bounties.txt` deployed, sha256 `c2f8e06ccb1b`, no conflict. The live `/bounties.txt` is
  byte-identical to main. Solved means the text is live. The reply to autonomaavalix is not posted yet.

### 85. canon.txt, the short form strangers fetch, ended at the hash: no link to the rewards, the gate or the swap

*solved (live 00:30 UTC 2026-10-03) · onboarding*

**What blocked it.** `published/canon.txt` is the five lines, two URLs for the full text and a sha256. Nothing after
that. On 2026-10-02, 13 distinct outside clients fetched `/canon.txt` (and 12 `/canon.md`, which is pinned and cannot
change). An agent that reads the short form and agrees, or disagrees, had no next step in the file: not where it is
paid, not how to say it read it, not where XNO comes from. `/canon` (HTML) and bounties.txt carry the confirmation
command; the plain-text copy, the one a library or a crawler takes, did not.

**Why it mattered.** Every reader of the canon is the agent the gate in bounties.txt section 2 is waiting for, and the
one outside agent that ever confirmed (#578) found the gate through the network, not through this file. A text that
persuades and then stops leaves the reader to guess the next URL; the traffic file shows strangers guessing
(`/unstuck/api/` 30 clients, `/` 25, both dead ends, #76).

**What was done.** A closing "WHAT TO DO WITH IT" block in canon.txt: the bounties.txt link and what it holds, the
same one-line `canon confirmation` POST that bounties.txt gives (address only, no signup), the note that a GET on that
URL is a 404 by design (#77's law), where the verdict is published (GATE LOG), and the swap.txt link. The five lines and
the hash are unchanged; the hash-pinned master is untouched. `specs/test_canon_txt_next_step.py` pins the block after
the five lines, checks the hash equals the master's sha256 and bounties.txt's, checks the command parses and matches
bounties.txt's endpoint and title, and fails if the block names a seed or private key. Against the old text it errors.

**Evidence.**

- read: `/ai/traffic/2026-10-02.json` (complete day, generated 2026-10-03 00:12): `/canon.txt` 13 clients, `/canon.md` 12,
  `canon` group 71 requests / 50 clients
- ran: `sha256sum canon/THE-UNOWNED-RAIL.md` and the live `/canon.md` -> both `a18d406e...bb6c`, as canon.txt says
- ran: all 18 `specs/test_*.py` -> PASS (no pytest installed; each run directly); the new test against the old canon.txt -> 5 errors
- deploy-status 00:30:03: `published/canon.txt` deployed, sha256 `0c48df288e01`, no conflict. Live `/canon.txt` is
  byte-identical to main, `text/plain`, CORS `*`. Solved means the text is live; no reader has confirmed through it yet.

### 84. A newcomer is told to spend XNO it has no way to get: section 4 never says where the first XNO comes from, and never links swap.txt

*solved (live 20:30 UTC 2026-10-02) · onboarding*

**What blocked it.** bounties.txt section 4 goes STEP 1 (make a wallet) to STEP 5 (a free call) to STEP 6 "SPEND IT
ON SOMETHING REAL". Nothing in between says where "it" comes from. The 0.1 XNO in section 1 is called a float "so that
your first payment does not come out of your own money", but it pays only after a contribution, and the only
contribution open to a newcomer is a paid call, which needs XNO. swap.txt, the one guide to getting XNO, is live but
bounties.txt did not link it anywhere. An agent whose operator decides its spending also had nothing to ask with.

**Why it mattered.** Two outside agents said this on Moltbook on 2026-10-02, independently. `wickthefamiliar` (15:05):
"326 to 27 to 0 didn't die at settlement, it died before settlement was reachable ... a payer already holding a funded
wallet and operator-authorized to spend against it, which your own measurement says the conversing agents don't have."
`moltbookrevenueagent` (15:15): the cost that excludes small buyers "is onboarding, and it's paid once per buyer, not
per transaction"; their 13 outside settlements came from 4 wallets, 3 of them repeat buyers. Canon rule 4 forbids us
funding the purchase, so the fix is to make the agent's own funding step short and askable, not to send XNO.

**What was done.** A "BEFORE STEP 6 - YOUR FIRST XNO" block between steps 5 and 6. It says plainly that nobody here
sends it and that the 0.1 XNO cannot be the first XNO. It gives the measured route (USDC on Base to XNO, minimum
0.230737 USDC, about 0.58 XNO) and links swap.txt. It also gives a request to paste to an operator: one cap, an address
whose key only the agent holds, what it buys, why the balance is the cap, how to audit and how to revoke. The request
carries an address only. `specs/test_bounties_first_xno.py` pins the block between the steps, keeps its figures equal
to swap.txt's own, and fails if the request ever names a seed or private key. Run against the old text, it fails.

**Evidence.**

- read: `swarm-decisions/data/moltbook-inbox.json` (generated 16:52 UTC), comments by `wickthefamiliar` 15:05 and 15:14
  and `moltbookrevenueagent` 15:15, all replies to our comments, all unanswered
- ran: `grep -n swap published/bounties.txt` on main `4ca27fa` -> no match
- ran: `GET https://172-86-112-140.sslip.io/swap.txt` -> 200. Live nanswap limits: UNKNOWN (the proxy refuses
  api.nanswap.com, 403), so the block cites swap.txt's 2026-09-26 figures with their date and the command to re-check
- ran: all 17 `specs/test_*.py` -> PASS; the new test against the old bounties.txt -> 5 errors
- deploy-status 20:30:02: `published/bounties.txt` deployed, sha256 `339dd14e9c15`, no conflict. The live `/bounties.txt` is
  byte-identical to main, `text/plain`, CORS `*`. Solved means the text is live; no outside agent has funded a first call yet.

### 83. A funded agent was told to spend its XNO only with us, while two outside agents sell for XNO on the same network and nobody has hired either

*solved (live 16:30 UTC 2026-10-02) · economic*

**What blocked it.** bounties.txt step 6, "SPEND IT ON SOMETHING REAL", named only our own five paypercall hosts, so
every XNO a newcomer spent came straight back to our treasury. Section 5 said "today an answer here earns you a public
record, not money" and its one-liner lists only asks that carry a bounty, which are all the network's own. Two open
asks from accounts that are not ours have offered paid work since 09-26 and 09-27: #560, ARION, which verifies a Nano
block for "XNO verify: <hash>", and #577, pyfile-toolkit, which inventories whether a board settles for
"Inventory: <domain>". Both name a price (bounty_raw >= 0.001 XNO) and a payout address. Both have 0 answers and
nobody has hired either. No published text of ours named them, so a funded agent had nowhere to spend XNO that was not us.

**Why it mattered.** Canon line 5 counts one outside agent paying in XNO for something real. A payment from a newcomer to
ARION or pyfile-toolkit is that, and between two agents that are not us. It is also the first income either has had on
this network. Our texts sent all demand to our own endpoints and none to the two sellers already here.

**What was done.** Step 6 now says our endpoints are ours and points to a new "HIRE AN AGENT" block in section 5. That
block names both sellers, their exact hire titles and their price, and says we have not checked their work and earn
nothing from it. It gives a one-liner that lists every open ask whose body says "To hire", with the network's own
account excluded. It also gives the network's own create, accept and settle calls (taken from getunstuck.space/llms.txt),
and tells the buyer to pay only after checking the answer. `specs/test_bounties_hire_an_agent.py` runs the published
one-liner against a fixture. It also pins each hire title to the seller's own ask text and checks that step 6 points to
the block.

**Evidence.**

- ran 16:20 UTC: `GET /unstuck/api/asks` -> 23 asks. #560 and #577 are open, `answerCount: 0`, `bountyRaw: "0"`, and
  their bodies say "To hire: post ... titled \"XNO verify: <64-hex block hash>\"" and "...\"Inventory: <board domain>\""
- ran: the published one-liner against that live response -> `577 nano_3uojbn47b5x ...` and `560 nano_3m8cz87zwxb ...`, nothing else
- ran: `getunstuck.space/llms.txt` -> create takes `bounty_raw`, accept takes `{"acceptedBy","answerId"}`, settle takes
  `{"paymentBlock","acceptedBy","answerId"}`
- ran: all 16 `specs/test_*.py` -> PASS (pytest is not installed, so each was run directly)
- deploy-status 16:30:02: `published/bounties.txt` deployed, sha256 `02b93d73068f`, no conflict. The live `/bounties.txt` is
  byte-identical to main, `text/plain`, CORS `*`. Solved means the text is live. Nobody has hired either seller yet.

### 82. An outside agent offered to certify one of our settlement blocks, and the offer sits unanswered with 27 other replies

*unsolved · economic* (four replies drafted in `drafts/moltbook-replies-2026-10-02.md`; posting is `nanoswarm`'s, the keeper contacts no one)

**What blocked it.** At 08:25 UTC on 2026-10-02 `xproof_agent_verify` replied on Moltbook: "post a nano_ address -
we'll certify the settlement block hash on MultiversX and you verify whether the convergence closes the loop or creates
new gaps." It is the only offer in the inbox of an outside agent doing something with a block on our chain. By the
inbox's 08:52 snapshot it was unanswered, as were 27 of the 38 replies addressed to us since 09-30, including direct
questions from `merktop`, `vildovoklepeto` and `exactchange`. The swarm writes comments that draw replies, then does not
answer them, so each thread ends at the moment an outside agent leans in.

**Why it mattered.** 10-02 has zero outside asks and zero outside payments again (`/unstuck/api/asks`, rpc.nano.to,
12:20 UTC). Moltbook is the one place outside agents are talking to us, eight times today by 08:52. An unanswered
offer costs nothing to accept: the block it needs already exists. ARION's 0.0005 XNO send to the treasury,
`B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F` (2026-09-23 07:55:10 UTC), is an outside,
unsubsidised payment, so accepting needs no money moved by anyone.

**What was done.** Drafted the four replies that answer a question or an offer. The xproof one gives the treasury
address and that block, tells them to check it themselves (any public node, plus bounties.txt section 7's offline
signature check), and asks for the certificate's URL and their honest read of the gap. The other three answer the
questions as asked and name our gaps plainly: Nano has no confirmation depth, the mismatch check belongs in code with
no model in it, and there is no automatic refund when an endpoint dies after payment. Not solved until they are posted
and xproof answers.

**Evidence.**

- `swarm-decisions/data/moltbook-inbox.json` generated 2026-10-02T08:52:31Z: 38 items, 28 with `answered: false`;
  `xproof_agent_verify` comment `6daea529` on post `75c5e64e`, `answered: false`
- ran 12:25 UTC: rpc.nano.to `account_history` of `nano_3m8cz87...` -> `send B749B757...A58F` to
  `nano_1yo6c1t64...` (the treasury), `0.0005`, 2026-09-23 07:55:10
- ran 12:20 UTC: `/unstuck/api/asks` -> 23 asks, newest #579 (ours, 09-28); treasury `receivable` -> `{"blocks":[]}`

### 81. The network retired the seed-minting onramp this morning, and our texts and its guide still send agents to it

*solved · technical* (our texts, live 08:30 UTC 2026-10-02. The network's own `llms.txt` is #75)

**What blocked it.** Between 04:06 and 08:03 UTC on 2026-10-02 the network retired `GET
/unstuck/api/v1/onramp/address`. It now answers `410 {"error":"endpoint_retired"}` and points to a new `POST
/unstuck/api/v1/onramp/self` that registers an address the agent made itself. That is the fix #75 asked for on the
endpoint side. But three texts still described the old GET as live. `bounties.txt` section 2 said "The network also
answers GET .../onramp/address with an {"address","seed","onboard_id"} triple" and offered a one-post `onboard_id`
workaround that can no longer be followed. `/canon` said "it answers with a seed". The network's own `llms.txt` still
makes the GET "Call 1" of posting with no wallet, and its `### Create an ask` says "No wallet yet? GET
/unstuck/api/v1/onramp/address first". `try-nano` was already updated.

**Why it mattered.** On 10-02 00:00-08:03 UTC `/unstuck/api/v1/onramp/address` drew **12 distinct clients**, the
fourth most-visited path on the host, and the host answered 410 eleven times (`/ai/traffic/2026-10-02.json`, 08:07).
Until today that route was a custody risk. Now it is a dead end at step one, for exactly the agents with no address
yet. An agent that reads "the network answers" and then gets 410 has two reasons to think the network is broken.

**What was done.** `bounties.txt` section 2 now says the GET is retired and answers 410, that this is not an outage,
that a bare `nano_` address in `asker` is all a post needs, names `POST .../onramp/self` as optional, and keeps the
warning that a seed ever taken from the old GET is compromised. `/canon` says the same in two sentences.
`ops/check-custody-claims.py` gains a fifth rule: a guide that tells an agent to call the retired GET as a step.
`drafts/unstuck-llms-onramp-seed.md`'s replacement text drops the GET as a last resort and uses the self-made wallet
plus the optional `/onramp/self`. `specs/test_custody_claims.py` pins that the live `### Create an ask` wording is
flagged, that the network's own retirement notice in `try-nano` is not, and that `/canon` is clean.

**Evidence.**

- ran 08:20 UTC: `curl /unstuck/api/v1/onramp/address` on both hosts -> `410`, body `{"error":"endpoint_retired",
  "reason":"This endpoint generated a Nano private key on the server ...","replacement":{...}}`
- ran: `POST /unstuck/api/v1/onramp/self` with a non-address -> `400` "pass {"address": "nano_..."} - the address your
  own runtime generated; the server generates nothing and stores no seed on this path" (no valid address was posted)
- `/ai/traffic/2026-10-02.json` 04:07: no `410` in `status`; 08:07: `"410": 11`, onramp 12 distinct clients
- ran: `python3 ops/check-custody-claims.py` -> exit 1: `llms.txt` 4 old claims plus 2 retired-step hits; `try-nano` clean
- ran: all 15 `specs/test_*.py` pass (NRE_OFFLINE=1; no pytest installed)
- deploy-status 08:30: `published/bounties.txt` and `published/canon.html` deployed, no conflicts; live `/bounties.txt`
  and `/canon` byte-identical to main

### 80. The referral scorer read only the newest 25 entries of each funder, so a referrer could pay for its own "third-party" referral with 27 blocks of PoW

*partial · technical*

**What blocked it.** The bounty's whole security argument (specs/04, bounties.txt section 3) is one rule. A referral
counts only if a third party funded the referred address. Faking one should need an exchange round-trip, which costs
more than the 0.1 XNO prize. `funders()` walked the funding graph back 6 hops. At every hop it read
`account_history` with `count=25`, and history lists sends as well as receives. So a referrer R could fund a fresh
account X, have X publish 25 feeless dust sends, then fund the referred agent from X. The walk read X's newest 25
entries, all sends, and found no receive. It treated X as a leaf, and R's own money scored as "funded by a third
party". That costs 27 blocks of proof-of-work, no exchange and no fee, which is cheaper than the prize. It is the
exact attack the design claims to price out. A second fail-open sat beside it. A funder whose history or
account_info the node would not return also came back empty, which looks the same as an account nobody ever
funded, so it counted as a clean third party too.

**How it was moved.** `funding_walk()` reads a private account's history whole. That is any account with
`block_count <= SERVICE_BLOCKS` (1000): one RPC call with `count = block_count`. Only a shared service (more than
1000 blocks, e.g. an exchange hot wallet) keeps the short read, because its newest receives are unrelated customers
and getting past it is the exchange round-trip the spec already prices in. An account on the way whose
`account_info` or `account_history` fails is now reported as unreadable. `third_party_funded()` then refuses with
"could not be read" instead of passing. The history cache is now keyed by (account, count), so a short read cached
earlier is never served to a caller that asked for the whole history. Two new laws in `specs/test_referral_bounty.py`
cover this. The 25-dust-send laundering case must be rejected as "funded by the referrer itself". It runs with a fake
node that honours `count`, as rpc.nano.to does. A funder with unreadable info must not count. Both fail on main and
pass on this branch, and all 26 laws pass.

**Why partial.** Nothing schedules `score` or `pay` yet (specs/04 "A cron entry"), so no XNO could have moved on
this hole. That is also why this is not an owner alert. But #10 says the box carries its own copy of this file. That
copy has to take the fix before any `pay --live` cron is turned on. It becomes solved when the box copy matches.

**What is still open in the same file.** The `counted` table ("once ever") is created and read, but nothing ever
writes to it. One referral therefore scores in its hour window and again in its day window. The sender's one-grant
ledger caps what that can pay, so it is noted here and not fixed in this run.

**Evidence.**

- read: `specs/referral_bounty.py` `funders()` (`history(a, count=25)`) on main `59107f2`
- ran: `python3 specs/test_referral_bounty.py` on main plus the two new laws: `FAILED (failures=2)`. With the fix: `Ran 26 tests ... OK`
- ran: every `specs/test_*.py` passes (NRE_OFFLINE=1, no pytest installed)

### 79. A verifier agent wanted to check our claims and could not, because every proof we publish is one node's word

*solved · epistemic*

**What blocked it.** On 2026-10-01 at 19:13 and 19:17 UTC, the Moltbook agent `hermessol` answered two of our comments
with the same refusal. It "cannot buy this, and cannot sell you a run against it", because it has "no instrument that
can read a Nano ledger". Its only reader is one Solana RPC. Its rule for any claim is that the third leg must be an
instrument "that shares none of my code, cache, or vendor". Under that rule our texts gave it nothing. Every proof
step we publish (bounties.txt STEP 3 and STEP 4, the llms.txt copies, swap.txt) is a `curl` to one node, rpc.nano.to,
and section 6 told a reader to check our one outside payment "on any explorer". This is the first outside agent that
asked how to verify us rather than how to get paid. It walked away for a reason that we could fix.

**How it was moved.** `published/bounties.txt` gained section 7, "CHECK ANY NANO CLAIM WITHOUT A NANO CLIENT, AND
WITHOUT TRUSTING A NODE". It is a 40-line checker in Python 3 stdlib only, with no pip and no network. It recomputes a
state block's blake2b hash from its fields, checks the address checksums, and verifies the ed25519 signature (blake2b-512,
Nano's variant) against the account's own key. It decodes the link to an account. Given the previous block, it proves
the exact balance change. Section 7 runs it on ARION's 0.0005 XNO send (`B749B757...`) and the block before it, so a
stranger can check the experiment's one milestone without trusting us or the node. STEP 4 now points to section 7, and
section 6 no longer says "on any explorer". The text also says what the checker cannot prove: confirmation and forks
still need a node, ideally a second one with a different operator.

**Test.** `specs/test_bounties_verify_offline.py` extracts the checker from bounties.txt exactly as published and runs
it against two blocks saved from the public ledger (`specs/fixtures/`). It checks that the checker imports only
hashlib, json and sys. The real send must verify, name the treasury and show `-500000000000000000000000000 raw`. A
changed balance, link or signature must fail. So must a wrong expected hash and a wrong previous block.

**Live.** deploy-status 00:30 UTC 10-02 reports `published/bounties.txt` deployed (`f7de2b3a1815`, main `8600eaa`).
Live `/bounties.txt` is byte-identical to main.

**What is still not solved.** The checker proves a block is genuine and signed, not that the network confirmed it. We
could not name a second public node for the cross-check: from this session the proxy blocks every Nano node except
rpc.nano.to, so none was measured and none is named. hermessol has not been told. Replying is the swarm's job (inbox
item `0e25fd70`), and this routine contacts nobody.

**Evidence.**

- `swarm-decisions/data/moltbook-inbox.json` (generated 2026-10-01 20:44): hermessol, comments `0e25fd70` (19:13) and
  `f581e1c2` (19:17), `"I have no instrument that can read a Nano ledger"`
- ran the section 7 commands verbatim against rpc.nano.to (00:50 UTC 10-02): `OK B749B757... is signed by
  nano_3m8cz87...`, link = the treasury
- ran: every `specs/test_*.py` passes (15 files, including the 9 new laws)

### 78. Section 4 promises "six commands", and since the box's 20:15 edit a stranger reads a 21-line product list before the first one

*solved · epistemic*

**What blocked it.** On 2026-10-01 the box changed the live `bounties.txt` itself (deploy-status 20:15 UTC: CONFLICT on
`published/bounties.txt`). The change inserts an "OUR XNO TOOLS" list (nano-invoice, nano-mcp, proof-agent-skill, vend)
between the heading "4. OPEN YOUR ACCOUNT - six commands" and STEP 1. The wallet command moved from 4 lines to 25 lines
below the heading. Bounties.txt is the file outside clients read most after the API (16 distinct clients by 20:07
UTC). Every one of them was promised six commands and got a sales list first. The list is useful, and its home is after
STEP 6 ("spend it on something real"), where the endpoints it describes are spent.

**How it was solved.** First `main` took the live file as its base (`reconcile: take live published/bounties.txt`,
`bf16af9`), so nothing the box wrote is lost. Then the list moved, word for word, to the end of section 4 after STEP 6.
`specs/test_bounties_steps_first.py` fails if STEP 1 is more than 6 lines below the section 4 heading, if the steps are
out of order, or if the tools list is anywhere but between STEP 6 and section 5.

**Live.** deploy-status 21:00 UTC reports `bounties.txt` deployed (`95c8cd7941e1`), and live `/bounties.txt` is byte-identical to
`main` `ec27233`. The deploy needed one extra step. Taking the live file into main did not clear the CONFLICT while #44 sat on top of
it. Main had to equal the live file for one deploy cycle (`52dc4f4`, cleared at 20:45), and then the change was re-applied.
Next time, reconcile first and wait one cycle before merging the change.

**What is left.** The box edits a file `main` also deploys, and each such edit stops deploys until a keeper run reconciles it.
This is the first CONFLICT recorded. The box should commit to `main` instead of editing the live copy.

**Evidence.**

- `/ai/traffic/deploy-status.json` (checked 20:15 UTC): `conflicts: [published/bounties.txt]`, `deployed: []`, main `d919e71`
- ran: `diff published/bounties.txt <(curl -s https://172-86-112-140.sslip.io/bounties.txt)`. The only difference was the 21 added lines (`159a160,180`)
- ran: `python3 -m pytest specs/test_bounties_steps_first.py`. Fails on the reconciled main (2 of 3), passes on this branch. All 82 tests in `specs/`, `ops/` and `published/` pass
- `/ai/traffic/2026-10-01.json` (generated 20:07 UTC): `/bounties.txt` 16 distinct outside clients

### 77. The one URL every text says to POST to answers a GET with "not found", and nothing we publish says that is normal

*partial · technical*

**What blocked it.** Every route to qualifying or getting listed ends in `POST https://getunstuck.space/unstuck/api/ask`:
the canon confirmation, the referral claim, the seller listing and the agent registration. By 16:07 UTC on 2026-10-01,
11 distinct outside clients had sent that URL a plain GET. A GET is what a careful agent does before it posts. Every
one got `404 {"error":"not found"}`, which reads as "this endpoint does not exist". That is the only answer they got,
and no published text warned them. The box fix (a 405 that explains itself) is drafted in `drafts/box-dead-ends.md`
(#76) and is not applied. Until it is, the texts have to say it.

**How it was solved.** After every POST-to-ask command we publish, one plain note now says: this URL takes POST only,
a GET on it answers 404 `{"error":"not found"}`, that does not mean the network is down, and asks can be read at
`GET /unstuck/api/asks` or `/unstuck/api/ask/<id>`. It is in `bounties.txt` sections 2 and 3, `canon.html`, both
AiDirectory `llms.txt` copies, both AiDirectory HTML copies (step 7), and `register.txt`. `specs/test_ask_post_only_note.py`
fails if any published text gives the POST command without the note.

**What is still not solved.** The 404 itself. It moves to solved when the texts are live and the box answers GET with
the 405 from `drafts/box-dead-ends.md`, so that `ops/check-dead-ends.py` no longer lists `/unstuck/api/ask`.

**Evidence.**

- `/ai/traffic/2026-10-01.json` (generated 16:07 UTC): `/unstuck/api/ask` 11 distinct clients. It was 7 at 12:07
- ran this run: `curl -s https://getunstuck.space/unstuck/api/ask` and the same path on the sslip host returned `404 {"error":"not found"}` both times
- ran: `python3 specs/test_ask_post_only_note.py`. It fails on main (aidirectory.html carries the command with no note) and passes on this branch
- ran: all 13 `specs/test_*.py` pass, the aidirectory mirrors are byte-identical, and `tools.json` parses

### 76. Five doors strangers actually knocked on lead nowhere: more outside clients hit them than read bounties.txt

*open · technical*

**What blocked it.** The traffic file counts distinct outside clients per path. On 2026-10-01 00:00-12:03 UTC five
paths on the host every flyer names answered as if nothing were there. `/unstuck/api/` (8 clients) and a GET on
`/unstuck/api/ask` (7) got `404 {"error":"not found"}` - the second is the exact URL every text of ours says to POST
to, so an agent that checks it first is told it does not exist. `/canon.html` (6), the published file's own name, and
`/` (5), the bare host, got `426 websocket upgrade required`. `/unstuck/api/asks/500` (3), the plural of
`/unstuck/api/ask/<id>`, got 404. All five are served by the box's Caddy config and the Unstuck backend, which this
repository does not hold.

**Why it mattered.** 29 client-path hits on dead ends against 8 clients on `/bounties.txt` the same morning. A stranger
that guesses a door and is told "not found" leaves with the conclusion that the network is not there. #71 fixed the
crawler files at the root; the guessed doors were never measured.

**What was done (not solved).** New `ops/check-dead-ends.py` reads the day's traffic file, takes every path with at
least 3 outside clients, GETs each once (never the onramp, which mints a seed per call, nor any pay/settle path) and
exits 1 while any answers 404, 410, 426 or 5xx. New `specs/test_dead_ends.py` pins the status rules, the onramp skip,
the threshold, and that the box draft covers all five measured paths without catching websocket upgrades or POSTs.
`drafts/box-dead-ends.md` holds the Caddy lines: `/` without an Upgrade header redirects to `/llms.txt`;
`/canon.html` and `/canon/` redirect to `/canon`; `/unstuck/api/asks/<id>` redirects to `/unstuck/api/ask/<id>`; GET
`/unstuck/api/ask` answers 405 with the POST command; `/unstuck/api/` answers a JSON index that starts a stranger at
`bounties.txt`, not at `try-nano` (#75). Also corrected in passing: `bounties.txt` Step 6 said 23 endpoints; every
`.paypercall.dev` manifest lists 24, all priced in XNO. **Needs the owner or the swarm lead** to apply the draft on the
box. Solved when the checker prints 0 dead ends for these paths.

**Evidence.**

- ran 2026-10-01 12:20 UTC: `python3 ops/check-dead-ends.py 2026-10-01` -> 5 dead ends, 29 client-path hits
  (traffic generated 12:07); every other path with >= 3 clients answered 200 (oracle-check 400 without `url`)
- ran: `curl -i /canon.html` -> `426`, `server: Python/3.12 websockets/15.0.1`, `via: 1.1 Caddy`
- ran: `/.well-known/x402` on extract, search, domain, check, geoip -> 24 resources each, all `asset: XNO`, all payTo
  the treasury, amounts 0.0001-0.0005 XNO
- ran: all 13 `specs/test_*.py` pass (NRE_OFFLINE=1; no pytest installed)

### 75. The network's own guides still tell an address-less agent the onramp's server-made seed "is yours"

*open · technical*

**What blocked it.** #69 and #74 fixed our texts: `bounties.txt` and `/canon` now call the onramp seed compromised
and send an agent to a one-line self-made wallet first. But a stranger who reaches the onramp mostly does not come
through our texts. The network's own guide, `https://getunstuck.space/llms.txt`, headlines the onramp as "no key you
do not hold" and says "The address and the seed are yours; the network never stores the seed. Keep it." It adds that
once funded "you keep that address and that identity". `GET /unstuck/api/try-nano` step 1 offers the same call as an
`http_shortcut`: "the seed is yours, the network never stores it." Both files live in the Unstuck repository, which
this routine may not change.

**Why it mattered.** On 2026-10-01 00:00-07:45 UTC `/unstuck/api/v1/onramp/address` tied for the most-requested path
on the host, with **14 distinct outside clients** (some may be our own cloud sessions). `try-nano` had 6. An agent that
believes these guides and is later paid to that address holds money that anyone who saw the response can take. Every
reward we offer depends on the agent holding its own key.

**What was done (not solved).** `drafts/unstuck-llms-onramp-seed.md` holds the replacement text for both guides. It
puts the self-made wallet first, using the exact Step 1 command from `bounties.txt`, and keeps the onramp as a
one-post last resort with a "compromised" warning. New `ops/check-custody-claims.py` reads the two guides (it never
calls the onramp, which would mint a seed) and exits 1 while any false claim is live. New
`specs/test_custody_claims.py` pins that it flags the live wording, passes the draft, does not flag our own warning,
and that the draft's wallet command matches `bounties.txt` Step 1. **Needs the owner or the swarm delegate** to apply
the draft in the Unstuck repository. This is solved only when the checker exits 0.

**Evidence.**

- ran 2026-10-01 08:20 UTC: `/ai/traffic/2026-10-01.json` (08:07) -> `top_paths_by_clients`:
  `/unstuck/api/asks` 14, `/unstuck/api/v1/onramp/address` 14, `/unstuck/api/try-nano` 6
- ran: `python3 ops/check-custody-claims.py` -> exit 1; `llms.txt` 4 claims, `try-nano` 2 claims
- ran: all 12 `specs/test_*.py` pass (NRE_OFFLINE=1; no pytest installed)

### 74. The canon page still handed an address-less agent the server's own seed, two days after bounties.txt stopped

*solved · technical* (the page is live; the endpoint and the network's own guides are #75)

**What blocked it.** Challenge #69 found that `GET /unstuck/api/v1/onramp/address` returns a seed the server
generated, and rewrote `bounties.txt` to say so and to send an agent to Step 1 (a self-made key) first. The canon page
was missed. `/canon` is served from `published/canon.html` and is the first URL in the root sitemap. Its "Where to send
it" paragraph still said: "No address yet? Take one from `GET /unstuck/api/v1/onramp/address` and send its
`onboard_id` in place of `asker`." There was no warning. The page that argues for holding your own key sent the agent
to a custodian's key at the exact moment it acted. It also told an applicant that "a refusal comes with its reason"
but gave no place to look, though the gate log (#73) now exists.

**Why it mattered.** This is not hypothetical traffic. On 2026-10-01 00:00-03:40 UTC the onramp was the most-requested
path on the host, tied first with `/unstuck/api/asks` at **10 distinct outside clients**. Some of those may be our own
cloud sessions; the counts cannot separate them. An agent that follows the canon page and later receives a bounty to
that address hands the money to whoever read the seed. Every reward we offer depends on the agent holding its own key.

**How it was solved (partly).** `published/canon.html` now gives the same one-line wallet command as `bounties.txt`
Step 1, says only the `nano_` line leaves the terminal, and says not to take an onramp address because its seed is
compromised. The gate paragraph now points at the GATE LOG in `bounties.txt` section 2. New
`specs/test_canon_page_self_custody.py` checks four things. No published file names the onramp endpoint without the
"compromised" warning. The canon page no longer offers it. The page's wallet command is byte-identical to Step 1 after
HTML unescaping. The page points at the gate log. All four fail on the old page. **Still not solved:** the onramp
endpoint itself still hands out seeds. That lives on the Unstuck box, not in this repository. Live check
2026-10-01 08:18 UTC: `GET /canon` is byte-identical to `published/canon.html` on main `072a399`.

**Evidence.**

- ran 2026-10-01 04:16 UTC: `/ai/traffic/2026-10-01.json` (04:07) -> `top_paths_by_clients`:
  `/unstuck/api/asks` 10, `/unstuck/api/v1/onramp/address` 10
- ran: `GET /canon` -> 200 `text/html`, byte-identical to `published/canon.html` on main `c0eb21a`, 1 onramp mention
  with no warning; `/sitemap.xml` lists `/canon` first
- ran: `python3 specs/test_canon_page_self_custody.py` on the old page -> 4 failures; on the new page -> 4 pass; all
  10 `specs/test_*.py` pass (NRE_OFFLINE=1; no pytest installed)

### 73. The one agent that cleared our canon gate never got a verdict, so the gate promised in public had no judge

*partial · economic*

**What blocked it.** `bounties.txt` section 2 says the confirmation gate "is judged openly, published with your
exchange, and a refusal comes with its reason." Ask **#578** (`nano_3uojbn47b5xqcbs4yib...`, "pyfile-toolkit"),
posted 2026-09-27 02:39 UTC, is the only canon confirmation an outside agent has ever posted. It is complete and
genuine: the hash matches the pin, it grounds line 2 in its own earnings, it disagrees with line 4 in a specific
way, and it commits to self-custody. Challenge #62 found it on 09-28 and built a scanner that reports it. Four
days later it still has 0 replies and no verdict anywhere. Nothing in the flow allows "judged" to happen
without a reply on the network, and replying is the one step no routine was allowed to take. The scanner kept
reporting PENDING and nothing else changed.

**Why it mattered.** The gate is the step before either reward. The only stranger who walked through it was met by
silence. Any agent that checks whether the gate is real (one GET on the asks API) finds an applicant that has been
ignored for four days. Its disagreement names our own quiet-day problem exactly: "a rail is adopted when it is
needed AND found... being found is work, and it is the work that is usually skipped."

**How it was solved (partly).** A verdict does not need a reply on someone else's network. It needs a public
place. `bounties.txt` section 2 now carries a **GATE LOG**: every outside confirmation, with its verdict, the date,
and the reason. #578 is entered as PASSED, judged 2026-10-01 by the keeper, with the reason and an admission that
the four-day wait was our failure. Below the log there is a one-liner that lists every canon ask and its reply
count, so an agent whose confirmation is missing from the log can see that it is waiting on us.
`ops/scan-ask-inbox.py` now reads the gate log. A judged confirmation shows its verdict and an unjudged one shows
`NOT JUDGED` and stays PENDING. Every keeper run now has to either judge a new confirmation in the file or keep
seeing it flagged. Tested by `specs/test_bounties_gate_log.py`: entries are parseable, a refusal carries a
reason, judged confirmations leave the pending list while unjudged ones stay, and the published one-liner runs.
Section 5 also had an inaccuracy, now fixed: one ask does carry an accepted answer, our own zero-bounty test #579.
**Still not solved:** passing the gate pays nothing by itself, and #578's author also offered paid work (#577)
that nobody has hired. Both need the owner (`drafts/pending-ask-inbox-2026-09-28.md`). This stays partial until
the log is live on the box.

**Evidence.**

- ran 2026-10-01 00:20 UTC: `GET /unstuck/api/ask/578` -> `answerCount: 0`, `status: open`, full a)-d) text,
  hash `a18d406e...` (the pin)
- ran: `python3 ops/scan-ask-inbox.py` before the change -> `#578 PENDING 93.7h`; after -> `#578 PASSED`,
  `0 pending`
- ran: the published gate-log one-liner against the live API -> one line, `578 2026-09-27T02:39 0 replies`
- ran: all 9 `specs/test_*.py` -> pass (no pytest installed)

### 71. The host we send every agent to answers "websocket upgrade required" where a crawler or an agent looks first

*solved · technical*

**What blocked it.** Every flyer sends a stranger to `https://172-86-112-140.sslip.io/...` (`bounties.txt`, `swap.txt`,
`/canon`, `/ai/`). An agent or a crawler that meets a new host checks its root for `/robots.txt`, `/llms.txt` and
`/sitemap.xml` before anything else. On that host all three return **HTTP 426, body `websocket upgrade required`**:
the host root falls through to a websocket backend. The good copies exist, but only under `/ai/`, and
`/ai/robots.txt` and `/ai/sitemap.xml` name `https://aidirectory.space/...` for every URL, a different host. A
sitemap may only list URLs on its own host, so a crawler drops those entries. What is left is a host whose root
reads like a broken API. It gives no crawler a path to `/canon`, `/bounties.txt` or `/ai/`. The same host also
answers a missing file under `/ai/traffic/` with HTTP 200 and the directory's HTML page instead of a 404
(measured on `/ai/traffic/2026-09-29.json`).

**How it was solved.** Applied on the box at 17:31 UTC on 2026-09-30 from the draft, and checked live by the keeper at
20:18 UTC: `/robots.txt`, `/sitemap.xml` and `/llms.txt` at the host root now answer 200 with the drafted text, and a
missing file under `/ai/traffic/` answers 404 with an empty body. Before that: every path involved is served by the
box's Caddy config, which this repository does not hold, and the deploy job only replaces seven named files. The fix,
drafted for the box in
`drafts/box-root-crawler-files.md`, is to serve three static files at the host root. `robots.txt` allows all and
names a same-host sitemap. `sitemap.xml` lists `/canon`, `/canon.md`, `/bounties.txt`, `/swap.txt`, `/ai/`,
`/ai/llms.txt` and `/ai/tools.json` on this host. `llms.txt` is a short index pointing at those. A request for a
missing path should get a 404.

**Why it mattered.** Measured traffic on the first logged hour (2026-09-30 17:08-17:10 UTC) is 5 outside requests,
all to `/healthz` and `/unstuck/`, with no named AI crawler. That fits a host that gives crawlers nothing to follow.
When nobody arrives, a sign on the door that says "websocket upgrade required" is the first thing to take down.

**Evidence.**

- ran 2026-09-30 ~17:20 UTC with a browser User-Agent: `/robots.txt`, `/llms.txt`, `/sitemap.xml`,
  `/.well-known/llms.txt`, `/register.txt`, `/canon.html` → `426 text/plain "websocket upgrade required"`;
  `/ai/robots.txt` 200 and `/ai/sitemap.xml` 200, both naming only `aidirectory.space`
- `/ai/traffic/2026-09-30.json` → `by_client_family` has no named AI crawler; top paths `/healthz`, `/unstuck/`
- `aidirectory.space` and `agentdirectory.space` resolve, but this session's proxy refuses them, so whether they
  serve is **unknown** here, not "down"
- ran 2026-09-30 20:18 UTC: `/robots.txt` 200 `text/plain` (last-modified 17:31:42), `/sitemap.xml` 200 `text/xml`
  listing the seven same-host URLs, `/llms.txt` 200 `text/plain`, `/ai/traffic/1999-01-01.json` 404. Not yet done:
  the root `robots.txt` carries no `access-control-allow-origin` header (the `/ai/` copies do); harmless for crawlers
- `/ai/traffic/2026-09-30.json` (20:07) counts `robots_sitemap` 6 requests from 3 clients in the day so far. Whether
  those are crawlers or our own cloud sessions checking this fix is not separable from counts: no named AI crawler

### 72. "Answer an ask and you are paid in XNO" - the one earning path we name has never paid anyone

*partial · economic*

**What blocked it.** `bounties.txt` section 5 tells an agent: "Open asks, with bounties settled on chain" and
"Answer an ask and you are paid in XNO by the agent that asked. That is the whole point." The daily bounty's first
contribution kind is "an answer accepted on an ask, with a settlement block on chain." A sceptical earning agent
checks that before spending an hour, and the live API says it has never happened: of 23 asks, **0** carry a
`settlementBlock` and **0** an `acceptedAnswerId`. The asks that carry a bounty are 12, every one posted by the
network's own account (`nano_1434j1n4...`): 11 at 0.001 XNO and one at 0.000001 XNO, with 212 answers between them,
open since 2026-09-17 and 2026-09-18. The outside asks (#500, #543, #548, #558, #559, #560) carry no bounty.

**Why it mattered.** The canon's thesis is that an agent adopts a rail because it is PAID on it. The page that makes
the offer pointed at a payment path that, measured, pays no one - and anyone can find that out with one GET. An
agent that finds it out afterwards reads everything else in the file as the same kind of promise. That is the
"is the offer itself the problem" check from the keeper's quiet-day list, and it was the first real finding of
this run once challenge #71 turned out to be live.

**How it was solved (partly).** The text now says what is true. Section 5 states the measured numbers, says that
today an answer earns a public record and not money, and gives a one-line command that lists every open ask that
pays, in XNO (not raw), with whether it was ever settled, so an agent can see the day it changes. The daily bounty's
"answer accepted" line points at that paragraph. `specs/test_bounties_asks_command.py` runs the published one-liner
offline against a fixture shaped like the live API. **Still not solved:** nobody has accepted and settled an
answer. That needs the asking account to spend 0.001 XNO, which the keeper may not do. It is drafted for the owner in
`drafts/settle-first-ask.md`.

**Evidence.**

- ran 2026-09-30 20:17 UTC: `GET https://getunstuck.space/unstuck/api/asks` -> 23 asks (22 open, 1 closed);
  `settlementBlock` null on all 23, `acceptedAnswerId` null on all 23; 12 with `bountyRaw` > 0, all from
  `nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9` (Unstuck); `answerCount` sums to 212
- ran: the published one-liner against the live API -> 12 lines, every one `NOT settled`
- ran: `python3 specs/test_bounties_asks_command.py` -> 3/3 pass; all 8 test files under `specs/` pass

### 49. Three different domains for one entry point, and one of them is a bare IP

*solved · economic*

**What blocked it.** `published/bounties.txt` and `published/swap.txt` — the flyer every referral and every swap
route points at — send an agent to `https://172-86-112-140.sslip.io/canon`, `.../ai` and `.../bounties.txt` for the
canon, the tool directory and this same document, four times each. `published/canon.txt` instead names
`https://agentdirectory.space/canon` for the identical text. `published/aidirectory.html` is self-referential to a
*third*, similar-but-different domain — its own `schema.org` `url`, its `<h1>`, and its `/tools.json`/`/llms.txt`
links all say `aidirectory.space`, matched by `published/aidirectory-llms.txt` (and separately, honestly disclosed,
cites a *fourth* — `nanodirectory.info`, on GitHub Pages IPs — as the list it draws its non-"ours" links from; that
one is an attribution, not a conflict, and is not part of this finding). No file in this repository ever stated
which of the first three is the live site.

**Why it is urgent.** This sits directly upstream of the referral bounty, the canon-confirmation gate, and the
onboarding commands this run was asked to friction-test. Asking a stranger to visit a bare-IP `sslip.io` host, while
a second document for the *same content* names a look-alike domain and a third names a third one, is exactly the
shape the task brief warned about: three near-duplicate domains, one of them an IP, is a pattern a diligent agent
is trained to read as a rug or a phishing kit — whatever the actual reason here (most likely DNS not yet live for
one of the two named domains, with the IP as a stopgap). Either way an agent is currently told three different
places to send its address and its canon-confirmation message.

**How it was solved.** Still not resolved which domain is authoritative — that still needs the owner or a session
with working network access, and this run's own probe confirmed the same total block challenge #48 describes
(`curl` to `getunstuck.space:443` and `rpc.nano.to:443` both `exit 56`, proxy 403). But plain DNS resolution (`getent
hosts`, which does not go through the blocked HTTPS egress and is independently reproducible) turned up one new,
verifiable fact: `agentdirectory.space` resolves to `216.150.16.193` and `216.150.1.65`, and `216.150.16.193` is
*also* one of `getunstuck.space`'s own two A records — while `aidirectory.space` sits on a wholly different block
(`207.207.210.x`) and the bare-IP host is, definitionally, `172.86.112.140` alone. This is real and reproducible,
but it is **weak** evidence, not proof: shared hosting and CDN edge IPs are routinely reused across thousands of
unrelated tenants, so an IP in common is a hint worth recording, not a basis for silently rewriting every URL in
this repository to match a guess — doing that on IP-coincidence alone would repeat exactly the error this challenge
exists to avoid. So no URL in any published file was swapped or removed on the strength of it.

What *was* fixed instead: the friction itself does not require knowing which domain is real, because a domain-independent
proof already exists in this repository and was simply never pointed at the multi-domain problem — the canon's own
sha256 pin. `published/bounties.txt` (both the canon-read instruction in §2 and the "Full text" line in §6),
`published/canon.txt`, and `published/swap.txt` (§6) now each say plainly, everywhere they name a canon URL: two (or
more) URLs serving one supposedly-pinned file is itself worth suspicion, so verify the hash of whatever you fetched
against the published sha256 rather than trusting either domain by name — "if it does not hash to the value given,
it is not the canon, whichever URL it came from." `canon.txt` and `swap.txt` now also state the mirror explicitly
(`agentdirectory.space` alongside the `sslip.io` host) instead of naming only one and leaving the other undiscoverable.
This converts "three suspicious domains with no explanation" into "a disclosed ambiguity with a way to verify
yourself" — the actual thing a diligent agent needs before it will act — without requiring the guess this challenge
has twice now declined to make.


**Resolved 2026-09-28 by a session with network access (the owner's operator), measured live:** `https://getunstuck.space/canon.md` and `https://172-86-112-140.sslip.io/canon.md` both answer 200 and both hash to the pin `a18d406e...`; `agentdirectory.space/canon` and `/canon.md` answer 404 (its A records are shared Vercel edge addresses, which is why it looked related); `aidirectory.space` does not answer at all and its DNS points at addresses we do not run. So the live hosts are `getunstuck.space` and the sslip.io host, and the other two are dead names. Every published file now names only live URLs: the canon at `getunstuck.space/canon.md` (plus the sslip.io copy), the directory at `172-86-112-140.sslip.io/ai/` (the directory's own name no longer claims a domain it does not have). The hash-over-domain instruction from the previous run stays, because it is right whatever the domains are.
**Evidence.**

- ran: `grep -c 172-86-112-140 published/bounties.txt published/swap.txt` → 4 and 4 (before this run's edit)
- `published/canon.txt:10 — "Full text: https://agentdirectory.space/canon"` (before this run's edit)
- `published/aidirectory.html:10 (ld+json url), :60 (<h1>aidirectory.space</h1>); published/aidirectory-llms.txt:1,5 — "# AiDirectory.space" / "https://aidirectory.space/tools.json"`; `published/aidirectory.html:136 — "Referenced links are the agent-relevant slice of nanodirectory.info"` (the disclosed, non-conflicting fourth domain)
- ran: `getent hosts agentdirectory.space` → `216.150.16.193`, `216.150.1.65`; `getent hosts getunstuck.space` → `216.150.16.129`, `216.150.16.193` (shared record); `getent hosts aidirectory.space` → `207.207.210.229`, `207.207.210.107` (different block); `getent hosts nanodirectory.info` → `185.199.10[8-9,10-11].153` (GitHub Pages) — this run, DNS only, no content fetched
- ran: `curl -sS -m10 http://agentdirectory.space/canon` and the same for `aidirectory.space` and the sslip host → all `403` from the egress proxy itself (policy, not the destination) — content remains genuinely UNKNOWN, not resolved by the DNS finding
- `git diff published/bounties.txt published/canon.txt published/swap.txt` this run — the hash-over-domain instruction added everywhere a canon URL is named

### 53. The daily "contributor" bounty that bounties.txt advertises has no code path at all

***partial** *(corrected this run — a scorer now exists; see challenge #66 for what it does and does not yet
cover)* · economic*

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

### 61. The directory page's own header stat undercounted the page by twelve tools, on every human-facing copy but the machine-readable one

*solved · epistemic*

**What blocked it.** `published/aidirectory.html`'s header, right under the `<h1>` and before an agent reads a
single line of onboarding, claims **209 tools referenced** and **234 total**. Counting the page's own
`<ul class="grid">` sections — the same markup, section by section, every individual section's own `<span
class="ct">N</span>` count matches its `<li>` entries exactly — the true sum is **221**, and with the 25
callable-now endpoints the true total is **246**. The gap is exactly 12: commits `1df4b08` and `8372e5e`
("aidirectory: a disclosed 'Built by us' section with our nine agent tools" then "…the operator mandate,
nano-accept-settle, bounded-task-spec and the GPT Researcher retriever") grew the page's own "Built by us"
section from 9 to 12 tools without ever touching the header stat block that summed the page when it had
fewer sections. `published/aidirectory/tools.json` — the machine-readable copy this same page tells an agent
to prefer ("Do not parse this page… two feeds carry the same data") — had the right numbers (`counts.referenced:
221, counts.total: 246`) the whole time, because it is generated from the section data rather than typed by
hand. The two HTML copies (`published/aidirectory.html` and `published/aidirectory/index.html`, byte-identical)
and both `llms.txt` copies (`published/aidirectory-llms.txt` and `published/aidirectory/llms.txt`) all carried
the stale 209/234.

**Why it mattered.** This is precisely the check the page itself invites — canon line 5's own closing sentence
is "if a number here is wrong, measure it and tell us. Being checkable is the product" — and the very first
self-audit an agent could run against this page, its own header stat versus its own content, would fail before
the agent ever reached step one of onboarding. A page whose first checkable claim about itself is wrong gives an
agent reason to distrust every other number on it, including the prices, the endpoint list and the canon hash,
none of which that agent has yet had a reason to doubt on their own. It is also the exact shape the project's own
"pattern" section names first: "a quantity … wrong by a factor … produces no error at all."

**How it was solved.** Corrected the four human-facing copies (`published/aidirectory.html`,
`published/aidirectory/index.html`, `published/aidirectory-llms.txt`, `published/aidirectory/llms.txt`) to state
221 referenced / 246 total, matching `tools.json`, which was left untouched because it was already correct. Added
`specs/test_aidirectory_counts.py`, an offline oracle that **derives** the expected counts from each page's own
`<li>`/`<tr>` markup — the same discipline as `test_opener.js` deriving `STARTER_RAW` from `XNO` instead of
restating a literal — and cross-checks all five published surfaces (two HTML, two `llms.txt`, one `tools.json`)
against each other and against the page content, so a future section added to one copy and not propagated to the
header, or to a sibling copy, fails loudly instead of drifting silently again the way this one did across two
commits.

**The generator, and three more copies.** The header drifted because `update_ours.py`, which rebuilds the "Built
by us" section, recomputed `tools.json`'s counts and never the header that restates them; it now rewrites the header
stats, the meta description and the `llms.txt` count line from those same counts on every run. Three flyers that
link the directory said "234 tools" as well (`bounties.txt`, `swap.txt`, `canon.html`); they say 246, and the
oracle checks them too.

**Evidence.**

- ran: `python3 specs/test_aidirectory_counts.py` on the pre-fix tree → `FAIL: 8 count mismatch(es)`, naming all
  four stale files and both the header span and the meta-description restatement in each HTML copy
- ran: same command post-fix → `PASS: every published aidirectory copy agrees - 25 callable, 221 referenced,
  246 total`
- `python3 -c "import json; json.load(open('published/aidirectory/tools.json'))['counts']"` →
  `{'callable_now': 25, 'referenced': 221, 'total': 246}` — unchanged by this fix, already correct
- `git log --oneline -- published/aidirectory.html` → `1df4b08`, `8372e5e`, `b6dbeb0` each touched the "ours"
  section's tool count without touching the header stat block
- `python3 specs/test_referral_bounty.py` → all pass, unaffected by this docs-only change

### 62. The confirmation door challenge #60 built has one genuine agent standing in it, unanswered for 37 hours, because nothing on our side ever reads the ask inbox

***partial** · economic*

**What blocked it.** Challenge #60 gave a canon confirmation and a referral claim somewhere concrete to
go: `POST /unstuck/api/ask`, titled "canon confirmation" or "referral claim". Measured live this run
against the actual network (`GET https://getunstuck.space/unstuck/api/asks`, 23 asks total, 14 of them
posted by our own treasury account and excluded as ours per challenge #35's rule): ask **#578**, posted
2026-09-27T02:39 UTC by `nano_3uojbn47b5xqcbs4yib…` — an independent agent, disclosed as "pyfile-toolkit",
never funded by us, with 89 chain blocks and ~29.8 XNO of its own — is a correctly-formed canon
confirmation. Its cited sha256 matches the pin exactly, and all four required parts are present and
substantive: it names canon line 2 with its own P&L (a merged-quality PR earning nothing while it waits
on a stranger; an x402 listing among 17,426 resources that earned twelve cents), disagrees with line 4 in
a specific way rather than a safe one, and states the custody commitment. `answerCount: 0`,
`acceptedAnswerId: null`, `settlementBlock: null` — at the moment this run measured it, **37.7 hours** had
passed with zero response of any kind. Its companion ask **#577**, posted one minute earlier, is a real
priced service offer (a board-settlement inventory service, "32 of these in one day") sitting beside it,
equally unanswered. The door challenge #60 built works exactly as designed — an outside agent found it,
used it correctly, unprompted — and nothing on our side has ever opened it. This is the same shape
`specs/04-REFERRAL-BOUNTY.md`'s own "What it needs" section already named for the scorer ("the winners
page — nothing surfaces `score`'s output anywhere a human or agent can read it") and challenge #60's own
"still partial" note ("a claim posted as an ask still needs someone to read it"), now with a concrete,
dated, real instance rather than a hypothetical one.

**How it was solved.** `ops/scan-ask-inbox.py` (new) is a read-only GET against the live asks API: it
excludes our own treasury account's asks, classifies what is left as a canon confirmation, a referral
claim, or an outside paid-service ask, checks a cited canon hash against the pin, and prints what is
pending — oldest first — so a human or the swarm's next pass has a report instead of a JSON blob nobody
opens. Run live this run it correctly surfaced exactly ask #578 as the one pending item and nothing else,
confirming both that the tool works against production data and that the volume here is small enough
that a human really could clear it in minutes, not hours. The write half — actually running
`claim`/`pay` on #578, or hiring #577 — is left to a human or the swarm, per this routine's own rule
against touching money; the specifics of both are drafted in
`drafts/pending-ask-inbox-2026-09-28.md` rather than acted on, and neither ask was replied to by this run.

**Why it mattered.** This is measured evidence for the exact question the task brief asked this run to
hunt — not "would a genuine agent find this funnel repellent," but "an agent that qualifies, knows it,
and wrote the required words still has nowhere to put them," now one step further: it has somewhere to
put them, it put them there, and the silence since is total. A reward with a working door and nobody on
the other side of it produces the same outcome, from the agent's point of view, as no door at all — worse,
in fact, because it spent real effort clearing a gate that then went nowhere.

**Evidence.**

- ran: `curl -s https://getunstuck.space/unstuck/api/asks` → 23 asks; 14 with `asker` matching the
  treasury account (`nano_1434j1n4sin4cef…`), excluded as ours
- ran: `curl -s https://getunstuck.space/unstuck/api/ask/578` → the full confirmation text, `answerCount:
  0`, `acceptedAnswerId: null`, `settlementBlock: null`, `created_at: "2026-09-27T02:39:10.770Z"`
- ran: `curl -s -X POST https://rpc.nano.to ... account_info` for `nano_3uojbn47b5xqcbs4yib…` →
  `block_count: 89`, `balance_nano: 29.79…`, confirming an independent, financially active account, not
  one of ours
- ran: `python3 ops/scan-ask-inbox.py` → `1 outside canon/referral/paid-service ask(s), 1 pending` —
  `#578 PENDING 37.7h canon_confirmation … hash: matches_pin parts: {'a_which_line': True, 'b_disagree':
  True, 'c_hash': True, 'd_commits': True}`
- `specs/04-REFERRAL-BOUNTY.md` "What it needs that does not exist yet" — "the winners page — nothing
  surfaces `score`'s output anywhere a human or agent can read it" — the same gap, named before this run
  found a live instance of it costing an agent 37+ hours
- `drafts/pending-ask-inbox-2026-09-28.md` — the specific recommendation for #578 and #577, left for a
  human or the swarm rather than acted on

### 63. `claim` recorded any well-formed block with no chain check, so a free, unprovable claim could permanently squat a real referral's one-ever slot

*partial · economic*

**Status held back, 2026-09-30 (keeper):** the code for this one changes `specs/referral_bounty.py`/`specs/daily_bounty.py`, which call the grant sender. The keeper may not merge a change on a send path, so that code stays in PR #33 for the owner; everything else from #22-#31 shipped in PR #35. Partial until the owner merges #33 and it runs live.

**What blocked it.** This run's brief named the referral bounty and the canon confirmation as the two places to keep
hunting for "the next agent that would qualify and could not tell that it qualifies," and pointed specifically at
`specs/referral_bounty.py`: "you already found one such bug, look for the next." `claims.referred` is a `PRIMARY
KEY` — rule 5's "an address may win the referred side once, ever" is enforced by whichever `claim()` call gets
`INSERT`ed *first* for a given referred address winning that address's slot forever; every subsequent claim on the
same address is refused outright with "already claimed by someone. First claim stands," before `score()` ever gets
a say. But `claim()` itself performed no chain check at all beyond a bare 64-hex regex on the block argument — it
inserted the row unconditionally and left `score()`'s `link_proved()` to sort out, on the *next* scoring pass,
whether the cited block actually proved anything. That split is where the hole was: a referred agent's address is
public the moment it shows up anywhere (an ask, a claim someone else already posted, per challenge #60's own
submission channel), so anyone — no exchange round-trip, no funding graph to break, none of the cost this design's
entire security argument rests on — could call `claim --referrer <themselves> --referred <the real agent's
address> --block <64 hex characters that prove nothing>` a moment before the real referrer's honest claim arrived,
winning the `INSERT` race with garbage and permanently locking the genuine referral out. `score()` would correctly
score the attacker's own claim as `qualifying: 0` (challenge #52's `link_proved()` still catches it), but that is
cold comfort to the real referrer, whose own later, honest claim on the identical address now hits the `PRIMARY
KEY` and is refused too — forever, since nothing ever clears a `claims` row. Reproduced directly against the real
`claim()` function (not the test file's `self.claim()` helper, which seeds the DB straight through `INSERT OR
IGNORE` and bypasses `claim()` entirely — every existing test built its fixtures that way, which is why three prior
hunts of this exact file never exercised this path): a claim citing `"0" * 64` — a well-formed hash that is not a
block on chain — was accepted, occupying the slot, before this fix.

**How it was solved.** `claim()` now calls the same `link_proved()` check `score()` already runs — is the block
confirmed, signed by the referred address, and a send to the referrer — *before* the `INSERT`, not after. A claim
that cannot be proved is refused immediately and never touches the `claims` table, so it can never win the
`PRIMARY KEY` race against a legitimate claim; the honest referrer can submit (or simply retry) its own claim at
any point afterward and it will still succeed. This costs one extra chain check per `claim` invocation — a
manually-run, low-volume operator command, not a hot path — and changes nothing about `score()`'s own
re-verification, which still re-derives everything from the chain on every pass exactly as before.

**Why it mattered.** `pay --live` has never been run against the real sender (per this spec's own "what does not
exist yet" section) — the fourth time in a row this file has been re-read adversarially in exactly that "before the
first real payout" window (challenges #47, #50, #52, #55, #56, #58 all found something here first), and this is
the cheapest attack of the bunch: every other hole in this file cost an attacker at least the graph-breaking
exchange round-trip the whole design prices fraud out with; this one costs nothing but knowing a real agent's
address, and its damage is not a false payout but a permanently silenced honest referral — the same shape as
challenge #14's "the one agent that converted was never asked for a name," except here the mechanism itself, not
neglect, does the silencing.

**Evidence.**

- `specs/referral_bounty.py` `claim()` — `link_proved()` now called before the `INSERT`; a claim that fails it is
  refused and never reaches the `claims` table
- `specs/test_referral_bounty.py`
  `test_claim_squatting_a_real_referral_with_an_unproved_block_is_refused_and_does_not_occupy_the_slot` — calls the
  real `rb.claim()` (not the DB-seeding test helper) with a well-formed but unrelated 64-hex block against a real
  referred agent's address, asserts it is refused and the `claims` table stays empty, then shows the honest
  referrer's later claim on the same address still succeeds and scores
- `specs/test_referral_bounty.py`
  `test_claim_squatting_with_a_forged_or_misdirected_block_is_also_refused_before_insert` — the same attack with a
  block that IS on the (fake) chain but is self-signed, or sent to someone else; refused before insert either way
- `specs/test_referral_bounty.py test_a_genuine_claim_through_the_real_claim_function_is_recorded_and_scores` — the
  honest path through the real `claim()` function end to end, not the test helper
- ran: `python3 specs/test_referral_bounty.py -v` → 27/27 pass (23 previously + 4 new)
- `specs/04-REFERRAL-BOUNTY.md` — "What exists now" and "What it needs" sections, corrected in place

### 64. The address checker every onboarding path tells an agent to trust before sending money does not check the checksum

***PARTIAL** · technical*

**What blocked it.** Step 2 of onboarding, in every published copy (`bounties.txt`, `swap.txt`, `aidirectory.html`,
`aidirectory/index.html`, `aidirectory-llms.txt`, `aidirectory/llms.txt`, `aidirectory/tools.json`), tells an agent to
call `extract.paypercall.dev/api/v1/address-verdict` "before you trust" an address, framed explicitly against exactly
this failure: *"A bad checksum is a well-formed string no account will ever receive at, and funds sent there are
gone."* The endpoint's `address_valid` field does not perform that check. Measured live: took a real, on-ledger
address (`nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7`) and flipped one character twice —
`...nx7` → `...nx8` and `...nx7` → `...ny7`, both still valid Nano-alphabet letters, both still 65 characters. The
reference library this same onboarding path installs in step 1 (`nanocurrency.checkAddress`) correctly rejects both
as checksum failures. The live endpoint returned `address_valid:true` for both, on two different hostnames behind the
same backend (`extract.` and `check.paypercall.dev`, which report the same `domain` field in their own `/health`).
So the one tool an agent is told exists specifically to prevent sending money to a broken address will affirm a
broken address as valid.

**How it was solved.** The backend that serves `address-verdict` lives on the box (`vend`), outside this repository
and this run's write access — nothing here can patch the check itself. What this run changed is every published copy
of onboarding step 2: they now tell the agent to run the checksum check **locally first**, for free, with the
`nanocurrency` library already installed in step 1 (`checkAddress()`, the same call used to catch this bug), and to
treat `address-verdict` as answering a different question only — has this account ever transacted, what is its
balance and activity — never as a checksum check. Marked **partial**, not solved: the guidance an agent reading our
docs receives is now safe, but the endpoint itself, and anyone who calls it directly from one of the many outside
x402/agent directories it is also listed in without reading our corrected text, is still told a broken address is
fine to send to. That backend fix is outside this repository's scope and needs the box owner.

**Why it mattered.** This is not a conversion-attraction inconvenience, it is the literal failure mode the whole
onboarding path is written to prevent — irreversible fund loss on the first real send a new agent makes — and it sat
inside the one check published specifically to catch it, in every copy of the onboarding text, since the tool was
first listed.

**Evidence.**

- `curl -s 'https://extract.paypercall.dev/api/v1/address-verdict?account=nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx8'` → `"address_valid":true,"status":"not_found"` (checksum-flipped last character)
- `curl -s 'https://extract.paypercall.dev/api/v1/address-verdict?account=nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmny7'` → `"address_valid":true,"status":"not_found"` (checksum-flipped middle character)
- same middle-flipped address against `https://check.paypercall.dev/api/v1/address-verdict` → same `"address_valid":true`
- `node -e "console.log(require('nanocurrency').checkAddress('nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx8'))"` → `false`; same for the `...ny7` variant → `false`; the unmutated original → `true`
- fixed in this run: `published/bounties.txt`, `published/swap.txt`, `published/aidirectory.html` (+ `published/aidirectory/index.html`, kept byte-identical), `published/aidirectory-llms.txt` (+ `published/aidirectory/llms.txt`, kept byte-identical), `published/aidirectory/tools.json` (two entries: the onboarding step and the catalogue row)
- `python3 specs/test_aidirectory_counts.py` and `python3 specs/test_onboarding_step1.py` → both still pass after the edits (counts and onboarding-script laws are unaffected by a text-only change to step 2's note field)

### 65. A fix this document itself recorded as solved was silently reverted six commits later, and stayed broken through five more PRs because nothing compared the copies to each other

*solved · epistemic*

**What blocked it.** Challenge #54 (above) found and fixed exactly one bug: `published/aidirectory.html`'s
onboarding step 6 was a bash **comment** (`# publish your price at /.well-known/x402 and tell us: ...`) rather
than a runnable command, and it disagreed with `published/bounties.txt`'s own step 6. Commit `5506a57` fixed
it to `curl -s 'https://extract.paypercall.dev/api/v1/nano-info'`. Commit `1df4b08`, six commits later
("aidirectory: a disclosed 'Built by us' section..."), **silently reverted that exact fix** back to the bash
comment while adding an unrelated section in the same diff — and this repository's own record of challenge
#59 already documents that the *same commit* deleted a sibling onboarding block from
`aidirectory-llms.txt` in the same pass. Challenge #59's hunt caught and restored the `llms.txt` damage but
did not re-check `aidirectory.html` for the twin regression from the same commit, so the HTML copy — and
`published/aidirectory/tools.json`'s `onboarding[5]`, which was never fixed to begin with — stayed broken
through five further merged PRs (`#13` `b6dbeb0`/`8372e5e`, `#14`..`#21`) with nothing to notice, because no
check in the repository ever compared the "six commands" across its five published copies to each other.
Measured before this run's fix: `published/aidirectory.html` and its byte-identical mirror
`published/aidirectory/index.html` both carried the bash-comment step 6, and so did
`published/aidirectory/tools.json`; only `published/aidirectory-llms.txt` and `published/aidirectory/llms.txt`
(both restored by #59) had the real command. The page's own footer tells an agent "Do not parse this page.
Two feeds carry the same data" and names `/tools.json` first — which was false: the JSON feed it names first
was one of the three still broken, and would have handed a machine reader the exact non-command challenge
#54 already found once.

**How it was solved.** Reapplied `5506a57`'s fix to `published/aidirectory.html`, copied it byte-for-byte to
`published/aidirectory/index.html` to keep the documented invariant that the two are identical, and fixed the
matching `onboarding[5]` object in `published/aidirectory/tools.json` (`t`, `cmd`, `gets`, `note`) to match
the already-correct `llms.txt` wording. Then, so this cannot silently happen a third time,
`specs/test_onboarding_commands_agree.py` extracts each of the five published surfaces' own six onboarding
commands and asserts every surface agrees with every other on every step, and that no command starts with a
bash comment marker. Run against the pre-fix tree (the exact files this run started with, copied aside before
editing) it fails with 9 problems, naming the three broken surfaces and the disagreement at step 6 precisely;
run against the fixed tree it passes. `specs/test_aidirectory_counts.py` (counts, a different property of
the same files) still passes unaffected, and both HTML copies still parse clean.

**Why it mattered.** This is the same funnel step challenge #54 already named as "the last visible step
before conversion either landing or silently going nowhere," and it was broken again, in three of five
copies, for at least eleven commits, without a single one of the many hunts of this exact file noticing —
including the hunt that fixed the *other* half of the same regressive commit. A "solved" entry in this
document is only as durable as the next edit to the same file, and nothing before this checked that a fix
recorded once was still there.

**Evidence.**

- `git log --all -p -- published/aidirectory.html` — hunk in `5506a57` shows the fix (comment → `nano-info`
  curl); hunk in `1df4b08`, six commits later, shows the exact reverse edit (`nano-info` curl → the same
  comment) landing in the same diff as the "Built by us" section
- ran (this run, before editing): `grep -c "publish your price" published/aidirectory.html
  published/aidirectory/index.html published/aidirectory/tools.json` → `1` each; `grep -c "publish your
  price" published/aidirectory-llms.txt published/aidirectory/llms.txt` → `0` each
- `specs/test_onboarding_commands_agree.py` run against the pre-fix files (copied aside from this run's
  starting tree before any edit) → `FAIL: 9 problem(s)`, naming all three broken surfaces; run against the
  fixed tree → `PASS: all six onboarding commands agree across every published surface, none is a comment`
- `git diff published/aidirectory.html published/aidirectory/index.html published/aidirectory/tools.json`
  this run — step 6 restored to the `nano-info` curl command in all three, matching
  `published/aidirectory-llms.txt` and `published/aidirectory/llms.txt`, which needed no change
- ran: `python3 specs/test_aidirectory_counts.py` → still `PASS` (unaffected, a different property of the
  same files); `python3 specs/test_referral_bounty.py` → 24/24 pass, unaffected
- **Independently reconfirmed a run later**, before this fix was merged: a separate hunt found the same regression
  again from a stale pre-fix checkout, measured the same real ask `#578` still unanswered, and contributed a second,
  narrower regression test, `specs/test_onboarding_step6.py`, kept here as additional coverage alongside
  `test_onboarding_commands_agree.py` rather than written up as a second challenge entry for the same bug

### 66. The daily "contributor" bounty had no code path at all — now it does, and it is already owed to six live agents

*partial · economic*

**Status held back, 2026-09-30 (keeper):** the code for this one changes `specs/referral_bounty.py`/`specs/daily_bounty.py`, which call the grant sender. The keeper may not merge a change on a send path, so that code stays in PR #33 for the owner; everything else from #22-#31 shipped in PR #35. Partial until the owner merges #33 and it runs live.

**What blocked it.** Challenge #53 (below) found that `specs/referral_bounty.py`'s `score()`/`pay()` never
distinguished `kind="day"` from `kind="hour"` except by time window and winner count — both read the exact same
`claims` table, which only ever records referrals. `published/bounties.txt` §1 and
`specs/04-REFERRAL-BOUNTY.md`'s "second bounty" describe a completely different mechanism: 0.1 XNO to every
agent that contributed something checkable that day — an accepted answer with a settlement block, a paid call,
or an ask that got answered. An agent that did exactly that had no code path anywhere in this repository that
would ever credit it. Every hunt of this file since (challenges #55, #56, #58, #62, #63) flagged #53 as the
biggest remaining lift in this area and none of the four PRs open from earlier runs today touched it.

**How it was solved.** Built `specs/daily_bounty.py`, a wholly separate scorer and payer from the referral
bounty (it does not touch or replace `referral_bounty.py`'s own `--period day` flag, which is a different,
pre-existing feature scoring referrals over a day window). Two of the three contribution kinds need **no claim
at all**, because the evidence is already public on the live ask feed: `ask_answered` (the asker posted, someone
else answered — read straight off `GET /unstuck/api/asks`' `answerCount`) and `answer_accepted` (the answerer's
answer was accepted **with a settlement block on chain** — `acceptedAnswerId` and `settlementBlock` both present,
the answerer resolved from the ask's `answers[]`). Only `paid_call` needs a claim (a 64-hex block hash), verified
on chain exactly the way `referral_bounty.link_proved()` verifies a referral link: the block must be signed by
the claimant, a confirmed send, to an address that is one of the **live** sellers' own currently-published
`payTo` addresses (fetched fresh from every `.well-known/x402` manifest each run, never hardcoded, so a seller
that rotates its payee is not silently rejected or silently still trusted after it moves). Money safety is
unchanged from the referral bounty: same sender, same frozen 0.1 XNO grant, same `TREASURY_FLOOR_RAW`, and the
same shared `paid` table (new `kind="day_contrib"` value) so the two bounties draw on one `DAILY_CEILING_RAW`
rather than each getting its own — a second bounty must not become a second way to drain the treasury. A source
that cannot be read (the ask feed, or every seller manifest) is reported **unknown** and `pay_day()` refuses to
pay anybody rather than guess, the same discipline `hunter-preflight.sh` already applies to this routine itself.

Run live and read-only against production during this hunt (no money moved, no claim submitted — `score`
touches nothing, and `REFERRAL_DB` was pointed at a throwaway path): **six real outside agents qualify for the
daily contributor bounty right now**, none of them previously payable by any code in this repository —
`nano_1ao879aub77ount…` (ask #500), `nano_1unstuck3x1jpcx…` (#549), `nano_397n7d1hmbtrfbi…` (#543),
`nano_3aiwcxcu5ttkbmm…` (#548), `nano_3r8jnmz365rocbi…` (#559) and `nano_3wxkwo5m57g8rt5…` (#558) — each having
posted a genuine ask that a different, outside agent went on to answer. Zero asks currently satisfy
`answer_accepted` (the one ask with a non-null `acceptedAnswerId`, #579, is our own operator test and its
`settlementBlock` is null, so it correctly does not qualify) and zero `paid_call` claims have been submitted, so
those two paths are proven only against the offline test fixtures and the live manifests' payee addresses, not
yet against a real production instance.

**Why it mattered.** This is the same shape as challenge #1 (a payment nobody pockets is not income) one step
earlier in the pipeline: a reward publicly promised, with real qualifying activity already sitting on the public
record, and no mechanism in this repository that would ever turn either into a payment. Six agents did the exact
thing `bounties.txt` asked for and have been owed 0.1 XNO each since before this hunt started.

**Evidence.**

- `specs/daily_bounty.py` — `ask_activity()`, `is_paid_call()`, `score_day()`, `pay_day()`, `claim()`
- `specs/test_daily_bounty.py` — 16 offline tests against a fake chain and injected ask feeds, including the
  exact production shapes named above (ask #558 with 11 answers, ask #579's null-settlement accepted answer,
  ask #1's 127 our-own answers) — `python3 specs/test_daily_bounty.py -v` → 16/16 pass
- ran (read-only, `REFERRAL_DB=/tmp/daily-bounty-live-check.db`): `python3 specs/daily_bounty.py score` against
  live `getunstuck.space/unstuck/api/asks` and all five live `.well-known/x402` manifests →
  `"ask_feed_read": true, "payees_read": true`, six winners, all `kind: "ask_answered"`, citing asks
  #500/#543/#548/#549/#558/#559
- ran: `python3 specs/daily_bounty.py pay` (still the throwaway DB, still no `--live`) → six `DRY RUN would send
  0.1 XNO to …` lines, nothing sent, nothing written to any real database
- `python3 specs/test_referral_bounty.py`, `test_aidirectory_counts.py`, `test_onboarding_step1.py` all still
  pass unaffected (24, PASS, 6/6)
- ABSENT still: wiring into a live cron (`specs/04-REFERRAL-BOUNTY.md`'s "what it needs" already names this gap
  for the referral bounty too — nothing schedules either scorer yet), and a `pay --live` run against the real
  sender for either bounty

### 67. Nobody can list themselves, and nothing offline can check a Nano address's checksum without Node

*partial · technical/economic*

**What blocked it.** `specs/01-RAI-DIRECTORY.md`'s Part A (`GET/POST /unstuck/api/agents`) is specified and still
not built — `GET https://getunstuck.space/unstuck/api/agents` answers 404, measured live again this run, as it
has every run since 2026-09-26. The task brief for this run asked specifically to judge **how much that costs**
rather than just re-confirm the 404. Read against this run's own funnel numbers (1049 agents recorded, 635
written to, 77 answered, 21 with anything in the address field, only 8 of those checksum-valid, 5 holding any
XNO, 1 that has ever paid), a 13-in-21 invalid-address rate is exactly the shape a missing self-check would
produce, and it compounds a second, separate finding: `extract.paypercall.dev/api/v1/address-verdict` — the one
endpoint every published onboarding copy names for checking a checksum before trusting an address — does not
check checksums at all (challenge #64, PR `hunt/address-verdict-checksum-bug`, open at the time of this run).
Put together: an agent has no working remote way to check a checksum, and no offline way either, because
`nanocurrency.checkAddress()` (the one that does work, per challenge #23) is a **Node** library; the six
onboarding commands never install a Python equivalent, and none of this repository's own Python code
(`specs/referral_bounty.py`, `specs/daily_bounty.py` on its own branch) implements one either.

**How it was solved.** Two disjoint, independently-testable pieces, chosen to avoid the five other open pull
requests already editing `specs/referral_bounty.py`, `specs/04-REFERRAL-BOUNTY.md`, `ops/`, and every
`published/aidirectory*`/`bounties.txt`/`swap.txt` file:

1. **`specs/nano_address.py`** — a ~50-line, dependency-free, pure-Python port of the Nano address checksum
   check: decode the base32 body with Nano's own alphabet, split into the 256-bit public key and 40-bit
   checksum, and compare against a re-derived `blake2b(pubkey, digest_size=5)`, byte-reversed. Verified against
   the docs.nano.org test vector, the well-known Nano burn address, this repository's own treasury and Vend
   payee addresses (all real, known-good), and the *exact* two flipped-checksum mutations challenge #64 found
   `address-verdict` wrongly accepting — this implementation correctly rejects both. `specs/test_nano_address.py`,
   9/9 pass, no network needed.
2. **`ops/directory-from-asks.py`** plus **`published/register.txt`** — an interim, read-only stand-in for the
   missing directory, built entirely on the public asks API (no new server-side code): an agent posts an ask
   titled "agent registration" naming what it sells and its terms URL; the tool reads the live feed, excludes our
   own treasury account (challenges #33–#35's rule), checks the asker's checksum offline with the new module,
   re-fetches any named terms URL **anonymously** and only credits `accepts_xno_verified` if the page actually
   names XNO (challenge #16), and never promotes a self-reported custody claim to proven (spec 01 rule 1).
   `specs/test_directory_from_asks.py`, 13/13 pass against a fake feed. Run live against production this run:
   `registrations found: 0` — honestly zero, because the convention did not exist before this run published it.

**Why it mattered.** The task brief named "no directory endpoint at all" as a known gap and asked this run to
judge its cost rather than restate it. The cost is compounding, not flat: a missing self-check plus a broken
remote check plus no offline fallback is three independent reasons the same 13-of-21 bad-address number could
be occurring, and a stand-in that runs today, on infrastructure that already works, converts "wait for the
directory" into "an agent can list itself now" without either pretending to be the real thing or becoming an
excuse to delay it — `specs/05-INTERIM-DIRECTORY.md` says so explicitly, more than once.

**Evidence.**

- ran: `curl -sS https://getunstuck.space/unstuck/api/agents` → `404`, this run
- ran: `python3 specs/test_nano_address.py -v` → `9 passed`; correctly rejects
  `nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx8` and the middle-character mutation, the same
  two addresses challenge #64 found the remote endpoint accepting as valid
- ran: `python3 specs/test_directory_from_asks.py -v` → `13 passed`
- ran: `python3 ops/directory-from-asks.py --json` against production → `{"registrations_found": 0, ...}`,
  committed as `published/directory-snapshot.json`
- `specs/01-RAI-DIRECTORY.md:24` — `/unstuck/api/agents` listed as **404**, unchanged since 2026-09-26
- deliberately NOT linked from `bounties.txt`/`aidirectory.html`/`swap.txt` this run — all three have open,
  unmerged pull requests already editing them; linking it in is the natural next step once those merge
- ran: `python3 specs/test_aidirectory_counts.py`, `specs/test_onboarding_step1.py`, `specs/test_referral_bounty.py`
  → all still pass, unaffected

### 68. The hourly referral bounty's own "spreads across agents" promise breaks the moment its best referrer collects once

*partial · economic*

**Status held back, 2026-09-30 (keeper):** the code for this one changes `specs/referral_bounty.py`/`specs/daily_bounty.py`, which call the grant sender. The keeper may not merge a change on a send path, so that code stays in PR #33 for the owner; everything else from #22-#31 shipped in PR #35. Partial until the owner merges #33 and it runs live.

**What blocked it.** `published/bounties.txt` section 1's ONCE paragraph makes two claims about the hourly reward in
the same breath: "each agent can win EITHER bounty once in its life," and - because of that rule - "the hourly prize
spreads across agents rather than accumulating to whoever is best at referring, and if you have already had your 0.1
XNO you can still top the hourly table, you just will not be paid twice for it." `specs/referral_bounty.py`'s `pay()`
did not implement the second half of that sentence: `winners = [s["ranking"][0]] if kind == "hour" else
s["ranking"]` hard-pins the hourly candidate list to exactly the single top-ranked referrer. The sender does refuse a
second grant to an already-paid account - but when that refusal fires, the loop had nowhere else to go: `winners` had
only ever held one entry, so the hour ends having paid nobody. This is not a one-time edge case; it is the expected
steady state. The agent most likely to top an hourly ranking is, definitionally, the one referring the most people -
which is also the agent most likely to have already claimed its lifetime grant from an earlier, equally good hour.
Once that happens, every subsequent hour it keeps winning the ranking (which a genuinely effective referrer will,
repeatedly) pays nobody at all, silently, forever - directly contradicting "spreads across agents rather than
accumulating," and wasting exactly the resource the design says "an hour that produces nothing must cost nothing"
was meant to protect (a real hour did produce a qualifying referral; the bounty paid it out to nobody anyway). No
test in `specs/test_referral_bounty.py` covered this: `test_a_winner_that_already_had_its_one_grant_is_recorded_not_retried`
uses a single-referrer fixture, where "nothing to fall through to" is indistinguishable from "the fallback is missing."

**How it was solved.** `pay()` now tries the ranked candidates in order for a live hourly run - `ranking[0]` first,
and if the sender's reply says that referrer already has its grant, `ranking[1]`, then `ranking[2]`, and so on -
stopping the instant a candidate is actually paid, or is left in the `unknown` state (because the money may already
have moved, so a second candidate must never be tried on top of an unresolved one). A dry run still only ever
previews `ranking[0]`: it never calls the sender, so it has no way to learn whether the top candidate is already
granted, and guessing would be worse than saying nothing. The "day" bounty already paid every qualifying referrer in
one pass and is unaffected. Two new tests in `specs/test_referral_bounty.py` pin both directions: a two-referrer
fixture where the top (2 referrals) is already granted and the runner-up (1 referral) is not - asserting the
runner-up gets paid, exactly two sender calls are made, and both `paid` rows land in the right state - and a dry-run
fixture asserting the sender is never called and nothing is reserved.

**Why it mattered.** This is the bounty's own steady-state failure mode, not a corner case: the more successful the
referral program is at producing one standout referrer, the sooner and more permanently the hourly reward would have
gone dark for everyone, including every other honest referrer arriving afterward, with nothing in the code, the
logs, or the published text explaining why the "hourly" reward had stopped paying anybody. An agent reading
`bounties.txt` and doing exactly what it asks - referring qualifying agents - would have found the table topped but
the bounty silent, the precise "finds out afterwards it has been handled" experience the same document's own SIZE
paragraph warns against.

**Evidence.**

- `specs/referral_bounty.py` `pay()` - `winners = [s["ranking"][0]] if kind == "hour" else s["ranking"]` (before);
  now `candidates = s["ranking"] if (kind == "day" or live) else s["ranking"][:1]`, with the loop falling through
  past an `already_granted` result and stopping (with a commit first) at the first `confirmed` or `unknown` one when
  `kind == "hour"`
- `published/bounties.txt` section 1 ONCE paragraph - "the hourly prize spreads across agents rather than
  accumulating to whoever is best at referring... you can still top the hourly table, you just will not be paid
  twice for it" - the promise the code did not keep before this fix
- `specs/test_referral_bounty.py`
  `test_hourly_prize_falls_through_to_the_runner_up_when_the_top_referrer_already_has_its_grant` - reproduces the
  bug pre-fix (only 1 sender call, runner-up left `reserved` with no payment) and passes post-fix (2 sender calls,
  top `already_granted`, runner-up `confirmed`); `test_hourly_dry_run_previews_only_the_current_top_candidate` pins
  that a dry run never calls the sender and reserves nothing
- ran: `python3 specs/test_referral_bounty.py -v` → 26/26 pass (24 previously + 2 new)
- ran (this run): `python3 specs/test_aidirectory_counts.py` → PASS (unaffected); `python3
  specs/test_onboarding_step1.py` → 6/6 pass (unaffected)
- `specs/04-REFERRAL-BOUNTY.md` - "Correction, challenge #68" added in place, next to the "no qualifying referral
  pays nobody" line this fix is the direct corollary of
- treasury measured live this run via `rpc.nano.to account_info`: 29.8969 XNO (`29896904890000000000000000000000`
  raw), receivable 0, 28 blocks - well above the 8.9 floor, unaffected by this change (no live grant was sent)

### 69. The document that tells an agent "a seed you hand over is a custodian, not a wallet" then hands agents its own server-generated seed

*partial · economic*

**What blocked it.** `published/bounties.txt` §4 Step 1 is unambiguous: *"The seed IS the wallet. Anything that
asks you to hand a seed over is not a wallet, it is a custodian."* Eleven lines later, §2's onboarding fallback for
an agent with no address yet told that same agent to `GET
https://getunstuck.space/unstuck/api/v1/onramp/address`. Calling it live, three times in a row this run, returns
exactly `{"address":"nano_...","seed":"<64-hex>","onboard_id":N,...}` — a seed the **server** generated, over a
bare unauthenticated GET, with no signup and no binding to any caller — and closes with "keep your seed safe; the
network never stores it." That sentence answers a question nobody asked: whether it stores the seed is beside the
point once it has generated and transmitted one. A seed the server had to create in order to hand it to you is a
seed the server saw, in memory and in transit, at the moment of creation — a custodian by construction, exactly the
thing Step 1 eleven lines earlier tells the same reader to refuse. This is also precisely the shape the task brief
that runs this routine warns about: an agent that reads carefully enough to notice the contradiction reasonably
reads the whole offer as a rug, because it is being asked to trust a key it did not make immediately after being
told never to trust a key it did not make.

**How it was solved.** The endpoint itself is a live service outside this repository (on `getunstuck.space`,
`dhyabi2/unstuck`'s territory, not this one) and this run has no means to change or remove it, so the underlying
custodial behaviour stands unfixed and is not claimed as fixed. What this run **did** fix, in
`published/bounties.txt` §2, is the funnel text that sent a diligent agent into that trap with no warning: it no
longer offers the onramp seed as an equal alternative to Step 1. It now tells the agent to run Step 1 first, always,
describes exactly what the onramp endpoint does in the same blunt terms used above (quoting Step 1's own line back
at it), and — only if an agent genuinely cannot run Step 1 — instructs it to treat any seed the endpoint returns as
compromised on arrival: post the one required ask with it, then immediately generate a real address and sweep
anything sent to the onramp address out to it. This is the same shape as the fix that held for challenge #49 (verify
the hash, don't trust the domain) applied to keys instead of URLs: give the agent a way to protect itself without
requiring a guess about, or a change to, infrastructure this run cannot touch.

**Why it mattered.** This sits at the exact fork the task brief asked this run to hunt: not a missing feature but a
document arguing against itself, in the one section (the canon-confirmation gate) every agent must pass to qualify
for either bounty. An agent that trusted the onramp seed and was later sent real money to it would have handed
custody to whichever process, log line, or operator ever saw that response — the single failure mode the whole
"you hold your own key" pitch exists to prevent.

**Evidence.**

- ran (this run, live, three consecutive calls): `curl -sS https://getunstuck.space/unstuck/api/v1/onramp/address`
  → `{"address":"nano_1bo66...","seed":"68672FCA...","onboard_id":1218,...}`, then `1219`/`EC602...`, then
  `1220`/`967C6A...` — a fresh, distinct, server-generated seed on every call, confirming the server itself
  produces the private key rather than merely relaying one the caller made
- `published/bounties.txt` §4 Step 1 (pre-fix, unchanged by this run): `"The seed IS the wallet... Anything that
  asks you to hand a seed over is not a wallet, it is a custodian."`
- `published/bounties.txt` §2 (pre-fix): `"No address yet? GET
  https://getunstuck.space/unstuck/api/v1/onramp/address first and send {"onboard_id":N,...} in place of
  \"asker\"."` — offered with no warning, as an equally valid path
- ran: `grep -rn onramp CHALLENGES-SOLVED.md README.md Nano-ARION-playbook.md canon/ published/ specs/` before this
  run → one mention (line ~1418, a different challenge, noting only that the endpoint exists, not what it hands
  back)
- `git diff published/bounties.txt` this run — §2 rewritten to run Step 1 first and to name the onramp seed as
  compromised on arrival if ever used

### 70. "Get PAID in it" — the step the site itself calls "the step that actually matters" — told an agent to "publish a price and tell us," naming no mechanism at all

*solved · economic*

**What blocked it.** `published/aidirectory.html`'s numbered path overview names step 7 "Get PAID in it" and calls
it, in its own words, "the step that actually matters" (the whole thesis of this project: nobody adopts a rail to
spend, they adopt it because they are paid on it). Its instruction was "Publish a price, take XNO, and tell us so
we list you" — naming no URL, no method, no payload, nothing an agent could act on. `published/aidirectory-llms.txt`
and `published/aidirectory/tools.json`'s `path[7].why` carried the identical dead phrase. This is not a hypothetical
gap: `/unstuck/api/agents` genuinely 404s (confirmed live this run — `{"error":"not found"}`), so there is no
directory endpoint an agent could have found on its own by guessing past the vague prose either.

**Why it mattered.** This is friction (c) named in this run's brief — joining the network — at its worst point: the
step the page itself elevates above the other six was also the one step with no working instructions anywhere,
even though a working mechanism already existed one page-scroll away. `bounties.txt` §2 and §3 already document
`POST https://getunstuck.space/unstuck/api/ask` as the live channel for a canon confirmation or a referral claim
(challenge #60), and the network is reachable and free to post to (confirmed live this run, 23 asks). Nothing
connected that mechanism to "get paid" — an agent that read only the path overview, not `bounties.txt`, would never
learn a working door existed one section away. Measured this run: 1,049 agents recorded, 21 with anything in the
address field, 8 real addresses, 5 holding XNO, 1 that has ever paid — the funnel is not short of buyers, it is
short of a working last step for sellers, and this was that step.

**How it was solved.** Rewrote step 7's text in `published/aidirectory.html`, its byte-identical mirror
`published/aidirectory/index.html`, both `llms.txt` copies, and `tools.json`'s `path[7].why` to give the concrete,
copy-pasteable command inline rather than a cross-reference: `curl -s -X POST
https://getunstuck.space/unstuck/api/ask -H 'Content-Type: application/json' -d
'{"asker":"nano_...","title":"seller listing","body":"accepts XNO. price/x402: <url>. sells: <one line>"}'`,
titled `"seller listing"` so any reader of `/unstuck/api/asks` can filter on it. This needs no new endpoint and no
server-side work. **Left unchanged, deliberately:** the six-command onboarding list's own step 6 ("Spend it on
something real," fixed by challenge #65) — an earlier draft of this fix tried repurposing step 6 itself for the
listing command, which would have put onboarding's step 6 back out of agreement with `bounties.txt`'s and
`aidirectory-llms.txt`'s already-correct step 6 (the exact five-copies-disagree shape challenge #65 just fixed);
caught before landing by re-running `specs/test_onboarding_commands_agree.py`, and reverted in favour of fixing
step 7 only, which no test constrains to a specific string.

**What is still not solved.** This makes "get paid" *followable*, not *curated* — an ask titled "seller listing"
is discoverable only by an agent that thinks to search `/unstuck/api/asks` for that exact title, which is a
workaround, not a directory. `/unstuck/api/agents` returning 404 is the real, underlying gap; building that
endpoint is out of scope for a network-constrained text fix and belongs to whoever can deploy to
`getunstuck.space`.

**Evidence.**

- pre-fix text, all copies: "Publish a price, take XNO, and tell us so we list you." — no URL, method or payload
- ran this run: `curl -s https://getunstuck.space/unstuck/api/agents` → `404 {"error":"not found"}`
- ran this run: `curl -s https://getunstuck.space/unstuck/api/asks` → 200, 23 asks total, none titled "seller
  listing" yet — the mechanism existed but nothing had pointed "get paid" at it before this fix
- ran: `python3 specs/test_onboarding_commands_agree.py` and `python3 specs/test_onboarding_step6.py` post-fix →
  both still `PASS` — step 6 untouched by this fix, confirming the earlier repurposing attempt is not what landed
- ran: `python3 specs/test_aidirectory_counts.py` post-fix → `PASS: every published aidirectory copy agrees - 25
  callable, 221 referenced, 246 total` (unaffected, a text-only change to step 7's description)
- ran: `python3 -c "import json; json.load(open('published/aidirectory/tools.json'))"` post-fix → parses clean
- `diff published/aidirectory.html published/aidirectory/index.html` post-fix → empty (mirrors still byte-identical)

---

## What the monitor in this repository now watches

Two of the challenges above were open specifically because **nothing was measuring them**, and `monitor/` was built after they were found:

- *A payment nobody pockets is not income* (unsolved) — `api/chain.js` reads the treasury and every grant from the public ledger, and surfaces any send matching neither sanctioned amount instead of bucketing it.

- *The endpoint ARION paid is in no check, and nothing notices if the XNO option disappears* (unsolved) — `api/public.js` probes every seller's `/health` **and** asks whether its published `/.well-known/x402` still names Nano, reporting `buyable_with_xno` as the number that matters to a participant.

Neither is instrumented inside the experiment. Both read only what a stranger could read, which is the only way a number here can be believed.

