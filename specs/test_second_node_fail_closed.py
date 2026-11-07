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

    def test_every_failure_but_unreadable_is_nonzero_and_distinct(self):
        # nrx#211 follow-up LOW 4 (the workflow is gone, owner rule a18424e): the exit code alone must say what
        # happened - 1 disagrees, 4 misread reference, 3 none readable, 0 agrees.
        self.assertEqual(csn.exit_code([{"verdict": "REFERENCE"}, {"verdict": "DISAGREES"}]), 1)
        self.assertEqual(csn.exit_code([{"verdict": "UNKNOWN", "faulty_reference": True}, {"verdict": "UNKNOWN"}]), 4)
        self.assertEqual(csn.exit_code([{"verdict": "REFERENCE"}, {"verdict": "UNKNOWN"}]), 3)
        self.assertEqual(csn.exit_code([{"verdict": "REFERENCE"}, {"verdict": "AGREES"}]), 0)


class WrongBlockIsNeverMasked(unittest.TestCase):
    """nrx#211 follow-up (2026-11-07): a missing field or a faulty reference hid a candidate's wrong block as UNKNOWN."""

    def test_wrong_payee_with_missing_balance_disagrees(self):
        attacker = dict(GOOD_BLOCK, contents={"link_as_account": "nano_3attacker"})
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT),
                                             "https://n1": (attacker, {"frontier": "AB" * 32})}))
        self.assertEqual(rows[1]["verdict"], "DISAGREES")
        self.assertIn("payee", rows[1]["detail"])
        self.assertEqual(csn.exit_code(rows), 1)

    def test_wrong_amount_with_empty_reference_account_disagrees(self):
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, {}),
                                             "https://n1": (dict(GOOD_BLOCK, amount="1"), dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[1]["verdict"], "DISAGREES")
        self.assertIn("amount", rows[1]["detail"])

    def test_wrong_block_disagrees_even_against_a_faulty_reference(self):
        unconfirmed = dict(GOOD_BLOCK, confirmed="false")
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (unconfirmed, GOOD_ACCOUNT),
                                             "https://n1": (dict(GOOD_BLOCK, subtype="receive"), dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[1]["verdict"], "DISAGREES")


class FaultyReferenceIsItsOwnRed(unittest.TestCase):
    def test_a_misread_reference_exits_4_not_3(self):
        wrong = dict(GOOD_BLOCK, contents={"link_as_account": "nano_3attacker"})
        rows = csn.run(["https://n1", "https://n2"], stub({csn.REFERENCE: (wrong, GOOD_ACCOUNT),
                                                           "https://n1": (GOOD_BLOCK, dict(GOOD_ACCOUNT)),
                                                           "https://n2": (GOOD_BLOCK, dict(GOOD_ACCOUNT))}))
        self.assertTrue(all(r["verdict"] == "UNKNOWN" for r in rows))
        self.assertEqual(csn.exit_code(rows), 4)

    def test_an_unreachable_reference_still_exits_3(self):
        def call(url, payload):
            if url == csn.REFERENCE:
                raise OSError("timeout")
            return stub({"https://n1": (GOOD_BLOCK, GOOD_ACCOUNT)})(url, payload)
        self.assertEqual(csn.exit_code(csn.run(["https://n1"], call)), 3)


class GarbageBlockDoesNotCrash(unittest.TestCase):
    def test_a_string_block_is_a_fault_not_a_traceback(self):
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT),
                                             "https://n1": ("garbage", dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[1]["verdict"], "DISAGREES")

    def test_string_contents_is_a_payee_fault(self):
        self.assertTrue(any(f.startswith("payee=") for f in csn.block_faults(dict(GOOD_BLOCK, contents="x"))))


if __name__ == "__main__":
    unittest.main()
