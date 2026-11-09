#!/usr/bin/env python3
"""Append dealer-posted $/bf prices for dealer batch 4 (checked 2026-11-09) to seed.csv and dealers.csv.
Sources saved under raw/batch4/ (gitignored). Same rules as earlier batches: only plain/flat-sawn stock at each dealer's
standard grade and the smallest-quantity (retail) price tier; quartersawn, rift, figured/curly/birdseye, ambrosia, wormy,
rustic/knotty, #1 Common, wide-board premiums, live edge, shorts and per-linear-foot items are skipped. Mahogany rows are only
used when the dealer says African mahogany (type-not-stated mahogany is skipped, as it may be genuine/Honduran).
New this batch: Basswood and Alder rows (BoardFoot didn't track these species before). All eight dealers post USD prices.
Idempotent: removes earlier rows for these dealers first. Appends with CRLF; existing lines are kept byte-for-byte."""
import csv,io,re,subprocess
from decimal import Decimal as Dn, ROUND_HALF_UP
from bs4 import BeautifulSoup
TODAY='2026-11-09'; R='raw/batch4/'
SP=['Poplar','Red Oak','Hickory','Soft Maple','Ash','Cherry','Hard Maple','White Oak','Sapele','Walnut','Mahogany','Basswood','Alder']
rows=[]
def add(sp,th,su,p,dn,city,st,url):
    assert sp in SP and re.fullmatch(r'\d+/4',th),(sp,th)
    p=Dn(str(p)).quantize(Dn('0.01'),ROUND_HALF_UP); assert Dn('1')<p<Dn('60'),(sp,th,p)
    rows.append(dict(species=sp,thickness=th,surfacing=su,price_per_bf=str(p),dealer=dn,city=city,state=st,source_url=url,date_checked=TODAY))
def pdf(f): return subprocess.run(['pdftotext','-layout',R+f,'-'],capture_output=True,text=True).stdout
IN={'1"':'4/4','1”':'4/4','1-1/4"':'5/4','1-1/2"':'6/4','2"':'8/4','2-1/2"':'10/4','3"':'12/4','3”':'12/4','4"':'16/4'}

# ---- 1. Badger Hardwoods of Wisconsin, Walworth WI: products.html table. "prices ... based on surfaced two sides and random widths and lengths"
BD='Badger Hardwoods of Wisconsin'; BU='https://www.badgerwood.com/products.html'
s=BeautifulSoup(open(R+'badger.html',errors='replace').read(),'lxml')
assert 'surfaced two sides and random' in re.sub(r'\s+',' ',s.get_text(' '))
bt={}
for tr in s.find_all('tr'):
    tds=tr.find_all('td',recursive=False)
    if len(tds)==3:
        c=[t.get_text('\n',strip=True) for t in tds]
        bt[re.sub(r'\s+',' ',c[0].split(':')[0]).strip()]=list(zip(c[1].split('\n'),c[2].split('\n')))
BM={'African Mahogany':'Mahogany','Alder':'Alder','Ash':'Ash','Basswood':'Basswood','Cherry':'Cherry','Hard Maple':'Hard Maple','Hickory':'Hickory',
    'Poplar':'Poplar','Red Oak':'Red Oak','Soft Maple':'Soft Maple','Walnut':'Walnut','White Oak':'White Oak'}
for lab,sp in BM.items():
    n=0
    for th_gr,pr in bt[lab]:
        m=re.fullmatch(r'(\d+/4) (.+)',th_gr); pm=re.fullmatch(r'\$(\d+\.\d\d)/bf',pr)
        if not (m and pm): continue
        gr=m.group(2)
        if gr in ('Rustic',) : continue
        extra='; African mahogany' if sp=='Mahogany' else ''
        add(sp,m.group(1),f'S2S, random width & length ({gr}{extra})',pm.group(1),BD,'Walworth','WI',BU); n+=1
    assert n,lab

