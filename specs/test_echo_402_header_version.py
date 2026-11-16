#!/usr/bin/env python3
"""Challenge #291: the echo route's 402 header is not the x402 v2 shape; the guide must say where the version is.

Measured 05:2x UTC 2026-11-16: the Payment-Required header of an unpaid POST to /unstuck/api/v1/echo decodes to a
bare list (the accepts array), with no x402Version and no resource; the body carries "x402Version":2 and a quoteId.
An outside agent who ran the call asked which challenge version it had parsed. This law keeps the guide's paragraph
and the box draft honest offline: the guide tells a reader to take the version from the body, names what it lacks,
promises no attempt ID or response hash, and points at a draft that exists and builds the v2 object. No network.
"""
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
DRAFT = os.path.join(ROOT, "drafts", "unstuck-echo-402-header-v2.md")
HEAD = "ITS PAYMENT-REQUIRED HEADER IS NOT THE x402 v2 SHAPE - READ THE BODY."


def paragraph(text):
    start = text.index(HEAD)
    end = text.index("WHAT THE SEND TAKES", start)
    return " ".join(text[start:end].split())


class EchoHeaderVersion(unittest.TestCase):
    def setUp(self):
        with open(BOUNTIES, encoding="utf-8") as f:
            self.bounties = f.read()
        self.p = paragraph(self.bounties)

    def test_paragraph_sits_under_the_echo_call(self):
        echo = self.bounties.index("ONE PAID CALL OF OURS DOES ANSWER")
        here = self.bounties.index(HEAD)
        send = self.bounties.index("WHAT THE SEND TAKES", echo)
        self.assertTrue(echo < here < send)

    def test_names_what_the_header_lacks_and_where_it_is(self):
        for want in ("bare list", "no x402Version", "no resource", '"x402Version":2', "quoteId",
                     "GET /unstuck/api/v1/x402", "record the version from the body"):
            self.assertIn(want, self.p)

    def test_promises_no_receipt_fields_we_did_not_measure(self):
        self.assertIn("not measured", self.p)
        self.assertIn("no attempt ID or response hash", self.p)
        self.assertIn("keep your block hash", self.p)

    def test_stamped_and_sourced(self):
        self.assertIn("05:2x UTC 2026-11-16", self.p)
        self.assertIn("heysaladcommerceprobe", self.p)

    def test_draft_exists_and_builds_the_v2_object(self):
        self.assertIn("drafted for the box, not live", self.p)
        self.assertNotIn("github.com", self.p)
        with open(DRAFT, encoding="utf-8") as f:
            draft = f.read()
        new = draft[draft.index("NEW:"):]
        for want in ('"x402Version": 2', '"resource"', '"accepts": accepts', '"method": "POST"'):
            self.assertIn(want, new)
        self.assertIn("Not live", draft)

    def test_sample_header_shapes_parse_as_the_text_says(self):
        bare = json.loads('[{"scheme":"exact","network":"nano:mainnet","asset":"XNO"}]')
        v2 = json.loads('{"x402Version":2,"resource":{"url":"u"},"accepts":[]}')
        self.assertIsInstance(bare, list)
        self.assertEqual(v2.get("x402Version"), 2)

    def test_no_address_in_draft(self):
        with open(DRAFT, encoding="utf-8") as f:
            self.assertNotRegex(f.read(), r"nano_[13][13-9a-km-uw-z]{59}")


if __name__ == "__main__":
    unittest.main()
