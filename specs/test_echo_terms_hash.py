#!/usr/bin/env python3
"""Challenge #294: the echo route's terms carry no version, so the guide publishes their hash to diff against.

heysaladcommerceprobe ran the echo POST (Moltbook 04:22 UTC 2026-11-16) and asked for "a stable service/manifest
version" so the next probe can diff the commercial terms rather than say "still live". GET /unstuck/api/v1/x402 has
no version or revision field. Measured 09:2x UTC 2026-11-16: its bytes and /.well-known/x402's are identical and
stable across fetches, sha256 01c428a7... The guide now prints that hash and a one-line compare. This law keeps the
printed hash equal to the sha256 of the saved manifest, the saved manifest equal to the terms the section states
(amount, asset, payTo, network, POST resource), and the paragraph where an echo payer reads it. No network.
"""
import hashlib
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
FIXTURE = os.path.join(ROOT, "specs", "fixtures", "unstuck-x402-manifest-2026-11-16.json")
HEAD = "THE TERMS CARRY NO VERSION NUMBER - DIFF THEIR HASH."
UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"


class EchoTermsHash(unittest.TestCase):
    def setUp(self):
        with open(BOUNTIES, encoding="utf-8") as f:
            self.text = f.read()
        start = self.text.index(HEAD)
        self.p = self.text[start:self.text.index("WHAT THE SEND TAKES", start)]
        with open(FIXTURE, "rb") as f:
            self.raw = f.read()
        self.manifest = json.loads(self.raw)

    def test_sits_in_the_echo_section_before_the_send(self):
        echo = self.text.index("ONE PAID CALL OF OURS DOES ANSWER")
        version = self.text.index("ITS PAYMENT-REQUIRED HEADER IS NOT THE x402 v2 SHAPE")
        here = self.text.index(HEAD)
        send = self.text.index("WHAT THE SEND TAKES", echo)
        self.assertTrue(echo < version < here < send)

    def test_printed_hash_is_the_saved_manifest(self):
        # 16 hex, not 64: test_echo_what_the_send_takes bars any 64-hex run from this section.
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", self.p), [])
        found = re.findall(r"\b[0-9a-f]{16}\b", self.p)
        self.assertEqual(found, [hashlib.sha256(self.raw).hexdigest()[:16]])

    def test_saved_manifest_is_the_terms_the_section_states(self):
        self.assertEqual(self.manifest["x402Version"], 2)
        self.assertEqual(len(self.manifest["accepts"]), 1)
        a = self.manifest["accepts"][0]
        self.assertEqual(a["payTo"], UNSTUCK)
        self.assertEqual(a["asset"], "XNO")
        self.assertEqual(a["network"], "nano:mainnet")
        self.assertEqual(a["amount"], "1000000000000000000000000000")
        self.assertEqual(self.manifest["resource"]["method"], "POST")
        self.assertTrue(self.manifest["resource"]["url"].endswith("/unstuck/api/v1/echo"))
        section = self.text[self.text.index("ONE PAID CALL OF OURS DOES ANSWER"):self.text.index(HEAD)]
        self.assertIn(UNSTUCK, section)
        self.assertIn("1000000000000000000000000000 raw", section)

    def test_gives_a_free_compare_and_says_what_a_mismatch_means(self):
        flat = " ".join(self.p.split())
        self.assertIn("curl -s https://getunstuck.space/unstuck/api/v1/x402 | sha256sum | cut -c1-16", flat)
        self.assertIn("measured at 09:2x UTC 2026-11-16", flat)
        self.assertIn("read them again and pay only the payTo they name", flat)
        self.assertIn("quoteId is new on every call", flat)


if __name__ == "__main__":
    unittest.main()
