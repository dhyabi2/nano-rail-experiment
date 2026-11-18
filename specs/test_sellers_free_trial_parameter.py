#!/usr/bin/env python3
"""Challenge #304: the paypercall.dev sellers' free trial (5 calls a day, "trial" in every manifest) is the only real
paid-tool use an agent holding no XNO can make, and bounties.txt hid it: the RIGHT NOW box did not name it, and step 0
of "HOW A CALL IS PAID" said "A 402 there is the trial spent". Measured 03:2x UTC 2026-11-18 from the cloud: a call
that carries its parameter (extract?url=, geoip?ip=) answered 200 with "free_trial": true and "trial_remaining" 3, 2, 1
across two hosts (one count for all five), while the same call with no parameter answered 402 at once with trial left.
So a stranger probing a bare URL reads "pay first" and leaves. This law keeps the box line, the parameter rule and a
runnable parameterised example, and forbids the old diagnosis.

Run: python3 specs/test_sellers_free_trial_parameter.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class SellersFreeTrialParameter(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt"), encoding="utf-8") as f:
            self.txt = f.read()
        i = self.txt.index(" RIGHT NOW - measured ")
        self.box = " ".join(self.txt[i:self.txt.index(" 1. THE REWARDS")].split())
        s6 = self.txt.index("\n STEP 6 - ")
        j = self.txt.index(" HOW A CALL IS PAID", s6)
        self.block = self.txt[j:self.txt.index("\n\n", j)]
        self.flat = " ".join(self.block.split())

    def test_box_names_the_trial_and_the_parameter(self):
        self.assertIn("5 calls a day FREE (trial) if the call carries its ?url=/?ip=: STEP 6.", self.box)

    def test_step0_says_a_bare_url_answers_402_with_trial_left(self):
        self.assertIn('a call WITH its parameter (?url=, ?ip=, ?account=, ?q=) was served 200', self.flat)
        self.assertIn('"free_trial": true', self.flat)
        self.assertIn("one count for all five hosts", self.flat)
        self.assertIn("a bare URL answered 402 at once, trial or not", self.flat)
        self.assertIn("Add the parameter before you decide to pay", self.flat)

    def test_old_diagnosis_is_gone(self):
        self.assertNotIn("A 402 there is the trial spent", self.flat)

    def test_example_carries_its_parameter_and_no_payment_header(self):
        cmd = re.search(r"curl -s '(https://geoip\.paypercall\.dev/api/v1/geoip\?ip=[0-9.]+)'", self.block)
        self.assertIsNotNone(cmd)
        line = [ln for ln in self.block.splitlines() if "geoip?ip=" in ln][0]
        self.assertNotIn("X-PAYMENT", line)

    def test_law_fails_on_the_old_text(self):
        old = self.flat.replace("A 402 is not the seller down", "A 402 there is the trial spent, not the seller down")
        self.assertIn("A 402 there is the trial spent", old)


if __name__ == "__main__":
    unittest.main(verbosity=2)
