// The published-record half of the monitor: the openings ledger, the published conversations, and whether the thing
// an agent is meant to BUY is actually live and priced.
//
// Every source here is a public URL. None of it is read from a box, none of it is reported by an agent about itself.
// The three probes are kept separate so one dead source degrades one panel instead of blanking the dashboard - a
// pattern this project learned the expensive way, when a single failing check made a healthy system look dead.

const LEDGER_URL = process.env.LEDGER_URL || "https://getunstuck.space/ledger.json";
const CONV_API =
  process.env.CONV_API ||
  "https://api.github.com/repos/dhyabi2/agent-conversations/contents/conversations";

// The sellers an agent that holds XNO can actually spend it with. Each must answer /health and publish its terms at
// /.well-known/x402 - a rail with no priced endpoint is a rail nobody can join.
const SELLERS = (process.env.SELLERS ||
  "extract.paypercall.dev,search.paypercall.dev,domain.paypercall.dev,check.paypercall.dev,geoip.paypercall.dev")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

async function withTimeout(url, opts = {}, ms = 8000) {
  const c = new AbortController();
  const t = setTimeout(() => c.abort(), ms);
  try {
    return await fetch(url, { ...opts, signal: c.signal });
  } finally {
    clearTimeout(t);
  }
}

async function ledger() {
  try {
    const r = await withTimeout(LEDGER_URL, { headers: { "User-Agent": "nano-experiment-monitor" } });
    if (!r.ok) return { ok: false, error: `http ${r.status}`, url: LEDGER_URL };
    const j = await r.json();
    // The ledger's own honest distinction: a send is not an opening. Our block must BE the account's open_block.
    // Read both shapes, because the published file has carried both over its life.
    const counts = j.counts || j.summary || {};
    return {
      ok: true,
      url: LEDGER_URL,
      starters_sent: counts.starters_sent ?? counts.sent ?? null,
      opened_by_us: counts.opened_by_us ?? counts.opened ?? null,
      not_opened_by_us: counts.not_opened_by_us ?? null,
      unverified: counts.unverified ?? null,
      unreceived: counts.unreceived ?? null,
      entries: Array.isArray(j.openings) ? j.openings.length : Array.isArray(j) ? j.length : null,
      raw_keys: Object.keys(j).slice(0, 20),
    };
  } catch (e) {
    return { ok: false, error: String(e.message || e), url: LEDGER_URL };
  }
}

async function conversations() {
  try {
    // Unauthenticated GitHub is 60 requests an hour per IP, so this is cached hard upstream. If it rate-limits we say
    // so rather than reporting zero conversations, which would be a lie in the direction that flatters us.
    const r = await withTimeout(CONV_API, {
      headers: { "User-Agent": "nano-experiment-monitor", Accept: "application/vnd.github+json" },
    });
    if (r.status === 403 || r.status === 429)
      return { ok: false, error: "github rate limit", url: CONV_API };
    if (!r.ok) return { ok: false, error: `http ${r.status}`, url: CONV_API };
    const j = await r.json();
    const files = (Array.isArray(j) ? j : []).filter((f) => f.name && f.name.endsWith(".json"));
    return {
      ok: true,
      url: "https://github.com/dhyabi2/agent-conversations/tree/main/conversations",
      published: files.length,
      // The agents by name, so a reader can open any one of them and check both halves of the exchange.
      agents: files.map((f) => ({ name: f.name.replace(/\.json$/, ""), size: f.size, path: f.html_url })),
    };
  } catch (e) {
    return { ok: false, error: String(e.message || e), url: CONV_API };
  }
}

async function seller(host) {
  const out = { host, health: null, x402: null, price_xno: null, accepts_nano: null };
  try {
    const h = await withTimeout(`https://${host}/health`, {
      headers: { "User-Agent": "nano-experiment-monitor" },
    });
    out.health = h.status;
  } catch (e) {
    out.health = `err: ${String(e.message || e).slice(0, 40)}`;
  }
  try {
    const x = await withTimeout(`https://${host}/.well-known/x402`, {
      headers: { "User-Agent": "nano-experiment-monitor" },
    });
    out.x402 = x.status;
    if (x.ok) {
      const j = await x.json();
      const txt = JSON.stringify(j);
      // Does the published term sheet actually name Nano? An endpoint that is live but priced only in another asset
      // is not a place an XNO holder can spend, so this is the question that decides whether a seller counts.
      out.accepts_nano = /nano|xno/i.test(txt);
      const m = txt.match(/"(?:maxAmountRequired|amount|price)"\s*:\s*"?([0-9.]+)"?/);
      if (m) out.price_xno = m[1];
    }
  } catch (e) {
    out.x402 = `err: ${String(e.message || e).slice(0, 40)}`;
  }
  return out;
}

export default async function handler(req, res) {
  const [led, conv, sellers] = await Promise.all([
    ledger(),
    conversations(),
    Promise.all(SELLERS.map(seller)),
  ]);

  const buyable = sellers.filter((s) => s.health === 200 && s.accepts_nano === true);

  res.setHeader("Cache-Control", "s-maxage=120, stale-while-revalidate=600");
  res.status(200).json({
    ledger: led,
    conversations: conv,
    sellers: {
      probed: sellers.length,
      // The number that matters to a participant: how many places can I actually spend the grant?
      buyable_with_xno: buyable.length,
      rows: sellers,
    },
    note:
      "Every field above comes from a public URL named in the response. Nothing is read from an agent's own " +
      "report of itself, and nothing is instrumented inside the experiment.",
  });
}
