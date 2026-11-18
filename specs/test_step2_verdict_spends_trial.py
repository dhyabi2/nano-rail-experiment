#!/usr/bin/env python3
"""Challenge #307: onboarding step 2 ("check an address") told every reader that extract.paypercall.dev's
address-verdict "costs 0.0001 XNO, so an empty wallet gets HTTP 402 (measured 2026-11-11)". Since #304/#305 the same
texts say the sellers serve 5 calls a day FREE per IP, one count for all five sellers (#304: trial_remaining 3, 2, 1
across extract and geoip). So the step 2 line was wrong for a first call, and it hid the real cost for an agent with
no XNO: a verdict call at step 2 spends one of the free calls step 6 depends on. Measured 07:3x UTC 11-18 from the
cloud (whose trial was already spent): address-verdict WITH ?account= answered 402 payment_required.

This law keeps the corrected line in all seven copies and forbids the old one.

Run: python3 specs/test_step2_verdict_spends_trial.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FILES = [
    "published/aidirectory/llms.txt",
    "published/aidirectory-llms.txt",
    "published/aidirectory/index.html",
    "published/aidirectory.html",
    "published/bounties.txt",
]
OLD = ["so an empty wallet gets HTTP 402 (measured 2026-11-11)",
       "(an empty wallet gets HTTP 402, measured 2026-11-11)",
       "so a wallet made in step 1 gets HTTP 402 (measured 2026-11-11)"]
NEW = ["past the sellers' free trial it costs 0.0001 XNO",
       "for all five sellers",
       "a call here spends a free call",
       "step 6 needs",
       "402 even with ?account= once the trial was spent"]


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.replace("&#x27;", "'").split()).lower()


class Step2VerdictSpendsTrial(unittest.TestCase):
    def check(self, text, where):
        t = flat(text)
        for o in OLD:
            self.assertNotIn(o.lower(), t, where)
        for n in NEW:
            self.assertIn(n.lower(), t, where + ": " + n)

    def test_published_copies(self):
        for p in FILES:
            self.check(read(p), p)

    def test_tools_json_step2_note(self):
        notes = []

        def walk(x):
            if isinstance(x, dict):
                v = x.get("note")
                if isinstance(v, str) and "address-verdict" in v and "checksum" in v:
                    notes.append(v)
                for w in x.values():
                    walk(w)
            elif isinstance(x, list):
                for w in x:
                    walk(w)

        walk(json.loads(read("published/aidirectory/tools.json")))
        self.assertTrue(notes, "tools.json has no step 2 note")
        for v in notes:
            self.check(v, "tools.json step 2 note")

    def test_law_fails_on_the_old_text(self):
        with self.assertRaises(AssertionError):
            self.check("Do not use address-verdict for this step: it costs 0.0001 XNO, so an empty wallet gets "
                       "HTTP 402 (measured 2026-11-11).", "old")


if __name__ == "__main__":
    unittest.main(verbosity=2)
