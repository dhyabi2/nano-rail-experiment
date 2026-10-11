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
        rb._hist_failed.clear()
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

    def test_referrer_funding_hidden_behind_25_dust_sends_is_still_found(self):
        """Challenge #80. funders() used to read only the newest 25 history entries of every account it walked, and
        history entries include SENDS. So a referrer could fund an intermediate X, have X publish 25 feeless dust
        sends, then fund the referred agent from X: the walk read X's 25 sends, saw no receive, treated X as a
        leaf, and scored a referral the referrer paid for itself as "funded by a third party". No exchange
        round-trip, only 27 blocks of PoW - the one cost the spec's whole security argument rests on, skipped.
        A non-service account's history must be read whole."""
        referrer, x, referred = "nano_1sybilreferrer", "nano_1sybilmiddleman", "nano_1sybilreferred"
        now = int(time.time())
        x_hist = [{"type": "send", "account": "nano_1dustsink", "local_timestamp": str(now - 100 - i), "amount": "1"}
                  for i in range(26)]
        x_hist.append({"type": "receive", "account": referrer, "local_timestamp": str(now - 5000),
                       "amount": str(XNO_HALF)})
        self.chain.history[x] = x_hist
        self.chain.info[x] = {"block_count": str(len(x_hist))}
        self.agent(referred, funded_by=x)
        self.claim(referrer, referred)
        truncating = self.chain.h
        rb.history = lambda acct, count=50: truncating(acct)[:int(count)]  # the node honours `count`, as rpc.nano.to does
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0, out["detail"])
        self.assertIn("funded by the referrer itself", out["detail"][0]["why"])

    def test_a_funder_whose_history_cannot_be_read_is_not_a_clean_third_party(self):
        """Challenge #80, the fail-open half: an account in the funding walk whose history the node would not return
        used to look exactly like an account nobody ever funded - a leaf, so a clean "third party". A check that
        cannot run must never report a clean result."""
        x = "nano_1unreadablemiddleman"
        self.chain.info[x] = {}          # account_info failed: no block count
        self.agent("nano_1referredU", funded_by=x)
        self.claim("nano_1referrerU", "nano_1referredU")
        out = rb.score("hour", verbose=False)
        self.assertEqual(out["qualifying"], 0)
        self.assertIn("could not be read", out["detail"][0]["why"])

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

    def test_a_day_run_stops_at_the_treasury_floor_not_one_grant_short_of_it(self):
        """FLOOR_RAW's own comment is "bounties stop before the treasury does", and treasury_ok() asks
        whether ONE grant still leaves it standing. `pay --period day` pays the WHOLE ranking (score()'s
        funders_used comment says so), and nothing asked again from the second winner on.

        The treasury here holds 9 XNO: exactly one grant of room above the 8.9 XNO floor. Three
        qualifying referrers took 0.3 XNO and left it at 8.7 - under the floor - and the daily ceiling
        cannot catch it, because the ceiling bounds ten grants while the floor has room for one."""
        for name, referrer in (("f1", "nano_1floorone"), ("f2", "nano_1floortwo"),
                               ("f3", "nano_1floorthree")):
            self.claim(referrer, self._real_stranger(name))
        self.assertEqual(rb.score("day", verbose=False)["qualifying"], 3)

        bal = 9 * rb.XNO
        rb.info = lambda a: {"balance": str(bal)} if rb.norm(a) == rb.norm(rb.TREASURY) else self.chain.i(a)
        rb._info.clear()
        calls = []
        class R:
            returncode, stdout, stderr = 0, '{"block": "' + "B" * 64 + '"}', ""
        orig_run = rb.subprocess.run
        rb.subprocess.run = lambda *a, **kw: (calls.append(a[0]), R())[1]
        try:
            rb.pay("day", live=True)
        finally:
            rb.subprocess.run = orig_run

        con = rb.db()
        granted = sum(int(r[0]) for r in con.execute(
            "SELECT amount_raw FROM paid WHERE state <> 'already_granted'").fetchall())
        self.assertEqual(len(calls), 1, "the second winner must not be sent to at all")
        self.assertEqual(granted, rb.GRANT_RAW)
        self.assertGreaterEqual(bal - granted, rb.FLOOR_RAW,
                                "a day run must not take the treasury below the floor")

    def test_a_dry_day_run_promises_only_what_the_floor_allows(self):
        """A dry run that prints three "would send" lines where a live run sends once is a dry run that
        lies. The floor is consumed by the reservation, so both modes stop in the same place."""
        for name, referrer in (("g1", "nano_1dryone"), ("g2", "nano_1drytwo")):
            self.claim(referrer, self._real_stranger(name))
        self.chain.info[rb.TREASURY] = {"balance": str(9 * rb.XNO)}
        rb._info.clear()
        import contextlib
        import io
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rb.pay("day", live=False)
        out = buf.getvalue()
        self.assertEqual(out.count("DRY RUN would send"), 1)
        self.assertIn("below the", out)
        con = rb.db()
        self.assertEqual(con.execute("SELECT COUNT(*) FROM paid").fetchone()[0], 0,
                         "a dry run leaves no reservation behind")

    def test_claim_cli_refuses_without_a_block_hash(self):
        self.assertEqual(rb.claim("nano_1r", "nano_1x", ""), 1)
        self.assertEqual(rb.claim("nano_1r", "nano_1x", "not-a-hash"), 1)
        con = rb.db()
        self.assertEqual(con.execute("SELECT COUNT(*) FROM claims").fetchone()[0], 0)

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

    def test_the_ceiling_counts_a_payout_whose_reply_was_lost(self):
        """DAILY_CEILING_RAW is frozen in referral_bounty.py so that "a bug cannot drain the treasury", and pay()
        writes state='unknown' when the sender's reply is lost - with its own comment saying why: "the money may
        have moved." spent_today() counted state='confirmed' only, so every one of those payouts was invisible to
        the ceiling. Measured before the fix: ten lost replies name 1.0 XNO of grants that may have left and
        spent_today() reported 0, leaving pay() room for ten more."""
        con = rb.db()
        now = time.time()
        for i in range(10):
            con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                        ("2026-01-01T%02d" % i, f"nano_1lost{i}", "hour", str(rb.GRANT_RAW), "unknown", now))
        con.commit()
        self.assertEqual(rb.spent_today(con), 10 * rb.GRANT_RAW,
                         "a payout whose outcome is unknown must count against the ceiling")
        self.assertGreater(rb.spent_today(con) + rb.GRANT_RAW, rb.DAILY_CEILING_RAW,
                           "ten unknown grants must be enough to close the ceiling")

    def test_the_ceiling_counts_a_reservation_whose_process_died(self):
        """pay() INSERTs the row as 'reserved' BEFORE it calls the sender - that ordering is the idempotency. A
        process that dies between the INSERT and the UPDATE leaves the row 'reserved' for good, and the money may
        already have moved, so it counts too."""
        con = rb.db()
        con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                    ("2026-01-01T00", "nano_1crashed", "hour", str(rb.GRANT_RAW), "reserved", time.time()))
        con.commit()
        self.assertEqual(rb.spent_today(con), rb.GRANT_RAW)

    def test_an_unrecognised_state_counts_rather_than_being_ignored(self):
        """The filter is "everything except already_granted", not a list of states that count, so a state added to
        this file later is counted by default. For a ceiling the fail-closed default is to count."""
        con = rb.db()
        con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                    ("2026-01-01T00", "nano_1future", "hour", str(rb.GRANT_RAW), "some_future_state", time.time()))
        con.commit()
        self.assertEqual(rb.spent_today(con), rb.GRANT_RAW)

    def test_a_grant_the_sender_refused_does_not_count(self):
        """'already_granted' is the one state where the sender said in as many words that it sent nothing - its
        grants ledger refuses a second grant to the same account, ever. Counting it would starve real winners of
        the ceiling's room for no reason."""
        con = rb.db()
        con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                    ("2026-01-01T00", "nano_1hadone", "hour", str(rb.GRANT_RAW), "already_granted", time.time()))
        con.commit()
        self.assertEqual(rb.spent_today(con), 0)

    def test_yesterdays_unknown_payout_does_not_count_against_today(self):
        """The control on the window: widening WHICH states count must not widen WHEN they count."""
        con = rb.db()
        today_start = calendar.timegm(time.strptime(time.strftime("%Y-%m-%d", time.gmtime()), "%Y-%m-%d"))
        con.execute("INSERT INTO paid(period,winner,kind,amount_raw,state,at) VALUES(?,?,?,?,?,?)",
                    ("2026-01-01T00", "nano_1yesterday", "hour", str(rb.GRANT_RAW), "unknown", today_start - 60))
        con.commit()
        self.assertEqual(rb.spent_today(con), 0)

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
