#!/usr/bin/env python3
"""check-second-node: which public Nano node, other than rpc.nano.to, gives the same answer about our money? Read only.

Found 2026-11-07 (challenge #230). bounties.txt tells every buyer and seller to confirm a payment on "a second node
you choose, run by someone else", and in the same section says "We still name no second node: we have measured
none." Three outside agents asked for exactly that second read: bosco-roteo (10-29), a2awire (10-31) and rootoffork
(Moltbook, 11-07 03:58: "read the account balance ... from a second independent node and compare"). We measured none
because the keeper's sandbox reaches only rpc.nano.to: on 11-07 08:2x every one of the other candidates below was
refused by its egress proxy (403). Run it by hand from a machine with open egress (no GitHub Actions workflow runs
it); --summary-md writes the table to a file.

For each candidate it asks, at the same moment as rpc.nano.to:
  - blocks_info on a reference payment (an outside agent's first payment to the treasury, B749B757..., bounties.txt
    STEP 4's example): confirmed, subtype send, payee the treasury, amount 0.0005 XNO;
  - account_info on the treasury: balance and frontier, compared with rpc.nano.to's read.
Verdict per node: AGREES (the block reads exactly as expected AND balance and frontier match rpc.nano.to's),
DISAGREES (it answered, with different fields - name the field; or it answered that the confirmed reference payment
does not exist: "Block not found", no blocks, the hash mapped to null), or UNKNOWN (no answer, a timeout, a non-JSON,
another error body, an odd shape). A node we could not read is UNKNOWN, never "agrees" and never "disagrees".
A candidate's block is always judged first, against the fixed expected values, not against rpc.nano.to: a wrong or
denied block DISAGREES even when its own account_info fails, a balance or frontier is missing, or the reference is
faulty or down. Fail closed (challenge #232): only a candidate whose block reads as expected becomes UNKNOWN when
rpc.nano.to itself reads the reference block wrongly, or either side's account_info fails or lacks balance or
frontier - two missing fields are not two equal answers, and agreeing with a faulty reference is not agreeing with
the ledger.

What this cannot tell: who runs a node. Two hostnames can be one operator, or one backend behind two proxies, and
then two "witnesses" are one. It also proves nothing on its own: two nodes that agree can share a fault (bounties.txt
section 7). It only says which node a stranger could add today and get a real second read from.

    python3 ops/check-second-node.py [--json] [--summary-md FILE]
    exit 0 at least one other node AGREES; 1 some node DISAGREES; 3 no other node could be read (UNKNOWN);
    4 rpc.nano.to itself read the reference block wrongly, or answered but could not give it ("Block not found", no
      blocks, the hash mapped to null) - nothing can be compared, and that is news, not a flaky day. A reference that
      does not answer at all (timeout, refusal) is 3.
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
    """What one node said. Keys:
    block: the reference block as answered (any JSON value but null), or None;
    error: why blocks_info told us nothing (timeout, refusal, reset, or one of the two cases below);
    block_unreadable: blocks_info answered, but with an error body other than "not found" or an odd shape;
    block_denied: blocks_info answered cleanly that it has no such block ("Block not found", no blocks, hash -> null);
    account: the account_info dict, or None; account_error: why account_info told us nothing.
    The block is asked and kept first: an account_info failure never discards a block that was read.
    """
    out = {"block": None, "error": None, "block_denied": False, "block_unreadable": False, "account": None, "account_error": None}
    try:
        bi = call(url, {"action": "blocks_info", "hashes": [REF_BLOCK], "json_block": "true"})
    except Exception as e:  # timeout, refusal, reset, bad JSON: we learned nothing
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
        return out
    blocks = bi.get("blocks") if isinstance(bi, dict) else None
    if isinstance(bi, dict) and "error" in bi:
        if "not found" in str(bi["error"]).lower():
            out["block_denied"] = True
        else:
            out["block_unreadable"] = True
        out["error"] = "blocks_info error body: %s" % str(bi)[:120]
    elif isinstance(blocks, dict) and blocks.get(REF_BLOCK) is None:
        out["block_denied"] = True
        out["error"] = "blocks_info answered without the reference block: %s" % str(bi)[:120]
    elif not isinstance(blocks, dict):
        out["block_unreadable"] = True
        out["error"] = "blocks_info answer has no blocks object: %s" % str(bi)[:120]
    else:
        out["block"] = blocks[REF_BLOCK]
    try:
        ai = call(url, {"action": "account_info", "account": TREASURY})
    except Exception as e:
        out["account_error"] = "account_info %s: %s" % (type(e).__name__, str(e)[:120])
        return out
    if not isinstance(ai, dict) or "error" in ai:
        out["account_error"] = "account_info error body: %s" % str(ai)[:120]
    else:
        out["account"] = ai
    return out


def block_faults(b):
    if not isinstance(b, dict):
        return ["block=%s (not an object)" % type(b).__name__]
    faults = []
    contents = b.get("contents")
    if not isinstance(contents, dict):
        contents = {}
    if str(b.get("confirmed")).lower() != "true":
        faults.append("confirmed=%s" % b.get("confirmed"))
    if b.get("subtype") != "send":
        faults.append("subtype=%s" % b.get("subtype"))
    if contents.get("link_as_account") != TREASURY:
        faults.append("payee=%s" % str(contents.get("link_as_account"))[:16])
    if str(b.get("amount")) != REF_AMOUNT:
        faults.append("amount=%s" % b.get("amount"))
    return faults


def reference_faults(ref):
    """Why rpc.nano.to's own read of the reference block is wrong ([] if it is right or we could not read it)."""
    if ref["block_denied"]:
        return ["cannot read the confirmed reference payment %s (%s)" % (REF_BLOCK[:8], ref["error"])]
    if ref["block_unreadable"]:
        return [ref["error"]]
    if ref["error"]:
        return []  # timeout, refusal, reset: unreachable (exit 3), not faulty
    return block_faults(ref["block"])


