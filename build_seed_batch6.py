#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for dealer batch 6 (Monday 2026-11-23) to seed.csv and dealers.csv.
Sources saved under raw/batch6/ (gitignored). Same rules as earlier batches: only plain/flat-sawn stock at each dealer's standard grade
and smallest-quantity (retail) tier; quartersawn, rift, figured/curly/birdseye, ambrosia, wormy, rustic/knotty, #1/#2 Common, shorts,
cutoffs, wide-board premiums, live edge and per-linear-foot items are skipped. Mahogany rows only when the dealer says African mahogany.
Rock Creek Millworks (Ottawa KS) was dropped at re-verification: its inventory page prices are "$/ft." with no thickness, so board foot
vs linear foot can't be confirmed. Jubilee Specialty Woods (next in the stack) took its slot.
Idempotent: removes earlier rows for these dealers first. Appends with CRLF; existing lines are kept byte-for-byte."""
import csv,io,re,json,subprocess,sys,collections,statistics
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-11-23'; R='raw/batch6/'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany','Basswood','Alder']
rows=[]
def add(sp,th,su,p,dn,city,st,url):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),dealer=dn,city=city,state=st,source_url=url,date_checked=TODAY))
def txt(f): return re.sub(r'\s+',' ',BeautifulSoup(open(R+f,errors='replace').read(),'lxml').get_text(' '))
def pdf(f): return subprocess.run(['pdftotext','-layout',R+f,'-'],capture_output=True,text=True).stdout

# ---- 1. Hardwood Heaven, Lincoln NE: "LumberPrices 101223.pdf" linked from the home page, dated 10/12/2026,
#      "ALL PRICES ARE PER BOARD FOOT, UNLESS MARKED OTHERWISE". In-stock lumber is already surfaced (S3S unless noted). Over-9"-wide,
#      quartersawn, curly, rustic, 1/2 Com, knotty alder, cypress, cedar, beech, birch and pine skipped.
HH='Hardwood Heaven'; HHU='https://img1.wsimg.com/blobby/go/fd7169d2-1597-46a8-a51d-3ba853e6dfa7/LumberPrices%20101223.pdf'
ht=pdf('hh_cur.pdf'); assert '10/12/2026' in ht and 'ALL PRICES ARE PER BOARD FOOT' in ht and 'LumberPrices%20101223.pdf' in open(R+'hh.html').read()
hl=[re.sub(r'\.{3,}',' ',l) for l in ht.splitlines()]
def hh(sp,sec,lab,v,th,su='S3S'):
    i=next(k for k,l in enumerate(hl) if l.strip()==sec)
    ok=any(re.fullmatch(r'\s*'+re.escape(lab)+r'\s+\$'+re.escape(v)+r'\s*',hl[k]) for k in range(i+1,i+16)); assert ok,(sec,lab,v)
    add(sp,th,su+', Select & Better (list dated 10/12/2026)',v,HH,'Lincoln','NE',HHU)
hh('Alder','ALDER','4/4 Superior, S3S','7.25','4/4'); rows[-1]['surfacing']='S3S, Superior grade (list dated 10/12/2026)'
for th,v in [('4/4','6.25'),('5/4','7.50'),('8/4','8.75')]: hh('Ash','ASH',th+' S&B, S3S',v,th)
for th,v in [('4/4','5.95'),('5/4','5.95'),('8/4','8.95')]: hh('Basswood','BASSWOOD',th+' S&B, S3S',v,th)
hh('Basswood','BASSWOOD','16/4 S&B, S2S','9.95','16/4','S2S')
for th,v in [('4/4','6.25'),('5/4','7.25'),('6/4','7.75'),('8/4','8.50')]: hh('Cherry','CHERRY',th+' S&B, S3S',v,th)
hh('Hickory','HICKORY','4/4 S&B, S3S','5.75','4/4'); hh('Hickory','HICKORY','5/4 S&B, S4S','6.75','5/4','S4S')
for th,v in [('4/4','6.95'),('5/4','7.25'),('6/4','9.15'),('8/4','9.25')]: hh('Hard Maple','MAPLE, HARD',th+' S&B, S3S',v,th)
hh('Soft Maple','MAPLE, SOFT','4/4 S&B, S3S','7.25','4/4')
for th,v in [('4/4','4.85'),('5/4','4.45'),('6/4','6.65'),('8/4','7.45')]: hh('Red Oak','OAK, RED',th+' S&B, S3S',v,th)
for th,v in [('4/4','11.95'),('5/4','13.50'),('8/4','17.75')]: hh('White Oak','OAK, WHITE',th+' S&B, S3S',v,th)
for th,v in [('4/4','3.95'),('5/4','4.50'),('6/4','4.65'),('8/4','4.75')]: hh('Poplar','POPLAR',th+' S&B, S3S',v,th)
for th,v in [('4/4','18.50'),('5/4','21.00'),('8/4','21.00')]: hh('Walnut','WALNUT',th+' S&B, S3S',v,th)

# ---- 2. Capital Hardwood and Supply, Madison WI: Retail_Price_List_20261104.pdf "Prices as of November 4, 2026", "Prices per board foot".
#      Columns 4/4 5/4 6/4 8/4; under-50 BF price (8%/17% volume discounts not used). Rough unless S4S (+$1/bf). Natural walnut, #2 common
#      cherry, heart hickory, QS/rift, figured maple and QS sapele skipped.
CH='Capital Hardwood and Supply'; CHU='https://capitalhardwood.com/pages/in-store-price-list'
ct=pdf('cap.pdf'); assert 'Prices as of November 4, 2026' in ct and 'Prices per board foot' in ct and 'Retail_Price_List_20261104.pdf' in open(R+'cap.html').read()
COLS=['4/4','5/4','6/4','8/4']
def cap(sp,lab,grade,vals,note=''):
    m=re.search(r'^\s*'+re.escape(lab)+r'\s{2,}'+re.escape(grade)+r'\s+(.*)$',ct,re.M); assert m,(lab,grade)
    got=m.group(1).split(); assert len(got)==4 and [g.lstrip('$') for g in got]==[v or '-' for v in vals],(lab,got)
    for th,v in zip(COLS,vals):
        if v: add(sp,th,f'rough, {grade} (S4S +$1/bf; under-50 BF price; list as of Nov 4, 2026{note})',v,CH,'Madison','WI',CHU)
cap('Alder','Alder - Red','Superior',['5.45','','',''],'; red alder')
cap('Ash','Ash - White','Select & Better',['4.95','','','5.95'])
cap('Basswood','Basswood','Select & Better',['3.95','','','4.95'])
cap('Cherry','Cherry - American','4/4 FAS, 6/4 & 8/4 S&B',['5.95','','6.45','6.95'])
cap('Hickory','Hickory - Calico/Brown','Select & Better',['5.95','','','6.95'],'; calico/brown hickory')
cap('Hard Maple','Maple - Hard','Select & Better',['5.95','6.95','6.95','7.95'])
cap('Soft Maple','Maple- Soft','Select & Better',['4.95','','',''])
cap('Red Oak','Oak - Red','4/4 FAS, 8/4 S&B',['4.95','','5.95','5.95'])
cap('White Oak','Oak - White Flat Sawn','Select & Better',['8.95','','12.95','14.95'],'; flat sawn')
cap('Poplar','Poplar - Yellow','Select & Better',['3.95','','','4.45'])
cap('Walnut','Walnut - Black','Select & Better',['12.95','','','16.95'])
m=re.search(r'^\s*Mahagony - African\s+FEQ\s+\$9\.95\s+\$10\.95\s*$',ct,re.M); assert m
for th,v in [('4/4','9.95'),('8/4','10.95')]: add('Mahogany',th,'rough, FEQ (S4S +$1/bf; under-50 BF price; list as of Nov 4, 2026; African mahogany)',v,CH,'Madison','WI',CHU)

# ---- 3. Enndure, Ormond Beach FL: homepage inventory table fed by the public Google Sheet (Inventory tab, CSV export 2026-11-23).
#      "Most hardwoods are S2S, milled to nearest 15/16"". Only rows with a posted price; cutoffs, 90/10 rough, rustic, spalted skipped.
EN='Enndure'; ENU='https://enndure.com/'
inv={r['name'].strip():r for r in csv.DictReader(open(R+'enn.csv'))}
def en(sp,name,th,note=''):
    v=inv[name]['price']; assert v,name
    add(sp,th,'S2S to about 15/16" (live inventory sheet'+note+')',v,EN,'Ormond Beach','FL',ENU)
en('Cherry','4/4 Cherry','4/4'); en('Cherry','8/4 Cherry','8/4')
en('Hard Maple','4/4 Maple, Hard','4/4'); en('Hard Maple','8/4 Maple, Hard','8/4')
en('Red Oak','4/4 Oak, Red','4/4'); en('Red Oak','8/4 Oak, Red','8/4')
en('White Oak','4/4 Oak, White FAS KD','4/4','; FAS, KD'); en('White Oak','8/4 Oak, White FAS KD','8/4','; FAS, KD')
en('Poplar','4/4 Poplar','4/4'); en('Poplar','8/4 Poplar','8/4')
en('Sapele','4/4 Sapele','4/4'); en('Sapele','8/4 Sapele','8/4')
en('Walnut','4/4 Walnut, Black Premium','4/4','; premium grade'); en('Walnut','8/4 Walnut, Black Premium','8/4','; premium grade')

# ---- 4. Mount Vernon Hardwood, Mount Vernon OH: /inventory-pricing/ "Price List (Rough Sawn, Updated NOV 20th 2026)". Kiln dried, rough sawn.
#      Single-board price (100+ BF prices not used). Harry pre-approved 2026-11-10 despite the low-price flag. Rustic, shorts, skip-planed narrow,
#      ambrosia, sassafras and elm skipped.
MV='Mount Vernon Hardwood'; MVU='https://mountvernonhardwood.com/inventory-pricing/'
mt=txt('mv.html'); assert 'Updated NOV 20th 2026' in mt and 'All wood is kiln dried, rough sawn' in mt
def mv(sp,lab,v,th):
    assert re.search(re.escape(lab)+r' ?– ?\$'+re.escape(v)+r' ?/ ?BF',mt),(lab,v)
    add(sp,th,'kiln dried, rough sawn (list updated Nov 20, 2026)',v,MV,'Mount Vernon','OH',MVU)
for th in ['4/4','5/4']: mv('Walnut',th+' Black Walnut','6.69',th)
for th in ['6/4','8/4']: mv('Walnut',th+' Black Walnut','6.99',th)
mv('Hard Maple','4/4 Hard Maple','3.19','4/4'); mv('Hard Maple','6/4 Hard Maple','3.39','6/4'); mv('Hard Maple','8/4 Hard Maple','3.39','8/4')
mv('Red Oak','4/4 Red Oak','2.73','4/4')
mv('Cherry','4/4 Cherry','3.29','4/4'); mv('Cherry','5/4 Cherry','3.29','5/4'); mv('Cherry','6/4 Cherry','3.39','6/4')
assert '4/4 Sapele $7.99/BF' in mt; add('Sapele','4/4','kiln dried, rough sawn (list updated Nov 20, 2026)','7.99',MV,'Mount Vernon','OH',MVU)
mv('Hickory','4/4 Hickory','2.45','4/4'); mv('Poplar','4/4 Poplar','1.99','4/4')

# ---- 5. Advantage Lumber (Buffalo NY showroom; also Sarasota FL, Grover NC, Santa Fe Springs CA): Shopify catalog
#      (collections/domestic-hardwood and exotic-hardwood products.json, 2026-11-23). Random-width lumber sold by the board foot: the
#      "1 Board Foot / Rough" variant, or the single "Board Feet" quantity price. In-stock items only. S4S 1x/2x boards (per linear foot),
#      QS, curly, ambrosia, rustic, mill-run, #1 and ribbon skipped. +10% for lengths over 7 ft not applied.
AL='Advantage Lumber'; ALB='https://buy.advantagelumber.com/products/'
M={'Ash':'Ash','Basswood':'Basswood','Black Cherry':'Cherry','Hard Maple':'Hard Maple','Soft Maple':'Soft Maple','Hickory':'Hickory','Poplar':'Poplar','Red Oak':'Red Oak','White Oak':'White Oak','Walnut':'Walnut','Alder':'Alder','African Mahogany':'Mahogany','Sapele':'Sapele'}
seen=set()
for f in ['adv_dom.json','adv_exo.json']:
    for p in json.load(open(R+f))['products']:
        m=re.fullmatch(r'(\d+/4) (.+?) Lumber',p['title'].strip())
        if not m or m.group(2) not in M: continue
        th,sp=m.group(1),M[m.group(2)]
        v=[x for x in p['variants'] if x['title'] in ('1 Board Foot / Rough','1 Board Foot')] or ([p['variants'][0]] if len(p['variants'])==1 and p['variants'][0]['title']=='Default Title' else [])
        if not v or not v[0]['available']: continue
        assert (sp,th) not in seen,(sp,th); seen.add((sp,th))
        add(sp,th,'rough, random width, priced per board foot (1 BF price; +10% over 7 ft'+('; African mahogany' if sp=='Mahogany' else '')+')',v[0]['price'],AL,'Buffalo','NY',ALB+p['handle'])

# ---- 6. Northshore Woods, Mandeville LA: price-list image "NORTHSHORE WOODS PRICELIST 6/9/2026" on /lumber-price-list (read by eye,
#      raw/batch6/ns_full.png). "PRICES ARE CALCULATED BY THE BOARD FOOT", "These prices are Retail"; 10% off over 100 BF not used.
#      List "does not reflect current inventory". Genuine/Santos mahogany, slabs, QS white oak 5/8", pine and exotics skipped.
NS='Northshore Woods'; NSU='https://www.woodsnorthshore.com/lumber-price-list'
nt=txt('ns.html'); assert 'PRICES ARE CALCULATED BY THE BOARD FOOT' in nt and 'These prices are Retail' in nt
NSS='retail price list dated 6/9/2026 (surfacing not stated; list does not reflect current stock)'
for th,v in [('4/4','5'),('6/4','6'),('12/4','8')]: add('Hard Maple',th,NSS,v,NS,'Mandeville','LA',NSU)
for th in ['4/4','5/4','6/4','8/4','12/4','16/4']: add('Poplar',th,NSS,'3',NS,'Mandeville','LA',NSU)
for th,v in [('4/4','9'),('5/4','9'),('6/4','9'),('8/4','11')]: add('Walnut',th,NSS,v,NS,'Mandeville','LA',NSU)
for th,v in [('5/4','6'),('6/4','7'),('8/4','8')]: add('Sapele',th,NSS[:-1]+'; listed as Mahogany, Sapele)',v,NS,'Mandeville','LA',NSU)
for th,v in [('5/4','6'),('6/4','6')]: add('Mahogany',th,NSS[:-1]+'; African mahogany)',v,NS,'Mandeville','LA',NSU)

# ---- 7. Jubilee Specialty Woods, Summerdale AL: "Current Price List" on /retail/ -> Retail-Price-List-June-2026.pdf (dated 05.06.2026).
#      1-49 BF column. Kiln-dried, mostly rough-cut, random width. QS, guitar, ambrosia, curly, birdseye, Superior/wide walnut, rustic skipped.
JB='Jubilee Specialty Woods'; JBU='https://jubileespecialtywoods.com/wp-content/uploads/2026/06/Retail-Price-List-June-2026.pdf'
jt=pdf('jub.pdf'); assert '05.06.2026' in jt and 'Retail-Price-List-June-2026.pdf' in open(R+'jub.html').read()
JS='kiln dried, mostly rough, random width; 1-49 BF price (list dated 05.06.2026)'
def jb(sp,th,grade,v,note=''):
    assert re.search(r'(^|\s{2,})'+re.escape(th)+r'\s+'+re.escape(grade)+r'\s+'+re.escape(v)+r'\s',jt,re.M),(sp,th,grade,v)
    add(sp,th,JS[:-1]+'; '+grade+note+')',v,JB,'Summerdale','AL',JBU)
for th,v in [('4/4','4.65'),('6/4','4.88'),('8/4','5.60')]: jb('Ash',th,'FAS',v)
for th,v in [('4/4','4.96'),('8/4','6.90')]: jb('Cherry',th,'FAS',v)
for th,v in [('4/4','6.85'),('8/4','7.95')]: jb('Hard Maple',th,'FAS',v)
jb('Hickory','4/4','FAS','3.95')
for th,v in [('4/4','3.55'),('8/4','4.95')]: jb('Poplar',th,'FAS',v)
for th,v in [('4/4','3.95'),('8/4','5.45')]: jb('Red Oak',th,'FAS',v)
for th,v in [('4/4','6.50'),('8/4','7.25')]: jb('Soft Maple',th,'FAS',v)
for th,v in [('4/4','10.00'),('6/4','11.50'),('8/4','12.00')]: jb('Walnut',th,'FAS',v)
for th,v in [('4/4','8.00'),('6/4','10.50'),('8/4','11.00')]: jb('White Oak',th,'FAS',v)
for th,v in [('4/4','6.95'),('8/4','7.25')]: jb('Mahogany',th,'Select & Better',v,'; African mahogany')
for th,v in [('4/4','7.95'),('5/4','7.95'),('6/4','7.95'),('8/4','8.15'),('16/4','8.45')]: jb('Sapele',th,'Select & Better',v)

NEW=[HH,CH,EN,MV,AL,NS,JB]
old=[r for r in csv.DictReader(open('seed.csv')) if r['dealer'] not in NEW and not r['dealer'].startswith('Customer')]
by=collections.defaultdict(list)
for r in old: by[(r['species'],r['thickness'])].append(float(r['price_per_bf']))
for r in rows:
    a=by.get((r['species'],r['thickness'])); p=float(r['price_per_bf'])
    if not a: print('NO-COMPARE',r['dealer'],r['species'],r['thickness'],p); continue
    if p>max(a) or p<min(a): print('OUTSIDE',r['dealer'],r['species'],r['thickness'],p,'min',min(a),'med',statistics.median(a),'max',max(a))
if '--dry' in sys.argv:
    print(collections.Counter(r['dealer'] for r in rows),len(rows)); sys.exit()

HOLD=set(a for a in sys.argv[1:] if not a.startswith('--'))
rows=[r for r in rows if r['dealer'] not in HOLD]
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+d+',') in l or (',"'+d+'",') in l for d in NEW)]
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
dcols=list(csv.DictReader(open('dealers.csv')).fieldnames); dl=[d for d in csv.DictReader(open('dealers.csv')) if d['dealer'] not in NEW]
nd=[
 dict(dealer=HH,city='Lincoln',state='NE',ships='Not stated',shipping_note="No shipping policy found; retail store at 645 N 66th St. In-stock lumber is already surfaced (S3S unless noted); rough is special order. Boards with one straight edge get 5% added to the board-foot measure",shipping_source_url='https://hardwoodheaven.net/',date_checked=TODAY,affiliate=''),
 dict(dealer=CH,city='Madison',state='WI',ships='Not stated',shipping_note="Posted list is the in-store retail price list for the Madison shop (Mon-Fri 10-6, Sat 10-2); no shipping policy found for lumber. Prices shown are the under-50 BF price; 8% off at 50-99 BF and 17% off at 100-249 BF. S4S is $1/bf extra",shipping_source_url=CHU,date_checked=TODAY,affiliate=''),
 dict(dealer=EN,city='Ormond Beach',state='FL',ships='Not stated',shipping_note="No shipping policy found; warehouse open to the public Mon/Wed/Fri 9:30-5, Saturday by appointment. Call or text to confirm stock before visiting. Most hardwoods S2S to about 15/16\"; boards over 10\" wide +10%, under 4\" wide -10%",shipping_source_url=ENU,date_checked=TODAY,affiliate=''),
 dict(dealer=MV,city='Mount Vernon',state='OH',ships='No (local pickup by appointment)',shipping_note="Inventory page: sales by appointment only with easy local pickup about 1 mile from downtown Mount Vernon; text or email for this week's availability. Kiln dried, rough sawn. Prices shown are single-board prices (lower at 50-100+ BF)",shipping_source_url=MVU,date_checked=TODAY,affiliate=''),
 dict(dealer=AL,city='Buffalo',state='NY',ships='Yes (nationwide and international)',shipping_note="Online catalog ships from four US mills (Buffalo NY, Sarasota FL, Grover NC, Santa Fe Springs CA); small orders by UPS, larger by freight. Walk-in showroom at 601 Ohio St, Buffalo. Prices shown are the 1 BF rough price; lengths over 7 ft are 10% more",shipping_source_url='https://www.advantagelumber.com/contact',date_checked=TODAY,affiliate=''),
 dict(dealer=NS,city='Mandeville',state='LA',ships='Not stated',shipping_note="No shipping policy found; appointment-only pickup at 1750 South Lane, cash or Venmo. Small quantities or a single board OK. Price list dated 6/9/2026 does not reflect current inventory; 10% off over 100 BF. Closed for Thanksgiving until Nov 30, 2026",shipping_source_url=NSU,date_checked=TODAY,affiliate=''),
 dict(dealer=JB,city='Summerdale',state='AL',ships='Not stated',shipping_note="No shipping policy found; walk-in retail at the Summerdale yard Mon-Sat 9-5 (closed Thanksgiving). Sells 1 board or 1,000. Prices shown are the 1-49 BF column (50 BF+ is lower)",shipping_source_url='https://jubileespecialtywoods.com/retail/',date_checked=TODAY,affiliate='')]
for d in nd: d['date_added']=TODAY
dl+=[d for d in nd if d['dealer'] not in HOLD]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added; held:',HOLD or 'none')
print(collections.Counter((r['dealer'],r['species']) for r in rows if r['species'] in ('Basswood','Alder')))
