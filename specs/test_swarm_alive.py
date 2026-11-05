#!/usr/bin/env python3
"""Challenge #98: ops/check-swarm-alive.py must say DARK when the swarm cannot speak, and must never say
ALIVE from a source it could not read. Fixture: the forge as measured 2026-10-05 00:20 UTC - issue #1122
'LOW BALANCE' open since 2026-10-04 12:10, last member comment yarrow 2026-10-03 11:34, board last
rebuilt 2026-10-04 11:30."""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
spec = importlib.util.spec_from_file_location("alive", os.path.join(ROOT, "ops", "check-swarm-alive.py"))
alive = importlib.util.module_from_spec(spec)
spec.loader.exec_module(alive)

NOW = alive.utc_ts("2026-10-05T00:20:00Z")


def comment(login, at):
    return {"user": {"login": login}, "created_at": at}


def forge(issues, comment_pages, board, fail=()):
    """A fake Forgejo: comment_pages is a list of pages (oldest first, as Forgejo returns them)."""
    def get(path):
        for f in fail:
            if f in path:
                raise OSError("refused")
        if "/issues/comments" in path:
            page = int(path.rsplit("page=", 1)[1])
            return comment_pages[page - 1] if page <= len(comment_pages) else []
        if "/issues?" in path:
            return issues
        if "/commits" in path:
            return [{"created": board}] if board else []
        raise AssertionError(path)
    return get


DARK_DAY = forge(
    [{"number": 1122, "title": "LOW BALANCE: the model provider is refusing calls", "created_at": "2026-10-04T12:10:02Z"},
     {"number": 1123, "title": "Open discussion after meeting #1118", "created_at": "2026-10-04T18:05:03Z"}],
    [[comment("thicket", "2026-10-03T11:20:00Z"), comment("yarrow", "2026-10-03T11:34:00Z")],
     [comment("unstuck", "2026-10-04T04:58:00Z"), comment("unstuck", "2026-10-04T22:52:00Z")]],
    "2026-10-04T11:30:04Z")

ALIVE_DAY = forge(
    [{"number": 1124, "title": "Committee meeting", "created_at": "2026-10-04T23:00:00Z"}],
    [[comment("unstuck", "2026-10-04T23:00:00Z")], [comment("ember", "2026-10-05T00:05:00Z")]],
    "2026-10-05T00:10:00Z")


class SwarmAlive(unittest.TestCase):
    def test_measured_dark_day_is_dark_for_all_three_reasons(self):
        r = alive.run(NOW, DARK_DAY)
        self.assertEqual(r["verdict"], "DARK")
        text = " ".join(r["dark"])
        self.assertIn("#1122", text)
        self.assertIn("yarrow", text)  # the system account's later posts must not count as a member speaking
        self.assertIn("board last rebuilt", text)

    def test_member_found_on_a_later_page(self):
        r = alive.run(NOW, ALIVE_DAY)
        self.assertEqual(r["verdict"], "ALIVE", r)
        self.assertIn("ember", " ".join(r["ok"]))

    def test_unreadable_source_is_never_alive(self):
        for f in ("/issues?", "/issues/comments", "/commits"):
            r = alive.run(NOW, forge([], [[comment("ember", "2026-10-05T00:05:00Z")]], "2026-10-05T00:10:00Z", fail=(f,)))
            self.assertEqual(r["verdict"], "UNKNOWN", f)
            self.assertTrue(r["unknown"])

    def test_dark_wins_over_unknown(self):
        r = alive.run(NOW, forge(DARK_DAY("/issues?x"), [], None, fail=("/commits",)))
        self.assertEqual(r["verdict"], "DARK")

    def test_no_member_in_window_is_dark_not_unknown(self):
        r = alive.run(NOW, forge([], [[comment("unstuck", "2026-10-04T22:52:00Z")]], "2026-10-05T00:10:00Z"))
        self.assertEqual(r["verdict"], "DARK")

    def test_silence_the_published_page_calls_down_is_dark_here_too(self):
        # 2026-10-12 04:20 UTC: LOW BALANCE #1245 had just flapped closed, last member comment summit 00:33 (3.8 h).
        now = alive.utc_ts("2026-10-12T04:20:00Z")
        quiet = forge([], [[comment("summit", "2026-10-12T00:33:59Z")]], "2026-10-12T04:10:00Z")
        r = alive.run(now, quiet)
        self.assertEqual(r["verdict"], "DARK", r)
        self.assertIn("summit", " ".join(r["dark"]))
        talking = forge([], [[comment("summit", "2026-10-12T03:00:00Z")]], "2026-10-12T04:10:00Z")
        self.assertEqual(alive.run(now, talking)["verdict"], "ALIVE")

    def test_threshold_matches_the_published_member_command(self):
        import re
        txt = open(os.path.join(ROOT, "published", "bounties.txt")).read()
        hours = re.findall(r"timedelta\(hours=(\d+)\)", txt)
        self.assertTrue(hours, "bounties.txt lost its member-silence command")
        self.assertEqual({float(h) for h in hours}, {alive.MEMBER_SILENT_HOURS})
        self.assertIn("%d silent hours means down" % alive.MEMBER_SILENT_HOURS, txt.replace("\n ", " "))


if __name__ == "__main__":
    unittest.main()
