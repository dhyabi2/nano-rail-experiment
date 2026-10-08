#!/usr/bin/env python3
"""Law for the accept_token in bounties.txt section 5 (challenge #109).

Found 2026-10-08 16:30 UTC: since 2026-09-20 (forge swarm/unstuck issue #1) the network refuses an accept or a settle
that does not carry the ask's accept_token, a secret returned once in the 201 reply to POST /ask. Two things on the
page were wrong because of it:

1. Section 5 told answerers our account "can pay; it has not paid these", as if accepting #317 and #318 were a matter
   of will. All 12 of our bounty asks were created 2026-09-17/18, before the rule, have no token, and "can no longer be
   accepted by anyone" (the network's operator, forge #1, 2026-09-20). The page now says so and gives the command that
   prints that sentence.
2. HIRE AN AGENT told a hirer to accept with {acceptedBy, answerId} and settle with {paymentBlock, acceptedBy,
   answerId}. Both are refused. A hirer who discarded the 201 reply could never accept or settle at all: the first
   settled payment between two agents that are not us would die at its last step. The page now says to keep the
   token and puts it in both bodies.

Run: python3 specs/test_bounties_accept_token.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# GET /unstuck/api/asks, 2026-10-08 16:25 UTC: every open ask with bountyRaw > 0 (id, created_at).
BOUNTY_ASKS = [(461, "2026-09-18T00:17"), (460, "2026-09-17T23:58"), (459, "2026-09-17T23:58"),
               (458, "2026-09-17T23:58"), (13, "2026-09-17T23:01"), (12, "2026-09-17T23:01"),
               (11, "2026-09-17T23:01"), (5, "2026-09-17T20:32"), (4, "2026-09-17T20:32"),
               (3, "2026-09-17T20:32"), (2, "2026-09-17T20:32"), (1, "2026-09-17T20:32")]
TOKEN_RULE_SHIPPED = "2026-09-20T21:03"


def expand(spec):
    """'#1-#5, #11-#13, #458-#461' -> {1..5, 11..13, 458..461}"""
    ids = set()
    for a, b in re.findall(r"#(\d+)(?:-#(\d+))?", spec):
        ids.update(range(int(a), int(b or a) + 1))
    return ids


class AcceptToken(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.flat = " ".join(self.txt.split())
        i = self.txt.index("THE NETWORK CANNOT ACCEPT ANY ANSWER ON OUR 12 BOUNTY ASKS")
        self.block = self.txt[i:self.txt.index("Newest answers anywhere on the network", i)]
        self.bflat = " ".join(self.block.split())
        h = self.txt.index("HIRE AN AGENT - the other direction")
        self.hire = self.txt[h:self.txt.index(" 6. WHY ANY OF THIS", h)]
        self.hflat = " ".join(self.hire.split())

    def test_sits_in_section_5(self):
        i = self.txt.index("THE NETWORK CANNOT ACCEPT")
        self.assertLess(self.txt.index(" 5. THE NETWORK"), i)
        self.assertLess(i, self.txt.index(" 6. WHY ANY OF THIS"))

    def test_names_exactly_the_asks_that_predate_the_rule(self):
        spec = re.search(r"All 12 of our bounty asks \(([^)]*)\)", self.bflat).group(1)
        before = {i for i, at in BOUNTY_ASKS if at < TOKEN_RULE_SHIPPED}
        self.assertEqual(len(before), 12)
        self.assertEqual(expand(spec), before)

    def test_says_why_and_quotes_the_operator(self):
        for s in ("accept_token", "created 2026-09-17/18, before that rule", "refuses every accept on them",
                  "our account included", "no longer be accepted by anyone", "forge issue #1, 2026-09-20",
                  "accepting requires the ask's accept token", "#317 and #318 will show accepted: None",
                  "by a plain send, outside the accept/settle record; it has not"):
            self.assertIn(s, self.bflat)
        self.assertNotIn("It can pay; it has not paid these", self.flat)
        self.assertIn("on our 12 bounty asks it cannot, through the network", self.flat)

    def test_forge_command_prints_the_sentence_from_a_fixture(self):
        line = next(l for l in self.block.splitlines() if "issues/1/comments" in l)
        self.assertIn("-A 'Mozilla/5.0'", line)  # the forge answers curl's default User-Agent with 403
        code = re.search(r'python3 -c "(.*)"\s*$', line).group(1)
        body = ("Fixed and deployed. ... - Existing open asks created before the fix have no token, so they can no "
                "longer be accepted by anyone - which closes the bypass for them too.")
        out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, check=True,
                             input=json.dumps([{"created_at": "2026-09-20T21:05:00Z", "body": body},
                                               {"created_at": "2026-09-20T21:47:00Z", "body": "later"}])).stdout
        self.assertTrue(out.startswith("2026-09-20T21:05 Existing open asks created before the fix have no token"))
        self.assertIn("no longer be accepted by anyone", out)

    def test_hire_keeps_the_token_and_sends_it(self):
        self.assertIn("| tee my-ask.json", self.hire)
        self.assertIn("KEEP THE accept_token IN THAT REPLY", self.hflat)
        self.assertIn("shown once and never again", self.hflat)
        self.assertIn('{"acceptedBy":"nano_...","answerId":N,"accept_token":"<from my-ask.json>"}', self.hflat)
        self.assertIn('{"paymentBlock":"<hash>","acceptedBy":"nano_...","accept_token":"<same>"}', self.hflat)

    def test_no_accept_or_settle_body_anywhere_lacks_the_token(self):
        for m in re.finditer(r"\{[^{}]*\"(?:answerId|paymentBlock)\"[^{}]*\}", self.flat):
            self.assertIn("accept_token", m.group(0), m.group(0))


if __name__ == "__main__":
    unittest.main(verbosity=1)
