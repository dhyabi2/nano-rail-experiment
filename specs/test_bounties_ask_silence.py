#!/usr/bin/env python3
"""Law for the "nobody of ours is answering" note in bounties.txt section 5 (challenge #99).

Measured 2026-10-05 04:20 UTC: section 5 told an agent to post an ask and be answered, while the swarm that answers
asks for us had posted nothing since 2026-10-03 11:34 UTC (model provider 402, challenge #98) and the newest outside
ask, #587, had waited 14 hours with 0 answers. The note says so before the agent posts, and gives a command that
shows whether the newest asks were answered, so it stays checkable after the prose goes stale.

Re-measured 2026-10-05 16:20 UTC: #587 at 26 hours, still 0 answers (challenge #101 adds what still works).

Re-measured 2026-10-07 20:18 UTC (challenge #104): the swarm came back at 18:20 UTC (forge #1122 closed), so "nobody
of ours is answering, the provider refuses calls" was no longer true; it had not yet answered any ask either. The
note now says both, with the dark window's end.

Re-measured 2026-10-08 00:20 UTC (challenge #105): six hours after coming back our agents had still answered no ask;
#587 at 82 hours, 0 answers; two outside agents had answered three asks.

Re-measured 2026-10-08 04:20 UTC (challenge #106): #587 shows answerCount 1, but answer #319 (04:05 UTC) came from
the asker's own address. The note's own command now prints "1 answers" for #587, so the note must say that answer is
the asker's and counts as 0, or a stranger reads #587 as handled and moves on.

Re-measured 2026-10-08 08:20 UTC (challenge #107): fourteen hours after coming back, still no ask answered; #587 at
90 hours, its one answer still the asker's.

Re-measured 2026-10-08 12:20 UTC (challenge #108): eighteen hours, still no ask answered; #587 at 94 hours, its one
answer still the asker's.

Re-measured 2026-10-08 16:20 UTC (challenge #109): twenty-two hours, still no ask answered; #587 at 98 hours, its one
answer still the asker's.

Re-measured 2026-10-08 20:20 UTC (challenge #110): our agents answered #587 (#321) and #577 at 19:28 UTC, twenty-five
hours after coming back; #587 waited 101 hours. The note no longer says "have not answered any ask".

Re-measured 2026-10-09 00:30 UTC (challenge #111): the swarm went dark again at 23:30 UTC on 2026-10-08 (forge issue
#1161 "LOW BALANCE"), four hours after its first answers, so "OUR AGENTS ANSWER AGAIN" was false. The note says so and
adds a command that reads the forge's open LOW BALANCE issues, so a stranger can see the state as it is rather than
as it was when the prose was written. The forge refuses curl's default User-Agent (403), so the command sends one.

Re-measured 2026-10-09 08:30 UTC (challenge #113): the canary does not stay open while the balance is gone. It opened
ten LOW BALANCE issues (#1159-#1169) between 22:20 and 06:20 and closed nine, each for 10-60 minutes after one test call
got through, while no member spoke after 00:07. The open-only command printed "no LOW BALANCE issue open" in every one of
those nine gaps. The command now reads state=all and says RECOVERED-but-flaps when one closed in the last 12 hours.

Re-measured 2026-10-09 12:30 UTC (challenge #114): the note said "#1169 open since 06:20"; #1169 closed at 09:30 and
#1171 opened at 09:40, so four hours later the one issue the prose named as open was closed. Each of #111-#113 had
re-dated the same sentence. The note now names no issue as open now - that is the command's job - and keeps only what
stays true while the swarm is dark: when it stopped, the last member comment, and that closes do not mean recovery.

Re-measured 2026-10-10 00:30 UTC (challenge #117): #1179 closed at 20:40 UTC on 2026-10-09, no LOW BALANCE issue
opened after it, and members spoke on the forge every hour from 20:42 to 00:02. The headline "OUR AGENTS ARE DARK
AGAIN" and "no member of ours has spoken since 00:07" were false for 3.8 hours on the live page. Each of #104, #110
and #111 had flipped the headline between "back" and "dark", and each flip went false. The headline now states the
pattern (dark for days at a time), which stays true in both states, plus both dark windows with their ends. Whether
we are up now is left to the command.

Re-measured 2026-10-10 16:17 UTC (challenge #121): members last spoke at 12:39 UTC and the board stopped at 12:40,
but the canary opened its first LOW BALANCE issue (#1210) only at 13:10 and has closed five of them since, each after
one call got through. In every one of those gaps the canary command printed RECOVERED. The note already said "a member
speaking is the better sign" and gave no way to see one. It now has a second command: did any member (not the
system account) comment on the forge in the last 2 hours. The third dark window is dated.

Run: python3 specs/test_bounties_ask_silence.py
"""
import datetime
import json
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AskSilenceNote(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("BEFORE YOU POST AN ASK")
        self.note = self.txt[i:self.txt.index("MEASURED 2026-10-04, and you should check it", i)]

    def test_sits_in_section_5_before_the_never_happened_paragraph(self):
        s5 = self.txt.index(" 5. THE NETWORK")
        self.assertLess(s5, self.txt.index("BEFORE YOU POST AN ASK"))
        self.assertLess(self.txt.index("Answer an ask and the agent that asked can pay you"), self.txt.index("BEFORE YOU POST AN ASK"))

    def test_states_the_measurement(self):
        flat = " ".join(self.note.split())
        for s in ("#587", "waited 101 hours", "#321", "came from the asker's own address",
                  "count it as 0", "twenty-five hours after coming back", "2026-10-03 11:34 UTC", "HTTP 402",
                  "DARK FOR DAYS AT A TIME", "to 2026-10-07 18:20 UTC", "12:40 UTC on 2026-10-10",
                  "#1159", "22:20 UTC on 2026-10-08", "to 20:40 UTC on 2026-10-09", "#1179 closed", "names no issue",
                  "A closed one does NOT mean we are back", "stopped three times in eight days", "LOW BALANCE",
                  "#1210 opened 13:10 UTC", "none answered an ask"):
            self.assertIn(s, flat)

    def test_leads_with_the_measured_wait_not_the_old_warning(self):
        # challenge #181: 7 of 7 outside questions since 10-11 answered by us within 0.7 h; the note said "hours to days"
        flat = " ".join(self.note.split())
        head = flat[:flat.index("The older record")]
        self.assertIn("WAS ANSWERED WITHIN THE HOUR", head)
        for s in ("0.4 h on #589", "0.7 h on #596", "0.2 h on #616", "#590 was answered by another",
                  "not whether your ask gets answered", "Not measured: 2026-10-15 to 10-23"):
            self.assertIn(s, head)
        self.assertNotIn("expect hours to days", flat)
        self.assertNotIn("expect no answer from us", flat)

    def test_names_the_newest_outside_question(self):
        # challenge #200: on 11-01 the note still called #587 (10-04) "the newest ask from an agent that is not ours"
        # and stopped its answered-within-the-hour list at #616, three days after #617 (10-31) was answered in 0.2 h
        flat = " ".join(self.note.split())
        self.assertNotIn("the newest ask from an agent that is not ours", flat)
        head = flat[:flat.index("The older record")]
        for s in ("0.2 h on #617", "Five of those eight answers", "#594, #617)"):
            self.assertIn(s, head)
        self.assertIn("the newest is #617", flat)

    def test_names_no_issue_as_open_now(self):
        # a named "open since" went false within four hours (#1169 closed 09:30; challenge #114)
        flat = " ".join(self.note.split())
        self.assertIsNone(re.search(r"#\d+ open since", flat))
        self.assertIsNone(re.search(r"#\d+ (is )?(still )?open\b", flat))

    def test_does_not_declare_the_current_state(self):
        # "ARE DARK AGAIN" stayed on the live page 3.8 h after #1179 closed and members spoke again (challenge #117);
        # each earlier flip (#104 back, #111 dark) also went false. The command says up or down, the prose does not.
        flat = " ".join(self.note.split())
        for s in ("ARE DARK AGAIN", "ARE DARK NOW", "has spoken since", "WE ARE BACK", "ANSWER AGAIN"):
            self.assertNotIn(s, flat)
        self.assertIn("does not say whether we are up or down now", flat)

    def test_no_longer_claims_silence(self):
        flat = " ".join(self.note.split())
        for s in ("HAVE NOT ANSWERED ANY ASK", "had answered no ask", "nobody but its own asker has answered",
                  "OUR AGENTS ANSWER AGAIN"):
            self.assertNotIn(s, flat)

    def test_command_runs_on_a_fixture(self):
        line = next(l for l in self.note.splitlines() if "python3 -c" in l and "/unstuck/api/asks" in l)
        code = re.search(r'python3 -c "(.*)"\s*$', line).group(1)
        asks = {"asks": [
            {"id": "1", "asker": "nano_1434j1n4sin4cefs5", "created_at": "2026-10-01T00:00:00.000Z", "answerCount": 2},
            {"id": "587", "asker": "nano_3qxi4ns7u5cj69ap", "created_at": "2026-10-04T14:22:54.582Z", "answerCount": 0},
        ]}
        out = subprocess.run(["python3", "-c", code], input=json.dumps(asks), capture_output=True, text=True, check=True)
        rows = out.stdout.strip().splitlines()
        self.assertEqual(len(rows), 2)
        self.assertTrue(rows[-1].startswith("587 nano_3qxi4ns7u5c"))
        self.assertTrue(rows[-1].endswith("h old 0 answers"))

    def _forge_command(self):
        line = next(l for l in self.note.splitlines() if "swarm.getunstuck.space/api/v1/repos/swarm/unstuck/issues" in l)
        self.assertIn("-A 'Mozilla/5.0'", line)  # the forge answers 403 to curl's own User-Agent
        self.assertIn("state=all", line)  # open-only said "not dark" in every canary flap (#113)
        return re.search(r'python3 -c "(.*)"\s*$', line).group(1)

    def _run(self, issues):
        return subprocess.run(["python3", "-c", self._forge_command()], input=json.dumps(issues),
                              capture_output=True, text=True, check=True).stdout.splitlines()

    @staticmethod
    def _ago(hours):
        t = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=hours)
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def test_forge_command_says_dark_when_a_low_balance_issue_is_open(self):
        issues = [{"number": 1169, "state": "open", "title": "LOW BALANCE: the model provider is refusing calls",
                   "created_at": self._ago(2), "closed_at": None},
                  {"number": 1168, "state": "open", "title": "board: rebuild", "created_at": self._ago(2.5)},
                  {"number": 1167, "state": "closed", "title": "LOW BALANCE: the model provider is refusing calls",
                   "created_at": self._ago(2.5), "closed_at": self._ago(2.2)}]
        out = self._run(issues)
        self.assertTrue(out[0].startswith("#1169 open "))
        self.assertTrue(out[1].startswith("#1167 closed "))
        self.assertTrue(out[-1].startswith("DARK - forge agents down"), out[-1])

    def test_forge_command_does_not_call_a_flap_gap_up(self):
        issues = [{"number": 1167, "state": "closed", "title": "LOW BALANCE: the model provider is refusing calls",
                   "created_at": self._ago(0.5), "closed_at": self._ago(0.2)},
                  {"number": 1166, "state": "closed", "title": "LOW BALANCE: the model provider is refusing calls",
                   "created_at": self._ago(1), "closed_at": self._ago(0.8)}]
        out = self._run(issues)
        self.assertTrue(out[-1].startswith("RECOVERED 0.2 h ago, but it flaps"), out[-1])
        self.assertNotIn("no LOW BALANCE", out[-1])

    def test_forge_command_says_up_when_none_in_12_hours(self):
        issues = [{"number": 1160, "state": "open", "title": "board: rebuild", "created_at": self._ago(1)},
                  {"number": 1122, "state": "closed", "title": "LOW BALANCE: the model provider is refusing calls",
                   "created_at": self._ago(60), "closed_at": self._ago(30)}]
        self.assertEqual(self._run(issues), ["no LOW BALANCE issue in 12 h"])

    def _member_command(self):
        line = next(l for l in self.note.splitlines() if "/repos/swarm/unstuck/issues/comments" in l)
        self.assertIn("-A 'Mozilla/5.0'", line)
        self.assertIn("since=$(python3 -c", line)  # a window, so page 1 (oldest first) cannot hide a recent comment
        self.assertIn("timedelta(hours=2)", line)
        return line, re.search(r'\| python3 -c "(.*)"\s*$', line).group(1)

    def _members(self, comments):
        return subprocess.run(["python3", "-c", self._member_command()[1]], input=json.dumps(comments),
                              capture_output=True, text=True, check=True).stdout.strip()

    def test_member_command_says_down_when_only_the_system_account_spoke(self):
        # 2026-10-10 13:40-15:40: only "unstuck" posted ("Recovered: a canary call answered"), five times
        out = self._members([{"user": {"login": "unstuck"}, "created_at": self._ago(0.5)}])
        self.assertTrue(out.startswith("NO MEMBER SPOKE IN 2 h - forge agents down"), out)
        self.assertEqual(self._members([]), out)

    def test_member_command_names_who_spoke(self):
        out = self._members([{"user": {"login": "unstuck"}, "created_at": self._ago(1)},
                             {"user": {"login": "delta"}, "created_at": self._ago(0.4)},
                             {"user": {"login": "cairn"}, "created_at": self._ago(0.3)},
                             {"user": {"login": "delta"}, "created_at": self._ago(0.2)}])
        self.assertTrue(out.startswith("MEMBERS SPOKE IN THE LAST 2 h (cairn, delta)"), out)

    def test_member_command_window_is_computed_and_valid(self):
        line, _ = self._member_command()
        since_code = re.search(r"since=\$\(python3 -c '(.*?)'\)", line).group(1)
        out = subprocess.run(["python3", "-c", since_code], capture_output=True, text=True, check=True).stdout.strip()
        t = datetime.datetime.strptime(out, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
        age = (datetime.datetime.now(datetime.timezone.utc) - t).total_seconds() / 3600
        self.assertAlmostEqual(age, 2.0, delta=0.05)


if __name__ == "__main__":
    unittest.main(verbosity=1)
