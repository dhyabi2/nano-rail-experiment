#!/usr/bin/env python3
"""Laws for challenge #230: ops/check-second-node.py names a second node only when it really agrees.

bounties.txt tells every payer to confirm on a second node and says "we have measured none". The probe that measures
one must never call a node that did not answer "agrees", must name the field a disagreeing node differs on, must send
only read-only RPC actions, and must run where egress is open (GitHub's runners), not only in the keeper's sandbox.

Run: python3 specs/test_second_node.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("csn", os.path.join(ROOT, "ops", "check-second-node.py"))
csn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(csn)

GOOD_BLOCK = {"confirmed": "true", "subtype": "send", "amount": csn.REF_AMOUNT,
              "contents": {"link_as_account": csn.TREASURY}}
GOOD_ACCOUNT = {"balance": "71617800000000000000000000000000", "frontier": "AB" * 32}


def stub(answers):
    """answers: url -> (block, account) or an Exception to raise."""
    sent = []

    def call(url, payload):
        sent.append(payload["action"])
        a = answers[url]
        if isinstance(a, Exception):
            raise a
        block, account = a
        if payload["action"] == "blocks_info":
            return {"blocks": {csn.REF_BLOCK: block}} if block is not None else {"blocks": {}}
        return account
    call.sent = sent
    return call


class SecondNode(unittest.TestCase):
    def test_a_matching_node_agrees(self):
        call = stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT), "https://n1": (GOOD_BLOCK, dict(GOOD_ACCOUNT))})
        rows = csn.run(["https://n1"], call)
        self.assertEqual([r["verdict"] for r in rows], ["REFERENCE", "AGREES"])
        self.assertEqual(csn.exit_code(rows), 0)
        self.assertEqual(set(call.sent), {"blocks_info", "account_info"})

    def test_a_silent_node_is_unknown_never_agrees(self):
        call = stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT), "https://n1": OSError("403 Forbidden")})
        rows = csn.run(["https://n1"], call)
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")
        self.assertIn("403", rows[1]["detail"])
        self.assertEqual(csn.exit_code(rows), 3, "no other node read is not a clean result")

    def test_an_error_body_is_unknown(self):
        call = stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT), "https://n1": (GOOD_BLOCK, {"error": "rate limited"})})
        self.assertEqual(csn.run(["https://n1"], call)[1]["verdict"], "UNKNOWN")

    def test_a_missing_block_is_unknown(self):
        call = stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT), "https://n1": (None, GOOD_ACCOUNT)})
        self.assertEqual(csn.run(["https://n1"], call)[1]["verdict"], "UNKNOWN")

    def test_disagreement_names_the_field(self):
        bad = dict(GOOD_BLOCK, confirmed="false")
        other = dict(GOOD_ACCOUNT, frontier="CD" * 32)
        call = stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT), "https://n1": (bad, GOOD_ACCOUNT),
                     "https://n2": (GOOD_BLOCK, other)})
        rows = csn.run(["https://n1", "https://n2"], call)
        self.assertEqual(rows[1]["verdict"], "DISAGREES")
        self.assertIn("confirmed=false", rows[1]["detail"])
        self.assertEqual(rows[2]["verdict"], "DISAGREES")
        self.assertIn("frontier", rows[2]["detail"])
        self.assertEqual(csn.exit_code(rows), 1)

    def test_nothing_to_compare_when_the_reference_is_down(self):
        call = stub({csn.REFERENCE: OSError("timeout"), "https://n1": (GOOD_BLOCK, GOOD_ACCOUNT)})
        rows = csn.run(["https://n1"], call)
        self.assertEqual([r["verdict"] for r in rows], ["UNKNOWN", "UNKNOWN"])

    def test_read_only(self):
        with self.assertRaises(ValueError):
            csn.rpc("https://n1", {"action": "process"})
        src = open(os.path.join(ROOT, "ops", "check-second-node.py")).read()
        for word in ("seed", "private", "send_block", '"process"'):
            self.assertNotIn(word, src.replace("sends nothing", "").replace("read-only", ""))

    def test_rpc_nano_to_is_not_its_own_second_node(self):
        self.assertNotIn(csn.REFERENCE, csn.CANDIDATES)

    def test_no_github_actions_workflow_is_assumed(self):
        # Owner rule (a18424e): no GitHub Actions. The probe is run by hand where egress is open; nothing may
        # claim a scheduled workflow runs it.
        self.assertFalse(os.path.exists(os.path.join(ROOT, ".github", "workflows", "second-node.yml")))
        self.assertNotIn(".github/workflows", open(os.path.join(ROOT, "ops", "check-second-node.py")).read())

    def test_bounties_names_only_measured_nodes(self):
        # Measured 08:24 UTC 2026-11-07 on GitHub's runners (second-node run 1): these AGREED with rpc.nano.to.
        measured = ["https://nanoslo.0x.no/proxy", "https://node.somenano.com/proxy",
                    "https://rainstorm.city/api", "https://app.natrium.io/api"]
        txt = open(os.path.join(ROOT, "published", "bounties.txt")).read()
        step4 = txt[txt.index(" STEP 4 - PROVE"):txt.index(" STEP 5 - TRY")]
        for node in measured:
            self.assertIn(node, step4)
            self.assertIn(node, csn.CANDIDATES, "a node named in the guide must stay in the daily probe")
        self.assertIn("Measured 08:24 UTC 2026-11-07", step4)
        self.assertIn("two names can be one operator", step4)
        self.assertNotIn("we have measured none", txt)


if __name__ == "__main__":
    unittest.main()
