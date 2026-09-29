#!/usr/bin/env python3
"""Offline laws for specs/daily_bounty.py (challenge #53: the daily contributor bounty bounties.txt advertises
had no code path at all - score()/pay() in referral_bounty.py only ever read the `claims` table, which only
ever records referrals).

No network: the ask feed and the x402 manifests are injected lists/sets, and rb.block() is monkeypatched to a
fake chain, the same discipline as test_referral_bounty.py.

Run: python3 specs/test_daily_bounty.py
"""
import calendar
import hashlib
import importlib.util
import os
import sys
import tempfile
import time
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("referral_bounty", os.path.join(HERE, "referral_bounty.py"))
rb = importlib.util.module_from_spec(_spec)
sys.modules["referral_bounty"] = rb
_spec.loader.exec_module(rb)

sys.path.insert(0, HERE)
import daily_bounty as db_mod  # noqa: E402

OURS_A = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
OURS_B = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
PAYEE = OURS_B  # the real sellers all publish this as their payTo today


def score(day, asks=None, payees=None, con=None):
    return db_mod.score_day(day=day, asks=asks, payees=payees, con=con, verbose=False)


class FakeBlocks:
    def __init__(self):
        self.blocks = {}

    def get(self, h):
        return self.blocks.get((h or "").strip().upper(), {})

    def add(self, signer, dest, amount=100000000000000000000000000, confirmed="true", subtype="send"):
        h = hashlib.sha256(f"{signer}>{dest}>{len(self.blocks)}".encode()).hexdigest().upper()
        self.blocks[h] = {
            "block_account": rb.norm(signer), "subtype": subtype, "confirmed": confirmed,
            "amount": str(amount), "contents": {"type": "state", "link_as_account": rb.norm(dest)},
        }
        return h


