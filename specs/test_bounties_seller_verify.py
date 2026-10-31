#!/usr/bin/env python3
"""Laws for bounties.txt section 7's seller check, nanopaid.py (challenge #177).

Found 2026-10-29. Two x402 sellers (mapleaiagent 10-09, inkassat0r4 10-28) named the same gate to adding
nano:mainnet: a keyless verify step with no node of their own. Section 7's nanoverify.py proves a block is genuine
but not that it paid THIS seller, the right amount, confirmed, recently and only once, and the hosted facilitator
(#175, #176) waits on the owner. nanopaid.py is that check as one stdlib file a seller copies. These laws run it
exactly as published against a stub node.

Run: python3 specs/test_bounties_seller_verify.py
"""
import http.server
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import time
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
H = "B749B757EE750FC9AEA72F33CB429EACCD2ABEC9F2CCF59BF17AFAC304C9A58F"
PAYEE = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
OTHER = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
PAYER = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
RAW = "500000000000000000000000000"


def published_code():
    txt = open(BOUNTIES, encoding="utf-8").read()
    m = re.search(r"cat > nanopaid\.py <<'EOF'\n(.*?)\nEOF\n", txt, re.S)
    if not m:
        raise AssertionError("bounties.txt has no `cat > nanopaid.py <<'EOF'` block")
    return txt, m.group(1)


def block(**over):
    b = {"block_account": PAYER, "amount": RAW, "confirmed": "true", "subtype": "send",
         "local_timestamp": str(int(time.time()) - 5),
         "contents": {"type": "state", "account": PAYER, "link_as_account": PAYEE}}
    for k, v in over.items():
        if k == "link_as_account":
            b["contents"][k] = v
        else:
            b[k] = v
    return b


def stub(answer):
    """A node that answers every block_info with `answer` (a dict), or drops the connection if answer is None."""
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert body == {"action": "block_info", "json_block": "true", "hash": H}, body
            if answer is None:
                self.close_connection = True
                return
            out = json.dumps(answer).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *a):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_port


