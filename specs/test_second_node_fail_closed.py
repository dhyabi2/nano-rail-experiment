#!/usr/bin/env python3
"""Laws for challenge #232: ops/check-second-node.py fails closed, and keeps measuring every node bounties.txt names.

bounties.txt STEP 4 names second nodes "measured to agree" on the strength of this probe. Three ways it could say
AGREES without a real agreement: both sides' account_info missing balance (None == None), a reference node that read
the reference block wrongly, and a named node dropped from CANDIDATES so nothing measures it any more. And a node that
DISAGREES must turn the scheduled run red, not hide in a green job's summary.

Run: python3 specs/test_second_node_fail_closed.py
"""
import importlib.util
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("csn", os.path.join(ROOT, "ops", "check-second-node.py"))
csn = importlib.util.module_from_spec(spec)
spec.loader.exec_module(csn)

GOOD_BLOCK = {"confirmed": "true", "subtype": "send", "amount": csn.REF_AMOUNT,
              "contents": {"link_as_account": csn.TREASURY}}
GOOD_ACCOUNT = {"balance": "71617800000000000000000000000000", "frontier": "AB" * 32}


def stub(answers):
    def call(url, payload):
        block, account = answers[url]
        if payload["action"] == "blocks_info":
            return {"blocks": {csn.REF_BLOCK: block}}
        return account
    return call


class FailClosed(unittest.TestCase):
    def test_two_missing_balances_are_not_agreement(self):
        bare = {"frontier": "AB" * 32}
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, bare), "https://n1": (GOOD_BLOCK, dict(bare))}))
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")
        self.assertIn("balance", rows[1]["detail"])
        self.assertEqual(csn.exit_code(rows), 3)

    def test_a_node_missing_frontier_is_unknown(self):
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT),
                                             "https://n1": (GOOD_BLOCK, {"balance": GOOD_ACCOUNT["balance"]})}))
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")
        self.assertIn("frontier", rows[1]["detail"])

    def test_a_faulty_reference_makes_every_candidate_unknown(self):
        unconfirmed = dict(GOOD_BLOCK, confirmed="false")
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (unconfirmed, GOOD_ACCOUNT),
                                             "https://n1": (GOOD_BLOCK, dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[0]["verdict"], "UNKNOWN")
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")
        self.assertIn("reference", rows[1]["detail"])

    def test_a_real_match_still_agrees(self):
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT),
                                             "https://n1": (GOOD_BLOCK, dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[1]["verdict"], "AGREES")

    def test_every_node_bounties_names_is_still_measured(self):
        text = open(os.path.join(ROOT, "published", "bounties.txt")).read()
        hosts = {re.sub(r"^https://([^/:]+).*", r"\1", c) for c in csn.CANDIDATES}
        for named in ("nanoslo.0x.no", "node.somenano.com", "rainstorm.city", "app.natrium.io"):
            self.assertIn(named, text, "bounties.txt STEP 4 no longer names %s: update this law" % named)
            self.assertIn(named, hosts, "%s is named in bounties.txt but the probe no longer measures it" % named)

    def test_a_disagreeing_node_turns_the_run_red(self):
        wf = open(os.path.join(ROOT, ".github", "workflows", "second-node.yml")).read()
        self.assertRegex(wf, r'if \[ "\$code" = "1" \]; then exit 1; fi')


if __name__ == "__main__":
    unittest.main()