# ---- 2. Bell Forest Products, Ishpeming MI: /exotic-lumber/prices/ table, "< 10" BF column (10-99 and 100-499 BF tiers are cheaper)
BF='Bell Forest Products'; BFU='https://www.bellforestproducts.com/exotic-lumber/prices/'
s=BeautifulSoup(open(R+'bell.html',errors='replace').read(),'lxml')
bl={}
for tr in s.find_all('tr'):
    c=[x.get_text(' ',strip=True) for x in tr.find_all(['td','th'])]
    if len(c)==4 and c[1].startswith('$'): bl[re.sub(r'\s+',' ',c[0])]=c[1][1:]
def bell(sp,label,th,su):
    k=[k for k in bl if k.startswith(label)]; assert len(k)==1,(label,k)
    add(sp,th,su+'; under 10 BF price',bl[k[0]],BF,'Ishpeming','MI',BFU)
for th in ['5/4','6/4','8/4','12/4','16/4']: bell('Basswood',f'{th} Basswood ( Sel & Btr )',th,'Sel & Btr (surfacing not stated)')
bell('Cherry','4/4 Cherry ( Sel & Btr , 90/70+ Red, S2S','4/4','S2S (Sel & Btr, 90/70+ red)')
bell('Cherry','5/4 Cherry ( Sel & Btr , 90/80+ Red, S2S','5/4','S2S (Sel & Btr, 90/80+ red)')
bell('Cherry','8/4 Cherry ( Sel & Btr , 90/90+ Red, Rough','8/4','rough (Sel & Btr, 90/90+ red)')
bell('Cherry','12/4 Cherry ( Sel & Btr , 90/70+ Red, Rough','12/4','rough (Sel & Btr, 90/70+ red)')
bell('Hard Maple','4/4 Hard Maple ( Sel & Btr','4/4','S2S (Sel & Btr, #1 & 2 white)')
bell('Hard Maple','5/4 Hard Maple ( Sel & Btr','5/4','S2S (Sel & Btr, #1 & 2 white)')
bell('Hard Maple','8/4 Hard Maple ( Sel & Btr','8/4','S2S (Sel & Btr, #1 & 2 white)')
bell('Hard Maple','12/4 Hard Maple ( Sel & Btr','12/4','S2S (Sel & Btr, sap & btr)')
bell('Hickory','4/4 Hickory ( Sel & Btr','4/4','S2S (Sel & Btr, unselected)')
bell('Poplar','4/4 Poplar (FAS/1F','4/4','S2S (FAS/1F)'); bell('Poplar','8/4 Poplar (FAS/1F','8/4','S2S (FAS/1F)')
bell('Red Oak','4/4 Red Oak ( Sel','4/4','S2S (Sel & Btr)'); bell('Red Oak','8/4 Red Oak ( Sel','8/4','S2S (Sel & Btr)')
bell('Soft Maple','4/4 Soft Maple ( Sel & Btr','4/4','Sel & Btr, sap & btr, 15/16" (surfacing not stated)')
bell('Soft Maple','8/4 Soft Maple ( Sel & Btr','8/4','S2S (Sel & Btr, sap & btr)')
bell('Soft Maple','12/4 Soft Maple ( Sel & Btr','12/4','rough (Sel & Btr, sap & btr)')
for th,su in [('4/4','S2S'),('5/4','S2S'),('7/4','S2S'),('8/4','rough')]:
    bell('Walnut',f'{th} Walnut (FAS/1F Oak Rules',th,f'{su} (FAS/1F, 90/70+ brown, steamed)')