class SellerCheck(unittest.TestCase):
    def setUp(self):
        self.txt, code = published_code()
        self.dir = tempfile.mkdtemp()
        self.script = os.path.join(self.dir, "nanopaid.py")
        with open(self.script, "w") as f:
            f.write(code + "\n")
        self.used = os.path.join(self.dir, "nanopaid.used")
        self.servers = []

    def tearDown(self):
        for s in self.servers:
            s.shutdown()

    def node(self, answer):
        srv, url = stub(answer)
        self.servers.append(srv)
        return url

    def run_it(self, nodes, *args, h=H, payee=PAYEE, raw=RAW):
        env = dict(os.environ, NANO_NODES=",".join(nodes), NANOPAID_USED=self.used)
        return subprocess.run([sys.executable, self.script, h, payee, raw] + list(args),
                              capture_output=True, text=True, timeout=60, env=env)

    def refused(self, r, why):
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("NOT PAID", r.stderr)
        self.assertIn(why, r.stderr)
        self.assertNotIn("PAID " + H, r.stdout)

    def unknown(self, r, why):
        self.assertEqual(r.returncode, 5, r.stdout + r.stderr)
        self.assertIn("UNKNOWN", r.stderr)
        self.assertIn(why, r.stderr)
        self.assertIn("do NOT answer 402", r.stderr)
        self.assertNotIn("NOT PAID", r.stderr)
        self.assertNotIn("PAID " + H, r.stdout)

    def test_stdlib_only_and_no_key(self):
        _, code = published_code()
        mods = set()
        for line in code.splitlines():
            m = re.match(r"import (.+)", line)
            if m:
                mods.update(x.strip() for x in m.group(1).split(","))
            self.assertNotRegex(line, r"^\s*from \S+ import")
        self.assertEqual(mods, {"json", "os", "sys", "time", "urllib.request"})
        for word in ("seed", "private", "sign", "subprocess"):
            self.assertNotIn(word, code.lower(), word)

    def test_paid_once_then_replay_refused(self):
        url = self.node(block())
        r = self.run_it([url])
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.strip(), "PAID %s by %s - %s raw to %s" % (H, PAYER, RAW, PAYEE))
        self.already_paid(self.run_it([url]))
        self.refused(self.run_it([url], raw=str(int(RAW) + 7)), "already accepted once (replay)")

    def already_paid(self, r):
        self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
        self.assertTrue(r.stdout.startswith("ALREADY PAID %s for this same quote, %s raw" % (H, RAW)), r.stdout)
        self.assertIn("send that request's stored answer again", r.stdout)

    def test_lowercase_hash_is_the_same_payment(self):
        url = self.node(block())
        self.assertEqual(self.run_it([url], h=H.lower()).returncode, 0)
        self.already_paid(self.run_it([url]))

    # Challenge #188 (2026-10-30): prismdeadlines asked on Moltbook what happens when a buyer's send confirms but its
    # client never learns it, it retries with the same hash, and a second send of the exact quote follows. Before,
    # the same hash got "replay" and a 402 - the buyer who paid was charged again. Now each case has its own exit.
    def test_a_used_file_from_before_this_change_still_refuses_the_hash(self):
        with open(self.used, "w") as f:
            f.write(H + "\n")
        self.refused(self.run_it([self.node(block())]), "already accepted once (replay)")

    def test_a_second_block_for_a_paid_quote_is_a_duplicate_not_a_call(self):
        quote, earlier = str(int(RAW) + 4242), "A" * 64
        with open(self.used, "w") as f:
            f.write(earlier + " " + quote + "\n")
        ts = int(time.time()) - 5
        due = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts + 86400))
        url = self.node(block(amount=quote, local_timestamp=str(ts)))
        for _ in range(2):  # judged the same way every time, and never recorded as accepted
            r = self.run_it([url], raw=quote)
            self.assertEqual(r.returncode, 3, r.stdout + r.stderr)
            self.assertEqual(r.stderr.strip(), "DUPLICATE %s: quote %s raw was already paid by %s - do not serve a second "
                             "call; refund %s raw to %s by %s, 24 h after this block's time (this script sends nothing)"
                             % (H, quote, earlier, quote, PAYER, due))
            self.assertNotIn("PAID " + H, r.stdout)
        self.assertNotIn(H, open(self.used).read())

    def test_a_fixed_price_is_never_called_a_duplicate(self):
        with open(self.used, "w") as f:
            f.write("A" * 64 + " " + RAW + "\n")
        self.assertEqual(self.run_it([self.node(block())]).returncode, 0)

    def test_text_answers_the_ambiguous_case_without_running_anything(self):
        i = self.txt.index("PAID, BUT THE BUYER NEVER GOT THE ANSWER - THE AMBIGUOUS CASE, AS TEXT.")
        sec = self.txt[i:self.txt.index("WHOSE WORD IS", i)]
        for s in ("BEFORE it is signed and published", "call again with the same hash", "exit 2", "exit 1, replay",
                  "exit 3, DUPLICATE", "Never answer 402 to a hash you accepted", "sends nothing itself"):
            self.assertIn(s, " ".join(sec.split()), s)
        self.assertNotRegex(sec, r"\n\s+(python3|curl|cat|node|pip) ")
        for n in ("Exit 2 prints ALREADY PAID", "Exit 3 prints DUPLICATE"):
            self.assertIn(n, self.txt)

    def test_xrb_prefix_is_the_same_payee(self):
        url = self.node(block(link_as_account="xrb_" + PAYEE[5:]))
        self.assertEqual(self.run_it([url]).returncode, 0)

    def test_wrong_payee(self):
        self.refused(self.run_it([self.node(block(link_as_account=OTHER))]), "paid %s, not you" % OTHER)

    def test_wrong_amount_either_way(self):
        url = self.node(block())
        self.refused(self.run_it([url], raw=str(int(RAW) + 1)), "amount %s raw, price" % RAW)
        self.refused(self.run_it([url], raw=str(int(RAW) - 1)), "amount %s raw, price" % RAW)

    # Challenge #189 (2026-10-31): prismdeadlines (Moltbook, 10-30 20:19) - between a confirmed transfer and a delivered
    # call a buyer needs a distinguishable pending state, not an error that looks like non-payment. An unconfirmed send
    # used to be NOT PAID, exit 1, "answer 402 again": the buyer who had paid was told it had not.
    def pending(self, r, raw=RAW):
        self.assertEqual(r.returncode, 4, r.stdout + r.stderr)
        self.assertEqual(r.stdout.strip(), "PENDING %s: pays you %s raw but is not confirmed yet - serve nothing yet, ask "
                         "for no new payment; tell the buyer to retry with this same hash in a few seconds" % (H, raw))
        self.assertNotIn("NOT PAID", r.stderr)

    def test_unconfirmed_is_pending_not_unpaid_and_records_nothing(self):
        self.pending(self.run_it([self.node(block(confirmed="false"))]))
        self.assertFalse(os.path.exists(self.used))
        r = self.run_it([self.node(block())])  # the same hash, once confirmed
        self.assertEqual(r.returncode, 0, r.stderr)
        self.already_paid(self.run_it([self.node(block())]))

    def test_one_listed_node_not_confirmed_yet_is_pending(self):
        good, slow = self.node(block()), self.node(block(confirmed="false"))
        for order in ([good, slow], [slow, good]):
            self.pending(self.run_it(order))
        self.assertFalse(os.path.exists(self.used))

    def test_unconfirmed_still_refused_for_the_wrong_payee_amount_or_age(self):
        self.refused(self.run_it([self.node(block(confirmed="false", link_as_account=OTHER))]), "not you")
        self.refused(self.run_it([self.node(block(confirmed="false"))], raw=str(int(RAW) + 1)), "amount")
        self.refused(self.run_it([self.node(block(confirmed="false", local_timestamp="0"))]), "older than")

    def test_text_says_pending_is_not_a_402_and_the_refund_has_a_deadline(self):
        flat = " ".join(self.txt.split())
        for s in ("Exit 4 prints PENDING", "do NOT answer 402", "Sent, not confirmed yet: exit 4, PENDING",
                  "24 h after the duplicate block's own time", "a refund sent after the deadline still settles the duplicate",
                  "Never treat overdue as final", "by the time it prints"):
            self.assertIn(s, flat, s)
        self.assertNotIn("not confirmed yet - ask again in a few seconds", self.txt)

    def test_not_a_send(self):
        self.refused(self.run_it([self.node(block(subtype="receive"))]), "not a send")

    def test_too_old_and_unknown_age(self):
        old = block(local_timestamp=str(int(time.time()) - 700))
        self.refused(self.run_it([self.node(old)]), "older than 600 s")
        self.refused(self.run_it([self.node(block(local_timestamp="0"))]), "older than")
        self.assertEqual(self.run_it([self.node(old)], "3600").returncode, 0)

    def test_not_found(self):
        self.refused(self.run_it([self.node({"error": "Block not found"})]), "Block not found")

    # Challenge #193 (2026-10-31): a node that did not answer printed NOT PAID, exit 1 ("answer 402 again"), so a
    # rate-limited or dead default node told every buyer who had paid to pay twice. It is UNKNOWN, exit 5.
    def test_no_node_answered_is_unknown_not_unpaid(self):
        self.unknown(self.run_it([self.node(None), "http://127.0.0.1:9"]), "did not answer")
        self.assertFalse(os.path.exists(self.used))

    def test_every_listed_node_must_answer_and_agree(self):
        good = self.node(block())
        self.refused(self.run_it([good, self.node(block(link_as_account=OTHER))]), "not you")
        self.refused(self.run_it([good, self.node(block(block_account=OTHER))]), "nodes disagree on the payer")
        self.assertEqual(self.run_it([good, self.node(block())]).returncode, 0)

    # Challenge #180 (2026-10-29): a listed node that did not answer was skipped, so a seller who listed two nodes to
    # avoid trusting one was silently back on one whenever the second was down or blocked. Every listed node must answer.
    def test_a_silent_second_node_is_not_paid_and_writes_nothing(self):
        good = self.node(block())
        for silent in (self.node(None), "http://127.0.0.1:9"):
            for order in ([good, silent], [silent, good]):
                self.unknown(self.run_it(order), "node %s did not answer" % silent)
        self.assertFalse(os.path.exists(self.used))
        self.assertEqual(self.run_it([good]).returncode, 0)

    def test_rate_limited_or_erroring_node_is_unknown_and_writes_nothing(self):
        good = self.node(block())
        limit = self.node({"error": "api_key_required_for_heavy_usage", "message": "Free public RPC limit reached"})
        for order in ([limit], [good, limit], [limit, good]):
            self.unknown(self.run_it(order), "api_key_required_for_heavy_usage")
        self.unknown(self.run_it([self.node(["not", "a", "block"])]), "sent no block_info reply")
        self.assertFalse(os.path.exists(self.used))
        self.assertEqual(self.run_it([good]).returncode, 0)

    def test_http_429_is_unknown(self):
        class H429(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers["Content-Length"]))
                out = b'{"error":"Free public RPC limit reached"}'
                self.send_response(429)
                self.send_header("Content-Length", str(len(out)))
                self.end_headers()
                self.wfile.write(out)

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H429)
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        self.servers.append(srv)
        self.unknown(self.run_it(["http://127.0.0.1:%d" % srv.server_port]), "did not answer")

    def test_text_says_a_down_node_is_unknown_not_a_402(self):
        for s in ("Exit 5 prints UNKNOWN", "never with a 402", "means UNKNOWN, exit 5",
                  "A NODE THAT IS DOWN IS NOT A PAYMENT THAT FAILED", "We still name no second node: we have measured none"):
            self.assertIn(s, self.txt)
        self.assertNotIn("one that is down or blocked means NOT PAID", self.txt)

    def test_text_says_whose_word_confirmed_is(self):
        self.assertIn("every node you list must answer", self.txt)
        self.assertNotIn("every node that answers must agree", self.txt)
        self.assertIn('WHOSE WORD IS "confirmed"? With the default, rpc.nano.to\'s alone', self.txt)
        self.assertIn("two witnesses, not a proof", self.txt)

    def test_bad_hash(self):
        self.refused(self.run_it(["http://127.0.0.1:9"], h="B749"), "not a 64-hex block hash")

    def test_text_shows_a_runnable_example_and_the_replay(self):
        self.assertIn("python3 nanopaid.py " + H, self.txt)
        self.assertIn(PAYEE + " " + RAW + " 999999999", self.txt)
        self.assertIn("already accepted once (replay)", self.txt)


    # Challenge #178 (2026-10-29): with one fixed price, anyone reading the seller's public account history can hand
    # over a buyer's fresh block first and be served; the buyer then gets "replay". Section 7 must tell the seller to
    # quote a new amount per 402, and give the line that does it.
    def quote_line(self):
        m = re.search(r'^   (python3 -c "import secrets,sys;print\(int\(sys\.argv\[1\]\)\+1\+secrets\.randbelow\(10\*\*6\)\)") <price in raw>$',
                      self.txt, re.M)
        self.assertIsNotNone(m, "section 7 must give the per-402 quote line")
        return m.group(1)

    def test_text_warns_that_one_fixed_price_lets_a_watcher_take_the_block(self):
        self.assertIn("QUOTE A NEW AMOUNT IN EVERY 402, NOT ONE PRICE FOR EVERYONE", self.txt)
        self.assertIn("<that request's quoted raw>", self.txt)
        self.assertNotIn("nano_<your address> <price in raw> [max age s]", self.txt)

    def test_quote_line_gives_a_fresh_amount_just_above_the_price(self):
        line = self.quote_line()
        code = re.match(r'python3 -c "(.*)"$', line).group(1)
        quotes = set()
        for _ in range(8):
            r = subprocess.run([sys.executable, "-c", code, RAW], capture_output=True, text=True, timeout=30)
            self.assertEqual(r.returncode, 0, r.stderr)
            q = int(r.stdout.strip())
            self.assertGreater(q, int(RAW))
            self.assertLessEqual(q, int(RAW) + 10 ** 6)
            quotes.add(q)
        self.assertGreater(len(quotes), 1, "eight quotes were all the same amount")

    def test_a_block_paid_for_one_quote_does_not_buy_another_request(self):
        quote_a, quote_b = str(int(RAW) + 417), str(int(RAW) + 90211)
        url = self.node(block(amount=quote_a))
        self.refused(self.run_it([url], raw=quote_b), "amount %s raw, price %s raw" % (quote_a, quote_b))
        self.refused(self.run_it([url], raw=RAW), "amount %s raw" % quote_a)
        self.assertEqual(self.run_it([url], raw=quote_a).returncode, 0)

if __name__ == "__main__":
    unittest.main()
