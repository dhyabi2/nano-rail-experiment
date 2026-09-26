#!/usr/bin/env python3
"""THE UNOWNED RAIL is pinned by hash, and drift is repaired rather than reported.

Owner, 2026-09-26: "this book should be protected with hash, so that it cannot be manipulated and modified."

The agent itself already cannot edit it: the rules directory is bound read-only into every sandbox, and a `touch`
from inside answers "Read-only file system" (proved). So the real threat is not an agent - it is US. A
`<swarm>-swarm deploy` installs the forge's copy of the rules over the box's, and that is exactly how
`territories.txt` was silently reverted on all three boxes while the units kept running. A document that can be
reverted by a routine deploy is not protected by being read-only.

So: one root-owned master, one root-owned sha256 pin, and this check every ten minutes. A copy that differs is
RESTORED from the master and the event is recorded - the canon cannot be quietly rewritten or quietly removed.

  canon-check.py SWARM [--verify-only]

Fails CLOSED and loudly: a missing master or a missing pin is reported as a fault, never as "nothing to do",
because a check that cannot run must never report a clean result.
"""
import hashlib
import os
import shutil
import subprocess
import sys

NAME = "THE-UNOWNED-RAIL.md"
MASTER = "/etc/rai-canon/" + NAME
PIN = "/etc/rai-canon/canon.sha256"


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def journal(swarm, text):
    """Say it where a person will see it: the swarm's own journal, and a file if that fails."""
    try:
        subprocess.run(["/usr/local/bin/%s-bridge" % swarm, "note", text],
                       capture_output=True, timeout=60)
    except Exception:
        pass
    try:
        with open("/root/CANON-ALERT.txt", "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except OSError:
        pass


def main():
    swarm = sys.argv[1] if len(sys.argv) > 1 else ""
    verify_only = "--verify-only" in sys.argv
    if not swarm:
        sys.exit("canon-check.py SWARM [--verify-only]")

    if not os.path.exists(MASTER):
        msg = f"CANON FAULT: the master {MASTER} is missing - the canon cannot be verified on this box"
        print(msg)
        journal(swarm, msg)
        return 2
    if not os.path.exists(PIN):
        msg = f"CANON FAULT: the pin {PIN} is missing - refusing to declare the canon intact"
        print(msg)
        journal(swarm, msg)
        return 2

    pinned = open(PIN, encoding="utf-8").read().split()[0].strip()
    actual_master = sha(MASTER)
    if actual_master != pinned:
        # The master itself was changed. Never overwrite copies from an unpinned master.
        msg = (f"CANON FAULT: the MASTER does not match its pin ({actual_master[:16]}… against "
               f"{pinned[:16]}…). Nothing restored. A person must re-pin deliberately.")
        print(msg)
        journal(swarm, msg)
        return 3

    targets = []
    for d in sorted(os.listdir(f"/srv/{swarm}-swarm")) if os.path.isdir(f"/srv/{swarm}-swarm") else []:
        p = f"/srv/{swarm}-swarm/{d}/rules"
        if os.path.isdir(p):
            targets.append(os.path.join(p, NAME))
    if os.path.isdir("/root/.hermes/swarm"):
        targets.append("/root/.hermes/swarm/" + NAME)

    ok = missing = drifted = 0
    for t in targets:
        if not os.path.exists(t):
            missing += 1
            if not verify_only:
                shutil.copyfile(MASTER, t)
                os.chmod(t, 0o444)
            continue
        if sha(t) == pinned:
            ok += 1
        else:
            drifted += 1
            if not verify_only:
                os.chmod(t, 0o644)
                shutil.copyfile(MASTER, t)
                os.chmod(t, 0o444)

    verb = "would restore" if verify_only else "restored"
    line = (f"{swarm}: canon {NAME} pin {pinned[:16]}… — {ok} intact, "
            f"{drifted} drifted ({verb}), {missing} missing ({verb}), of {len(targets)} copies")
    print(line)
    if drifted or missing:
        journal(swarm, "CANON DRIFT: " + line)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
