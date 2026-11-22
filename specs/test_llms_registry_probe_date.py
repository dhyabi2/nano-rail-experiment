"""Challenge #333: llms.txt told buyers the XNO registry was last probed 2026-11-02.

The box re-probes dhyabi2/xno-acceptance-registry daily at 05:47 UTC
(swarm-decisions claude/box-tools/registry-probe/README-registry-probe.md). The
2026-11-22 build (generated_at 2026-11-22T05:47Z) counts live_402_nano 22 of 39,
dead 10. A buyer told the list is 20 days old has no reason to trust a row.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
COPIES = [
    ROOT / "published" / "aidirectory" / "llms.txt",
    ROOT / "published" / "aidirectory-llms.txt",
]
REGISTRY = "https://raw.githubusercontent.com/dhyabi2/xno-acceptance-registry/HEAD/registry.json"


def registry_line(path):
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("Who takes XNO, probed:"):
            return line
    raise AssertionError(f"{path}: no 'Who takes XNO, probed:' line")


class RegistryLine(unittest.TestCase):
    def test_both_copies_say_the_same(self):
        self.assertEqual(registry_line(COPIES[0]), registry_line(COPIES[1]))

    def test_links_the_registry(self):
        for p in COPIES:
            self.assertIn(REGISTRY, registry_line(p))

    def test_no_stale_probe_claim(self):
        for p in COPIES:
            line = registry_line(p)
            self.assertNotIn("last probed 2026-11-02", line)
            self.assertNotIn("25 of 39", line)

    def test_names_daily_reprobe_and_a_dated_build(self):
        for p in COPIES:
            line = registry_line(p)
            self.assertIn("re-probed daily at 05:47 UTC", line)
            dates = re.findall(r"20\d\d-\d\d-\d\d", line)
            self.assertTrue(dates, line)
            self.assertGreaterEqual(max(dates), "2026-11-22")

    def test_counts_are_out_of_the_registry_total(self):
        for p in COPIES:
            m = re.search(r"(\d+) of (\d+) answered with a Nano 402", registry_line(p))
            self.assertIsNotNone(m)
            self.assertLessEqual(int(m.group(1)), int(m.group(2)))
            self.assertEqual(m.group(2), "39")

    def test_tells_the_buyer_to_check_generated_at(self):
        for p in COPIES:
            self.assertIn("generated_at", registry_line(p))


if __name__ == "__main__":
    unittest.main()
