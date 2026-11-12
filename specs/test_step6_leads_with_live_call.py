#!/usr/bin/env python3
"""Law: STEP 6 says which paid call answers BEFORE it lists the 24 sellers that do not (challenge #197).

Measured 2026-11-01 08:17 UTC: all five paypercall.dev sellers still answer nothing (down since about 10:25 UTC
10-17), yet STEP 6 in bounties.txt opened with "24 endpoints, 0.0001-0.0005 XNO a call, no signup", and the
aidirectory copies put the dead extract call as step 6's only command. The one paid call that answers
(getunstuck.space's x402 route, 0.001 XNO) came 15+ lines later. A skimming agent stops at the first command.

Run: python3 specs/test_step6_leads_with_live_call.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = "ONE PAID CALL OF OURS DOES ANSWER"
POINTER = "ONE PAID CALL OF OURS"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().split())


class Step6LeadsWithLiveCall(unittest.TestCase):
    def test_bounties_says_right_now_before_the_seller_list(self):
        s = read("published/bounties.txt")
        i = s.index(" STEP 6 - ")
        lead = s.index("RIGHT NOW:", i)
        self.assertLess(lead, s.index("24 endpoints", i))
        self.assertLess(lead, s.index("paypercall.dev", i))
        self.assertIn(POINTER, s[lead:lead + 300])
        self.assertNotIn(MARK, s[lead:lead + 300])  # the pointer must not steal the heading test_step6_live_paid_call anchors on
        self.assertIn(MARK, s[lead + 300:])  # the pointer names a block that exists further down

    def test_aidirectory_copies_say_right_now_next_to_the_dead_command(self):
        for rel in ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
                    "published/aidirectory/index.html", "published/aidirectory.html"):
            s = read(rel)
            cmd = s.index("api/v1/nano-info?account=nano_...'")
            lead = s.index("RIGHT NOW:", cmd)
            self.assertLess(lead - cmd, 80, rel + ": RIGHT NOW must sit right under the dead command")
            self.assertIn(MARK, s[lead + 200:], rel)

    def test_tools_json_step6_carries_right_now(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            doc = json.load(f)
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
        walk(doc)
        self.assertTrue(found)
        for o in found:
            self.assertIn(POINTER, o.get("right_now", ""))


if __name__ == "__main__":
    unittest.main()
