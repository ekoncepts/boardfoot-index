import csv,re,os,statistics as S,html
BASE='https://ekoncepts.github.io/boardfoot-index/'
rows=list(csv.DictReader(open('seed.csv')))
for r in rows:r['p']=float(r['price_per_bf'])
idx=open('index.html').read()
style=re.search(r'<style>.*?</style>',idx,re.S).group(0)
report=re.search(r'<div class="box"><h2>Report a price</h2>.*?</script>',idx,re.S).group(0)
kit=re.search(r'<div class="box"><h2>Get the monthly.*?ck\.5\.js" async></script>',idx,re.S).group(0)
e=html.escape
def slug(s):return s.lower().replace(' ','-')
def cls(r):
  s=r['surfacing'].lower()
  return 'Rough' if s.startswith('rough') else 'Surfaced' if s.startswith('s2s') or s.startswith('s4s') else 'Not stated'
species=sorted({r['species'] for r in rows})
def stat(ps):return f"${S.median(ps):.2f}",f"${min(ps):.2f}–${max(ps):.2f}",len(ps)
urls=[BASE]
for sp in species:
  a=sorted([r for r in rows if r['species']==sp],key=lambda r:r['p'])
  ps=[r['p'] for r in a];med,rng,n=stat(ps)
  states=sorted({r['state'] for r in a})
  thk=sorted({r['thickness'] for r in a},key=lambda t:(t=='not stated',float(t.split('/')[0])/4 if '/' in t else 0))
  trows=''.join(f"<tr><td>{t}</td><td>{'</td><td>'.join(map(str,stat([r['p'] for r in a if r['thickness']==t])))}</td></tr>" for t in thk)
  srows=''.join(f"<tr><td>{c}</td><td>{'</td><td>'.join(map(str,stat([r['p'] for r in a if cls(r)==c])))}</td></tr>" for c in ['Rough','Surfaced','Not stated'] if any(cls(r)==c for r in a))
  drows=''.join(f"<tr><td>{e(r['thickness'])}</td><td>{e(r['surfacing'])}</td><td>${r['p']:.2f}</td><td><a href=\"{e(r['source_url'])}\" rel=\"nofollow noopener\">{e(r['dealer'])}</a></td><td>{e(r['city'])}, {r['state']}</td><td>{r['date_checked']}</td></tr>" for r in a)
  tips=[f"The lowest posted price we found was ${a[0]['p']:.2f}/bf ({a[0]['thickness']}, {a[0]['surfacing']}) at {a[0]['dealer']} in {a[0]['city']}, {a[0]['state']}; the highest was ${a[-1]['p']:.2f}/bf."]
  ro=[r['p'] for r in a if cls(r)=='Rough'];su=[r['p'] for r in a if cls(r)=='Surfaced']
  if ro and su: tips.append(f"Rough-sawn median ${S.median(ro):.2f} vs surfaced median ${S.median(su):.2f} in our data — buying rough saves money if you can mill it yourself.")
  elif ro: tips.append(f"Rough-sawn listings median ${S.median(ro):.2f}/bf; rough needs jointing and planing before use.")
  th4=[r['p'] for r in a if r['thickness']=='4/4'];th8=[r['p'] for r in a if r['thickness']=='8/4']
  if th4 and th8: tips.append(f"8/4 median ${S.median(th8):.2f} vs 4/4 median ${S.median(th4):.2f} per bf — thicker stock costs {'more' if S.median(th8)>S.median(th4) else 'about the same or less'} per board foot here.")
  if any('100-249' in r['dealer'] for r in a): tips.append("Wood Vendors prices shown are its 100–249 bf tier; that dealer lists lower per-bf prices for larger orders.")
  tips.append(f"Only {n} prices from {len(states)} state(s) so far — always call the dealer to confirm, and report what you pay to improve this page.")
  others=' · '.join(f'<a href="../{slug(o)}-price-per-board-foot/">{o}</a>' for o in species if o!=sp)
  title=f"{sp} Price per Board Foot (2026): Real Dealer Prices | BoardFoot Index"
  desc=f"{sp} lumber costs a median {med}/bf across {n} posted dealer prices ({rng}) in {', '.join(states)}. See prices by thickness, rough vs surfaced, and sources."
  out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{slug(sp)}-price-per-board-foot/">{style}</head><body>
<p><a href="../">← BoardFoot Index</a></p><h1>{sp} price per board foot</h1>
<p>How much does {sp.lower()} lumber cost? Across {n} publicly posted dealer prices checked in October 2026, {sp.lower()} has a median of <b>{med}</b> per board foot, ranging {rng}. Data comes from dealer price sheets in {', '.join(states)}; every price links to its source.</p>
<h2>By thickness</h2><table><thead><tr><th>Thickness</th><th>Median</th><th>Range</th><th>Prices</th></tr></thead><tbody>{trows}</tbody></table>
<h2>Rough vs surfaced</h2><table><thead><tr><th>Surfacing</th><th>Median</th><th>Range</th><th>Prices</th></tr></thead><tbody>{srows}</tbody></table>
<h2>All {sp.lower()} prices</h2><table><thead><tr><th>Thick</th><th>Surfacing</th><th>$/BF</th><th>Dealer</th><th>Location</th><th>Checked</th></tr></thead><tbody>{drows}</tbody></table>
<h2>Buying tips from the data</h2><ul>{''.join(f"<li>{e(t)}</li>" for t in tips)}</ul>
{report}
{kit}
<h2>Other species</h2><p>{others}</p></body></html>'''
  os.makedirs(f'{slug(sp)}-price-per-board-foot',exist_ok=True)
  open(f'{slug(sp)}-price-per-board-foot/index.html','w').write(out)
  urls.append(f'{BASE}{slug(sp)}-price-per-board-foot/')
open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{u}</loc><lastmod>2026-10-16</lastmod></url>\n' for u in urls)+'</urlset>\n')
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
nav='<!--SPECIES-->'+'<p><b>Prices by species:</b> '+' · '.join(f'<a href="{slug(s)}-price-per-board-foot/">{s}</a>' for s in species)+'</p><!--/SPECIES-->'
idx=re.sub(r'<!--SPECIES-->.*?<!--/SPECIES-->','',idx,flags=re.S).replace('<p id="summary"',nav+'<p id="summary"',1)
open('index.html','w').write(idx)
print(len(urls))
