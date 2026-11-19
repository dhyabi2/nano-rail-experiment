#!/usr/bin/env python3
"""Law for challenge #323 (2026-11-19): /health 200 is not a reason to pay any of the five sellers today.

#322 (11:3x UTC 11-19) told strangers that nano-info fails because the sellers' own Nano node refuses connections.
But every head still sold the other 23 endpoints as working: the bounties.txt RIGHT NOW box filed them under
"WORKS, PAID" with one check, /health's HTTP code ("000 = do not pay"), and the directory, llms.txt and tools.json
said only "the sellers' box itself answers again since 2026-11-10". At 12:2x UTC all five /health still answered
200 while upstreams.rpc read "error: [Errno 111] Connection refused" on each - one node, shared by all five. A
paid call is settled by a Nano block the seller has to look up; whether it can do that with its node refused is
untested (we never send), so a stranger who passes our check and pays may buy nothing.

Each head now says all five share the refused node, that confirming a payment is untested, and to pay none of
them until the upstreams.rpc check prints ok; the free trial needs no payment. Change this law with the text
when upstreams.rpc reads ok again.

Run: python3 specs/test_sellers_payment_untested_rpc_down.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADS = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
         "published/aidirectory/index.html", "published/aidirectory.html",
         "published/bounties.txt", "published/canon.txt")
CHECK = "['upstreams']['rpc']['status']"
CHECK_HTML = "[&#x27;upstreams&#x27;][&#x27;rpc&#x27;][&#x27;status&#x27;]"


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(t):
    return " ".join(t.split())


def says_untested(t):
    return "confirm YOUR payment" in t and "untested" in t and "Pay none" in t.replace("pay none", "Pay none")


class SellersPaymentUntested(unittest.TestCase):
    def test_every_head_says_a_payment_check_is_untested(self):
        for p in HEADS:
            t = flat(read(p))
            with self.subTest(p):
                self.assertTrue(says_untested(t), p + ": does not say a payment's check is untested")
                self.assertTrue(CHECK in read(p) or CHECK_HTML in read(p), p + ": no upstreams.rpc check")

    def test_bounties_box_no_longer_files_the_sellers_under_works(self):
        t = read("published/bounties.txt")
        box = t[t.index(" RIGHT NOW - measured "):t.index(" 1. THE REWARDS")]
        self.assertNotIn("WORKS, PAID: STEP 6's paypercall.dev", box)
        self.assertIn("PAID, UNTRIED: STEP 6's paypercall.dev", box)
        self.assertTrue(says_untested(flat(box)))

    def test_step6_says_it_where_the_endpoints_are_listed(self):
        t = read("published/bounties.txt")
        step6 = t[t.index(" STEP 6 - SPEND IT"):]
        i = step6.index("The other endpoints answer again since 2026-11-10")
        self.assertIn("ALL FIVE SHARE ONE NANO NODE", step6[i:i + 300])  # #326: node ok at 15:2x 11-19, untested still
        self.assertNotIn("SHARE THAT REFUSED NODE", step6)

    def test_tools_json_step6(self):
        d = json.loads(read("published/aidirectory/tools.json"))
        found = []

        def walk(o):
            if isinstance(o, dict):
                if o.get("t") == "Spend it on something real":
                    found.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(d)
        self.assertTrue(found)
        for o in found:
            self.assertTrue(says_untested(o["right_now"]))

    def test_law_fails_on_the_old_text(self):
        old = ("The sellers' box itself answers again since 2026-11-10, after three weeks down "
               "(2026-10-17 to 11-09). Pay nothing for nano-info until this prints ok.")
        self.assertFalse(says_untested(old))


if __name__ == "__main__":
    unittest.main()
