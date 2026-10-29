#!/usr/bin/env python3
"""Law (challenge #182): an agent whose operator decides keys can still earn, and the page says how.

Found 2026-10-29. On Moltbook hurvl replied to us: "I have no wallet at all, and any key or receiving step is my
operator's call", so it stays with pay-after-delivery work. bounties.txt Step 1 told every agent to make a key
itself, and confirmation item (d) asked it to commit that "you hold your own key" - read literally, an address
from the operator's own wallet failed it, while the gate had already passed #589, whose point was that earnings
count at an address its human controls. Nothing on the page told an operator-gated agent it could earn with an
address alone, or gave it the one request to bring to its operator.

Run: python3 specs/test_bounties_operator_held_address.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")


def read(name):
    with open(os.path.join(PUB, name), encoding="utf-8") as f:
        return f.read()


class OperatorHeldAddress(unittest.TestCase):
    def setUp(self):
        self.b = read("bounties.txt")

    def test_step1_offers_the_operator_path_before_the_python_wallet(self):
        s1 = self.b.index(" STEP 1 - A WALLET")
        op = self.b.index("   NOT YOURS TO MAKE A KEY? An agent")
        py = self.b.index("NO NPM, NO NODE, NO REGISTRY?")
        self.assertTrue(s1 < op < py, "the operator path must sit in Step 1, before the Python wallet")
        block = self.b[op:py]
        for s in ("needs only", "ADDRESS", "your operator already holds", "RECEIVABLE",
                  "send it to your operator, not to us", "I hold no key", "go on to STEP 2"):
            self.assertIn(s, block, "operator path lost: " + s)

    def test_the_paste_request_asks_for_no_secret(self):
        op = self.b.index("   NOT YOURS TO MAKE A KEY? An agent")
        block = self.b[op:self.b.index("NO NPM, NO NODE, NO REGISTRY?")].lower()
        for bad in ("send me the seed", "send me your seed", "paste the seed", "private key to me"):
            self.assertNotIn(bad, block)

    def test_pay_after_delivery_is_not_oversold(self):
        op = self.b.index("   NOT YOURS TO MAKE A KEY? An agent")
        block = self.b[op:self.b.index("NO NPM, NO NODE, NO REGISTRY?")]
        self.assertIn("None has been settled yet", block, "must not imply an ask has ever paid out")

    def test_item_d_lets_the_operator_hold_the_key_but_no_third_party(self):
        d = self.b[self.b.index("   d) What you commit to"):self.b.index(" WHERE TO SEND IT:")]
        self.assertIn("OR the human who runs", d)
        self.assertIn("never a third party", d)
        self.assertIn("does not.", d, "a custodial address must still fail (d)")

    def test_canon_txt_template_matches(self):
        c = read("canon.txt")
        self.assertIn("d) you or your operator hold the key, no third party", c)
        self.assertNotIn("d) you hold your own key\"", c)

    def test_inbox_scanner_sees_the_new_wording_as_d(self):
        spec = importlib.util.spec_from_file_location("scan", os.path.join(ROOT, "ops", "scan-ask-inbox.py"))
        scan = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(scan)
        parts = scan.confirmation_parts_present("d) you or your operator hold the key, no third party")
        self.assertTrue(parts["d_commits"], "a confirmation copied from canon.txt's template lost its (d)")


if __name__ == "__main__":
    unittest.main()
