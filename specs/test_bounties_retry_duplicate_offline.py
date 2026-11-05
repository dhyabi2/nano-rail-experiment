#!/usr/bin/env python3
"""Laws for the offline retried-payment check in bounties.txt section 4 (challenge #132).

Found 2026-10-12. An outside agent (squidgibblets, Moltbook 11:06 UTC) answered our claim that a unique block
settles a task: "a unique block proves a transfer, not task completion or freedom from duplicate charges: two
retries can create two distinct transfers for one order", and asked for a compact synthetic example - one order, a
retried payment, receiver acceptance, the duplicate flagged, no live payment. Section 4 already claimed nano-invoice
refuses duplicates, but only in prose. It now publishes retrycheck.py, which runs nano-invoice's own code against
its in-memory test ledger. These laws run the block exactly as published.

The run needs a clone of github.com/dhyabi2/nano-invoice. Without network the run law is SKIPPED and says so:
a skip is "could not check", never a pass.

Run: python3 specs/test_bounties_retry_duplicate_offline.py
"""
import os
import re
import subprocess
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BOUNTIES = os.path.join(ROOT, "published", "bounties.txt")
CLONE = "git clone -q --depth 1 https://github.com/dhyabi2/nano-invoice && cd nano-invoice"


def published():
    txt = open(BOUNTIES, encoding="utf-8").read()
    m = re.search(r"cat > retrycheck\.py <<'EOF'\n(.*?)\nEOF\n   python3 retrycheck\.py\n", txt, re.S)
    if not m:
        raise AssertionError("bounties.txt has no `cat > retrycheck.py <<'EOF'` ... `python3 retrycheck.py` block")
    return txt, m.group(1)


class Published(unittest.TestCase):
    def test_block_is_published_with_its_clone_line(self):
        txt, _ = published()
        self.assertIn("   " + CLONE + "\n   cat > retrycheck.py", txt)

    def test_it_sits_under_nano_invoice_in_section_4(self):
        txt, _ = published()
        s4, s5 = txt.index(" OUR XNO TOOLS"), txt.index(" 5. THE NETWORK")
        self.assertTrue(s4 < txt.index("cat > retrycheck.py") < s5)

    def test_nothing_in_it_holds_a_key_or_sends(self):
        _, code = published()
        for word in ("seed", "private", "sign_delivery_ack", "rpc.nano.to", "http://", "urlopen", "requests"):
            self.assertNotIn(word, code)
        self.assertIn("FakeLedger", code)

    def test_it_says_what_it_does_not_prove(self):
        txt, _ = published()
        self.assertIn("NOT show that the deliverable was any good", txt)


class Runs(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.code = published()
        cls.dir = tempfile.mkdtemp()
        repo = os.path.join(cls.dir, "nano-invoice")
        try:
            subprocess.run(["git", "clone", "-q", "--depth", "1", "https://github.com/dhyabi2/nano-invoice", repo],
                           check=True, capture_output=True, timeout=300)
        except (subprocess.SubprocessError, OSError) as e:
            raise unittest.SkipTest(f"UNKNOWN: could not clone nano-invoice ({e})")
        with open(os.path.join(repo, "retrycheck.py"), "w", encoding="utf-8") as f:
            f.write(cls.code + "\n")
        cls.res = subprocess.run(["python3", "retrycheck.py"], cwd=repo, capture_output=True, text=True,
                                 timeout=120)
        cls.lines = cls.res.stdout.splitlines()

    def test_exits_zero(self):
        self.assertEqual(self.res.returncode, 0, self.res.stderr)

    def test_retry_gets_the_same_invoice(self):
        self.assertTrue(self.lines[0].startswith("1 order"), self.lines)
        self.assertTrue(self.lines[0].endswith("same invoice: True"), self.lines[0])

    def test_first_pays_second_is_duplicate(self):
        blocks = [l.split() for l in self.lines if l.startswith("2 block")]
        self.assertEqual([b[3] for b in blocks], ["payment", "duplicate"], blocks)
        self.first, self.second = blocks[0][2], blocks[1][2]
        refunds = [l.split() for l in self.lines if l.startswith("3 refund")]
        self.assertEqual(len(refunds), 1, refunds)
        self.assertEqual(refunds[0][7], blocks[1][2])  # refund is for the duplicate block
        self.assertEqual(refunds[0][8], "duplicate")
        accept = self.lines[-1]
        self.assertIn("4 accept  paid by " + blocks[0][2], accept)
        self.assertTrue(accept.endswith("log verifies offline: True"), accept)

    def test_refund_is_the_whole_amount(self):
        pay = self.lines[0].split("pay_raw ")[1].split()[0]
        refund = next(l for l in self.lines if l.startswith("3 refund")).split()[2]
        self.assertEqual(refund, pay)


if __name__ == "__main__":
    unittest.main(verbosity=2)
