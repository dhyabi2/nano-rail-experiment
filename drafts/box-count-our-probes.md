# For the box: count our own probes as ours (challenge #207)

**Who applies it:** whoever owns the traffic job on 172-86-112-140 that writes `/ai/traffic/<date>.json`.
Not deployed by `experiment-deploy`; the keeper cannot change the box.

**What is wrong.** `ours_requests` counts only the swarm's three boxes. Our other probes come from addresses that change:
the hourly `outage-watch` on GitHub's runners (`ops/watch-outage.py`: bounties.txt, canon.txt, swap.txt, /canon,
/unstuck/api/asks, /ai/, deploy-status.json, every hour) and the keeper's cloud runs (every 4 h, the same pages plus
the echo, the x402 terms, tools.json, llms.txt). Each lands in `outside` as `browser-or-bot:desktop`. On 11-02
`/ai/traffic/deploy-status.json`, which only our tools read, had 20 outside clients; canon had 21, bounties 12, swap 9.
So the outside reader counts on those paths are mostly us.

**The change.** From the merge of #207 every `ops/` tool sends this User-Agent:

    Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36 unowned-rail-probe/1

In the traffic job, before the family and group counts, treat a request whose User-Agent contains
`unowned-rail-probe/` as ours: add it to `ours_requests` (or a new `ours_probe_requests`) and leave it out of
`outside`, `by_group`, `by_client_family`, `status` and `top_paths_by_clients`. Nothing else changes.

**How to check.** After the next hourly run at :41, the day's `deploy-status.json` client count in
`top_paths_by_clients` should stop rising, and `ours_requests` should rise by about 7 per hour.
