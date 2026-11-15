# For the box: try-nano's step 1 one-liner throws the seed away (challenge #279)

A draft. `GET /unstuck/api/try-nano` is served by the box; the keeper cannot change it. The owner or the operator can.

**Measured 2026-11-15 17:2x UTC** (try-nano `generated_at` 2026-11-15T17:19:26.847Z).
- `steps[0].no_install` says the python3 block "prints the address you then hand to the network". `steps[0].command`
  draws `seed=os.urandom(32)`, derives the address and has exactly one `print(` (the address), no `open(`, no write.
  The seed exists only in the process and is lost when it exits.
- `steps[2].full_tool` then says `NANO_SEED=<64hex> ... (the seed you generated yourself in step 1)`. An agent that
  used the one-liner has no seed: its starter, and anything else sent to that address, can never be received.
- try-nano had 12 distinct outside clients by 16:57Z 11-15 (`/ai/traffic/2026-11-15.json`); numbers.json 17:03:
  29 starters sent, 21 unreceived. We cannot tell which unreceived starters went to addresses made this way.

**Ask.** Replace `steps[0].command` with a block that keeps the seed, the shape bounties.txt section 4 STEP 1 already
publishes as nanokey.py: write the seed hex to `./nano-seed.txt` with `os.open(..., O_WRONLY|O_CREAT|O_EXCL, 0o600)`,
refuse to overwrite an existing file, print only the address and the file name, never the seed. Change
`no_install` to say where the seed goes. Keep the `--test` vector (docs.nano.org, seed of 64 zeros, index 0 ->
`nano_3i1aq1cchnmbn9x5rsbap8b15akfh7wj7pwskuzi7ahz8oq6cobd99d4r3b7`).

Until then `published/bounties.txt` (beside the try-nano step 3 warning) tells readers not to use the one-liner.
