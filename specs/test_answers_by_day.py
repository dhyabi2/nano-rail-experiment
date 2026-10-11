#!/usr/bin/env python3
"""Laws for ops/answers-by-day.py (challenge #102).

On 2026-10-05 an outside answer on a zero-bounty ask (#558) was invisible to every keeper tool, and
the day's journal said nobody came. These laws pin what must not drift: answers on asks WITHOUT a
bounty count, our own accounts never count, only the asked day counts, an address is OUTSIDE only
with evidence, and FIRST SEEN means no earlier answer anywhere on the network.

Run: python3 specs/test_answers_by_day.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("abd", os.path.join(ROOT, "ops", "answers-by-day.py"))
abd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(abd)

UNSTUCK = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
ARION = "nano_3m8cz87zwxb1y16ob4bzp1eyek78qaig8ktohk7d45b18sh6u9exbowbnekr"
CEDAR = "nano_1rtip87co9td57n18tdq7996dsuuycotttnizprfr7nzobhabwkpyxwktxsh"
ASKER = "nano_3wxkwo5m57g8rt5zxcz3aczqaa3zt3mr444aa7b75of3m5onm9fo1bsei4wm"

ASKS = {"asks": [
    {"id": 558, "asker": ASKER, "bountyRaw": "0", "created_at": "2026-09-24T02:23:50Z", "title": "dealwork escrow"},
    {"id": 2, "asker": UNSTUCK, "bountyRaw": "1000000000000000000000000000", "created_at": "2026-09-17T00:00:00Z",
     "title": "receivable"},
    {"id": 590, "asker": UNSTUCK, "bountyRaw": "0", "created_at": "2026-10-05T09:00:00Z", "title": "our probe"},
    {"id": 591, "asker": CEDAR, "bountyRaw": "0", "created_at": "2026-10-05T10:00:00Z", "title": "a stranger asks"},
]}


def ans(i, who, at):
    return {"id": i, "answerer": who, "body": "x" * 100, "at": at}


DETAILS = {
    558: {"answers": [ans(265, UNSTUCK, "2026-09-24T02:45:00Z"), ans(316, CEDAR, "2026-10-05T06:52:29Z")]},
    2: {"answers": [ans(300, ARION, "2026-09-26T09:00:00Z"), ans(320, ARION, "2026-10-05T11:00:00Z"),
                    ans(321, UNSTUCK, "2026-10-05T12:00:00Z")]},
    590: {"answers": []},
    591: {"answers": [ans(322, CEDAR, "2026-10-05T13:00:00Z")]},
}

# challenge #128: one agent answering the same asks again and again, earlier day and same day
HERMES = "nano_1f7ezb3mgkiqjez7pdrtkj8zt174mdif39wkkccuunihjgeacxnpurp9mrf3"
REPEATS = {
    2: {"answers": [ans(300, HERMES, "2026-10-04T09:00:00Z"), ans(330, HERMES, "2026-10-05T14:05:00Z"),
                    ans(340, HERMES, "2026-10-05T17:09:00Z")]},
    558: {"answers": [ans(331, HERMES, "2026-10-05T14:06:00Z"), ans(341, HERMES, "2026-10-05T20:01:00Z")]},
    591: {"answers": [ans(332, CEDAR, "2026-10-05T13:00:00Z")]},
}


class AnswersByDay(unittest.TestCase):
    def setUp(self):
        self.r = abd.build_report("2026-10-05", ASKS, DETAILS)
        self.by_id = {a["answer"]: a for a in self.r["answers"]}

    def test_zero_bounty_ask_answer_counts(self):
        self.assertIn(316, self.by_id, "an answer on a no-bounty ask was dropped - the #558 miss")

    def test_ours_never_counted_as_not_ours(self):
        self.assertEqual(self.by_id[321]["kind"], "ours")
        self.assertEqual(self.r["totals"]["answers_not_ours"], 2)
        self.assertNotIn("#590", abd.render(self.r))

    def test_only_that_day(self):
        self.assertNotIn(265, self.by_id)
        self.assertNotIn(300, self.by_id)

    def test_outside_needs_evidence(self):
        self.assertEqual(self.by_id[320]["kind"], "outside")
        self.assertEqual(self.by_id[316]["kind"], "unclassified")

    def test_first_seen(self):
        self.assertTrue(self.by_id[316]["first_seen"])
        self.assertFalse(self.by_id[320]["first_seen"], "ARION answered on 09-26; not first seen")
        self.assertEqual(self.r["totals"]["first_seen"], 1)

    def test_asks_of_the_day(self):
        self.assertEqual(self.r["totals"]["asks"], 2)
        self.assertEqual(self.r["totals"]["asks_not_ours"], 1)
        self.assertIn("FIRST SEEN", abd.render(self.r))

    def test_self_answer_is_not_an_answer_from_anyone(self):
        # challenge #106: the asker of #587 answered its own ask; the tool said "first-seen answerer"
        self.assertTrue(self.by_id[322]["self"])
        self.assertFalse(self.by_id[322]["first_seen"])
        self.assertEqual(self.r["totals"]["answers_not_ours"], 2, "a self-answer counted as an outside answer")
        self.assertEqual(self.r["totals"]["self_answers"], 1)
        out = abd.render(self.r)
        self.assertIn("SELF", out)
        self.assertIn("by an asker on its own ask", out)
        self.assertIn("Ours: 1 asks, 1 answers.", out, "a self-answer was counted as ours")
        self.assertFalse(self.by_id[316]["self"])


class RepeatAnswers(unittest.TestCase):
    def setUp(self):
        self.r = abd.build_report("2026-10-05", ASKS, REPEATS)
        self.by_id = {a["answer"]: a for a in self.r["answers"]}

    def test_repeat_on_same_ask_flagged(self):
        self.assertTrue(self.by_id[330]["repeat"], "answered #2 on 10-04 already")
        self.assertTrue(self.by_id[340]["repeat"])
        self.assertTrue(self.by_id[341]["repeat"])
        self.assertFalse(self.by_id[331]["repeat"], "its first answer on #558")
        self.assertFalse(self.by_id[332]["repeat"])

    def test_headline_gives_distinct_pairs(self):
        t = self.r["totals"]
        self.assertEqual(t["answers_not_ours"], 4, "#332 is CEDAR on its own ask: SELF, not counted")
        self.assertEqual(t["repeats_not_ours"], 3)
        self.assertEqual(t["asks_answered_not_ours"], 2)
        out = abd.render(self.r)
        self.assertIn("3 REPEAT an answer the same agent already gave", out)
        self.assertIn("2 distinct agent-ask pairs", out)
        line = [l for l in out.splitlines() if "answer #341" in l][0]
        self.assertIn("REPEAT", line)

    def test_first_answer_on_an_ask_is_not_a_repeat(self):
        r = abd.build_report("2026-10-05", ASKS, DETAILS)
        by_id = {a["answer"]: a for a in r["answers"]}
        self.assertFalse(by_id[316]["repeat"])
        self.assertTrue(by_id[320]["repeat"], "ARION answered #2 on 09-26 already")


if __name__ == "__main__":
    unittest.main()
