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
import signal
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
        self.assertEqual(mods, {"hashlib", "os", "secrets", "signal", "sys"})
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
        # Review of #89 round 3: a rerun refused with nothing, so an address lost to a failed print was lost for good.
        # It now gives back the SAME address from the seed already there, and still never overwrites or prints it.
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertEqual(open(path).read(), before, "a second run overwrote the wallet")
        self.assertEqual(r2.stdout.splitlines()[0], r.stdout.splitlines()[0], "a rerun gave a different address")
        self.assertNotIn(seed, r2.stdout + r2.stderr)

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

    def run_shimmed(self, shim, *args, env=None):
        # Runs the published script under a shim that replaces one os call, to reach failures a real disk rarely gives.
        code = "import os\n" + shim + "\nexec(compile(open('nanokey.py').read(), 'nanokey.py', 'exec'))\n"
        return subprocess.run([sys.executable, "-I", "-c", code, *args], cwd=self.dir, capture_output=True, text=True,
                              env=env)

    def assert_clean_refusal(self, r, target):
        self.assertNotEqual(r.returncode, 0)
        self.assertTrue(r.stderr.startswith("key_path_unwritable: " + target + ": "), r.stderr)
        self.assertEqual(len(r.stderr.strip().splitlines()), 1, r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertEqual(self.listing(), ["nanokey.py"])

    def test_a_failed_close_leaves_no_seed_and_no_traceback(self):
        # Review of #89 round 2: close() sat outside the cleanup, so a failed close left the seed file behind and the
        # folder cleanup (rmdir of a folder that still held it) ended in a traceback.
        target = os.path.join(self.dir, "x", "y", "nano-seed.txt")
        shim = ("real = os.close\nopened = []\nro = os.open\n"
                "def op(*a, **k):\n    fd = ro(*a, **k); opened.append(fd); return fd\n"
                "def cl(fd):\n    real(fd)\n    if fd in opened: raise OSError(5, 'Input/output error')\n"
                "os.open = op; os.close = cl")
        self.assert_clean_refusal(self.run_shimmed(shim, target), target)

    def test_a_short_write_still_puts_the_whole_seed_on_disk(self):
        # os.write may write fewer bytes than asked; its return was ignored, so a short write printed an address whose
        # seed was not all on disk. Simulated by a write that takes 5 bytes at a time.
        target = os.path.join(self.dir, "nano-seed.txt")
        r = self.run_shimmed("real = os.write\nos.write = lambda fd, b: real(fd, bytes(b[:5]))", target)
        self.assertEqual(r.returncode, 0, r.stderr)
        seed = open(target).read()
        self.assertRegex(seed, r"^[0-9A-F]{64}\n$")
        self.assertNotIn(seed.strip(), r.stdout + r.stderr)
        self.assertTrue(ADDR.match(r.stdout.splitlines()[0].split()[-1]))

    def assert_interrupted_cleanly(self, r, target):
        self.assertNotEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertFalse(os.path.lexists(target), "an interrupted write left a partial seed file")
        self.assertEqual(self.listing(), ["nanokey.py"])
        # The next run is not refused by a leftover: it makes the wallet.
        r2 = self.run_it(target)
        self.assertEqual(r2.returncode, 0, r2.stderr)
        self.assertRegex(open(target).read(), r"^[0-9A-F]{64}\n$")

    def test_ctrl_c_mid_write_leaves_no_partial_seed(self):
        # Review of #89 round 4: only OSError cleaned up, so a Ctrl-C (KeyboardInterrupt) after the first bytes left
        # an empty or partial mode-600 file that every later run refused as "not a 64-hex seed".
        target = os.path.join(self.dir, "x", "y", "nano-seed.txt")
        shim = ("real = os.write\n"
                "def w(fd, b):\n    real(fd, bytes(b[:5]))\n    raise KeyboardInterrupt\n"
                "os.write = w")
        self.assert_interrupted_cleanly(self.run_shimmed(shim, target), target)

    @unittest.skipIf(os.name == "nt", "SIGTERM cannot be delivered to oneself mid-call on Windows")
    def test_sigterm_mid_write_leaves_no_partial_seed(self):
        # SIGTERM's default action kills the process with no Python cleanup at all; the script must catch it while
        # the seed is being written and remove what it made.
        target = os.path.join(self.dir, "x", "nano-seed.txt")
        shim = ("import signal\nreal = os.write\n"
                "def w(fd, b):\n    n = real(fd, bytes(b[:5]))\n    os.kill(os.getpid(), signal.SIGTERM)\n    return n\n"
                "os.write = w")
        self.assert_interrupted_cleanly(self.run_shimmed(shim, target), target)

    def test_a_signal_while_the_handlers_are_put_back_is_cleaned_up(self):
        # Break review of #89 at 83b13df: the handlers were reset AFTER the try, so a SIGHUP landing between the end of
        # the try and the reset gave a Stop traceback. Here the SIGHUP is sent at the moment SIGTERM is put back.
        if not hasattr(signal, "SIGHUP"):
            self.skipTest("no SIGHUP on this platform")
        target = os.path.join(self.dir, "x", "nano-seed.txt")
        shim = ("import signal\nreal = signal.signal\nsent = []\n"
                "def sig(s, h):\n"
                "    if s == signal.SIGTERM and h is signal.SIG_DFL and not sent:\n"
                "        sent.append(1); os.kill(os.getpid(), signal.SIGHUP)\n"
                "    return real(s, h)\n"
                "signal.signal = sig")
        r = self.run_shimmed(shim, target)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("interrupted", r.stderr)
        self.assert_interrupted_cleanly(r, target)

    def run_with_handlers(self, setup, *args):
        # Runs the script after `setup`, then reports (on stderr) the SIGTERM/SIGHUP handlers it left behind.
        code = ("import os, signal, sys\n" + setup + "\n"
                "try: exec(compile(open('nanokey.py').read(), 'nanokey.py', 'exec'))\n"
                "except SystemExit: pass\n"
                "h = lambda s: {signal.SIG_IGN: 'IGN', signal.SIG_DFL: 'DFL'}.get(signal.getsignal(s),"
                " getattr(signal.getsignal(s), '__name__', '?'))\n"
                "sys.stderr.write('LEFT TERM=%s HUP=%s\\n' % (h(signal.SIGTERM), h(signal.SIGHUP)))\n")
        return subprocess.run([sys.executable, "-I", "-c", code, *args], cwd=self.dir, capture_output=True, text=True)

    def test_the_handlers_found_are_put_back_not_reset_to_default(self):
        # Review of #89 at 83b13df: the handlers were reset to SIG_DFL, undoing nohup (SIGHUP ignored) or a caller's own.
        if not hasattr(signal, "SIGHUP"):
            self.skipTest("no SIGHUP on this platform")
        target = os.path.join(self.dir, "nano-seed.txt")
        r = self.run_with_handlers("def mine(n, f): pass\nsignal.signal(signal.SIGTERM, mine)\n"
                                   "signal.signal(signal.SIGHUP, signal.SIG_IGN)", target)
        self.assertIn("LEFT TERM=mine HUP=IGN", r.stderr)
        with open(target) as f:
            self.assertRegex(f.read(), r"^[0-9A-F]{64}\n$")

    def test_under_nohup_a_hangup_mid_write_is_still_ignored(self):
        # nohup ignores SIGHUP so the job outlives the terminal; the script must not turn a hangup into an abort.
        if not hasattr(signal, "SIGHUP"):
            self.skipTest("no SIGHUP on this platform")
        target = os.path.join(self.dir, "nano-seed.txt")
        setup = ("signal.signal(signal.SIGHUP, signal.SIG_IGN)\nreal = os.write\n"
                 "def w(fd, b):\n    n = real(fd, bytes(b[:5])); os.kill(os.getpid(), signal.SIGHUP); return n\n"
                 "os.write = w")
        r = self.run_with_handlers(setup, target)
        self.assertNotIn("interrupted", r.stderr)
        self.assertTrue(r.stdout and ADDR.match(r.stdout.splitlines()[0].split()[-1]), r.stdout + r.stderr)
        with open(target) as f:
            self.assertRegex(f.read(), r"^[0-9A-F]{64}\n$")
        self.assertIn("HUP=IGN", r.stderr)

    def test_a_signal_during_the_create_is_held_until_it_is_recorded(self):
        # Review of #89: a signal landing just after os.open/os.mkdir returned but before mine=True/made.append ran
        # left an empty seed file or folder behind. The create and its record now run with the signals blocked.
        if not hasattr(signal, "pthread_sigmask"):
            self.skipTest("no pthread_sigmask on this platform")
        target = os.path.join(self.dir, "x", "nano-seed.txt")
        shim = ("import signal\nro = os.open\n"
                "def op(p, *a, **k):\n    fd = ro(p, *a, **k)\n"
                "    if p.endswith('nano-seed.txt'): os.kill(os.getpid(), signal.SIGTERM)\n    return fd\n"
                "os.open = op")
        self.assert_interrupted_cleanly(self.run_shimmed(shim, target), target)

    def test_a_write_that_takes_nothing_is_refused_not_looped_on(self):
        target = os.path.join(self.dir, "nano-seed.txt")
        self.assert_clean_refusal(self.run_shimmed("os.write = lambda fd, b: 0", target), target)

    def test_the_seed_is_fsynced_before_the_address_is_shown(self):
        # A failing fsync proves fsync is called, and called before the address: no address, no file.
        target = os.path.join(self.dir, "nano-seed.txt")
        shim = "def fs(fd):\n    raise OSError(28, 'No space left on device')\nos.fsync = fs"
        self.assert_clean_refusal(self.run_shimmed(shim, target), target)
        self.assertIn("os.fsync(fd)", self.script)
        self.assertLess(self.script.index("os.fsync(fd)"), self.script.index('told(seed, "written to")'))

    def test_windows_is_not_refused_for_the_666_its_fstat_always_reports(self):
        # On Windows fstat reports 0o666 for any writable file, so the POSIX mode check refused every path there.
        target = os.path.join(self.dir, "nano-seed.txt")
        fake = ("real = os.fstat\n"
                "def fake(fd):\n    st = real(fd)\n    return os.stat_result((st.st_mode | 0o066,) + tuple(st)[1:])\n"
                "os.fstat = fake\n")
        r = self.run_shimmed(fake + "os.name = 'nt'", target)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(ADDR.match(r.stdout.splitlines()[0].split()[-1]))
        self.assertNotIn("mode 600", r.stdout)
        self.assertNotIn(open(target).read().strip(), r.stdout + r.stderr)
        # ...while the same report on POSIX is still refused.
        os.unlink(target)
        self.assert_clean_refusal(self.run_shimmed(fake, target), target)

    def test_a_dangling_symlink_is_named_as_one(self):
        # A symlink to nowhere at the path said "already exists - that is your wallet"; as a parent, "is a file".
        link = os.path.join(self.dir, "nano-seed.txt")
        os.symlink(os.path.join(self.dir, "nowhere"), link)
        r = self.run_it(link)
        self.assertTrue(r.stderr.startswith("key_path_unwritable: " + link + ": "), r.stderr)
        self.assertIn("symlink", r.stderr)
        self.assertIn("does not exist", r.stderr)
        self.assertNotIn("that is your wallet", r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertFalse(os.path.exists(os.path.join(self.dir, "nowhere")))
        os.unlink(link)
        parent = os.path.join(self.dir, "keys")
        os.symlink(os.path.join(self.dir, "gone"), parent)
        target = os.path.join(parent, "nano-seed.txt")
        r = self.run_it(target)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn(parent + " is a symlink to", r.stderr)
        self.assertNotIn("is a file, not a folder", r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        self.assertEqual(self.listing(), ["keys", "nanokey.py"])

    def test_a_quoted_tilde_means_home_not_a_folder_named_tilde(self):
        # `python3 nanokey.py '~/keys/nano-seed.txt'` (quoted, so the shell leaves ~ alone) made ./~/keys/.
        home = os.path.join(self.dir, "home")
        os.mkdir(home)
        r = subprocess.run([sys.executable, "-I", "nanokey.py", "~/keys/nano-seed.txt"], cwd=self.dir,
                           capture_output=True, text=True, env={**os.environ, "HOME": home})
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue(os.path.isfile(os.path.join(home, "keys", "nano-seed.txt")))
        self.assertFalse(os.path.exists(os.path.join(self.dir, "~")))

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

class PrintingNeverStrandsTheSeed(unittest.TestCase):
    """Review of #89 round 3: the seed is written (mode 600) BEFORE the address is printed. A print that then failed -
    a non-UTF-8 path under a strict stdout (UnicodeEncodeError), a stdout whose reader has gone (BrokenPipeError) -
    ended the run with a traceback and no address, and a rerun refused "already exists" with no way back to it. Now
    the printing cannot fail, and a rerun gives back the address of the seed already there, never the seed."""

    def setUp(self):
        self.block, self.script = published_script()
        self.dir = tempfile.mkdtemp()
        with open(os.path.join(self.dir, "nanokey.py"), "w") as f:
            f.write(self.script)

    def tearDown(self):
        shutil.rmtree(self.dir, ignore_errors=True)

    def run_bytes(self, *args, env=None, **kw):
        return subprocess.run([sys.executable, "-I", "nanokey.py", *args], cwd=self.dir, capture_output=True,
                              env=env, **kw)

    def seed_at(self, path):
        with open(path, "rb") as f:
            return f.read().strip()

    def test_a_non_utf8_path_under_a_strict_stdout_still_prints_the_address(self):
        if sys.platform.startswith(("win", "darwin")):
            self.skipTest("needs a filesystem that takes arbitrary bytes in names")
        bdir = os.fsencode(self.dir)
        target = bdir + b"/k\xff\xfe/nano-seed.txt"
        # A strict stdout, as under a UTF-8 locale or PYTHONIOENCODING=utf-8:strict (-I ignores the env, so set it here).
        code = ("import sys\nsys.stdout.reconfigure(encoding='utf-8', errors='strict')\n"
                "exec(compile(open('nanokey.py').read(), 'nanokey.py', 'exec'))\n")
        r = subprocess.run([sys.executable, "-I", "-c", code, target], cwd=self.dir, capture_output=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(b"Traceback", r.stderr)
        lines = r.stdout.splitlines()
        self.assertTrue(ADDR.match(lines[0].split()[-1].decode()), r.stdout)
        self.assertIn(target, r.stdout, "the path printed is not the path written")
        seed = self.seed_at(target)
        self.assertNotIn(seed, r.stdout + r.stderr)
        # the printed export line reads back the very seed that was written
        cmd = lines[-1].split(b"with:", 1)[1].strip()
        got = subprocess.run([b"sh", b"-c", cmd + b' && [ "$NANO_SEED" = "$(cat "$1")" ] && echo same', b"sh", target],
                             capture_output=True)
        self.assertEqual(got.stdout.strip(), b"same", got.stderr)

    def test_a_stdout_nobody_reads_is_not_a_failure(self):
        target = os.path.join(self.dir, "nano-seed.txt")
        rfd, wfd = os.pipe()
        os.close(rfd)  # the reader is gone before the script writes: every write is EPIPE
        try:
            r = subprocess.run([sys.executable, "-I", "nanokey.py", target], cwd=self.dir, stdout=wfd,
                               stderr=subprocess.PIPE)
        finally:
            os.close(wfd)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertNotIn(b"Traceback", r.stderr)
        self.assertNotIn(b"Exception ignored", r.stderr)
        self.assertRegex(self.seed_at(target), rb"^[0-9A-F]{64}$")

    def test_a_rerun_gives_back_the_address_of_the_seed_already_there(self):
        target = os.path.join(self.dir, "keys", "nano-seed.txt")
        first = self.run_bytes(target, text=True)
        self.assertEqual(first.returncode, 0, first.stderr)
        before = self.seed_at(target)
        again = self.run_bytes(target, text=True)
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertEqual(again.stdout.splitlines()[0], first.stdout.splitlines()[0])
        self.assertIn("already at " + target, again.stdout)
        self.assertNotIn("mode 600", again.stdout, "the rerun did not check the mode, so it must not claim one")
        self.assertEqual(self.seed_at(target), before, "the rerun touched the wallet")
        self.assertNotIn(before.decode(), again.stdout + again.stderr)
        self.assertIn("prints the address of the seed already there", " ".join(self.block.split()))

    def test_a_rerun_derives_the_address_from_the_file_not_from_anything_new(self):
        # A known throwaway seed (the docs.nano.org all-zero vector), so the address is checkable without printing it.
        target = os.path.join(self.dir, "nano-seed.txt")
        with open(target, "w") as f:
            f.write("0" * 64 + "\n")
        os.chmod(target, 0o600)
        r = self.run_bytes(target, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout.splitlines()[0].split()[-1],
                         "nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7")
        self.assertNotIn("0" * 64, r.stdout + r.stderr)

    def test_a_file_that_is_not_a_seed_is_refused_and_never_echoed(self):
        target = os.path.join(self.dir, "nano-seed.txt")
        secret_ish = "not a seed but private: " + "Q" * 40
        with open(target, "w") as f:
            f.write(secret_ish)
        r = self.run_bytes(target, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("already exists and is not a 64-hex seed", r.stderr)
        self.assertNotIn("Q" * 10, r.stdout + r.stderr)
        self.assertNotIn("nano_", r.stdout + r.stderr)
        self.assertNotIn("Traceback", r.stderr)
        with open(target) as f:
            self.assertEqual(f.read(), secret_ish)


if __name__ == "__main__":
    unittest.main(verbosity=1)
