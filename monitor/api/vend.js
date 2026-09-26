// Vend merchant progress, read entirely from outside Vend.
//
// The two numbers this exists to keep apart: money RECEIVED and money PAID BUT NEVER CLAIMED. Every earlier count
// collapsed them into "income" and reported a merchant that was doing better than it was. Today the split is the most
// important fact about Vend - 10.0016 XNO across 13 blocks has been paid and never received, eleven of them at exactly
// the list price, which means eleven real customers.
//
// Three rules carried over from challenges that were paid for:
//   - a listing is not a caller: our own addresses never count as customers (104 of 118 requests were once our probe)
//   - a live endpoint that has silently stopped naming XNO is invisible to every other check, so ask each manifest
//   - a source that cannot be read reports unknown, never zero

const RPC = process.env.NANO_RPC_URL || "https://rpc.nano.to";
const XNO = 10n ** 30n;

// Read the payee from the live manifest rather than trusting a constant: the manifest is what buyers are TOLD to pay,
// and a payee swapped in a merged pull request is the one line that silently diverts all future income.
const HOSTS = (process.env.VEND_HOSTS ||
  "extract.paypercall.dev,search.paypercall.dev,domain.paypercall.dev,check.paypercall.dev,geoip.paypercall.dev")
  .split(",").map((s) => s.trim()).filter(Boolean);

// Accounts that are ours. A receive from one of these is internal movement, never a customer.
const OURS = new Set(
  (process.env.OUR_ACCOUNTS ||
    "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9")
    .split(",").map((s) => s.trim()).filter(Boolean).map(norm),
);

// nano_ and xrb_ are two spellings of ONE account. Comparing raw strings is an unsolved bug elsewhere in this project
// that double-counts an agent; it is not repeated here.
function norm(a) {
  return String(a || "").replace(/^xrb_/, "nano_").toLowerCase();
}

const xno = (raw) => Number(raw) / 1e30;

async function rpc(body) {
  const r = await fetch(RPC, {
    method: "POST",
    headers: { "Content-Type": "application/json", "User-Agent": "vend-merchant-monitor" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`rpc ${r.status}`);
  const j = await r.json();
  if (j.error) throw new Error(`rpc: ${j.error}`);
  return j;
}

async function timed(url, ms = 9000) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try {
    return await fetch(url, { headers: { "User-Agent": "vend-merchant-monitor" }, signal: c.signal });
  } finally {
    clearTimeout(t);
  }
}

// One host: is it alive, does it still advertise XNO, at what price, and to whom.
async function host(h) {
  const out = { host: h, health: null, terms: null, names_xno: null, price_xno: null, payees: [], resources: null };
  try {
    out.health = (await timed(`https://${h}/health`)).status;
  } catch (e) {
    out.health = `err: ${String(e.message || e).slice(0, 36)}`;
  }
  try {
    const r = await timed(`https://${h}/.well-known/x402`);
    out.terms = r.status;
    if (r.ok) {
      const j = await r.json();
      const res = Array.isArray(j.resources) ? j.resources : [];
      out.resources = res.length;
      const accepts = res.flatMap((x) => (Array.isArray(x.accepts) ? x.accepts : []));
      const nano = accepts.filter((a) => /xno|nano/i.test(`${a.asset} ${a.network}`));
      out.names_xno = nano.length > 0;
      out.payees = [...new Set(nano.map((a) => a.payTo).filter(Boolean))];
      const amt = nano.map((a) => a.amount).filter(Boolean)[0];
      if (amt) out.price_xno = xno(BigInt(amt));
    }
  } catch (e) {
    out.terms = `err: ${String(e.message || e).slice(0, 36)}`;
  }
  return out;
}

export default async function handler(req, res) {
  const hosts = await Promise.all(HOSTS.map(host));

  // Every payee the live manifests actually name. If the merchant is healthy there is exactly one.
  const payees = [...new Set(hosts.flatMap((h) => h.payees).map(norm))];

  const accounts = [];
  for (const p of payees) {
    const a = { account: p, ok: false };
    try {
      const info = await rpc({ action: "account_info", account: p, receivable: "true" });
      const hist = await rpc({ action: "account_history", account: p, count: "500" }).catch(() => ({ history: [] }));
      const rows = Array.isArray(hist.history) ? hist.history : [];

      const received = rows.filter((r) => r.type === "receive").map((r) => ({
        hash: r.hash, from: norm(r.account), amount_xno: xno(BigInt(r.amount || "0")),
      }));
      // A listing is not a caller, and neither is our own treasury moving money about.
      const customer = received.filter((r) => !OURS.has(r.from));

      let recv = { ok: false, blocks: [], total: 0 };
      try {
        // `source: true` is required, not cosmetic: without it the node returns a bare ARRAY of hashes and the
        // amounts are simply absent - which read as an amount and threw. Handle both shapes, because a node that
        // ignores the flag would otherwise silently report every payment as zero.
        const pend = await rpc({ action: "accounts_receivable", accounts: [p], count: "100", source: "true" });
        const b = (pend.blocks || {})[p] || {};
        let blocks;
        if (Array.isArray(b)) {
          // Hashes only: we know a payment is waiting but not how much. Say so rather than invent 0.
          blocks = b.map((hash) => ({ hash, amount_xno: null }));
        } else {
          blocks = Object.entries(b).map(([hash, v]) => ({
            hash,
            amount_xno: xno(BigInt(typeof v === "object" ? v.amount || "0" : v)),
          }));
        }
        const known = blocks.filter((x) => x.amount_xno !== null);
        recv = {
          ok: true,
          blocks,
          total: known.reduce((s, x) => s + x.amount_xno, 0),
          // If the node withheld amounts, the total is a floor, not the figure. Labelled so nobody quotes it as one.
          total_is_partial: known.length !== blocks.length,
        };
      } catch (e) {
        recv = { ok: false, error: String(e.message || e) };
      }

      a.ok = true;
      a.balance_xno = xno(BigInt(info.balance || "0"));
      a.block_count = info.block_count ? Number(info.block_count) : null;
      a.received = {
        blocks: received.length,
        from_customers: customer.length,
        distinct_customers: new Set(customer.map((r) => r.from)).size,
        total_xno: received.reduce((s, r) => s + r.amount_xno, 0),
      };
      // The number that must never be folded into income.
      a.unreceived = recv;
      a.history_complete = rows.length < 500;
    } catch (e) {
      a.error = String(e.message || e);
    }
    accounts.push(a);
  }

  const live = hosts.filter((h) => h.health === 200);
  const buyable = hosts.filter((h) => h.health === 200 && h.names_xno === true);

  res.setHeader("Cache-Control", "s-maxage=60, stale-while-revalidate=300");
  res.status(200).json({
    endpoints: {
      probed: hosts.length,
      live: live.length,
      // Live but no longer naming XNO is the silent failure nothing else watches for.
      live_but_not_naming_xno: live.length - buyable.length,
      rows: hosts,
    },
    // More than one payee across the manifests means something diverged. It should always be exactly 1.
    payees: { count: payees.length, accounts: payees, consistent: payees.length === 1 },
    money: accounts,
    note:
      "Read from the live manifests and the public ledger. Nothing is instrumented inside Vend, and no number here " +
      "is reported by Vend about itself. Received and unreceived are kept apart deliberately.",
  });
}
