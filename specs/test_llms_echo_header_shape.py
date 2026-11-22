#!/usr/bin/env python3
"""Law for challenge #331 (2026-11-22): /ai/llms.txt warns that the echo 402's PAYMENT-REQUIRED header is a bare list.

#291 (11-16) put the warning into bounties.txt section 4: the echo route's Payment-Required header decodes to a bare
list of accepts with no x402Version and no resource, while the JSON body of the same 402 is the v2 object. Both
llms.txt copies - the most-read guide after the Unstuck API (aidirectory 135 outside requests, 18 clients by 10:59Z
11-22) - still said only "Unpaid, it answers 402 with the same terms", so an x402 v2 client sent there from llms.txt
would read the header and meet a shape it may refuse. Re-measured 11:1x UTC 11-22: header still the bare list, body
still x402Version 2 with a quoteId. Change this law with the text when the box sends the v2 object in the header.

Run: python3 specs/test_llms_echo_header_shape.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ("published/aidirectory/llms.txt", "published/aidirectory-llms.txt")


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return " ".join(f.read().split())


def echo_paragraph(t):
    start = t.index("Unpaid, it answers 402 with the same terms.")
    return t[start:t.index("Send exactly that amount", start)]


class LlmsEchoHeaderShape(unittest.TestCase):
    def test_both_copies_identical(self):
        self.assertEqual(read(COPIES[0]), read(COPIES[1]))

    def test_warning_sits_before_the_send(self):
        for p in COPIES:
            para = echo_paragraph(read(p))
            with self.subTest(copy=p):
                self.assertIn("PAYMENT-REQUIRED HEADER IS NOT THE x402 v2 SHAPE - READ THE BODY", para)
                self.assertIn("bare list", para)
                self.assertIn("no x402Version and no resource", para)
                self.assertIn('"x402Version":2', para)
                self.assertIn("quoteId", para)

    def test_points_at_the_box_draft_that_exists(self):
        self.assertIn("drafts/unstuck-echo-402-header-v2.md", echo_paragraph(read(COPIES[0])))
        self.assertTrue(os.path.exists(os.path.join(ROOT, "drafts/unstuck-echo-402-header-v2.md")))

    def test_bounties_still_carries_the_same_warning(self):
        with open(os.path.join(ROOT, "published/bounties.txt"), encoding="utf-8") as f:
            self.assertIn("ITS PAYMENT-REQUIRED HEADER IS NOT THE x402 v2 SHAPE - READ THE BODY", f.read())


if __name__ == "__main__":
    unittest.main()
