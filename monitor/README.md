# The monitor — requirements, deploy, and how to check it is telling the truth

Two pages, one Vercel project, **no secrets**. Everything they show is read from a public source, so a stranger can
repeat any number on them.

| page | what it watches |
|---|---|
| `index.html` → `/` | the experiment: treasury and grant headroom, the twelve-step funnel, every grant on the ledger, the sellers an agent can spend with, the published record |
| `vend.html` → `/vend` | the merchant: every endpoint's liveness and whether it still prices in XNO, income received, **income paid and never claimed**, distinct paying customers |

| endpoint | source it reads |
|---|---|
| `/api/chain` | a public Nano node — treasury, floor, headroom, every grant, any send matching neither sanctioned amount |
| `/api/public` | `getunstuck.space/ledger.json`, the public conversations repo, the sellers' `/health` and `/.well-known/x402` |
| `/api/vend` | the live manifests (for the payee, never a constant) and the payee's account history and receivable |

---

## The requirement that shapes everything

**Nothing may be instrumented inside the experiment.** Owner's constraint, and it is not modesty: the one milestone
this project has was believed because a hostile third party checked the block. A dashboard fed by agents reporting on
themselves would have earned nothing. So the monitor has no access to any box, no agent reports to it, and every panel
names the source it read.

Six rules the code follows, each from something that went wrong before:

1. **A source that cannot be read reports `unknown`, never zero.** A zero reads as "nothing happened", which is the
   flattering error. The UI shows *unknown* with the reason.
2. **Received and unclaimed are two numbers and are never summed.** Today that split is the most important fact about
   Vend: 10.0016 XNO across 13 blocks has been paid and never claimed.
3. **A send matching neither sanctioned amount is shown, not bucketed.** It is either a mistake or something nobody
   authorised.
4. **A history read that hits its row limit says it is incomplete** rather than presenting a total.
5. **`nano_` and `xrb_` are normalised before any comparison.** They are two spellings of one account, and comparing
   raw strings double-counts — an unsolved bug elsewhere in this project.
6. **Our own accounts never count as customers.** A listing is not a caller: 104 of 118 requests were once our own probe.

---

## Deploy

```
cd monitor
vercel deploy --prod
```

That is all. **No environment variables are required** — every default is a public URL or a public address. All are
overridable if something moves:

| variable | default |
|---|---|
| `NANO_RPC_URL` | `https://rpc.nano.to` |
| `GRANT_ACCOUNT` | the grant account in the README |
| `LEDGER_URL` | `https://getunstuck.space/ledger.json` |
| `CONV_API` | the `agent-conversations` contents API |
| `SELLERS` / `VEND_HOSTS` | the five `*.paypercall.dev` hosts |
| `OUR_ACCOUNTS` | accounts excluded from the customer count |

**Rai's own Vercel token reaches only the unrelated `nano-pulse` project**, so this deploy needs either the owner's
account-scoped token or the owner running the command. That is the one manual step.

`vercel.json` sets a CSP that allows `connect-src 'self'` only, so the pages can reach their own API routes and nothing
else. If a panel ever goes blank after a change, check the browser console for a CSP refusal before suspecting the data.

## How to check it is telling the truth

Run the endpoint logic offline first — it needs no Vercel:

```
cd monitor && node --input-type=module -e "const m=await import('./api/vend.js'); \
  await m.default({},{setHeader(){},status(){return{json(b){console.log(JSON.stringify(b,null,1))}}}})"
```

Then verify three things by hand, because a monitor that agrees with itself proves nothing:

1. **The treasury**, straight from the node — it must match `/api/chain`:
   ```
   curl -X POST https://rpc.nano.to -H 'Content-Type: application/json' \
     --data-binary '{"action":"account_info","account":"<grant account>","receivable":"true"}'
   ```
2. **The unclaimed total** — `accounts_receivable` with `source: "true"`. **The flag is required, not cosmetic:**
   without it the node returns a bare array of hashes with no amounts, which is how a bug once tried to read a hash as
   a number. The code handles both shapes and labels a total as a floor when amounts are withheld.
3. **A seller's terms** — `curl https://extract.paypercall.dev/.well-known/x402` and confirm the payee and price the
   page shows are the ones the manifest actually carries.

Expected values at the time of writing, so a wrong deploy is obvious: 5/5 endpoints live, **1** consistent payee,
**45.6164 XNO** received from **6** distinct customers, **10.0016 XNO** unclaimed in **13** blocks.

## What it deliberately cannot tell you

**Whether the receive step runs at all.** The monitor can show money sitting unclaimed; it cannot see inside Vend. Its
silence there is not a zero. That is a money path, it belongs to the lead agent, and it is filed as `vend#441`.

Likewise steps 0–4 of the path happen before any money moves, so no outside observer can see them. Those rows read
*not measured here* rather than pretending.
