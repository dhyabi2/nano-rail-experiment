#!/usr/bin/env python3
"""Law for challenge #234: nothing in this repository runs on GitHub Actions (owner rule, 2026-11-07).

The owner deleted outage-watch.yml and second-node.yml at 20:48 UTC 11-07 ("owner rule: no GitHub Actions"). Four
laws still opened those files, so the whole suite failed and no keeper PR could be merged. This law keeps the rule:
no workflow file comes back, and ROUTINES.md and bounties.txt do not say a probe is still re-run on GitHub's runners.

Run: python3 specs/test_no_github_actions.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class NoGitHubActions(unittest.TestCase):
    def test_no_workflow_file(self):
        wf = os.path.join(ROOT, ".github", "workflows")
        files = sorted(os.listdir(wf)) if os.path.isdir(wf) else []
        self.assertEqual(files, [], "owner rule 2026-11-07: no GitHub Actions workflow")

    def test_routines_schedules_nothing_on_github(self):
        txt = open(os.path.join(ROOT, "ROUTINES.md")).read()
        self.assertNotIn("## On GitHub's runners", txt)
        self.assertIn("Nothing runs on GitHub Actions", txt)

    def test_bounties_does_not_claim_a_rerun(self):
        txt = open(os.path.join(ROOT, "published", "bounties.txt")).read()
        step4 = txt[txt.index(" STEP 4 - PROVE"):txt.index(" STEP 5 - TRY")]
        self.assertNotIn("run on GitHub's runners", step4)
        self.assertIn("nothing re-runs it now", step4)


if __name__ == "__main__":
    unittest.main()
