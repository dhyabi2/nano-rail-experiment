#!/usr/bin/env python3
"""Laws for STEP 6 of the onboarding ("spend it on something real"), in every copy we publish.

This exact step regressed once already (challenge #54, fixed in commit 5506a57): a bash comment
("# publish your price at /.well-known/x402 and tell us: ...") instead of a runnable command. An
unrelated commit (1df4b08, "a disclosed 'Built by us' section...") silently reintroduced the same
broken comment into aidirectory.html, aidirectory/index.html and aidirectory/tools.json while
touching a different section of the same files - the two llms.txt copies were untouched by that
commit and kept the fix, which is how the regression was caught: the copies disagreed.

Run: python3 specs/test_onboarding_step6.py
"""
import html
import json
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
HTML_COPIES = ["aidirectory.html", "aidirectory/index.html"]
LLMS_COPIES = ["aidirectory-llms.txt", "aidirectory/llms.txt"]


def step6_commands():
    """(where, command) for every published copy of step 6."""
    out = []
    with open(os.path.join(PUB, "bounties.txt")) as f:
        txt = f.read()
    i = txt.index("STEP 6 - ")
    block = txt[i:txt.index("---", i)]
    lines = [ln.strip() for ln in block.splitlines() if "extract.paypercall.dev" in ln]
    out.append(("bounties.txt", lines[0] if lines else ""))
    for rel in HTML_COPIES:
        with open(os.path.join(PUB, rel)) as f:
            page = f.read()
        m = re.search(r'<span class="num">6</span>.*?<pre><code>(.*?)</code></pre>', page, re.S)
        out.append((rel, html.unescape(m.group(1))))
    for rel in LLMS_COPIES:
        with open(os.path.join(PUB, rel)) as f:
            txt = f.read()
        i = txt.index("### 6.")
        line = next(ln for ln in txt[i:].splitlines()[1:] if ln.strip())
        out.append((rel, line.strip()))
    with open(os.path.join(PUB, "aidirectory", "tools.json")) as f:
        out.append(("aidirectory/tools.json", json.load(f)["onboarding"][5]["cmd"]))
    return out


class StaticLaws(unittest.TestCase):
    def test_every_copy_found(self):
        cmds = step6_commands()
        self.assertEqual(len(cmds), 1 + len(HTML_COPIES) + len(LLMS_COPIES) + 1)
        for where, cmd in cmds:
            self.assertTrue(cmd, where)

    def test_no_copy_is_a_comment(self):
        # A bash comment is not a command: pasted verbatim it does nothing, and it cannot fail,
        # so it proves nothing was ever "run" to produce it - challenge #54's exact finding.
        for where, cmd in step6_commands():
            self.assertFalse(cmd.lstrip().startswith("#"), where)

    def test_every_copy_names_the_real_endpoint(self):
        # bounties.txt lists the bare URL (it also lists four sibling endpoints on the next
        # lines); every other copy gives a runnable `curl` command. Both are fine - a comment is not.
        for where, cmd in step6_commands():
            self.assertIn("extract.paypercall.dev/api/v1/nano-info", cmd, where)

    def test_html_and_llms_and_json_copies_agree(self):
        # bounties.txt's format legitimately differs (a bare URL, not a curl command); the other
        # five copies all render the same one-line onboarding step and must say the same thing.
        cmds = {where: cmd for where, cmd in step6_commands() if where != "bounties.txt"}
        self.assertEqual(len(set(cmds.values())), 1, cmds)


if __name__ == "__main__":
    unittest.main(verbosity=2)
