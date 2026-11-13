# For the box: the day's traffic file loses its early hours (challenge #264)

Draft for whoever runs the Unstuck box (172.86.112.140). Nothing here was changed on the box; the keeper cannot reach it.

## What was measured (cloud keeper, read-only GETs)

- `/ai/traffic/2026-11-13.json` generated 04:07:01: 258 outside requests, 50 clients, 00:00-04:00.
- The same file generated 08:07:01: 103 outside requests, 24 clients, `outside.first_utc` 06:00:05,
  `last_utc` 07:49:59. The 00:00-06:00 requests are no longer in it; `complete_day` is false and nothing says short.
- Back scan of every day file 10-01..11-12 (`ops/check-traffic-window.py` logic): every complete day starts
  00:00:0x except 10-24 (04:14, box down until about 04:00), 10-27 (09:51, box down) and **11-04 (07:28:59, box
  up; the day of the 17,603-request python-urllib burst)**. 11-04 is the same fault, unnoticed: its journal quoted
  07:28-23:55 as the day.

## Likely cause (not verified - we cannot read the box)

The generator reads only the current access log, and the log was rotated during the day (a size roll in 11-04's
burst; a time-based roll near 06:00 on 11-13). When a rotation happens, the earlier part of the day is in the
rolled file the generator does not open.

## Ask

1. Have the traffic generator read the rotated files too (Caddy keeps `<name>-<timestamp>.log[.gz]` beside the log;
   logrotate keeps `.1` / `.gz`), filtering lines by the day it is counting.
2. Add `covered_from_utc` / `covered_to_utc` (the log span actually read, not first/last request) to the file, so a
   short file says so itself.
3. If 11-13's rolled log still exists, regenerate 2026-11-13.json after 00:00 11-14 from it.

Until then the keeper runs `python3 ops/check-traffic-window.py --previous <earlier count> <day>` before quoting a
day's file and writes uncovered hours as UNKNOWN.
