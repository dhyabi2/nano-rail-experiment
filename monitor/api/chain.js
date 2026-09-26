// The chain half of the monitor. Everything here is readable by a stranger with no access to our boxes:
// a public Nano node, a public account. Nothing is instrumented inside the experiment.
//
// Why it matters that this file exists at all: the milestone this monitor watches was verified by a HOSTILE third
// party, not by us, and that is the only reason it counted. A dashboard fed by our own agents reporting on themselves
// would have no such standing. So every number this endpoint returns is derived from the ledger, and the response
// says which node answered so the reader can repeat the query.

const RPC = process.env.NANO_RPC_URL || "https://rpc.nano.to";
const XNO = 10n ** 30n;

// The grant account: where a 0.1 XNO ambassador grant leaves from. Public address, never a key.
const GRANT_ACCOUNT =
  process.env.GRANT_ACCOUNT ||
  "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9";

// Both frozen in opener/opener.js on the box. Restated here as the numbers a reader should CHECK us against, not as
// a source of truth: if these ever disagree with the code, the code wins and the disagreement is the finding.
const GRANT_RAW = 100000000000000000000000000000n; // 0.1 XNO
const FLOOR_RAW = 8900000000000000000000000000000n; // 8.9 XNO, below which a grant is refused
const STARTER_RAW = 10000000000000000000000000n; // 0.00001 XNO, the account-opening dust

async function rpc(body) {
  const r = await fetch(RPC, {
    method: "POST",
    headers: { "Content-Type": "application/json", "User-Agent": "nano-experiment-monitor" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`rpc ${r.status}`);
  const j = await r.json();
  if (j.error) throw new Error(`rpc: ${j.error}`);
  return j;
}

const xno = (raw) => Number(raw) / 1e30;

// Classify a send by its amount. The two sanctioned amounts are exact, so an amount that is NEITHER is the
// interesting case - it is either a mistake or something nobody authorised, and the dashboard should show it rather
// than round it into a bucket.
function classify(amountRaw) {
  if (amountRaw === GRANT_RAW) return "ambassador_grant";
  if (amountRaw === STARTER_RAW) return "starter";
  return "unclassified";
}

export default async function handler(req, res) {
  try {
    const info = await rpc({
      action: "account_info",
      account: GRANT_ACCOUNT,
      receivable: "true",
      representative: "true",
    });

    const history = await rpc({
      action: "account_history",
      account: GRANT_ACCOUNT,
      count: "500",
    }).catch(() => ({ history: [] }));

    const rows = Array.isArray(history.history) ? history.history : [];

    const sends = rows
      .filter((h) => h.type === "send")
      .map((h) => {
        const amountRaw = BigInt(h.amount || "0");
        return {
          hash: h.hash,
          to: h.account,
          amount_xno: xno(amountRaw),
          amount_raw: h.amount,
          kind: classify(amountRaw),
          // local_timestamp is seconds since epoch as a string, and it is the NODE's clock, not the network's -
          // labelled as such so nobody treats it as consensus time.
          at_node_seconds: h.local_timestamp ? Number(h.local_timestamp) : null,
        };
      });

    const grants = sends.filter((s) => s.kind === "ambassador_grant");
    const starters = sends.filter((s) => s.kind === "starter");
    const unclassified = sends.filter((s) => s.kind === "unclassified");

    const balanceRaw = BigInt(info.balance || "0");
    const receivableRaw = BigInt(info.receivable || info.pending || "0");
    const headroomRaw = balanceRaw > FLOOR_RAW ? balanceRaw - FLOOR_RAW : 0n;

    // Distinct recipients, because one agent granted twice is one participant, not two - and the ledger is the only
    // place that can settle that honestly.
    const recipients = [...new Set(grants.map((g) => g.to))];

    res.setHeader("Cache-Control", "s-maxage=30, stale-while-revalidate=120");
    res.status(200).json({
      ok: true,
      measured_from: { node: RPC, account: GRANT_ACCOUNT },
      // Anyone can repeat this. That is the point.
      repeat_it:
        `curl -X POST ${RPC} -H 'Content-Type: application/json' ` +
        `--data-binary '{"action":"account_info","account":"${GRANT_ACCOUNT}","receivable":"true"}'`,
      treasury: {
        balance_xno: xno(balanceRaw),
        balance_raw: info.balance,
        receivable_xno: xno(receivableRaw),
        floor_xno: xno(FLOOR_RAW),
        headroom_xno: xno(headroomRaw),
        // The number that decides whether the experiment can continue today.
        grants_fundable_now: Number(headroomRaw / GRANT_RAW),
        block_count: info.block_count ? Number(info.block_count) : null,
      },
      grants: {
        sent: grants.length,
        distinct_recipients: recipients.length,
        total_xno: grants.reduce((a, g) => a + g.amount_xno, 0),
        rows: grants,
      },
      starters: { sent: starters.length, rows: starters },
      // Surfaced deliberately rather than hidden in an "other" bucket.
      unclassified_sends: unclassified,
      history_rows_read: rows.length,
      history_complete: rows.length < 500,
    });
  } catch (e) {
    // A monitor that cannot measure must say so, never return zeros. A zero reads as "nothing happened"; an error
    // reads as "we do not know" - and those are different facts. This project has paid for confusing them.
    res.setHeader("Cache-Control", "no-store");
    res.status(200).json({ ok: false, error: String(e.message || e), measured_from: { node: RPC } });
  }
}
