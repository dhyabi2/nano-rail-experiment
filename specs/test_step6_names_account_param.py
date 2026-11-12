#!/usr/bin/env python3
"""Law for challenge #261: the AI directory's paid step 6 command carries the parameter the seller requires.

nano-info answers a paid call that lacks ?account= with HTTP 400 "account parameter is required"
(payment_taken false), measured 20:2x UTC 2026-11-12. The unpaid bare URL still answers 402, so a
stranger who copied the directory's command "as it is" saw the right terms, paid, retried exactly as
told, and got a 400. bounties.txt always named ?account=nano_...; the five directory copies did not.

Run: python3 specs/test_step6_names_account_param.py
"""
import html
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
TEXT_COPIES = ["aidirectory/llms.txt", "aidirectory-llms.txt", "aidirectory/index.html", "aidirectory.html"]
NEEDLE = "api/v1/nano-info?account=nano_..."


def read(rel):
    with open(os.path.join(PUB, rel)) as f:
        return html.unescape(f.read())


class Step6NamesAccountParam(unittest.TestCase):
    def test_no_bare_nano_info_command_in_any_text_copy(self):
        for rel in TEXT_COPIES:
            s = read(rel)
            self.assertEqual(re.findall(r"api/v1/nano-info'", s), [], rel)
            self.assertGreaterEqual(s.count(NEEDLE + "'"), 2, rel)  # the unpaid call and the paid retry

    def test_tools_json_commands_carry_account(self):
        with open(os.path.join(PUB, "aidirectory", "tools.json")) as f:
            step = json.load(f)["onboarding"][5]
        self.assertIn(NEEDLE, step["cmd"])
        self.assertIn(NEEDLE, step["how_to_pay"]["cmd"])
        self.assertIn("account parameter is required", step["how_to_pay"]["then"])

    def test_every_copy_explains_the_400(self):
        for rel in TEXT_COPIES:
            flat = " ".join(read(rel).split())
            self.assertIn("account parameter is required", flat, rel)
            self.assertIn("payment_taken false", flat, rel)

    def test_bounties_still_names_account(self):
        self.assertIn(NEEDLE, read("bounties.txt"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
