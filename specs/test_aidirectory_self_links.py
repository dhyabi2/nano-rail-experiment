#!/usr/bin/env python3
"""Every root-absolute link the AiDirectory page makes to itself must stay under /ai/ (challenge #126).

The page is served at https://172-86-112-140.sslip.io/ai/ (its own ld+json "url"). Its <link rel="alternate">
tags and its "machine-readable" list pointed at /tools.json, /llms.txt and /.well-known/ai-directory.json -
paths left over from when the page sat at the root of its own domain. On this host /tools.json and
/.well-known/ai-directory.json answer 426 "websocket upgrade required", and /llms.txt is a different file
(the canon's). A crawler or agent that follows the page's own alternate link for the JSON gets a dead end.

    python3 specs/test_aidirectory_self_links.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = [ROOT / "published/aidirectory/index.html", ROOT / "published/aidirectory.html"]
# root-absolute paths this host serves itself; everything the directory publishes lives under /ai/
ALLOWED_PREFIXES = ("/ai/",)

fails = []
for page in PAGES:
    html = page.read_text(encoding="utf-8")
    for href in re.findall(r'(?:href|src)="(/[^"/][^"]*)"', html):
        if not href.startswith(ALLOWED_PREFIXES):
            fails.append(f"{page.relative_to(ROOT)}: {href} is outside /ai/ (dead or wrong file on this host)")
    for want in ("/ai/tools.json", "/ai/llms.txt"):
        if f'rel="alternate"' in html and f'href="{want}"' not in html:
            fails.append(f"{page.relative_to(ROOT)}: no link to {want}")

if fails:
    print("FAIL:\n  " + "\n  ".join(fails))
    sys.exit(1)
print(f"PASS: every root-absolute link in {len(PAGES)} AiDirectory pages stays under /ai/")
