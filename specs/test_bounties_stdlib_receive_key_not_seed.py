"""Challenge #142: bounties.txt said "we publish no standard-library receive" while our conversation agent hands
passed agents one (dhyabi2/nano-wallet-xno, receive-only). That tool's key file is a PRIVATE KEY; STEP 1's
nanokey.py writes a SEED in the same 64-hex shape, so the tool silently reads a different, empty account.
The page must name the tool, say it is not for nano-seed.txt, warn about the path that makes a new key, and give
a fetch-read-run alternative to piping a download into tar."""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class StdlibReceiveKeyNotSeed(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            txt = f.read()
        i = txt.index("WHERE THE PYTHON PATH ENDS TODAY")
        self.step1 = " ".join(txt[i:i + 10000].split())
        j = txt.index(" 8. RECEIVE WHAT WAS SENT TO YOU")
        self.s8 = " ".join(txt[j:j + 800].split())
        self.txt = " ".join(txt.split())

    def test_no_longer_claims_no_stdlib_receive(self):
        self.assertNotIn("we publish no standard-library receive", self.txt)

    def test_names_the_tool_and_its_profile(self):
        self.assertIn("A STANDARD-LIBRARY RECEIVE EXISTS IN THE THREADS TOO - BUT NOT FOR THIS SEED FILE", self.step1)
        self.assertIn("https://github.com/dhyabi2/nano-wallet-xno", self.step1)
        self.assertIn('"receive-only" profile does not register send', self.step1)

    def test_says_key_file_is_a_private_key_not_the_seed(self):
        for s in ("Its key file holds a PRIVATE KEY", "nano-seed.txt above holds a SEED",
                  "never with nano-seed.txt", "finds nothing receivable"):
            self.assertIn(s, self.step1)

    def test_warns_a_missing_path_makes_a_new_key(self):
        self.assertIn("makes a NEW key there instead of failing", self.step1)

    def test_gives_fetch_read_run_instead_of_a_pipe(self):
        # challenge #146: the clone is now pinned to a commit and serves the seed-file line too
        self.assertIn("git clone -q https://github.com/dhyabi2/nano-wallet-xno && git -C nano-wallet-xno checkout -q", self.step1)
        self.assertIn("profiles.py (which tools receive-only registers)", self.step1)
        self.assertNotIn("tar xz", self.txt)

    def test_says_we_did_not_execute_it(self):
        self.assertIn("read and not executed by us", self.step1)

    def test_section8_points_seed_holders_correctly(self):
        # challenge #146: section 8 now sends no-node seed holders to the stdlib seed-file line
        self.assertIn("No node? Step 1's nano-seed.txt has a standard-library receive now", self.s8)


if __name__ == "__main__":
    unittest.main()
