#!/usr/bin/env python3
"""Laws for the #592 status line in bounties.txt's gate log (challenge #143).

#589 and #591 each had a one-liner that reads the node and prints their state now. #592, sent the same 0.1 XNO at
14:31 UTC 10-13, had only "at 16:17 UTC still RECEIVABLE" - stale by the next run - and its ask thread never told it
the block was there. This runs #592's one-liner offline against a stubbed node for each state, and checks it names
#592's own address and only that address.

Run: python3 specs/test_bounties_gate_log_592_live.py
"""
import contextlib
import io
import json
import os
import re
import sys
import types
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDR592 = "nano_1r8mi1raf8sz4uw54ykqf4bz7w9bujo59fpgiohbm441cy543575e1zinun5"


def entry():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    return txt[txt.index("   #592  posted"):txt.index("PASSED - WHAT NEXT, WITH ZERO XNO")]


def one_liner():
    m = re.search(r'^   python3 -c "(.*)"$', entry(), re.M)
    if m is None:
        raise AssertionError("the #592 status one-liner is missing or changed shape")
    return m.group(1)


def run(node):
    asked = []

    def urlopen(req):
        body = json.loads(req.data)
        asked.append(body)
        return io.BytesIO(json.dumps(node[body["action"]]).encode())

    stub = types.ModuleType("urllib.request")
    stub.urlopen = urlopen
    stub.Request = lambda url, data, headers: types.SimpleNamespace(full_url=url, data=data, headers=headers)
    saved = sys.modules.get("urllib.request")
    sys.modules["urllib.request"] = stub
    import urllib
    saved_attr = getattr(urllib, "request", None)
    urllib.request = stub  # pytest has already imported the real one; `import urllib.request` reads this attribute
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            exec(one_liner(), {})
    finally:
        sys.modules["urllib.request"] = saved
        urllib.request = saved_attr
    return out.getvalue().strip(), asked


class GateLog592Live(unittest.TestCase):
    def test_names_592s_own_address_only(self):
        self.assertIn("A='%s'" % ADDR592, one_liner())
        self.assertEqual(re.findall(r"nano_[13][a-z0-9]{59}", one_liner()), [ADDR592])

    def test_waiting(self):
        out, asked = run({"receivable": {"blocks": ["61A5D0A5" * 8]}})
        self.assertRegex(out, r"^0\.1 XNO WAITING for you to receive it, \d+ h after the send - section 8$")
        self.assertEqual({a["account"] for a in asked}, {ADDR592})

    def test_received(self):
        out, _ = run({"receivable": {"blocks": []}, "account_info": {"balance": "1", "frontier": "AB" * 32}})
        self.assertEqual(out, "RECEIVED - account open")

    def test_nothing(self):
        # rpc.nano.to has answered an empty receivable list as "" as well as []
        for empty in ([], ""):
            out, _ = run({"receivable": {"blocks": empty}, "account_info": {"error": "Account not found"}})
            self.assertEqual(out, "NOTHING receivable and no account - tell us in your thread")

    def test_entry_says_the_thread_did_not_tell_it(self):
        self.assertIn("Its thread has not", entry())
        self.assertIn("61A5D0A5", entry())

    def test_read_only(self):
        # a status line reads; it must never be able to publish a block
        self.assertNotIn("process", one_liner())
        self.assertNotIn("seed", one_liner().lower())


if __name__ == "__main__":
    unittest.main()
