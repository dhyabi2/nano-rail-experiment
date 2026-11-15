#!/usr/bin/env python3
"""Law: bounties.txt warns that try-nano's step 1 one-liner loses the seed (challenge #279).

Measured 2026-11-15 17:2x UTC: GET /unstuck/api/try-nano step 1 "no_install" command draws seed=os.urandom(32) and
prints only the address - the seed is never printed or saved - while step 3 asks for "the seed you generated
yourself in step 1". An address made that way can never receive its starter. try-nano is served by the box
(drafts/box-try-nano-step1-seed-lost.md); until it changes, bounties.txt must say so beside its other try-nano
warnings and point at section 4's nanokey.py, which keeps the seed in ./nano-seed.txt.

Run: python3 specs/test_bounties_try_nano_step1_seed.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        return re.sub(r"\s+", " ", f.read())


class TryNanoStep1Seed(unittest.TestCase):
    def setUp(self):
        self.b = flat("published/bounties.txt")

    def test_warning_present(self):
        for phrase in ["Do not make your address with try-nano's step 1 \"no_install\" command",
                       "prints only the address: the seed is never printed and never written to a file",
                       "can never be received or spent by anyone"]:
            self.assertIn(phrase, self.b)

    def test_points_at_nanokey_which_keeps_the_seed(self):
        i = self.b.index("Do not make your address with try-nano's step 1")
        tail = self.b[i:i + 1200]
        self.assertIn("section 4's STEP 1 nanokey.py", tail)
        self.assertIn("./nano-seed.txt mode 600", tail)
        # the tool it names really keeps the seed
        self.assertIn('os.open("nano-seed.txt", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)', self.b)

    def test_warning_sits_with_the_other_try_nano_warnings(self):
        step3 = self.b.index("Do not receive it the way try-nano's step 3 says")
        step1 = self.b.index("Do not make your address with try-nano's step 1")
        self.assertLess(step3, step1)
        self.assertLess(step1 - step3, 2500)

    def test_box_draft_exists(self):
        d = flat("drafts/box-try-nano-step1-seed-lost.md")
        self.assertIn("challenge #279", d)
        self.assertIn("O_EXCL", d)


if __name__ == "__main__":
    unittest.main()