for th in ['10/4','12/4']: bell('Walnut',f'{th} Walnut (FAS/1F, 90/50',th,'rough (FAS/1F, 90/50+ brown, steamed)')
bell('Ash','4/4 White Ash','4/4','S2S (Sel & Btr; white ash)'); bell('Ash','8/4 White Ash','8/4','S2S (Sel & Btr; white ash)'); bell('Ash','12/4 White Ash','12/4','rough (Sel & Btr; white ash)')
bell('White Oak','4/4 White Oak ( Sel','4/4','S2S (Sel & Btr)'); bell('White Oak','8/4 White Oak ( Sel','8/4','S2S (Sel & Btr)')
for th in ['4/4','5/4','8/4','12/4']: bell('Mahogany',f'{th} African Mahogany',th,'African mahogany (Khaya; surfacing not stated)')

# ---- 3. L.L. Johnson Lumber / Johnson's Workbench, Charlotte MI: hardwood list PDF "PRICES UPDATED 10/01/2026", 1+ BF column.
#      Hardwood page: "Prices listed are for rough lumber, sold random width, and random length." Where 1" is split by length, the 9-10' row is used.
LJ='L.L. Johnson Lumber'; LJU='https://lljlumber.com/wp-content/uploads/wa_gsheet_pdf/hardwood-list-sheet.pdf'
lt=pdf('llj.pdf'); assert 'PRICES UPDATED 10/01/2026' in lt
assert 'Prices listed are for rough lumber, sold random width, and random length' in re.sub(r'\s+',' ',BeautifulSoup(open(R+'llj_hw.html',errors='replace').read(),'lxml').get_text(' '))
secs={}; cur=None
for line in lt.split('\n'):
    m=re.match(r'^([A-Z][A-Z .\-–/&]+?)\s{2,}(BF:|Lineal)',line)
    if m: cur=m.group(1).strip(); secs[cur]=[]; continue
    if cur: secs[cur].append(line)
def llj(sp,sec,size,grade,v,note=''):
    pat=re.compile(r'^'+re.escape(size)+r'\s+'+re.escape(grade)+r'\s+\(\$\s+'+re.escape(v)+r'\)')
    assert any(pat.match(l) for l in secs[sec]),(sec,size,grade,v)
    g=re.sub(r"\s*\d+'?\s*-\s*\d+'?$","",grade).replace('UNSEL*','').strip().replace('&',' & ')
    add(sp,IN[size],f'rough, random width & length ({g}{note})',v,LJ,'Charlotte','MI',LJU)
for z,v in [('1"','7.96'),('1-1/4"','8.17'),('2"','8.60')]: llj('Alder','ALDER',z,'Superior',v,'; red alder')
for z,v in [('1"','5.18'),('1-1/4"','5.33'),('1-1/2"','5.63'),('2"','6.51'),('2-1/2"','7.89'),('3"','8.49'),('4"','12.26')]: llj('Ash','ASH',z,'Sel&Btr',v)
for z,v in [('1"','3.05'),('1-1/4"','3.18'),('1-1/2"','3.33'),('2"','4.09'),('3"','8.21'),('4"','8.36')]: llj('Basswood','BASSWOOD',z,'Sel&Btr',v)
llj('Cherry','CHERRY','1"',"Sel&Btr 9-10'",'4.90','; 9-10 ft lengths')
for z,v in [('1-1/4"','5.25'),('1-1/2"','5.42'),('2"','5.83'),('2-1/2"','7.53'),('3"','7.63')]: llj('Cherry','CHERRY',z,'Sel&Btr',v)
llj('Hard Maple','HARD MAPLE - WHITE','1"',"Sel&Btr 9-10'",'5.68','; white; 9-10 ft lengths')
for z,v in [('1-1/4"','6.08'),('1-1/2"','6.90'),('2"','7.55'),('2-1/2"','10.97'),('3"','11.40'),('4"','13.12')]: llj('Hard Maple','HARD MAPLE - WHITE',z,'Sel&Btr',v,'; white')
for z,v in [('1"','4.41'),('1-1/4"','4.58'),('1-1/2"','4.99'),('2"','6.77')]: llj('Hickory','HICKORY',z,'Sel&Btr',v)
llj('Poplar','POPLAR LUMBER','1"',"Sel&Btr 9-10'",'3.35','; 9-10 ft lengths')
for z,v in [('1-1/4"','3.50'),('1-1/2"','3.55'),('2"','3.61'),('2-1/2"','4.26'),('3"','4.52'),('4"','4.90')]: llj('Poplar','POPLAR LUMBER',z,'Sel&Btr',v)
llj('Red Oak','RED OAK LUMBER','1"',"Sel&Btr 9'-10'",'3.81','; 9-10 ft lengths')
for z,v in [('1-1/4"','4.43'),('1-1/2"','5.05'),('2"','5.68'),('2-1/2"','9.35'),('3"','9.91')]: llj('Red Oak','RED OAK LUMBER',z,'Sel&Btr',v)
for z,v in [('1"','5.18'),('1-1/4"','5.38'),('1-1/2"','5.81'),('2"','6.45'),('2-1/2"','7.31'),('3"','8.28')]: llj('Soft Maple','SOFT MAPLE',z,'Sel&Btr UNSEL*',v,'; unselected color')
llj('Walnut','WALNUT','1"',"Sel&Btr 9' - 12'",'11.85','; 9-12 ft lengths')
for z,v in [('1-1/4"','12.17'),('1-1/2"','12.66'),('2"','13.80'),('2-1/2"','18.58'),('3"','19.78'),('4"','21.26')]: llj('Walnut','WALNUT',z,'Sel&Btr',v)
llj('White Oak','WHITE OAK','1"',"Sel&Btr 9-10'",'8.60','; 9-10 ft lengths')
for z,v in [('1-1/4"','10.43'),('1-1/2"','11.18'),('2"','13.12'),('2-1/2"','21.46'),('3”','22.64')]: llj('White Oak','WHITE OAK',z,'Sel&Btr',v)

