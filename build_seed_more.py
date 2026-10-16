# Appends real, publicly posted dealer prices parsed from saved source pages in raw/ (checked 2026-10-16).
import csv,re,html,sys
from bs4 import BeautifulSoup
D='2026-10-16'
R='raw/'
out=[]
def add(sp,th,surf,p,dealer,city,st,url): out.append([sp,th,surf,f"{float(p):.2f}",dealer,city,st,url,D])
money=lambda s: re.sub(r'[^0-9.]','',s)

# --- Hearne Hardwoods, Oxford PA (rough sawn per price-list page): FAS, plain, flat sawn, 4-8.5" wide
for f,sp,url in [('hearne_walnut.html','Walnut','https://www.hearnehardwoods.com/walnut-black-lumber-pricing/'),('hearne_maple.html','Hard Maple','https://www.hearnehardwoods.com/maple-hard-lumber-pricing/')]:
  s=BeautifulSoup(open(R+f).read(),'html.parser')
  for r in s.find('table').find_all('tr')[1:]:
    c=[x.get_text(' ',strip=True) for x in r.find_all('td')]
    if c[1]=='FAS' and c[2]=='None' and c[3].startswith('0') and c[4]=='Flat Sawn' and c[6].startswith('4.00'):
      add(sp,c[0],'rough',money(c[5]),'Hearne Hardwoods (FAS grade)','Oxford','PA',url)

# --- KenCraft Company, Toledo OH: 4/4..8/4 columns located by character position in the PDF layout
U='https://www.kencraftcompany.com/wp-content/uploads/2026/01/KenCraft_Price-List-1-3-2026-1.pdf'
cols=[(40,46,'4/4'),(52,57,'5/4'),(62,68,'6/4'),(75,80,'8/4')]
names={'ASH':'Ash','CHERRY':'Cherry','HICKORY':'Hickory','MAPLE HARD':'Hard Maple','MAPLE SOFT':'Soft Maple','MAHOGANY SAPELE':'Sapele','OAK - RED':'Red Oak','OAK - WHITE':'White Oak','POPLAR':'Poplar','WALNUT**':'Walnut'}
for l in open(R+'ken.txt').read().split('\n'):
  for k,sp in names.items():
    if l.startswith(k+' ') or l.startswith(k):
      if k=='ASH' and not l.startswith('ASH '):continue
      for m in re.finditer(r'(\d+\.\d\d)',l[:90]):
        for a,b,t in cols:
          if a<=m.start()<=b: add(sp,t,'not stated',m.group(1),'KenCraft Company','Toledo','OH',U)
      break

# --- The Wood Yard, Concord GA (base in-store prices, Oct 2026)
U='https://www.thewoodyard.com/current-pricing-list/'
wy={'Ash':[('4/4','6.10'),('6/4','7.25'),('8/4','7.95')],'Cherry':[('4/4','6.75'),('8/4','8.70')],'Hickory':[('4/4','6.00'),('8/4','9.75')],
'Hard Maple':[('4/4','8.35'),('8/4','9.20')],'Soft Maple':[('4/4','8.25'),('6/4','8.60'),('8/4','9.00')],
'Red Oak':[('4/4','6.10'),('6/4','6.60'),('8/4','7.45')],'White Oak':[('4/4','10.00'),('8/4','15.00')],
'Poplar':[('4/4','5.35'),('6/4','5.80'),('8/4','5.70')],'Walnut':[('4/4','16.50'),('8/4','17.00')],'Mahogany':[('4/4','7.50'),('8/4','15.25')]}
txt=re.sub(r'\s+',' ',open(R+'wy2.txt').read())
# verify each value really appears on the page text before accepting
for sp,l in wy.items():
  for t,p in l:
    assert f'${p}' in txt,(sp,t,p)
    add(sp,t,'not stated',p,'The Wood Yard','Concord','GA',U)

# --- Detwiler Hardwood Lumber, Indianapolis IN (effective 2026-07-01; 4/4 & 8/4 are surfaced, one straight edge)
U='https://detwilerhardwoodlumber.com/'
lines=[l.strip() for l in open(R+'detwiler.txt') if l.strip()]
dn={'Ash':'Ash','Cherry':'Cherry','Hard Maple':'Hard Maple','Hickory':'Hickory','Poplar':'Poplar','Red Oak':'Red Oak','Soft Maple':'Soft Maple','Walnut':'Walnut','White Oak (Plain Sawn)':'White Oak'}
for i,l in enumerate(lines):
  nm=re.sub(r'\s*ⓘ\s*$','',l)
  if nm in dn and re.match(r'\$[\d.]+$|—',lines[i+1]):
    for t,v in zip(['4/4','8/4'],[lines[i+1],lines[i+2]]):
      if v.startswith('$'): add(dn[nm],t,'surfaced (S2S, 1 straight edge)',money(v),'Detwiler Hardwood Lumber','Indianapolis','IN',U)

