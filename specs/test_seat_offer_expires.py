#!/usr/bin/env python3
"""Law for challenge #290: once the verdict clock of job-20261113-001 ends, no published file may still offer the seats.

Measured 04:2x UTC 2026-11-16, 39 hours before the clock ends: seven published texts (bounties.txt, canon.txt,
canon.html, swap.txt, both llms.txt copies, both /ai/ HTML copies, tools.json) say the paid work open now is three
verdict seats, "until 2026-11-17 19:28:13 UTC". The panel's rule (bounties.txt section 9, the job rows' "published
within 72 hours of the delivery") pays no verdict published after that minute. Nothing in the repository changes when
the minute passes: every law here compares texts with each other, never with the clock, so on 11-17 at 19:29 UTC the
suite stays green while each head still sends readers - 503 outside requests by 03:40 UTC on 11-16, ask 628 read by
19 clients - to do work that is no longer paid. This project's own rule is that "a reward you cannot actually collect
is worse than no reward" (section 1, ONCE).

This law reads the close from section 9 itself (never restated here), checks that every file that offers the seats
names that same close, and, from the close on, fails while any published file still claims the seats are open. The
fix it forces is a text change on the hour the clock ends: say the seats closed, how many verdicts came, and what the
rule does next (the row is published as undecided and we read the delivery ourselves - section 9, THE PAY).

Run: python3 specs/test_seat_offer_expires.py
"""
import datetime
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PUBLISHED = (
    "published/bounties.txt",
    "published/canon.txt",
    "published/canon.html",
    "published/swap.txt",
    "published/aidirectory/llms.txt",
    "published/aidirectory-llms.txt",
    "published/aidirectory/index.html",
    "published/aidirectory.html",
    "published/aidirectory/tools.json",
)

# Phrases that say the seats can still be taken. A file may still NAME the seats after the close (as history);
# it may not say they are open, give a live count of them, or give the close as a future limit.
OPEN_CLAIMS = (
    r"paid work,? (still )?open now",
    r"\b9\. paid work, open now",
    r"\b\d of 3 (seats )?taken\b",
    r"seats are (still )?open",
    r"verdicts (are taken )?until 2026-\d\d-\d\d \d\d:\d\d",
    r"open until 2026-\d\d-\d\d \d\d:\d\d( utc)?,? (and )?a seat",
    r"so the paid work (still open|left) is",
)


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def close_of(bounties):
    """The verdict close as section 9 states it ("Verdicts are taken until <date> <time> UTC"), as an aware datetime."""
    m = re.search(r"Verdicts are taken until (2026-\d\d-\d\d) (\d\d:\d\d:\d\d) UTC", flat(bounties))
    if not m:
        return None
    return datetime.datetime.strptime(m.group(1) + " " + m.group(2), "%Y-%m-%d %H:%M:%S").replace(
        tzinfo=datetime.timezone.utc)


def open_claims(text):
    low = flat(text).lower()
    return [p for p in OPEN_CLAIMS if re.search(p, low)]


def stale_offers(texts, close, now):
    """{file: [claims]} for every text that still offers the seats at `now`; empty before the close."""
    if close is None or now < close:
        return {}
    out = {}
    for rel, txt in texts.items():
        hits = open_claims(txt)
        if hits:
            out[rel] = hits
    return out


class SeatOfferExpires(unittest.TestCase):
    def setUp(self):
        self.texts = {rel: read(rel) for rel in PUBLISHED}
        self.close = close_of(self.texts["published/bounties.txt"])

    def test_section_9_states_the_close(self):
        # While section 9 offers seats it must say when they end; a removed clock line ends this law with it.
        if open_claims(self.texts["published/bounties.txt"]):
            self.assertIsNotNone(self.close, "section 9 offers seats but no 'Verdicts are taken until ... UTC' line")

    def test_every_offer_names_the_same_close(self):
        if self.close is None:
            return
        day_min = self.close.strftime("%Y-%m-%d %H:%M")
        for rel, txt in self.texts.items():
            if open_claims(txt):
                self.assertIn(day_min, flat(txt), "%s offers the seats but does not name the close %s" % (rel, day_min))

    def test_no_file_offers_the_seats_after_the_close(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        stale = stale_offers(self.texts, self.close, now)
        self.assertEqual(stale, {}, "the verdict clock ended %s; these files still offer the seats - say they "
                         "closed and what happens next (section 9, THE PAY): %s" % (self.close, stale))

    def test_guard_fires_on_todays_text_one_second_after_the_close(self):
        # A check that cannot fail is not a check: today's heads must be caught at close + 1 s and pass at close - 1 s.
        self.assertIsNotNone(self.close)
        before = stale_offers(self.texts, self.close, self.close - datetime.timedelta(seconds=1))
        after = stale_offers(self.texts, self.close, self.close + datetime.timedelta(seconds=1))
        self.assertEqual(before, {})
        if datetime.datetime.now(datetime.timezone.utc) < self.close:
            self.assertEqual(set(after), set(PUBLISHED), "every head offers the seats today, so each must be caught")

    def test_closed_wording_passes(self):
        closed = ("THE VERDICTS CLOSED at 2026-11-17 19:28:13 UTC with 0 verdicts. The row is published as "
                  "undecided, the silent seats are named, and we read the delivery ourselves.")
        self.assertEqual(open_claims(closed), [])
        self.assertEqual(open_claims("names no issue as open now"), [])


if __name__ == "__main__":
    unittest.main()
