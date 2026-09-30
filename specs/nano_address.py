"""A pure-Python, dependency-free Nano address checksum validator.

Why this exists: challenge #64 found that `extract.paypercall.dev/api/v1/address-verdict` —
the endpoint every published onboarding copy tells an agent to call *specifically to avoid
sending money to a broken address* — answers `address_valid:true` for an address with a
flipped, checksum-failing character. That is a bug on a box outside this repository, so it
cannot be fixed from here. But the deeper problem it exposes is structural: an agent whose
runtime is Python (not Node) has no local, offline way to check a Nano address's checksum
at all. Step 1 of onboarding installs `nanocurrency` for Node and calls its `checkAddress()`
before anything touches the network (the fix for challenge #23); a Python agent has no
equivalent and is entirely dependent on a remote endpoint that this project's own testing
just proved cannot be trusted for exactly this check.

This module is that equivalent: it decodes a `nano_`/`xrb_` address using Nano's own
base32 alphabet and re-derives its 5-byte blake2b checksum, entirely offline, with the
stdlib only. An agent — or a tool in this repository — can check a checksum before ever
making a network call.

The algorithm (public, from docs.nano.org's key-management guide):
  - strip the `nano_`/`xrb_` prefix, leaving a 60-character body
  - decode the body with the alphabet "13456789abcdefghijkmnopqrstuwxyz" (5 bits/char,
    300 bits total): 4 padding bits (always zero) + 256-bit public key + 40-bit checksum
  - the checksum is blake2b(pubkey, digest_size=5), byte-reversed
"""

import hashlib

ALPHABET = "13456789abcdefghijkmnopqrstuwxyz"
_IDX = {c: i for i, c in enumerate(ALPHABET)}


def check_nano_address(address: str) -> bool:
    """Return True iff `address` is a well-formed nano_/xrb_ address whose checksum matches.

    This checks SHAPE and CHECKSUM only — exactly what `nanocurrency.checkAddress()` (Node)
    checks. It says nothing about whether the account has ever transacted, is a known
    exchange deposit address, or is under anyone's control; those are separate questions
    this repository's other tools answer (see challenge #3, #23, #64).
    """
    if not isinstance(address, str):
        return False
    if address.startswith("nano_"):
        body = address[5:]
    elif address.startswith("xrb_"):
        body = address[4:]
    else:
        return False
    if len(body) != 60:
        return False
    if any(c not in _IDX for c in body):
        return False

    bits = "".join(format(_IDX[c], "05b") for c in body)
    if bits[:4] != "0000":
        # the encoding only ever uses 256 bits for the pubkey; a real address's first
        # 4 bits are always the padding zero bits from feeding 256 bits through 5-bit groups
        return False

    pubkey = int(bits[4:260], 2).to_bytes(32, "big")
    checksum_stored = int(bits[260:300], 2).to_bytes(5, "big")
    checksum_computed = hashlib.blake2b(pubkey, digest_size=5).digest()[::-1]
    return checksum_stored == checksum_computed


if __name__ == "__main__":
    import sys

    for addr in sys.argv[1:]:
        print(addr, "OK" if check_nano_address(addr) else "FAILS CHECKSUM")
