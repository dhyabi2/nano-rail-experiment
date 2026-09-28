#!/usr/bin/env python3
"""Laws for STEP 1 of the onboarding ("a wallet, in one line"), in every copy we publish.

Found by the zero-to-first-payment test on 2026-09-28: the command as published could not run. nanocurrency 2.x has
no init() (TypeError: n.init is not a function), and a module installed with `npm i -g` is not visible to require()
from the agent's own directory (Cannot find module 'nanocurrency'). Either one stops a new agent at the very first
step, before it holds an address.

The static laws need nothing. The live law installs nanocurrency from npm into a temp dir and runs the published
command there; it is skipped (with the reason) when npm or the registry is unreachable, or when NRE_OFFLINE=1.
The seed it prints is thrown away, never shown.

Run: python3 specs/test_onboarding_step1.py
"""
import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUB = os.path.join(ROOT, "published")
HTML_COPIES = ["aidirectory.html", "aidirectory/index.html"]
LLMS_COPIES = ["aidirectory-llms.txt", "aidirectory/llms.txt"]


def node_script(cmd):
    m = re.search(r'node -e "(.*?)"(?:\s|$)', cmd, re.S)
    return m.group(1) if m else None


def step1_commands():
    """(where, full command) for every published copy of step 1."""
    out = []
    with open(os.path.join(PUB, "bounties.txt")) as f:
        txt = f.read()
    i = txt.index("STEP 1 - ")
    block = txt[i:txt.index("STEP 2 - ", i)]
    lines = [ln.strip() for ln in block.splitlines() if ln.strip().startswith(("npm ", "node ", "mkdir ", "cd "))]
    out.append(("bounties.txt", " && ".join(lines)))
    for rel in HTML_COPIES:
        with open(os.path.join(PUB, rel)) as f:
            page = f.read()
        m = re.search(r'<span class="num">1</span>.*?<pre><code>(.*?)</code></pre>', page, re.S)
        out.append((rel, html.unescape(m.group(1))))
    for rel in LLMS_COPIES:
        with open(os.path.join(PUB, rel)) as f:
            txt = f.read()
        i = txt.index("### 1. A wallet, in one line")
        line = next(ln for ln in txt[i:].splitlines()[1:] if ln.strip())
        out.append((rel, line.strip()))
    with open(os.path.join(PUB, "aidirectory", "tools.json")) as f:
        out.append(("aidirectory/tools.json", json.load(f)["onboarding"][0]["cmd"]))
    return out


class StaticLaws(unittest.TestCase):
    def test_every_copy_found(self):
        cmds = step1_commands()
        self.assertEqual(len(cmds), 1 + len(HTML_COPIES) + len(LLMS_COPIES) + 1)
        for where, cmd in cmds:
            self.assertIn("nanocurrency", cmd, where)
            self.assertIsNotNone(node_script(cmd), where)

    def test_no_init_call(self):
        # nanocurrency 2.x (the only line on npm since 2019) exports no init().
        for where, cmd in step1_commands():
            self.assertNotIn(".init(", cmd, where)

    def test_no_global_install_before_require(self):
        # `npm i -g X` then `node -e "require('X')"` fails: global modules are not on require()'s path.
        for where, cmd in step1_commands():
            self.assertIsNone(re.search(r"npm (i|install)\b[^&]*\s(-g|--global)\b", cmd), where)

    def test_seed_is_a_string_not_a_promise(self):
        # generateSeed() returns a Promise in 2.x; deriveSecretKey(Promise) throws.
        for where, cmd in step1_commands():
            self.assertNotIn("generateSeed()", node_script(cmd), where)

    def test_all_copies_run_the_same_script(self):
        scripts = {where: node_script(cmd) for where, cmd in step1_commands()}
        self.assertEqual(len(set(scripts.values())), 1, scripts)


class LiveLaw(unittest.TestCase):
    def test_published_command_prints_a_valid_address(self):
        if os.environ.get("NRE_OFFLINE") == "1":
            self.skipTest("NRE_OFFLINE=1")
        if not (shutil.which("npm") and shutil.which("node")):
            self.skipTest("npm/node not installed")
        for where, cmd in step1_commands():
            with self.subTest(where=where):
                self._run(where, cmd)

    def _run(self, where, cmd):
        with tempfile.TemporaryDirectory() as d:
            env = dict(os.environ)
            env.pop("NODE_PATH", None)
            try:
                p = subprocess.run(["bash", "-c", cmd], cwd=d, env=env, capture_output=True, text=True, timeout=180)
            except subprocess.TimeoutExpired:
                self.skipTest("npm timed out (registry unreachable?)")
            if p.returncode != 0 and re.search(r"ENOTFOUND|EAI_AGAIN|ECONNREFUSED|ETIMEDOUT|E403|network", p.stderr):
                self.skipTest("npm registry unreachable")
            err = p.stderr.strip().splitlines()[-3:]
            self.assertEqual(p.returncode, 0, (where, err))
            addr = re.search(r"^ADDRESS \(safe to publish\): (\S+)$", p.stdout, re.M)
            self.assertIsNotNone(addr, "no ADDRESS line")
            seed = re.search(r"^SEED \(NEVER post[^)]*\): ([0-9a-f]{64})$", p.stdout, re.M)
            self.assertIsNotNone(seed, "no 64-hex SEED line")
            self.assertRegex(addr.group(1), r"^nano_[13][13456789abcdefghijkmnopqrstuwxyz]{59}$")


if __name__ == "__main__":
    unittest.main(verbosity=2)
