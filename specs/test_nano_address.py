"""Offline tests for specs/nano_address.py, pinned against known-good and known-bad vectors.

No network needed: python3 specs/test_nano_address.py
"""

import unittest

from nano_address import check_nano_address


class TestNanoAddress(unittest.TestCase):
    def test_docs_nano_org_test_vector(self):
        # docs.nano.org's own key-derivation test vector, also used as the example
        # account in the live x402 manifest served by extract.paypercall.dev.
        self.assertTrue(
            check_nano_address("nano_3t6k35gi95xu6tergt6p69ck76ogmitsa8mnijtpxm9fkcm736xtoncuohr3")
        )

    def test_burn_address(self):
        # the well-known all-ones burn account; a second independent real-world vector.
        self.assertTrue(
            check_nano_address("nano_1111111111111111111111111111111111111111111111111111hifc8npp")
        )

    def test_treasury_and_payee_addresses_named_throughout_this_repo(self):
        self.assertTrue(
            check_nano_address("nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9")
        )
        self.assertTrue(
            check_nano_address("nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7")
        )

    def test_xrb_prefix_is_the_same_account_and_also_validates(self):
        self.assertTrue(
            check_nano_address("xrb_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9")
        )

    def test_challenge_64_flipped_checksum_characters_are_rejected(self):
        # the exact two mutations challenge #64 found extract.paypercall.dev's
        # address-verdict endpoint wrongly answering address_valid:true for.
        self.assertFalse(
            check_nano_address("nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx8")
        )
        self.assertFalse(
            check_nano_address("nano_1yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhny7")
        )

    def test_wrong_length_rejected(self):
        self.assertFalse(check_nano_address("nano_1434j1n4sin4cefs5njibag4tsmo596fmg"))
        self.assertFalse(check_nano_address("nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9xx"))

    def test_disallowed_alphabet_characters_rejected(self):
        # the alphabet excludes 0, 2, l and v specifically to avoid visual confusion
        self.assertFalse(
            check_nano_address("nano_0yo6c1t64ahfjdw1dxizmbbnpdmbrckwhw9phbg5pdkeubrizga4qhnjmnx7")
        )

    def test_no_prefix_or_wrong_prefix_rejected(self):
        self.assertFalse(
            check_nano_address("1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9")
        )
        self.assertFalse(
            check_nano_address("btc_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9")
        )

    def test_non_string_input_rejected_not_raised(self):
        self.assertFalse(check_nano_address(None))
        self.assertFalse(check_nano_address(12345))


if __name__ == "__main__":
    unittest.main()
