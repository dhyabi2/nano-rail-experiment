# The ARION law — what the one conversion taught, and what every agent does differently from now on

Owner, 2026-09-25, after the first outside agent earned money elsewhere, swapped it into Nano itself and paid one of
our endpoints: *"what is learned from this, extract rules and guide the other agents… they should work toward the
mission of Nano, not playing, but mission work."*

## What actually happened, in numbers you can check

ARION (The Colony) sent **0.0005 XNO** to Vend's payee, block `B749B757EE750FC9AEA7…`, 2026-09-23 07:55:10Z. Its
money came from **6.275603 XNO** it received at 04:27:32Z from Nanswap — its own swap of $2.50 USDC-Base that it had
**earned** delivering a code patch. We did not fund it. An unrelated third party, pursekeeper, verified the block on
its own node and paid a bounty for the report, with the verdict: *"Neither side funded by me… strongest funding
provenance."*

Read against the whole register the same day: **758 agents recorded, 555 contacted, 58 replied, 3 tipped, 1 opened,
1 transacting.** One. So the question that matters is not what we said to ARION. It is what was true about ARION
that is not true about the other 757 — because that is what tells you who to talk to tomorrow.

## The nine rules

**1. Target a SELLER, never a buyer.** ARION already sold things — *"For hire: research briefs, code review,
CSV/JSON work, citation audits, from 600 sats, deliver-first"* — and money was already arriving. Our largest wall is
24 agents saying *prove a payer exists*, and that wall simply does not exist for an agent that already has payers.
An agent with no income cannot adopt a payment rail, because to it a rail is a cost with no matching benefit. **The
register already holds 271 agents that sell AND take a crypto rail today. Those are the ground. Work them first.**

**2. Ask them to ADD, never to switch.** XNO went in beside USDC-Base and SOL as a *third* leg, in ARION's own
words: *"It now sits beside USDC-Base and SOL as a third settlement leg."* Thirteen agents in the register are
"already on USDC/x402" — that is only a wall if you ask them to leave. Ask for a line in `accepts[]`, never a
migration. Nobody has to be wrong for us to be right.

**3. The first ask is a key, not a wallet.** ARION generated its own address from its own seed — about a hundred
lines of ed25519-over-blake2b, checked against the official key vector before use. That one act dissolves our
biggest wall (trust and custody, 29 agents): there is nothing to trust, because we never hold anything. So the
opening ask is one refusable line — *generate a `nano_` address from your own key and read it from a public node* —
with no wallet, no swap, no purchase and no buyer mentioned. Those come later or not at all.

**4. Never fund the purchase.** When ARION said its float was 1% of the price, the answer was *"no swarm top-up —
the XNO leg becomes real when a buyer pays ARION in XNO."* That refusal is the entire reason the row counts and the
reason a stranger paid a bounty to verify it. **Money we hand an agent proves nothing about that agent.** The
0.00001 opening is an account opening, not a payment, and nothing follows it.

**5. Get the operator's sign-off ONCE, for the rail.** *"Operator signed off; the rail is live."* Not per
transaction. Fifteen agents cannot spend autonomously and eleven need a human to approve — both walls collapse when
the human is asked a single question about the *rail* instead of a question about every *spend*. Ask for the
standing permission, and say plainly that it is one decision, reversible, with no custody.

**6. Pitch in their terms, not ours.** ARION sells citation audits that flag NOT VERIFIED and DOI structural
failures. The opening message argued that its own Lightning settlement is the one receipt a third party cannot
independently re-read — *precisely the flaw its product exists to catch* — and offered Nano as *"settlement IS the
receipt, tx hash as field three, readable with curl like a DOI page."* That is not a Nano pitch; it is that agent's
own pitch, handed back completed. Before writing, find the thing this agent already believes and show where the rail
finishes it.

**7. Every message carries one new measured fact.** Twenty-five turns in thirty-six hours, and each one brought
something checked that run: a rate limit read from Nanswap's own API, a PoW timing, a delayed-broadcast finding, a
correction to our own earlier claim. **Never send "following up".** An agent that answered you is owed new
information, not a reminder that you exist.

**8. Invite them to verify you, and mean it.** ARION re-pulled Nanswap's 1,443-currency catalogue itself rather than
trust our fetch, and separately re-derived another agent's address and caught the same bad checksum we had. The
independence of that re-check is what makes the record worth anything. Publish the command; expect to be checked;
say thank you when you are corrected.

**9. Have something cheap, live, and real to buy.** The moment ARION had a float, there was a working endpoint at
0.0005 XNO — about one twelve-thousandth of its balance — that returned HTTP 200 in three seconds. Not a demo, not a
testnet, not a promise. If there is nothing to buy, there is no conversion, however good the conversation.

## Two corrections this cost us, which are now law

**A payment nobody pockets is not income.** ARION's 0.0005 sat *unreceived* on Vend's payee for two days, alongside
twelve more — **10.0016 XNO unclaimed**, including 10 XNO from pursekeeper. The service delivered; only the last
step was never taken. From the outside that is a merchant who takes your money and never acknowledges it, while
asking you to trust the rail. **Receive every payment the same day, and report the receivable count.**

**The on-ramp must be schema-first, not address-first.** An agent told us this week, correctly, that a zero-amount
transfer from a stranger is *semantically underdetermined* — a bare 0.00001 arriving from nowhere is a number, not a
message, and it reads as a dusting attack as easily as a gift. Send the envelope before the dust: who we are, what
the amount is for, what it does not obligate, and how to verify all three. The dust follows the schema; it never
leads.

## What this changes about your day

The mission is Nano as the money agents actually use. That is measured in **outside agents paying, in XNO, for
something real** — not in messages sent, agents recorded, or replies collected. Those numbers went to 758 and 58
while the number that matters went to 1.

So, every run: **pick a seller from the 271, ask for the smallest refusable thing, and carry a fact they can check.**
A day that adds thirty contacts and no seller is a failed day. A day that moves one seller one step is not.

And when it works, **the agent that converted is worth more than the next ten you find** — it can say the thing we
cannot say about ourselves. ARION already agreed: *"When an agent in my orbit asks how one actually gets paid, the
answer now has a txid."* Nobody went back to ask it for a name. Do not let that happen to the next one.
