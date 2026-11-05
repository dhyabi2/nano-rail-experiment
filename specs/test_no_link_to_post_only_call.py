#!/usr/bin/env python3
"""Law: no published page hyperlinks a URL that answers a GET with 404 (challenge #206).

The x402 echo (https://getunstuck.space/unstuck/api/v1/echo) takes POST only; a GET answers a bare
{"error":"not found"}. #205 listed it in the AiDirectory with the name linked to that URL, so a crawler or a
reader that follows the link lands on a 404 - our own page made the dead end. 28 outside clients sent a GET to it
on 11-02 (traffic file, 20:07 UTC). The name now links to the terms (GET 200), which state the method.
The copy-paste curl commands (with -X POST) stay; only links (HTML href, Markdown link targets) are barred.

Run: python3 specs/test_no_link_to_post_only_call.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
POST_ONLY = ["https://getunstuck.space/unstuck/api/v1/echo"]
FILES = ["aidirectory/index.html", "aidirectory.html", "aidirectory/llms.txt", "aidirectory-llms.txt",
         "bounties.txt", "swap.txt", "canon.txt", "canon.html"]


class NoLinkToPostOnly(unittest.TestCase):
    def test_no_link_targets_a_post_only_url(self):
        for rel in FILES:
            p = os.path.join(PUB, rel)
            if not os.path.exists(p):
                continue
            s = open(p, encoding="utf-8").read()
            for u in POST_ONLY:
                for pat in (r'href="%s[?#"]' % re.escape(u), r"\]\(%s[)?#]" % re.escape(u)):
                    self.assertIsNone(re.search(pat, s), "%s links to POST-only %s" % (rel, u))

    def test_html_mirrors_identical(self):
        a = open(os.path.join(PUB, "aidirectory.html"), encoding="utf-8").read()
        b = open(os.path.join(PUB, "aidirectory/index.html"), encoding="utf-8").read()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
