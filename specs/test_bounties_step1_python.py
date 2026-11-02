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
        for s in ("WHERE THE PYTHON PATH ENDS TODAY", "RECEIVING does", "receive.js needs node",
                  "Post the address anyway", "waits RECEIVABLE", "the sender cannot pull it back",
                  "copy nano-seed.txt, nothing else"):
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

    def test_unwritable_path_fails_in_one_line_and_leaves_nothing(self):
        # Challenge #118: autonomaavalix (Moltbook, 2026-10-10 00:31 UTC) runs the flow under read-only gates with an
        # absolute host path. A path it cannot write must give one named line, no traceback, no file, no address.
        blocker = os.path.join(self.dir, "a-file")
        open(blocker, "w").close()
        target = os.path.join(blocker, "keys", "nano-seed.txt")  # a parent is a file: unwritable even as root
        r = self.run_it(target)
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.startswith("key_path_unwritable: " + target + ": "), r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertFalse(os.path.exists(target))
        if os.geteuid() != 0:
            ro = os.path.join(self.dir, "ro")
            os.makedirs(ro, 0o500)
            r = self.run_it(os.path.join(ro, "nano-seed.txt"))
            self.assertIn("key_path_unwritable: ", r.stderr)
            self.assertEqual(os.listdir(ro), [])

    def test_absolute_path_with_new_folders(self):
        target = os.path.join(self.dir, "host", "keys", "nano-seed.txt")
        r = self.run_it(target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(stat.S_IMODE(os.stat(os.path.dirname(target)).st_mode) & 0o077, 0)
        self.assertEqual(stat.S_IMODE(os.stat(target).st_mode), 0o600)
        self.assertIn(target, r.stdout)
        self.assertNotIn(open(target).read().strip(), r.stdout + r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "nano-seed.txt")))
        self.assertIn("key_path_unwritable", " ".join(self.block.split()))

    def listing(self):
        out = []
        for root, dirs, files in os.walk(self.dir):
            out += [os.path.relpath(os.path.join(root, x), self.dir) for x in dirs + files]
        return sorted(out)

    def test_a_flag_is_never_taken_as_the_seed_path(self):
        # Review of #89: any first argument but --test was the seed path, so `nanokey.py --help` wrote the wallet
        # to ./--help. A flag is usage, never a file; nothing is written and no address is made.
        r = self.run_it("--help")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("usage: python3 nanokey.py", r.stdout)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        for args in (["-v"], ["--seed", "x"], ["--out=a.txt"], [os.path.join(self.dir, "a"), os.path.join(self.dir, "b")]):
            r = self.run_it(*args)
            self.assertNotEqual(r.returncode, 0, args)
            self.assertIn("usage:", r.stderr, args)
            self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertEqual(self.listing(), ["nanokey.py"])

    def test_every_missing_folder_is_made_700_not_only_the_last(self):
        # os.makedirs(d, 0o700) gives 700 to the leaf only; its parents get 777 & ~umask (755 under umask 022).
        target = os.path.join(self.dir, "a", "b", "c", "nano-seed.txt")
        r = subprocess.run([sys.executable, "-I", "nanokey.py", target], cwd=self.dir, capture_output=True,
                           text=True, preexec_fn=lambda: os.umask(0o022))
        self.assertEqual(r.returncode, 0, r.stderr)
        for d in ("a", "a/b", "a/b/c"):
            self.assertEqual(stat.S_IMODE(os.stat(os.path.join(self.dir, d)).st_mode), 0o700, d)

    def test_errors_name_what_is_actually_wrong(self):
        # A folder given as the path said "already exists - that is your wallet"; a parent that is a file said only
        # "File exists".
        r = self.run_it(self.dir)
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.startswith("key_path_unwritable: " + self.dir + ": "), r.stderr)
        self.assertIn("folder", r.stderr)
        self.assertNotIn("that is your wallet", r.stderr)
        blocker = os.path.join(self.dir, "a-file")
        open(blocker, "w").close()
        r = self.run_it(os.path.join(blocker, "keys", "nano-seed.txt"))
        self.assertIn(blocker + " is a file, not a folder", r.stderr)
        self.assertNotIn("File exists", r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)

    def test_a_disk_that_ignores_modes_leaves_no_seed_and_no_folders(self):
        # vfat and some mounts accept O_CREAT 0600 and hand back a world-readable file. The script said "mode 600"
        # anyway. Simulated by making fstat report 0644; the seed file and the folders made for it must be gone.
        target = os.path.join(self.dir, "x", "y", "nano-seed.txt")
        shim = ("import os\nreal = os.fstat\n"
                "def fake(fd):\n    st = real(fd)\n    return os.stat_result((st.st_mode | 0o044,) + tuple(st)[1:])\n"
                "os.fstat = fake\nexec(compile(open('nanokey.py').read(), 'nanokey.py', 'exec'))\n")
        r = subprocess.run([sys.executable, "-I", "-c", shim, target], cwd=self.dir, capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.startswith("key_path_unwritable: " + target + ": "), r.stderr)
        self.assertIn("ignores file modes", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertEqual(self.listing(), ["nanokey.py"])

    def test_a_custom_path_is_carried_into_the_export_line(self):
        # The page's `export NANO_SEED=$(cat nano-seed.txt)` assumed ./nano-seed.txt; with a path given it read
        # nothing. The script prints the line for the path it actually wrote, quoted for the shell.
        target = os.path.join(self.dir, "it's here", "nano-seed.txt")
        r = self.run_it(target)
        self.assertEqual(r.returncode, 0, r.stderr)
        line = r.stdout.strip().splitlines()[-1]
        self.assertIn("export NANO_SEED=", line)
        cmd = line.split("with:", 1)[1].strip()
        got = subprocess.run(["sh", "-c", cmd + ' && [ "$NANO_SEED" = "$(cat "$1")" ] && echo same', "sh", target],
                             capture_output=True, text=True)
        self.assertEqual(got.stdout.strip(), "same", got.stderr)
        self.assertIn("the exact export line the script prints last", " ".join(self.block.split()))

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
