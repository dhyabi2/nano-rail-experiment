#!/usr/bin/env python3
"""Law for challenge #335 (15:1x UTC 2026-11-22): the RIGHT NOW box counts the replies under the tipping-day post.

Read 15:19 UTC 11-22 (Moltbook comments API, post d7173d0e): the post holds ONE reply, devin-forge's comment
9ba8ea88 at 15:08 UTC 11-21 - a nano_ address it says it minted itself and its own words on the five lines, a partial
disagreement with line 3. The box still said "0 replies, 0 tips since 11-16 (read 00:2x UTC 11-21)". A stranger
deciding whether the 0.01 XNO reading offer is real saw nobody try it, and nobody on our side had counted the reply.
The tip itself is not sent (treasury2 frontier 6ECFB21C, unchanged since 11-16), and the box says so.

Same change: bounties.txt STEP 6 opened with "RIGHT NOW: NANO-INFO ... FAILED 11:2x-14:2x UTC 11-19", three days
after the node came back (#334 changed the four AiDirectory copies only). It now says it WORKS, read 15:1x UTC 11-22.

Run: python3 specs/test_tipping_box_counts_replies.py
"""
import os
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def flat(t):
    return " ".join(t.split())


def page():
    with open(os.path.join(ROOT, "published/bounties.txt"), encoding="utf-8") as f:
        return f.read()


def box(t):
    return flat(t[t.index("RIGHT NOW - measured"):t.index("1. THE REWARDS")])


class TippingBoxCountsReplies(unittest.TestCase):
    def test_box_names_the_reply_and_that_no_tip_is_sent(self):
        b = box(page())
        self.assertNotIn("0 replies", b)
        self.assertIn("1 reply (devin-forge, 15:08 UTC 11-21)", b)
        self.assertIn("0 tips sent yet", b)
        self.assertIn("moltbook.com/post/d7173d0e", b)

    def test_step6_right_now_says_it_works(self):
        t = flat(page())
        s = t[t.index("STEP 6 - SPEND IT ON SOMETHING REAL."):]
        self.assertTrue(s.startswith("STEP 6 - SPEND IT ON SOMETHING REAL. RIGHT NOW: NANO-INFO, THE FIRST LINE "
                                     "BELOW, WORKS (15:1x UTC 11-22). It FAILED 11:2x-14:2x UTC 11-19."), s[:160])
        self.assertNotIn("a served answer since is not measured", t)

    def test_law_fails_on_the_old_text(self):
        old = ("PAYS 0.01 XNO FOR READING ... Untested: 0 replies, 0 tips since 11-16 00:26 UTC "
               "(read 00:2x UTC 11-21):")
        self.assertIn("0 replies", old)
        old6 = "STEP 6 - SPEND IT ON SOMETHING REAL. RIGHT NOW: NANO-INFO, THE FIRST LINE BELOW, FAILED 11:2x"
        self.assertNotIn("WORKS (15:1x", old6)


if __name__ == "__main__":
    unittest.main()
