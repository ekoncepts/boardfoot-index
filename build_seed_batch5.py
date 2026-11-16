#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for dealer batch 5 (Monday 2026-11-16) to seed.csv and dealers.csv.
Sources saved under raw/batch5/ (gitignored). Same rules as earlier batches: only plain/flat-sawn stock at each dealer's standard grade
and smallest-quantity (retail) tier; quartersawn, rift, figured/curly/birdseye, ambrosia, wormy, rustic/knotty, #1/#2 Common, shorts,
wide-board premiums, live edge and per-linear-foot items are skipped. Mahogany rows only when the dealer says African mahogany.
B.C.W. Lumber & Plywood and Caird Lumber post CAD prices: converted to USD at the Bank of Canada daily average for 2026-11-13
(1.4257 CAD per USD, raw/batch5/boc_usdcad.json); the original CAD price and rate are kept in the surfacing note.
Idempotent: removes earlier rows for these dealers first. Appends with CRLF; existing lines are kept byte-for-byte."""
import csv,io,re,json,subprocess,sys,collections,statistics
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-11-16'; R='raw/batch5/'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany','Basswood','Alder']
rows=[]
def add(sp,th,su,p,dn,city,st,url):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),dealer=dn,city=city,state=st,source_url=url,date_checked=TODAY))
def txt(f): return re.sub(r'\s+',' ',BeautifulSoup(open(R+f,errors='replace').read(),'lxml').get_text(' '))
FX=Dn('1.4257')
assert json.load(open(R+'boc_usdcad.json'))['observations'][0]=={'d':'2026-11-13','FXUSDCAD':{'v':'1.4257'}}
def cad(v): return (Dn(v)/FX).quantize(Dn('0.01'),ROUND_HALF_UP)
CADN='posted CAD ${}/bf converted to USD at 1.4257 CAD/USD (Bank of Canada, 2026-11-13)'

# ---- 1. Frank Thomas Sawmill, Fallston MD: price-list image "Prices effective: Jan 1, 2026" (raw/batch5/thomas_jan2026.jpg), read by eye.
#      "Lumber is sold by the Board Foot (BF)"; "All lumber is or can be surfaced two sides"; 12"+ wide is call for quote. 2-1/4" poplar skipped.
FT='Frank Thomas Sawmill'; FTU='https://thomassawmill.com/dry_lumber_price_list.htm'
assert 'Lumber_Price_List_January_1__%202026.jpg' in open(R+'thomas.html',errors='replace').read()
FS='dry lumber, can be surfaced two sides (list effective Jan 1, 2026)'
for th,v in [('4/4','5.00'),('5/4','5.50'),('6/4','5.80'),('8/4','6.00')]: add('Red Oak',th,FS,v,FT,'Fallston','MD',FTU)
add('White Oak','4/4',FS,'10.00',FT,'Fallston','MD',FTU)
for th,v in [('4/4','4.50'),('5/4','4.50'),('6/4','4.80'),('8/4','5.00')]: add('Poplar',th,FS,v,FT,'Fallston','MD',FTU)
add('Cherry','4/4',FS[:-1]+'; FAS)','6.00',FT,'Fallston','MD',FTU)
add('Walnut','4/4',FS[:-1]+'; Select)','10.00',FT,'Fallston','MD',FTU)
for th,v in [('4/4','7.00'),('6/4','7.00'),('8/4','7.50'),('10/4','7.50')]: add('Hard Maple',th,FS,v,FT,'Fallston','MD',FTU)

# ---- 2. West Penn Hardwoods, Conover NC: live catalog (POST /get-products, domestic category 3 and exotic category 4), sold by the BF, 10 BF minimum online.
#      Boards generally 4-7" random width, 6-8' long; 8-12" wide domestic +20%. QS, ambrosia, curly, shorts, live edge skipped.
WP='West Penn Hardwoods'; WPD='https://wphardwoods.com/products/categories/domestic-lumber'; WPE='https://wphardwoods.com/products/categories/exotic-lumber'
wp={}
import glob
for f in sorted(glob.glob(R+'wp_c*_p*.json')):
    for p in json.load(open(f))['products']: wp[(f.split('wp_')[1][:2],p['name'].strip())]=p
WM=[('Ash','ASH'),('Basswood','BASSWOOD'),('Cherry','CHERRY'),('Hard Maple','HARD MAPLE'),('Hickory','HICKORY'),('Poplar','POPLAR'),('Red Oak','RED OAK'),('Walnut','WALNUT')]
for sp,lab in WM:
    n=0
    for th in ['4/4','5/4','6/4','8/4','12/4','16/4']:
        p=wp.get(('c3',f'{lab} {th}'))
        if p: assert p['size']==th; add(sp,th,'random width 4-7", 6-8 ft (surfacing not stated; 10 BF online minimum)',p['price'],WP,'Conover','NC',WPD); n+=1
    assert n,lab
for sp,lab,ex in [('Mahogany','AFRICAN MAHOGANY','; African mahogany'),('Sapele','SAPELE','')]:
    for th in ['4/4','5/4','6/4','8/4']:
        p=wp[('c4',f'{lab} {th}')]; add(sp,th,f'random width (surfacing not stated; 10 BF online minimum{ex})',p['price'],WP,'Conover','NC',WPE)

# ---- 3. Les Steen Hardwoods, North Little Rock AR: /price-list "Prices as of October 14, 2026". All lumber dried and S2S, usually SLR.
#      FAS/Sel rows under 9" wide; walnut 4/4 and 5/4 use the 8' (under 8-1/2" wide) tier. 9/4 rows skipped.
LS='Les Steen Hardwoods'; LSU='https://www.steenhardwoods.com/price-list'
st=txt('steen.html'); assert 'Prices as of October 14, 2026' in st and 'All lumber is dried and surfaced 2 sides' in st
LSS='S2S, usually straight-line ripped (FAS/Sel)'
def steen(sp,sec,lab,v,th,note=''):
    i=st.index(sec+' '); j=st.index(lab+' $'+v+' per bd. ft.',i); assert j-i<2500,(sec,lab,v)
    add(sp,th,LSS[:-1]+note+')',v,LS,'North Little Rock','AR',LSU)
for th,v in [('4/4','7.15'),('5/4','8.25'),('8/4','9.00')]: steen('Ash','Domestic Species Ash',th+' FAS/Sel',v,th)
steen('Basswood','Basswood 16/4','16/4 FAS/Sel','6.10','16/4')
for th,v in [('4/4','7.15'),('5/4','7.55'),('8/4','8.75')]: steen('Cherry','Cherry & Sassafras',th+' FAS/Sel',v,th,'; listed as Cherry & Sassafras')
steen('Cherry','Cherry & Sassafras','12/4 FAS/Sel','12.00','12/4','; listed as Cherry & Sassafras')
for th,v in [('4/4','10.45'),('5/4','10.95'),('8/4','11.70')]: steen('Hard Maple','Maple (Hard)',th+' FAS/Sel',v,th)
steen('Soft Maple','Maple (Soft)','4/4 FAS/Sel','8.85','4/4'); steen('Soft Maple','Maple (Soft)','10/4 FAS','9.75','10/4')
for th,v in [('4/4','5.60'),('5/4','6.95'),('8/4','8.65')]: steen('Red Oak','Oak (Red)',th+' FAS/Sel',v,th)
for th,v in [('4/4','10.40'),('5/4','11.65'),('8/4','12.35')]: steen('White Oak','Oak (White)',th+' FAS/Sel',v,th)
for th,v in [('4/4','4.15'),('5/4','4.90')]: steen('Poplar','Poplar',th+' FAS/Sel',v,th)
steen('Walnut','Walnut 4/4','4/4 FAS/Sel 8\' less than 8½" wide','13.45','4/4','; 8 ft, under 8-1/2" wide')
steen('Walnut','Walnut 4/4','5/4 FAS/Sel 8\' less than 8½" wide','14.15','5/4','; 8 ft, under 8-1/2" wide')
steen('Walnut','Walnut 4/4','8/4 FAS Sel','23.15','8/4')
for th,v in [('4/4','9.70'),('8/4','12.85')]: steen('Mahogany','Mahogany (African)',th,v,th,'; African mahogany')

# ---- 4. Mark Frieden Hardwoods, Pomona KS: products.html "As of Jan 2026, these are my current lumber prices per board foot".
#      "Everything listed is a clear grade of lumber, kiln dried and planed." Unlabeled rows are the base (4/4) row. 8/4 white oak (mainly QS),
#      premium-dark 6/4 walnut, cheaper 13/16" walnut, rustic (knotty) alder, birdseye/curly maple skipped.
MF='Mark Frieden Hardwoods'; MFU='https://www.friedenlumber.com/products.html'
fr=txt('frieden.html'); assert 'As of Jan 2026, these are my current lumber prices per board foot' in fr and 'kiln dried and planed' in fr
MFS='KD, planed, clear grade (list as of Jan 2026)'
def fri(sp,lab,v,th,note=''):
    assert re.search(r'(^|\s)'+re.escape(lab)+r' \$'+re.escape(v)+r'(\s|$)',fr),(lab,v); add(sp,th,MFS[:-1]+note+')',v,MF,'Pomona','KS',MFU)
fri('Red Oak','Red Oak','4.95','4/4','; thickness not labeled, base row'); fri('Red Oak','8/4 Red Oak','7.25','8/4'); fri('Red Oak','6/4 Red Oak','7.25','6/4')
fri('White Oak','White Oak','9.25','4/4','; thickness not labeled, base row')
fri('Walnut','Walnut','7.50','4/4','; thickness not labeled, base row'); fri('Walnut','8/4 Walnut','15.00','8/4','; premium dark')
fri('Poplar','Poplar','4.95','4/4','; thickness not labeled, base row')
for th in ['6/4','8/4']: fri('Poplar','8/4 & 6/4 Poplar','7.00',th)
fri('Ash','Ash','5.95','4/4','; thickness not labeled, base row'); fri('Ash','8/4 Ash','8.00','8/4')
fri('Basswood','Basswood','4.95','4/4','; thickness not labeled, base row'); fri('Basswood','8/4 Basswood','6.95','8/4')
fri('Cherry','Cherry','5.95','4/4','; thickness not labeled, base row'); fri('Cherry','8/4 Cherry','8.50','8/4')
fri('Soft Maple','Soft Maple when available','6.75','4/4','; thickness not labeled, base row; when available')
fri('Hard Maple','Hard Maple','6.75','4/4','; thickness not labeled, base row')
for th in ['6/4','8/4']: fri('Hard Maple','8/4 & 6/4 Hard Maple','9.00',th)
fri('Hickory','Pecan/Hickory','5.50','4/4','; listed as Pecan/Hickory; thickness not labeled, base row'); fri('Hickory','8/4 Pecan/Hickory','8.00','8/4','; listed as Pecan/Hickory')
fri('Mahogany','African Mahogany','8.00','4/4','; African mahogany; thickness not labeled, base row'); fri('Mahogany','8/4 African Mahogany','9.50','8/4','; African mahogany')
fri('Sapele','Sapeli','9.00','4/4','; listed as Sapeli; thickness not labeled, base row'); fri('Sapele','8/4 sapele','10.50','8/4')

# ---- 5. B.C.W. Lumber & Plywood, Brantford ON: /products/lumber/ table "Last edited Dec 2025". "All lumber is rough"; planing $0.50/bf per 1/4". CAD.
#      Shorts, brown hard maple, birdseye/curly, quartersawn and pine skipped. 1" white oak uses the flat-sawn row.
BC='B.C.W. Lumber & Plywood'; BCU='https://www.bcwpl.ca/products/lumber/'
bt=txt('bcw.html'); assert 'Last edited Dec 2025' in bt and 'All lumber is rough' in bt
BIN={'1"':'4/4','1 1/2"':'6/4','2"':'8/4','3"':'12/4'}
def bcw(sp,size,lab,v,note=''):
    assert f'{size} {lab} ${v}' in bt,(size,lab,v)
    add(sp,BIN[size],'rough (list last edited Dec 2025'+note+'); '+CADN.format(v),cad(v),BC,'Brantford','ON',BCU)
bcw('Ash','1"','Ash','5.50'); bcw('Ash','2"','Ash','6.50')
bcw('Basswood','1"','Basswood','3.50'); bcw('Basswood','2"','Basswood','4.50')
bcw('Cherry','1"','Colour Sorted Cherry','6.00','; colour sorted'); bcw('Cherry','2"','Cherry','7.00'); bcw('Cherry','3"','Cherry','10.00')
bcw('Hard Maple','1"','White Hard Maple','7.25','; white'); bcw('Hard Maple','1 1/2"','Hard Maple','7.50'); bcw('Hard Maple','2"','White Hard Maple','8.00','; white')
bcw('Red Oak','1"','Red Oak','4.50'); bcw('Red Oak','1 1/2"','Red Oak','5.00'); bcw('Red Oak','2"','Red Oak','5.75')
bcw('White Oak','1"','White Oak Flat Sawn','7.00','; flat sawn'); bcw('White Oak','2"','White Oak','13.00')
bcw('Poplar','1"','Poplar','4.00'); bcw('Poplar','1 1/2"','Poplar','4.25'); bcw('Poplar','2"','Poplar','4.50')
bcw('Walnut','1"','Walnut','14.00'); bcw('Walnut','2"','Walnut','12.50')

# ---- 6. Caird Lumber Ltd, Kingston ON outlet (mill in Verona): domestic pricing PDF linked from /hardwoods-domestic. "Prices are per board foot",
#      "Prices exclude HST", "Select Grade, Rough cut on 6' lengths or longer". CAD. "Maple (Regular)" (hard/soft not stated), shorts, wormy,
#      spalted, roasted, birch, butternut and pine skipped.
CL='Caird Lumber Ltd'; CLU='https://cairdlumberltd.ca/hardwoods-domestic'
ct=subprocess.run(['pdftotext','-layout',R+'caird.pdf','-'],capture_output=True,text=True).stdout
assert 'Prices exclude HST' in ct and '*Prices are per board foot*' in txt('caird.html')
def caird(sp,lab,th,v,note=''):
    assert re.search(r'^\s*'+re.escape(lab)+r'\s{2,}'+re.escape(th)+r'”\s+\$'+re.escape(v)+r'\s*$',ct,re.M),(lab,th,v)
    add(sp,th,'rough, KD, Select, 6 ft+ (excl. HST'+note+'); '+CADN.format(v),cad(v),CL,'Kingston','ON',CLU)
caird('Ash','Ash','4/4','5.50')
caird('Basswood','Basswood','4/4','4.21'); caird('Basswood','Basswood','8/4','5.38')
for th,v in [('4/4','17.25'),('6/4','17.25'),('8/4','17.60')]: caird('Walnut','Black Walnut',th,v)
caird('Cherry','Cherry','4/4','5.50'); caird('Cherry','Cherry','8/4','6.46')
caird('Hickory','Hickory','4/4','4.84')
for th,v in [('4/4','4.48'),('6/4','4.66'),('8/4','4.66')]: caird('Poplar','Poplar (Yellow)',th,v,'; yellow poplar')
caird('Red Oak','Red Oak','4/4','5.48'); caird('Soft Maple','Soft Maple','4/4','7.90')
for th,v in [('4/4','14.74'),('6/4','15.82'),('8/4','18.88')]: caird('White Oak','White Oak',th,v)

# ---- 7. White Oak Orchard, Trenton SC: /pages/lumber "Prices shown below are per board foot". Air-dried (about 8-12% MC), random width,
#      4/4, 5/4, 6/4 and 8/4 at one price. Rough-sawn column used (S4S is +$2/bf). Slabs and 4x4 timbers skipped.
WO='White Oak Orchard'; WOU='https://www.whiteoakorchard.com/pages/lumber'
wt=txt('woo.html'); assert 'Species Rough-Sawn S4S White Oak $6 per bd ft $8 per bd ft Red Oak $5 per bd ft $7 per bd ft' in wt and 'air-dried to approximately 8–12% moisture content' in wt
for th in ['4/4','5/4','6/4','8/4']:
    add('White Oak',th,'rough-sawn, air-dried (about 8-12% MC), random width; same price 4/4-8/4','6.00',WO,'Trenton','SC',WOU)
    add('Red Oak',th,'rough-sawn, air-dried (about 8-12% MC), random width; same price 4/4-8/4','5.00',WO,'Trenton','SC',WOU)

NEW=[FT,WP,LS,MF,BC,CL,WO]
# ---- outlier report vs the existing index (same species+thickness) ----
old=[r for r in csv.DictReader(open('seed.csv')) if r['dealer'] not in NEW and not r['dealer'].startswith('Customer')]
by=collections.defaultdict(list)
for r in old: by[(r['species'],r['thickness'])].append(float(r['price_per_bf']))
for r in rows:
    a=by.get((r['species'],r['thickness'])); p=float(r['price_per_bf'])
    if not a: print('NO-COMPARE',r['dealer'],r['species'],r['thickness'],p); continue
    if p>max(a)*1.0 or p<min(a)*1.0: print('OUTSIDE',r['dealer'],r['species'],r['thickness'],p,'min',min(a),'med',statistics.median(a),'max',max(a))
if '--dry' in sys.argv:
    print(collections.Counter(r['dealer'] for r in rows),len(rows)); sys.exit()

# ---- write seed.csv (append, CRLF, existing bytes untouched) ----
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
 dict(dealer=FT,city='Fallston',state='MD',ships='Not stated',shipping_note="No shipping policy found; sawmill yard at 2019 Fallston Rd, open Mon-Fri 8-4:30 and Sat 8-12 (closed 12-1 daily). Lumber 12\" and wider is call for a quote; all lumber is or can be surfaced two sides",shipping_source_url=FTU,date_checked=TODAY,affiliate=''),
 dict(dealer=WP,city='Conover',state='NC',ships='Yes (UPS Ground or freight, continental US)',shipping_note="Shipping page: orders under about 100 BF usually ship UPS Ground, larger orders by common carrier to a terminal or commercial address ($45 residential fee); no international orders. 10 BF minimum online; domestic boards 8-12\" wide add 20%",shipping_source_url='https://wphardwoods.com/shipping-info',date_checked=TODAY,affiliate=''),
 dict(dealer=LS,city='North Little Rock',state='AR',ships='Not stated',shipping_note="No shipping policy found; retail showroom open Wednesday and Saturday 9 AM-12 noon or by appointment, cash or check only. All lumber dried and surfaced two sides; prices shown are FAS/Sel under 9\" wide",shipping_source_url=LSU,date_checked=TODAY,affiliate=''),
 dict(dealer=MF,city='Pomona',state='KS',ships='Pickup (prefers not to ship)',shipping_note="Contact page: he prefers a phone call and prefers not to ship; sells lumber one board at a time, kiln dried and planed. Price list dated Jan 2026",shipping_source_url='https://www.friedenlumber.com/',date_checked=TODAY,affiliate=''),
 dict(dealer=BC,city='Brantford',state='ON',ships='Not stated',shipping_note="No shipping policy found; retail shop open Mon-Fri 9-5 and Sat 9-12. Lumber is rough; planing is $0.50/bf per 1/4\". Prices are posted in Canadian dollars; shown here converted to USD at 1.4257 CAD/USD (Bank of Canada, 2026-11-13). List last edited Dec 2025",shipping_source_url=BCU,date_checked=TODAY,affiliate=''),
 dict(dealer=CL,city='Kingston',state='ON',ships='Not stated',shipping_note="No shipping policy found; Kingston hardwood outlet (35 Terry Fox Dr, Unit 202) open Mon-Fri 8-5; mill office in Verona by appointment. Select grade, rough, 6 ft and longer; prices exclude HST. Posted in Canadian dollars; shown here converted to USD at 1.4257 CAD/USD (Bank of Canada, 2026-11-13)",shipping_source_url='https://cairdlumberltd.ca/hardwood-retail-outlet',date_checked=TODAY,affiliate=''),
 dict(dealer=WO,city='Trenton',state='SC',ships='No (pickup; local delivery within 50 miles)',shipping_note="Lumber page: 'We do not ship lumber orders'; viewing and pickup by appointment only. Lumber is air-dried to about 8-12% moisture content. S4S is $2/bf more than the rough-sawn price shown",shipping_source_url=WOU,date_checked=TODAY,affiliate='')]
for d in nd: d['date_added']=TODAY
dl+=[d for d in nd if d['dealer'] not in HOLD]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added; held:',HOLD or 'none')
print(collections.Counter((r['dealer'],r['species']) for r in rows if r['species'] in ('Basswood','Alder')))
