import csv,re,os,statistics as S,html
BASE='https://ekoncepts.github.io/boardfoot-index/'
rows=list(csv.DictReader(open('seed.csv')))
for r in rows:r['p']=float(r['price_per_bf'])
def is_cust(r):return not r['source_url'].startswith('http')
cust_all=[r for r in rows if is_cust(r)]
rows=[r for r in rows if not is_cust(r)]   # medians, ranges, tips and tables use dealer-posted prices only
dealers={}
for _r in csv.DictReader(open('dealers.csv')): dealers[_r['dealer']]=_r
for _d in {r['dealer'] for r in rows}:
  if _d not in dealers: print('WARNING: no dealers.csv entry for',_d)
# ---- affiliate partner (The Knotty Lumber Co.). The tracking URL lives in monetization/affiliate.json (gitignored), never in seed/dealers data ----
import json
AFF=None
for _p in ('monetization/affiliate.json','/workspace/boardfoot/monetization/affiliate.json'):
  if os.path.exists(_p): AFF=json.load(open(_p)).get('knotty'); break
if not AFF: print('WARNING: monetization/affiliate.json not found; affiliate Buy links omitted')
def is_aff(dn):return dealers.get(dn,{}).get('affiliate','').strip().lower()=='yes'
BADGE_STYLE='font-size:.75rem;background:#fff3d6;border:1px solid #e5d8c7;border-radius:3px;padding:0 .35em;white-space:nowrap;text-decoration:none'
def aff_badge(pre):return f' <a href="{pre}affiliate-disclosure/" title="Affiliate partner: we earn a commission on orders placed through our Knotty link. It never changes prices, medians or sort order." style="{BADGE_STYLE}">Affiliate partner</a>'
def buy_link():
  return f'<a href="{html.escape(AFF["url"])}" rel="sponsored noopener">Buy at Knotty (affiliate link)</a>' if AFF else ''
def aff_note(pre):
  if not AFF: return ''
  return f'<p style="background:#fff3d6;border:1px solid #e5d8c7;border-radius:4px;padding:.5rem .75rem"><b>Affiliate partner:</b> The Knotty Lumber Co. is an affiliate partner. If you order through {buy_link()}, we earn a {html.escape(AFF["commission"])} commission at no extra cost to you. Knotty ships from Canada (Hamilton, Ontario), so US buyers may owe import duties, tariffs or brokerage fees that are not included in the listed prices. That never changes prices, medians, ranges or sort order. <a href="{pre}affiliate-disclosure/">Affiliate disclosure</a>.</p>'
def ship_label(dn):return dealers.get(dn,{}).get('ships','Not stated')
def ship_note(dn):return dealers.get(dn,{}).get('shipping_note','No shipping information recorded')
def ship_td(dn,attrs=''):return f'<td{attrs} title="{html.escape(ship_note(dn))}">{html.escape(ship_label(dn))}</td>'
# ---- mobile layout: wide tables become stacked cards (class "cards", via CSS in index.html <style>) or scroll in a .tw wrapper ----
def L(label):return f' data-label="{html.escape(label)}"'
def wrap_tables(s):
  return re.sub(r'<table(?![^>]*class="cards)([^>]*)>(.*?)</table>',lambda m:'<div class="tw"><table'+m.group(1)+'>'+m.group(2)+'</table></div>',s,flags=re.S)
def ship_info_table(dnames,pre='../'):
  trs=''
  for dn in sorted(set(dnames)):
    d=dealers.get(dn)
    if not d: continue
    trs+=f'<tr><td{L("Dealer")}>{html.escape(dn)}</td><td{L("Location")}>{html.escape(d["city"])}, {d["state"]}</td><td{L("Ships?")}>{html.escape(d["ships"])}</td><td{L("What the dealer\'s site says")}>{html.escape(d["shipping_note"])}</td><td{L("Where we found it")}><a href="{html.escape(d["shipping_source_url"])}" rel="nofollow noopener">source</a> ({d["date_checked"]})'+((' &middot; '+buy_link()+' <small>(<a href="'+pre+'affiliate-disclosure/">disclosure</a>)</small>') if is_aff(dn) and AFF else '')+'</td></tr>'
  return '<table class="cards lab"><thead><tr><th>Dealer</th><th>Location</th><th>Ships?</th><th>What the dealer\'s site says</th><th>Where we found it</th></tr></thead><tbody>'+trs+'</tbody></table>'
SHIPNOTE='<p><small>Shipping details come from each dealer\'s own site as of the date shown; &ldquo;Not stated&rdquo; means we found no shipping policy, not that the dealer does not ship. Always confirm with the dealer.</small></p>'
# ---- site footer + info pages (About / Privacy / Affiliate disclosure) ----
CONTACT_EMAIL='boardfootindex@gmail.com'
UPDATED='October 17, 2026'
PRIVACY_UPDATED='October 20, 2026'
# ---- analytics (GoatCounter: cookieless, aggregate counts only) ----
ANALYTICS_SNIPPET='<script data-goatcounter="https://boardfootindex.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>'
def add_analytics(page):
  # insert exactly one copy just before the closing </body>
  page=page.replace(ANALYTICS_SNIPPET,'')
  i=page.rfind('</body>');assert i>=0
  return page[:i]+ANALYTICS_SNIPPET+'\n'+page[i:]
def footer(pre):
  return f'<footer id="sitefooter" style="margin-top:2rem;padding-top:1rem;border-top:1px solid #e5d8c7;font-size:.85rem"><a href="{pre}about/">About</a> · <a href="{pre}privacy/">Privacy</a> · <a href="{pre}affiliate-disclosure/">Affiliate disclosure</a></footer>'
def contact_html():
  if CONTACT_EMAIL: return f'<a href="mailto:{html.escape(CONTACT_EMAIL)}">{html.escape(CONTACT_EMAIL)}</a>'
  print('WARNING: CONTACT_EMAIL is not set; Privacy/About pages show a placeholder')
  return '<mark>[CONTACT EMAIL PLACEHOLDER &mdash; Harry to supply before publishing]</mark>'