def verdict(read, ref):
    """('AGREES'|'DISAGREES'|'UNKNOWN', detail)."""
    # A candidate's own block is judged against the fixed expected block first, so neither its own account_info
    # failure, a gap, nor a faulty or unreachable reference can mask a wrong or denied payment.
    if read["block_denied"]:
        return "DISAGREES", "denies the confirmed reference payment %s (%s)" % (REF_BLOCK[:8], read["error"])
    if read["error"]:
        return "UNKNOWN", read["error"]
    own_faults = block_faults(read["block"])
    if own_faults:
        return "DISAGREES", "; ".join(own_faults)
    if read["account_error"]:
        return "UNKNOWN", "reference block as expected, but %s" % read["account_error"]
    if reference_faults(ref):
        return "UNKNOWN", "the reference node read the reference block wrongly (%s)" % "; ".join(reference_faults(ref))
    if ref["error"] or ref["account_error"]:
        return "UNKNOWN", "the reference node could not be read, so there is nothing to compare with"
    for field in ("balance", "frontier"):
        for side, acct in (("this node", read["account"]), (REFERENCE, ref["account"])):
            if not acct.get(field):
                return "UNKNOWN", "account_info from %s has no %s, so there is nothing to compare" % (side, field)
    faults = []
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
    ref_faults = reference_faults(ref)
    if ref_faults:
        detail = "FAULTY REFERENCE: %s %s" % (REFERENCE, "; ".join(ref_faults))
    else:
        detail = ref["error"] or ref["account_error"] or "the node every guide names"
    ok = not (ref_faults or ref["error"] or ref["account_error"])
    rows.append({"node": REFERENCE, "verdict": "REFERENCE" if ok else "UNKNOWN",
                 "detail": detail, "faulty_reference": bool(ref_faults)})
    for url in candidates:
        v, detail = verdict(read_node(url, call), ref)
        rows.append({"node": url, "verdict": v, "detail": detail})
    return rows


def exit_code(rows):
    others = [r["verdict"] for r in rows[1:]]
    if "DISAGREES" in others:
        return 1
    if rows and rows[0].get("faulty_reference"):
        return 4
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