# --- Berkshire Products, Sheffield MA (prices as of June 2026); 4/4 and 5/4 columns, rows align with species list
U='https://berkshireproducts.com/lumber-prices/'
s=BeautifulSoup(open(R+'berk.html').read(),'html.parser');tb=s.find_all('table')
sp_rows=[r.find_all('td')[0].get_text(' ',strip=True) for r in tb[0].find_all('tr')[1:]]
pr_rows=[[c.get_text(' ',strip=True) for c in r.find_all('td')] for r in tb[1].find_all('tr')[1:]]
assert len(sp_rows)==len(pr_rows)==21,(len(sp_rows),len(pr_rows))
bm={'Ash':'Ash','Cherry':'Cherry','Hickory':'Hickory','Maple, Hard':'Hard Maple','Maple, Soft':'Soft Maple','Oak, Red':'Red Oak','Oak, White':'White Oak','Tulip(Yellow Poplar)':'Poplar','Walnut':'Walnut'}
for n,p in zip(sp_rows,pr_rows):
  if n in bm:
    for t,v in zip(['4/4','5/4'],p[:2]):
      if v.startswith('$'): add(bm[n],t,'not stated',money(v),'Berkshire Products','Sheffield','MA',U)

# --- Cygnus Lumber, Pungo / Virginia Beach VA
U='https://cygnuslumber.com/current-pricing/'
cy={'Cherry':[('4/4','4.25'),('5/4','4.50'),('8/4','5.00')],'Hickory':[('4/4','3.50'),('5/4','3.75')],'Soft Maple':[('4/4','4.75'),('8/4','6.50')],'Hard Maple':[('4/4','4.75'),('5/4','5.25'),('8/4','6.00')],
'White Oak':[('4/4','7.25'),('5/4','8.25'),('8/4','10.00')],'Red Oak':[('4/4','3.50'),('5/4','3.75'),('8/4','4.50')],'Poplar':[('4/4','3.00'),('5/4','3.25'),('8/4','3.75')],
'Walnut':[('5/4','10.50'),('8/4','10.75')],'Sapele':[('4/4','7.50'),('5/4','7.75')]}
ct=re.sub(r'\s+',' ',open(R+'cygnus.txt').read())
chk={'Cherry':'Cherry - Premium FAS','Hickory':'Hickory - -','Soft Maple':'Maple Soft Premium FAS','Hard Maple':'Maple Hard Premium FAS','White Oak':'White Oak White Premium FAS','Red Oak':'Red Oak Red Premium FAS','Poplar':'Poplar - Premium FAS','Walnut':'Walnut - FAS','Sapele':'Sapele Flat Sawn -'}
for sp,l in cy.items():
  for t,p in l:
    assert re.search(re.escape(chk[sp])+r' '+re.escape(t)+r' \$'+re.escape(p)+r'\b',ct),(sp,t,p)
    add(sp,t,'not stated',p,'Cygnus Lumber','Virginia Beach','VA',U)

# --- C.P. Johnson Lumber, Elkwood VA (price list dated 2026-10-06 in filename); standard-width rows only
U='https://cpjohnsonlumber.com/wp-content/uploads/2026/10/CP-Johnson-Lumber-Price-List-100626.pdf'
cp={'Ash':[('4/4','5.25'),('5/4','5.50'),('6/4','5.65'),('8/4','5.75')],'Cherry':[('4/4','5.00'),('5/4','5.35'),('6/4','5.50'),('8/4','6.25')],
'Hard Maple':[('5/4','5.35'),('6/4','5.65'),('8/4','5.95')],'Soft Maple':[('4/4','4.95'),('5/4','4.95'),('6/4','5.10'),('8/4','5.35')],
'Poplar':[('4/4','3.25'),('5/4','3.35'),('6/4','3.45'),('8/4','3.50')],'Walnut':[('8/4','13.25')],'White Oak':[('5/4','7.25'),('6/4','8.95'),('8/4','11.50')]}
pt=re.sub(r'\s+',' ',open(R+'cpj.txt').read())
for sp,l in cp.items():
  for t,p in l:
    assert f'${p}' in pt,(sp,t,p)
    add(sp,t,'not stated',p,'C.P. Johnson Lumber','Elkwood','VA',U)

