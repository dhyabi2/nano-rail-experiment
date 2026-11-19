#!/usr/bin/env python3
"""Law for challenge #322 (2026-11-19): step 6's nano-info fails, and every head that sends a stranger there says so.

Followed as a stranger at 11:2x UTC 11-19, onboarding step 6 - `curl -s
'https://extract.paypercall.dev/api/v1/nano-info?account=nano_...'`, the one "spend it on something real" call in
/ai/llms.txt, /ai/, tools.json and bounties.txt STEP 6 - answered HTTP 400 {"error": "Nano RPC unreachable or
returned no response"} twice, for two different accounts, and each failed call still counted against the caller's
5 free trial calls (trial_remaining 2, then 1). The seller's /health answers 200 with "status": "ok" at the top, so
every check we publish (the RIGHT NOW box's `/health` loop, "000 = do not pay") passes, while its
upstreams.rpc reads "error: [Errno 111] Connection refused". Every head still said "the command above answers
again since 2026-11-10".

Each head now says the command fails, that the failed call spends a trial call, and gives the one-line check of
upstreams.rpc to run before paying. Change this law with the text when upstreams.rpc reads ok again.

Changed for challenge #326 (15:2x UTC 11-19): upstreams.rpc reads "ok" on all five sellers and an unpaid nano-info
answers 402 with its terms again, not the 400. Every head still said "FAILS TODAY" and "refuses connections", so a
stranger was told to skip the one paid call step 6 is built around. Each head now says it FAILED 11:2x-14:2x, that
the node reads ok at 15:2x, keeps the 400 text and the trial-call warning for the next outage, and keeps the check.

Run: python3 specs/test_step6_nano_info_rpc_down.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADS = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
         "published/aidirectory/index.html", "published/aidirectory.html", "published/bounties.txt")
CHECK = "['upstreams']['rpc']['status']"
CHECK_HTML = "[&#x27;upstreams&#x27;][&#x27;rpc&#x27;][&#x27;status&#x27;]"
OLD = "the command above answers again since 2026-11-10"


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(t):
    return " ".join(t.split())


class Step6NanoInfoRpcDown(unittest.TestCase):
    def test_every_head_says_it_fails_and_spends_a_trial_call(self):
        for p in HEADS:
            t = flat(read(p))
            with self.subTest(p):
                self.assertIn("FAILED 11:2x-14:2x UTC 11-19", t)
                self.assertNotIn("FAILS TODAY", t)
                self.assertNotIn("refuses connections", t)
                self.assertIn("ok at 15:2x", t)
                self.assertIn("Nano RPC unreachable or returned no response", t.replace("&quot;", '"'))
                self.assertIn("STILL USES UP one of your 5 free trial calls", t)
                self.assertNotIn(OLD, t)

    def test_every_head_gives_the_upstream_check(self):
        for p in HEADS:
            t = read(p)
            with self.subTest(p):
                self.assertTrue(CHECK in t or CHECK_HTML in t, p + ": no upstreams.rpc check")

    def test_failure_sits_right_under_the_command_in_the_aidirectory_copies(self):
        cmd = "api/v1/nano-info?account=nano_...'"
        for p in HEADS[:4]:
            t = read(p)
            i = t.index(cmd)
            with self.subTest(p):
                self.assertLess(t.index("FAILED", i) - i, 120)

    def test_bounties_box_warns_that_health_200_is_not_enough(self):
        t = flat(read("published/bounties.txt"))
        box = t[t.index("RIGHT NOW - measured"):t.index("1. THE REWARDS")]
        self.assertNotIn("NANO-INFO FAILS", box)
        self.assertIn("200 ABOVE IS NOT ENOUGH", box)
        self.assertIn("ok at 15:2x", box)

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
            self.assertIn("FAILED 11:2x-14:2x UTC 11-19", o["right_now"])
            self.assertNotIn("FAILS TODAY", o["right_now"])
            self.assertIn(CHECK, o["right_now"])
            self.assertNotIn(OLD, o["right_now"])

    def test_law_fails_on_the_old_text(self):
        old = ("RIGHT NOW: the command above answers again since 2026-11-10, after three weeks down "
               "(2026-10-17 to 11-09). Two paid calls do answer even when it is down")
        self.assertNotIn("FAILS", old)
        self.assertIn(OLD, old)

    def test_law_fails_on_the_1119_outage_text(self):
        old = "RIGHT NOW: THE COMMAND ABOVE FAILS TODAY (why, and the check, in the next paragraph)."
        self.assertNotIn("FAILED 11:2x-14:2x UTC 11-19", old)
        self.assertIn("FAILS TODAY", old)


if __name__ == "__main__":
    unittest.main()
