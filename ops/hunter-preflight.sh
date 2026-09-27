#!/usr/bin/env bash
# Preflight for the conversion-blocker hunter routine (trig_01KzZuSB66ooSpKmu7fc8aTM).
#
# Why this exists: on 2026-09-26 the hunter's own cloud session had every measurement
# host denied by its environment's network egress policy (getunstuck.space, all five
# paypercall.dev subdomains, rpc.nano.to, swarm/board.getunstuck.space) - not because
# any of those services were down, but because the SESSION's allowed-domains list did
# not cover them. Every curl came back `exit 56, CONNECT tunnel failed, response 403`
# and every WebFetch came back `EGRESS_BLOCKED`. Nothing about the experiment changed;
# the hunter simply went blind. A run that does not check for this distinguishes
# "I looked and nothing changed" from "I could not look" nowhere, and the two read
# identically in CHALLENGES-SOLVED.md and in the PR body - exactly the failure this
# project keeps naming as its costliest shape (challenge #39; specs/03 closing line:
# "a check that could not run and reported a clean result").
#
# Run this FIRST, before any measurement step. It classifies each required host as
# reachable, policy-blocked (a proxy/egress denial, not the remote service's fault),
# or actually down/erroring, and exits non-zero the moment ANY host is blocked or down
# so the caller can report the whole measurement phase as unknown rather than silently
# skipping to "nothing to report".
#
# Usage: ops/hunter-preflight.sh
# Exit 0  - every host answered normally; safe to proceed with real measurement.
# Exit 2  - one or more hosts were policy-blocked (egress denial) - environment fix
#           needed; the run must report UNKNOWN for whatever depended on them, never
#           zero, and should say so plainly rather than silently thin its report.
# Exit 3  - one or more hosts were reachable but erroring - a real candidate for
#           "an endpoint that stopped accepting XNO" / "a site or API down".

set -u

HOSTS=(
  "https://getunstuck.space/ledger.json"
  "https://getunstuck.space/unstuck/api/asks"
  "https://extract.paypercall.dev/health"
  "https://search.paypercall.dev/health"
  "https://domain.paypercall.dev/health"
  "https://check.paypercall.dev/health"
  "https://geoip.paypercall.dev/health"
  "https://swarm.getunstuck.space"
  "https://board.getunstuck.space"
  "https://rpc.nano.to"
)

blocked=0
errored=0
ok=0

printf '%-55s %-10s %s\n' "HOST" "STATUS" "DETAIL"
for url in "${HOSTS[@]}"; do
  # -sS silent-but-show-errors, short timeouts, no retry: this is a probe, not a client.
  out=$(curl -sS -o /dev/null -m 10 --connect-timeout 6 -w '%{http_code}' "$url" 2>&1)
  code=$?
  http="${out##*$'\n'}"
  if [ "$code" -eq 0 ]; then
    printf '%-55s %-10s %s\n' "$url" "OK" "http $http"
    ok=$((ok + 1))
  elif [ "$code" -eq 56 ] || [ "$code" -eq 7 ]; then
    # 56 = CONNECT tunnel/transfer failed (the shape a proxy 403 takes); 7 = could not
    # connect at all. Both are the network refusing the attempt, not the remote server.
    printf '%-55s %-10s %s\n' "$url" "BLOCKED" "curl exit $code (egress denial, not the remote service)"
    blocked=$((blocked + 1))
  else
    printf '%-55s %-10s %s\n' "$url" "ERROR" "curl exit $code"
    errored=$((errored + 1))
  fi
done

echo
echo "ok=$ok blocked=$blocked errored=$errored"

if [ "$blocked" -gt 0 ]; then
  echo
  echo "PREFLIGHT FAILED: $blocked host(s) were denied by this session's own network egress" \
       "policy, not by the remote service. Do not report this run's measurements as" \
       "'nothing changed' - report them as UNKNOWN and say the session was network-blind." \
       "Fix: broaden this cloud environment's Network access / allowed domains" \
       "(see environment.network in the session's documentation tool)."
  exit 2
fi

if [ "$errored" -gt 0 ]; then
  echo
  echo "PREFLIGHT WARNING: $errored host(s) reached the network but did not answer" \
       "normally - this is a real candidate for 'a site or API down', not a session" \
       "network problem. Investigate before writing anything to CHALLENGES-SOLVED.md."
  exit 3
fi

echo
echo "PREFLIGHT OK: all hosts reachable. Proceed with real measurement."
exit 0
