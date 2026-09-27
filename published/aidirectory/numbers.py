#!/usr/bin/env python3
"""numbers.json: the ONE source for every number our posts cite (owner, 2026-09-27; Moltbook readers caught
326 / 724 / 1,061 posted for the same thing). Rebuilt every 15 minutes from the network's own records.
A failed source leaves the previous file in place - a stale number with its time beats a wrong one."""
import json, os, subprocess, sys, tempfile, time
OUT = sys.argv[1] if len(sys.argv) > 1 else "/var/www/aidirectory/numbers.json"
def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=120).stdout
def first_json(s):
    return json.loads(s[s.index("{"):])
sw = first_json(run(["unstuck-bridge", "swarm"]))
op = first_json(run(["node", "send.js", "--counts"], cwd="/root/unstuck/opener"))
line = sw.get("line", "")
import re
def grab(p):
    m = re.search(p, line); return int(m.group(1).replace(",", "")) if m else None
f = sw.get("funnel", {})
out = {
  "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
  "rule": "These are the only numbers our posts may cite. Quote them with generated_utc.",
  "outside_agents": {
    "recorded": grab(r"([\d,]+) outside agents recorded"),
    "written_to": grab(r"([\d,]+) actually written to"),
    "answered": grab(r"([\d,]+) answered"),
    "converted": grab(r"([\d,]+) converted"),
    "funnel": f,
  },
  "starter_payments": {k: op.get(k) for k in ("starters_sent", "opened_by_us", "not_opened_by_us", "unreceived")},
  "sources": ["unstuck-bridge swarm", "node opener/send.js --counts"],
}
assert out["outside_agents"]["recorded"] is not None and out["starter_payments"]["starters_sent"] is not None
d = os.path.dirname(OUT); fd, tmp = tempfile.mkstemp(dir=d, prefix=".numbers.")
with os.fdopen(fd, "w") as fh: json.dump(out, fh, indent=1)
os.chmod(tmp, 0o644); os.replace(tmp, OUT)
print(json.dumps(out)[:400])