idx=open('index.html').read()
idx=re.sub(r'<!--ANALYTICS-->.*?<!--/ANALYTICS-->\n?','',idx,flags=re.S).replace(ANALYTICS_SNIPPET,'')
style=re.search(r'<style>.*?</style>',idx,re.S).group(0)
# ---- logo / favicon / social image ----
def head_extra(pre):
  return (f'<!--LOGOHEAD--><link rel="icon" href="{pre}assets/favicon.ico" sizes="any"><link rel="icon" type="image/png" sizes="32x32" href="{pre}assets/favicon-32.png">'
          f'<link rel="apple-touch-icon" href="{pre}assets/apple-touch-icon.png"><meta name="theme-color" content="#fdf6ea">'
          f'<meta property="og:image" content="{BASE}assets/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
          f'<meta property="og:site_name" content="BoardFoot Index"><meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{BASE}assets/og-image.png"><!--/LOGOHEAD-->')
def logo_html(pre):
  return f'<a href="{pre or "./"}" class="sitelogo" style="display:inline-block;line-height:0"><img src="{pre}assets/logo.png" alt="BoardFoot Index" width="198" height="40" style="height:40px;width:auto;max-width:100%"></a>'
HX=head_extra('../')
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
pub_states=sorted([s for s,c in state_counts.items() if c>=MIN_STATE and s in STATE_NAMES],key=lambda s:STATE_NAMES[s])
skipped_states=sorted([(s,c) for s,c in state_counts.items() if c<MIN_STATE or s not in STATE_NAMES])
def sslug(s):return STATE_NAMES[s].lower().replace(' ','-')+'-hardwood-lumber-prices'
state_links=lambda pre,ex=None:' · '.join(f'<a href="{pre}{sslug(s)}/">{STATE_NAMES[s]}</a>' for s in pub_states if s!=ex)
species=sorted({r['species'] for r in rows})
# ---- shared number formatting: every page (and the calculator) rounds medians/prices through fmt2, so they always agree ----
def fmt2(x):return f"{x:.2f}"
def money(x):return '$'+fmt2(x)
# ---- place counting: US states and Canadian provinces are counted separately ("15 states plus Ontario") ----
PROV_NAMES={'AB':'Alberta','BC':'British Columbia','MB':'Manitoba','NB':'New Brunswick','NL':'Newfoundland and Labrador','NS':'Nova Scotia','ON':'Ontario','PE':'Prince Edward Island','QC':'Quebec','SK':'Saskatchewan'}
def places_text(codes):
  codes=set(codes); us=[c for c in codes if c not in PROV_NAMES]; ca=sorted(PROV_NAMES[c] for c in codes if c in PROV_NAMES)
  parts=[f"{len(us)} state{'' if len(us)==1 else 's'}"] if us else []
  if ca: parts.append((' and '.join(ca) if len(ca)<=2 else f"{len(ca)} Canadian provinces"))
  return ' plus '.join(parts)
def stat(ps):return money(S.median(ps)),f"{money(min(ps))}–{money(max(ps))}",len(ps)
urls=[BASE]
for sp in species:
  a=sorted([r for r in rows if r['species']==sp],key=lambda r:r['p'])
  ps=[r['p'] for r in a];med,rng,n=stat(ps)
  states=sorted({r['state'] for r in a})
  thk=sorted({r['thickness'] for r in a},key=lambda t:(t=='not stated',float(t.split('/')[0])/4 if '/' in t else 0))
  trows=''.join(f"<tr><td>{t}</td><td>{'</td><td>'.join(map(str,stat([r['p'] for r in a if r['thickness']==t])))}</td></tr>" for t in thk)
  srows=''.join(f"<tr><td>{c}</td><td>{'</td><td>'.join(map(str,stat([r['p'] for r in a if cls(r)==c])))}</td></tr>" for c in ['Rough','Surfaced','Not stated'] if any(cls(r)==c for r in a))
  drows=''.join(f"<tr data-p=\"{r['p']}\" data-d=\"{e(r['dealer'])}\" data-s=\"{r['state']}\"><td class=\"c-th\">{e(r['thickness'])}</td><td class=\"c-su\">{e(r['surfacing'])}</td><td class=\"c-pr\">${r['p']:.2f}</td><td class=\"c-de\"><a href=\"{e(r['source_url'])}\" rel=\"nofollow noopener\">{e(r['dealer'])}</a>{aff_badge('../') if is_aff(r['dealer']) else ''}</td><td class=\"c-lo\">{e(r['city'])}, {r['state']}</td>{ship_td(r['dealer'],' class=\"c-sh\"')}<td class=\"c-ck\">{r['date_checked']}</td></tr>" for r in a)
  ca=sorted([r for r in cust_all if r['species']==sp],key=lambda r:(r['thickness'],r['p']))
  cust=''
  if ca:
    crow=''.join(f"<tr><td{L('Thick')}>{e(r['thickness'])}</td><td{L('Notes')}>{e(r['surfacing'])}</td><td{L('$/BF')}>${r['p']:.2f}</td><td{L('Dealer')}>{e(r['dealer'])}</td><td{L('Location')}>{e(r['city'])}, {r['state']}</td><td{L('Source')}>customer-reported</td></tr>" for r in ca)
    cust=f'<h2>Customer-reported small-piece prices</h2><p>These came from a real order at {e(ca[0]["dealer"])}: small S4S (surfaced, unfinished) pieces sold per piece, converted to $/bf using <em>nominal</em> size (nominal thickness × nominal width × length ÷ 12). Real boards are slightly smaller than nominal, so these run higher per bf than dealer-posted board-foot prices. They are <b>not</b> included in the medians, ranges or tips above.</p><table class="cards lab"><thead><tr><th>Thick</th><th>Notes</th><th>$/BF</th><th>Dealer</th><th>Location</th><th>Source</th></tr></thead><tbody>{crow}</tbody></table>'
  tips=[f"The lowest posted price we found was ${a[0]['p']:.2f}/bf ({a[0]['thickness']}{'' if a[0]['surfacing']=='not stated' else ', '+a[0]['surfacing']}) at {a[0]['dealer']} in {a[0]['city']}, {a[0]['state']}; the highest was ${a[-1]['p']:.2f}/bf."]
  ro=[r['p'] for r in a if cls(r)=='Rough'];su=[r['p'] for r in a if cls(r)=='Surfaced']
  if ro and su:
    if S.median(ro)<S.median(su): tips.append(f"Rough-sawn median ${S.median(ro):.2f} vs surfaced median ${S.median(su):.2f} in our data (mixed dealers and grades) — rough is cheaper per bf if you can mill it yourself.")
    else: tips.append(f"Rough-sawn median ${S.median(ro):.2f} vs surfaced median ${S.median(su):.2f} in our data — rough was not cheaper here because dealers, grades and regions differ; compare like with like.")
  elif ro: tips.append(f"Rough-sawn listings median ${S.median(ro):.2f}/bf; rough needs jointing and planing before use.")
  th4=[r['p'] for r in a if r['thickness']=='4/4'];th8=[r['p'] for r in a if r['thickness']=='8/4']
  if th4 and th8: tips.append(f"8/4 median ${S.median(th8):.2f} vs 4/4 median ${S.median(th4):.2f} per bf — thicker stock costs {'more' if S.median(th8)>S.median(th4) else 'about the same or less'} per board foot here.")
  if any('100-249' in r['dealer'] for r in a): tips.append("Wood Vendors prices shown are its 100–249 bf tier; that dealer lists lower per-bf prices for larger orders.")
  if any(is_aff(r['dealer']) for r in a): tips.append("The Knotty Lumber Co. ships from Hamilton, Ontario, Canada. Its prices here are as shown on its US storefront in US dollars (no conversion by us), and US buyers may owe import duties, tariffs or brokerage fees that are not included in the listed prices.")
  tips.append(f"Only {n} prices from {places_text(states)} so far — always call the dealer to confirm, and report what you pay to improve this page.")
  others=' · '.join(f'<a href="../{slug(o)}-price-per-board-foot/">{o}</a>' for o in species if o!=sp)
  title=f"{sp} Price per Board Foot (2026): Real Dealer Prices | BoardFoot Index"
  desc=f"{sp} lumber costs a median {med}/bf across {n} posted dealer prices ({rng}) in {', '.join(states)}. See prices by thickness, rough vs surfaced, and sources."
  out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{slug(sp)}-price-per-board-foot/">{style}{HX}</head><body>
