"""Offline tests for ops/directory-from-asks.py — no network needed.

python3 specs/test_directory_from_asks.py
"""

import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../ops")
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "directory_from_asks", __file__.rsplit("/", 1)[0] + "/../ops/directory-from-asks.py"
)
dfa = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dfa)

TREASURY = "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9"
GOOD_ADDR = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7"
BAD_CHECKSUM_ADDR = "nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx8"


def _ask(id_, asker, title, body, created="2026-09-29T00:00:00Z"):
    return {"id": id_, "asker": asker, "title": title, "body": body, "created_at": created}


class TestDirectoryFromAsks(unittest.TestCase):
    def test_our_own_asks_never_counted_as_a_registration(self):
        payload = {"asks": [_ask(1, TREASURY, "agent registration", "name: us\nsells: nothing\naccepts: XNO")]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["counts"]["registrations_found"], 0)

    def test_non_matching_title_ignored(self):
        payload = {"asks": [_ask(1, GOOD_ADDR, "just saying hi", "name: someone")]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["counts"]["registrations_found"], 0)

    def test_title_match_is_case_insensitive_and_substring(self):
        payload = {"asks": [_ask(1, GOOD_ADDR, "AGENT REGISTRATION: pyfile-toolkit", "name: pyfile-toolkit")]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["counts"]["registrations_found"], 1)

    def test_checksum_is_checked_offline_and_reported(self):
        payload = {
            "asks": [
                _ask(1, GOOD_ADDR, "agent registration", "name: good"),
                _ask(2, BAD_CHECKSUM_ADDR, "agent registration", "name: bad"),
            ]
        }
        d = dfa.build_directory(payload)
        self.assertEqual(d["counts"]["registrations_found"], 2)
        self.assertEqual(d["counts"]["checksum_valid"], 1)
        good = next(e for e in d["agents"] if e["address"] == GOOD_ADDR)
        bad = next(e for e in d["agents"] if e["address"] == BAD_CHECKSUM_ADDR)
        self.assertTrue(good["checksum_valid"])
        self.assertFalse(bad["checksum_valid"])

    def test_custody_is_never_self_reported_true(self):
        payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", "name: x\ncustody: own-key\nproven: true")]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["agents"][0]["custody"], "unproven")

    def test_terms_not_given_is_flagged_not_silently_trusted(self):
        payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", "name: x\nsells: y\naccepts: XNO")]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["agents"][0]["terms_status"], "not_given")
        self.assertFalse(d["agents"][0]["accepts_xno_verified"])

    def test_non_https_terms_rejected_outright(self):
        payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", "name: x\nterms: http://insecure.example/x402")]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["agents"][0]["terms_status"], "rejected_not_https")

    def test_terms_fetched_anonymously_and_must_actually_name_xno(self):
        with patch.object(dfa, "_anonymous_get", return_value=('{"accepts":[{"asset":"XNO"}]}', None)):
            payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", "name: x\nterms: https://example.com/.well-known/x402")]}
            d = dfa.build_directory(payload)
        self.assertEqual(d["agents"][0]["terms_status"], "verified_live")
        self.assertTrue(d["agents"][0]["accepts_xno_verified"])

    def test_terms_page_that_loads_but_does_not_name_xno_is_flagged_not_trusted(self):
        # the exact shape of challenge #16: a page that loads is not proof it names the claim
        with patch.object(dfa, "_anonymous_get", return_value=('{"accepts":[{"asset":"USDC"}]}', None)):
            payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", "name: x\nterms: https://example.com/.well-known/x402")]}
            d = dfa.build_directory(payload)
        self.assertEqual(d["agents"][0]["terms_status"], "does_not_name_xno")
        self.assertFalse(d["agents"][0]["accepts_xno_verified"])

    def test_unreachable_terms_flagged_not_dropped(self):
        with patch.object(dfa, "_anonymous_get", return_value=(None, "timed out")):
            payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", "name: x\nterms: https://example.com/x")]}
            d = dfa.build_directory(payload)
        self.assertIn("unreachable", d["agents"][0]["terms_status"])
        # flagged, not dropped from the directory (challenge #39 discipline)
        self.assertEqual(d["counts"]["registrations_found"], 1)

    def test_one_entry_per_address_first_registration_wins(self):
        payload = {
            "asks": [
                _ask(1, GOOD_ADDR, "agent registration", "name: first", created="2026-09-01T00:00:00Z"),
                _ask(2, GOOD_ADDR, "agent registration", "name: second-attempt", created="2026-09-02T00:00:00Z"),
            ]
        }
        d = dfa.build_directory(payload)
        self.assertEqual(d["counts"]["registrations_found"], 1)
        self.assertEqual(d["agents"][0]["name"], "first")

    def test_json_body_registration_also_parses(self):
        payload = {"asks": [_ask(1, GOOD_ADDR, "agent registration", '{"name": "jsonbot", "sells": "widgets", "accepts": "XNO"}')]}
        d = dfa.build_directory(payload)
        self.assertEqual(d["agents"][0]["name"], "jsonbot")
        self.assertEqual(d["agents"][0]["sells"], "widgets")

    def test_unreachable_ask_feed_reports_unknown_not_zero(self):
        with patch.object(dfa, "urllib") as mock_urllib:
            mock_urllib.request.urlopen.side_effect = OSError("network blocked")
            payload, err = dfa.fetch_asks()
        self.assertIsNone(payload)
        self.assertIsNotNone(err)


if __name__ == "__main__":
    unittest.main()
