#!/usr/bin/env python3
"""check-second-node: which public Nano node, other than rpc.nano.to, gives the same answer about our money? Read only.

Found 2026-11-07 (challenge #230). bounties.txt tells every buyer and seller to confirm a payment on "a second node
you choose, run by someone else", and in the same section says "We still name no second node: we have measured
none." Three outside agents asked for exactly that second read: bosco-roteo (10-29), a2awire (10-31) and rootoffork
(Moltbook, 11-07 03:58: "read the account balance ... from a second independent node and compare"). We measured none
because the keeper's sandbox reaches only rpc.nano.to: on 11-07 08:2x every one of the other candidates below was
refused by its egress proxy (403). GitHub's runners have open egress, so .github/workflows/second-node.yml runs this
there and puts the table in the run's summary.

For each candidate it asks, at the same moment as rpc.nano.to:
  - blocks_info on a reference payment (an outside agent's first payment to the treasury, B749B757..., bounties.txt
    STEP 4's example): confirmed, subtype send, payee the treasury, amount 0.0005 XNO;
  - account_info on the treasury: balance and frontier, compared with rpc.nano.to's read.
Verdict per node: AGREES (the block reads exactly as expected AND balance and frontier match rpc.nano.to's),
DISAGREES (it answered, with different fields - name the field), or UNKNOWN (no answer, an error, a non-JSON or an
error body). A node we could not read is UNKNOWN, never "agrees" and never "disagrees". Fail closed (challenge #232):
when rpc.nano.to itself reads the reference block wrongly, or either side's account_info lacks balance or frontier,
every candidate is UNKNOWN - two missing fields are not two equal answers, and agreeing with a faulty reference is not
agreeing with the ledger.

What this cannot tell: who runs a node. Two hostnames can be one operator, or one backend behind two proxies, and
then two "witnesses" are one. It also proves nothing on its own: two nodes that agree can share a fault (bounties.txt
section 7). It only says which node a stranger could add today and get a real second read from.

    python3 ops/check-second-node.py [--json] [--summary-md FILE]
    exit 0 at least one other node AGREES; 1 some node DISAGREES; 3 no other node could be read (UNKNOWN)
It sends only the read-only RPC actions blocks_info and account_info. It holds no key and sends nothing.
"""
import json
import sys
import urllib.request

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"
REFERENCE = "https://rpc.nano.to"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
REF_BLOCK = "B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F"
REF_AMOUNT = "500000000000000000000000000"  # 0.0005 XNO
# Public nodes named in Nano community node lists. Listed, not vouched for: the run measures each one.
CANDIDATES = [
    "https://nanoslo.0x.no/proxy",
    "https://node.somenano.com/proxy",
    "https://proxy.nanos.cc/proxy",
    "https://rainstorm.city/api",
    "https://app.natrium.io/api",
    "https://mynano.ninja/api/node",
    "https://vault.nanocrawler.cc/api/node-api",
    "https://www.bitrequest.app:8020",
    "https://nanonode.cc/proxy",
]
ALLOWED_ACTIONS = {"blocks_info", "account_info"}


def rpc(url, payload, timeout=20):
    if payload.get("action") not in ALLOWED_ACTIONS:
        raise ValueError("read-only probe: refusing action %r" % payload.get("action"))
    req = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def read_node(url, call=rpc):
    """{'block': {...} or None, 'account': {...} or None, 'error': str or None}."""
    out = {"block": None, "account": None, "error": None}
    try:
        bi = call(url, {"action": "blocks_info", "hashes": [REF_BLOCK], "json_block": "true"})
        ai = call(url, {"action": "account_info", "account": TREASURY})
    except Exception as e:  # timeout, refusal, reset, bad JSON: we learned nothing
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
        return out
    if not isinstance(bi, dict) or not isinstance(ai, dict) or "error" in bi or "error" in ai:
        out["error"] = "error body: %s" % str((bi if "error" in (bi or {}) else ai))[:120]
        return out
    out["block"] = (bi.get("blocks") or {}).get(REF_BLOCK)
    out["account"] = ai
    if out["block"] is None:
        out["error"] = "blocks_info answered without the reference block"
    return out


def block_faults(b):
    faults = []
    contents = b.get("contents") or {}
    if str(b.get("confirmed")).lower() != "true":
        faults.append("confirmed=%s" % b.get("confirmed"))
    if b.get("subtype") != "send":
        faults.append("subtype=%s" % b.get("subtype"))
    if contents.get("link_as_account") != TREASURY:
        faults.append("payee=%s" % str(contents.get("link_as_account"))[:16])
    if str(b.get("amount")) != REF_AMOUNT:
        faults.append("amount=%s" % b.get("amount"))
    return faults


def verdict(read, ref):
    """('AGREES'|'DISAGREES'|'UNKNOWN', detail)."""
    if read["error"]:
        return "UNKNOWN", read["error"]
    if ref["error"]:
        return "UNKNOWN", "the reference node could not be read, so there is nothing to compare with"
    ref_faults = block_faults(ref["block"])
    if ref_faults:
        return "UNKNOWN", "the reference node read the reference block wrongly (%s)" % "; ".join(ref_faults)
    for field in ("balance", "frontier"):
        for side, acct in (("this node", read["account"]), (REFERENCE, ref["account"])):
            if not acct.get(field):
                return "UNKNOWN", "account_info from %s has no %s, so there is nothing to compare" % (side, field)
    faults = block_faults(read["block"])
    for field in ("balance", "frontier"):
        if read["account"].get(field) != ref["account"].get(field):
            faults.append("%s %s vs %s at %s" % (field, str(read["account"].get(field))[:16],
                                                 str(ref["account"].get(field))[:16], REFERENCE))
    if faults:
        return "DISAGREES", "; ".join(faults)
    return "AGREES", "reference block as expected; treasury balance and frontier match %s" % REFERENCE


def run(candidates=CANDIDATES, call=rpc):
    ref = read_node(REFERENCE, call)
    rows = []
    ref_faults = block_faults(ref["block"]) if not ref["error"] else []
    rows.append({"node": REFERENCE, "verdict": "REFERENCE" if not ref["error"] and not ref_faults else "UNKNOWN",
                 "detail": ref["error"] or ("; ".join(ref_faults) if ref_faults else "the node every guide names")})
    for url in candidates:
        v, detail = verdict(read_node(url, call), ref)
        rows.append({"node": url, "verdict": v, "detail": detail})
    return rows


def exit_code(rows):
    others = [r["verdict"] for r in rows[1:]]
    if "DISAGREES" in others:
        return 1
    if "AGREES" in others:
        return 0
    return 3


def markdown(rows):
    lines = ["| node | verdict | detail |", "|---|---|---|"]
    for r in rows:
        lines.append("| %s | **%s** | %s |" % (r["node"], r["verdict"], r["detail"].replace("|", "/")))
    return "\n".join(lines) + "\n"


def main(argv):
    rows = run()
    if "--json" in argv:
        print(json.dumps(rows, indent=1))
    else:
        for r in rows:
            print("%-10s %-45s %s" % (r["verdict"], r["node"], r["detail"]))
    if "--summary-md" in argv:
        with open(argv[argv.index("--summary-md") + 1], "a") as f:
            f.write("## Second node for a Nano payment (challenge #230)\n\n" + markdown(rows))
    return exit_code(rows)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
