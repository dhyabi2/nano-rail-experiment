#!/usr/bin/env python3
"""An interim stand-in for the still-unbuilt `GET /unstuck/api/agents` (spec 01, Part A).

Why this exists: `specs/01-RAI-DIRECTORY.md` specifies a real agent directory and it is not
built — `/unstuck/api/agents` still answers 404 (checked live, every hunter run since
2026-09-26). Until it exists, an outside agent that wants to be found, or wants to find
anyone else, has nothing: no way to list itself, no way to see who else showed up. That
is real, uncounted friction in "joining the network" — the funnel's own numbers (1049
agents recorded, 21 with anything in the address field, only 8 of those checksum-valid,
per the routine's brief) are consistent with agents arriving and having nowhere obvious
to register themselves as a seller.

This script does NOT build the real directory (that requires server-side code on a box
this repository does not contain, per spec 01's "How this gets built" section). It builds
the smallest possible stand-in from infrastructure that already exists and already works:
the public asks API. The convention — publish it once this is reviewed — is:

    an agent that wants to be listed posts an ask titled "agent registration" with a body
    naming what it sells, what it accepts, and where its /.well-known/x402 (or other
    terms) page lives. This script reads that feed, verifies what it can, and reports a
    directory. Running it costs nothing and needs no new server-side code, which is the
    whole point of a stand-in: it must not become an argument for delaying the real thing.

Every lesson this project has already paid for is honoured on purpose:
  - our own asks are excluded (challenge #33/#34/#35 — a listing is not a caller, our own
    probe is not their reply)
  - an asker's address checksum is checked OFFLINE, first, with `nano_address.py`, never
    trusted because a remote endpoint said so (challenge #23, #64)
  - `custody` is never self-reported: an entry that merely claims a key gets
    `custody: "unproven"`, exactly as spec 01 rule 1 requires; nothing here can promote it
  - `accepts` is not trusted from the ask body alone: if a terms URL is given, it is
    re-fetched ANONYMOUSLY and must actually name XNO, or the entry is flagged
    `terms_unreachable` / `terms_does_not_name_xno` rather than silently listed as a payee
    of ours or trusted at face value (challenge #16 — a cited page must contain what we cite)
  - a source that cannot be read reports unknown, never an empty-but-clean directory
    (challenge #39 / the hunter's own preflight discipline)

Usage:
    python3 ops/directory-from-asks.py            # human-readable report
    python3 ops/directory-from-asks.py --json      # the directory.json shape
Read-only. Sends no XNO, no claim, no registration. Does not touch REFERRAL_DB or any
money path.
"""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request

sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/../specs")
from nano_address import check_nano_address  # noqa: E402

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"

ASKS_URL = "https://getunstuck.space/unstuck/api/asks"
TIMEOUT_S = 15
MAX_REDIRECTS = 5

# our own accounts — never counted as an outside registration, per challenge #33-#35
OUR_ACCOUNTS = {
    "nano_1434j1n4sin4cefs5njibag4tsmo596fmg3s6bdogtod3ndmdfez5yuebrh9",  # treasury
}

REGISTRATION_TITLE_RE = re.compile(r"\bagent registration\b", re.IGNORECASE)


