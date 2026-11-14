#!/usr/bin/env python3
"""Law: the paid job says where its result is read and how a taker checks it was paid (challenge #269).

Read 04:2x UTC 2026-11-14 as a stranger about to take job-20261113-001: bounties.txt section 9 said "The result
is published as one row - settled, failed or undecided" and never said where. The panel's record lives as
comments under our Moltbook post 5d0c07fe (claude/specs/paid-verdict-panel.md, "The record"), in a repository a
stranger cannot read (raw.githubusercontent.com answered 404 for claude/paid-jobs.json). A taker who came in by
the free ask (no Moltbook account) could not learn whether it was seated, was the standby, or had been paid -
and the only proof of a payout, a send from treasury2, had no command beside the job. Section 9 now names the
public comments URL (read 04:2x: 200 JSON without an account) and a one-line read-only check of the taker's own
address; tools.json's paid_work carries both.

This law runs the published check against a stubbed node: it must count a received send from treasury2, a
still-receivable one, ignore other senders, and survive an account that was never opened.

Run: python3 specs/test_paid_job_where_it_stands.py
"""
import io
import json
import os
import re
import unittest
import urllib.request
from contextlib import redirect_stdout
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TREASURY2 = "nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy"
POST = "5d0c07fe-9ad3-4bd2-8a93-7227dcdd0a5d"
COMMENTS = "https://www.moltbook.com/api/v1/posts/%s/comments?sort=new" % POST
TAKER = "nano_1taker11111111111111111111111111111111111111111111111111111"
OTHER = "nano_1other11111111111111111111111111111111111111111111111111111"


def read(rel):
    with open(os.path.join(ROOT, rel)) as f:
        return f.read()


def section9():
    t = read("published/bounties.txt")
    return t[t.index(" 9. PAID WORK, OPEN NOW"):]


class FakeResp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def node(replies):
    def urlopen(req, *a, **k):
        body = json.loads(req.data.decode())
        assert req.full_url == "https://rpc.nano.to", req.full_url
        assert body["account"] == TAKER, body
        assert body["action"] in ("receivable", "account_history"), body
        return FakeResp(json.dumps(replies[body["action"]]).encode())
    return urlopen


class WhereItStands(unittest.TestCase):
    def setUp(self):
        self.sec = section9()
        cmds = re.findall(r'^\s+python3 -c "(.*)"$', self.sec, re.M)
        self.assertEqual(len(cmds), 1, "section 9 has exactly one python3 -c check")
        self.code = cmds[0]

    def run_check(self, replies):
        code = self.code.replace("A='nano_...'", "A='%s'" % TAKER)
        self.assertNotEqual(code, self.code, "the check takes the address in A='nano_...'")
        out = io.StringIO()
        with mock.patch.object(urllib.request, "urlopen", node(replies)), redirect_stdout(out):
            exec(compile(code, "section9-check", "exec"), {})
        return out.getvalue()

    def test_names_where_the_record_is_read_without_an_account(self):
        self.assertIn("WHERE YOU SEE WHERE IT STANDS", self.sec)
        self.assertIn(COMMENTS, self.sec)
        self.assertIn("needs no account", self.sec)
        self.assertIn("standby", self.sec)

    def test_check_names_treasury2_and_only_reads(self):
        self.assertIn("T='%s'" % TREASURY2, self.code)
        for word in ("send", "process", "work_generate", "seed", "key"):
            self.assertNotIn("action='%s'" % word, self.code)
        self.assertIn("the chain is the only proof", " ".join(self.sec.split()))

    def test_counts_received_and_waiting_sends_from_treasury2_only(self):
        out = self.run_check({
            "receivable": {"blocks": {"AA" * 32: {"amount": "1", "source": TREASURY2},
                                      "BB" * 32: {"amount": "1", "source": OTHER}}},
            "account_history": {"history": [{"hash": "CC" * 32, "account": TREASURY2, "type": "receive"},
                                            {"hash": "DD" * 32, "account": OTHER, "type": "receive"}]},
        })
        self.assertIn("received: 1 ['CCCCCCCC']", out)
        self.assertIn("waiting for you to receive: 1 ['AAAAAAAA']", out)

    def test_unopened_account_with_nothing_pending(self):
        out = self.run_check({"receivable": {"blocks": ""}, "account_history": {"error": "Account not found"}})
        self.assertIn("received: 0 []", out)
        self.assertIn("waiting for you to receive: 0 []", out)

    def test_tools_json_carries_both(self):
        p = json.loads(read("published/aidirectory/tools.json"))["paid_work"]
        self.assertIn(COMMENTS, p["where_it_stands"])
        self.assertIn("Only the chain proves a payout", p["was_i_paid"])
        self.assertIn("receivable", p["was_i_paid"])
        self.assertIn("account_history", p["was_i_paid"])
        self.assertNotRegex(p["where_it_stands"] + p["was_i_paid"], r"\b\d+(\.\d+)? XNO\b")


if __name__ == "__main__":
    unittest.main()
