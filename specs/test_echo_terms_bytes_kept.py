#!/usr/bin/env python3
"""Challenge #297: the guide told an echo payer to keep the terms' hash but kept no copy of the terms.

allways (Moltbook 08:39 UTC 2026-11-16): "The digest is enough to detect a changed quote, but not to let a later
reviewer evaluate the original terms. Retain the canonical quote bytes with a durable retrieval reference." #294's
paragraph printed the first 16 hex of the echo terms' sha256 and said "record the hash"; nothing kept the bytes. The
guide now tells the payer to save the exact file and hash that file, and names a copy at a fixed commit of this public
repository (51c229ab, the commit that added the fixture). This law keeps: the paragraph after the hash paragraph and
before the send; the save line writing the file that the hash line reads; the pinned URL naming a full 40-hex commit
that contains the fixture with the same bytes; and the printed 16 hex equal to that fixture's sha256. No network.
"""
import hashlib
import os
import re
import subprocess
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
FIXTURE_REL = "specs/fixtures/unstuck-x402-manifest-2026-11-16.json"
HEAD = "KEEP THE BYTES, NOT ONLY THE HASH."
TERMS = "https://getunstuck.space/unstuck/api/v1/x402"


class EchoTermsBytesKept(unittest.TestCase):
    def setUp(self):
        with open(BOUNTIES, encoding="utf-8") as f:
            self.text = f.read()
        start = self.text.index(HEAD)
        self.p = self.text[start:self.text.index("WHAT THE SEND TAKES", start)]
        with open(os.path.join(ROOT, FIXTURE_REL), "rb") as f:
            self.raw = f.read()

    def test_sits_after_the_hash_and_before_the_send(self):
        hashp = self.text.index("THE TERMS CARRY NO VERSION NUMBER - DIFF THEIR HASH.")
        here = self.text.index(HEAD)
        send = self.text.index("WHAT THE SEND TAKES", hashp)
        self.assertTrue(hashp < here < send)

    def test_save_line_writes_the_file_the_hash_line_reads(self):
        m = re.search(r"curl -s (\S+) -o (\S+)\n\s+sha256sum (\S+)\n", self.p)
        self.assertIsNotNone(m)
        self.assertEqual(m.group(1), TERMS)
        self.assertEqual(m.group(2), m.group(3))
        self.assertIn("Keep " + m.group(2) + " with your block hash", self.p)

    def test_pinned_copy_is_a_full_commit_and_the_fixture(self):
        urls = re.findall(r"https://raw\.githubusercontent\.com/dhyabi2/nano-rail-experiment/(\S+)", self.p)
        self.assertEqual(len(urls), 1)
        commit, _, path = urls[0].partition("/")
        self.assertRegex(commit, r"^[0-9a-f]{40}$")
        self.assertEqual(path, FIXTURE_REL)
        try:
            blob = subprocess.run(["git", "-C", ROOT, "show", commit + ":" + path],
                                  capture_output=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            self.skipTest("git history not available in this checkout")
        self.assertEqual(blob, self.raw)

    def test_printed_hash_is_the_kept_bytes(self):
        # The hash is printed once, in #294's paragraph just above; this one points back at it.
        self.assertEqual(re.findall(r"\b[0-9a-f]{64}\b", self.p), [])
        self.assertEqual(re.findall(r"\b[0-9a-f]{16}\b", self.p), [])
        self.assertIn("behind the hash above", self.p)
        above = self.text[self.text.index("THE TERMS CARRY NO VERSION NUMBER"):self.text.index(HEAD)]
        self.assertEqual(re.findall(r"\b[0-9a-f]{16}\b", above), [hashlib.sha256(self.raw).hexdigest()[:16]])


if __name__ == "__main__":
    unittest.main()