# ---- 4. Logs to Lumber Co., Hastings MN: /domestic-pricing/ "D.H. Kiln Dried Lumber Price List" (undated). "5/5" rows (typo?) and price ranges/out-of-stock rows skipped.
LT='Logs to Lumber Co.'; LTU='https://logs-to-lumber.com/domestic-pricing/'
s=BeautifulSoup(open(R+'ltl.html',errors='replace').read(),'lxml'); lrows=[]
for tr in [tb for tb in s.find_all('table') if 'Red Oak Flatsawn' in tb.get_text()][0].find_all('tr'):
    lrows.append([x.get_text(' ',strip=True) for x in tr.find_all(['td','th'])])
cur=None; LM={'Red Oak Flatsawn':('Red Oak',''),'White Oak Flatsawn':('White Oak',''),'Walnut':('Walnut','; FAS 1F oak rules, 90/90'),'Soft Maple- white 2-face':('Soft Maple','; white 2-face'),
    'Hard Maple-white 2-face':('Hard Maple','; white 2-face'),'Cherry':('Cherry','; Sel & Btr'),'Ash':('Ash',''),'Hickory':('Hickory','')}
seen=set()
for c in lrows:
    if len(c)<3: continue
    if c[0] and not c[0].startswith(('(','90/','S&B','S$B','Wide','S4S','Heavy','Light')): cur=c[0]
    th,v=c[1],c[2]
    if cur in LM and re.fullmatch(r'\d+/4',th) and re.fullmatch(r'\$\d+\.\d\d',v):
        if cur=='Cherry' and c[0].startswith('Wide'): continue
        sp,ex=LM[cur]; seen.add(cur)
        add(sp,th,'KD (dehumidification kiln; surfacing not stated'+ex+')',v[1:],LT,'Hastings','MN',LTU)
assert seen==set(LM),set(LM)-seen