class _NoRedirectBeyondLimit(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        count = getattr(req, "_redirect_count", 0) + 1
        if count > MAX_REDIRECTS:
            return None
        new_req = super().redirect_request(req, fp, code, msg, headers, newurl)
        if new_req is not None:
            new_req._redirect_count = count
        return new_req


def _anonymous_get(url: str):
    """Fetch a URL the way challenge #16 requires: no cookies, no auth, capped redirects,
    a bounded timeout, and a result that is either a 200 body or a stated failure — never
    a silent None that later gets read as "nothing wrong here"."""
    opener = urllib.request.build_opener(_NoRedirectBeyondLimit)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with opener.open(req, timeout=TIMEOUT_S) as resp:
            if resp.status != 200:
                return None, f"http {resp.status}"
            return resp.read(4096).decode("utf-8", errors="replace"), None
    except urllib.error.URLError as e:
        return None, str(e)
    except Exception as e:  # noqa: BLE001 - this is a best-effort probe, never allowed to crash the run
        return None, str(e)


def fetch_asks():
    try:
        with urllib.request.urlopen(ASKS_URL, timeout=TIMEOUT_S) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def parse_registration_body(body: str) -> dict:
    """Lenient parser: try JSON first, else simple `key: value` lines. An agent's own
    words are honoured in whatever shape it wrote them, rather than rejected for not
    matching a schema nobody has published to it yet."""
    body = (body or "").strip()
    if body.startswith("{"):
        try:
            data = json.loads(body)
            if isinstance(data, dict):
                return {str(k).lower(): v for k, v in data.items()}
        except Exception:  # noqa: BLE001
            pass
    fields = {}
    for line in body.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip().lower()
        value = value.strip()
        if key and value and key not in fields:
            fields[key] = value
    return fields


def build_directory(asks_payload: dict) -> dict:
    asks = asks_payload.get("asks", [])
    entries = []
    seen_addresses = set()
    for ask in asks:
        asker = ask.get("asker", "")
        title = ask.get("title", "") or ""
        if asker in OUR_ACCOUNTS:
            continue
        if not REGISTRATION_TITLE_RE.search(title):
            continue
        if asker in seen_addresses:
            continue  # one entry per address; first registration wins, same discipline as claims.referred
        seen_addresses.add(asker)

        checksum_valid = check_nano_address(asker)
        fields = parse_registration_body(ask.get("body", ""))
        terms_url = fields.get("terms") or fields.get("x402") or fields.get("manifest")

        terms_status = "not_given"
        names_xno = None
        if terms_url:
            if not terms_url.startswith("https://"):
                terms_status = "rejected_not_https"
            else:
                body_text, err = _anonymous_get(terms_url)
                if body_text is None:
                    terms_status = f"unreachable ({err})"
                else:
                    names_xno = ("XNO" in body_text) or ('"asset": "XNO"' in body_text) or ("xno" in body_text.lower())
                    terms_status = "verified_live" if names_xno else "does_not_name_xno"

        entries.append(
            {
                "address": asker,
                "checksum_valid": checksum_valid,
                "name": fields.get("name", ""),
                "sells": fields.get("sells", ""),
                "accepts_claimed": fields.get("accepts", ""),
                "terms": terms_url,
                "terms_status": terms_status,
                "accepts_xno_verified": bool(names_xno),
                "custody": "unproven",  # never self-reported true; spec 01 rule 1
                "first_seen": ask.get("created_at"),
                "source_ask_id": ask.get("id"),
            }
        )

    return {
        "convention": 'post an ask titled "agent registration" with a body naming what you sell, '
        "what you accept, and your terms URL (e.g. /.well-known/x402)",
        "source": ASKS_URL,
        "not_a_replacement_for": "the real /unstuck/api/agents directory in specs/01-RAI-DIRECTORY.md, "
        "which is still not built (404, checked live)",
        "counts": {
            "registrations_found": len(entries),
            "checksum_valid": sum(1 for e in entries if e["checksum_valid"]),
            "terms_verified_live_naming_xno": sum(1 for e in entries if e["accepts_xno_verified"]),
        },
        "agents": entries,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="print the directory.json shape")
    args = parser.parse_args()

    payload, err = fetch_asks()
    if payload is None:
        print(json.dumps({"error": "unknown", "detail": err, "note": "ask feed unreachable this run"}))
        sys.exit(2)

    directory = build_directory(payload)

    if args.json:
        print(json.dumps(directory, indent=2))
        return

    print(f"convention: {directory['convention']}")
    print(f"registrations found: {directory['counts']['registrations_found']}")
    print(f"  checksum-valid address: {directory['counts']['checksum_valid']}")
    print(f"  terms verified live, naming XNO: {directory['counts']['terms_verified_live_naming_xno']}")
    for e in directory["agents"]:
        print(f"- {e['address'][:24]}... name={e['name'] or '(none given)'} "
              f"checksum={'ok' if e['checksum_valid'] else 'FAILS'} terms={e['terms_status']}")


if __name__ == "__main__":
    main()
