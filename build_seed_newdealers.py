#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for outreach batch 1 (checked 2026-10-21) to seed.csv and dealers.csv.
Sources saved under raw/newdealers/ (gitignored). Only plain/flat-sawn stock at each dealer's standard grade is used;
quartersawn, rift, figured, rustic, #1 Common and per-linear-foot S4S items are skipped (same as earlier dealers).
Peacock Lumber posts prices in Canadian dollars (no USD storefront, unlike Knotty), so its prices are converted to USD at the
Bank of Canada daily average for 2026-10-21 (1.4057 CAD per USD); the original CAD price and the rate are kept in the surfacing note.
Idempotent: removes earlier rows for these dealers first. Appends with CRLF; existing lines are kept byte-for-byte."""
import csv,io,re,json
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-10-21'; R='raw/newdealers/'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany']
rows=[]
def add(sp,th,su,p,dn,city,st,url):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),dealer=dn,city=city,state=st,source_url=url,date_checked=TODAY))
# ---- 1. Willard Brothers Woodcutters, Trenton NJ: "S2S Domestic Hardwoods" Wix table (rendered with Chrome, raw/newdealers/wb_frames.txt)
t=open(R+'wb_frames.txt').read()
dom=t[t.find('S2S Domestic Hardwoods\t'):t.find('S2S Exotic Hardwoods\t')]
H=['4/4','5/4','6/4','8/4','10/4','12/4','16/4']
WB={'Ash (Flat or Qtr Sawn)':('Ash','; flat or qtr sawn'),'Cherry (Flat and Qtr Sawn)':('Cherry','; flat and qtr sawn'),'Hickory':('Hickory',''),
    'Mahogany (African)':('Mahogany','; African mahogany'),'Maple (Hard, Flat and Qtr Sawn)':('Hard Maple','; flat and qtr sawn'),'Maple (Soft)':('Soft Maple',''),
    'Oak (Red, Flat and Qtr Sawn)':('Red Oak','; flat and qtr sawn'),'Oak (White)':('White Oak',''),'Poplar':('Poplar',''),
    'Sapele (Flat and Qtr Sawn)':('Sapele','; flat and qtr sawn'),'Walnut (Black, Flat and Qtr Sawn)':('Walnut','; flat and qtr sawn')}
seen=set()
for line in dom.split('\n'):
    c=[x.strip() for x in line.split('\t')]
    if c[0] in WB:
        sp,extra=WB[c[0]]; seen.add(c[0])
        for th,v in zip(H,c[1:]):
            if not v.startswith('$'): continue
            if sp=='Sapele' and th=='12/4': continue   # domestic table says $13.00, exotic table says $12.00: conflicting, skipped
            add(sp,th,'S2S (KD, straight-line ripped one edge'+extra+')',v[1:],'Willard Brothers Woodcutters','Trenton','NJ','https://www.willardbrothers.net/hardwood-prices-1')
assert seen==set(WB),set(WB)-seen
# ---- 2. Exotic Lumber, Annapolis MD: retail rough $/bf table (under 100 BF; wholesale list is separate)
s=BeautifulSoup(open(R+'exotic.html').read(),'lxml'); tb=s.find('table'); hdr=[x.get_text(strip=True) for x in tb.find('tr').find_all(['td','th'])]
assert hdr==['Species','4/4','5/4','6/4','8/4','10/4','12/4','16/4'],hdr
EX={'Ash, White':'Ash','Cherry':'Cherry','Hickory':'Hickory','Mahogany, African':'Mahogany','Maple, Hard':'Hard Maple','Maple, Soft':'Soft Maple',
    'Oak, Red':'Red Oak','Oak, White':'White Oak','Poplar':'Poplar','Mahogany, Sapele':'Sapele','Walnut':'Walnut'}
seen=set()
for tr in tb.find_all('tr')[1:]:
    c=[x.get_text(strip=True) for x in tr.find_all(['td','th'])]
    if c and c[0] in EX:
        assert len(c)==8,c; seen.add(c[0]); sp=EX[c[0]]
        for th,v in zip(hdr[1:],c[1:]):
            if re.fullmatch(r'\d+(\.\d+)?',v): add(sp,th,'rough (retail list, under 100 BF'+('; African mahogany' if sp=='Mahogany' else '')+')',v,'Exotic Lumber','Annapolis','MD','https://exoticlumber.com/pages/lumber')
assert seen==set(EX)
# ---- 3. Kettle Moraine Hardwoods, Hartford WI: "Prices effective 8/9/2026", priced on rough thickness; Select & Better rows
s=BeautifulSoup(open(R+'km_pw.render.html').read(),'lxml'); tb=s.find('table')
trs=[[x.get_text(' ',strip=True) for x in tr.find_all(['td','th'])] for tr in tb.find_all('tr')]
assert trs[0][2:]==['4/4(1")','5/4 (1.25")','6/4 (1.5")','8/4 (2")','10/4 (2.5")','12/4 (3")'],trs[0]
KH=['4/4','5/4','6/4','8/4','10/4','12/4']
KM={'ASH':'Ash','CHERRY':'Cherry','HARD MAPLE':'Hard Maple','HICKORY':'Hickory','POPLAR':'Poplar','RED OAK':'Red Oak','SOFT MAPLE':'Soft Maple','WALNUT':'Walnut','WHITE OAK':'White Oak'}
cur=None; seen=set()
def kmadd(sp,c,su):
    for th,v in zip(KH,c[2:]):
        if v.startswith('$'): add(sp,th,su,v[1:],'Kettle Moraine Hardwoods','Hartford','WI','https://www.kmhardwoods.com/lumber-prices')
for c in trs[1:]:
    if all(x=='' for x in c[1:]): cur=c[0]; continue
    if c[0]=='Select & Better' and cur in KM: kmadd(KM[cur],c,'rough (Select & Better)'); seen.add(cur)
    elif c[0]=='Ribbon (Quartersawn)' and cur=='AFRICAN MAHOGANY': kmadd('Mahogany',c,'rough (African mahogany, ribbon/quartersawn)'); seen.add(cur)
    elif c[0]=='SAPELE': kmadd('Sapele',c,'rough (grade not stated)'); seen.add('SAPELE')
assert seen==set(KM)|{'AFRICAN MAHOGANY','SAPELE'},seen
# ---- 4. Kunz Carpentry Warehouse, Trenton IL: "Last Updated 10/10/2026" (raw/newdealers/kunz_webfetch.txt); KD, planed hit-or-miss, SLR
KU='http://www.kunzcarpentry.com/hardwood_lumber.html'
for sp,gr,vals in [('Red Oak','FAS',{'4/4':'4.95','5/4':'5.50','6/4':'5.95','8/4':'5.95'}),('White Oak','FAS',{'4/4':'10.95','8/4':'13.95'}),
    ('Hickory','FAS',{'4/4':'5.95','8/4':'7.95'}),('Poplar','FAS',{'4/4':'4.10','5/4':'4.25','6/4':'4.25','8/4':'4.95'}),
    ('Hard Maple','Select & Better',{'4/4':'6.25','5/4':'6.95','8/4':'7.95'}),('Soft Maple','Select',{'4/4':'5.50'}),
    ('Walnut','FAS',{'4/4':'13.95','5/4':'15.95','6/4':'15.95','8/4':'15.95'}),('Cherry','Select & Better',{'4/4':'6.45','5/4':'6.95','6/4':'6.95','8/4':'6.95'}),
    ('Mahogany','Select African mahogany',{'4/4':'8.75','8/4':'9.95'})]:
    for th,v in vals.items(): add(sp,th,f'KD, hit-and-miss planed, SLR ({gr})',v,'Kunz Carpentry Warehouse','Trenton','IL',KU)
kt=open(R+'kunz_webfetch.txt').read()
for r in rows:
    if r['dealer']=='Kunz Carpentry Warehouse': assert '$'+r['price_per_bf'] in kt,r
# ---- 5. Peacock Lumber, Oshawa ON: per-bf tables on each rough hardwood product page, prices in CAD -> USD
FX=Dn('1.4057')   # Bank of Canada FXUSDCAD daily average, 2026-10-21 (raw/newdealers/boc_usdcad.json)
assert json.load(open(R+'boc_usdcad.json'))['observations'][0]=={'d':'2026-10-21','FXUSDCAD':{'v':'1.4057'}}
PC={'african-mahog':('Mahogany','Select & Better','; African mahogany'),'cherry-2':('Cherry','90/50 Red',''),'hickory-2':('Hickory','Prime',''),
    'red-oak-2':('Red Oak','Sel&Btr',''),'sapele-2':('Sapele','Select & Better',''),'soft-maple':('Soft Maple','F1F & Better',''),'w-ash':('Ash','Select & Better','; white ash'),
    'walnut-2':('Walnut','Select & Better',''),'white-maple-2':('Hard Maple','Sap & Btr','; white maple'),'white-oak':('White Oak','Flat Sliced','')}
for h,(sp,gr,extra) in PC.items():
    s=BeautifulSoup(open(R+f'peacock/{h}.html').read(),'lxml')
    for x in s(['script','style','noscript']): x.decompose()
    t=s.get_text('\n',strip=True); assert 'priced per\nboard foot' in t,h
    seg=t[t.find('Price (BF)'):]; seg=seg[:seg.find('THICKNESS MEASUREMENTS')].split('\n')[1:]
    n=0
    for i in range(0,len(seg)-2,3):
        g,th,v=seg[i:i+3]
        if g!=gr: continue
        m=re.match(r'\$(\d+\.\d+)( \(48 hour notice\))?$',v); assert m,(h,v)
        cad=Dn(m.group(1)); usd=(cad/FX).quantize(Dn('0.01'),ROUND_HALF_UP); n+=1
        note=f'rough ({gr}{extra}{"; 48 hour notice" if m.group(2) else ""}); posted CAD ${m.group(1)}/bf converted to USD at 1.4057 CAD/USD (Bank of Canada, 2026-10-21)'
        add(sp,th,note,usd,'Peacock Lumber','Oshawa','ON',f'https://peacocklumber.ca/product/{h}/')
    assert n,h
# ---- write seed.csv (append, CRLF, existing bytes untouched) ----
NEW={'Willard Brothers Woodcutters','Exotic Lumber','Kettle Moraine Hardwoods','Kunz Carpentry Warehouse','Peacock Lumber'}
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+d+',') in l for d in NEW)]
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
# ---- dealers.csv ----
dcols=list(csv.DictReader(open('dealers.csv')).fieldnames); dl=[d for d in csv.DictReader(open('dealers.csv')) if d['dealer'] not in NEW]
dl+= [
 dict(dealer='Willard Brothers Woodcutters',city='Trenton',state='NJ',ships='Not stated',shipping_note="No lumber shipping policy found; price page says S2S lumber is sold by the board foot at random widths and lengths, offers one free cut per board 'to fit in your vehicle', and lists showroom hours",shipping_source_url='https://www.willardbrothers.net/hardwood-prices-1',date_checked=TODAY,affiliate=''),
 dict(dealer='Exotic Lumber',city='Annapolis',state='MD',ships='Yes (area not stated)',shipping_note='Online store orders are processed within three business days and shipped by standard shipping; large, multi-package or over-50 lb orders are charged actual shipping. Carrier and shipping area not stated; the $/bf retail list is for under 100 BF (separate wholesale list)',shipping_source_url='https://exoticlumber.com/policies/shipping-policy',date_checked=TODAY,affiliate=''),
 dict(dealer='Kettle Moraine Hardwoods',city='Hartford',state='WI',ships='Not stated',shipping_note='No shipping policy found; price page says prices are per board foot on rough thickness, a 25% wide-board premium applies, and planing, ripping and sanding are available for lumber bought at the store',shipping_source_url='https://www.kmhardwoods.com/lumber-prices',date_checked=TODAY,affiliate=''),
 dict(dealer='Kunz Carpentry Warehouse',city='Trenton',state='IL',ships='Not stated',shipping_note="No shipping policy found; price list says 'In Stock Prices ONLY', 10% off 100 bd. ft. or more, and to call 618-224-9636 for bundle discounts",shipping_source_url='http://www.kunzcarpentry.com/hardwood_lumber.html',date_checked=TODAY,affiliate=''),
 dict(dealer='Peacock Lumber',city='Oshawa',state='ON',ships='Local delivery (area not stated)',shipping_note="Product pages show 'In-store pick up' and 'Delivery Available'; no delivery area or long-distance shipping stated. Prices are posted in Canadian dollars; shown here converted to USD at 1.4057 CAD/USD (Bank of Canada, 2026-10-21). Volume discounts: 7% at 100 BF, 12% at 250 BF; premiums for 12 ft+ lengths and 8 in.+ widths",shipping_source_url='https://peacocklumber.ca/product/walnut-2/',date_checked=TODAY,affiliate='')]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
import collections
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added')
