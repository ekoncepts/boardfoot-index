#!/usr/bin/env python3
"""Regenerate newsletter issue #1 and the Reddit drafts from seed.csv so their numbers never go stale.
Run: python3 build_drafts.py  (after any seed.csv change)"""
import csv, statistics as st, collections, re
rows = list(csv.DictReader(open('seed.csv')))
dealer = lambda r: re.sub(r'\s*\(.*\)$', '', r['dealer'])
n = len(rows); dealers = sorted({dealer(r) for r in rows}); states = sorted({r['state'] for r in rows})
by = collections.defaultdict(list)
for r in rows: by[r['species']].append(float(r['price_per_bf']))
order = sorted(by, key=lambda s: st.median(by[s]))
med = {s: st.median(by[s]) for s in by}
def m(x): return f"${x:,.2f}"
def states_text(s):
    return ", ".join(s[:-1]) + " and " + s[-1]
# 4/4 walnut spread
w44 = sorted((float(r['price_per_bf']), r) for r in rows if r['species']=='Walnut' and r['thickness']=='4/4')
wlo, whi = w44[0], w44[-1]
w44med = st.median([p for p,_ in w44])
# cheapest find per species (4/4), top 4 cheapest overall distinct species
cheap = {}
for r in rows:
    if r['thickness']!='4/4': continue
    p=float(r['price_per_bf'])
    if r['species'] not in cheap or p < float(cheap[r['species']]['price_per_bf']): cheap[r['species']]=r
cheapest = sorted(cheap.values(), key=lambda r: float(r['price_per_bf']))[:4]
def nice(x): return x.replace('rough (KD, ','rough, kiln dried, ').replace(')','').replace('(',', ')
def surf(r): return '' if r['surfacing']=='not stated' else f", {nice(r['surfacing'])}"
def tier(lo, hi): return [s for s in order if lo <= med[s] < hi]

table = "\n".join(f"| {s} | {m(med[s])} | {m(min(by[s]))}-{m(max(by[s]))} | {len(by[s])} |" for s in order)
newsletter = f"""Subject: Lumber Price Report #1 - walnut ranges from {m(wlo[0])} to {m(whi[0])} a board foot

Hey there,

Welcome to the very first Lumber Price Report from BoardFoot Index. Each month I pull real, publicly posted hardwood prices so you can tell a fair deal from a rip-off before you load the truck.

This month: {n} prices across {len(by)} species from {len(dealers)} dealers in {len(states)} states ({states_text(states)}), all checked {rows[0]['date_checked']}.

## Median price per board foot

| Species | Median $/BF | Range | Prices |
|---|---|---|---|
{table}

Mixed thicknesses, grades and surfacing, so compare like with like.

## Cheapest 4/4 finds

""" + "\n".join(f"- 4/4 {r['species']}, {m(float(r['price_per_bf']))}/BF - {dealer(r)}, {r['city']}, {r['state']}{surf(r)}" for r in cheapest) + f"""

**Walnut check:** 4/4 walnut ran from {m(wlo[0])} ({dealer(wlo[1])}, {wlo[1]['state']}) to {m(whi[0])} ({dealer(whi[1])}, {whi[1]['state']}, {nice(whi[1]['surfacing'])}) across {len(w44)} dealers, with a median of {m(w44med)}. Grade and board length explain some of that gap, so ask what grade you're getting before you compare.

## Help build the index

Paid for lumber lately? It takes 30 seconds to share it, and every report makes the numbers better for everyone in your area:
https://ekoncepts.github.io/boardfoot-index/

Prices change, so always call the dealer before you drive.

See you next month,
Harry
BoardFoot Index
"""
open('newsletter/issue-001.md','w').write(newsletter)

old = open('/workspace/boardfoot-archive/drafts.old-67rows.md').read()
rules = old.split('## Post 1')[0].rstrip()
notes = '### Notes for Harry' + old.split('### Notes for Harry')[1]
lst = "\n".join(f"- {s} {m(med[s])}" for s in order)
def rng(ss): return f"{m(min(med[s] for s in ss))}-{m(max(med[s] for s in ss))}"
cheap2, mid, pricey = order[:2], order[2:7], order[7:]
reddit = f"""{rules}

---

## Post 1 - r/woodworking (flair: Discussion, if offered)

**Title:** I logged {n} posted hardwood prices from {len(dealers)} dealers in {len(states)} states. 4/4 walnut ranged from {m(wlo[0])} to {m(whi[0])}/bf. What are you paying?

**Body:**
I got tired of not knowing whether a price was fair, so I wrote down every per-board-foot price I could find on {len(dealers)} dealers' public price sheets ({states_text(states)}), checked this week. {n} prices, {len(by)} species. Medians, mixing thicknesses and grades:

{lst}

Stuff that stood out:
- 4/4 walnut went from {m(wlo[0])} ({wlo[1]['state']}) to {m(whi[0])} ({whi[1]['state']}, {nice(whi[1]['surfacing'])}). Median across {len(w44)} dealers was {m(w44med)}. Grade and length explain part of it, but that's still a big spread.
- Cheapest 4/4 I found: """ + "; ".join(f"{r['species'].lower()} {m(float(r['price_per_bf']))} ({r['state']})" for r in cheapest) + f""".

Still a small sample, so take it with a grain of salt. What are you paying per bf where you are? Species, thickness, rough or surfaced and a rough location (state is fine) would be great. I'll add them to my spreadsheet and post an update.

---

## Post 2 - r/BeginnerWoodWorking (flair: Question / Discussion, whichever fits)

**Title:** Beginner reference: what hardwood actually costs per board foot right now ({n} real dealer prices)

**Body:**
When I started out I had no idea if $14/bf for walnut was normal or a rip-off, so here's a quick reference from {len(dealers)} dealers' posted price sheets across {len(states)} states, checked this week (medians):

- Cheapest: {cheap2[0].lower()} (~{m(med[cheap2[0]])}) and {cheap2[1].lower()} (~{m(med[cheap2[1]])}). Great for practice and shop projects.
- Mid: {', '.join(s.lower() for s in mid)} ({rng(mid)})
- Pricey: {', '.join(f"{s.lower()} (~{m(med[s])})" for s in pricey)}

Beginner tips from the data:
- **Same board, very different prices.** 4/4 walnut ran {m(wlo[0])} to {m(whi[0])} depending on the dealer, so it pays to call around.
- **Ask about grade.** Higher grades (FAS, Face & Better) cost more, and that explains a lot of the spread.
- **Rough vs surfaced matters.** Rough needs a planer/jointer (or a shop that'll mill it for you), surfaced costs extra.
- **Thickness changes price.** 8/4 usually costs more per bf than 4/4.

Experienced folks: what do you pay, and where? Beginners: what have you been quoted? Post species, thickness, price and state, and I'll compile it into an update.

---
{notes}"""
open('reddit/drafts.md','w').write(reddit)
print('ok', n, len(dealers), len(states))
