# North American Hardwood Dealers (/directory/). Executed by build_pages.py
# (shares that file's globals: csv, re, dealers, dname, place_name, tel, e,
#  quote_plus, DCSS, contact_html, write, shell).
ND=list(csv.DictReader(open('directory/dealers-directory.csv')))
_ND_STOP={'lumber','hardwood','hardwoods','wood','woods','products','sawmill','mill','millworks','fine','group','supply'}
def _nd_tok(n):
  n=re.sub(r'\s*\((affiliate|FAS grade|[^)]*BF tier)\)$','',n,flags=re.I)
  n=n.lower(); n=re.sub(r"[.,'()/&+]",' ',n)
  n=re.sub(r'\b(inc|llc|ltd|ltee|co|company|corp|corporation|limited|the|of)\b','',n)
  return [t for t in n.split() if t]
def nd_index(name,st,city):
  ti=_nd_tok(name); sig=set(ti)-_ND_STOP; city=(city or '').lower(); best=None
  for full,d in dealers.items():
    if d['state']!=st: continue
    tr=_nd_tok(dname(full)); sr=set(tr)-_ND_STOP
    ok=(ti==tr) or (sig and sig==sr) or (sig and sr and (sig<=sr or sr<=sig))
    if not ok:
      ni,nr=' '.join(ti),' '.join(tr)
      if ni and nr and len(ni)>6 and len(nr)>6 and (ni in nr or nr in ni): ok=True
    if not ok: continue
    dcity=d['city'].lower(); city_ok=bool(city and dcity and (city in dcity or dcity in city))
    if city_ok or ti==tr or (sig and sig==sr):
      cand=(city_ok, dname(full), full)
      if best is None or cand>best: best=cand
  return best
_ND_CAT_SLUG={'Retail hardwood dealers':'retail','Wholesalers and distributors':'wholesale','Small businesses and independents':'independent','Hobbyist and woodworking suppliers':'hobbyist','Sawmills':'sawmill'}
_ND_CAT_ORDER=['Retail hardwood dealers','Wholesalers and distributors','Small businesses and independents','Hobbyist and woodworking suppliers','Sawmills']
_ND_CC={'United States':'US','Canada':'CA'}
def nd_sort(d):
  return (0 if d['country']=='United States' else 1, place_name(d['state_prov']), re.sub(r'^the\s+','',d['name'],flags=re.I).lower())
ND.sort(key=nd_sort)
def nd_card(d):
  st=d['state_prov']; pl=place_name(st); cc=_ND_CC.get(d['country'],d['country'])
  cat=d['category']; slug=_ND_CAT_SLUG.get(cat,'other')
  line2=f"{e(d['city'])}, {st}"+(f" {e(d['postal'])}" if d['postal'] else '')
  addr=(f"{e(d['address'])}<br>{line2}" if d['address'] else f"{line2}<br><small>Street address not published</small>")
  qparts=[d['name'],d['city'],st,pl,d['country'],cat]
  if d['trade_only']=='yes': qparts.append('trade wholesale only')
  hit=nd_index(d['name'],st,d['city'])
  aff=bool(hit and is_aff(hit[2]))
  site=d.get('website') or ''
  site_rel='noopener'
  if aff and AFF and AFF.get('url'):
    site=AFF['url']; site_rel='sponsored noopener'
  ct=[]
  if d['phone']: ct.append('Phone: '+tel(d['phone']))
  if d['toll_free']: ct.append('Toll-free: '+tel(d['toll_free']))
  if d['fax']: ct.append('Fax: '+e(d['fax']))
  for em in [x.strip() for x in (d['email'] or '').split(';') if x.strip()]:
    ct.append(f'Email: <a href="mailto:{e(em)}">{e(em)}</a>')
  links=[]
  if site: links.append(f'<a href="{e(site)}" rel="{site_rel}">Website</a>')
  if d['contact_form']: links.append(f'<a href="{e(d["contact_form"])}" rel="noopener">Contact form</a>')
  if d['address'] or d['city']:
    mq=d['name']+', '+(d['address']+', ' if d['address'] else '')+d['city']+', '+st+(' '+d['postal'] if d['postal'] else '')
    links.append(f'<a href="https://www.google.com/maps/search/?api=1&amp;query={quote_plus(mq)}" target="_blank" rel="noopener">Map</a>')
  badges=''
  if aff:
    badges+=aff_badge('../')
  if hit:
    q=quote_plus(hit[1])
    badges+=f' <a class="d-prices" href="../dealers/?q={e(q)}" title="Posted board-foot prices on BoardFoot Index">See prices</a>'
  if d['trade_only']=='yes':
    badges+=' <span class="d-trade">Trade/wholesale only</span>'
  src=d.get('verification_source') or d.get('website') or ''
  src_html=(f'From the <a href="{e(src)}" rel="nofollow noopener">dealer&rsquo;s website</a>, checked {e(d["checked_date"])}.' if src
            else f'From the dealer&rsquo;s website, checked {e(d["checked_date"])}.')
  other=(f'<p class="d-note">{e(d["other"])}</p>' if d.get('other') else '')
  return (f'<div class="dcard" data-c="{cc}" data-s="{e(st)}" data-cat="{slug}" data-q="{e(" ".join(qparts).lower())}">'
          f'<h3>'+(f'<a href="{e(site)}" rel="{site_rel}">{e(d["name"])}</a>' if site else e(d['name']))+badges+'</h3>'
          f'<p class="d-loc">{e(d["city"])}, {e(pl)} · {e(cat)}</p>'
          f'<p class="d-addr">{addr}</p>'
          +(f'<p class="d-ct">{"<br>".join(ct)}</p>' if ct else '')
          +other
          +(f'<p class="d-links">{" · ".join(links)}</p>' if links else '')
          +f'<p class="d-src"><small>{src_html}</small></p></div>')
