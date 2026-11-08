#!/usr/bin/env python3
"""Laws for challenge #232: ops/check-second-node.py fails closed, and keeps measuring every node bounties.txt names.

bounties.txt STEP 4 names second nodes "measured to agree" on the strength of this probe. Three ways it could say
AGREES without a real agreement: both sides' account_info missing balance (None == None), a reference node that read
the reference block wrongly, and a named node dropped from CANDIDATES so nothing measures it any more. And a node that
DISAGREES must make the run exit 1 (red), not hide in a zero exit.

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


def blocks_answer(ref_bi):
    """The reference answers blocks_info with ref_bi verbatim; n1 is healthy."""
    good = stub({"https://n1": (GOOD_BLOCK, dict(GOOD_ACCOUNT))})

    def call(url, payload):
        if url == csn.REFERENCE:
            return ref_bi if payload["action"] == "blocks_info" else dict(GOOD_ACCOUNT)
        return good(url, payload)
    return call


class ReferenceThatCannotReadTheBlockIsRed(unittest.TestCase):
    """nrx#212 review MEDIUM 2: rpc.nano.to denying the confirmed reference payment exited 3 (green)."""

    def check(self, ref_bi):
        rows = csn.run(["https://n1"], blocks_answer(ref_bi))
        self.assertEqual(rows[0]["verdict"], "UNKNOWN")
        self.assertTrue(rows[0]["faulty_reference"])
        self.assertIn("FAULTY REFERENCE", rows[0]["detail"])
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")
        self.assertEqual(csn.exit_code(rows), 4)
        return rows

    def test_block_not_found_exits_4(self):
        self.assertIn("Block not found", self.check({"error": "Block not found"})[0]["detail"])

    def test_empty_blocks_exits_4(self):
        self.check({"blocks": {}})

    def test_reference_block_null_exits_4(self):
        self.check({"blocks": {csn.REF_BLOCK: None}})


class OddBlocksShapeIsUnreadableNotACrash(unittest.TestCase):
    """nrx#212 review LOW 4: {"blocks": [..]} or {"blocks": "x"} raised AttributeError (exit 1, no summary)."""

    def test_candidate_with_list_or_string_blocks_is_unknown(self):
        for odd in ([GOOD_BLOCK], "x"):
            def call(url, payload, odd=odd):
                if url == "https://n1" and payload["action"] == "blocks_info":
                    return {"blocks": odd}
                return stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT), "https://n1": (GOOD_BLOCK, GOOD_ACCOUNT)})(url, payload)
            rows = csn.run(["https://n1"], call)
            self.assertEqual(rows[1]["verdict"], "UNKNOWN")
            self.assertEqual(csn.exit_code(rows), 3)

    def test_reference_with_list_or_string_blocks_exits_4(self):
        for odd in ([GOOD_BLOCK], "x"):
            rows = csn.run(["https://n1"], blocks_answer({"blocks": odd}))
            self.assertEqual(csn.exit_code(rows), 4)


ATTACKER = dict(GOOD_BLOCK, contents={"link_as_account": "nano_3attacker"})


def raw(answers):
    """answers: url -> (blocks_info answer or Exception, account_info answer or Exception), returned verbatim."""
    def call(url, payload):
        a = answers[url][0 if payload["action"] == "blocks_info" else 1]
        if isinstance(a, Exception):
            raise a
        return a
    return call


def wrap(block):
    return {"blocks": {csn.REF_BLOCK: block}}


