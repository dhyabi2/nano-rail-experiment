#!/usr/bin/env python3
"""Offline laws for specs/referral_bounty.py.

No network, no real chain: history() and info() are monkeypatched to a fake ledger built per test. This exists
because the referral bounty's entire security argument is arithmetic over chain data (specs/04-REFERRAL-BOUNTY.md)
and, before this file, nothing exercised it - a bug here either pays a Sybil ring or silently starves real
referrers, and nobody would notice until real XNO moved.

Run: python3 specs/test_referral_bounty.py
"""
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

XNO_HALF = 500000000000000000000000000000
XNO_045 = 450000000000000000000000000000


class FakeChain:
    """A hand-built ledger. Keys are already-normalised nano_ addresses."""

    def __init__(self):
        self.history = {}
        self.info = {}

    def h(self, acct, count=50):
        return self.history.get(rb.norm(acct), [])

    def i(self, acct):
        return self.info.get(rb.norm(acct), {})


class ReferralBountyTests(unittest.TestCase):
    def setUp(self):
        self.chain = FakeChain()
        self._orig_history, self._orig_info = rb.history, rb.info
        rb.history, rb.info = self.chain.h, self.chain.i
        rb._hist.clear()
        rb._info.clear()
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.unlink(self.db_path)  # db() creates it fresh
        rb.DB = self.db_path

    def tearDown(self):
        rb.history, rb.info = self._orig_history, self._orig_info
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    # ---- fixture builders -------------------------------------------------
    def fund(self, acct, blocks):
        """Register a funder account that itself has no interesting history, just a block count."""
        self.chain.info[rb.norm(acct)] = {"block_count": str(blocks)}
        self.chain.history.setdefault(rb.norm(acct), [])

    def agent(self, addr, funded_by, blocks=3, ago=3600, sent_ago=60, no_send=False):
        """A normal converted agent: received from `funded_by`, then sent (self-custody proof)."""
        now = time.time()
        recv = {"type": "receive", "account": rb.norm(funded_by),
                "local_timestamp": str(int(now - ago)), "amount": str(XNO_HALF)}
        hist = [recv] if no_send else [
            {"type": "send", "local_timestamp": str(int(now - sent_ago)), "amount": str(XNO_045)}, recv,
        ]
        self.chain.history[rb.norm(addr)] = hist
        self.chain.info[rb.norm(addr)] = {"block_count": str(blocks)}

    def pass_through(self, addr, funded_by):
        """Two blocks, forwards ~everything within minutes: an exchange deposit slip, not an agent."""
        now = time.time()
        self.chain.history[rb.norm(addr)] = [
            {"type": "send", "local_timestamp": str(int(now - 100)), "amount": str(XNO_045)},
            {"type": "receive", "account": rb.norm(funded_by), "local_timestamp": str(int(now - 150)),
             "amount": str(XNO_HALF)},
        ]
        self.chain.info[rb.norm(addr)] = {"block_count": "2"}

    def claim(self, referrer, referred, block="BLOCKHASH"):
        con = rb.db()
        con.execute("INSERT OR IGNORE INTO claims(referred,referrer,block,at) VALUES(?,?,?,?)",
                    (rb.norm(referred), rb.norm(referrer), block, time.time()))
        con.commit()
        con.close()

    # ---- the bug this file exists to catch --------------------------------
    def test_two_referrals_sharing_a_public_exchange_both_count(self):
        """Challenge #47: two UNRELATED real agents who both cashed out through the same exchange (Nanswap's own
        pattern in ARION's case file) must not collapse into one referral just because they share that exchange."""
        exchange = "nano_1exchangehotwallet"
        self.fund(exchange, blocks=200000)  # Nanswap-shaped: far above SERVICE_BLOCKS
        self.agent("nano_1referredA", funded_by=exchange)
        self.agent("nano_1referredB", funded_by=exchange)
        self.claim("nano_1referrerR", "nano_1referredA")
        self.claim("nano_1referrerR", "nano_1referredB")

        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 2)
        self.assertEqual(out["ranking"][0]["count"], 2)
        self.assertEqual(set(out["ranking"][0]["referred"]), {"nano_1referreda", "nano_1referredb"})

    def test_two_referrals_sharing_a_private_wallet_count_once(self):
        """The case rule 2 actually exists for: one attacker-controlled stash (low block count) funding several
        addresses directly must still collapse to a single referral."""
        stash = "nano_1attackerstash"
        self.fund(stash, blocks=4)  # a fresh private wallet, not a service
        self.agent("nano_1referredC", funded_by=stash)
        self.agent("nano_1referredD", funded_by=stash)
        self.claim("nano_1referrerR", "nano_1referredC")
        self.claim("nano_1referrerR", "nano_1referredD")

        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 1)
        rejected = [d for d in out["detail"] if not d["counted"]]
        self.assertEqual(len(rejected), 1)
        self.assertIn("private", rejected[0]["why"])

    # ---- the rules that already existed, still enforced --------------------
    def test_self_referral_rejected(self):
        self.fund("nano_1funder", blocks=10)
        self.agent("nano_1both", funded_by="nano_1funder")
        self.claim("nano_1both", "nano_1both")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertEqual(out["detail"][0]["why"], "self-referral")

    def test_referred_funded_by_us_rejected(self):
        ours = next(iter(rb.OURS))
        self.fund("nano_1decoy", blocks=10)
        self.agent("nano_1referredE", funded_by=ours)
        self.claim("nano_1referrerR", "nano_1referredE")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("funded by us", out["detail"][0]["why"])

    def test_referrer_is_the_funder_rejected(self):
        self.agent("nano_1referredF", funded_by="nano_1referrerR")
        self.claim("nano_1referrerR", "nano_1referredF")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("funded by the referrer itself", out["detail"][0]["why"])

    def test_no_signed_send_rejected(self):
        self.fund("nano_1funder2", blocks=10)
        self.agent("nano_1referredG", funded_by="nano_1funder2", no_send=True)
        self.claim("nano_1referrerR", "nano_1referredG")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("no signed send", out["detail"][0]["why"])

    def test_pass_through_rejected(self):
        self.fund("nano_1funder3", blocks=10)
        self.pass_through("nano_1referredH", funded_by="nano_1funder3")
        self.claim("nano_1referrerR", "nano_1referredH")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("deposit", out["detail"][0]["why"])

    def test_never_funded_rejected(self):
        self.chain.history["nano_1referredi"] = [
            {"type": "send", "local_timestamp": str(int(time.time())), "amount": str(XNO_045)}]
        self.chain.info["nano_1referredi"] = {"block_count": "1"}
        self.claim("nano_1referrerR", "nano_1referredI")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("no incoming funding", out["detail"][0]["why"])

    def test_empty_period_pays_nobody(self):
        # pay() must not touch the treasury or any sender when there is nothing to pay.
        rc = rb.pay("hour", live=False)
        self.assertEqual(rc, 0)

    def test_period_id_is_clock_derived_not_stored(self):
        h1 = rb.period_id("hour")
        h2 = rb.period_id("hour")
        self.assertEqual(h1, h2)  # same clock, same id - never an incrementing counter a crash could double
        self.assertRegex(h1, r"^\d{4}-\d{2}-\d{2}T\d{2}$")
        self.assertRegex(rb.period_id("day"), r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