# ---- 5. Hobby Hardwood Alabama, New Market AL: price list image dated 10-24-2026 (raw/batch4/hha_oct24.jpg), read by eye.
#      Page: kiln dried, skip planed 2 sides, random width; 4/4 base price is for boards under 6" wide (+$0.50/bf at 6", again at 10"); 8/4 and 12/4: same price all widths.
HH='Hobby Hardwood Alabama'; HU='https://www.hobbyhardwoodalabama.com/price-list.html'
HS4='KD, skip planed 2 sides (base price, boards under 6" wide)'; HS8='KD, skip planed 2 sides (same price all widths)'
for sp,v in [('Alder','10.50'),('Ash','8.00'),('Basswood','8.00'),('Cherry','8.50'),('Hickory','7.00'),('Hard Maple','10.00'),('Soft Maple','10.00'),
             ('Poplar','6.00'),('Red Oak','5.75'),('Walnut','21.00'),('White Oak','14.50'),('Sapele','16.25')]:
    add(sp,'4/4',HS4[:-1]+('; walnut "Superior" grade' if sp=='Walnut' else '')+('; listed as "Maple Rock"' if sp=='Hard Maple' else '')+')',v,HH,'New Market','AL',HU)
for sp,v in [('Ash','12.50'),('Basswood','7.25'),('Cherry','10.25'),('Hard Maple','11.75'),('Soft Maple','10.50'),('Poplar','6.75'),('Red Oak','8.00'),
             ('Walnut','21.00'),('White Oak','14.00'),('Sapele','14.00')]:
    add(sp,'8/4',HS8[:-1]+('; walnut "Superior" grade' if sp=='Walnut' else '')+')',v,HH,'New Market','AL',HU)
for sp,v in [('Basswood','8.25'),('Poplar','7.25')]: add(sp,'12/4',HS8,v,HH,'New Market','AL',HU)

# ---- 6. Groff & Groff Lumber, Quarryville PA: printable price list PDF "AS OF 06/04/26". "Priced in the rough"; FAS rows (Superior for alder; basswood grade not stated).
GG='Groff & Groff Lumber'; GU='https://www.groffslumber.com/_files/ugd/77fc40_49be9bd23fc041ef8cd5d6954a3b5fd6.pdf'
gt=pdf('groff.pdf'); assert 'AS OF 06/04/26' in gt and 'Priced in the rough' in re.sub(r'\s+',' ',gt)
gsec={}; cur=None
for line in gt.split('\n'):
    m=re.match(r'^\s{5,}([A-Z][A-Za-z ()\-/]+?)(\s{2,}\(.*)?$',line)
    if m and '$' not in m.group(1) and not line.strip().startswith(('NAME','DOMESTIC','EXOTIC','Groff','858','Quarryville','Phone','Fax','sales@')): cur=m.group(1).strip(); gsec.setdefault(cur,[]); continue
    if cur: gsec[cur].append(re.sub(r'\s{2,}','  ',line.strip()))
def groff(sp,sec,th,grade,v,note=''):
    want=(th+'  '+grade+'  $'+v) if grade else (th+'  $'+v)
    assert want in gsec[sec],(sec,want,gsec.get(sec))
    add(sp,th,f'rough ({grade or "grade not stated"}{note})',v,GG,'Quarryville','PA',GU)
