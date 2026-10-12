#!/usr/bin/env python3
"""Laws for the XNO accepts entry we show a seller (challenge #119).

Two outside x402 sellers (mapleaiagent 2026-10-09, spendrails 2026-10-10) are weighing an XNO entry beside USDC.
spendrails asked whether a client library throws on an unknown entry. Measured 2026-10-10: the official Python
client (pip x402 2.25.0) validates the whole 402 with a schema that REQUIRES maxTimeoutSeconds on every entry, so an
XNO entry shaped like our own manifest's (scheme, network, asset, amount, payTo) makes it reject the 402 outright,
USDC entry included. With maxTimeoutSeconds and extra the 402 parses and an EVM-only client skips the XNO entry.
So every XNO entry we show a seller as JSON must carry both fields, and Step 7 ("Get PAID in it") must show one.

Run: python3 specs/test_xno_entry_shape.py
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LLMS = [("published", "aidirectory", "llms.txt"), ("published", "aidirectory-llms.txt")]
SHOWN_TO_SELLERS = LLMS + [
    ("drafts", "reply-mapleaiagent-xno-verifier-2026-10-09.md"),
    ("drafts", "reply-spendrails-unknown-entry-2026-10-10.md"),
]
ENTRY = re.compile(r'\{"scheme":"exact","network":"nano:mainnet"[^{}]*(?:\{\})?[^{}]*\}')


def read(*p):
    with open(os.path.join(ROOT, *p)) as f:
        return f.read()


def step7(text):
    i = text.index("### Step 7. Get PAID in it")
    j = text.find("\n<!--", i)
    return text[i:j if j != -1 else len(text)]


def is_seller_ready(entry):
    """True when an entry carries every field the x402 v2 PaymentRequirements schema requires."""
    return {"scheme", "network", "asset", "amount", "payTo", "maxTimeoutSeconds"} <= set(entry) and \
        isinstance(entry["maxTimeoutSeconds"], int) and entry["maxTimeoutSeconds"] > 0


class XnoEntryShape(unittest.TestCase):
    def test_step7_shows_a_complete_entry_beside_usdc(self):
        for p in LLMS:
            s = step7(read(*p))
            found = [json.loads(m) for m in ENTRY.findall(s)]
            self.assertTrue(found, f"{'/'.join(p)} Step 7 shows no XNO accepts entry")
            for e in found:
                self.assertTrue(is_seller_ready(e), f"{'/'.join(p)}: {e}")
                self.assertEqual(e.get("extra"), {})
            flat = re.sub(r"\s+", " ", s)
            self.assertIn("BESIDE USDC", flat)
            self.assertIn("maxTimeoutSeconds Field required", flat)

    def test_every_json_entry_shown_to_a_seller_is_complete(self):
        for p in SHOWN_TO_SELLERS:
            text = read(*p)
            for m in ENTRY.findall(text):
                e = json.loads(m)
                if e.get("payTo") == "nano_...":
                    continue  # quoting our own manifest's shape; the next lines must add the fields
                self.assertTrue(is_seller_ready(e), f"{'/'.join(p)}: {m}")

    def test_quoting_our_manifest_says_what_to_add(self):
        t = re.sub(r"\s+", " ", read("drafts", "reply-mapleaiagent-xno-verifier-2026-10-09.md"))
        self.assertIn('"maxTimeoutSeconds":300,"extra":{}', t)

    def test_the_two_llms_copies_agree(self):
        self.assertEqual(step7(read(*LLMS[0])), step7(read(*LLMS[1])))

    def test_incomplete_shape_is_caught(self):
        self.assertFalse(is_seller_ready({"scheme": "exact", "network": "nano:mainnet", "asset": "XNO",
                                          "amount": "1", "payTo": "nano_x"}))


if __name__ == "__main__":
    unittest.main()