<p>{logo_html("../")}</p><h1>{sp} price per board foot</h1>
<p>How much does {sp.lower()} lumber cost? Across {n} publicly posted dealer prices checked in October 2026, {sp.lower()} has a median of <b>{med}</b> per board foot, ranging {rng}. Data comes from dealer price sheets in {', '.join(states)}; every price links to its source.</p>
<h2>By thickness</h2><table><thead><tr><th>Thickness</th><th>Median</th><th>Range</th><th>Prices</th></tr></thead><tbody>{trows}</tbody></table>
<h2>Rough vs surfaced</h2><table><thead><tr><th>Surfacing</th><th>Median</th><th>Range</th><th>Prices</th></tr></thead><tbody>{srows}</tbody></table>
<h2>All {sp.lower()} prices</h2>{aff_note('../') if any(is_aff(r['dealer']) for r in a) else ''}<p><label>Sort by <select id="sortby"><option value="price">Price (cheapest first)</option><option value="dealer">Dealer (A to Z)</option><option value="state">State (A to Z, then dealer)</option></select></label></p><table id="alltbl" class="cards"><thead><tr><th>Thick</th><th>Surfacing</th><th>$/BF</th><th>Dealer</th><th>Location</th><th>Ships?</th><th>Checked</th></tr></thead><tbody>{drows}</tbody></table>
<h3>Do these dealers ship?</h3>{ship_info_table([r['dealer'] for r in a])}{SHIPNOTE}
<script>{SORTJS}</script>
{cust}<h2>Buying tips from the data</h2><ul>{''.join(f"<li>{e(t)}</li>" for t in tips)}</ul>
{report}
{kit}
<h2>Other species</h2><p>{others}</p>
<h2>{sp} prices by state</h2><p>{state_links('../')}</p>
<p>Need to know how many board feet a project takes? Try the <a href="../board-foot-calculator/">free board foot calculator</a>. Looking for {sp.lower()} in a certain thickness? <a href="../find-wood/?species={sp.replace(' ','+')}">Find which dealers carry it</a>.</p>{footer('../')}</body></html>'''
  os.makedirs(f'{slug(sp)}-price-per-board-foot',exist_ok=True)
  open(f'{slug(sp)}-price-per-board-foot/index.html','w').write(add_analytics(wrap_tables(out)))
  urls.append(f'{BASE}{slug(sp)}-price-per-board-foot/')

def shell(title,desc,path,body,depth_prefix='../'):
  return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">{style}{HX}</head><body>
<p>{logo_html(depth_prefix)}</p>{body}
{report}
{kit}
{footer(depth_prefix)}
</body></html>"""
def write(path,content):
  content=add_analytics(wrap_tables(content))
  os.makedirs(path,exist_ok=True);open(path+'/index.html','w').write(content);urls.append(BASE+path+'/')
species_links=lambda pre:' · '.join(f'<a href="{pre}{slug(s)}-price-per-board-foot/">{s}</a>' for s in species)

# ---- per-state pages ----
for st in pub_states:
  nm=STATE_NAMES[st]; a=[r for r in rows if r['state']==st]
  sps=sorted({r['species'] for r in a}); dealers_list=sorted({(r['dealer'],r['city']) for r in a})
  srows=''
  for sp in sps:
    ps=[r['p'] for r in a if r['species']==sp]; m,rg,n=stat(ps)
    srows+=f'<tr><td><a href="../{slug(sp)}-price-per-board-foot/">{sp}</a></td><td>{m}</td><td>{rg}</td><td>{n}</td></tr>'
  drows=''
  for dn,ct in dealers_list:
    da=[r for r in a if r['dealer']==dn and r['city']==ct]
    main=collections.Counter(r['source_url'] for r in da).most_common(1)[0][0]
    spl=[]
    for sp in sorted({r['species'] for r in da}):
      u=collections.Counter(r['source_url'] for r in da if r['species']==sp).most_common(1)[0][0]
      spl.append(f'<a href="{e(u)}" rel="nofollow noopener">{sp}</a>')
    drows+=f'<tr><td{L("Dealer")}><a href="{e(main)}" rel="nofollow noopener">{e(dn)}</a></td><td{L("Location")}>{e(ct)}, {st}</td>{ship_td(dn,L("Ships?"))}<td{L("Prices")}>{len(da)}</td><td{L("Species (links go to the source)")}>{", ".join(spl)}</td><td{L("Checked")}>{max(r["date_checked"] for r in da)}</td></tr>'
  allp=[r['p'] for r in a]; med,rng,n=stat(allp)
  meds={sp:S.median([r['p'] for r in a if r['species']==sp]) for sp in sps}
  lo=min(a,key=lambda r:r['p']); hi=max(a,key=lambda r:r['p'])
  cheap=min(meds,key=meds.get); dear=max(meds,key=meds.get)
  others=state_links('../',st)
  title=f"Hardwood Lumber Prices in {nm} (2026): Dealer Price per Board Foot | BoardFoot Index"
  desc=f"Real posted hardwood prices in {nm}: {n} dealer prices across {len(sps)} species from {len(dealers_list)} dealer{'s' if len(dealers_list)!=1 else ''}, ranging {rng} per board foot. Medians by species, sources and dates."
  body=f"""<h1>Hardwood lumber prices in {nm}</h1>
<p>We found {n} publicly posted hardwood prices from {len(dealers_list)} {nm} dealer{'s' if len(dealers_list)!=1 else ''}, covering {len(sps)} species. Across all species and thicknesses the median is <b>{med}</b> per board foot, ranging {rng}. Every figure below comes from a dealer's own price list or product page, checked in October 2026 — nothing is estimated.</p>
<p>In this data, {cheap} has the lowest species median in {nm} ({money(meds[cheap])}/bf) and {dear} the highest ({money(meds[dear])}/bf). The single lowest posted price is ${lo['p']:.2f}/bf ({lo['species']} {lo['thickness']}, {e(lo['dealer'])}); the highest is ${hi['p']:.2f}/bf ({hi['species']} {hi['thickness']}, {e(hi['dealer'])}).</p>
<h2>Median and range by species in {nm}</h2>
<table><thead><tr><th>Species</th><th>Median</th><th>Range</th><th>Prices</th></tr></thead><tbody>{srows}</tbody></table>
<p><small>Each row mixes thicknesses, grades and rough vs surfaced stock from that state's dealers, so use the <a href="../">searchable table</a> or the species pages for like-for-like comparisons.</small></p>
<h2>{nm} dealers with posted prices</h2>
<table class="cards lab"><thead><tr><th>Dealer</th><th>Location</th><th>Ships?</th><th>Prices</th><th>Species (links go to the source)</th><th>Checked</th></tr></thead><tbody>{drows}</tbody></table>
<h3>Do {nm} dealers ship?</h3>{ship_info_table([d for d,_ in dealers_list])}{SHIPNOTE}
<p>Prices change without notice and may differ by grade, width, length and quantity — call the dealer before you drive. Paid something different? Report it below.</p>
<h2>Estimate a project</h2><p>Use the <a href="../board-foot-calculator/">board foot calculator</a> to convert board dimensions to board feet and a rough cost, or <a href="../find-wood/?state={st}">find which dealers carry a species near you</a>.</p>
<h2>Other states</h2><p>{others}</p>
<h2>Prices by species</h2><p>{species_links('../')}</p>"""
  write(sslug(st),shell(title,desc,sslug(st)+'/',body))

# ---- calculator ----
def calc_opt(sp):
  ps=[r['p'] for r in rows if r['species']==sp]
  # value/lo/hi are the exact strings the species pages show (same stat()/fmt2 rounding), so the calculator can never disagree with them
  return f'<option value="{fmt2(S.median(ps))}" data-n="{len(ps)}" data-places="{e(places_text(r["state"] for r in rows if r["species"]==sp))}" data-lo="{fmt2(min(ps))}" data-hi="{fmt2(max(ps))}">{sp}</option>'
opts=''.join(calc_opt(sp) for sp in species)
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
 if(o.value){var m=+o.value,n=o.dataset.n;/* o.value is the species-page median already rounded to cents */
  est.innerHTML='<b>Estimated cost: about $'+(tot*m).toFixed(2)+'</b> ('+tot.toFixed(2)+' bf &times; $'+o.value+'/bf median). <em>This is only an estimate</em> based on the median of '+n+' dealer-posted '+o.text.toLowerCase()+' prices from '+o.dataset.places+' (range $'+o.dataset.lo+'&ndash;$'+o.dataset.hi+'/bf). Real prices depend on thickness, grade, rough vs surfaced, width, length and quantity &mdash; <b>call the dealer</b> for a quote.'}}
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

# ---- "Find this wood" page: species + thickness + location -> matching dealers (dealer-posted rows only) ----
def tq(t):return float(t.split('/')[0])/4 if '/' in t else None   # quarter sizes -> inches
def ships_far(lbl):l=lbl.lower();return l.startswith('yes') and 'local delivery only' not in l
FW_THK=['4/4','5/4','6/4','8/4','10/4','12/4','16/4']
for _t in {r['thickness'] for r in rows if '/' in r['thickness']}:
  if _t not in FW_THK: FW_THK.append(_t)
FW_THK.sort(key=tq)
fw_dn=sorted({r['dealer'] for r in rows})
fw_dealers=[{'n':dn,'c':dealers.get(dn,{}).get('city',''),'s':dealers.get(dn,{}).get('state',''),'sh':ship_label(dn),'sn':ship_note(dn),'far':ships_far(ship_label(dn)),'aff':bool(is_aff(dn) and AFF)} for dn in fw_dn]
fw_off=[]
_g=collections.defaultdict(list)
for r in rows:_g[(r['species'],r['thickness'],r['dealer'])].append(r)
for (sp,th,dn),rs in sorted(_g.items()):
  ps=[r['p'] for r in rs]
  fw_off.append({'sp':sp,'th':th,'d':fw_dn.index(dn),'p':fmt2(S.median(ps)),'n':len(ps),'lo':fmt2(min(ps)),'hi':fmt2(max(ps)),
    'su':'; '.join(sorted({r['surfacing'] for r in rs})),'u':collections.Counter(r['source_url'] for r in rs).most_common(1)[0][0],'dt':max(r['date_checked'] for r in rs)})
FW_JSON=json.dumps({'dealers':fw_dealers,'offers':fw_off},separators=(',',':')).replace('</','<\\/')
fw_places=''.join(f'<option value="{c}">{n}</option>' for c,n in sorted(STATE_NAMES.items(),key=lambda x:x[1]))
fw_prov=''.join(f'<option value="{c}">{n}</option>' for c,n in sorted(PROV_NAMES.items(),key=lambda x:x[1]))
fw_sp=''.join(f'<option value="{e(s)}">{e(s)}</option>' for s in species)
fw_th=''.join(f'<option value="{t}"{" selected" if t=="4/4" else ""}>{t} ({fmt2(tq(t)).rstrip("0").rstrip(".")}&Prime;)</option>' for t in FW_THK)
FW_AFF_TPL=(f'<template id="fw-aff">{aff_badge("../")} &middot; {buy_link()} <small>(<a href="../affiliate-disclosure/">disclosure</a>)</small></template>') if AFF else ''
FWCSS='''<style>#fw-form label{display:inline-block;margin:.15rem .4rem .15rem 0}#fw-form fieldset{border:1px solid #e5d8c7;border-radius:6px;margin:.6rem 0;padding:.4rem .7rem}#fw-form legend{font-size:.85rem;color:#5b4a3a;padding:0 .3rem}
.fw-grp{margin-top:1.4rem}.fw-grp h3{margin-bottom:.2rem}.fw-grp p.sub{margin:.1rem 0 .5rem;font-size:.85rem;color:#5b4a3a}.fw-note{background:#fff3d6;border:1px solid #e5d8c7;border-radius:4px;padding:.5rem .75rem}.fw-thk{font-size:.8rem;color:#7a4a1e;font-weight:600}td.c-es{white-space:nowrap}
@media (max-width:640px){#fw-form label{display:block}#fw-form select,#fw-form input[type=text]{max-width:100%}.cards td.c-es{order:6;margin-left:auto;font-weight:600}.cards td.c-es::before{content:"Est. ";font-weight:400}.cards td.c-lo{order:5;flex:0 1 auto}.cards td.c-de{order:4}.cards td.c-su{order:7}.cards td.c-sh{order:8;flex:1 0 100%}.cards td.c-ck{order:9}}</style>'''
FWJS=r"""(function(){
var D=JSON.parse(document.getElementById('fw-data').textContent);
function num(s){s=String(s).trim();if(!s)return NaN;var m;
 if(m=s.match(/^(\d+(?:\.\d+)?)\s+(\d+)\/(\d+)$/))return +m[1]+ +m[2]/ +m[3];
 if(m=s.match(/^(\d+)\/(\d+)$/))return +m[1]/ +m[2];
 if(/^\d*\.?\d+$/.test(s))return +s;return NaN}
function tq(t){var m=/^(\d+)\/4$/.exec(t);return m?+m[1]/4:NaN}
function esc(s){return String(s).replace(/[&<>"']/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]})}
var $=function(i){return document.getElementById(i)},aff=$('fw-aff'),ids=['fw-sp','fw-th','fw-st','fw-ship','fw-w','fw-l','fw-lu','fw-q','fw-bf'];
var NM={};[].forEach.call($('fw-st').options,function(o){if(o.value)NM[o.value]=o.text});
function grp(d,st){return st&&d.s===st?0:d.far?1:2}
function bfFor(stockT){/* board feet for one dealer: calculator math (thickness x width x length(ft) / 12 x qty) using the stock thickness you'd buy */
 var w=num($('fw-w').value),l=num($('fw-l').value),q=num($('fw-q').value||'1'),bf=num($('fw-bf').value),want=tq($('fw-th').value);
 if(w>0&&l>0&&q>0){var lf=$('fw-lu').value=='in'?l/12:l;return stockT*w*lf/12*q}
 if(bf>0)return bf*stockT/want;return NaN}
function row(o,st,showT){var d=D.dealers[o.d],bf=bfFor(tq(o.th)),pr='$'+o.p;
 var multi=o.n>1?' <small>(median of '+o.n+': $'+o.lo+'&ndash;$'+o.hi+')</small>':'';
 var loc=esc(d.c)+', '+d.s+(st&&d.s===st?' <small>(your '+(D.prov[st]?'province':'state')+')</small>':'');
 var link='<a href="'+esc(o.u)+'" rel="nofollow noopener">'+esc(d.n)+'</a>'+(d.aff&&aff?aff.innerHTML:'');
 var est=bf>0?'$'+(bf*+o.p).toFixed(2)+' <small>('+bf.toFixed(2)+' bf)</small>':'&mdash;';
 return '<tr><td class="c-th">'+o.th+(showT?' <span class="fw-thk">thicker</span>':'')+'</td><td class="c-pr">'+pr+multi+'</td><td class="c-de">'+link+'</td><td class="c-lo">'+loc+'</td><td class="c-sh" title="'+esc(d.sn)+'">'+esc(d.sh)+'</td><td class="c-su">'+esc(o.su)+'</td><td class="c-es">'+est+'</td><td class="c-ck">'+o.dt+'</td></tr>'}
function table(list,st,showT){return '<table class="cards"><thead><tr><th>Thick</th><th>$/BF</th><th>Dealer (links to the price source)</th><th>Location</th><th>Ships?</th><th>Surfacing / grade</th><th>Est. cost</th><th>Checked</th></tr></thead><tbody>'+list.map(function(o){return row(o,st,showT)}).join('')+'</tbody></table>'}
var GH=[['In your state','Closest option: you can likely pick up. Call ahead to confirm stock.'],['Dealers that ship','Their site says they ship (area in the Ships? column). Get a shipping quote; freight can add a lot on small orders.'],['Other dealers','Pickup only, local delivery only, or no shipping policy found. Worth a call if you are nearby.']];
function groups(list,st,showT){var out='',only=$('fw-ship').checked;
 for(var g=0;g<3;g++){if(only&&g==2)continue;var L=list.filter(function(o){return grp(D.dealers[o.d],st)==g});if(!L.length)continue;
  L.sort(function(a,b){return +a.p-+b.p||tq(a.th)-tq(b.th)||D.dealers[a.d].n.localeCompare(D.dealers[b.d].n)});
  out+='<div class="fw-grp"><h3>'+GH[g][0]+' ('+L.length+')</h3><p class="sub">'+GH[g][1]+'</p>'+table(L,st,showT)+'</div>'}
 return out}
function run(){var sp=$('fw-sp').value,th=$('fw-th').value,st=$('fw-st').value,only=$('fw-ship').checked,res=$('fw-res'),sum=$('fw-sum'),want=tq(th);
 var qs=new URLSearchParams();if(sp)qs.set('species',sp);if(th)qs.set('thickness',th);if(st)qs.set('state',st);if(only)qs.set('ships','1');
 try{history.replaceState(null,'',location.pathname+(qs.toString()?'?'+qs:''))}catch(e){}
 var need=sp+' '+th+(st?' near '+(NM[st]||st):'');
 $('fw-ask').href='mailto:"""+CONTACT_EMAIL+r"""?subject='+encodeURIComponent("Can't find: "+need)+'&body='+encodeURIComponent('Species: '+sp+'\nThickness: '+th+'\nSize / board feet needed: \nWhere I am: '+(st?NM[st]:'')+'\nAnything else (grade, rough or surfaced, quantity): \n');
 if(!sp){sum.innerHTML='Pick a species to see dealers.';res.innerHTML='';return}
 var w=num($('fw-w').value),l=num($('fw-l').value),q=num($('fw-q').value||'1'),bf=num($('fw-bf').value),dims='';
 if(w>0&&l>0&&q>0){var lf=$('fw-lu').value=='in'?l/12:l;dims=' Your cut: <b>'+(want*w*lf/12*q).toFixed(2)+' board feet</b> at '+th+' ('+q+' piece'+(q==1?'':'s')+'). Est. cost = board feet &times; that dealer\'s $/bf.'}
 else if(bf>0)dims=' You need <b>'+bf.toFixed(2)+' board feet</b> at '+th+'. Est. cost = board feet &times; that dealer\'s $/bf.';
 var all=D.offers.filter(function(o){return o.sp===sp}),keep=function(o){return !only||grp(D.dealers[o.d],st)<2};
 var ex=all.filter(function(o){return o.th===th}).filter(keep);
 /* thicker fallback: per dealer, the thinnest stock that is still thicker than requested */
 var best={};all.forEach(function(o){var t=tq(o.th);if(t>want&&keep(o)&&!ex.some(function(x){return x.d===o.d})&&(!best[o.d]||t<tq(best[o.d].th)))best[o.d]=o});
 var thick=Object.keys(best).map(function(k){return best[k]});
 var ns=all.filter(function(o){return o.th==='not stated'}).filter(keep);
 var h='';
 if(ex.length){h+=groups(ex,st,false);
  sum.innerHTML='<b>'+ex.length+' dealer'+(ex.length==1?'':'s')+'</b> list '+esc(sp.toLowerCase())+' at '+th+'.'+dims}
 else{var thinner=all.filter(function(o){return tq(o.th)<want}).filter(keep),tn={};thinner.forEach(function(o){tn[o.th]=1});
  sum.innerHTML='No dealer in our data lists '+esc(sp.toLowerCase())+' at exactly '+th+(only?' (among dealers in your area or that ship)':'')+'.'+(thick.length?' <b>'+thick.length+' dealer'+(thick.length==1?'':'s')+'</b> carry it thicker.':'')+dims;
  if(thick.length)h+='<p class="fw-note"><b>Thicker stock, can be resawn or cut to size.</b> These dealers list '+esc(sp.toLowerCase())+' thicker than '+th+'. Many yards will cut to size; otherwise plan to resaw or plane it down. You pay for the thicker board feet, and the estimate uses the thicker stock.</p>'+groups(thick,st,true);
  else h+='<p class="fw-note">No thicker '+esc(sp.toLowerCase())+' in our data either.'+(Object.keys(tn).length?' Thinner stock ('+Object.keys(tn).sort(function(a,b){return tq(a)-tq(b)}).join(', ')+') is listed, and two boards can be glued up to thickness.':'')+' Try another thickness, or tell us what you need (link below).</p>'}
 if(ns.length)h+='<div class="fw-grp"><h3>Thickness not stated ('+ns.length+')</h3><p class="sub">These dealers post a '+esc(sp.toLowerCase())+' price without a thickness. Ask what they have.</p>'+table(ns.sort(function(a,b){return +a.p-+b.p}),st,false)+'</div>';
 res.innerHTML=h}
ids.forEach(function(i){$(i).oninput=run;$(i).onchange=run});
var P=new URLSearchParams(location.search),setv=function(id,v){if(v==null)return;var s=$(id);[].forEach.call(s.options,function(o){if(o.value.toLowerCase()===String(v).toLowerCase())s.value=o.value})};
setv('fw-sp',P.get('species'));setv('fw-th',P.get('thickness'));setv('fw-st',(P.get('state')||'').toUpperCase());if(P.get('ships')==='1')$('fw-ship').checked=true;
run()})();"""
fbody=f"""{FWCSS}<h1>Find this wood</h1>
<p>Tell us what you're looking for and where you are. We'll list the dealers in our data that post a price for it, closest options first, with their price per board foot and a link to the dealer.</p>
<form id="fw-form" class="box" onsubmit="return false">
<label>Species <select id="fw-sp"><option value="">Choose a species</option>{fw_sp}</select></label>
<label>Thickness <select id="fw-th">{fw_th}</select></label>
<label>Where are you? <select id="fw-st"><option value="">Anywhere</option><optgroup label="US states">{fw_places}</optgroup><optgroup label="Canada">{fw_prov}</optgroup></select></label>
<label><input type="checkbox" id="fw-ship"> Only dealers in my state or that ship</label>
<fieldset><legend>Optional: how much do you need?</legend>
<label>Width (in) <input type="text" id="fw-w" size="5" inputmode="decimal" placeholder="6"></label>
<label>Length <input type="text" id="fw-l" size="5" inputmode="decimal" placeholder="8"></label> <select id="fw-lu" aria-label="Length unit"><option value="ft">feet</option><option value="in">inches</option></select>
<label>Pieces <input type="text" id="fw-q" size="3" inputmode="numeric" placeholder="1"></label>
<label>or board feet <input type="text" id="fw-bf" size="5" inputmode="decimal" placeholder="e.g. 20"></label>
</fieldset>
<p id="fw-sum" class="stat" aria-live="polite"></p>
</form>
<p style="font-size:.85rem;color:#5b4a3a"><b>Availability isn't live.</b> Prices and products come from each dealer's own site as of the &ldquo;Checked&rdquo; date. They're not a stock check or a quote, so confirm stock and price with the dealer before you buy or drive. Shipping info only reflects what the dealer's site says. Customer-reported prices are not included. Partner dealers are marked &ldquo;Affiliate partner&rdquo; and never change prices or sort order (<a href="../affiliate-disclosure/">disclosure</a>).</p>
<div id="fw-res" aria-live="polite"></div>
<p class="box"><b>Can't find it?</b> <a id="fw-ask" href="mailto:{CONTACT_EMAIL}">Tell us what you need</a> (species, size, where you are) and we'll look for dealers to add. Already bought some? Use the price report form below.</p>
<h2>How the results are sorted</h2>
<p>Dealers in your state come first, then dealers whose site says they ship, then everyone else (pickup only, local delivery only, or no shipping policy found). Within each group the cheapest price per board foot is first. When a dealer posts more than one price for the same species and thickness (different grades or surfacing), we show the median of those prices and the range. If you enter a size, the estimated cost uses the same math as the <a href="../board-foot-calculator/">board foot calculator</a>: thickness &times; width &times; length (ft) &divide; 12 &times; pieces, times that dealer's price.</p>
<p>Species pages: {species_links('../')}</p><p>State pages: {state_links('../')}</p>
{FW_AFF_TPL}<script type="application/json" id="fw-data">{FW_JSON}</script>
<script>{FWJS}</script>"""
FW_JSON=FW_JSON  # noqa
fbody=fbody.replace('"offers":','"prov":'+json.dumps({k:1 for k in PROV_NAMES})+',"offers":',1)
write('find-wood',shell("Find This Wood: Which Dealers Carry It, Near You | BoardFoot Index","Pick a hardwood species, thickness and your state to see which dealers post a price for it, nearest first, with price per board foot, shipping info and an estimated cost.",'find-wood/',fbody))

# ---- info pages ----
def info_page(title,desc,path,body):
  return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}{path}">{style}{HX}</head><body>
<p>{logo_html("../")}</p>{body}
{footer('../')}
</body></html>"""
CE=contact_html()
about_body=f"""<h1>About BoardFoot Index</h1>
<p>BoardFoot Index is a free price tracker for hardwood lumber. It shows what dealers charge per board foot, by species and by state, so woodworkers can see what a fair price looks like before they buy.</p>
<h2>Who runs it</h2>
<p>BoardFoot Index is run by Harry, a woodworking hobbyist. It is a small independent project, not a lumber dealer or a company that sells wood.</p>
<h2>Where the prices come from</h2>
<ul>
<li><b>Dealer-posted prices.</b> Most prices come from the public price lists and product pages of lumber dealers. Every one of these prices links back to the page it came from, with the date we checked it.</li>
<li><b>Customer-reported prices.</b> Woodworkers can report what they paid. Reports are reviewed before they appear, and they are labeled &ldquo;customer-reported.&rdquo; They are <b>excluded</b> from the medians, ranges and buying tips, which use dealer-posted prices only.</li>
<li><b>Shipping information.</b> The &ldquo;Ships?&rdquo; column only reflects what each dealer's own site says. &ldquo;Not stated&rdquo; means we found no shipping policy, not that the dealer won't ship.</li>
</ul>
<h2>Prices change: confirm with the dealer</h2>
<p>Lumber prices change without notice and can differ by grade, width, length, quantity and location. A price here is a snapshot from the date shown, not a quote. Please check with the dealer before you buy or drive anywhere. If you spot a wrong or out-of-date price, use the report form on the <a href="../">home page</a> or contact us.</p>
<h2>Neutrality</h2>
<p>Some links on this site may earn a commission, and dealers may one day pay for a featured spot. That money will never change a price, a median, a range or the order in which dealers are sorted. Paid placements will be labeled &ldquo;Sponsored.&rdquo; See the <a href="../affiliate-disclosure/">affiliate disclosure</a> for details.</p>
<h2>Contact</h2>
<p>Questions, corrections, or removal requests: {CE}. See also the <a href="../privacy/">privacy policy</a>.</p>"""
priv_body=f"""<h1>Privacy Policy</h1>
<p><small>Last updated {PRIVACY_UPDATED}.</small></p>
<p>This page explains what BoardFoot Index collects and who handles it. We keep it simple because the site does very little.</p>
<h2>How the site is hosted</h2>
<p>BoardFoot Index is a static website hosted on GitHub Pages. We do not run our own web server or database. GitHub, as the host, may log technical information about visits (such as IP address and browser) under its own <a href="https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement" rel="nofollow noopener">privacy statement</a>. We do not have access to that data as site analytics.</p>
<h2>Analytics and cookies</h2>
<p>We do not use advertising trackers, and we do not set our own cookies. The newsletter signup form loads a script from Kit (see below), which may set its own cookies or similar technology.</p>
<h3 id="visit-counts">Visit counts (GoatCounter)</h3>
<p>We use GoatCounter to count visits to this site anonymously. It uses no cookies, does not track you across other websites, and collects no personal information. Only aggregate counts, such as page views and which sites people came from, are kept. You can read <a href="https://www.goatcounter.com/help/privacy" rel="nofollow noopener">GoatCounter's privacy policy</a>.</p>
<h2>Price reports</h2>
<p>If you use the &ldquo;Report a price&rdquo; form, the details you type (species, thickness, surfacing, price per board foot, dealer, city, state and an optional link) are sent to a Google Apps Script run by the site owner and saved in a private Google Sheet, along with the date and time you sent it. The form does not ask for your name or email address, so please do not put personal details in the fields. Reports are reviewed before any appear on the site, and a published report shows the price, dealer and location, not who sent it. Google processes this data under its own <a href="https://policies.google.com/privacy" rel="nofollow noopener">privacy policy</a>.</p>
<h2>Newsletter</h2>
<p>If you subscribe to the Lumber Price Report, the email address you enter is collected and stored by Kit (formerly ConvertKit), our email service provider, under <a href="https://kit.com/privacy" rel="nofollow noopener">Kit's privacy policy</a>. We use it only to send the newsletter. Every email has an unsubscribe link, and you can unsubscribe at any time.</p>
<h2>What we do not do</h2>
<ul><li>We do not sell your data or share it for advertising.</li><li>We do not use your email address for anything except the newsletter you signed up for.</li></ul>
<h2>Links to other sites</h2>
<p>Prices link to dealer websites we do not control. Some links may be affiliate links (see the <a href="../affiliate-disclosure/">affiliate disclosure</a>). Each dealer's site has its own privacy practices. If you click an affiliate link, the dealer and its affiliate-tracking service may set cookies on their own site so that a purchase can be credited to us; we do not receive your personal information from them.</p>
<h2>Requesting access or removal</h2>
<ul>
<li><b>Newsletter:</b> use the unsubscribe link in any email to be removed from the list. To have your address deleted completely, contact us.</li>
<li><b>Price reports:</b> because the form does not collect your identity, we may not be able to tell which report is yours. Tell us the details of the report (species, price, dealer, approximate date) and we will delete it or remove it from the site.</li>
<li><b>Anything else:</b> contact us and we will respond and act on reasonable requests.</li>
</ul>
<p>Contact: {CE}</p>
<h2>Changes</h2>
<p>If we change this policy, we will update the date at the top of this page.</p>"""
disc_body=f"""<h1>Affiliate Disclosure</h1>
<p><small>Last updated {UPDATED}.</small></p>
<p>Plain version: <b>some links on BoardFoot Index may be affiliate links.</b> If you click one and buy something, the site may earn a small commission at no extra cost to you.</p>
<h2>What this means</h2>
<ul>
<li>We may join affiliate programs with lumber dealers, tool sellers and retailers. Where a link is an affiliate link, we aim to say so near the link or on the page.</li>
<li>Commissions help pay for running the site. They do not make anything cost more for you.</li>
</ul>
<h2>What commissions never change</h2>
<p>Affiliate commissions never affect the prices we list, the medians and ranges we calculate, which dealers appear, or the order in which they are sorted. Prices are copied from public dealer pages, and the sort options (price, dealer name, state) are the same for everyone. A dealer cannot pay to change its listed price or its position.</p>
<h2>Current affiliate partners</h2>
<ul><li><b>The Knotty Lumber Co.</b> (Hamilton, Ontario). We earn a 10% commission on qualifying orders placed through links labeled &ldquo;Buy at Knotty (affiliate link)&rdquo;. Knotty's prices are listed and counted exactly like every other dealer's, so the commission does not affect prices, medians, ranges or sort order. The commission is paid by Knotty and does not raise what you pay. Knotty ships from Canada, so US buyers may owe import duties, tariffs or brokerage fees, which are not included in the listed prices; see its shipping policy.</li></ul>
<p>Rows and dealer names for an affiliate partner are marked &ldquo;Affiliate partner.&rdquo;</p>
<h2>Sponsored listings</h2>
<p>If a dealer pays for a featured spot or other promotion, it will be clearly labeled <b>&ldquo;Sponsored.&rdquo;</b> Sponsored placements will be kept separate from the price tables and will not alter them.</p>
<h2>Amazon</h2>
<p>If we join the Amazon Associates program, we will add the required statement here: &ldquo;As an Amazon Associate we earn from qualifying purchases.&rdquo;</p>
<h2>Questions</h2>
<p>See the <a href="../about/">About page</a> and <a href="../privacy/">privacy policy</a>, or contact us: {CE}</p>"""
write('about',info_page('About BoardFoot Index | Who runs it and where the prices come from','BoardFoot Index is a free hardwood lumber price tracker run by Harry, a woodworking hobbyist. Learn where prices come from and how we stay neutral.','about/',about_body))
write('privacy',info_page('Privacy Policy | BoardFoot Index','What BoardFoot Index collects: price reports and newsletter signups, who handles them, and how to ask for removal.','privacy/',priv_body))
write('affiliate-disclosure',info_page('Affiliate Disclosure | BoardFoot Index','Some links on BoardFoot Index may be affiliate links. Commissions never change prices, medians or sort order, and paid placements are labeled Sponsored.','affiliate-disclosure/',disc_body))

open('sitemap.xml','w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{u}</loc><lastmod>2026-10-16</lastmod></url>\n' for u in urls)+'</urlset>\n')
open('robots.txt','w').write(f'User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n')
nav='<!--SPECIES-->'+'<p><b>Prices by species:</b> '+' · '.join(f'<a href="{slug(s)}-price-per-board-foot/">{s}</a>' for s in species)+'</p><p><b>Prices by state:</b> '+state_links('')+'</p><p><b>Free tools:</b> <a href="board-foot-calculator/">Board foot calculator</a> · <a href="find-wood/">Find this wood (which dealers carry it near you)</a></p><!--/SPECIES-->'
idx=re.sub(r'<!--SPECIES-->.*?<!--/SPECIES-->','',idx,flags=re.S).replace('<p id="summary"',nav+'<p id="summary"',1)
pd=sorted({r['dealer'] for r in rows}); 
blk='<!--DEALERS--><h2>Do these dealers ship?</h2>'+ship_info_table(pd,'')+SHIPNOTE+'<!--/DEALERS-->'
idx=re.sub(r'<!--DEALERS-->.*?<!--/DEALERS-->',lambda m:blk,idx,flags=re.S)
idx=re.sub(r'<!--FOOTER-->.*?<!--/FOOTER-->','',idx,flags=re.S).replace('</body>','<!--FOOTER-->'+footer('')+'<!--/FOOTER--></body>')
idx=re.sub(r'<!--LOGOHEAD-->.*?<!--/LOGOHEAD-->','',idx,flags=re.S).replace('</head>',head_extra('')+'</head>',1)
idx=re.sub(r'<!--LOGO-->.*?<!--/LOGO-->','',idx,flags=re.S).replace('<h1>BoardFoot Index</h1>','<!--LOGO-->'+'<p>'+logo_html('')+'</p><!--/LOGO-->'+'<h1>BoardFoot Index</h1>',1)
assert idx.count('</body>')==1,'index.html: expected one </body>'
idx=idx.replace('</body>','<!--ANALYTICS-->'+ANALYTICS_SNIPPET+'<!--/ANALYTICS--></body>')
open('index.html','w').write(idx)
print(len(urls))
