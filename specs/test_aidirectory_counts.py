#!/usr/bin/env python3
"""Oracle for published/aidirectory* header stats, written after finding they had drifted (challenge, this run).

The page's own header claims N tools "referenced" and a "total". Nothing derived those numbers from the
page's own content - they were typed once and never updated when the "Built by us" section grew from 9 to
12 tools across commits #12-#14. published/aidirectory/tools.json (the machine-readable copy, generated
separately) had the right numbers the whole time; the four human-facing copies (the two aidirectory.html
files and the two aidirectory-llms.txt files) did not. An agent doing exactly what the canon asks - "if a
number here is wrong, measure it and tell us" - would have caught a self-inconsistency on the very first
stat block of the page.

This test DERIVES the claimed totals from the page's own <ul class="grid"> sections and <tr> rows, the same
way test_opener.js derives STARTER_RAW from XNO instead of restating it, so a future edit that adds a tool
without updating the header fails loudly instead of silently drifting again.

    python3 specs/test_aidirectory_counts.py
"""
import json
import re
import sys

REPO = __file__.rsplit("/specs/", 1)[0]


def section_counts(html):
    """Every <h2 ...><span class="ct">N</span></h2> section's claimed count vs its actual <li> count."""
    return re.findall(
        r'<h2[^>]*>([^<]*?)\s*<span class="ct">(\d+)</span></h2>\s*(?:<p class="why">.*?</p>)?\s*'
        r'<ul class="grid">(.*?)</ul>',
        html, re.S)


def callable_rows(html):
    return len(re.findall(r'<tr><td class="n">', html))


def check_html(path):
    html = open(path, encoding="utf-8").read()
    problems = []
    referenced_actual = 0
    for title, claimed, body in section_counts(html):
        n = len(re.findall(r"<li>", body))
        referenced_actual += n
        if int(claimed) != n:
            problems.append(f"{path}: section {title.strip()!r} claims {claimed}, has {n} <li> entries")

    callable_actual = callable_rows(html)
    m = re.search(r"<span><b>(\d+)</b>tools referenced</span>", html)
    if not m:
        problems.append(f"{path}: no 'tools referenced' stat found in the header")
    else:
        claimed_ref = int(m.group(1))
        if claimed_ref != referenced_actual:
            problems.append(
                f"{path}: header says {claimed_ref} tools referenced, page actually has {referenced_actual}")

    m2 = re.search(r"<span><b>(\d+)</b>total</span>", html)
    if m2:
        claimed_total = int(m2.group(1))
        actual_total = callable_actual + referenced_actual
        if claimed_total != actual_total:
            problems.append(
                f"{path}: header says {claimed_total} total, "
                f"page actually has {callable_actual} callable + {referenced_actual} referenced = {actual_total}")

    m3 = re.search(r"25 callable without signup, (\d+) more referenced", html)
    if m3 and int(m3.group(1)) != referenced_actual:
        problems.append(f"{path}: meta description says {m3.group(1)} referenced, page actually has {referenced_actual}")

    return problems, referenced_actual, callable_actual


def check_llms_txt(path, expected_referenced):
    text = open(path, encoding="utf-8").read()
    m = re.search(r"\(25 callable now, (\d+) referenced\)", text)
    if not m:
        return [f"{path}: no '(25 callable now, N referenced)' line found"]
    claimed = int(m.group(1))
    if claimed != expected_referenced:
        return [f"{path}: claims {claimed} referenced, page content says {expected_referenced}"]
    return []


def check_tools_json(path, expected_callable, expected_referenced):
    d = json.load(open(path))
    c = d.get("counts", {})
    problems = []
    if c.get("callable_now") != expected_callable:
        problems.append(f"{path}: counts.callable_now={c.get('callable_now')}, page has {expected_callable}")
    if c.get("referenced") != expected_referenced:
        problems.append(f"{path}: counts.referenced={c.get('referenced')}, page has {expected_referenced}")
    if c.get("total") != expected_callable + expected_referenced:
        problems.append(f"{path}: counts.total={c.get('total')}, expected {expected_callable + expected_referenced}")
    return problems


def check_flyers(expected_total):
    """The flyers that link the directory restate its size; each mention must be the page's own total."""
    pats = {
        "bounties.txt": r"Full list with (\d+) tools",
        "swap.txt": r"(\d+) tools, \d+ callable",
        "canon.html": r"one-liners and (\d+)\s+tools",
    }
    problems = []
    for name, pat in pats.items():
        path = f"{REPO}/published/{name}"
        found = re.findall(pat, open(path, encoding="utf-8").read())
        if not found:
            problems.append(f"{path}: no tool-count mention matching {pat!r}")
        for n in found:
            if int(n) != expected_total:
                problems.append(f"{path}: says {n} tools, the directory has {expected_total}")
    return problems


def main():
    problems = []
    html_problems, referenced, callable_n = check_html(f"{REPO}/published/aidirectory.html")
    problems += html_problems
    dir_problems, _, _ = check_html(f"{REPO}/published/aidirectory/index.html")
    problems += dir_problems

    problems += check_llms_txt(f"{REPO}/published/aidirectory-llms.txt", referenced)
    problems += check_llms_txt(f"{REPO}/published/aidirectory/llms.txt", referenced)
    problems += check_tools_json(f"{REPO}/published/aidirectory/tools.json", callable_n, referenced)
    problems += check_flyers(callable_n + referenced)

    if problems:
        print(f"FAIL: {len(problems)} count mismatch(es)")
        for p in problems:
            print(" -", p)
        return 1
    print(f"PASS: every published aidirectory copy agrees - {callable_n} callable, {referenced} referenced, "
          f"{callable_n + referenced} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
