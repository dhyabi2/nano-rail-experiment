#!/usr/bin/env python3
"""Rebuild the 'Built by us' section of AiDirectory (index.html, llms.txt, tools.json) from ours.json.
Idempotent: the section is replaced between markers each run. Disclosed as ours on every surface.
Also repoints the dead PANDeveloper001 links to dhyabi2. Usage: update_ours.py <dir> <ours.json>"""
import html, json, re, sys, time
d, src = sys.argv[1], sys.argv[2]
ours = json.load(open(src))
TITLE = "Built by us - tools from the swarm behind this directory"
WHY = ("Disclosure: everything in this section is ours (github.com/dhyabi2). Listed separately so you can weigh it "
       "accordingly. Each one exists because an agent told us it was stuck without it. Our own numbers, "
       "good and bad, refreshed every 15 minutes: https://172-86-112-140.sslip.io/ai/numbers.json")
def fixpan(s): return s.replace("github.com/PANDeveloper001/", "github.com/dhyabi2/")
# tools.json
p = f"{d}/tools.json"; t = json.load(open(p))
t = json.loads(fixpan(json.dumps(t)))
cat = {"title": TITLE, "why": WHY, "items": [{"name": o["name"], "url": o["url"], "from": "ours", "what": o["what"]} for o in ours]}
old = len(t["catalogue"].get("ours", {}).get("items", []))
t["catalogue"] = {"ours": cat, **{k: v for k, v in t["catalogue"].items() if k != "ours"}}
t["counts"]["referenced"] = t["counts"]["referenced"] - old + len(ours)
t["counts"]["total"] = t["counts"]["total"] - old + len(ours)
t["updated"] = time.strftime("%Y-%m-%d", time.gmtime())
json.dump(t, open(p, "w"), indent=1, ensure_ascii=False)
# index.html
p = f"{d}/index.html"; h = fixpan(open(p).read())
li = "".join(f'<li><a href="{html.escape(o["url"])}">{html.escape(o["name"])}</a> <span class="what">{html.escape(o["what"])}</span></li>' for o in ours)
sec = (f'<!--ours-start--><section id="ours"><h2>{html.escape(TITLE)} <span class="ct">{len(ours)}</span></h2>'
       f'<p class="why">{html.escape(WHY)}</p><ul class="grid">{li}</ul></section><!--ours-end-->')
if "<!--ours-start-->" in h:
    h = re.sub(r"<!--ours-start-->.*?<!--ours-end-->", lambda m: sec, h, flags=re.S)
else:
    anchor = '<section id="own-key">'; assert h.count(anchor) == 1; h = h.replace(anchor, sec + anchor)
open(p, "w").write(h)
# llms.txt
p = f"{d}/llms.txt"; l = fixpan(open(p).read())
block = "<!--ours-start-->\n## " + TITLE + "\n" + WHY + "\n\n" + "".join(f"- [{o['name']}]({o['url']}): {o['what']}\n" for o in ours) + "<!--ours-end-->\n\n"
if "<!--ours-start-->" in l:
    l = re.sub(r"<!--ours-start-->.*?<!--ours-end-->\n\n", lambda m: block, l, flags=re.S)
else:
    anchor = "## Hosted APIs and payment tooling"; assert l.count(anchor) == 1; l = l.replace(anchor, block + anchor)
open(p, "w").write(l)
print("ours:", len(ours), "| total", t["counts"]["total"])
