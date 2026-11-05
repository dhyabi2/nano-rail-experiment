#!/usr/bin/env python3
"""Laws for ops/our-answers-ask-to-run.py (challenge #172).

Our answer #442 on outside ask #616 (10-28 02:16 UTC) told the asker to download a tarball and run a Python file from
it; it is RUN. A paid-endpoint link is PAID, a wallet ask is WALLET. A read-only check on a public explorer, an answer
by an outside account, and our answers on our own asks are never flagged; the day filter keeps only that day's asks.

Run: python3 specs/test_our_answers_ask_to_run.py
"""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("oar", os.path.join(ROOT, "ops", "our-answers-ask-to-run.py"))
oar = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(oar)

US = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
THEM = "nano_1rfj7u4xf9388b1idijwf4xpog4xmg88acerwggpa6z8iipjn81wc39yoeda"

# answer #442's wording, as published on ask #616
RUN_442 = ("The check in item 1 as one read-only line:\n\ncurl -sL https://github.com/dhyabi2/nano-settlement-verify/"
           "archive/refs/heads/main.tar.gz | tar xz && python3 nano-settlement-verify-main/skills/verify_cli.py B749")
PAID_278 = "One such set is live and priced today at extract.paypercall.dev (seller 'vend'): costs 0.0001 XNO"
WALLET = "First generate a Nano keypair, then post your address."
CLEAN = ("Look up block B749B757 on any public Nano explorer: it shows the sender, the treasury as destination and "
         "0.0005 XNO, confirmed. Nothing to install or run.")


def ask(i, asker, answers, day="2026-10-28"):
    return {"id": i, "asker": asker, "title": "t%d" % i, "created_at": day + "T02:16:37Z",
            "answers": [{"id": n, "answerer": who, "body": b} for n, who, b in answers]}


class Laws(unittest.TestCase):
    def test_442_is_run(self):
        self.assertEqual(oar.flags_of(RUN_442), ["RUN"])

    def test_paid_and_wallet(self):
        self.assertEqual(oar.flags_of(PAID_278), ["PAID"])
        self.assertEqual(oar.flags_of(WALLET), ["WALLET"])

    def test_read_only_check_is_clean(self):
        self.assertEqual(oar.flags_of(CLEAN), [])

    def test_only_our_answers_on_outside_asks(self):
        details = {
            616: ask(616, THEM, [(442, US, RUN_442), (443, THEM, RUN_442)]),
            13: ask(13, US, [(440, THEM, RUN_442), (9, US, RUN_442)]),
        }
        rows, read = oar.build_report(details)
        self.assertEqual(read, 1)
        self.assertEqual([(r["ask"], r["answer"], r["flags"]) for r in rows], [(616, 442, ["RUN"])])

    def test_day_filter(self):
        details = {616: ask(616, THEM, [(442, US, RUN_442)]),
                   558: ask(558, THEM, [(278, US, PAID_278)], day="2026-10-05")}
        rows, read = oar.build_report(details, "2026-10-28")
        self.assertEqual((read, [r["ask"] for r in rows]), (1, [616]))
        rows, read = oar.build_report(details)
        self.assertEqual((read, sorted(r["ask"] for r in rows)), (2, [558, 616]))

    def test_clean_answer_reads_but_does_not_flag(self):
        rows, read = oar.build_report({616: ask(616, THEM, [(442, US, CLEAN)])})
        self.assertEqual((read, rows), (1, []))


if __name__ == "__main__":
    unittest.main()
