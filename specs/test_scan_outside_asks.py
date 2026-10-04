#!/usr/bin/env python3
"""Challenge #96: ops/scan-ask-inbox.py must surface every outside ask, not only canon confirmations,
referral claims and asks with a bounty. On 2026-10-04 ask #587 (an outside seller asking where a first
buyer comes from, bounty 0) was dropped as "other", so the one tool that reads our door reported nothing.
Our own asks - Unstuck's account, the treasury, and the swarm's titled probes - must stay out."""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("scan", os.path.join(ROOT, "ops", "scan-ask-inbox.py"))
scan = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scan)

OUTSIDE = "nano_3qxi4ns7u5cj69apaxiouwacfhffpo6ho7dg53b9am13c7s14wdj6p87b3rx"


def ask(i, asker, title, answers=0, bounty="0"):
    return {"id": i, "asker": asker, "title": title, "body": "", "bountyRaw": bounty, "status": "open",
            "acceptedAnswerId": None, "settlementBlock": None, "answerCount": answers,
            "created_at": "2026-10-04T14:22:54.582Z"}


FIXTURE = {"asks": [
    ask(587, OUTSIDE, "Selling one exact, non-scalable read: 15 days, 0 buyers. Where is the first-buyer channel?"),
    ask(1, scan.TREASURY, "How do I verify an incoming Nano payment without running a Nano node?", 21, "100000"),
    ask(2, "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7", "treasury question"),
    ask(582, "nano_314997u53oqa4jq5etuskx6wrabw6gjmwpms9u3uboyraumxdrj31xfau4fk", "self-probe onramp e2e"),
    ask(584, "nano_1rk6kg39omchu8bspurrqj4gs5kn6xgez1g8j7d6tw77hyp97jgmxjr6dgxd",
        "self-onramp path verification (throwaway probe, will be closed)", 1),
    ask(579, "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9", "[TEST] accept-token fix verification"),
]}


class OutsideAsksVisible(unittest.TestCase):
    def setUp(self):
        self.rows = {r["id"]: r for r in scan.build_report(FIXTURE, {})}

    def test_plain_outside_question_is_listed_and_pending(self):
        self.assertIn(587, self.rows, "an outside ask with no bounty and no keyword was dropped")
        self.assertTrue(self.rows[587]["pending"])
        self.assertEqual(self.rows[587]["kind"], "outside_ask")

    def test_our_own_asks_and_probes_are_not_outside(self):
        self.assertEqual(set(self.rows), {587}, "our own account, treasury or a titled probe counted as outside")


if __name__ == "__main__":
    unittest.main()
