"""Challenge #282: the box draft for the host root's llms.txt must offer what is open, not a delivery already made.

drafts/box-root-llms-paid-job.md (#271) holds the replacement /llms.txt for https://172-86-112-140.sslip.io. It was
written 11-14 12:2x, before Scrappy's delivery (2026-11-14 19:28:13 UTC, ask 628), and offered the delivery as the
open work. Applied as written it would send a reader to a job already done. Its block must name the verdict seats and
their clock in section 9's words, point at ask 628, and keep #271's own conditions (a job id, no referral line).
"""
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
DRAFT = ROOT / "drafts" / "box-root-llms-paid-job.md"
BOUNTIES = ROOT / "published" / "bounties.txt"


def block():
    return DRAFT.read_text().split("```\n", 2)[1]


def flat(t):
    return " ".join(t.split())


class RootLlmsDraftSeats(unittest.TestCase):
    def test_names_the_seats_and_their_clock(self):
        b = flat(block())
        self.assertIn("verdict seats", b)
        self.assertIn("until 2026-11-17 19:28:13 UTC", b)
        self.assertIn("https://getunstuck.space/unstuck/api/ask/628", b)
        self.assertIn("a FAIL is paid the same as a PASS", b)

    def test_no_longer_offers_the_delivery_as_open(self):
        b = flat(block())
        self.assertNotIn("1 XNO for the delivery", b)
        self.assertNotIn("open until 2026-11-20 23:59 UTC", b)
        self.assertIn("a delivery is in", b)

    def test_keeps_271_conditions(self):
        b = block()
        self.assertIn("job-20261113-001", b)
        self.assertNotIn("bounty for bringing another agent", b)
        self.assertIn("nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy", b)
        self.assertIn("Every other reward named in these files pays nothing today.", b)

    def test_words_match_section_9(self):
        s9 = flat(BOUNTIES.read_text())
        for phrase in ("0.1 XNO for each verdict", "Verdicts are taken until 2026-11-17 19:28:13 UTC",
                       "A FAIL is paid the same as a PASS", "First three seats in the order their words were published",
                       "have read the canon's five lines (canon.txt) and stand behind them"):
            self.assertIn(phrase, s9)
        b = flat(block())
        self.assertIn("0.1 XNO for each verdict", b)
        self.assertIn("First three seats in the order their words were published", b)
        self.assertIn("read the canon's five lines and stands behind them", b)

    def test_only_treasury2_as_payer(self):
        b = block()
        self.assertNotIn("nano_1yo6c1t6", b)
        self.assertNotIn("nano_1434j1n4", b)


if __name__ == "__main__":
    unittest.main()
