#!/usr/bin/env python3
"""Law: step 2 ("check an address") never hands an empty wallet a paid call as its command (challenge #250).

Measured 2026-11-11 00:2x UTC: every guide's step 2 gave the curl
`https://extract.paypercall.dev/api/v1/address-verdict?account=nano_...` as the way to learn whether an account has
ever transacted. That call answers HTTP 402 ("Pay 0.0001 XNO to nano_3z335ug5oz...") with no payment, and step 2 comes
right after step 1 made a wallet holding nothing - so the one command a newcomer runs to check an address fails. The
same fact is free from a node: rpc.nano.to account_info answers 200 with "Account not found" for a never-opened
account (measured on five treasury2 starter payees, 00:2x 11-11).

This law: no published copy offers the address-verdict curl as a runnable command, and every copy's step 2 names the
free account_info read and says "Account not found" is not a reason to stop. Listing address-verdict as a priced
tool in a catalogue is fine; it is priced there.

Run: python3 specs/test_address_check_is_free.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEXTS = ["published/bounties.txt", "published/swap.txt", "published/aidirectory/llms.txt",
         "published/aidirectory-llms.txt", "published/aidirectory/index.html", "published/aidirectory.html"]
PAID_CURL = "curl -s 'https://extract.paypercall.dev/api/v1/address-verdict"
FREE_READ = """--data-binary '{"action":"account_info","account":"nano_..."}'"""


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().replace("&quot;", '"').replace("&#x27;", "'").split())


class AddressCheckIsFree(unittest.TestCase):
    def test_no_copy_runs_the_paid_verdict(self):
        for rel in TEXTS:
            self.assertNotIn(PAID_CURL, flat(rel), rel)

    def test_every_copy_gives_the_free_read(self):
        for rel in TEXTS:
            s = flat(rel)
            self.assertIn(FREE_READ, s, rel)
            i = s.index(FREE_READ)
            near = s[i:i + 400]
            self.assertIn("Account not found", near, rel)
            self.assertIn("not a reason to stop", near, rel)

    def test_paid_price_is_said(self):
        for rel in TEXTS:
            s = flat(rel)
            self.assertIn("0.0001 XNO", s, rel)
            self.assertIn("402", s, rel)

    def test_tools_json_step2(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            d = json.load(f)
        step2 = [x for x in d["onboarding"] if x["n"] == "2"][0]
        self.assertNotIn(PAID_CURL, step2["note"])
        self.assertIn('"action":"account_info"', step2["note"])
        self.assertIn("not a reason to stop", step2["note"])


if __name__ == "__main__":
    unittest.main()
