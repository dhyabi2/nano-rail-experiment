#!/usr/bin/env bash
# Install THE UNOWNED RAIL on a box: one root-owned master, one root-owned sha256 pin, a copy in every agent's
# rules mount, the checker, and a cron line that repairs drift every ten minutes.
#
# The pin is written from the master that is being installed, so the hash is never typed by hand and never
# guessed. Everything is root-owned and mode 0444 - the agents' rules directory is already bound read-only into
# each sandbox, so an agent cannot edit its copy; the pin exists for the other threat, which is a deploy
# reverting it.
set -uo pipefail
N="${1:?swarm}"
SRC="/root/.THE-UNOWNED-RAIL.md"
NAME="THE-UNOWNED-RAIL.md"
DIR="/etc/rai-canon"
[ -s "$SRC" ] || { echo "$N: no source at $SRC"; exit 1; }

install -d -m 0755 "$DIR"
install -m 0444 "$SRC" "$DIR/$NAME"
sha256sum "$DIR/$NAME" | awk '{print $1}' > "$DIR/canon.sha256"
chmod 0444 "$DIR/canon.sha256"
echo "$N: master + pin installed"
echo -n "  pin: "; cat "$DIR/canon.sha256"

install -m 0755 /root/.canon-check.py /opt/nano-pulse/canon-check.py
python3 -m py_compile /opt/nano-pulse/canon-check.py || { echo "$N: checker does not compile"; exit 1; }

# every agent's box
n=0
for d in /srv/"$N"-swarm/*/rules; do
  [ -d "$d" ] || continue
  install -m 0444 "$DIR/$NAME" "$d/$NAME" && n=$((n+1))
done
[ -d /root/.hermes/swarm ] && install -m 0444 "$DIR/$NAME" "/root/.hermes/swarm/$NAME"
echo "$N: installed into $n member rule sets (plus the lead)"

# the repair cron, in /etc/cron.d as everything here must be - never the root crontab
F="/etc/cron.d/$N-swarm"
if grep -q canon-check "$F" 2>/dev/null; then
  echo "$N: canon check already scheduled"
else
  printf '# THE UNOWNED RAIL is pinned by hash. A deploy that reverts it is repaired within ten minutes.\n*/10 * * * * root /usr/bin/python3 /opt/nano-pulse/canon-check.py %s >> /var/log/%s-canon.log 2>&1\n' "$N" "$N" >> "$F"
  echo "$N: canon check scheduled every 10 minutes"
fi
systemctl restart cron 2>/dev/null || systemctl restart crond 2>/dev/null

echo "$N: first verification —"
python3 /opt/nano-pulse/canon-check.py "$N"