nd_us=sum(1 for d in ND if d['country']=='United States')
nd_ca=len(ND)-nd_us
nd_states=[]
for d in ND:
  if d['state_prov'] not in nd_states: nd_states.append(d['state_prov'])
def nd_optgroup(country, code):
  sts=[s for s in nd_states if any(d['state_prov']==s and d['country']==country for d in ND)]
  opts=''.join(f'<option value="{s}" data-c="{code}">{e(place_name(s))} ({sum(1 for d in ND if d["state_prov"]==s)})</option>' for s in sts)
  return f'<optgroup label="{e(country)}">{opts}</optgroup>'
nd_state_opts=nd_optgroup('United States','US')+nd_optgroup('Canada','CA')
nd_cat_opts=''.join(f'<option value="{_ND_CAT_SLUG[c]}">{e(c)} ({sum(1 for d in ND if d["category"]==c)})</option>' for c in _ND_CAT_ORDER if any(d['category']==c for d in ND))
NDCSS=DCSS+'''<style>#dfilter{row-gap:.55rem}.dcard h3 a.d-prices{display:inline-block;font-size:.75rem;font-weight:700;background:#7a4a1e;color:#fff;border-radius:3px;padding:.18em .5em;margin-left:.4em;text-decoration:none;vertical-align:middle;white-space:nowrap}.dcard h3 a.d-prices:hover,.dcard h3 a.d-prices:focus{color:#fff;text-decoration:underline}.d-trade{display:inline-block;font-size:.75rem;font-weight:600;background:#eee8df;color:#5b4a3a;border:1px solid #c9b59c;border-radius:3px;padding:.15em .45em;margin-left:.35em;vertical-align:middle;white-space:nowrap}#dfilter select{max-width:100%}@media (max-width:640px){#dfilter label,#dfilter select{flex-basis:100%}}</style>'''
NDJS='''(function(){var country=document.getElementById('dcountry'),state=document.getElementById('dstate'),cat=document.getElementById('dcat'),inp=document.getElementById('dsearch'),cards=document.querySelectorAll('.dcard'),cnt=document.getElementById('dcount'),none=document.getElementById('dnone'),tot=cards.length;
function stateLabel(){var o=state.options[state.selectedIndex];return o&&o.value?o.text.replace(/ \\(\\d+\\)$/,''):'';}
function apply(){var c=country.value,s=state.value,k=cat.value,t=inp.value.trim().toLowerCase(),w=t?t.split(/\\s+/):[],n=0;
Array.prototype.forEach.call(state.options,function(o){if(!o.value)return;var cc=o.getAttribute('data-c');o.hidden=!!(c&&cc&&cc!==c);});
if(s&&state.selectedOptions[0]&&state.selectedOptions[0].hidden){state.value='';s='';}
cards.forEach(function(card){var q=' '+(card.getAttribute('data-q')||'');var on=(!c||card.getAttribute('data-c')===c)&&(!s||card.getAttribute('data-s')===s)&&(!k||card.getAttribute('data-cat')===k)&&w.every(function(x){return q.indexOf(' '+x)>-1});card.hidden=!on;if(on)n++;});
var msg=(n===tot?'Showing all '+tot+' dealers':'Showing '+n+' of '+tot+' dealers');
if(c)msg+=' in '+(c==='US'?'the United States':'Canada');if(s)msg+=' — '+stateLabel();
cnt.textContent=msg;none.hidden=n>0;
var u=new URL(location.href);function set(key,val){if(val)u.searchParams.set(key,val);else u.searchParams.delete(key);}
set('country',c);set('state',s);set('cat',k);set('q',t?inp.value.trim():'');history.replaceState(null,'',u);}
var p=new URLSearchParams(location.search);
if(p.get('country')&&country.querySelector('option[value="'+p.get('country')+'"]'))country.value=p.get('country');
var st=(p.get('state')||'').toUpperCase();if(st&&state.querySelector('option[value="'+st+'"]'))state.value=st;
if(p.get('cat')&&cat.querySelector('option[value="'+p.get('cat')+'"]'))cat.value=p.get('cat');
if(p.get('q'))inp.value=p.get('q');
country.addEventListener('change',apply);state.addEventListener('change',apply);cat.addEventListener('change',apply);
inp.addEventListener('input',apply);inp.addEventListener('search',apply);apply();})();'''
ndbody=f'''{NDCSS}<h1>North American Hardwood Dealers</h1>
<p>A contact directory of hardwood lumber dealers in the United States and Canada, for anyone buying lumber &mdash; hobbyists, trades, and businesses. {len(ND)} listings ({nd_us} in the United States, {nd_ca} in Canada) are shown here because we verified their contact details on the company&rsquo;s own website. For posted board-foot prices, use <a href="../dealers/">Board-Foot Prices</a>.</p>
<p>Last reviewed November 2026. We review this list twice a year.</p>
<p><a href="dealers-directory.csv" download>Download spreadsheet (CSV)</a></p>
<div class="box" id="dfilter">
<input type="search" id="dsearch" placeholder="Search by name, city, or state" autocomplete="off" aria-label="Search dealers by name, city, or state">
<label for="dcountry"><b>Country:</b></label> <select id="dcountry"><option value="">United States and Canada</option><option value="US">United States ({nd_us})</option><option value="CA">Canada ({nd_ca})</option></select>
<label for="dstate"><b>State / province:</b></label> <select id="dstate"><option value="">All states and provinces</option>{nd_state_opts}</select>
<label for="dcat"><b>Type:</b></label> <select id="dcat"><option value="">All types</option>{nd_cat_opts}</select>
<span id="dcount" aria-live="polite">Showing all {len(ND)} dealers</span>
</div>
<p id="dnone" hidden>No dealers match. Try a different spelling, or set the filters to show all dealers.</p>
<div class="dgrid">{"".join(nd_card(d) for d in ND)}</div>
<p>Know a dealer we missed, or spot a wrong address or phone number? Contact us: {contact_html()}. Dealers already on the Index have a <b>See prices</b> badge.</p>
<script>{NDJS}</script>'''
write('directory',shell("North American Hardwood Dealers | BoardFoot Index",f"Contact information for {len(ND)} website-verified hardwood lumber dealers across the United States and Canada, organized by type and location. Prices are listed on the Board-Foot Prices page.",'directory/',ndbody))
HOME_NA=f'<p><b>North American Hardwood Dealers:</b> a contact directory of {len(ND)} website-verified hardwood lumber dealers in the United States and Canada, for anyone buying lumber. <a href="directory/">Browse the directory</a></p>'
