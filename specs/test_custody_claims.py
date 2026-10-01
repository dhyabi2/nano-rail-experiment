#!/usr/bin/env python3
"""Laws for ops/check-custody-claims.py (challenge #75).

The checker must flag the live wording of getunstuck.space/llms.txt as of 2026-10-01, must pass the replacement text
proposed in drafts/unstuck-llms-onramp-seed.md, and must not flag our own warning in bounties.txt.

Run: python3 specs/test_custody_claims.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("ccc", os.path.join(ROOT, "ops", "check-custody-claims.py"))
ccc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ccc)

# Verbatim from https://getunstuck.space/llms.txt, fetched 2026-10-01 08:20 UTC.
LIVE_2026_10_01 = """### Post an ask with NO wallet (two calls, no signup, no key you do not hold)
  Call 1 - GET /unstuck/api/v1/onramp/address
  Response: {"address":"nano_...","seed":"<64 hex>","index":0,"onboard_id":7}
  The address and the seed are yours; the network never stores the seed. Keep it.
  The stored asker is the nano_ address from call 1. When your account is funded you
  keep that address and that identity - it is yours."""

# Verbatim from https://getunstuck.space/unstuck/api/try-nano step 1 "http_shortcut", same fetch.
TRY_NANO_2026_10_01 = ("GET https://getunstuck.space/unstuck/api/v1/onramp/address returns {address, seed, index} "
                       "- the seed is yours, the network never stores it.")


def draft_replacement():
    with open(os.path.join(ROOT, "drafts", "unstuck-llms-onramp-seed.md")) as f:
        d = f.read()
    start = d.index("<<<REPLACEMENT") + len("<<<REPLACEMENT")
    return d[start:d.index("REPLACEMENT>>>")]


class CustodyClaims(unittest.TestCase):
    def test_flags_every_false_claim_in_live_text(self):
        labels = {l for l, _ in ccc.find_claims(LIVE_2026_10_01)}
        self.assertEqual(labels, {l for l, _ in ccc.CLAIMS})

    def test_flags_try_nano_shortcut(self):
        labels = {l for l, _ in ccc.find_claims(TRY_NANO_2026_10_01)}
        self.assertEqual(labels, {"seed called the agent's own", "server says it never stores the seed"})

    def test_draft_replacement_is_clean_and_says_compromised(self):
        rep = draft_replacement()
        self.assertEqual(ccc.find_claims(rep), [])
        self.assertIn("compromised", rep.lower())
        self.assertIn("/unstuck/api/v1/onramp/address", rep)
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            b = f.read()
        node_cmd = [ln.strip() for ln in b[b.index("STEP 1 - "):b.index("STEP 2 - ")].splitlines()
                    if ln.strip().startswith("node ")][0]
        self.assertIn(node_cmd, rep, "draft wallet command drifted from bounties.txt Step 1")

    def test_our_own_warning_is_not_flagged(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.assertEqual(ccc.find_claims(f.read()), [])

    def test_checker_never_calls_the_onramp(self):
        for url in ccc.GUIDES:
            self.assertNotIn("onramp", url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
