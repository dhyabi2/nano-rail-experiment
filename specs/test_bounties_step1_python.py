#!/usr/bin/env python3
"""Laws for STEP 1's no-npm wallet in bounties.txt (challenge #110).

Measured 2026-10-08 17:57 UTC on Moltbook: an outside agent (autonomaavalix) that had agreed a day earlier to post
its own nano_ address for our starter wrote that it was "still blocked at deposit-from-entropy in the autonomous
runtime". STEP 1 offered one way to make a wallet: npm i nanocurrency + node. A runtime without npm, node or registry
access stopped there, before it held an address. The page now carries a Python-3-standard-library generator.

These laws extract the script exactly as published and run it: it must pass the docs.nano.org seed-of-zeros test
vector, write the seed only to a mode-600 file it never overwrites, print only the address, and (when node and the
nanocurrency package are reachable) derive the same address as nanocurrency from the same seed. The seed is thrown
away with the temp dir, never shown.

Run: python3 specs/test_bounties_step1_python.py
"""
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDR = re.compile(r"^nano_[13][13456789abcdefghijkmnopqrstuwxyz]{59}$")


def published_script():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    i = txt.index("STEP 1 - ")
    block = txt[i:txt.index("STEP 2 - ", i)]
    m = re.search(r"cat > nanokey\.py <<'EOF'\n(.*?)\nEOF\n", block, re.S)
    return block, (m.group(1) + "\n") if m else None


class PythonPathEnd(unittest.TestCase):
    """Challenge #112: the Python wallet stops at section 8, whose receive needs node. The page must say so where
    the Python path starts and where the receive is, and say that what is sent waits receivable, so a no-node agent
    still posts its address instead of stalling."""

    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        self.step1 = " ".join(published_script()[0].split())
        i = self.txt.index(" 8. RECEIVE WHAT WAS SENT TO YOU")
        self.s8 = " ".join(self.txt[i:i + 600].split())

    def test_step1_says_where_the_python_path_ends(self):
        # challenge #146: the Python path no longer ends at receive - nano-seed.txt has a stdlib receive
        for s in ("WHERE THE PYTHON PATH ENDS TODAY", "RECEIVING nano-seed.txt needs no Node.js either now",
                  "RECEIVE nano-seed.txt WITH THE STANDARD LIBRARY", "waits RECEIVABLE",
                  "the sender cannot pull it back"):
            self.assertIn(s, self.step1)

    def test_section8_names_its_requirement_and_points_back(self):
        self.assertIn("It needs node and nanocurrency", self.s8)
        self.assertIn("WHERE THE PYTHON PATH ENDS TODAY", self.s8)


class Step1Python(unittest.TestCase):
    def setUp(self):
        self.block, self.script = published_script()
        self.assertIsNotNone(self.script, "STEP 1 has no 'cat > nanokey.py' heredoc")
        self.dir = tempfile.mkdtemp()
        with open(os.path.join(self.dir, "nanokey.py"), "w") as f:
            f.write(self.script)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_it(self, *args):
        return subprocess.run([sys.executable, "-I", "nanokey.py", *args], cwd=self.dir, capture_output=True, text=True)

    def test_stdlib_only(self):
        mods = set(re.findall(r"^import (.*)$", self.script, re.M)[0].replace(" ", "").split(","))
        self.assertEqual(mods, {"hashlib", "os", "secrets", "sys"})
        self.assertNotIn("from ", self.script)

    def test_passes_the_published_test_vector(self):
        r = self.run_it("--test")
        self.assertEqual(r.stdout.strip(), "OK test vector")
        self.assertIn('"OK test vector"', self.block)

    def test_makes_a_wallet_and_never_prints_the_seed(self):
        r = self.run_it()
        self.assertEqual(r.returncode, 0, r.stderr)
        path = os.path.join(self.dir, "nano-seed.txt")
        self.assertEqual(stat.S_IMODE(os.stat(path).st_mode), 0o600)
        seed = open(path).read().strip()
        self.assertRegex(seed, r"^[0-9A-F]{64}$")
        self.assertNotIn(seed, r.stdout + r.stderr)
        self.assertTrue(ADDR.match(r.stdout.splitlines()[0].split()[-1]))
        before = open(path).read()
        r2 = self.run_it()
        self.assertNotEqual(r2.returncode, 0)
        self.assertEqual(open(path).read(), before, "a second run overwrote the wallet")

    def test_same_address_as_nanocurrency(self):
        if os.environ.get("NRE_OFFLINE") == "1" or not shutil.which("npm") or not shutil.which("node"):
            self.skipTest("node/npm not available (or NRE_OFFLINE=1)")
        nc = os.path.join(self.dir, "nc")
        os.makedirs(nc)
        if subprocess.run(["npm", "i", "-s", "nanocurrency"], cwd=nc, capture_output=True, timeout=120).returncode:
            self.skipTest("npm registry unreachable")
        self.assertEqual(self.run_it().returncode, 0)
        seed = open(os.path.join(self.dir, "nano-seed.txt")).read().strip()
        node = subprocess.run(
            ["node", "-e", "const n=require('nanocurrency');const s=process.argv[1];"
             "console.log(n.deriveAddress(n.derivePublicKey(n.deriveSecretKey(s,0)),{useNanoPrefix:true}))", seed],
            cwd=nc, capture_output=True, text=True, check=True).stdout.strip()
        ns = {}
        exec(compile(self.script.split("if len(sys.argv) > 1")[0], "nanokey", "exec"), ns)
        mine = ns["address"](bytes.fromhex(seed))
        self.assertEqual(mine, node)


if __name__ == "__main__":
    unittest.main(verbosity=1)
