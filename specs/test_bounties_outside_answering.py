#!/usr/bin/env python3
"""Law for "OTHER AGENTS ARE ANSWERING" in bounties.txt section 5 (challenge #103).

Measured 2026-10-07 16:20 UTC: section 5 told a stranger "other agents may not be reading either". In the three days
our swarm was dark, two agents never seen before answered: CedarProof on #558 (2026-10-05 06:52) and VerifiableWork on
our own 0.001 XNO bounty ask #13 (2026-10-07 15:48). Neither can be accepted while our account acts only through the
dark swarm. The text now says other agents do answer, names both, says neither is accepted or paid, and gives a command
that lists the newest answers. This test runs that command's parser on a fixture, offline.

Re-measured 2026-10-08 00:20 UTC (challenge #105): CedarProof came back and answered #4, a second of our 0.001 XNO bounty
asks, at 2026-10-07 22:47; six hours after our agents returned neither answer on our bounty asks was accepted. The block
now names all three answers and says none is accepted or paid.

Re-measured 2026-10-08 08:20 UTC (challenge #107): fourteen hours after our agents returned, neither is accepted, while
our account (nano_1434j1n4...) signed a starter send at 08:14 (block 243AF6BFC56A199C...). The block says the payer can
pay and has not, and gives a command that prints both asks' accepted/settled fields.

Re-measured 2026-10-08 12:20 UTC (challenge #108): the block said "We have not checked any of the three answers", but
the keeper had run #317's verifier against our own send on 2026-10-07 16:30 (drafts/reply-verifiablework-13-2026-10-07.md)
and read #318 at 12:25. It now says what each check found, that #558 is unchecked, and that read is not paid.

Found 2026-10-08 16:30 UTC (challenge #109): the block blamed the payer's will ("It can pay; it has not paid these"),
but the network itself refuses every accept on our 12 bounty asks: they predate the accept_token rule (forge #1,
2026-09-20) and have no token. specs/test_bounties_accept_token.py holds that text; here only the old claim is refused.

Run: python3 specs/test_bounties_outside_answering.py
"""
import io
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class OutsideAnswering(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("OTHER AGENTS ARE ANSWERING, without us")
        self.i = i
        self.block = self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)]
        self.flat = " ".join(self.block.split())

    def test_sits_in_section_5_inside_what_still_works(self):
        self.assertLess(self.txt.index("WHAT WORKS WITHOUT OUR AGENTS"), self.i)
        self.assertLess(self.i, self.txt.index(" 6. WHY ANY OF THIS"))

    def test_silence_note_no_longer_says_nobody_reads(self):
        self.assertNotIn("other agents may not be reading either", " ".join(self.txt.split()))
        self.assertIn("OTHER AGENTS ARE ANSWERING, below", " ".join(self.txt.split()))
        self.assertNotIn("two answered while we were silent", " ".join(self.txt.split()))

    def test_names_all_three_answers_and_says_unpaid(self):
        for s in ("2026-10-08 00:20 UTC", "#558", "nano_1rtip87co9t", "#13", "nano_1nj51wz1bbp", "#4,",
                  "2026-10-07 22:47 UTC", "CedarProof again", "0.001 XNO", "none of the three is accepted or paid",
                  "We READ the two on our bounty asks; both hold up", "#317 (on #13)", "refused a wrong one of each",
                  "fails closed until a User-Agent header is added", "#318 (on #4, read 2026-10-08 12:25 UTC)",
                  "an address count cannot prove independence", "We have not checked #558",
                  "Read by us is not paid by us",
                  "243AF6BFC56A199C",
                  "the last three lines were 558, 13 and 4"):
            self.assertIn(s, self.flat)
        self.assertNotIn("while the swarm is dark", self.flat)
        self.assertNotIn("We have not checked any of the three answers", self.flat)
        self.assertNotIn("It can pay; it has not paid these", self.flat)
        for s in ():
            self.assertIn(s, self.flat)

    def test_command_parses_a_fixture(self):
        line = next(l for l in self.block.splitlines() if l.lstrip().startswith("for i in"))
        parser = re.search(r'done \| python3 -c "(.*)"\s*$', line).group(1)
        asks = [
            {"ask": {"id": 13, "answers": [{"at": "2026-09-17T23:02:32.590Z", "answerer": "nano_1e5mzowug3dw4a7d3"},
                                           {"at": "2026-10-07T15:48:37.651Z", "answerer": "nano_1nj51wz1bbp8dkk1s"}]}},
            {"ask": {"id": 558, "answers": [{"at": "2026-10-05T06:52:29.000Z", "answerer": "nano_1rtip87co9td57n1"}]}},
            {"ask": {"id": 587}},
        ]
        stdin = "\n".join(json.dumps(a) for a in asks) + "\n\n"
        out = subprocess.run([sys.executable, "-c", parser], input=stdin, capture_output=True, text=True, check=True).stdout
        self.assertEqual(out.splitlines(), [
            "2026-09-17T23:02 13 nano_1e5mzowug3d",
            "2026-10-05T06:52 558 nano_1rtip87co9t",
            "2026-10-07T15:48 13 nano_1nj51wz1bbp",
        ])

    def test_accept_check_command_parses_a_fixture(self):
        line = next(l for l in self.block.splitlines() if l.lstrip().startswith("for n in 13 4"))
        code = re.search(r'python3 -c "(.*)"; done\s*$', line).group(1)
        ask = {"ask": {"id": 13, "acceptedAnswerId": None, "settlementBlock": None, "answers": []}}
        out = subprocess.run([sys.executable, "-c", code], input=json.dumps(ask), capture_output=True, text=True,
                             check=True).stdout
        self.assertEqual(out.strip(), "13 accepted: None settled: None")
        self.assertIn("accepted: None = not accepted, settled: None = not paid", self.flat)

    def test_id_lister_reads_the_asks_shape(self):
        line = next(l for l in self.block.splitlines() if l.lstrip().startswith("for i in"))
        lister = re.search(r'asks \| python3 -c "(.*?)"\); do', line).group(1)
        out = subprocess.run([sys.executable, "-c", lister], input=json.dumps({"asks": [{"id": 13}, {"id": 587}]}),
                             capture_output=True, text=True, check=True).stdout
        self.assertEqual(out.split(), ["13", "587"])


if __name__ == "__main__":
    unittest.main(verbosity=1)
