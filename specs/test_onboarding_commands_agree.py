#!/usr/bin/env python3
"""Oracle: the six onboarding commands must agree across every published surface, and none may be a
bash comment.

Why this exists. Challenge #54 found and fixed exactly one bug: aidirectory.html's step 6 was a bash
COMMENT ("# publish your price at ... and tell us: ...") rather than a runnable command - pasted
verbatim it does nothing, and it disagreed with bounties.txt's own step 6. Commit 5506a57 fixed it to
`curl -s 'https://extract.paypercall.dev/api/v1/nano-info'`, matching bounties.txt.

Commit 1df4b08 (six commits later, "a disclosed 'Built by us' section") silently REVERTED that fix -
aidirectory.html's step 6 went back to being the same bash comment - while adding an unrelated section
in the same diff. Challenge #59 caught a SIBLING regression from that identical commit (it deleted the
whole onboarding block from aidirectory-llms.txt) and restored it, but nobody re-checked aidirectory.html
itself for the same shape of damage, so the HTML step 6 - and published/aidirectory/tools.json's
onboarding[5], which was apparently never fixed to begin with - stayed broken through five further PRs
(#13 through #21) with nothing to notice it, because no check compared the surfaces to each other.

Measured before this run's fix: aidirectory.html and aidirectory/index.html (byte-identical) and
aidirectory/tools.json all carried the bash-comment step 6; only aidirectory-llms.txt and
aidirectory/llms.txt (both restored by #59) had the real curl command. The page's own text tells an
agent "Do not parse this page. Two feeds carry the same data, generated from the same source" - which
was false: the JSON feed it names first was one of the three still broken.

This test derives nothing clever - it just extracts each surface's own six command strings and asserts
they are identical across every surface, and that none of them starts with a bash comment marker. A
future edit that changes one copy and not its siblings fails loudly here instead of drifting silently
for eleven commits again.

    python3 specs/test_onboarding_commands_agree.py
"""
import json
import re
import sys

REPO = __file__.rsplit("/specs/", 1)[0]

HTML_STEP_RE = re.compile(
    r'<span class="num">(\d)</span><b>[^<]*</b></div><pre><code>(.*?)</code></pre>', re.S)
LLMS_STEP_RE = re.compile(
    r'^### (\d)\. .*?\n((?:    .*\n?)+)', re.M)


def unescape_html(s):
    return (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
             .replace("&#x27;", "'").replace("&quot;", '"'))


def commands_from_html(path):
    html = open(path, encoding="utf-8").read()
    return {n: unescape_html(cmd.strip()) for n, cmd in HTML_STEP_RE.findall(html)}


def commands_from_llms(path):
    text = open(path, encoding="utf-8").read()
    out = {}
    for n, block in LLMS_STEP_RE.findall(text):
        # the command is the first indented line; a wrapped "You get:" paragraph is not indented
        first_line = block.strip("\n").splitlines()[0].strip()
        out[n] = first_line
    return out


def commands_from_tools_json(path):
    d = json.load(open(path, encoding="utf-8"))
    return {item["n"]: item["cmd"].strip() for item in d.get("onboarding", [])}


def main():
    surfaces = {
        "aidirectory.html": commands_from_html(f"{REPO}/published/aidirectory.html"),
        "aidirectory/index.html": commands_from_html(f"{REPO}/published/aidirectory/index.html"),
        "aidirectory-llms.txt": commands_from_llms(f"{REPO}/published/aidirectory-llms.txt"),
        "aidirectory/llms.txt": commands_from_llms(f"{REPO}/published/aidirectory/llms.txt"),
        "aidirectory/tools.json": commands_from_tools_json(f"{REPO}/published/aidirectory/tools.json"),
    }

    problems = []
    for name, cmds in surfaces.items():
        if len(cmds) != 6:
            problems.append(f"{name}: found {len(cmds)} onboarding steps, expected 6 ({sorted(cmds)})")

    # every surface's step N must agree with every other surface's step N
    for n in [str(i) for i in range(1, 7)]:
        values = {name: cmds.get(n) for name, cmds in surfaces.items() if n in cmds}
        distinct = set(values.values())
        if len(distinct) > 1:
            problems.append(f"step {n}: surfaces disagree -")
            for name, v in values.items():
                problems.append(f"    {name}: {v!r}")
        for name, v in values.items():
            if v is not None and v.lstrip().startswith("#"):
                problems.append(f"{name} step {n}: command is a bash COMMENT, not runnable: {v!r}")

    if problems:
        print(f"FAIL: {len(problems)} problem(s)")
        for p in problems:
            print(" -", p)
        return 1
    print("PASS: all six onboarding commands agree across every published surface, none is a comment")
    return 0


if __name__ == "__main__":
    sys.exit(main())
