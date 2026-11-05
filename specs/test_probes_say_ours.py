"""Challenge #207. Our own probes must say they are ours.

The hourly outage watch runs on GitHub's runners, a new address each hour, and fetched the canon, bounties, swap,
asks and AiDirectory pages with a plain Chrome User-Agent. The box's traffic file counts any address that is not one of
the swarm's three boxes as outside, so each run read as one more outside browser on exactly the paths duty 3 uses to
decide whether anybody came (11-02: deploy-status.json, which only our tools read, had 20 "outside" clients).

Law: every ops/ tool that sends an HTTP request sends the one marked User-Agent below, so the box can count it as ours.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARK = "unowned-rail-probe/1"
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 " + MARK


class ProbesSayOurs(unittest.TestCase):
    def test_every_fetching_tool_sends_the_marked_user_agent(self):
        fetchers = 0
        for f in sorted((ROOT / "ops").glob("*.py")):
            s = f.read_text()
            if "urllib.request.Request(" not in s:
                continue
            fetchers += 1
            uas = re.findall(r'^UA = "([^"\n]*)"', s, re.M)
            self.assertEqual(uas, [UA], "%s: UA constant must be the marked one" % f.name)
            for h in re.findall(r'"User-Agent":\s*([^,}]+)', s):
                self.assertEqual(h.strip(), "UA", "%s sends a User-Agent other than UA: %s" % (f.name, h))
        self.assertGreaterEqual(fetchers, 10)

    def test_the_box_draft_names_the_same_mark(self):
        d = (ROOT / "drafts" / "box-count-our-probes.md").read_text()
        self.assertIn(MARK, d)


if __name__ == "__main__":
    unittest.main()
