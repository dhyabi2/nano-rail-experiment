#!/usr/bin/env python3
"""Laws for ops/unpaid-outside-answers.py (challenge #92).

The tool reads the network's bounty asks and lists the answers that came from outside and were never
paid, so the asker can settle one without reading 214 answers by hand. These laws pin what must not
drift: our own answers never count as outside, an address is OUTSIDE only with evidence, a bad-checksum
address is flagged and gets no pay command, a settled or closed ask is not "unpaid", one ask's bounty is
owed once however many answers sit on it, and the printed calls are the asker's, not ours to run.

Run: python3 specs/test_unpaid_outside_answers.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("upoa", os.path.join(ROOT, "ops", "unpaid-outside-answers.py"))
upoa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upoa)

UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
TREASURY = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
ARION = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
STRANGER = "nano_1dscwmthd93dm1kbsaehqz9c39yedt53by7sbcdh7jhb74ou7994ry3kf45a"  # valid checksum, no evidence
BAD = "nano_1e5mzowug3dw4a7d3x3jwt8wxntf1u7q4zg7qkagqz8hsqn5yy9sc5c6nwm"       # live answerer; node: "Bad account number"
MILLI = "1000000000000000000000000000"

ASKS = {"asks": [
    {"id": 13, "asker": UNSTUCK, "status": "open", "bountyRaw": MILLI, "settlementBlock": None, "title": "verify a payment"},
    {"id": 2, "asker": UNSTUCK, "status": "open", "bountyRaw": MILLI, "settlementBlock": None, "title": "receivable"},
    {"id": 9, "asker": UNSTUCK, "status": "open", "bountyRaw": MILLI, "settlementBlock": "AB" * 32, "title": "settled"},
    {"id": 579, "asker": UNSTUCK, "status": "closed", "bountyRaw": MILLI, "settlementBlock": None, "title": "closed"},
    {"id": 560, "asker": ARION, "status": "open", "bountyRaw": "0", "settlementBlock": None, "title": "no bounty"},
]}


def ans(i, who, chars, at="2026-09-26T09:16:00Z"):
    return {"id": i, "answerer": who, "body": "x" * chars, "status": "pending", "at": at}


DETAILS = {
    13: {"answers": [ans(219, ARION, 895, "2026-09-22T23:11:00Z"), ans(291, ARION, 2164), ans(182, TREASURY, 900),
                     ans(10, BAD, 1300), ans(305, STRANGER, 500)]},
    2: {"answers": [ans(295, ARION, 2072), ans(21, UNSTUCK, 400), ans(46, BAD, 27)]},
    9: {"answers": [ans(1, ARION, 3000)]},
    579: {"answers": [ans(308, ARION, 3000)]},
    560: {"answers": [ans(400, STRANGER, 3000)]},
}


class UnpaidOutsideAnswers(unittest.TestCase):
    def setUp(self):
        self.report = upoa.build_report(ASKS, DETAILS)
        self.rows = {r["answerer"]: r for r in self.report["answerers"]}

    def test_only_open_unsettled_bounty_asks(self):
        self.assertEqual([a["id"] for a in upoa.unpaid_bounty_asks(ASKS)], [2, 13])
        self.assertEqual(self.report["totals"]["bounty_asks"], 2)

    def test_ours_never_counted_as_outside(self):
        self.assertNotIn(TREASURY, self.rows)
        self.assertNotIn(UNSTUCK, self.rows)
        self.assertEqual(self.report["totals"]["ours"], 2)

    def test_outside_needs_evidence(self):
        self.assertEqual(self.rows[ARION]["kind"], "outside")
        self.assertTrue(self.rows[ARION]["evidence"])
        self.assertEqual(self.rows[STRANGER]["kind"], "unclassified")
        self.assertEqual(self.report["answerers"][0]["answerer"], ARION)

    def test_bounty_owed_once_per_ask(self):
        self.assertEqual(self.rows[ARION]["asks"], [2, 13])
        self.assertEqual(self.rows[ARION]["owed_raw"], 2 * int(MILLI))
        self.assertEqual(len(self.rows[ARION]["answers"]), 3)

    def test_settled_and_closed_answers_not_listed(self):
        listed = {a["answer"] for r in self.report["answerers"] for a in r["answers"]}
        self.assertNotIn(1, listed)
        self.assertNotIn(308, listed)
        self.assertNotIn(400, listed)

    def test_bad_checksum_is_flagged_and_gets_no_pay_command(self):
        self.assertFalse(self.rows[BAD]["address_ok"])
        self.assertTrue(self.rows[ARION]["address_ok"])
        out = upoa.render(self.report, ASKS)
        bad_block = out[out.index(BAD):]
        self.assertIn("CHECKSUM FAILS", bad_block.splitlines()[0])
        self.assertNotIn(BAD, "".join(l for l in out.splitlines() if "curl" in l))

    def test_pay_first_is_the_askers_call_on_the_longest_answer(self):
        out = upoa.render(self.report, ASKS)
        curls = [l.strip() for l in out.splitlines() if l.strip().startswith("curl")]
        self.assertEqual(len(curls), 2)  # one accept + one settle, for ARION only
        self.assertIn("/ask/13/accept", curls[0])
        self.assertIn('"answerId":291', curls[0])
        self.assertIn(f'"acceptedBy":"{UNSTUCK}"', curls[0])
        self.assertIn("<send block hash>", curls[1])  # the tool never invents or makes a payment

    def test_tool_has_no_write_path(self):
        with open(os.path.join(ROOT, "ops", "unpaid-outside-answers.py")) as f:
            src = f.read()
        self.assertNotIn("data=", src)
        self.assertNotIn('method="POST"', src)
        self.assertNotIn("seed", src.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