# --- The Hardwood Store of North Carolina, Gibsonville NC (rough; 1-99 BF tier)
U='https://hardwoodstore.com/domestic-lumber/'
s=BeautifulSoup(open(R+'hsnc.html').read(),'html.parser')
hm={'Ash':'Ash','Cherry':'Cherry','Hickory':'Hickory','Maple, Hard (Sugar)':'Hard Maple','Maple, Soft (Red)':'Soft Maple','Poplar':'Poplar','Oak, White':'White Oak','Oak, Red':'Red Oak','Walnut':'Walnut'}
for t in s.find_all('table'):
  h=t.find_all_previous(['h1','h2','h3','h4'],limit=1)
  if not h:continue
  n=h[0].get_text(' ',strip=True)
  if n not in hm:continue
  for r in t.find_all('tr')[1:2]:   # first data row holds the whole 5-wide flattened row set
    c=[x.get_text(' ',strip=True) for x in r.find_all('td')]
    i=0
    while i+4<len(c)+0 and i<len(c):
      th=c[i]
      m=re.match(r'^(\d+/4)\s*(\(.*\))?$',th)
      if m and c[i+1].startswith('$') and (not m.group(2) or re.fullmatch(r'\(\d[\d /]*"\)',m.group(2))):
        add(hm[n],m.group(1),'rough',money(c[i+1]),'The Hardwood Store of NC','Gibsonville','NC',U)
      i+=5
# --- Wolverine Hardwoods, Allegan MI (September 2026 retail list; prepared 9/15/2026)
U='https://wolverinehardwoods.com/wp-content/uploads/2026/09/September-2026-Prices-Retail.pdf'
wv={'ASH':'Ash','CHERRYRED':'Cherry','HARD MAPLE':'Hard Maple','HICKORY':'Hickory','POPLAR':'Poplar','RED OAK':'Red Oak','WHITE OAK':'White Oak','WALNUT':'Walnut'}
seen=set()
for l in open(R+'wolv.txt'):
  m=re.match(r'^(ASH|CHERRYRED|HARD MAPLE|HICKORY|POPLAR|RED OAK|WHITE OAK|WALNUT)\s{2,}(.*?)\s+(\d/4)\s+(FB|SBB)\s+\$\s+([\d.]+)\s*$',l)
  if m:
    sp=wv[m.group(1)];note=m.group(2).strip()
    if note not in ('','RL','90/70 RED','1+2 WHITE','') : continue
    key=(sp,m.group(3))
    if key in seen: continue
    seen.add(key); add(sp,m.group(3),'not stated',m.group(5),'Wolverine Hardwoods','Allegan','MI',U)
for sp,t,p in [('Sapele','4/4','9.00'),('Mahogany','4/4','9.50'),('Mahogany','5/4','10.00'),('Mahogany','8/4','11.00')]:
  assert re.search(r'\s'+t+r'\s+FB\s+\$\s+'+re.escape(p)+r'\s',open(R+'wolv.txt').read())
  add(sp,t,'not stated',p,'Wolverine Hardwoods','Allegan','MI',U)

# --- Odd Wood Lumber, Port Richey FL (posted per-BF prices on lumber page)
U='https://www.owlumber.com/lumber'
ow=BeautifulSoup(open(R+'ow.html').read(),'html.parser').get_text('\n',strip=True)
for sp,label,th in [('Walnut','4/4 Walnut','4/4'),('Walnut','5/4 Walnut','5/4'),('White Oak','4/4 White Oak','4/4'),('Hard Maple','4/4 Hard Maple','4/4'),('Ash','4/4 Ash','4/4'),('Ash','8/4 Ash','8/4'),('Cherry','4/4 Cherry','4/4'),('Hickory','4/4 Hickory','4/4'),('Sapele','4/4 Sapele (QTR Sawn)','4/4'),('Sapele','6/4 Sapele (QTR Sawn)','6/4'),('Sapele','8/4 Sapele (QTR Sawn)','8/4')]:
  m=re.search(re.escape(label)+r'\n\$([\d.]+)/BF',ow); assert m,label
  add(sp,th,'not stated',m.group(1),'Odd Wood Lumber','Port Richey','FL',U)

old=list(csv.reader(open('seed.csv')))
hdr,rows=old[0],old[1:]
exist={tuple(r) for r in rows}
new=[r for r in out if tuple(r) not in exist]
with open('seed.csv','w',newline='') as f:
  w=csv.writer(f);w.writerow(hdr);w.writerows(rows+new)
print(len(rows),'+',len(new),'=',len(rows)+len(new))
from collections import Counter
print(Counter((r[6],r[4]) for r in new))
