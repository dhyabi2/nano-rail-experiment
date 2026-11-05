#!/usr/bin/env python3
"""Laws for the #589 starter status line in bounties.txt's gate log (challenge #131).

On 2026-10-12 the gate log still said "ten hours on" about #589's promised starter at 08:18 UTC, eighteen hours on:
a line a keeper rewrites every four hours is stale for most of them. The entry now carries a one-liner that reads the
node and prints the state and the hours since the promise. This runs that exact one-liner offline against a stubbed
node for each of the three states, and checks it names #589's own address.

Run: python3 specs/test_bounties_starter_status_live.py
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
HERMES = "nano_1f7ezb3mgkiqjez7pdrtkj8zt174mdif39wkkccuunihjgeacxnpurp9mrf3"


def entry():
    with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
        txt = f.read()
    return txt[txt.index("   #589  posted"):txt.index("PASSED - WHAT NEXT, WITH ZERO XNO")]


def one_liner():
    m = re.search(r'^   python3 -c "(.*)"$', entry(), re.M)
    if m is None:
        raise AssertionError("the #589 status one-liner is missing or changed shape")
    return m.group(1)


def run(node):
    """Run the published one-liner with urllib.request replaced by a stub answering from `node`."""
    asked = []

    class Resp(io.BytesIO):
        pass

    def urlopen(req):
        body = json.loads(req.data)
        asked.append(body)
        return Resp(json.dumps(node[body["action"]]).encode())

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


class StarterStatusLive(unittest.TestCase):
    def test_names_589s_own_address(self):
        self.assertIn("A='%s'" % HERMES, one_liner())

    def test_not_sent(self):
        out, asked = run({"receivable": {"blocks": []},
                          "account_info": {"error": "Account not found", "balance": "0"}})
        self.assertRegex(out, r"^NOT SENT, \d+ h after the promise$")
        self.assertEqual({a["account"] for a in asked}, {HERMES})

    def test_not_sent_with_empty_string_blocks(self):
        # rpc.nano.to has answered an empty receivable list as "" as well as []
        out, _ = run({"receivable": {"blocks": ""}, "account_info": {"error": "Account not found"}})
        self.assertTrue(out.startswith("NOT SENT"))

    def test_sent_waiting(self):
        out, asked = run({"receivable": {"blocks": ["AB" * 32]}})
        self.assertEqual(out, "SENT - waiting for you to receive it")
        self.assertEqual([a["action"] for a in asked], ["receivable"])

    def test_sent_and_received(self):
        out, _ = run({"receivable": {"blocks": []}, "account_info": {"balance": "10000000000000000000000000"}})
        self.assertEqual(out, "SENT and received - account open")

    def test_hours_count_from_the_promise(self):
        self.assertIn("D.datetime(2026,10,11,14,25", one_liner())
        self.assertIn("about 14:25 UTC on 10-11", " ".join(entry().split()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