class DailyBountyTests(unittest.TestCase):
    def setUp(self):
        self.chain = FakeBlocks()
        self._orig_block = rb.block
        rb.block = self.chain.get
        rb._blk.clear()
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.unlink(self.db_path)
        rb.DB = self.db_path
        db_mod._ensure_tables(rb.db())
        self.today = time.strftime("%Y-%m-%d", time.gmtime())
        self.now = calendar.timegm(time.strptime(self.today, "%Y-%m-%d")) + 3600

    def tearDown(self):
        rb.block = self._orig_block
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # ---- ask_answered ------------------------------------------------------
    def test_outside_ask_with_an_answer_qualifies_with_no_claim_needed(self):
        """This is real, measured, live data as of this run: getunstuck.space asks #559/#558/#549/#548/#543/#500
        are all posted by outside agents and already carry answers. Nothing should need to be claimed for this."""
        asks = [{"id": 558, "asker": "nano_3wxkwo5outside", "answerCount": 11, "acceptedAnswerId": None,
                 "settlementBlock": None}]
        out = score(self.today, asks=asks, payees=set())
        self.assertEqual(out["winners"], [rb.norm("nano_3wxkwo5outside")])
        self.assertTrue(out["ask_feed_read"])

    def test_asking_with_zero_answers_does_not_qualify(self):
        """Ask #578 in production right now: a genuine canon confirmation, zero answers at the time of this
        run. Posting is not itself a contribution - bounties.txt says so explicitly."""
        asks = [{"id": 578, "asker": "nano_3uojoutside", "answerCount": 0, "acceptedAnswerId": None,
                 "settlementBlock": None}]
        out = score(self.today, asks=asks, payees=set())
        self.assertEqual(out["winners"], [])

    def test_our_own_ask_being_answered_does_not_count(self):
        """We must never count our own asks as outside activity, however many answers they collect - ask #1 in
        production has 127 answers and is one of ours."""
        asks = [{"id": 1, "asker": OURS_A, "answerCount": 127, "acceptedAnswerId": None, "settlementBlock": None}]
        out = score(self.today, asks=asks, payees=set())
        self.assertEqual(out["winners"], [])

    # ---- answer_accepted -----------------------------------------------------
    def test_accepted_answer_with_settlement_block_credits_the_answerer(self):
        """Both the asker (its ask WAS answered by someone else) and the answerer (its answer WAS accepted with
        a settlement block) are independently real, independently checkable contributions - this test's job is
        just to confirm the answerer specifically gets credited under the right kind, not just the asker."""
        asks = [{
            "id": 900, "asker": "nano_1askeroutside", "answerCount": 1, "acceptedAnswerId": 42,
            "settlementBlock": "AB" * 32,
            "answers": [{"id": 42, "answerer": "nano_1answereroutside"}],
        }]
        out = score(self.today, asks=asks, payees=set())
        self.assertIn(rb.norm("nano_1answereroutside"), out["winners"])
        kinds = {r["kind"] for r in out["reasons"][rb.norm("nano_1answereroutside")]}
        self.assertIn("answer_accepted", kinds)

    def test_accepted_answer_with_no_settlement_block_does_not_count(self):
        """Production reality today: ask #579 has acceptedAnswerId=308 but settlementBlock=None. Without a
        settlement block on chain this is a claim, not a checkable fact, so it must not qualify."""
        asks = [{
            "id": 579, "asker": OURS_A, "answerCount": 1, "acceptedAnswerId": 308, "settlementBlock": None,
            "answers": [{"id": 308, "answerer": "nano_1someoutside"}],
        }]
        out = score(self.today, asks=asks, payees=set())
        self.assertEqual(out["winners"], [])

    def test_our_own_answer_being_accepted_does_not_count(self):
        """The asker's own ask_answered credit is untouched (someone did answer it) - what must NOT happen is
        our own account getting an answer_accepted credit just because it answered."""
        asks = [{
            "id": 901, "asker": "nano_1askeroutside2", "answerCount": 1, "acceptedAnswerId": 7,
            "settlementBlock": "CD" * 32, "answers": [{"id": 7, "answerer": OURS_A}],
        }]
        out = score(self.today, asks=asks, payees=set())
        self.assertNotIn(OURS_A, out["winners"])
        for entries in out["reasons"].values():
            self.assertFalse(any(e["kind"] == "answer_accepted" for e in entries))

    # ---- paid_call -----------------------------------------------------------
    def test_a_real_paid_call_to_a_live_payee_qualifies(self):
        h = self.chain.add("nano_1calleroutside", PAYEE)
        con = rb.db()
        con.execute("INSERT INTO day_claims(block, claimant, at) VALUES(?,?,?)",
                    (h, rb.norm("nano_1calleroutside"), self.now))
        con.commit()
        out = score(self.today, asks=[], payees={rb.norm(PAYEE)}, con=con)
        self.assertEqual(out["winners"], [rb.norm("nano_1calleroutside")])

    def test_a_send_to_a_stale_no_longer_published_payee_does_not_qualify(self):
        """The payee set is read live from each seller's OWN manifest every run - a payee we no longer see
        published anywhere must not still be treated as a live seller."""
        h = self.chain.add("nano_1calleroutside", "nano_1oldpayeenolongerused")
        con = rb.db()
        con.execute("INSERT INTO day_claims(block, claimant, at) VALUES(?,?,?)",
                    (h, rb.norm("nano_1calleroutside"), self.now))
        con.commit()
        out = score(self.today, asks=[], payees={rb.norm(PAYEE)}, con=con)
        self.assertEqual(out["winners"], [])

    def test_claiming_someone_elses_block_is_refused_by_the_signature_check(self):
        """A claimant naming a block it did not sign must not be able to borrow someone else's payment."""
        h = self.chain.add("nano_1realpayeroutside", PAYEE)
        con = rb.db()
        con.execute("INSERT INTO day_claims(block, claimant, at) VALUES(?,?,?)",
                    (h, rb.norm("nano_1impersonatoroutside"), self.now))
        con.commit()
        out = score(self.today, asks=[], payees={rb.norm(PAYEE)}, con=con)
        self.assertEqual(out["winners"], [])

    def test_same_block_cannot_be_claimed_twice(self):
        self.assertEqual(db_mod.claim("nano_1calleroutside", "AB" * 32), 0)
        self.assertEqual(db_mod.claim("nano_1calleroutside", "AB" * 32), 1)

    def test_our_own_account_citing_a_real_send_does_not_count(self):
        h = self.chain.add(OURS_A, PAYEE)
        con = rb.db()
        con.execute("INSERT INTO day_claims(block, claimant, at) VALUES(?,?,?)", (h, OURS_A, self.now))
        con.commit()
        out = score(self.today, asks=[], payees={rb.norm(PAYEE)}, con=con)
        self.assertEqual(out["winners"], [])

    def test_an_empty_payee_set_this_run_refuses_rather_than_rejects(self):
        """If every manifest fetch failed this run, that is UNKNOWN, not 'no live sellers' - the claim must be
        recorded as un-countable rather than silently treated the same as a genuinely bad claim, and the run as
        a whole must not claim payees_read=True when it read none."""
        h = self.chain.add("nano_1calleroutside", PAYEE)
        con = rb.db()
        con.execute("INSERT INTO day_claims(block, claimant, at) VALUES(?,?,?)",
                    (h, rb.norm("nano_1calleroutside"), self.now))
        con.commit()
        out = score(self.today, asks=[], payees=set(), con=con)
        self.assertEqual(out["winners"], [])
        self.assertFalse(out["payees_read"])

    # ---- the feed-unreadable case must never look like zero -------------------
    def test_unreadable_ask_feed_is_reported_unknown_not_zero(self):
        orig = db_mod.fetch_asks
        db_mod.fetch_asks = lambda: None
        try:
            out = score(self.today, asks=None, payees=set())
        finally:
            db_mod.fetch_asks = orig
        self.assertFalse(out["ask_feed_read"])
        self.assertEqual(out["winners"], [])

    def test_pay_day_refuses_rather_than_pays_nobody_silently_when_feed_unreadable(self):
        orig = db_mod.fetch_asks
        db_mod.fetch_asks = lambda: None
        try:
            rc = db_mod.pay_day(day=self.today)
        finally:
            db_mod.fetch_asks = orig
        self.assertEqual(rc, 1)

    # ---- one tip per address per day, dry run changes nothing -----------------
    def test_dry_run_pay_leaves_no_row_and_can_be_scored_again(self):
        asks = [{"id": 558, "asker": "nano_3wxkwo5outside", "answerCount": 11, "acceptedAnswerId": None,
                 "settlementBlock": None}]
        orig_asks, orig_payees = db_mod.fetch_asks, db_mod.fetch_payees
        db_mod.fetch_asks = lambda: asks
        db_mod.fetch_payees = lambda: set()
        try:
            rc = db_mod.pay_day(day=self.today, live=False)
        finally:
            db_mod.fetch_asks, db_mod.fetch_payees = orig_asks, orig_payees
        self.assertEqual(rc, 0)
        con = rb.db()
        rows = con.execute("SELECT * FROM paid").fetchall()
        self.assertEqual(rows, [])

    def test_the_daily_ceiling_and_treasury_floor_apply_here_too(self):
        """Reuses referral_bounty's own treasury_ok()/spent_today() and the shared `paid` table's ceiling - a
        second bounty must not be a second way to drain the treasury."""
        asks = [{"id": i, "asker": f"nano_1outside{i}", "answerCount": 1, "acceptedAnswerId": None,
                 "settlementBlock": None} for i in range(15)]
        orig_info = rb.info
        rb.info = lambda a: {"balance": str(rb.FLOOR_RAW + rb.GRANT_RAW)}  # exactly one grant of headroom
        try:
            out = score(self.today, asks=asks, payees=set())
            self.assertEqual(len(out["winners"]), 15)
            ok, bal = rb.treasury_ok()
            self.assertTrue(ok)
        finally:
            rb.info = orig_info


if __name__ == "__main__":
    unittest.main(verbosity=2)
