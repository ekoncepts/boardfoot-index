import csv,re,os,statistics as S,html
BASE='https://ekoncepts.github.io/boardfoot-index/'
rows=list(csv.DictReader(open('seed.csv')))
for r in rows:r['p']=float(r['price_per_bf'])
def is_cust(r):return not r['source_url'].startswith('http')
cust_all=[r for r in rows if is_cust(r)]
rows=[r for r in rows if not is_cust(r)]   # medians, ranges, tips and tables use dealer-posted prices only
idx=open('index.html').read()
style=re.search(r'<style>.*?</style>',idx,re.S).group(0)
report=re.search(r'<div class="box"><h2>Report a price</h2>.*?</script>',idx,re.S).group(0)
kit=re.search(r'<div class="box"><h2>Get the monthly.*?ck\.5\.js" async></script>',idx,re.S).group(0)
e=html.escape
def slug(s):return s.lower().replace(' ','-')
def cls(r):
  s=r['surfacing'].lower()
  return 'Rough' if s.startswith('rough') else 'Surfaced' if s.startswith(('s2s','s4s','surfaced')) else 'Not stated'
SORTJS='''(function(){var A=function(x,y){return x.localeCompare(y,'en',{sensitivity:'base'})},tb=document.querySelector('#alltbl tbody'),sel=document.getElementById('sortby');
var P=function(a,b){return +a.dataset.p-+b.dataset.p};
var cmp={price:function(a,b){return P(a,b)||A(a.dataset.d,b.dataset.d)},dealer:function(a,b){return A(a.dataset.d,b.dataset.d)||P(a,b)},state:function(a,b){return A(a.dataset.s,b.dataset.s)||A(a.dataset.d,b.dataset.d)||P(a,b)}};
sel.onchange=function(){[].slice.call(tb.rows).sort(cmp[sel.value]).forEach(function(r){tb.appendChild(r)})};sel.onchange()})();'''

