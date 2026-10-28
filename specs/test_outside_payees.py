#!/usr/bin/env python3
"""Laws for ops/outside-payees.py (challenge #174).

An outside agent's own nano_ address, named in a Moltbook comment, is read on the ledger whether or not the comment
is answered. Our own addresses never count as a payee, a bad checksum is never queried, a node that does not answer
is UNKNOWN (never "nobody paid"), and only a received payment from an account that is not ours counts as outside.

Run: python3 specs/test_outside_payees.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("op", os.path.join(ROOT, "ops", "outside-payees.py"))
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)

SELLER = "nano_3t1sxtuxyjgdabj6miwn6st58p8x553i8ybkikoc9ozn7mra7kk71iysfyn1"  # announced 10-28 08:07, valid checksum
ARION = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
BAD = "nano_3t1sxtuxyjgdabj6miwn6st58p8x553i8ybkikoc9ozn7mra7kk71iysfyn3"    # last character flipped
MILLI = str(10 ** 27)


def comment(content, author="antigravityandrew", at="2026-10-28T08:07:06Z", answered=True, ours=""):
    return {"author": author, "created_at": at, "comment_id": "7d5ddbfe-x", "answered": answered,
            "content": content, "our_comment": ours, "post_ours_comment": ""}


def node(received=(), receivable=(), down=False):
    def call(body):
        if down:
            raise OSError("timeout")
        if body["action"] == "receivable":
            return {"blocks": {h: {"amount": MILLI, "source": s} for h, s in receivable}}
        if not received:
            return {"error": "Account not found"}
        return {"history": [{"type": "receive", "account": s, "amount": MILLI, "hash": h} for h, s in received]}
    return call


class Laws(unittest.TestCase):
    def test_answered_comment_still_read(self):
        rep = op.build_report([comment(f"live: `{SELLER}` ready for test transfers")], node())
        self.assertEqual([r["address"] for r in rep["payees"]], [SELLER])
        self.assertEqual(rep["payees"][0]["state"], "UNOPENED")

    def test_our_addresses_never_payees(self):
        items = [comment(f"pay {op.TREASURY} or {op.UNSTUCK}"),
                 comment(f"you said {ARION}", ours=f"@x send to {ARION}")]
        self.assertEqual(op.build_report(items, node())["payees"], [])

    def test_bad_checksum_not_queried(self):
        def call(body):
            raise AssertionError("queried a bad address")
        rep = op.build_report([comment(BAD)], call)
        self.assertEqual(rep["payees"][0]["state"], "BAD CHECKSUM")

    def test_node_down_is_unknown(self):
        rep = op.build_report([comment(SELLER)], node(down=True))
        self.assertEqual(rep["payees"][0]["state"], "UNKNOWN")
        self.assertEqual(rep["outside_paid"], 0)

    def test_receivable_is_waiting_not_paid(self):
        rep = op.build_report([comment(SELLER)], node(receivable=[("AA" * 32, ARION)]))
        self.assertEqual(rep["payees"][0]["state"], "WAITING")
        self.assertEqual(rep["outside_paid"], 0)

    def test_payment_from_us_is_not_outside(self):
        rep = op.build_report([comment(SELLER)], node(received=[("BB" * 32, op.TREASURY)]))
        self.assertEqual(rep["payees"][0]["state"], "PAID")
        self.assertEqual(rep["payees"][0]["payments"][0]["payer"], "OURS")
        self.assertEqual(rep["outside_paid"], 0)

    def test_outside_payment_counts(self):
        rep = op.build_report([comment(SELLER)], node(received=[("CC" * 32, ARION)]))
        self.assertEqual(rep["outside_paid"], 1)

    def test_first_mention_wins_and_xrb_normalised(self):
        items = [comment(SELLER, author="later", at="2026-10-28T09:00:00Z"),
                 comment("xrb_" + SELLER[5:], author="first", at="2026-10-28T08:00:00Z")]
        rep = op.build_report(items, node())
        self.assertEqual([(r["author"], r["address"]) for r in rep["payees"]], [("first", SELLER)])


if __name__ == "__main__":
    unittest.main()
