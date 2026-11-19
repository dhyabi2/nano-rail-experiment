"""Challenge #318. The keeper's per-run measurement is an ops/ tool, marked as ours, read-only, UNKNOWN when unread.

Law: ops/measure-day.py sends only GETs and the three read-only RPC actions, refuses any other action, prints
UNKNOWN (never 0) for a source it could not read, counts a node's 402 as UNKNOWN, and names the floor of our own
share of the day's clients from the path only our tools read. (Its User-Agent is covered by test_probes_say_ours.)
"""
import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("measure_day", ROOT / "ops" / "measure-day.py")
md = importlib.util.module_from_spec(spec)
spec.loader.exec_module(md)

TRAFFIC = {
    "generated_utc": "2026-11-19T07:07:02+00:00", "complete_day": False, "ours_requests": 0,
    "outside": {"requests": 1149, "distinct_clients": 152, "first_utc": "a", "last_utc": "b"},
    "by_group": {"canon": {"requests": 27, "distinct_clients": 15}},
    "by_client_family": {"ai:GPTBot": {"requests": 2, "distinct_clients": 1},
                         "lib:curl": {"requests": 50, "distinct_clients": 13}},
    "status": {"200": 1101, "402": 10},
    "top_paths_by_clients": [{"path": "/ai/traffic/deploy-status.json", "distinct_clients": 14}],
}


def fake(responses, calls):
    def f(url, body=None):
        calls.append((url, body))
        key = body["action"] if body else url.rsplit("/", 1)[-1]
        return responses.get(key, (None, None))
    return f


class MeasureDay(unittest.TestCase):
    def test_refuses_any_action_that_is_not_a_read(self):
        for action in ("send", "work_generate", "process", "receive", "block_create"):
            with self.assertRaises(ValueError):
                md.rpc(action, "nano_x", fetch=lambda u, b=None: (200, {}))

    def test_only_reads_are_sent(self):
        calls = []
        md.run("2026-11-19", fetch=fake({}, calls))
        for url, body in calls:
            if body is not None:
                self.assertEqual(url, md.RPC)
                self.assertIn(body["action"], md.READ_ONLY_ACTIONS)

    def test_nothing_readable_is_unknown_never_zero(self):
        out = "\n".join(md.run("2026-11-19", fetch=fake({}, [])))
        self.assertIn("traffic: UNKNOWN", out)
        self.assertIn("deploy: UNKNOWN", out)
        self.assertIn("numbers: UNKNOWN", out)
        self.assertEqual(out.count("balance UNKNOWN"), 3)
        self.assertEqual(out.count("receivable UNKNOWN"), 3)
        self.assertNotIn("receivable 0", out)

    def test_a_402_from_the_node_is_unknown(self):
        out = "\n".join(md.run("2026-11-19", fetch=fake({"account_info": (402, None),
                                                          "receivable": (429, None)}, [])))
        self.assertEqual(out.count("balance UNKNOWN"), 3)
        self.assertEqual(out.count("receivable UNKNOWN"), 3)

    def test_reads_traffic_money_and_our_share_floor(self):
        r = {"2026-11-19.json": (200, TRAFFIC),
             "account_info": (200, {"balance": "11000040000000000000000000000000", "frontier": "6ECFB21CAB",
                                    "block_count": "9"}),
             "receivable": (200, {"blocks": ""}),
             "account_history": (200, {"history": []})}
        out = "\n".join(md.run("2026-11-19", fetch=fake(r, [])))
        self.assertIn("1149 outside requests, 152 clients", out)
        self.assertIn("named AI crawlers: ai:GPTBot 2/1", out)
        self.assertIn("our share floor: 14 clients", out)
        self.assertIn("balance 11.00004 XNO, frontier 6ECFB21C, 9 blocks, receivable 0 (none)", out)

    def test_xno_is_exact(self):
        self.assertEqual(md.xno("10000000000000000000000000"), "0.00001")
        self.assertEqual(md.xno("29896884890000000000000000000000"), "29.89688489")
        self.assertEqual(md.xno(0), "0")


if __name__ == "__main__":
    unittest.main()
