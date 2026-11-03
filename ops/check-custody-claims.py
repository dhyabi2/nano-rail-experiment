#!/usr/bin/env python3
"""check-custody-claims: does any live guide still tell an agent the onramp's server-made seed is its own?

Found 2026-10-01 (challenge #75). Challenges #69 and #74 stopped our own texts (bounties.txt, /canon) from offering
GET /unstuck/api/v1/onramp/address without saying its seed is compromised. But the network's own guide,
https://getunstuck.space/llms.txt, still says "no key you do not hold" and "The address and the seed are yours; the
network never stores the seed. Keep it." The network's /unstuck/api/try-nano step 1 offers the onramp as an
"http_shortcut": "the seed is yours, the network never stores it." Both live in the
Unstuck repository, not here, so this repository cannot change them. On 2026-10-01 00:00-07:45 UTC the onramp was
tied for the most-requested path on the host (14 distinct outside clients), and these guides are the likeliest way in.

This tool measures whether the claim is still live, so each keeper run reports it instead of assuming it. It reads
only public guides with a GET. It never calls the onramp itself, because every call mints a fresh seed and an
onboard_id and would add our own probe to the network's counter.

    python3 ops/check-custody-claims.py          report; exit 1 while any claim is live, 3 if a guide was unreadable
    python3 ops/check-custody-claims.py --json   the same as JSON
"""
import json
import re
import sys
import urllib.request

GUIDES = [
    "https://getunstuck.space/llms.txt",
    "https://getunstuck.space/unstuck/api/try-nano",
]
UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1"

# Each claim is false for a seed the server generated and returned in a response body.
CLAIMS = [
    ("seed called the agent's own", r"(?i)\bthe seed (?:is|are) yours|\bseed are yours"),
    ("server says it never stores the seed", r"(?i)never stores? (?:the seed|your seed|it\b)"),
    ("onramp sold as holding your own key", r"(?i)no key you do not hold"),
    ("onramp address kept as a permanent identity", r"(?i)keep that address and that identity"),
    # Since 2026-10-02 the endpoint answers 410 endpoint_retired (challenge #81): a guide that still tells an agent to
    # call it first sends every address-less agent into a dead end at step one.
    ("agent sent to the retired onramp as a step",
     r"(?i)Call 1\s*\W{1,3}\s*GET /unstuck/api/v1/onramp/address|GET /unstuck/api/v1/onramp/address first"),
]


def find_claims(text):
    """Return [(label, matched text)] for every false custody claim in text."""
    out = []
    for label, pat in CLAIMS:
        for m in re.finditer(pat, text):
            out.append((label, m.group(0)))
    return out


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main(argv):
    report = []
    unreadable = False
    for url in GUIDES:
        try:
            text = fetch(url)
        except Exception as e:  # unreadable is UNKNOWN, never clean
            unreadable = True
            report.append({"url": url, "status": "UNKNOWN", "error": str(e)[:200]})
            continue
        found = find_claims(text)
        report.append({"url": url, "status": "CLAIM LIVE" if found else "clean",
                       "claims": [{"label": l, "text": t} for l, t in found]})
    if "--json" in argv:
        print(json.dumps(report, indent=1))
    else:
        for r in report:
            print(f"{r['status']:10} {r['url']}")
            for c in r.get("claims", []):
                print(f"           - {c['label']}: \"{c['text']}\"")
            if "error" in r:
                print(f"           - could not read: {r['error']}")
    if any(r["status"] == "CLAIM LIVE" for r in report):
        return 1
    return 3 if unreadable else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
