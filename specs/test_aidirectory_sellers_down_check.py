#!/usr/bin/env python3
"""Law for the seller check outside bounties.txt (challenge #151).

Challenge #149 put a bounded /health check in front of bounties.txt STEP 6, because the five paypercall.dev sellers
had not answered since about 10:25 UTC 2026-10-17. The AiDirectory copies (the most-read guide on 10-24: 28 outside
clients by 16:07 UTC) and swap.txt step 5 still said "spend it" there with no check. Every copy now carries the same
command as bounties.txt, says 000 means do not pay, and names what needs no seller. bounties.txt also no longer
points strangers at an issue in a private repository.

Run: python3 specs/test_aidirectory_sellers_down_check.py
"""
import html
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")


def read(rel):
    with open(os.path.join(PUB, rel)) as f:
        return f.read()


def bounties_cmd():
    return next(ln.strip() for ln in read("bounties.txt").splitlines() if ln.strip().startswith("for h in"))


class SellersCheckEverywhere(unittest.TestCase):
    def test_llms_copies_check_inside_step6(self):
        for rel in ["aidirectory-llms.txt", "aidirectory/llms.txt"]:
            t = read(rel)
            i = t.index("### 6.")
            step = t[i:t.index("## Callable right now", i)]
            self.assertIn(bounties_cmd(), step, rel)
            self.assertIn("000 means no answer, so do not pay", " ".join(step.split()), rel)

    def test_html_copies_check_inside_step6(self):
        for rel in ["aidirectory.html", "aidirectory/index.html"]:
            t = read(rel)
            i = t.index('<span class="num">6</span>')
            step = html.unescape(t[i:t.index("</li>", i)])
            self.assertIn(bounties_cmd(), step, rel)
            self.assertIn("000 means no answer, so do not pay", step, rel)

    def test_tools_json_carries_the_same_check(self):
        d = json.loads(read("aidirectory/tools.json"))
        self.assertEqual(d["onboarding"][5]["check_first"]["cmd"], bounties_cmd())
        self.assertIn("paypercall.dev", d["callable_now_caveat"])

    def test_callable_list_is_not_unqualified(self):
        for rel in ["aidirectory-llms.txt", "aidirectory/llms.txt", "aidirectory.html"]:
            t = read(rel)
            i = t.index("Callable right now")
            self.assertIn("run onboarding step 6&#x27;s check" if rel.endswith(".html") else
                          "run onboarding step 6's check", t[i:i + 600], rel)

    def test_swap_step5_checks_before_spending(self):
        t = read("swap.txt")
        i = t.index(" 5. Spend")
        step = t[i:t.index(" 6. ", i)]
        self.assertIn(bounties_cmd(), step)
        self.assertIn("000 means no", step)

    def test_no_published_file_links_the_private_repo(self):
        for rel in ["bounties.txt", "swap.txt", "canon.txt", "aidirectory-llms.txt", "aidirectory.html"]:
            self.assertNotIn("github.com/dhyabi2/nano-rail-experiment", read(rel), rel)


if __name__ == "__main__":
    unittest.main(verbosity=2)