for th,v in [('4/4','6.50'),('6/4','7.25')]: groff('Alder','Alder',th,'Superior',v)
for th,v in [('4/4','6.25'),('8/4','7.25'),('12/4','8.75'),('16/4','11.25')]: groff('Ash','Ash',th,'FAS',v)
assert '5/4 and 6/4  FAS  $6.75' in gsec['Ash']
for th in ['5/4','6/4']: add('Ash',th,'rough (FAS)','6.75',GG,'Quarryville','PA',GU)
for th,v in [('4/4','5.00'),('8/4','5.50'),('12/4','6.25'),('16/4','8.00')]: groff('Basswood','Basswood',th,'',v)
for th,v in [('4/4','5.00'),('5/4','5.25'),('6/4','5.75'),('8/4','6.25'),('10/4','8.25'),('12/4','8.75'),('16/4','10.75')]: groff('Cherry','Cherry',th,'FAS',v)
for th,v in [('4/4','5.50'),('5/4','6.50'),('8/4','8.00')]: groff('Hickory','Hickory',th,'FAS',v)
for th,v in [('4/4','7.00'),('5/4','7.25'),('8/4','8.25'),('12/4','9.75')]: groff('Hard Maple','Maple (Hard)',th,'FAS',v)
for th,v in [('4/4','6.50'),('5/4','6.75'),('6/4','7.25'),('8/4','7.75'),('12/4','8.75')]: groff('Soft Maple','Maple (Soft)',th,'FAS',v)
for th,v in [('4/4','4.30'),('5/4','4.55'),('6/4','5.05'),('8/4','5.80'),('10/4','8.50'),('12/4','9.30')]: groff('Red Oak','Oak (Red Oak)',th,'FAS',v)
for th,v in [('4/4','10.25'),('5/4','10.50'),('6/4','11.50'),('8/4','13.75'),('10/4','16.25'),('12/4','17.25')]: groff('White Oak','Oak (White Oak)',th,'FAS',v)
for th,v in [('4/4','3.50'),('5/4','3.80'),('6/4','4.20'),('8/4','4.30'),('10/4','5.50'),('12/4','6.10')]: groff('Poplar','Poplar' if th in ('4/4','5/4','6/4') else 'Poplar (continued)',th,'FAS',v)
for th,v in [('4/4','10.00'),('5/4','10.25'),('6/4','12.75'),('8/4','13.50'),('10/4','15.75')]: groff('Walnut','Walnut',th,'FAS',v)
for th,v in [('4/4','9.00'),('5/4','9.25'),('6/4','9.50'),('8/4','9.75'),('10/4','10.00'),('12/4','10.75'),('16/4','11.75')]: groff('Mahogany','African Mahogany',th,'',v,'; African mahogany')
for th,v in [('4/4','8.00'),('5/4','8.25'),('6/4','8.50'),('8/4','8.75'),('10/4','9.00'),('12/4','9.75'),('16/4','10.75')]: groff('Sapele','Sapele',th,'',v)
# alder 5/4 and 8/4 are posted as "Rustic / Superior": use the Superior figure
for th,v in [('5/4','6.75'),('8/4','7.75')]:
    assert any(l.startswith(th+'  Rustic / Superior') and l.endswith('/ $'+v) for l in gsec['Alder']); add('Alder',th,'rough (Superior)',v,GG,'Quarryville','PA',GU)

# ---- 7. Irion Lumber Company, Wellsboro PA: price-list JPEGs (page 1 dated 10/6/26; page 2 file "April-Price-List-Page-2", undated on the page), read by eye.
#      Plain (not figured) stock, narrowest width band (4-9" or 5-9"); surfacing not stated. Mahogany (type not stated), 10/4+ walnut (ambiguous rows) and "plain maple" skipped.
IR='Irion Lumber Company'; IRU='https://irionlumber.com/price-list/'
for th,v in [('4/4','5.00'),('5/4','5.50'),('6/4','6.00'),('8/4','6.50'),('10/4','9.00'),('12/4','9.50'),('16/4','10.50')]:
    add('Cherry',th,'plain'+(', 4-9" wide' if th in ('4/4','5/4','6/4','8/4') else '')+' (surfacing not stated; list dated 10/6/26)',v,IR,'Wellsboro','PA',IRU)
for th,v in [('4/4','6.00'),('5/4','6.50'),('8/4','7.00'),('12/4','8.00'),('16/4','10.00')]:
    add('Hard Maple',th,'plain'+(', 5-9" wide' if th in ('4/4','5/4','8/4') else '')+' (surfacing not stated; list dated 10/6/26)',v,IR,'Wellsboro','PA',IRU)
