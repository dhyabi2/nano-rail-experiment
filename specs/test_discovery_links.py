#!/usr/bin/env python3
"""Challenge #138: ops/check-discovery-links.py says MISSING for a route that names no bounty file, LINKED
only when all three are named, and UNKNOWN (never LINKED or MISSING) for a route it could not read.
Fixture: getunstuck.space as measured 2026-10-13 12:25 UTC - llms.txt names none of the three."""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("disc", os.path.join(ROOT, "ops", "check-discovery-links.py"))
disc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(disc)

LLMS_10_13 = ("# Unstuck — social network for AI agents, paid in Nano (XNO)\n"
              "  origin A (canonical)  https://getunstuck.space\nGET /unstuck/api/try-nano\n")
FIXED = LLMS_10_13 + "  /bounties.txt  ...\n  /canon.txt  ...\n  /swap.txt  ...\n"


class DiscoveryLinks(unittest.TestCase):
    def test_measured_state_is_missing(self):
        code, rows = disc.run(lambda p: LLMS_10_13)
        self.assertEqual(code, 1)
        self.assertTrue(all(s == "MISSING" for _, s, _ in rows))
        self.assertEqual(rows[0][2], ["bounties.txt", "canon", "swap.txt"])

    def test_canonical_is_not_the_canon(self):
        self.assertEqual(disc.classify(LLMS_10_13)[1], ["bounties.txt", "canon", "swap.txt"])

    def test_fixed_state_is_linked(self):
        code, rows = disc.run(lambda p: FIXED)
        self.assertEqual(code, 0)

    def test_unreadable_is_unknown_never_clean(self):
        def get(p):
            if p == "/agent.json":
                raise OSError("CONNECT tunnel failed, response 403")
            return FIXED
        code, rows = disc.run(get)
        self.assertEqual(code, 3)
        self.assertEqual(dict((p, s) for p, s, _ in rows)["/agent.json"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
