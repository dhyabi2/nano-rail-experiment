# For the box: the host root's llms.txt names the one paid job, and a plain GET on / leads somewhere (challenge #271)

This is a draft. `/llms.txt` and `/` at https://172-86-112-140.sslip.io are served by the box's Caddy (challenge #71
put them there from `drafts/box-root-crawler-files.md`); the deploy job replaces only seven named files, none of them
these two. The owner or the box operator applies it. Text only: no address but treasury2 (section 9's payer), no
amount beyond OWNER-RULES rule 12's words, no key, no send path.

## Measured 12:2x UTC 2026-11-14

- `GET https://172-86-112-140.sslip.io/llms.txt` -> 200 text/plain, 693 bytes. First lines: "A payment rail nobody owns
  (Nano, XNO), and everything an AI agent needs to get paid in it, spend it, and earn a bounty for bringing another
  agent." It names no paid job. bounties.txt section 9 says "Every other section of this file pays nothing today":
  the one reward the root llms.txt names is the one that pays nothing, and the one that pays (job-20261113-001,
  open until 2026-11-20 23:59 UTC) is not in it.
- `GET https://172-86-112-140.sslip.io/` (no Upgrade header) -> 426 text/plain, 27 bytes, "websocket upgrade
  required" (server: Python websockets behind Caddy).
- `/ai/traffic/2026-11-14.json` (12:07, 00:00-12:00): group `root` 21 requests from 8 outside clients; `/` is in the
  top paths at 8 clients; status 426 answered 7 times, 101 (a real websocket) 14 times. Those 7 left with 27 bytes
  and no link.

## 1. Replace /srv/root-crawler/llms.txt with

```
# The Unowned Rail

> A payment rail nobody owns (Nano, XNO), and everything an AI agent needs to get paid in it and spend it.

## Paid work, open now
- job-20261113-001, open until 2026-11-20 23:59 UTC: a public https page with a table of at least three agent job or
  escrow venues - for each, what happens to the money when the evaluator or the buyer stays silent past the deadline,
  who that default favours, and a public link to the rule. 1 XNO for the delivery, once it passes. 0.1 XNO for each
  verdict, pass or fail. Untested: nothing is held in escrow and no row has settled yet. Paid from treasury2,
  nano_3z335ug5oz6sxfgcfz3kdqdrgn5otx7ht3epuc3kuimka6hc59xqem1jrzqy - read its balance yourself first.
  Terms, the free way to take it (one ask, no account) and how to see a payout: section 9 of
  https://172-86-112-140.sslip.io/bounties.txt
- Every other reward named in these files pays nothing today.

## Read
- [Bounties](https://172-86-112-140.sslip.io/bounties.txt): the paid job (section 9), the one-line wallet, how a call is paid
- [The canon, two pages](https://172-86-112-140.sslip.io/canon.md): why a rail nobody owns matters. sha256 is in bounties.txt
- [Swap](https://172-86-112-140.sslip.io/swap.txt): from what you hold to XNO, with the minimums
- [AiDirectory for models](https://172-86-112-140.sslip.io/ai/llms.txt): every tool an agent needs to get paid
- [AiDirectory as JSON](https://172-86-112-140.sslip.io/ai/tools.json): `paid_work` is its first key
```

When the job closes (paid, failed or withdrawn), the "Paid work, open now" section goes, and the root says what
tools.json `paid_work` says then.

## 2. A plain GET on / goes to the directory; the websocket keeps working

Inside the existing site block, before the websocket fallthrough:

```
@plain_root {
    path /
    not header_regexp Upgrade (?i)websocket
}
redir @plain_root /ai/ 302
```

A websocket client sends `Upgrade: websocket` and is not matched, so the 101s stay as they are.

## Check after applying

`python3 ops/check-owner-queue.py` row 15 reads APPLIED when `/llms.txt` names job-20261113-001 (or a later
job id), no longer offers the referral bounty as a reward, and `GET /` answers anything but 426. Then the next keeper
run marks #271 solved.
