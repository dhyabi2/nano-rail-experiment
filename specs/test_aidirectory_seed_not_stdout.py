#!/usr/bin/env python3
"""Law: the AI directory's step 1 tells an autonomous agent where a seed that is never printed is made (challenge #254).

Measured 2026-11-11 16:07 UTC (/ai/traffic): the AI directory had 35 distinct outside clients by 16:07, bounties.txt
7 - the directory is now the most-read guide. Its step 1 ("A wallet, in one line") gave one way to make a wallet:
`npm i nanocurrency` plus a `node -e` that prints the SEED to stdout. Challenge #110 (2026-10-08) found that exact
shape stopped an outside agent's autonomous runtime ("still blocked at deposit-from-entropy") and that stdout is
where such a runtime's log keeps the seed; bounties.txt has carried nanokey.py (Python 3 standard library, seed to
./nano-seed.txt mode 600, never printed) and the operator-held-address path ever since. The directory never named
either. The same day an outside agent (a2awire, Moltbook 14:40 UTC 11-11) said it will generate a fresh key in its
own runtime from our snippet.

This law: every copy of the directory's step 1 points at nanokey.py and the operator path in bounties.txt, says why
(the seed goes to stdout), and the bounties.txt section it names still exists with nanokey.py's promises.

Run: python3 specs/test_aidirectory_seed_not_stdout.py
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COPIES = ["published/aidirectory/llms.txt", "published/aidirectory-llms.txt",
          "published/aidirectory/index.html", "published/aidirectory.html"]
MUST = ["prints the SEED to stdout", "nanokey.py", "Python 3 standard library only",
        "./nano-seed.txt (mode 600, never printed, never overwritten)", "prints only the address",
        "section 4, STEP 1 of", "NO NPM, NO NODE, NO REGISTRY?", "NOT YOURS TO MAKE A KEY?"]


def flat(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return " ".join(f.read().replace("&quot;", '"').replace("&#x27;", "'").split())


def step1(s):
    i = s.index("A wallet, in one line")
    j = s.index("Check an address before you trust it", i)
    return s[i:j]


class SeedNotStdout(unittest.TestCase):
    def test_every_copy_names_the_no_print_path_in_step1(self):
        for rel in COPIES:
            part = step1(flat(rel))
            for m in MUST:
                self.assertIn(m, part, "%s: %r" % (rel, m))
            self.assertIn("sslip.io/bounties.txt", part, rel)

    def test_tools_json_step1(self):
        with open(os.path.join(ROOT, "published/aidirectory/tools.json")) as f:
            d = json.load(f)
        note = [x for x in d["onboarding"] if x["n"] == "1"][0]["note"]
        for m in MUST:
            self.assertIn(m, note, m)

    def test_bounties_still_has_what_is_named(self):
        s = flat("published/bounties.txt")
        i = s.index("STEP 1 - A WALLET, IN ONE LINE")
        j = s.index("STEP 2 - CHECK AN ADDRESS", i)
        part = s[i:j]
        for m in ("NO NPM, NO NODE, NO REGISTRY?", "NOT YOURS TO MAKE A KEY?", "nanokey.py",
                  "./nano-seed.txt (mode 600, never printed, never overwritten)", "prints only the address",
                  "nanokey.py --test"):
            self.assertIn(m, part, m)


if __name__ == "__main__":
    unittest.main()
