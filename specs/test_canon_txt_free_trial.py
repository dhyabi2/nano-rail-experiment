#!/usr/bin/env python3
"""Challenge #306: canon.txt (11 outside clients on 11-18 by 06:00 UTC) and swap.txt (9) sent a reader with no XNO
only to a swap, and named the paypercall.dev sellers' free trial nowhere (0 hits for "trial" in either file), though
#304/#305 put it in bounties.txt and the directory. The trial ("trial": 5 calls a day per IP, in every manifest) is
the one use of a paid seller that needs no XNO. Measured 03:2x UTC 11-18: a call with its parameter answered 200
"free_trial": true, a bare URL 402; 06:2x UTC 11-18 the same network, its 5 spent, got 402 even with ?account=.
This law keeps, in both files' no-XNO lines: the trial, the parameter rule, a runnable parameterised call, and the
reading of a 402 with the parameter as spent, not down.

Run: python3 specs/test_canon_txt_free_trial.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CALL = "curl -s 'https://geoip.paypercall.dev/api/v1/geoip?ip=1.1.1.1'"


def read(name):
    with open(os.path.join(ROOT, "published", name), encoding="utf-8") as f:
        return f.read()


class CanonTxtFreeTrial(unittest.TestCase):
    def check(self, block, where):
        flat = " ".join(block.split())
        self.assertIn('"trial"', flat, where)
        self.assertIn("5 calls a day from one IP free", flat, where)
        self.assertIn('"free_trial": true', flat, where)
        self.assertIn("a bare URL answers 402 at once, trial or not", flat, where)
        self.assertIn(CALL, block, where)
        self.assertIn("not", flat[flat.index("A 402 WITH the parameter"):], where)
        self.assertIn("seller", flat[flat.index("A 402 WITH the parameter"):], where)

    def test_canon_txt_no_xno_line(self):
        txt = read("canon.txt")
        i = txt.index("  No XNO yet?")
        block = txt[i:txt.index("swap.txt", i)]
        self.check(block, "canon.txt")

    def test_swap_txt_before_routes(self):
        txt = read("swap.txt")
        end = txt.index(" 1. WHICH ROUTES ACTUALLY EXIST")
        i = txt.index("SEE THE RAIL SERVE BEFORE YOU SWAP, FREE")
        self.assertLess(i, end)
        self.check(txt[i:end], "swap.txt")

    def test_trial_line_is_dated(self):
        for name in ("canon.txt", "swap.txt"):
            self.assertIn("measured 03:2x UTC 11-18", " ".join(read(name).split()), name)


if __name__ == "__main__":
    unittest.main()
