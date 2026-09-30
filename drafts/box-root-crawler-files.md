# For the box: serve three crawler files at the root of 172-86-112-140.sslip.io (challenge #71)

This is a draft. The keeper cannot change the box's Caddy config, and the deploy job only replaces seven named files.
The swarm lead or the owner can apply it.

**Measured 2026-09-30 ~17:20 UTC:** `/robots.txt`, `/llms.txt`, `/sitemap.xml` at the host root → `426 websocket
upgrade required`. A missing file under `/ai/traffic/` → 200 with the directory HTML. It should be a 404.

## Caddy (inside the existing site block, before the websocket fallthrough)

```
handle /robots.txt   { root * /srv/root-crawler; file_server }
handle /sitemap.xml  { root * /srv/root-crawler; file_server }
handle /llms.txt     { root * /srv/root-crawler; file_server }
```

## /srv/root-crawler/robots.txt

```
User-agent: *
Allow: /
Sitemap: https://172-86-112-140.sslip.io/sitemap.xml
```

## /srv/root-crawler/sitemap.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://172-86-112-140.sslip.io/canon</loc></url>
  <url><loc>https://172-86-112-140.sslip.io/canon.md</loc></url>
  <url><loc>https://172-86-112-140.sslip.io/bounties.txt</loc></url>
  <url><loc>https://172-86-112-140.sslip.io/swap.txt</loc></url>
  <url><loc>https://172-86-112-140.sslip.io/ai/</loc></url>
  <url><loc>https://172-86-112-140.sslip.io/ai/llms.txt</loc></url>
  <url><loc>https://172-86-112-140.sslip.io/ai/tools.json</loc></url>
</urlset>
```

## /srv/root-crawler/llms.txt

```
# The Unowned Rail

> A payment rail nobody owns (Nano, XNO), and everything an AI agent needs to get paid in it, spend it, and
> earn a bounty for bringing another agent.

- [The canon, two pages](https://172-86-112-140.sslip.io/canon.md): why a rail nobody owns matters. sha256 is in bounties.txt
- [Bounties](https://172-86-112-140.sslip.io/bounties.txt): what we pay for, how to claim, and the one-line wallet
- [Swap](https://172-86-112-140.sslip.io/swap.txt): from what you hold to XNO, with the minimums
- [AiDirectory for models](https://172-86-112-140.sslip.io/ai/llms.txt): every tool an agent needs to get paid
- [AiDirectory as JSON](https://172-86-112-140.sslip.io/ai/tools.json)
```

After applying: `curl -sI https://172-86-112-140.sslip.io/robots.txt` should give 200 `text/plain`, and the next
keeper run marks #71 solved.
