#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for dealer batch 2 (checked 2026-10-28) to seed.csv and dealers.csv.
Sources saved under raw/batch2/ (gitignored). Only plain/flat-sawn stock at each dealer's standard grade is used;
quartersawn, rift, figured/curly, ambrosia, rustic, #1 Common, wide-board premiums and per-linear-foot items are skipped
(same rules as earlier batches). All five dealers post prices in USD, so no currency conversion is needed.
Idempotent: removes earlier rows for these dealers first. Appends with CRLF; existing lines are kept byte-for-byte."""
import csv,io,re
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-10-28'; R='raw/batch2/'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany']
rows=[]
def add(sp,th,su,p,dn,city,st,url):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),dealer=dn,city=city,state=st,source_url=url,date_checked=TODAY))
def flat(f):
    s=BeautifulSoup(open(R+f,errors='replace').read(),'lxml')
    for x in s(['script','style']): x.decompose()
    return s.get_text(' | ',strip=True)
# ---- 1. Steve Wall Lumber Co., Mayodan NC: site is behind a captcha for curl/headless, so the pages were read with WebFetch
#      (raw/batch2/swl_premier_webfetch.txt, swl_exotic_webfetch.txt). "Select" grade, standard widths (10"+ premiums skipped).
#      Posted prices are for 100 bd ft of one species/thickness; add $0.10/bf under 100 bd ft (kept as posted, stated in the note).
SW='Steve Wall Lumber Co.'; SWP='https://walllumber.com/products/premier-hardwoods/'; SWE='https://walllumber.com/products/exotic-hardwoods/'
swt=open(R+'swl_premier_webfetch.txt').read(); swx=open(R+'swl_exotic_webfetch.txt').read()
SWN='KD, rough (Select; posted price is for 100 bd ft, add $0.10/bf under 100 bd ft'
for sp,extra,vals in [('Ash','',{'4/4':'4.50','5/4':'4.60','8/4':'5.25','12/4':'6.00'}),('Cherry','',{'4/4':'4.90','5/4':'5.10','8/4':'5.75'}),
    ('Hickory','; hickory-pecan',{'4/4':'3.10','5/4':'3.40','8/4':'5.05'}),
    ('Mahogany','; African mahogany',{'4/4':'5.75','5/4':'5.80','6/4':'5.90','8/4':'5.95','12/4':'6.50','16/4':'7.10'}),
    ('Hard Maple','; white',{'4/4':'5.00','5/4':'5.50','8/4':'6.20'}),('Soft Maple','',{'4/4':'4.85','5/4':'5.40','8/4':'6.00','12/4':'5.25'}),
    ('Red Oak','',{'4/4':'3.15','5/4':'3.40','6/4':'3.55','8/4':'3.95'}),('White Oak','',{'4/4':'7.00','5/4':'7.20','8/4':'9.50'}),
    ('Walnut','',{'4/4':'8.25','5/4':'8.40','8/4':'10.00','12/4':'13.00'})]:
    for th,v in vals.items():
        assert re.search(r'\| '+re.escape(th)+r' \|[^\n]*Select \$'+re.escape(v)+r' \|',swt),(sp,th,v)
        add(sp,th,SWN+extra+')',v,SW,'Mayodan','NC',SWP)
assert '| Sapele | Good mahogany substitute | 4/4 8/4 | $5.75 $6.00 |' in swx
for th,v in [('4/4','5.75'),('8/4','6.00')]: add('Sapele',th,'KD, rough (grade not stated; S2S available for $0.40/bf extra)',v,SW,'Mayodan','NC',SWE)
# ---- 2. Highland Hardwoods, Brentwood NH: retail price pages "PRICING EFFECTIVE AS OF 08/27/26" (PDFs, pdftotext -layout);
#      domestic = Select & Better unless specified, exotics = Common & Better. Plain RGH (rough) rows only.
HL='Highland Hardwoods'
HD='https://cdn.shopify.com/s/files/1/0699/6747/9022/files/DOMESTIC_PRICE_PAGES_082726.pdf?v=1788441779'
HX='https://cdn.shopify.com/s/files/1/0699/6747/9022/files/EXOTIC_PRICE_PAGES_082726.pdf?v=1788441779'
hdt=open(R+'highland_dom.txt').read(); hxt=open(R+'highland_exo.txt').read()
assert 'PRICING EFFECTIVE AS OF 08/27/26' in hdt and 'PRICING EFFECTIVE AS OF 08/27/26' in hxt
for src,txt,sp,su,vals in [
    (HD,hdt,'Ash','rough (Select & Better; white ash)',{'4/4':'5.00','5/4':'5.50','6/4':'5.75','8/4':'6.25','10/4':'7.25','12/4':'7.50','16/4':'9.00'}),
    (HD,hdt,'Cherry','rough (Select & Better)',{'4/4':'6.70','5/4':'6.85','6/4':'7.10','8/4':'7.20','10/4':'9.00','12/4':'9.50','16/4':'11.60'}),
    (HD,hdt,'Red Oak','rough (Select & Better)',{'4/4':'4.10','5/4':'5.00','6/4':'5.60','8/4':'5.95','10/4':'6.90','12/4':'7.99'}),
    (HD,hdt,'Hickory','rough (Select & Better)',{'4/4':'4.75','5/4':'5.85','8/4':'7.75'}),
    (HD,hdt,'Hard Maple','rough (Select & Better)',{'4/4':'7.10','5/4':'7.40','6/4':'7.85','8/4':'8.00','10/4':'9.50','12/4':'10.30','16/4':'12.75'}),
    (HD,hdt,'Soft Maple','rough (unselected for color)',{'4/4':'7.50','5/4':'7.00','6/4':'7.10','8/4':'8.00'}),
    (HD,hdt,'Poplar','rough (Select & Better; yellow poplar)',{'4/4':'4.10','5/4':'4.25','6/4':'4.40','8/4':'4.60','10/4':'5.15','12/4':'5.35','16/4':'7.70'}),
    (HD,hdt,'Walnut','rough (Select & Better; black walnut)',{'4/4':'13.25','5/4':'13.75','6/4':'14.00','8/4':'15.00','10/4':'15.25','12/4':'16.50','16/4':'16.90'}),
    (HD,hdt,'White Oak','rough (Select & Better)',{'4/4':'10.00','5/4':'12.00','6/4':'12.25','8/4':'13.75','10/4':'17.50','12/4':'18.00'}),
    (HX,hxt,'Mahogany','rough (Common & Better; African mahogany)',{'4/4':'7.95','5/4':'8.00','6/4':'8.15','8/4':'8.25','10/4':'8.35','12/4':'8.50'}),
    (HX,hxt,'Sapele','rough (Common & Better)',{'4/4':'7.75','5/4':'8.00','6/4':'8.25','8/4':'8.50','10/4':'8.75','12/4':'9.00','16/4':'9.50'})]:
    for th,v in vals.items():
        assert re.search(r'(^|\s)'+re.escape(th)+r'\s+RGH\s+'+re.escape(v)+r'(\s|$)',txt,re.M),(sp,th,v)
        add(sp,th,su,v,HL,'Brentwood','NH',src)
# ---- 3. Intercity Lumber Co., Tampa FL: HTML table, columns 4/4, 5/4, 8/4 "PRICE PER BOARD FOOT"; grade and surfacing not stated
IC='https://www.intercitylumber.com/hardwood-lumber.html'
s=BeautifulSoup(open(R+'intercity.html',errors='replace').read(),'lxml'); trs=[[x.get_text(' ',strip=True) for x in tr.find_all(['td','th'])] for tr in s.find('table').find_all('tr')]
assert [h.split(' ')[0] for h in trs[0][1:]]==['4/4','5/4','8/4'],trs[0]
IM={'ASH':'Ash','CHERRY':'Cherry','MAHOGANY':'Mahogany','MAPLE (HARD)':'Hard Maple','MAPLE (SOFT)':'Soft Maple','POPLAR':'Poplar','RED OAK':'Red Oak',
    'WALNUT':'Walnut','WHITE OAK':'White Oak','SAPELE':'Sapele'}
seen=set()
for c in trs[2:]:
    if c and c[0] in IM:
        assert len(c)==4,c; seen.add(c[0]); sp=IM[c[0]]
        for th,v in zip(['4/4','5/4','8/4'],c[1:]):
            if v: assert re.fullmatch(r'\$\d+\.\d\d',v),v; add(sp,th,'grade and surfacing not stated'+('; mahogany type not stated' if sp=='Mahogany' else ''),v[1:],'Intercity Lumber Co.','Tampa','FL',IC)
assert seen==set(IM),set(IM)-seen
# ---- 4. M2 Lumber, Laurens SC: "Lumber Price List" on the stocked-lumber collection page; RWL, S3S ("Most of our Dimensional Lumber is sold as S3S")
M2='https://m2lumber.com/collections/stocked-lumber'
t=flat('m2_stocked.html'); seg=t[t.find('Lumber Price List | Species | 4/4 | 8/4 |'):]; seg=seg[:seg.find('Skip to results list')]
MM={'Ash':'Ash','Black Walnut':'Walnut','Cherry':'Cherry','Hard Maple':'Hard Maple','Hickory':'Hickory','Poplar':'Poplar','Red Oak':'Red Oak','Sapele':'Sapele','White Oak':'White Oak'}
seen=set()
for m in re.finditer(r'\| ([A-Za-z ]+) \| \$(\d+\.\d\d) \| \$(\d+\.\d\d)',seg):
    if m.group(1) in MM:
        seen.add(m.group(1))
        for th,v in [('4/4',m.group(2)),('8/4',m.group(3))]: add(MM[m.group(1)],th,'S3S, random widths (grade not stated)',v,'M2 Lumber','Laurens','SC',M2)
assert seen==set(MM),set(MM)-seen   # Ambrosia Maple skipped (figured/ambrosia rule)
# ---- 5. Dunham Hardwoods, Dunlap IA: "RETAIL PRICE LIST" (undated; "All prices subject to change without notice"); FAS rows only
DH='https://www.dunham-hardwoods.com/retailprices.asp'
t=re.sub(r'\s*\|\s*','|',flat('dunham.html'))
for sp,lab,vals in [('Ash','WHITE ASH',{'4/4':'5.14'}),('Cherry','CHERRY',{'4/4':'6.25','5/4':'6.50','8/4':'8.05'}),('Mahogany','MAHOGANY',{'4/4':'8.70','8/4':'9.05'}),
    ('Hickory','HICKORY',{'4/4':'5.00'}),('Hard Maple','HARD MAPLE (WHITE)',{'4/4':'7.00','8/4':'8.85'}),('Soft Maple','SOFT MAPLE',{'4/4':'6.65'}),
    ('Red Oak','RED OAK',{'4/4':'5.52','5/4':'5.77','6/4':'5.82','8/4':'6.00'}),('White Oak','WHITE OAK',{'4/4':'9.00'}),
    ('Poplar','YELLOW POPLAR',{'4/4':'5.17','5/4':'5.31','6/4':'5.51','8/4':'5.76'}),('Walnut','WALNUT',{'4/4':'11.72','5/4':'14.25','8/4':'15.50'})]:
    seg=t[t.find('|'+lab+'|'):]; assert seg
    for th,v in vals.items():
        # values are split across cells on the page ("$|6.25", "$6.|25", "$5|.|52"): compare with separators removed
        i=seg.find('|'+th+' FAS|'); assert i>=0,(lab,th); nxt=seg[i+len(th)+6:i+len(th)+6+12].replace('|','')
        assert nxt.startswith('$'+v),(lab,th,v,nxt)
        add(sp,th,'grade FAS; surfacing not stated'+('; mahogany type not stated' if sp=='Mahogany' else ''),v,'Dunham Hardwoods','Dunlap','IA',DH)
# ---- write seed.csv (append, CRLF, existing bytes untouched) ----
NEW={SW,HL,'Intercity Lumber Co.','M2 Lumber','Dunham Hardwoods'}
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+d+',') in l for d in NEW)]
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
# ---- dealers.csv ----
dcols=list(csv.DictReader(open('dealers.csv')).fieldnames); dl=[d for d in csv.DictReader(open('dealers.csv')) if d['dealer'] not in NEW]
dl+= [
 dict(dealer=SW,city='Mayodan',state='NC',ships='Yes (area not stated)',shipping_note="Price pages say prices are FOB Mayodan, NC, 'We ship UPS or Motor Freight', minimum order 10 bd ft (species can be mixed). Posted lumber prices are for 100 bd ft of one species and thickness; add $0.10/bf under 100 bd ft, subtract $0.10 over 300 bd ft and $0.20 over 500 bd ft (motor freight or pick-up only)",shipping_source_url=SWE,date_checked=TODAY,affiliate=''),
 dict(dealer=HL,city='Brentwood',state='NH',ships='Not stated',shipping_note="Retail lumber is sold at the Brentwood yard (online listings are marked 'In-Store Only'); the Delivery page describes truck delivery throughout New England for wholesale customers. Price pages list a 10% discount on orders over 100 bd ft (items in red excluded)",shipping_source_url='https://highlandhardwoods.com/pages/delivery',date_checked=TODAY,affiliate=''),
 dict(dealer='Intercity Lumber Co.',city='Tampa',state='FL',ships='Local delivery (area not stated)',shipping_note="Home page says 'Fast Delivery or Easy Drive Up Loading' and 'Serving the Tampa Bay area and much of central Florida'; no delivery area or long-distance shipping stated",shipping_source_url='https://www.intercitylumber.com/home.html',date_checked=TODAY,affiliate=''),
 dict(dealer='M2 Lumber',city='Laurens',state='SC',ships='Yes (freight quote; local delivery within 100 mi)',shipping_note="Free pickup at the Laurens yard; crew hand-delivers within 100 miles ($50 up to 16.6 mi, up to $300 at 83-100 mi, shown at checkout); farther orders ship by freight on a custom quote, usually with a $500 minimum",shipping_source_url='https://m2lumber.com/policies/shipping-policy',date_checked=TODAY,affiliate=''),
 dict(dealer='Dunham Hardwoods',city='Dunlap',state='IA',ships='Not stated',shipping_note="No shipping policy found; the retail price list says retail is for customers who 'pick their own lumber from our store' and lists store hours",shipping_source_url=DH,date_checked=TODAY,affiliate='')]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
import collections
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added')
