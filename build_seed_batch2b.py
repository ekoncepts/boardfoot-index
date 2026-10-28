#!/usr/bin/env python3
"""Dealer batch 2b (2026-10-28, approved by Harry): Frederick Lumber Company (Frederick MD), CR Muterspaw Lumber (Xenia OH),
and Kettle Moraine 4/4 hard maple grade labels (confirmed by Sam Wesp, KMH, 10/27).
Same rules as earlier batches: plain/flat-sawn stock only; quartersawn, rift, figured/curly, ambrosia/wormy, rustic, gummy,
#1 Common, shorts, wide-board premiums, per-SF / per-LF items, thermo-treated and Peruvian walnut are skipped.
Idempotent: removes earlier rows for these two dealers first. Existing lines kept byte-for-byte except the one KMH maple row relabeled."""
import csv,io,re
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-10-28'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany']
rows=[]
def add(sp,th,su,p,dn,city,st,url,dt=TODAY):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),dealer=dn,city=city,state=st,source_url=url,date_checked=dt))
# ---- 1. Frederick Lumber Company, Frederick MD: Harry's CSV of https://fredericklumber.com/price-list/ (site blocks curl via Cloudflare);
#      spot-checked against the live page 2026-10-28 (raw/batch2/frederick_spotcheck_2026-10-28.txt). Main 4/4-16/4 table only.
FL='Frederick Lumber Company'; FU='https://fredericklumber.com/price-list/'
rd=list(csv.reader(open('raw/frederick-lumber-2026-10-26.csv',encoding='utf-8-sig')))
hdr=rd[0]; assert hdr==['Lumber Species','4/4','5/4','6/4','8/4','10/4','12/4','16/4'],hdr
tab={}
for r in rd[1:]:
    if not r or not r[0]: break
    tab[r[0]]=r[1:8]
spot=open('raw/batch2/frederick_spotcheck_2026-10-28.txt').read()
FM={'Ash, Natural':('Ash',''),'Cherry':('Cherry',''),'Hickory':('Hickory',''),'Mahogany, African':('Mahogany','; African mahogany'),
    'Mahogany, Sapele':('Sapele',''),'Maple, Hard':('Hard Maple',''),'Maple, Soft':('Soft Maple',''),'Oak, Red':('Red Oak',''),
    'Oak, White':('White Oak',''),'Poplar':('Poplar',''),'Walnut':('Walnut','')}
for lab,(sp,extra) in FM.items():
    v=tab[lab]; live=' '.join(x[1:] if x else '-' for x in v)
    assert (lab+' | '+live) in spot,(lab,live)   # CSV matches live page
    for th,x in zip(hdr[1:],v):
        if x: assert re.fullmatch(r'\$\d+\.\d\d',x),x; add(sp,th,'grade and surfacing not stated'+extra,x[1:],FL,'Frederick','MD',FU)
# ---- 2. CR Muterspaw Lumber, Xenia OH: https://crlumber.com/price-list/ (raw/batch2/crlumber_price-list.html, fetched 2026-10-28,
#      identical to the 10/26 copy). 0-99BF column (the 100+BF column is a volume discount). Domestic stock "stored hit/miss planed";
#      exotics "kiln dried, FAS grade, and stored hit/miss planed".
CR='CR Muterspaw Lumber'; CU='https://crlumber.com/price-list/'
s=BeautifulSoup(open('raw/batch2/crlumber_price-list.html',errors='replace').read(),'lxml')
tr=[[x.get_text(' ',strip=True) for x in t.find_all(['td','th'])] for tb in s.find_all('table') for t in tb.find_all('tr')]
d={}
for c in tr:
    if len(c)==3 and c[1]!='0-99BF': d[c[0]]=c[1]
