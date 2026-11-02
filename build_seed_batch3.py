#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for dealer batch 3 (checked 2026-11-02) to seed.csv and dealers.csv.
Sources saved under raw/batch3/ (gitignored). Same rules as earlier batches: only plain/flat-sawn stock at each dealer's
standard grade; quartersawn, rift, figured/curly/birdseye, ambrosia, wormy, rustic, #1 Common, wide-board (8"+ etc.) premiums,
shorts, slabs and per-linear-foot items are skipped. All six dealers post prices in USD, so no currency conversion is needed.
Idempotent: removes earlier rows for these dealers first. Appends with CRLF; existing lines are kept byte-for-byte."""
import csv,io,re,json,subprocess
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-11-02'; R='raw/batch3/'
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
# ---- 1. Almendinger Sawmill, Johnstown OH: "KDL Pricing" PDF linked from the Kiln Dried Lumber page.
#      Page: "WE DO NOT SHIP! | ALL LUMBER IS ROUGH SAWN! ... All lumber is select and better grade". Specialty/curly/rustic/wormy/QS skipped.
AL='Almendinger Sawmill'; ALP='https://almendingersawmill.com/wp-content/uploads/2026/02/2025-kd-price-sheet.pdf'
at=subprocess.run(['pdftotext','-layout',R+'alm_kd2026.pdf','-'],capture_output=True,text=True).stdout
assert 'All lumber is select and better grade' in flat('alm_kdl.html') and 'WE DO NOT SHIP!' in flat('alm_kdl.html')
for sp,lab,vals in [('Ash','Ash',{'4/4':'4.15','8/4':'5.20'}),('Cherry','Cherry',{'4/4':'4.40','8/4':'5.50'}),
    ('Hard Maple','Hard Maple',{'4/4':'5.00','8/4':'6.25'}),('Hickory','Hickory',{'4/4':'3.65','8/4':'6.20'}),
    ('Poplar','Poplar',{'4/4':'3.10','8/4':'4.10'}),('Red Oak','Red Oak',{'4/4':'3.25','6/4':'4.25','8/4':'4.25'}),
    ('Soft Maple','Soft Maple',{'4/4':'4.15'}),('Walnut','Walnut',{'4/4':'9.65','8/4':'10.65'}),('White Oak','White Oak',{'4/4':'6.50','8/4':'9.50'})]:
    for th,v in vals.items():
        assert re.search(r'^\s*'+re.escape(lab)+r'\s+'+re.escape(th)+r'\s+\$'+re.escape(v)+r'\b',at,re.M),(lab,th,v)
        add(sp,th,'KD, rough sawn (Select & Better)'+('; 8"+ wide add $1.00/bf' if sp=='Walnut' else ''),v,AL,'Johnstown','OH',ALP)
# ---- 2. Zeyer Lumber, Baltimore OH: inventory table on the FAQ/price-list page (species | thickness | grade | surfacing | code | unit | price | note).
#      Standard (FAS/Prime/White) flat-sawn BF rows; first-listed row per species/thickness; 9'+ length, shorts, 1C, brown and curly rows skipped.
ZY='Zeyer Lumber'; ZU='https://www.zeyerlumber.com/faqs-and-lumber-price-list'
zt=flat('zeyer.html')
for sp,pat,su,v in [
    ('Ash','Ash | 4/4 | FAS | WA | BF | 4.25 | White','FAS (white ash; surfacing not stated)','4.25'),
    ('Ash','Ash | 8/4 | FAS | WA | BF | 7.00 | White','FAS (white ash; surfacing not stated)','7.00'),
    ('Cherry','Cherry | 4/4 | FAS | Rough-Cut | CH | BF | 3.50','rough (FAS)','3.50'),
    ('Cherry','Cherry | 5/4 | FAS | S2S | CH | BF | 4.00','S2S (FAS)','4.00'),
    ('Cherry','Cherry | 6/4 | FAS | S4S | CH | BF | 4.25','S4S (FAS)','4.25'),
    ('Cherry','Cherry | 8/4 | FAS | S3S | CH | BF | 4.75','S3S (FAS)','4.75'),
    ('Hard Maple','Hard Maple | 4/4 | White | S3S | HM | BF | 4.00','S3S (white)','4.00'),
    ('Hard Maple','Hard Maple | 5/4 | White | S3S | HM | BF | 4.75','S3S (white)','4.75'),
    ('Hard Maple','Hard Maple | 6/4 | White | S3S | HM | BF | 5.25','S3S (white)','5.25'),
    ('Hard Maple','Hard Maple | 8/4 | White | S3S | HM | BF | 5.75','S3S (white)','5.75'),
    ('Hickory','Hickory | 4/4 | Prime | HI | BF | 3.75','Prime (surfacing not stated)','3.75'),
    ('Hickory','Hickory | 6/4 | Prime | S3S | HI | BF | 4.75','S3S (Prime)','4.75'),
    ('Hickory','Hickory | 8/4 | Prime | HI | BF | 5.75','Prime (surfacing not stated)','5.75'),
    ('Mahogany','Khaya | 4/4 | FAS | KY | BF | 8.00 | A. Mahogany','FAS (African mahogany/khaya; surfacing not stated)','8.00'),
    ('Mahogany','Khaya | 8/4 | FAS | KY | BF | 9.00 | A. Mahogany','FAS (African mahogany/khaya; surfacing not stated)','9.00'),
    ('Mahogany','Khaya | 16/4 | FAS | KY | BF | 10.00 | A. Mahogany','FAS (African mahogany/khaya; surfacing not stated)','10.00'),
    ('Poplar','Poplar | 4/4 | FAS | Rough-Cut | YP | BF | 2.25','rough (FAS)','2.25'),
    ('Poplar','Poplar | 5/4 | FAS | Rough-Cut | YP | BF | 2.50','rough (FAS)','2.50'),
    ('Poplar','Poplar | 6/4 | FAS | Rough-Cut | YP | BF | 2.75','rough (FAS)','2.75'),
    ('Poplar','Poplar | 8/4 | FAS | Rough-Cut | YP | BF | 3.00','rough (FAS)','3.00'),
    ('Poplar','Poplar | 12/4 | FAS | Rough-Cut | YP | BF | 3.50','rough (FAS)','3.50'),
    ('Soft Maple','Red Maple | 4/4 | FAS | Rough-Cut | RM | BF | 3.50','rough (FAS; red maple)','3.50'),
    ('Red Oak','Red Oak | 4/4 | FAS | S2S | RO | BF | 3.00','S2S (FAS)','3.00'),
    ('Red Oak','Red Oak | 5/4 | FAS | S4S | RO | BF | 3.50','S4S (FAS)','3.50'),
    ('Red Oak','Red Oak | 6/4 | FAS | S3S | RO | BF | 4.25','S3S (FAS)','4.25'),
    ('Red Oak','Red Oak | 8/4 | FAS | S3S | RO | BF | 4.50','S3S (FAS)','4.50'),
    ('Sapele','Sapele | 4/4 | FAS | S2S | SP | BF | 9.00','S2S (FAS)','9.00'),
    ('Walnut','Walnut | 4/4 | FAS | BW | BF | 8.00','FAS (surfacing not stated)','8.00'),
    ('Walnut','Walnut | 6/4 | FAS | BW | BF | 9.00','FAS (surfacing not stated)','9.00'),
    ('Walnut','Walnut | 8/4 | FAS | BW | BF | 12.00','FAS (surfacing not stated)','12.00'),
    ('White Oak','White Oak | 4/4 | Flat-Sawn | Rough-Cut | WO | BF | 6.75','rough (flat-sawn; grade not stated)','6.75'),
    ('White Oak','White Oak | 5/4 | Flat-Sawn | Rough-Cut | WO | BF | 7.25','rough (flat-sawn; grade not stated)','7.25'),
    ('White Oak','White Oak | 6/4 | Flat-Sawn | S3S | WO | BF | 9.00','S3S (flat-sawn; grade not stated)','9.00'),
    ('White Oak','White Oak | 8/4 | Flat-Sawn | Rough-Cut | WO | BF | 10.00','rough (flat-sawn; grade not stated)','10.00')]:
    assert ('| '+pat) in zt,pat
    add(sp,pat.split(' | ')[1],su,v,ZY,'Baltimore','OH',ZU)
# ---- 3. K&J Lumber Products, Mora MN: price-list image "updated 10/13/26" (raw/batch3/kj_price.png, read by eye);
#      KD, planed, straight-line ripped, Select & Better.
KJ='K&J Lumber Products'; KJU='https://www.kandjlumber.com/lumber-price-list'
for sp,vals in [('Ash',{'4/4':'3.50','8/4':'4.25'}),('Cherry',{'4/4':'6.25','5/4':'6.50','8/4':'7.50'}),
    ('Hard Maple',{'4/4':'4.50','5/4':'5.25','8/4':'6.50'}),('Soft Maple',{'4/4':'3.75','5/4':'4.00','8/4':'4.50'}),
    ('White Oak',{'4/4':'5.50','5/4':'6.00','8/4':'6.50'}),('Red Oak',{'4/4':'3.25','5/4':'4.00','8/4':'4.50'}),
    ('Walnut',{'4/4':'10.50','5/4':'11.00','8/4':'12.75'}),('Hickory',{'4/4':'4.25','5/4':'4.50','8/4':'5.00'})]:
    for th,v in vals.items(): add(sp,th,'KD, planed (4/4 to 15/16", 5/4 to 1-1/8", 8/4 to 2"), straight-lined (Select & Better'+('; black & green ash' if sp=='Ash' else '; cherry select' if sp=='Cherry' else '')+')',v,KJ,'Mora','MN',KJU)
# ---- 4. Parkerville Wood Products, Manchester CT: live Ninja Tables data behind the Domestic Pricing page (raw/batch3/pk_dom.json).
#      Rows with no width premium ("--") only; QS/RS/curly/birdseye/quilted/ambrosia/swamp ash skipped.
PK='Parkerville Wood Products'; PKU='https://parkervillewoodproducts.com/domestic-pricing/'
PM={'Ash':'Ash','Cherry':'Cherry','Hickory':'Hickory','Maple, Hard':'Hard Maple','Maple, Soft':'Soft Maple','Oak, Red':'Red Oak',
    'Oak, White (PS)':'White Oak','Poplar':'Poplar','Walnut, Black':'Walnut'}
seen=set()
for r in json.load(open(R+'pk_dom.json')):
    v=r['value']; nm=v['species'].strip()
    if nm in PM and v['extra_wide'].strip()=='--':
        spec=v['specifications'].strip().rstrip(','); pr=v['price'].strip().replace(' ','')
        assert re.fullmatch(r'\$\d+\.\d\d',pr),(nm,pr)
        sp=PM[nm]; g='90/90 grade' if '90/90' in spec else 'FAS' if 'FAS' in spec else 'grade not stated'
        su='KD, R1E, S2S ('+g+(', plain-sawn' if sp=='White Oak' else '')+')'
        add(sp,v['size'].strip(),su,pr[1:],PK,'Manchester','CT',PKU); seen.add(nm)
assert seen==set(PM),set(PM)-seen
# ---- 5. Baker Lumber, White River Junction VT: online store hardwoods category (4 pages, 36/page), items priced "/Bdft".
#      Random-width (RW) or narrow standard rows only; 7"+/8"+/12"+ width rows, QS, curly, birdseye, butternut etc. skipped.
#      "MAPLE RW" rows with no hard/soft label (10/4, 16/4) are skipped.
BK='Baker Lumber'
items={}
for p in range(1,5):
    s=BeautifulSoup(open(R+f'baker_p{p}.html',errors='replace').read(),'lxml')
    for it in s.select('li.product-item'):
        a=it.select_one('a.product-item-link')
        if '/Bdft' in it.get_text(' ',strip=True): items[a['href']]=(re.sub(r'\s+',' ',a.get_text(' ',strip=True)),it.select_one('[data-price-amount]')['data-price-amount'])
B='https://www.bakerlumber.net/'
for sp,th,slug,su,v in [
    ('Ash','4/4','44-selbtr-ash-4-6','Select & Better, 4"-6" wide (surfacing not stated)','5.30'),
    ('Ash','5/4','54-selbtr-ash-rw','Select & Better, random width (surfacing not stated)','5.20'),
    ('Ash','8/4','84-sel-btr-ash-rw','Select & Better, random width (surfacing not stated)','5.75'),
    ('Cherry','4/4','44-fas-cherry-9090','FAS 90/90 grade (surfacing not stated)','6.10'),
    ('Cherry','12/4','124-fas-1f-cherry-rw','FAS/1F, random width (surfacing not stated)','7.25'),
    ('Cherry','16/4','164-fas-cherry-rw','FAS, random width (surfacing not stated)','15.00'),
    ('Hard Maple','4/4','44-fas1f-hard-maple-4-7','FAS/1F, 4"-7" wide (surfacing not stated)','5.30'),
    ('Hard Maple','5/4','54-hard-maple-rw','random width (grade and surfacing not stated)','5.80'),
    ('Hard Maple','6/4','64-selbtr-hard-maple-rw','Select & Better, random width (surfacing not stated)','5.99'),
    ('Hard Maple','8/4','84-hard-maple-4-9','4"-9" wide (grade and surfacing not stated)','6.50'),
    ('Hickory','4/4','44-sel-btr-hickory-4-6','Select & Better, 4"-6" wide (surfacing not stated)','5.30'),
    ('Hickory','5/4','54-sel-btr-hickory','Select & Better (surfacing not stated)','6.20'),
    ('Hickory','8/4','84-sel-btr-hickory','Select & Better (surfacing not stated)','10.44'),
    ('Red Oak','4/4','44-fas-1f-red-oak-4-7','FAS/1F, 4"-7" wide (surfacing not stated)','4.30'),
    ('Red Oak','5/4','54-fas1f-red-oak-rw','FAS/1F, random width (surfacing not stated)','4.70'),
    ('Red Oak','6/4','64-selbtr-rw-red-oak','Select & Better, random width (surfacing not stated)','4.95'),
    ('Red Oak','8/4','84-fas1f-red-oak-rw','FAS/1F, random width (surfacing not stated)','5.70'),
    ('Soft Maple','4/4','44-fas-1f-soft-maple','FAS/1F (surfacing not stated)','4.70'),
    ('Soft Maple','5/4','54-selbtr-soft-maple','Select & Better (surfacing not stated)','6.10'),
    ('Soft Maple','8/4','84-soft-maple','grade and surfacing not stated','5.60'),
    ('Poplar','4/4','44-yellow-poplar-4-7','4"-7" wide (grade and surfacing not stated)','3.50'),
    ('Poplar','5/4','54-yellow-poplar-4-7','4"-7" wide (grade and surfacing not stated)','4.00'),
    ('Poplar','6/4','64-yellow-poplar-4-7','4"-7" wide (grade and surfacing not stated)','4.00'),
    ('Poplar','8/4','84-yellow-poplar-4-7','4"-7" wide (grade and surfacing not stated)','4.00'),
    ('Walnut','8/4','84-prime-9070-walnut-rw','Prime 90/70 grade, random width (surfacing not stated)','16.00'),
    ('Walnut','12/4','124-fas-walnut-rw','FAS, random width (surfacing not stated)','16.20'),
    ('White Oak','4/4','44-fas-1f-white-oak-4-7','FAS/1F, 4"-7" wide (surfacing not stated)','10.27'),
    ('White Oak','5/4','54-selbtr-white-oak-rw','Select & Better, random width (surfacing not stated)','9.90'),
    ('White Oak','6/4','64-fas1f-white-oak-rw','FAS/1F, random width (surfacing not stated)','11.93'),
    ('White Oak','8/4','84-selbtr-white-oak-rw','Select & Better, random width (surfacing not stated)','13.00')]:
    u=B+slug+'.html'; assert u in items,u; nm,pr=items[u]
    assert Dn(pr)==Dn(v),(u,pr,v); assert nm.startswith(th),(nm,th)
    add(sp,th,su,v,BK,'White River Junction','VT',u)
# ---- 6. Camp Creek Hardwoods, Hawk Point MO: "ROUGH - CUT LUMBER PRICES | KILN-DRIED" on the home page (undated); planing adds $1.00/bf.
#      Cherry is marked OUT; red oak is custom-cut only; so both skipped.
CC='Camp Creek Hardwoods'; CCU='https://www.campcreekhardwoods.com/'
ct=re.sub(r'\s+',' ',flat('campcreek.html')); assert 'ROUGH - CUT LUMBER PRICES | KILN-DRIED' in ct and 'ADD $1.00 PER BF' in ct
for sp,pat,ths,v in [('Walnut','BLK WALNUT $7.50 BF 4/4 & 6/4 In Stock',['4/4','6/4'],'7.50'),('Hard Maple','HARD MAPLE $4.25 BF | Some Spalted | 4/4 In Stock',['4/4'],'4.25'),
    ('White Oak','WHT OAK $4.50 BF | 4/4 & 6/4 In Stock',['4/4','6/4'],'4.50'),('Hickory','HICKORY $4.25 BF | 4/4 In Stock',['4/4'],'4.25')]:
    assert pat in ct,pat
    for th in ths: add(sp,th,'KD, rough-cut (grade not stated; planing $1.00/bf extra)',v,CC,'Hawk Point','MO',CCU)
# ---- write seed.csv (append, CRLF, existing bytes untouched) ----
NEW={AL,ZY,KJ,PK,BK,CC}
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+d+',') in l for d in NEW)]
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
# ---- dealers.csv ----
dcols=list(csv.DictReader(open('dealers.csv')).fieldnames); dl=[d for d in csv.DictReader(open('dealers.csv')) if d['dealer'] not in NEW]
dl+= [
 dict(dealer=AL,city='Johnstown',state='OH',ships='Pickup only',shipping_note="Kiln Dried Lumber page says 'All kiln dried lumber must be picked up at the sawmill. WE DO NOT SHIP!'; all lumber rough sawn, Select & Better, no minimums, pick your own boards, no quantity discounts",shipping_source_url='https://almendingersawmill.com/kiln-dried-lumber/',date_checked=TODAY,affiliate=''),
 dict(dealer=ZY,city='Baltimore',state='OH',ships='Not stated',shipping_note="No shipping or delivery policy found; the price-list page lists yard hours (Mon-Sat mornings, afternoons by appointment) and call/text ordering",shipping_source_url=ZU,date_checked=TODAY,affiliate=''),
 dict(dealer=KJ,city='Mora',state='MN',ships='Not stated',shipping_note="No shipping or delivery policy found; the price list (updated 10/13/26) is for kiln-dried, planed and straight-line-ripped lumber sold at the Mora yard",shipping_source_url=KJU,date_checked=TODAY,affiliate=''),
 dict(dealer=PK,city='Manchester',state='CT',ships='Not stated',shipping_note="No shipping policy found on the pricing pages; showroom and yard in Manchester, CT. Prices are KD, R1E (one edge straight-lined), S2S; extra-wide boards carry posted premiums",shipping_source_url=PKU,date_checked=TODAY,affiliate=''),
 dict(dealer=BK,city='White River Junction',state='VT',ships='Yes (area not stated)',shipping_note="Online store banner says 'Fast shipping on all orders'; carriers, rates and shipping area not stated. Lumber priced per board foot in the online store",shipping_source_url='https://www.bakerlumber.net/',date_checked=TODAY,affiliate=''),
 dict(dealer=CC,city='Hawk Point',state='MO',ships='Not stated',shipping_note="Small sawmill; no shipping policy found. Site lists kiln-dried rough-cut lumber prices (undated), thickness planing for $1.00/bf extra, and asks buyers to email or text",shipping_source_url=CCU,date_checked=TODAY,affiliate='')]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
import collections
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added')