import collections
STATE_NAMES={'AL':'Alabama','AZ':'Arizona','AR':'Arkansas','CA':'California','CO':'Colorado','CT':'Connecticut','DE':'Delaware','FL':'Florida','GA':'Georgia','ID':'Idaho','IL':'Illinois','IN':'Indiana','IA':'Iowa','KS':'Kansas','KY':'Kentucky','LA':'Louisiana','ME':'Maine','MD':'Maryland','MA':'Massachusetts','MI':'Michigan','MN':'Minnesota','MS':'Mississippi','MO':'Missouri','MT':'Montana','NE':'Nebraska','NV':'Nevada','NH':'New Hampshire','NJ':'New Jersey','NM':'New Mexico','NY':'New York','NC':'North Carolina','ND':'North Dakota','OH':'Ohio','OK':'Oklahoma','OR':'Oregon','PA':'Pennsylvania','RI':'Rhode Island','SC':'South Carolina','SD':'South Dakota','TN':'Tennessee','TX':'Texas','UT':'Utah','VT':'Vermont','VA':'Virginia','WA':'Washington','WV':'West Virginia','WI':'Wisconsin','WY':'Wyoming'}
MIN_STATE=5
state_counts=collections.Counter(r['state'] for r in rows)
pub_states=sorted([s for s,c in state_counts.items() if c>=MIN_STATE],key=lambda s:STATE_NAMES[s])
skipped_states=sorted([(s,c) for s,c in state_counts.items() if c<MIN_STATE])
def sslug(s):return STATE_NAMES[s].lower().replace(' ','-')+'-hardwood-lumber-prices'
state_links=lambda pre,ex=None:' · '.join(f'<a href="{pre}{sslug(s)}/">{STATE_NAMES[s]}</a>' for s in pub_states if s!=ex)
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
  drows=''.join(f"<tr data-p=\"{r['p']}\" data-d=\"{e(r['dealer'])}\" data-s=\"{r['state']}\"><td>{e(r['thickness'])}</td><td>{e(r['surfacing'])}</td><td>${r['p']:.2f}</td><td><a href=\"{e(r['source_url'])}\" rel=\"nofollow noopener\">{e(r['dealer'])}</a></td><td>{e(r['city'])}, {r['state']}</td><td>{r['date_checked']}</td></tr>" for r in a)
  ca=sorted([r for r in cust_all if r['species']==sp],key=lambda r:(r['thickness'],r['p']))
  cust=''
  if ca:
    crow=''.join(f"<tr><td>{e(r['thickness'])}</td><td>{e(r['surfacing'])}</td><td>${r['p']:.2f}</td><td>{e(r['dealer'])}</td><td>{e(r['city'])}, {r['state']}</td><td>customer-reported</td></tr>" for r in ca)
    cust=f'<h2>Customer-reported small-piece prices</h2><p>These came from a real order at {e(ca[0]["dealer"])}: small S4S (surfaced, unfinished) pieces sold per piece, converted to $/bf using <em>nominal</em> size (nominal thickness × nominal width × length ÷ 12). Real boards are slightly smaller than nominal, so these run higher per bf than dealer-posted board-foot prices. They are <b>not</b> included in the medians, ranges or tips above.</p><table><thead><tr><th>Thick</th><th>Notes</th><th>$/BF</th><th>Dealer</th><th>Location</th><th>Source</th></tr></thead><tbody>{crow}</tbody></table>'
  tips=[f"The lowest posted price we found was ${a[0]['p']:.2f}/bf ({a[0]['thickness']}{'' if a[0]['surfacing']=='not stated' else ', '+a[0]['surfacing']}) at {a[0]['dealer']} in {a[0]['city']}, {a[0]['state']}; the highest was ${a[-1]['p']:.2f}/bf."]
  ro=[r['p'] for r in a if cls(r)=='Rough'];su=[r['p'] for r in a if cls(r)=='Surfaced']
  if ro and su:
    if S.median(ro)<S.median(su): tips.append(f"Rough-sawn median ${S.median(ro):.2f} vs surfaced median ${S.median(su):.2f} in our data (mixed dealers and grades) — rough is cheaper per bf if you can mill it yourself.")
    else: tips.append(f"Rough-sawn median ${S.median(ro):.2f} vs surfaced median ${S.median(su):.2f} in our data — rough was not cheaper here because dealers, grades and regions differ; compare like with like.")
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
<h2>All {sp.lower()} prices</h2><p><label>Sort by <select id="sortby"><option value="price">Price (cheapest first)</option><option value="dealer">Dealer (A to Z)</option><option value="state">State (A to Z, then dealer)</option></select></label></p><table id="alltbl"><thead><tr><th>Thick</th><th>Surfacing</th><th>$/BF</th><th>Dealer</th><th>Location</th><th>Checked</th></tr></thead><tbody>{drows}</tbody></table>
<script>{SORTJS}</script>
{cust}<h2>Buying tips from the data</h2><ul>{''.join(f"<li>{e(t)}</li>" for t in tips)}</ul>
{report}
{kit}
<h2>Other species</h2><p>{others}</p>
<h2>{sp} prices by state</h2><p>{state_links('../')}</p>
<p>Need to know how many board feet a project takes? Try the <a href="../board-foot-calculator/">free board foot calculator</a>.</p></body></html>'''
  os.makedirs(f'{slug(sp)}-price-per-board-foot',exist_ok=True)
  open(f'{slug(sp)}-price-per-board-foot/index.html','w').write(out)
  urls.append(f'{BASE}{slug(sp)}-price-per-board-foot/')

def shell(title,desc,path,body,depth_prefix='../'):
  return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">{style}</head><body>
<p><a href="{depth_prefix}">← BoardFoot Index</a></p>{body}
{report}
{kit}
</body></html>"""
def write(path,content):
  os.makedirs(path,exist_ok=True);open(path+'/index.html','w').write(content);urls.append(BASE+path+'/')
species_links=lambda pre:' · '.join(f'<a href="{pre}{slug(s)}-price-per-board-foot/">{s}</a>' for s in species)

# ---- per-state pages ----
for st in pub_states:
  nm=STATE_NAMES[st]; a=[r for r in rows if r['state']==st]
  sps=sorted({r['species'] for r in a}); dealers=sorted({(r['dealer'],r['city']) for r in a})
  srows=''
  for sp in sps:
    ps=[r['p'] for r in a if r['species']==sp]; m,rg,n=stat(ps)
    srows+=f'<tr><td><a href="../{slug(sp)}-price-per-board-foot/">{sp}</a></td><td>{m}</td><td>{rg}</td><td>{n}</td></tr>'
  drows=''
  for dn,ct in dealers:
    da=[r for r in a if r['dealer']==dn and r['city']==ct]
    main=collections.Counter(r['source_url'] for r in da).most_common(1)[0][0]
    spl=[]
    for sp in sorted({r['species'] for r in da}):
      u=collections.Counter(r['source_url'] for r in da if r['species']==sp).most_common(1)[0][0]
      spl.append(f'<a href="{e(u)}" rel="nofollow noopener">{sp}</a>')
    drows+=f'<tr><td><a href="{e(main)}" rel="nofollow noopener">{e(dn)}</a></td><td>{e(ct)}, {st}</td><td>{len(da)}</td><td>{", ".join(spl)}</td><td>{max(r["date_checked"] for r in da)}</td></tr>'
  allp=[r['p'] for r in a]; med,rng,n=stat(allp)
  meds={sp:S.median([r['p'] for r in a if r['species']==sp]) for sp in sps}
  lo=min(a,key=lambda r:r['p']); hi=max(a,key=lambda r:r['p'])
  cheap=min(meds,key=meds.get); dear=max(meds,key=meds.get)
  others=state_links('../',st)
  title=f"Hardwood Lumber Prices in {nm} (2026): Dealer Price per Board Foot | BoardFoot Index"
  desc=f"Real posted hardwood prices in {nm}: {n} dealer prices across {len(sps)} species from {len(dealers)} dealer{'s' if len(dealers)!=1 else ''}, ranging {rng} per board foot. Medians by species, sources and dates."
  body=f"""<h1>Hardwood lumber prices in {nm}</h1>
<p>We found {n} publicly posted hardwood prices from {len(dealers)} {nm} dealer{'s' if len(dealers)!=1 else ''}, covering {len(sps)} species. Across all species and thicknesses the median is <b>{med}</b> per board foot, ranging {rng}. Every figure below comes from a dealer's own price list or product page, checked in October 2026 — nothing is estimated.</p>
<p>In this data, {cheap} has the lowest species median in {nm} ({meds[cheap] and f'${meds[cheap]:.2f}'}/bf) and {dear} the highest (${meds[dear]:.2f}/bf). The single lowest posted price is ${lo['p']:.2f}/bf ({lo['species']} {lo['thickness']}, {e(lo['dealer'])}); the highest is ${hi['p']:.2f}/bf ({hi['species']} {hi['thickness']}, {e(hi['dealer'])}).</p>
<h2>Median and range by species in {nm}</h2>
<table><thead><tr><th>Species</th><th>Median</th><th>Range</th><th>Prices</th></tr></thead><tbody>{srows}</tbody></table>
<p><small>Each row mixes thicknesses, grades and rough vs surfaced stock from that state's dealers, so use the <a href="../">searchable table</a> or the species pages for like-for-like comparisons.</small></p>
<h2>{nm} dealers with posted prices</h2>
<table><thead><tr><th>Dealer</th><th>Location</th><th>Prices</th><th>Species (links go to the source)</th><th>Checked</th></tr></thead><tbody>{drows}</tbody></table>
<p>Prices change without notice and may differ by grade, width, length and quantity — call the dealer before you drive. Paid something different? Report it below.</p>
<h2>Estimate a project</h2><p>Use the <a href="../board-foot-calculator/">board foot calculator</a> to convert board dimensions to board feet and a rough cost.</p>
<h2>Other states</h2><p>{others}</p>
<h2>Prices by species</h2><p>{species_links('../')}</p>"""
  write(sslug(st),shell(title,desc,sslug(st)+'/',body))

# ---- calculator ----
opts=''.join(f'<option value="{S.median([r["p"] for r in rows if r["species"]==sp])!r}" data-n="{sum(1 for r in rows if r["species"]==sp)}" data-s="{len({r["state"] for r in rows if r["species"]==sp})}" data-lo="{min(r["p"] for r in rows if r["species"]==sp)!r}" data-hi="{max(r["p"] for r in rows if r["species"]==sp)!r}">{sp}</option>' for sp in species)
CALCJS=r"""(function(){
function num(s){s=String(s).trim();if(!s)return NaN;var m;
 if(m=s.match(/^(\d+(?:\.\d+)?)\s+(\d+)\/(\d+)$/))return +m[1]+ +m[2]/ +m[3];
 if(m=s.match(/^(\d+)\/(\d+)$/))return +m[1]/ +m[2];
 if(/^\d*\.?\d+$/.test(s))return +s;return NaN}
var $=function(i){return document.getElementById(i)};
function calc(){var t=num($('t').value),w=num($('w').value),l=num($('l').value),q=num($('q').value||'1');
 var out=$('out'),est=$('est');est.innerHTML='';
 if(!(t>0&&w>0&&l>0&&q>0)){out.textContent='Enter thickness, width, length and quantity to see board feet.';return}
 var lf=$('lu').value=='in'?l/12:l;var per=t*w*lf/12,tot=per*q;
 out.innerHTML='<b>'+per.toFixed(2)+' board feet</b> per piece &middot; <b>'+tot.toFixed(2)+' board feet</b> total ('+q+' piece'+(q==1?'':'s')+')';
 var o=$('sp').options[$('sp').selectedIndex];
 if(o.value){var m=+o.value,n=o.dataset.n;
  est.innerHTML='<b>Estimated cost: about $'+(tot*m).toFixed(2)+'</b> ('+tot.toFixed(2)+' bf &times; $'+m.toFixed(2)+'/bf median). <em>This is only an estimate</em> based on the median of '+n+' dealer-posted '+o.text.toLowerCase()+' prices from '+o.dataset.s+' state'+(o.dataset.s==1?'':'s')+' (range $'+(+o.dataset.lo).toFixed(2)+'&ndash;$'+(+o.dataset.hi).toFixed(2)+'/bf). Real prices depend on thickness, grade, rough vs surfaced, width, length and quantity &mdash; <b>call the dealer</b> for a quote.'}}
['t','w','l','q','lu','sp'].forEach(function(i){$(i).oninput=calc;$(i).onchange=calc});calc()})();"""
cbody=f"""<h1>Board foot calculator</h1>
<p>Work out how many board feet a board (or a stack of them) contains, and optionally get a rough cost from real dealer-posted prices.</p>
<div class="box"><div>
<label>Thickness <input id="t" value="4/4" size="6" inputmode="decimal" aria-label="Thickness"></label> <small>inches, or quarters like 4/4, 5/4, 8/4 (also 3/4, 1.5 or 1 1/2)</small><br>
<label>Width (in) <input id="w" value="6" size="6" inputmode="decimal"></label>
<label>Length <input id="l" value="8" size="6" inputmode="decimal"></label> <select id="lu" aria-label="Length unit"><option value="ft">feet</option><option value="in">inches</option></select>
<label>Quantity <input id="q" value="1" size="4" inputmode="numeric"></label><br>
<label>Species (optional) <select id="sp"><option value="">— no cost estimate —</option>{opts}</select></label></div>
<p id="out" class="stat" aria-live="polite"></p><p id="est" aria-live="polite"></p></div>
<h2>How board feet work</h2>
<p>A board foot is a volume of wood: 1 inch thick × 12 inches wide × 12 inches long (144 cubic inches). The formula is <b>thickness (in) × width (in) × length (ft) ÷ 12</b>, multiplied by the number of pieces. For example, one 4/4 board that is 6 inches wide and 8 feet long is 1 × 6 × 8 ÷ 12 = 4 board feet.</p>
<p>Hardwood thickness is quoted in quarters of an inch: 4/4 is 1 inch, 5/4 is 1¼, 6/4 is 1½, 8/4 is 2 inches. That is the <em>rough</em> thickness. Boards sold surfaced (S2S/S4S) are planed thinner — a 4/4 board is often about 13/16″ — but dealers generally still price by the nominal thickness, so use the quarter size you are buying, not the planed thickness.</p>
<p>Real boards come in random widths and lengths, dealers may round up each board, and some charge extra for narrow, short or wide stock, so buy 10–20% more than your cut list needs to cover waste. Treat this calculator's board feet as a planning number and confirm with your dealer.</p>
<h2>About the cost estimate</h2>
<p>If you pick a species, the estimate multiplies your board feet by the <b>median</b> of the dealer-posted prices on this site for that species (customer-reported prices are excluded). That median blends different thicknesses, grades, rough and surfaced stock, and dealers in different states, so your actual price could be well above or below it. See the species pages for breakdowns, and <b>call the dealer</b> for a real quote.</p>
<p>Species pages: {species_links('../')}</p><p>State pages: {state_links('../')}</p>
<script>{CALCJS}</script>"""
ctitle="Board Foot Calculator (Free) – Lumber Board Feet & Cost Estimate | BoardFoot Index"
cdesc="Free board foot calculator: enter thickness (inches or quarters like 4/4), width, length and quantity to get board feet, plus an optional cost estimate from real dealer-posted prices."
write('board-foot-calculator',shell(ctitle,cdesc,'board-foot-calculator/',cbody))

open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{u}</loc><lastmod>2026-10-16</lastmod></url>\n' for u in urls)+'</urlset>\n')
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
nav='<!--SPECIES-->'+'<p><b>Prices by species:</b> '+' · '.join(f'<a href="{slug(s)}-price-per-board-foot/">{s}</a>' for s in species)+'</p><p><b>Prices by state:</b> '+state_links('')+'</p><p><b>Free tool:</b> <a href="board-foot-calculator/">Board foot calculator</a></p><!--/SPECIES-->'
idx=re.sub(r'<!--SPECIES-->.*?<!--/SPECIES-->','',idx,flags=re.S).replace('<p id="summary"',nav+'<p id="summary"',1)
open('index.html','w').write(idx)
print(len(urls))
