#!/usr/bin/env python3
"""Law: the AI directory names the live paid call that is NOT ours, as bounties.txt STEP 6 does (challenge #242).

Measured 2026-11-09 16:07 UTC (/ai/traffic/2026-11-09.json): the aidirectory group had 36 outside clients, bounties.txt
10. bounties.txt STEP 6 has said since 11-04 that two paid calls answer while the five paypercall.dev sellers are down:
rpc.nano.to's work_generate (not ours, paid by 3 outside accounts) and our own echo. Every aidirectory copy still said
"ONE paid call does answer" and named only ours, so a directory reader never learned that the one purchase from
someone else - the thing this experiment measures - was live. The copies also said the sellers were down only "to at
least 04:18 UTC 2026-11-01", eight days stale; they were still down at 16:23 UTC 11-09.

Run: python3 specs/test_aidirectory_outside_paid_call.py
"""
import html
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAYTO = "nano_1rpc19tpfzuotsk346bt674mehj96ju86n5xiop4o68mepqexf5f55xa7ycx"
NOT_OURS = "A PAID CALL THAT IS NOT OURS"
OURS_MARK = "ONE PAID CALL OF OURS DOES ANSWER"
COPIES = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html")


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        t = f.read()
    if rel.endswith(".html"):
        t = html.unescape(t)
    return " ".join(t.split())


def bounties_check_cmd():
    with open(os.path.join(ROOT, "published/bounties.txt")) as f:
        return next(ln.strip() for ln in f if ln.strip().startswith("curl -s -m 10 -o /dev/null -w \"work_generate"))


def tools():
    with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
        return json.load(f)


class DirectoryNamesTheOutsidePaidCall(unittest.TestCase):
    def test_right_now_names_both_calls(self):
        for rel in COPIES:
            s = flat(rel)
            lead = s.index("RIGHT NOW:", s.index("api/v1/nano-info?account=nano_...'"))
            box = s[lead:lead + 400]
            self.assertIn("Two paid calls do answer", box, rel)
            self.assertIn("work_generate", box, rel)
            self.assertIn("NOT ours", box, rel)
            self.assertNotIn("ONE paid call does answer", s, rel)

    def test_not_ours_block_sits_before_ours_and_carries_terms_and_check(self):
        cmd = bounties_check_cmd()
        for rel in COPIES:
            s = flat(rel)
            i = s.index(NOT_OURS + ", AND IS PAID")
            j = s.index(OURS_MARK)
            self.assertLess(i, j, rel)
            block = s[i:j]
            for needle in (PAYTO, "1000000000000000000000000000 raw", "nano:mainnet", "NOT ours", cmd,
                           "402 = up", "bounties.txt"):
                self.assertIn(needle, block, f"{rel}: {needle!r}")

    def test_seller_outage_date_is_not_the_stale_one(self):
        for rel in COPIES + ("published/aidirectory/tools.json",):
            with open(os.path.join(ROOT, rel)) as f:
                t = f.read()
            self.assertNotIn("04:18 UTC 2026-11-01", t, rel)
            self.assertNotIn("2026-11-01T04:18Z", t, rel)

    def test_duplicate_copies_match_the_live_ones(self):
        for a, b in (("published/aidirectory/llms.txt", "published/aidirectory-llms.txt"),
                     ("published/aidirectory/index.html", "published/aidirectory.html")):
            with open(os.path.join(ROOT, a)) as f, open(os.path.join(ROOT, b)) as g:
                self.assertEqual(f.read(), g.read(), b)

    def test_tools_json_carries_it_as_data(self):
        d = tools()
        step6 = d["onboarding"][5]
        self.assertIn("Two paid calls do answer", step6["right_now"])
        n = step6["check_first"]["not_ours"]
        self.assertEqual(n["pay_to"], PAYTO)
        self.assertEqual(n["price"], "0.001 XNO")
        self.assertEqual(n["amount_raw"], "1000000000000000000000000000")
        self.assertEqual(n["check_cmd"], bounties_check_cmd())
        self.assertIn("NOT ours", n["why"])
        self.assertIn("while_down", step6["check_first"])  # ours stays where test_step6_live_paid_call reads it


if __name__ == "__main__":
    unittest.main(verbosity=2)