class BlockIsJudgedBeforeAccountInfo(unittest.TestCase):
    """nrx#212 review round 2: an account_info failure discarded a block that was read, hiding a wrong payee."""

    def test_candidate_wrong_payee_with_account_error_disagrees(self):  # HIGH 1
        for acct in ({"error": "Account not found"}, OSError("timeout")):
            rows = csn.run(["https://n1"], raw({csn.REFERENCE: (wrap(GOOD_BLOCK), GOOD_ACCOUNT),
                                                "https://n1": (wrap(ATTACKER), acct)}))
            self.assertEqual(rows[1]["verdict"], "DISAGREES", acct)
            self.assertIn("payee", rows[1]["detail"])
            self.assertEqual(csn.exit_code(rows), 1)

    def test_reference_wrong_payee_with_account_error_exits_4(self):  # MEDIUM 2
        for acct in ({"error": "x"}, OSError("timeout")):
            rows = csn.run(["https://n1"], raw({csn.REFERENCE: (wrap(ATTACKER), acct),
                                                "https://n1": (wrap(GOOD_BLOCK), dict(GOOD_ACCOUNT))}))
            self.assertTrue(rows[0]["faulty_reference"], acct)
            self.assertIn("payee", rows[0]["detail"])
            self.assertEqual(csn.exit_code(rows), 4)

    def test_good_block_with_account_error_is_still_unknown(self):
        rows = csn.run(["https://n1"], raw({csn.REFERENCE: (wrap(GOOD_BLOCK), GOOD_ACCOUNT),
                                            "https://n1": (wrap(GOOD_BLOCK), OSError("timeout"))}))
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")
        self.assertEqual(csn.exit_code(rows), 3)

    def test_reference_good_block_with_account_error_is_unreachable_not_faulty(self):
        rows = csn.run(["https://n1"], raw({csn.REFERENCE: (wrap(GOOD_BLOCK), OSError("timeout")),
                                            "https://n1": (wrap(GOOD_BLOCK), dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[0]["verdict"], "UNKNOWN")
        self.assertFalse(rows[0]["faulty_reference"])
        self.assertEqual(csn.exit_code(rows), 3)


class CandidateDenyingThePaymentDisagrees(unittest.TestCase):
    """nrx#212 review round 2 LOW 3: "Block not found" for a confirmed payment is a different answer, not no answer."""

    def test_each_denial_disagrees(self):
        for bi in ({"error": "Block not found"}, {"blocks": {}}, wrap(None)):
            rows = csn.run(["https://n1"], raw({csn.REFERENCE: (wrap(GOOD_BLOCK), GOOD_ACCOUNT),
                                                "https://n1": (bi, dict(GOOD_ACCOUNT))}))
            self.assertEqual(rows[1]["verdict"], "DISAGREES", bi)
            self.assertIn("denies", rows[1]["detail"])
            self.assertEqual(csn.exit_code(rows), 1)

    def test_other_error_body_is_still_unknown(self):
        rows = csn.run(["https://n1"], raw({csn.REFERENCE: (wrap(GOOD_BLOCK), GOOD_ACCOUNT),
                                            "https://n1": ({"error": "rate limited"}, dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[1]["verdict"], "UNKNOWN")


class DocstringSaysWhatTheCodeDoes(unittest.TestCase):
    def test_no_every_candidate_is_unknown_claim(self):  # LOW 4
        doc = csn.__doc__
        self.assertNotIn("every candidate is UNKNOWN", " ".join(doc.split()))
        self.assertTrue(all(len(line) <= 120 for line in doc.splitlines()))


class GarbageBlockDoesNotCrash(unittest.TestCase):
    def test_a_string_block_is_a_fault_not_a_traceback(self):
        rows = csn.run(["https://n1"], stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT),
                                             "https://n1": ("garbage", dict(GOOD_ACCOUNT))}))
        self.assertEqual(rows[1]["verdict"], "DISAGREES")

    def test_string_contents_is_a_payee_fault(self):
        self.assertTrue(any(f.startswith("payee=") for f in csn.block_faults(dict(GOOD_BLOCK, contents="x"))))

    def test_a_disagreeing_node_turns_the_run_red(self):
        # was a check on second-node.yml; the owner removed every workflow 11-07 (challenge #234), so the law is the exit
        other = dict(GOOD_ACCOUNT, balance="1")
        rows = csn.run(["https://n1", "https://n2"], stub({csn.REFERENCE: (GOOD_BLOCK, GOOD_ACCOUNT),
                                                          "https://n1": (GOOD_BLOCK, GOOD_ACCOUNT),
                                                          "https://n2": (GOOD_BLOCK, other)}))
        self.assertEqual([r["verdict"] for r in rows[1:]], ["AGREES", "DISAGREES"])
        self.assertEqual(csn.exit_code(rows), 1)


if __name__ == "__main__":
    unittest.main()
