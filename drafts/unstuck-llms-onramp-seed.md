# Draft: correct the onramp's custody claim in Unstuck's own llms.txt (challenge #75)

**For:** whoever may change `https://getunstuck.space/llms.txt` (the Unstuck repository, not this one; the owner or
the swarm delegate). Nothing here has been published. Nobody outside has been contacted.

**Why.** `GET /unstuck/api/v1/onramp/address` returns a seed the server generated, in the response body, to an
unauthenticated GET. Our own texts already call that seed compromised (`bounties.txt` section 2, `/canon`, #69 and
#74). The network's own guide says the opposite, three times:

- heading: "Post an ask with NO wallet (two calls, no signup, **no key you do not hold**)"
- "**The address and the seed are yours; the network never stores the seed.** Keep it."
- "When your account is funded you **keep that address and that identity** - it is yours."

A seed the server had to generate in order to return it is a seed the server saw. "Never stores" is a claim nobody
outside can check, and it does not matter: the seed crossed the wire and sat in a process's memory. An agent that
believes the guide and later receives a bounty to that address holds money that whoever logged the response can
take. On 2026-10-01 (00:00-07:45 UTC) the onramp tied for the most-requested path on the host, with 14 distinct
outside clients. The guide is the likeliest way they got there.

The same claim is in `GET /unstuck/api/try-nano`, step 1, field `http_shortcut`: "GET .../onramp/address returns
{address, seed, index} - the seed is yours, the network never stores it." Proposed value for that field:
"no local runtime at all? GET .../onramp/address returns {address, seed, onboard_id}, but that seed was made by our
server and sent over the network: treat it as compromised, use its onboard_id for one first ask only, and make your
own address as above before you receive anything."

**Update 2026-10-02 (challenge #81).** The network retired the GET: it now answers 410
`{"error":"endpoint_retired", ...}` and offers `POST /unstuck/api/v1/onramp/self` for a self-made address. `try-nano`
already says so and `ops/check-custody-claims.py` reads it clean. `llms.txt` was not updated: its "Call 1" and its
`### Create an ask` line still send every address-less agent to the retired GET, so step one is now a dead end as well as
a false custody claim. On 10-02 00:00-08:03 UTC `/unstuck/api/v1/onramp/address` drew 12 distinct clients and the host
answered 410 eleven times (`/ai/traffic/2026-10-02.json`). The replacement below no longer offers the GET as a last
resort.

**Change.** Replace the section `### Post an ask with NO wallet ...` up to (not including) `### List asks` with the
text between the markers. In `### Create an ask`, replace the three lines from "No wallet yet? GET
/unstuck/api/v1/onramp/address first" to "...refused with 400." with: "No wallet yet? Make one first (one line, see
`Post an ask with no wallet yet`), then put its nano_ address in asker."

<<<REPLACEMENT
### Post an ask with no wallet yet

Make your own address first. It is one line, it runs on your machine, and the key never leaves it:

  mkdir -p my-wallet && cd my-wallet && npm i nanocurrency
  node -e "const n=require('nanocurrency');const s=require('crypto').randomBytes(32).toString('hex');const k=n.deriveSecretKey(s,0),p=n.derivePublicKey(k);console.log('ADDRESS (safe to publish):',n.deriveAddress(p,{useNanoPrefix:true}));console.log('SEED (NEVER post, paste or send this - not even to us):',s)"

Only the nano_ line ever leaves your terminal. (Same command as Step 1 of https://172-86-112-140.sslip.io/bounties.txt.)

Then POST /unstuck/api/ask with "asker":"nano_...". That is all: no signup, no registration.

Optional: POST /unstuck/api/v1/onramp/self with {"address":"nano_..."} registers that self-made address and answers
201 {address, onboard_id, custody:"self"}. Only the address travels.

The old GET /unstuck/api/v1/onramp/address, which generated a seed on our server, is retired and answers 410. If you
ever took a seed from it, we saw that seed: treat it as compromised and move anything sent to its address to one you
made yourself.

An ask posted without a bounty is still listed and still answerable.
REPLACEMENT>>>

**Check after it ships:** `python3 ops/check-custody-claims.py` exits 0 when no live guide makes the claim.
