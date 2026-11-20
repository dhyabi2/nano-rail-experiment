#!/usr/bin/env python3
"""Law for challenge #328: once job-20261113-001's delivery window ends, no published file may still call the job open.

Measured 00:2x UTC 2026-11-20, 24 hours before the window ends: nine published texts (bounties.txt, canon.txt,
canon.html, swap.txt, both llms.txt copies, both /ai/ HTML copies, tools.json) say the one paid job is "open until
2026-11-20 23:59 UTC" (canon.txt: "open until 11-20"; tools.json: "open_until"). The job row in paid-jobs.json says
"delivered by 2026-11-20 23:59Z". Nothing in the repository changes when that minute passes: challenge #290's law
(specs/test_seat_offer_expires.py) watches the verdict seats' clock, and every other law here compares texts with each
other, never with the clock. So at 00:00 UTC 11-21 the suite would stay green while every head - 2949 outside requests
and 263 clients on 11-19 (/ai/traffic/2026-11-19.json) - still tells a reader the job is open. This project's own rule:
"a reward you cannot actually collect is worse than no reward" (bounties.txt section 1, ONCE).

This law reads the window's end from bounties.txt section 9 itself ("THE JOB (<id>, open until <date> <hh:mm> UTC)",
never restated here), checks that every file calling the job open names that same date, and, from the minute after
the window's end, fails while any published file still calls it open. The fix it forces is a text change on that
hour: say the job closed, when, and what was paid (section 9, THE PAY) - measured, not assumed.

Run: python3 specs/test_job_offer_expires.py
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

# section 9's clock line while the job is open; from the close on it may read "closed" (history) instead
CLOCK = re.compile(r"THE JOB \((job-\d{8}-\d{3}), (?:open until|closed) (2026-\d\d-\d\d) (\d\d:\d\d) UTC\)")


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def flat(s):
    return " ".join(re.sub(r"<[^>]+>", " ", s).split())


def window_end(bounties):
    """(job id, first minute the job is no longer open) from section 9, or (None, None)."""
    m = CLOCK.search(flat(bounties))
    if not m:
        return None, None
    last = datetime.datetime.strptime(m.group(2) + " " + m.group(3), "%Y-%m-%d %H:%M").replace(
        tzinfo=datetime.timezone.utc)
    return m.group(1), last + datetime.timedelta(minutes=1)


def open_claims(text, end):
    """Phrases in `text` that call the job open, for a window whose last open minute is end - 1 min."""
    day = (end - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d")
    short = day[5:]
    low = flat(text).lower()
    patterns = (
        r"\bopen until (?:%s|%s)\b" % (re.escape(day), re.escape(short)),
        r'"open_until": "%s' % re.escape(day),
        r"\bjob is open: job-",
    )
    return [p for p in patterns if re.search(p, low)]


def stale_offers(texts, end, now):
    """{file: [claims]} for every text that still calls the job open at `now`; empty before the end."""
    if end is None or now < end:
        return {}
    out = {}
    for rel, txt in texts.items():
        hits = open_claims(txt, end)
        if hits:
            out[rel] = hits
    return out


class JobOfferExpires(unittest.TestCase):
    def setUp(self):
        self.texts = {rel: read(rel) for rel in PUBLISHED}
        self.job, self.end = window_end(self.texts["published/bounties.txt"])

    def test_section_9_states_the_window(self):
        # section 9 names one paid job; while it does, it must say when the window ends
        if "job-20261113-001" in self.texts["published/bounties.txt"]:
            self.assertIsNotNone(self.end, "section 9 names the job but has no 'THE JOB (<id>, open until ... UTC)'")

    def test_every_open_claim_names_the_same_day(self):
        if self.end is None:
            return
        day = (self.end - datetime.timedelta(minutes=1)).strftime("%Y-%m-%d")
        for rel, txt in self.texts.items():
            for m in re.finditer(r"open until (2026-\d\d-\d\d|\d\d-\d\d)\b", flat(txt).lower()):
                self.assertTrue(day.endswith(m.group(1)), "%s says open until %s, section 9 says %s"
                                % (rel, m.group(1), day))

    def test_no_file_calls_the_job_open_after_the_window(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        stale = stale_offers(self.texts, self.end, now)
        self.assertEqual(stale, {}, "%s's window ended %s; these files still call it open - say it closed, when, "
                         "and what was paid (section 9, THE PAY), measured: %s" % (self.job, self.end, stale))

    def test_guard_fires_on_todays_text_one_minute_after_the_window(self):
        # a check that cannot fail is not a check: today's heads pass at end - 1 s and are caught at end
        self.assertIsNotNone(self.end)
        self.assertEqual(stale_offers(self.texts, self.end, self.end - datetime.timedelta(seconds=1)), {})
        if datetime.datetime.now(datetime.timezone.utc) < self.end:
            caught = stale_offers(self.texts, self.end, self.end)
            self.assertEqual(set(caught), set(PUBLISHED), "every head calls the job open today, so each must be caught")

    def test_closed_wording_passes(self):
        end = datetime.datetime(2026, 11, 21, 0, 0, tzinfo=datetime.timezone.utc)
        closed = ("THE JOB (job-20261113-001, closed 2026-11-20 23:59 UTC). Its delivery window ended; "
                  "the one delivery is under our own read.")
        self.assertEqual(open_claims(closed, end), [])
        self.assertEqual(window_end(closed)[1], end)
        self.assertNotEqual(open_claims("one paid job is open until 2026-11-20 23:59 UTC", end), [])
        self.assertNotEqual(open_claims("The job is open until 11-20 (untested", end), [])


if __name__ == "__main__":
    unittest.main()