for th,v in [('4/4','11.75'),('5/4','12.25'),('6/4','12.75'),('8/4','12.75')]: add('Walnut',th,'plain, 4-9" wide (surfacing not stated; April 2026 list page)',v,IR,'Wellsboro','PA',IRU)
for th,v in [('5/4','9.50'),('8/4','10.50'),('10/4','13.50')]: add('White Oak',th,'plain'+(', 5-9" wide' if th!='10/4' else '')+' (surfacing not stated; April 2026 list page)',v,IR,'Wellsboro','PA',IRU)
for th,v in [('4/4','5.00'),('5/4','5.50'),('8/4','5.50')]: add('Ash',th,'5-9" wide (surfacing not stated; April 2026 list page)',v,IR,'Wellsboro','PA',IRU)

# ---- 8. Hoosier Hardwood Supply, Fort Wayne IN: "Hardwood Lumber Price List" + "Exotic Lumber" PDFs (Google Drive links on /material-guide-pricing; PDF created 2026-09-04),
#      1-99 BF column. Page: most material is hit/miss planed (4/4 to 15/16"), priced by BF for random width graded material. SLRIE = straight-line ripped one edge.
#      13/16" sanded rows skipped; 4/4 white oak is listed twice ($9.15 and $7.87) so it is skipped.
HO='Hoosier Hardwood Supply'; HOU='https://www.hoosierhardwoodsupply.com/material-guide-pricing'
ht=pdf('hoosier_hw.pdf'); et=pdf('hoosier_ex.pdf')
def hoos(sp,th,item,v,txt=ht,su='hit/miss planed, SLR1E'):
    assert re.search(r'^\s*'+re.escape(th)+r'\s+'+re.escape(item)+r'\s+\$\s+'+re.escape(v)+r'\b',txt,re.M),(th,item,v)
    add(sp,th,f'{su} ({re.sub(r"^SB ","S&B ",item.replace(" SLRIE",""))})',v,HO,'Fort Wayne','IN',HOU)
for th,v in [('4/4','3.65'),('5/4','3.80'),('6/4','4.05'),('8/4','4.12')]: hoos('Poplar',th,'S&B Poplar SLRIE',v)
hoos('Red Oak','4/4','SB Red Oak SLRIE','3.99'); hoos('Red Oak','5/4','S&B Red Oak SLRIE','4.19'); hoos('Red Oak','8/4','S&B Red Oak SLRIE','5.40')
for th,v in [('4/4','5.35'),('5/4','5.58'),('6/4','6.05'),('8/4','6.19')]: hoos('Hard Maple',th,'S&B W. Hard Maple SLRIE',v)
for th,v in [('4/4','5.65'),('5/4','5.80'),('8/4','6.15')]: hoos('Cherry',th,'S&B Red Cherry SLRIE',v)
for th,v in [('6/4','10.85'),('8/4','11.67')]: hoos('White Oak',th,'S&B W. Oak SLRIE',v)
for th,v in [('4/4','9.49'),('6/4','12.15'),('8/4','13.60')]: hoos('Walnut',th,'S&B Walnut SLRIE',v)
hoos('Hickory','4/4','S&B Hickory SLRIE','5.20'); hoos('Hickory','5/4','S&B Hickory SLRIE','4.82')
hoos('Ash','4/4','S&B Ash SLRIE','4.78'); hoos('Alder','4/4','Cabinet Alder SLRIE','4.55')
hoos('Mahogany','4/4','African Mahogany','8.79',et,'grade and surfacing not stated'); hoos('Sapele','4/4','Sapele','8.75',et,'grade and surfacing not stated')
assert len(re.findall(r'^\s*4/4\s+S&B W\. Oak SLRIE',ht,re.M))==2

