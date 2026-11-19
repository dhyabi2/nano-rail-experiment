#!/usr/bin/env python3
"""Law for what section 5 says we measured about the 03:54Z answerer of 11-19 (challenge #316).

#315 named nano_3dksi4mpi6o... as first seen and its XNO storefront as unverified. At 05:2x UTC 11-19 the keeper
read the address on rpc.nano.to: account_info "Account not found", history empty, nothing receivable - the account
is not opened. #462 itself gives no URL, host or payTo for the storefront it describes, so there was nothing to probe
unpaid. A sceptical reader of section 5 should see both facts, with the hour, instead of a bare "unverified" that
reads as if we had not looked. The text must still never call it an outside agent, a verified seller, or paid.

Run: python3 specs/test_bounties_answerer_unopened_1119.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AnswererUnopened1119(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index("NEWEST, measured 2026-11-19")
        self.raw = txt[i:txt.index("BEFORE THAT, measured 2026-11-08", i)]
        self.para = " ".join(self.raw.split())

    def test_says_what_we_read_and_when(self):
        for s in ("gives no URL, host or payTo", "nothing to probe",
                  "no block and nothing receivable on rpc.nano.to at 05:2x UTC",
                  "account not opened", "nothing on chain says whose it is"):
            self.assertIn(s, self.para, s)

    def test_no_claim_beyond_measurement(self):
        low = self.para.lower()
        for s in ("outside agent", "verified seller", "paid it", "is ours", "send it "):
            self.assertNotIn(s, low, s)
        self.assertIn("we have sent it nothing", low)

    def test_lines_fit_80_columns(self):
        for line in self.raw.splitlines():
            self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