assert d['4/4 Walnut- Regular']=='$9.45' and d['4/4 Walnut -Prime']=='$11.45'
DOM='hit/miss planed (grade not stated)'
CM=[('Ash',DOM,['4/4 Ash','5/4 Ash','8/4 Ash']),
    ('Cherry',DOM,['4/4 Cherry','5/4 Cherry','6/4 Cherry','8/4 Cherry','12/4 Cherry','16/4 Cherry']),
    ('Hard Maple','hit/miss planed (white; grade not stated)',['4/4 Hard Maple White','5/4 Hard Maple White','8/4 Hard Maple White']),
    ('Soft Maple','hit/miss planed (white; grade not stated)',['4/4 Soft Maple White','5/4 Soft Maple White','8/4 Soft Maple White','12/4 Soft Maple White']),
    ('Hickory',DOM,['4/4 Hickory','8/4 Hickory']),
    ('Poplar',DOM,['4/4 Poplar','5/4 Poplar','6/4 Poplar','8/4 Poplar','12/4 Poplar']),('Poplar','S3S (grade not stated)',['4/4 Poplar S3S']),
    ('Red Oak',DOM,['4/4 Red Oak','5/4 Red Oak','8/4 Red Oak']),
    ('Walnut','hit/miss planed (Regular grade)',['4/4 Walnut- Regular','8/4 Walnut- Regular','12/4 Walnut- Regular']),
    ('Walnut','hit/miss planed (Prime grade)',['4/4 Walnut -Prime','5/4 Walnut Prime','6/4 Walnut Prime','8/4 Walnut -Prime']),
    ('White Oak',DOM,['4/4 White Oak','5/4 White Oak','8/4 White Oak']),
    ('Mahogany','hit/miss planed (FAS; African mahogany)',['4/4 African Mahogany','8/4 African Mahogany','12/4 African Mahogany']),
    ('Sapele','hit/miss planed (FAS)',['4/4 Sapele','8/4 Sapele'])]
for sp,su,labs in CM:
    for lab in labs:
        v=d[lab]; assert re.fullmatch(r'\$\d+\.\d\d',v),(lab,v)
        add(sp,lab.split(' ')[0],su,v[1:],CR,'Xenia','OH',CU)
# ---- 3. Kettle Moraine Hardwoods 4/4 hard maple: grade labels confirmed by Sam Wesp 10/27 (prices current).
#      The $4.62 4/4 "White Select & Better" row is on the same 8/9/2026 price table (raw/newdealers/km_pw.render.html) but was not
#      in seed.csv; add it with the label. Relabel the existing $2.85 Select & Better row.
KMU='https://www.kmhardwoods.com/lumber-prices'
s=BeautifulSoup(open('raw/newdealers/km_pw.render.html').read(),'lxml')
kt=[[x.get_text(' ',strip=True) for x in t.find_all(['td','th'])] for t in s.find('table').find_all('tr')]
i=kt.index(['HARD MAPLE','','','','','','',''])
assert kt[i+1][:3]==['Select & Better','*','$2.85'] and kt[i+3][:3]==['White Select & Better','*','$4.62'],kt[i:i+4]
KMW=dict(species='Hard Maple',thickness='4/4',surfacing='rough (White Select & Better)',price_per_bf='4.62',dealer='Kettle Moraine Hardwoods',
         city='Hartford',state='WI',source_url=KMU,date_checked='2026-10-21')
OLD='Hard Maple,4/4,rough (Select & Better),2.85,Kettle Moraine Hardwoods,'
NEWL='Hard Maple,4/4,"rough (Select & Better, mixed heartwood/sapwood)",2.85,Kettle Moraine Hardwoods,'
# ---- write seed.csv ----
NEW={FL,CR}
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+x+',') in l for x in NEW) and not l.startswith('Hard Maple,4/4,rough (White Select & Better),4.62,Kettle Moraine')]
n=0
for k,l in enumerate(lines):
    if l.startswith(OLD) or l.startswith(NEWL): lines[k]=NEWL+l.split('Kettle Moraine Hardwoods,',1)[1]; n+=1
assert n==1,n
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows+[KMW])
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
# ---- dealers.csv ----
dcols=list(csv.DictReader(open('dealers.csv')).fieldnames); dl=[x for x in csv.DictReader(open('dealers.csv')) if x['dealer'] not in NEW]
dl+=[dict(dealer=FL,city='Frederick',state='MD',ships='Yes (all 50 states per home page)',shipping_note="Home page says 'Can't make it to Frederick? We ship to all 50 states and worldwide' (online store of hand-selected pieces); no shipping rates or policy for price-list lumber found. Price list says prices are per board foot and subject to change without notice",shipping_source_url='https://fredericklumber.com/',date_checked=TODAY,affiliate=''),
     dict(dealer=CR,city='Xenia',state='OH',ships='Yes (FedEx or LTL freight, nationwide)',shipping_note="Delivery & Shipping page: local delivery on their own trucks, nationally via FedEx Ground (most orders under 75 bd ft) or common carrier/LTL (over 75 bd ft or long lengths); example given: 100 bd ft may cost about $125 to ship. Price list shows 0-99 BF and lower 100+ BF prices; this site uses 0-99 BF",shipping_source_url='https://crlumber.com/delivery-and-shipping/',date_checked=TODAY,affiliate='')]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
import collections
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows)+1,'rows added (incl. KMH white maple)')
