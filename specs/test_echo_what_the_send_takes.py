#!/usr/bin/env python3
"""Law for "WHAT THE SEND TAKES" beside our one live paid call (challenge #203).

Measured 2026-11-02 08:2x UTC: getunstuck.space's echo is the only paid call that answers (402 for 0.001 XNO, terms
name "workThreshold":"fffffff800000000"). bounties.txt told a stranger "Send exactly that amount from your own key",
but it publishes only a receive script (section 8, receive threshold fffffe0000000000), never said a send needs work
64 times harder, nor that 0.001 XNO must be received first (a starter is 0.00001). Nobody has ever paid that route.
This pins the note, and checks its arithmetic against the two thresholds.

Run: python3 specs/test_echo_what_the_send_takes.py
"""
import os
import re
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEND_T = "fffffff800000000"
RECV_T = "fffffe0000000000"


def mult(t):
    return 2 ** 64 / (2 ** 64 - int(t, 16))


class EchoSendTakes(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "published", "bounties.txt")) as f:
            self.txt = f.read()
        i = self.txt.index("ONE PAID CALL OF OURS DOES ANSWER")
        self.sec = self.txt[i:self.txt.index("HOW A CALL IS PAID", i)]
        self.flat = " ".join(self.sec.split())

    def test_note_comes_before_the_send_instruction(self):
        a = self.flat.index("WHAT THE SEND TAKES")
        self.assertLess(a, self.flat.index("Send exactly that amount from your own key"))
        self.assertLess(a, self.flat.index("X-Nano-Payment: <BLOCK_HASH>"))

    def test_names_both_thresholds_and_the_true_ratio(self):
        self.assertIn(SEND_T, self.flat)
        self.assertIn(RECV_T, self.flat)
        ratio = mult(SEND_T) / mult(RECV_T)
        self.assertEqual(ratio, 64.0)
        self.assertIn("%d times a receive's" % ratio, self.flat)
        self.assertIn("refused for a send", self.flat)
        # section 8's receive script really uses the receive threshold the note names
        self.assertIn("workThreshold:'%s'" % RECV_T, self.txt[self.txt.index(" 8. RECEIVE WHAT WAS SENT"):])

    def test_says_receive_first_and_no_send_script(self):
        self.assertIn("0.001 XNO RECEIVED first", self.flat)
        self.assertIn("0.00001 XNO starter is a hundredth", self.flat)
        self.assertIn("no send script", self.flat)
        self.assertNotRegex(self.sec, r"\b[0-9A-Fa-f]{64}\b(?!.*BLOCK_HASH)", "no hash or key in the note")

    def test_six_minutes_matches_six_seconds_times_64(self):
        self.assertIn("about 6 s", self.txt)  # section 7/8's measured receive time
        self.assertIn("about 6 minutes in node", self.flat)


if __name__ == "__main__":
    unittest.main()