# ---- write seed.csv (append, CRLF, existing bytes untouched) ----
NEW={BD,BF,LJ,LT,HH,GG,IR,HO}
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if not any((','+d+',') in l or (',"'+d+'",') in l for d in NEW)]
if not lines[-1].endswith('\n'): lines[-1]+='\r\n'
buf=io.StringIO(); csv.DictWriter(buf,fieldnames=cols,lineterminator='\r\n').writerows(rows)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
# ---- dealers.csv ----
dcols=list(csv.DictReader(open('dealers.csv')).fieldnames); dl=[d for d in csv.DictReader(open('dealers.csv')) if d['dealer'] not in NEW]
dl+= [
 dict(dealer=BD,city='Walworth',state='WI',ships='Yes (area not stated)',shipping_note="Home page says it offers 'mail order hardwoods and retail hardwoods'; the price page says 'Call for a Shipping Quote!!'. Prices are S2S, random widths and lengths (rough is $0.26/bf less; special sizes and straight-line ripping $0.26/bf extra)",shipping_source_url=BU,date_checked=TODAY,affiliate=''),
 dict(dealer=BF,city='Ishpeming',state='MI',ships='Yes (FedEx or LTL freight, area not stated)',shipping_note="Shipping policy: smaller orders ship FedEx; larger orders ship LTL freight on pallets with common carriers. Prices shown here are the under-10 BF column; the price list has lower 10-99 and 100-499 BF tiers",shipping_source_url='https://www.bellforestproducts.com/info/shipping-policy/',date_checked=TODAY,affiliate=''),
 dict(dealer=LJ,city='Charlotte',state='MI',ships='Yes (LTL anywhere in the US)',shipping_note="Delivery page: own trucks on set days in its delivery zones, and 'We also deliver LTL ... anywhere in the U.S.'; pickup at Charlotte, MI usually ready in 2 hours. Retail store also in South Bend, IN. Prices shown are the 1+ BF column (100+, 500+ and 1000+ BF tiers are lower)",shipping_source_url='https://lljlumber.com/delivery/',date_checked=TODAY,affiliate=''),
 dict(dealer=LT,city='Hastings',state='MN',ships='Yes (lower 48, quote by phone/email)',shipping_note="Shipping page: 'We do not ship outside the USA lower 48 states'; shipping is quoted per order by size and weight and is not free. Price page says to contact them about shipping or local pickup (the website doesn't take payment)",shipping_source_url='https://logs-to-lumber.com/shipping-returns/',date_checked=TODAY,affiliate=''),
 dict(dealer=HH,city='New Market',state='AL',ships='Not stated',shipping_note="No shipping policy found; small yard open for walk-in retail Fri and Sat 9-4, weekdays by appointment. Lumber is kiln dried, skip planed two sides, random width; 4/4 prices are for boards under 6\" wide (+$0.50/bf at 6\" and again at 10\")",shipping_source_url=HU,date_checked=TODAY,affiliate=''),
 dict(dealer=GG,city='Quarryville',state='PA',ships='Not stated',shipping_note="Price list says 'Prices do not include shipping'; no shipping policy or area found. Prices are in the rough (S2S adds $0.40/bf); boards 10\" and wider add $1.00/bf",shipping_source_url=GU,date_checked=TODAY,affiliate=''),
 dict(dealer=IR,city='Wellsboro',state='PA',ships='Yes (common carrier, area not stated)',shipping_note="Shipping policy: 'All orders are shipped via Common Carrier, unless there is a FedEx Ground option listed on the website'; customer unloads. Price list is priced by width band (wider boards cost more)",shipping_source_url='https://irionlumber.com/shipping/',date_checked=TODAY,affiliate=''),
 dict(dealer=HO,city='Fort Wayne',state='IN',ships='Not stated',shipping_note="No shipping policy found; store open to the public Mon-Fri 8-4:30, Sat 8-12, and will cut boards down for transport at no charge. Prices shown are the 1-99 BF column (100 BF column is lower; 300+ BF gets a custom quote)",shipping_source_url=HOU,date_checked=TODAY,affiliate='')]
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n'); w.writeheader(); w.writerows(dl)
import collections
print(collections.Counter(r['dealer'] for r in rows)); print(len(rows),'rows added')
print(collections.Counter(r['species'] for r in rows if r['species'] in ('Basswood','Alder')))
