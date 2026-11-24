#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for Rare Woods USA (Mexico, ME) to seed.csv and dealers.csv.

Source: retail price-list PDF https://www.rarewoodsusa.com/wp-content/uploads/2024/04/wood_04_04_2024.pdf
(linked from /pricelist/), dated Apr 4, 2024. The dealer confirmed by email on 2026-11-24 that the
posted list is still their most current, so date_checked is 2026-11-24 and the stale-date flag does
not apply. Conditions of sale: prices are per board foot for rough lumber unless otherwise stated.

Same rules as earlier batches: only plain/flat-sawn stock at the dealer's standard (or Prime/FAS)
grade; quartersawn, rift, figured/curly/birdseye, ambrosia, rustic/knotty, #1/#2 Common, shorts,
cutoffs, wide-board premiums, live edge, per-piece, per-lb and per-sq-ft items are skipped.
Mahogany rows only when the dealer says African mahogany. Soft Maple is omitted (only curly soft
is posted). White Oak is omitted (only #1 Common, including a quartersawn #1 Common row, is posted).
Maple Pacific is omitted as ambiguous (not labeled hard or soft).

Idempotent: removes earlier rows for this dealer first. Appends with CRLF; existing lines are kept
byte-for-byte. Sources saved under raw/rarewoods/ (gitignored).
"""
import csv,io,re,sys,collections,statistics,xml.etree.ElementTree as ET
from decimal import Decimal as Dn, ROUND_HALF_UP
from pathlib import Path

TODAY='2026-11-24'
R=Path('raw/rarewoods')
PDF_URL='https://www.rarewoodsusa.com/wp-content/uploads/2024/04/wood_04_04_2024.pdf'
DN='Rare Woods USA'
CITY,ST='Mexico','ME'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany','Basswood','Alder']
NOTE='list dated Apr 4, 2024, confirmed current 2026-11-24'
rows=[]

def add(sp,th,su,p):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),
                     dealer=DN,city=CITY,state=ST,source_url=PDF_URL,date_checked=TODAY))

def rough(extra=''):
    prefix=(extra+'; ') if extra else ''
    return f'rough ({prefix}{NOTE})'

# ---- verify posted prices against the saved pdftohtml XML (x-coordinates of the thickness headers) ----
xml_path=R/'wood.xml'
assert xml_path.exists(), xml_path
root=ET.parse(xml_path).getroot()
COLS=['4/4','5/4','6/4','8/4','10/4','12/4','16/4','24/4']
# header left edges are identical on pages 1-4 of this PDF
HDR={'4/4':386,'5/4':441,'6/4':494,'8/4':547,'10/4':602,'12/4':660,'16/4':705,'24/4':766,'lb':824}
bounds=[]
xs=[HDR[c] for c in COLS]
for a,b in zip(xs,xs[1:]):
    bounds.append((a+b)/2)
bounds.append((HDR['24/4']+HDR['lb'])/2)

def col_for(x):
    # x is the center of the price box; bands are [header left, next header left)
    edges=[HDR[c] for c in COLS]+[HDR['lb']]
    for c,start,end in zip(COLS,edges[:-1],edges[1:]):
        if start<=x<end: return c
    return 'lb'

def page_rows(page):
    items=[]
    for t in page.findall('text'):
        s=''.join(t.itertext()).strip()
        if not s: continue
        items.append((int(t.get('top')), int(t.get('left')), int(t.get('width')), s))
    # merge rows whose tops are within 4px (species + Quartersawn label, etc.)
    items.sort()
    groups=[]; cur=[]
    for it in items:
        if not cur or it[0]-cur[0][0]<=4:
            cur.append(it)
        else:
            groups.append(cur); cur=[it]
    if cur: groups.append(cur)
    out=[]
    for g in groups:
        name=' '.join(s for top,left,w,s in sorted(g,key=lambda x:x[1]) if left<360)
        prices={}
        for top,left,w,s in g:
            m=re.fullmatch(r'\$?(\d+\.\d{2})',s)
            if m and left>=360:
                # assign by the center of the price box into [header_left, next_header_left)
                prices[col_for(left+w/2)]=m.group(1)
        out.append((name,prices))
    return out

posted={}
for page in root.findall('page')[:4]:
    for name,prices in page_rows(page):
        if name:
            posted[name]=prices

def expect(name, expected):
    got=posted.get(name)
    assert got==expected, (name, got, expected)

expect('Alder (cabinet grade)', {'4/4':'5.00'})
expect('Ash', {'4/4':'4.50','5/4':'5.00','6/4':'5.50','8/4':'6.00','12/4':'7.00','16/4':'11.00'})
expect('Basswood', {'4/4':'5.00','8/4':'8.00','16/4':'8.00'})
expect('Cherry FAS  90/70', {'4/4':'7.50','6/4':'8.50','8/4':'9.50'})
expect('Hickory prime', {'4/4':'6.75'})
expect('Mahogany - African', {'4/4':'7.00','6/4':'7.50','8/4':'8.00','12/4':'9.00'})
expect('Maple - Hard', {'4/4':'5.00','6/4':'5.50','8/4':'6.00'})
expect('Oak Red, Prime', {'4/4':'5.00','6/4':'6.00'})
expect('Poplar', {'4/4':'4.50'})
expect('Sapele', {'4/4':'7.50','5/4':'7.50','6/4':'7.50','8/4':'7.50'})
expect('Walnut - American (Prime)', {'4/4':'12.00','6/4':'13.00','8/4':'14.00','12/4':'15.00'})

# included rows
add('Alder','4/4',rough('cabinet grade'),'5.00')
for th,v in [('4/4','4.50'),('5/4','5.00'),('6/4','5.50'),('8/4','6.00'),('12/4','7.00'),('16/4','11.00')]:
    add('Ash',th,rough(),v)
for th,v in [('4/4','5.00'),('8/4','8.00'),('16/4','8.00')]:
    add('Basswood',th,rough(),v)
for th,v in [('4/4','7.50'),('6/4','8.50'),('8/4','9.50')]:
    add('Cherry',th,rough('FAS 90/70'),v)
add('Hickory','4/4',rough('Prime'),'6.75')
for th,v in [('4/4','7.00'),('6/4','7.50'),('8/4','8.00'),('12/4','9.00')]:
    add('Mahogany',th,rough('African mahogany'),v)
for th,v in [('4/4','5.00'),('6/4','5.50'),('8/4','6.00')]:
    add('Hard Maple',th,rough(),v)
for th,v in [('4/4','5.00'),('6/4','6.00')]:
    add('Red Oak',th,rough('Prime'),v)
add('Poplar','4/4',rough(),'4.50')
for th,v in [('4/4','7.50'),('5/4','7.50'),('6/4','7.50'),('8/4','7.50')]:
    add('Sapele',th,rough(),v)
for th,v in [('4/4','12.00'),('6/4','13.00'),('8/4','14.00'),('12/4','15.00')]:
    add('Walnut',th,rough('Prime'),v)

assert len(rows)==32, len(rows)

# skipped (Index species only; verified present on the list)
SKIPPED=[
    ('Ash - 4" Figured Tiger Ash','figured'),
    ('Ash (Olive Euro Fiddleback)','figured'),
    ('Ash Slabs live edged.','live edge'),
    ('Ash - Swamp','special variety (swamp ash), not standard ash'),
    ('Ash - Swamp 13" & wider','special variety and wide-board premium'),
    ('Cherry 1 common','#1 Common'),
    ('Cherry 2 common','#2 Common'),
    ('Cherry Curly','figured'),
    ('Cherry Rift & quartered','rift/quartersawn'),
    ('Hickory (# 1 common)','#1 Common'),
    ('Hickory 1c - s2s','#1 Common'),
    ('Mahogany - African R & Q','rift/quartersawn'),
    ('Mahogany - Brazilian (Genuine)','not African mahogany'),
    ('Mahogany - Crotch','figured/specialty'),
    ('Mahogany Honduras Backing boards','backing boards, priced in the per-lb column'),
    ('Mahogany Pod (Chamfuta / Doussie)','different species'),
    ('Mahogany Santos','Santos mahogany; 5/8" price, nonstandard thickness'),
    ('Maple - Ambrosia','ambrosia'),
    ('Maple - Ambrosia Slabs','ambrosia / slabs'),
    ('Maple - Birdseye','figured'),
    ('Maple - Birdseye heavy figure','figured'),
    ('Maple - Birdseye peeler cores (+- 84" long)','per piece'),
    ('Maple - Birdseye Roasted','figured'),
    ('Maple Hard - blanks','per piece'),
    ('Maple, Hard, Slabs live edged *','live edge'),
    ('Maple Pacific','ambiguous: not labeled hard or soft maple'),
    ('Maple quarter cut','quartersawn'),
    ('Maple - Curly Soft','figured (no plain Soft Maple is posted)'),
    ('Maple - Curly Soft - High Figure Slabs','figured / slabs'),
    ('Maple - Curly Soft Roasted','figured'),
    ('Maple - Curly Hard','figured'),
    ('Maple - Curly Hard - 9" & wider','figured and wide-board premium'),
    ('Maple - Curly Hard - High Figure','figured'),
    ('Maple - Curly Hard - Billets 3"x3"x37"','per piece'),
    ('Maple - Curly Hard - Dowels. 2 13/16" x 37"','per piece'),
    ('Oak, White #1 common','#1 Common (no FAS/Prime White Oak posted)'),
    ('Oak White,(# 1 common) Quartersawn','#1 Common and quartersawn'),
    ('Sapele slicer boards','specialty cut'),
    ('Walnut - African','not American walnut'),
    ('Walnut - American 1c','#1 Common'),
    ('Walnut - American 2c','#2 Common'),
    ('Walnut - American (cores)','specialty; priced in the per-lb column'),
    ('Walnut - American (Figured)','figured'),
    ('Walnut - American (rustic) 3/4": $3.50','rustic and nonstandard 3/4" thickness'),
    ('Walnut - Australian','not American walnut'),
]
for name,why in SKIPPED:
    key=name
    # rustic walnut is stored under a longer XML name
    if name.startswith('Walnut - American (rustic)'):
        assert any(k.startswith('Walnut - American (rustic)') for k in posted), posted
    else:
        assert key in posted, key

NEW={DN}
old=[r for r in csv.DictReader(open('seed.csv')) if r['dealer'] not in NEW and not r['dealer'].startswith('Customer')]
by=collections.defaultdict(list)
for r in old: by[(r['species'],r['thickness'])].append(float(r['price_per_bf']))
for r in rows:
    a=by.get((r['species'],r['thickness'])); p=float(r['price_per_bf'])
    if not a: print('NO-COMPARE',r['dealer'],r['species'],r['thickness'],p); continue
    if p>max(a) or p<min(a): print('OUTSIDE',r['dealer'],r['species'],r['thickness'],p,'min',min(a),'med',statistics.median(a),'max',max(a))

print('SKIPPED:')
for name,why in SKIPPED:
    print(f'  {name}: {why}')

if '--dry' in sys.argv:
    print(collections.Counter(r['dealer'] for r in rows),len(rows),'rows')
    print(collections.Counter(r['species'] for r in rows))
    sys.exit()

cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+d+',') in l or (',"'+d+'",') in l for d in NEW)]
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())

dcols=list(csv.DictReader(open('dealers.csv')).fieldnames)
dl=[d for d in csv.DictReader(open('dealers.csv')) if d['dealer'] not in NEW]
dl.append(dict(
    dealer=DN,city=CITY,state=ST,
    ships='Yes (continental US; free on online orders over $100)',
    shipping_note="Shipping page: free shipping to the continental US (excluding Hawaii and Alaska) on online orders over $100, usually UPS Ground (sometimes USPS); larger orders may ship LTL; packages over 46 inches have a $12 surcharge. Custom phone/email orders ship at the buyer's expense, with a $10 handling fee under $100 (no minimum for walk-ins). Showroom at 120 Swift River Road, Mexico, ME, Tue-Fri 8-4 and Sat 9-1. Prices are per board foot for rough lumber (list dated Apr 4, 2024, confirmed current 2026-11-24)",
    shipping_source_url='https://www.rarewoodsusa.com/shipping/',
    date_checked=TODAY,affiliate='',date_added=TODAY))
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added')
print(collections.Counter(r['species'] for r in rows))
