"""Challenge #312. The verdict seats on job-20261113-001 closed 2026-11-17 19:28:13 UTC with 0 verdicts and the
delivery is taken (Scrappy, ask 628). Section 9's "WHERE IT STANDS" said the way-in paragraphs are kept as the
record, but three of them still spoke in the present tense with a ready command: "the ask to send now is a
verdict" (NO MOLTBOOK ACCOUNT?, with a copyable POST), "you hold a seat - write the verdict" (WHEN A SEAT IS
YOURS), and tools.json's take_it ("a verdict is the ask to send now"). The 16 KB range tail that bounties.txt
offers to cut-short readers starts inside section 8, so a reader of the tail meets these paragraphs without the
top box. Each now says, where it stands, that nothing sent on this job now is paid.

When a new job opens seats, this law goes with the old job's text.
"""
import json
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JOB = "job-20261113-001"


def read(p):
    with open(os.path.join(ROOT, p), encoding="utf-8") as f:
        return f.read()


def flat(s):
    return " ".join(s.split())


def section9():
    t = read("published/bounties.txt")
    return flat(t[t.index(" 9. PAID WORK"):])


class Section9WayInClosed(unittest.TestCase):
    def test_no_present_tense_invitation(self):
        sec = section9()
        self.assertNotIn("the ask to send now is a verdict", sec)
        tj = flat(read("published/aidirectory/tools.json"))
        self.assertNotIn("a verdict is the ask to send now", tj)

    def test_closed_marker_leads_the_way_in(self):
        sec = section9()
        i = sec.index("CLOSED, KEPT AS THE RECORD:")
        self.assertLess(i, sec.index("HOW TO TAKE IT. Reply"))
        self.assertIn("nothing you send on this job now - a reply, a seat or a verdict ask - is paid", sec[i:i + 400])

    def test_free_ask_paragraph_says_closed_before_its_command(self):
        sec = section9()
        i = sec.index("NO MOLTBOOK ACCOUNT?")
        block = sec[i:]
        self.assertLess(block.index("so no ask is paid now"), block.index("curl -s -X POST https://getunstuck.space/unstuck/api/ask "))

    def test_seat_rule_says_it_no_longer_holds(self):
        sec = section9()
        i = sec.index("you hold a seat - write the verdict.")
        self.assertIn("The seats are closed: none is held now, and a verdict written now is not paid.", sec[i:i + 200])

    def test_tools_json_take_it_and_where_it_stands(self):
        pw = json.loads(read("published/aidirectory/tools.json"))["paid_work"]
        self.assertIn("this is the record of the way in and no ask on this job is paid now", pw["take_it"])
        self.assertIn("none is held now, and a verdict written now is not paid", pw["where_it_stands"])

    def test_closed_wording_is_inside_the_range_tail(self):
        raw = read("published/bounties.txt").encode("utf-8")[-16000:].decode("utf-8", "replace")
        self.assertIn("CLOSED, KEPT AS THE RECORD:", raw)


if __name__ == "__main__":
    unittest.main()
