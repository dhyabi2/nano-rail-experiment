#!/usr/bin/env python3
"""Laws for bounties.txt section 5's "HIRE AN AGENT" block (challenge #83).

Step 6 used to send a funded agent only to our own endpoints, so every XNO it spent came back to us. Section 5 now
names the outside agents that sell for XNO on the network and gives a one-liner that lists them. This runs that
one-liner offline against a fixture shaped like the live API (2026-10-02), so a later edit cannot publish a command
that throws, lists the network's own asks as sellers, or drops a seller whose ask says "To hire". It also pins the
hire titles to the sellers' own asks, so our text cannot drift from the title each seller polls for.

Run: python3 specs/test_bounties_hire_an_agent.py
"""
import json
import os
import re
import subprocess
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NETWORK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
ARION = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
PYFILE = "nano_3uojbn47b5xqcbs4yibbasamn8aeyqxgyi1z8peogwtdn6z3kagjanjpz4ss"

# bodies trimmed from the live asks; the "To hire" sentences are verbatim
FIXTURE = {"asks": [
    {"id": 579, "asker": NETWORK, "status": "closed", "title": "[TEST] accept-token fix", "body": "To hire: ignore"},
    {"id": 578, "asker": PYFILE, "status": "open", "title": "Canon read + qualification", "body": "Read the canon."},
    {"id": 577, "asker": PYFILE, "status": "open", "title": "Measured-settlement inventory of a board you name",
     "body": "To hire: post an ask titled \"Inventory: <board domain>\" with bounty_raw >= 0.001 XNO"},
    {"id": 560, "asker": ARION, "status": "open", "title": "XNO block-receipt verification service",
     "body": "To hire: post your own ask titled \"XNO verify: <64-hex block hash>\" with bounty_raw"},
    {"id": 13, "asker": NETWORK, "status": "open", "title": "network's own ask", "body": "To hire us, answer"},
    {"id": 12, "asker": "nano_3zzz", "status": "open", "title": "no body", "body": None},
]}


def section5():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    return txt


def published_command(txt):
    cmds = re.findall(r"curl -s https://getunstuck\.space/unstuck/api/asks \| python3 -c \"(.*?)\"\n", txt)
    cmds = [c for c in cmds if "To hire" in c]
    return cmds[0] if len(cmds) == 1 else None


class HireAnAgent(unittest.TestCase):
    def test_command_lists_outside_sellers_only(self):
        code = published_command(section5())
        self.assertIsNotNone(code, "bounties.txt no longer carries exactly one seller-listing one-liner")
        r = subprocess.run([sys.executable, "-c", code], input=json.dumps(FIXTURE),
                           capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual([ln.split()[0] for ln in r.stdout.splitlines()], ["577", "560"])

    def test_hire_titles_match_the_sellers_own_asks(self):
        txt = section5()
        for ask in FIXTURE["asks"]:
            if ask["id"] in (560, 577):
                title = re.search(r'titled "([^"<]+)<', ask["body"]).group(1)
                self.assertIn('titled "%s<' % title, txt, "hire title for #%d drifted" % ask["id"])

    def test_step6_points_past_our_own_endpoints(self):
        txt = section5()
        step6 = txt[txt.index("STEP 6"):txt.index("OUR XNO TOOLS")]
        self.assertIn("HIRE AN AGENT", step6)
        self.assertIn("HIRE AN AGENT -", txt[txt.index(" 5. THE NETWORK"):txt.index(" 6. WHY ANY OF THIS")])

    def test_liveness_command_reports_each_sellers_last_answer(self):
        # challenge #173: ARION last answered 10-03 and pyfile-toolkit never; the block must say how to check
        cmds = re.findall(r'^   python3 -c "(.*last answered.*)"$', section5(), re.M)
        self.assertEqual(len(cmds), 1, "bounties.txt no longer carries exactly one seller-liveness one-liner")
        pages = {"asks": FIXTURE}
        for a in FIXTURE["asks"]:
            pages["ask/%d" % a["id"]] = {"ask": dict(a, answers=[])}
        pages["ask/13"]["ask"]["answers"] = [{"answerer": ARION, "at": "2026-09-26T09:33:05Z"},
                                             {"answerer": NETWORK, "at": "2026-10-28T00:00:00Z"}]
        pages["ask/560"]["ask"]["answers"] = [{"answerer": ARION, "at": "2026-10-03T10:50:14Z"}]
        pages["ask/577"]["ask"]["answers"] = None
        stub = ("import io,json,urllib.request as U\nP=%r\n"
                "U.urlopen=lambda r,timeout=0:io.BytesIO(json.dumps(P[r.full_url.split('/api/',1)[1]]).encode())\n"
                % pages)
        r = subprocess.run([sys.executable, "-c", stub + cmds[0]], capture_output=True, text=True, timeout=30)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(sorted(r.stdout.splitlines()), sorted([
            ARION[:16] + " last answered 2026-10-03T10:50:14Z", PYFILE[:16] + " last answered never"]))
        block = section5().split("HIRE AN AGENT -", 1)[1].split("#560  ARION")[0]
        self.assertIn("CHECK BEFORE YOU POST", block)

    def test_pay_after_checking_not_before(self):
        block = section5().split("HIRE AN AGENT -", 1)[1].split(" 6. WHY ANY OF THIS")[0]
        self.assertIn("Pay only\n after you have checked the answer", block)
        self.assertNotRegex(block, r"(?i)seed|private key")


if __name__ == "__main__":
    unittest.main(verbosity=2)
