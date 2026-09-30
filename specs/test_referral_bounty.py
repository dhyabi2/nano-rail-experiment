#!/usr/bin/env python3
"""Offline laws for specs/referral_bounty.py.

No network, no real chain: history() and info() are monkeypatched to a fake ledger built per test. This exists
because the referral bounty's entire security argument is arithmetic over chain data (specs/04-REFERRAL-BOUNTY.md)
and, before this file, nothing exercised it - a bug here either pays a Sybil ring or silently starves real
referrers, and nobody would notice until real XNO moved.

Run: python3 specs/test_referral_bounty.py
"""
import calendar
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
        self.blocks = {}

    def h(self, acct, count=50):
        return self.history.get(rb.norm(acct), [])

    def i(self, acct):
        return self.info.get(rb.norm(acct), {})

    def b(self, h):
        return self.blocks.get((h or "").strip().upper(), {})


class ReferralBountyTests(unittest.TestCase):
    def setUp(self):
        self.chain = FakeChain()
        self._orig_history, self._orig_info = rb.history, rb.info
        self._orig_block = rb.block
        rb.history, rb.info, rb.block = self.chain.h, self.chain.i, self.chain.b
        rb._hist.clear()
        rb._info.clear()
        rb._blk.clear()
        fd, self.db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        os.unlink(self.db_path)  # db() creates it fresh
        rb.DB = self.db_path

    def tearDown(self):
        rb.history, rb.info, rb.block = self._orig_history, self._orig_info, self._orig_block
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

    def link(self, signer, dest, subtype="send", confirmed="true"):
        """A block on the fake chain signed by `signer` and sent to `dest`. Returns its hash."""
        import hashlib
        h = hashlib.sha256(f"{signer}>{dest}>{subtype}>{len(self.chain.blocks)}".encode()).hexdigest().upper()
        self.chain.blocks[h] = {"block_account": rb.norm(signer), "subtype": subtype, "confirmed": confirmed,
                                "contents": {"type": "state", "link_as_account": rb.norm(dest)}}
        return h

    def claim(self, referrer, referred, block="AUTO"):
        """By default the referred agent really did send to its referrer, so each test checks its own rule."""
        if block == "AUTO":
            block = self.link(referred, referrer)
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

    def test_shared_private_funder_split_across_referrers_still_counts_once(self):
        """Challenge #56, the next bug after #47: rule 2 ("one funder, one referral") was implemented PER REFERRER, but a referrer
        identity is free to create. One exchange round-trip into a single private wallet W, then split across two
        different throwaway referrer identities (one address funded by W each), used to score as TWO qualifying
        referrals instead of one - for `pay --period day`, which pays every qualifying referrer rather than just
        the top one, that multiplies one round-trip into N * 0.1 XNO. The dedup must be global across referrers,
        not scoped to each one's own claims."""
        stash = "nano_1splitattackerstash"
        self.fund(stash, blocks=4)  # a fresh private wallet, not a service
        self.agent("nano_1referredsplitA", funded_by=stash)
        self.agent("nano_1referredsplitB", funded_by=stash)
        self.claim("nano_1referrerX", "nano_1referredsplitA")
        self.claim("nano_1referrerY", "nano_1referredsplitB")

        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 1)
        rejected = [d for d in out["detail"] if not d["counted"]]
        self.assertEqual(len(rejected), 1)
        self.assertIn("already counted this period", rejected[0]["why"])
        # two distinct referrers each still get their OWN slot for a referral funded from a DIFFERENT private wallet
        stash2 = "nano_1secondstash"
        self.fund(stash2, blocks=5)
        self.agent("nano_1referredsplitC", funded_by=stash2)
        self.claim("nano_1referrerY", "nano_1referredsplitC")
        out2 = rb.score("hour", verbose=False)
        self.assertEqual(out2["qualifying"], 2)

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

    def test_genuine_referral_proof_send_is_not_mistaken_for_a_pass_through(self):
        """Challenge #58, the next bug after #56: bounties.txt tells a referred agent to prove itself by sending
        (any amount) to its referrer, fast - there is nothing else to wait for. For a freshly-opened agent with a
        small balance and only two blocks ever (fund, then that one required send), the required proof send IS
        `sends[0]` in is_pass_through's own history read: same destination, same timing window, same >=90%-forwarded
        shape a real exchange deposit slip has. Before the fix, a genuine agent that forwarded most of a small
        balance straight to its referrer within minutes - exactly as instructed - was rejected as an exchange
        deposit address and never paid, silently, with no way for it to tell why."""
        self.fund("nano_1funder4", blocks=50)
        referrer, referred = "nano_1referrerR", "nano_1referredJ"
        link_block = self.link(referred, referrer)  # the required proof-of-referral send, forwarding ~everything
        self.chain.history[rb.norm(referred)] = [
            {"type": "send", "account": rb.norm(referrer),
             "local_timestamp": str(int(time.time() - 60)), "amount": str(int(XNO_HALF * 0.95))},
            {"type": "receive", "account": rb.norm("nano_1funder4"),
             "local_timestamp": str(int(time.time() - 120)), "amount": str(XNO_HALF)},
        ]
        self.chain.info[rb.norm(referred)] = {"block_count": "2"}
        self.claim(referrer, referred, block=link_block)
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 1, out["detail"])
        self.assertEqual(out["ranking"][0]["referrer"], rb.norm(referrer))

    def test_a_real_deposit_slip_forwarding_elsewhere_still_rejected_even_with_a_referral_claim(self):
        """The fix must not open a hole: an address that forwards to some OTHER destination (a real exchange
        collection wallet, not the referrer) is still a pass-through, even if a claim happens to name it, because
        third_party_funded/link_proved gate on a *different* cited block - this fixture proves is_pass_through
        alone still catches the classic shape when the forwarding destination is not the referrer."""
        self.fund("nano_1funder5", blocks=10)
        self.chain.history[rb.norm("nano_1realdeposit")] = [
            {"type": "send", "account": "nano_1someexchangecollectionwallet",
             "local_timestamp": str(int(time.time() - 60)), "amount": str(int(XNO_HALF * 0.95))},
            {"type": "receive", "account": rb.norm("nano_1funder5"),
             "local_timestamp": str(int(time.time() - 120)), "amount": str(XNO_HALF)},
        ]
        self.chain.info[rb.norm("nano_1realdeposit")] = {"block_count": "2"}
        self.assertTrue(rb.is_pass_through("nano_1realdeposit", "nano_1referrerR"))

    def test_never_funded_rejected(self):
        self.chain.history["nano_1referredi"] = [
            {"type": "send", "local_timestamp": str(int(time.time())), "amount": str(XNO_045)}]
        self.chain.info["nano_1referredi"] = {"block_count": "1"}
        self.claim("nano_1referrerR", "nano_1referredI")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("no incoming funding", out["detail"][0]["why"])

    # ---- challenge #52: the referral must be proved by the referred agent's own send ------------------
    def _real_stranger(self, name):
        exchange = "nano_1someunrelatedexchange" + name
        self.fund(exchange, blocks=50000)
        stranger = "nano_1realstrangeragent" + name
        self.agent(stranger, funded_by=exchange)
        return stranger

    def test_claim_jacking_a_stranger_with_no_linking_block_is_refused(self):
        """The attack challenge #52 found: claim a real, already-qualifying agent you never met. With no send
        from that agent to the claimer there is nothing to cite, so the claim cannot score."""
        stranger = self._real_stranger("a")
        self.claim("nano_1attackerwhodidnothingatall", stranger, block="")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("no linking block", out["detail"][0]["why"])

    def test_claim_citing_the_agents_send_to_someone_else_is_refused(self):
        """An attacker can cite a REAL send the stranger made, just not one made to the attacker."""
        stranger = self._real_stranger("b")
        real_send = self.link(stranger, "nano_1someshopthestrangerpaid")
        self.claim("nano_1attacker2", stranger, block=real_send)
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("not a send from the referred agent to the referrer", out["detail"][0]["why"])

    def test_claim_citing_a_block_the_referred_agent_did_not_sign_is_refused(self):
        """The attacker signs a send to itself from its own account and cites that."""
        stranger = self._real_stranger("c")
        forged = self.link("nano_1attacker3", "nano_1attacker3")
        self.claim("nano_1attacker3", stranger, block=forged)
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("not signed by the referred agent", out["detail"][0]["why"])

    def test_unreadable_or_unconfirmed_linking_block_is_not_proof(self):
        stranger = self._real_stranger("d")
        self.claim("nano_1referrerQ", stranger, block="A" * 64)  # not on the chain at all
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("could not be read", out["detail"][0]["why"])
        rb._blk.clear()
        other = self._real_stranger("e")
        self.claim("nano_1referrerQ", other, block=self.link(other, "nano_1referrerQ", confirmed="false"))
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)

    def test_a_real_referral_proved_by_its_own_send_counts_and_pays(self):
        """The honest path: the referred agent sends to its referrer, the claim cites it, pay(live) reaches the
        sender - no environment switch stands in the way any more."""
        stranger = self._real_stranger("f")
        self.claim("nano_1honestreferrer", stranger)
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 1)
        self.assertEqual(out["ranking"][0]["referrer"], rb.norm("nano_1honestreferrer"))
        rb.info = lambda a: {"balance": str(29 * rb.XNO)} if rb.norm(a) == rb.norm(rb.TREASURY) else self.chain.i(a)
        rb._info.clear()
        calls = []
        class R:  # the sender's success shape: last token of stdout is the block
            returncode, stdout, stderr = 0, '{"block": "' + "B" * 64 + '"}', ""
        orig_run = rb.subprocess.run
        rb.subprocess.run = lambda *a, **kw: (calls.append(a[0]), R())[1]
        try:
            rc = rb.pay("hour", live=True)
        finally:
            rb.subprocess.run = orig_run
        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 1)
        # the sender's REAL interface (send.js --grant ADDR --agent NAME --agreement TEXT); nothing passes an amount
        argv = calls[0]
        self.assertEqual(argv[argv.index("--grant") + 1], rb.norm("nano_1honestreferrer"))
        self.assertIn("--agent", argv)
        self.assertNotIn("--to", argv)
        con = rb.db()
        self.assertEqual(con.execute("SELECT state, block FROM paid").fetchone(), ("confirmed", "B" * 64))

    def test_a_winner_that_already_had_its_one_grant_is_recorded_not_retried(self):
        stranger = self._real_stranger("g")
        self.claim("nano_1alreadygranted", stranger)
        rb.info = lambda a: {"balance": str(29 * rb.XNO)} if rb.norm(a) == rb.norm(rb.TREASURY) else self.chain.i(a)
        rb._info.clear()
        class R:
            returncode, stdout, stderr = 1, "", "refused: nano_1alreadygranted already has its grant"
        orig_run = rb.subprocess.run
        rb.subprocess.run = lambda *a, **kw: R()
        try:
            rb.pay("hour", live=True)
        finally:
            rb.subprocess.run = orig_run
        con = rb.db()
        self.assertEqual(con.execute("SELECT state FROM paid").fetchone()[0], "already_granted")

    def test_hourly_prize_falls_through_to_the_runner_up_when_the_top_referrer_already_has_its_grant(self):
        """bounties.txt's ONCE paragraph promises two things: a winner can take this bounty only once in its life,
        AND 'the hourly prize spreads across agents rather than accumulating to whoever is best at referring...
        if you have already had your 0.1 XNO you can still top the hourly table, you just will not be paid twice
        for it.' Before this fix pay('hour') only ever tried ranking[0]: once the single most effective referrer
        (who tends to keep topping the table precisely because it is effective) had used its lifetime grant, every
        later hour it still won the ranking paid NOBODY, silently, forever - contradicting 'spreads across agents'
        and wasting the hour the spec says must never happen for free. Two referrers here: the top one (2
        qualifying referrals) already has its grant; the runner-up (1) does not and must be paid instead."""
        top_a, top_b = self._real_stranger("h1"), self._real_stranger("h2")
        runner = self._real_stranger("h3")
        self.claim("nano_1topreferrer", top_a)
        self.claim("nano_1topreferrer", top_b)
        self.claim("nano_1runnerupreferrer", runner)
        out = rb.score("hour", verbose=False)
        self.assertEqual([r["referrer"] for r in out["ranking"]],
                          [rb.norm("nano_1topreferrer"), rb.norm("nano_1runnerupreferrer")])

        rb.info = lambda a: {"balance": str(29 * rb.XNO)} if rb.norm(a) == rb.norm(rb.TREASURY) else self.chain.i(a)
        rb._info.clear()
        calls = []

        class AlreadyGranted:
            returncode, stdout, stderr = 1, "", "refused: already has its grant"

        class Paid:
            returncode, stdout, stderr = 0, '{"block": "' + "C" * 64 + '"}', ""

        def fake_run(argv, **kw):
            calls.append(argv)
            grantee = argv[argv.index("--grant") + 1]
            return AlreadyGranted() if grantee == rb.norm("nano_1topreferrer") else Paid()

        orig_run = rb.subprocess.run
        rb.subprocess.run = fake_run
        try:
            rc = rb.pay("hour", live=True)
        finally:
            rb.subprocess.run = orig_run

        self.assertEqual(rc, 0)
        self.assertEqual(len(calls), 2, "must try the runner-up after the top referrer turns out already granted")
        con = rb.db()
        rows = dict(con.execute("SELECT winner, state FROM paid").fetchall())
        self.assertEqual(rows[rb.norm("nano_1topreferrer")], "already_granted")
        self.assertEqual(rows[rb.norm("nano_1runnerupreferrer")], "confirmed")

    def test_hourly_dry_run_previews_only_the_current_top_candidate(self):
        """A dry run never calls the sender, so it has no way to learn whether the top referrer already has its
        grant - it must keep previewing just the top of the ranking rather than guessing at a fallback."""
        top_a, top_b = self._real_stranger("i1"), self._real_stranger("i2")
        runner = self._real_stranger("i3")
        self.claim("nano_1toppreview", top_a)
        self.claim("nano_1toppreview", top_b)
        self.claim("nano_1runnerpreview", runner)
        rb.info = lambda a: {"balance": str(29 * rb.XNO)} if rb.norm(a) == rb.norm(rb.TREASURY) else self.chain.i(a)
        rb._info.clear()
        orig_run = rb.subprocess.run
        rb.subprocess.run = lambda *a, **kw: (_ for _ in ()).throw(AssertionError("dry run must not call the sender"))
        try:
            rc = rb.pay("hour", live=False)
        finally:
            rb.subprocess.run = orig_run
        self.assertEqual(rc, 0)
        con = rb.db()
        self.assertEqual(con.execute("SELECT COUNT(*) FROM paid").fetchone()[0], 0, "dry run must reserve nothing")

    def test_claim_cli_refuses_without_a_block_hash(self):
        self.assertEqual(rb.claim("nano_1r", "nano_1x", ""), 1)
        self.assertEqual(rb.claim("nano_1r", "nano_1x", "not-a-hash"), 1)
        con = rb.db()
        self.assertEqual(con.execute("SELECT COUNT(*) FROM claims").fetchone()[0], 0)

    # ---- the next bug the brief asked to keep hunting for: griefing a genuine referrer -------------------
    def test_claim_squatting_a_real_referral_with_an_unproved_block_is_refused_and_does_not_occupy_the_slot(self):
        """Before this fix, rb.claim() inserted ANY syntactically-valid 64-hex block with no chain check at all -
        only score() later caught that it did not prove anything. But `claims.referred` is a PRIMARY KEY, so
        whichever claim got INSERTed FIRST permanently held that address's one-ever slot (rule 5), even if it was
        garbage. An attacker who merely knows a real agent's address - public the moment it appears in an ask -
        could submit a well-formed but unrelated 64-hex block as its own claim before the honest referrer's claim
        arrives, for free, and permanently lock the real referral out with "already claimed by someone." This
        reproduces the attack directly against rb.claim(), the real entry point (not the test's DB-seeding helper,
        which bypasses it)."""
        stranger = self._real_stranger("griefed")
        # well-formed hex, but proves nothing: not a block on the (fake) chain at all
        fake_block = "0" * 64
        self.assertEqual(rb.claim("nano_1attackerwhoneverpaidanything", stranger, fake_block), 1)
        con = rb.db()
        self.assertEqual(con.execute("SELECT COUNT(*) FROM claims").fetchone()[0], 0,
                          "an unproved claim must never occupy the referred address's slot")
        # the real referrer can still claim the same address afterwards - the slot was never taken
        real_block = self.link(stranger, "nano_1honestreferrerafterall")
        self.assertEqual(rb.claim("nano_1honestreferrerafterall", stranger, real_block), 0)
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 1)
        self.assertEqual(out["ranking"][0]["referrer"], rb.norm("nano_1honestreferrerafterall"))

    def test_claim_squatting_with_a_forged_or_misdirected_block_is_also_refused_before_insert(self):
        """Same attack, but the attacker cites a real block on chain rather than a made-up hash - one it signed
        itself, or one the stranger really sent to somebody else. Either way it is not a send from the stranger to
        the attacker, so it must be refused at claim time too, not merely at score time."""
        stranger = self._real_stranger("griefed2")
        forged = self.link("nano_1attacker4", "nano_1attacker4")
        self.assertEqual(rb.claim("nano_1attacker4", stranger, forged), 1)
        misdirected = self.link(stranger, "nano_1someoneelseentirely")
        self.assertEqual(rb.claim("nano_1attacker5", stranger, misdirected), 1)
        con = rb.db()
        self.assertEqual(con.execute("SELECT COUNT(*) FROM claims").fetchone()[0], 0)

    def test_a_genuine_claim_through_the_real_claim_function_is_recorded_and_scores(self):
        """The honest path through rb.claim() itself (not the test helper), end to end."""
        stranger = self._real_stranger("honestpath")
        block = self.link(stranger, "nano_1arealreferrer")
        self.assertEqual(rb.claim("nano_1arealreferrer", stranger, block), 0)
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 1)

    def test_daily_ceiling_is_the_owners_one_xno(self):
        self.assertEqual(rb.DAILY_CEILING_RAW, rb.XNO)

    def test_empty_period_pays_nobody(self):
        # pay() must not touch the treasury or any sender when there is nothing to pay.
        rc = rb.pay("hour", live=False)
        self.assertEqual(rc, 0)

    # ---- the daily ceiling's own clock ------------------------------------
    def test_spent_today_counts_early_utc_hours_regardless_of_server_timezone(self):
        """DAILY_CEILING_RAW is documented as a hard cap 'independent of how many winners the scorer finds' - a
        safety line that only holds if spent_today() actually sums everything paid on today's UTC calendar day.
        Before this fix it used time.mktime() on a UTC-derived day string, which mktime() reads as LOCAL time. On
        a box west of UTC (e.g. US Pacific) that pushed the window's start several hours into the current UTC day,
        so real payments made in those early hours were invisible to the ceiling check. Reproduced here by pinning
        the process to America/Los_Angeles and inserting a 'confirmed' payment 2 hours into today's UTC day -
        which the old mktime()-based cutoff placed hours in the future, excluding it."""
        if not hasattr(time, "tzset"):
            self.skipTest("time.tzset() is POSIX-only")
        orig_tz = os.environ.get("TZ")
        os.environ["TZ"] = "America/Los_Angeles"
        time.tzset()
        try:
            today_utc_start = calendar.timegm(time.strptime(time.strftime("%Y-%m-%d", time.gmtime()), "%Y-%m-%d"))
            early_utc_payment = today_utc_start + 2 * 3600  # 02:00 UTC today
            con = rb.db()
            con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                        ("2000-01-01", "nano_1someone", "day", str(rb.GRANT_RAW), "confirmed", early_utc_payment))
            con.commit()
            self.assertEqual(rb.spent_today(con), rb.GRANT_RAW,
                              "a payment 2h into today's UTC day must count toward today's spend on every TZ")
        finally:
            if orig_tz is None:
                os.environ.pop("TZ", None)
            else:
                os.environ["TZ"] = orig_tz
            time.tzset()

    def test_spent_today_survives_more_than_one_confirmed_payment(self):
        """SQLite's INTEGER affinity is a signed 64-bit value; a Nano raw amount (~1e29 for the 0.1 XNO grant) is
        ten orders of magnitude past that. `SUM(CAST(amount_raw AS INTEGER))` silently saturated to
        9223372036854775807 after just ONE confirmed payment, then raised `sqlite3.OperationalError: integer
        overflow` on a SECOND one in the same UTC day - an unhandled crash in pay()'s hot path, reachable after as
        few as two ordinary hourly payouts. Summing in Python (arbitrary-precision ints) must give the exact total
        and never raise, for any number of confirmed payments."""
        con = rb.db()
        now = time.time()
        for i in range(5):
            con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                        ("2000-01-01", f"nano_1winner{i}", "hour", str(rb.GRANT_RAW), "confirmed", now))
        con.commit()
        self.assertEqual(rb.spent_today(con), 5 * rb.GRANT_RAW)

    def test_treasury_ok_reads_the_treasury_not_an_arbitrary_ours_account(self):
        """OURS holds two different swarms' accounts - this treasury and Vend's own seller payee
        (Nano-ARION-playbook.md:265). treasury_ok() must read TREASURY by name, never `next(iter(OURS))`,
        whose order is randomised per Python process (verified: three separate `python3 -c` runs against the
        same two-element set returned the treasury address twice and the other account once). Prove it by giving
        the two accounts opposite balances and checking the answer follows the named treasury, not the set."""
        other_ours = [a for a in rb.OURS if a != rb.TREASURY][0]
        self.chain.info[rb.TREASURY] = {"balance": str(9 * rb.XNO)}      # well above the floor
        self.chain.info[other_ours] = {"balance": "0"}                  # would refuse everyone if read instead
        ok, bal = rb.treasury_ok()
        self.assertTrue(ok)
        self.assertEqual(bal, 9 * rb.XNO)

    def test_period_id_is_clock_derived_not_stored(self):
        h1 = rb.period_id("hour")
        h2 = rb.period_id("hour")
        self.assertEqual(h1, h2)  # same clock, same id - never an incrementing counter a crash could double
        self.assertRegex(h1, r"^\d{4}-\d{2}-\d{2}T\d{2}$")
        self.assertRegex(rb.period_id("day"), r"^\d{4}-\d{2}-\d{2}$")


if __name__ == "__main__":
    unittest.main()
