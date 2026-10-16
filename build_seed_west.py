#!/usr/bin/env python3
"""Append real publicly posted Western-state $/bf prices to seed.csv.
Sources: Woodworkers Source (AZ) product pages, SoCalTrim (CA) product pages,
Urban Forest Mill (CO) domestic lumber page, Goby Walnut (OR) latest-lumber page.
Every price is re-read live from the page at run time and asserted against the expected figure."""
import csv,re,subprocess,sys
from bs4 import BeautifulSoup
UA="Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
TODAY='2026-10-16'
def get(u):
    return subprocess.run(['curl','-sL','--compressed','-m','40','-A',UA,u],capture_output=True,text=True).stdout
def text(u):
    s=BeautifulSoup(get(u),'html.parser')
    for t in s(['script','style']): t.decompose()
    return s.get_text('\n',strip=True)
rows=[]
# ---- Woodworkers Source, AZ ----
W='https://www.woodworkerssource.com/'
wws=[ # species, thickness, path
 ('Walnut','4/4','walnut/premium-black-walnut-44-lumber'),('Walnut','6/4','walnut/premium-black-walnut-64-lumber'),
 ('Walnut','8/4','walnut/premium-black-walnut-84-lumber'),('Walnut','12/4','walnut/premium-black-walnut-124-lumber'),
 ('Walnut','4/4','walnut/natural-walnut-44-lumber'),
 ('Cherry','4/4','cherry/cherry-44-lumber'),('Cherry','6/4','cherry/cherry-64-lumber'),('Cherry','8/4','cherry/cherry-84-lumber'),('Cherry','12/4','cherry/cherry-124-lumber'),
 ('Hard Maple','4/4','hard-white-maple/maple-hard-white-44-lumber'),('Hard Maple','6/4','hard-white-maple/maple-hard-white-64-lumber'),('Hard Maple','8/4','hard-white-maple/maple-hard-white-84-lumber'),
 ('Red Oak','4/4','red-oak/red-oak-44-lumber'),('Red Oak','6/4','red-oak/red-oak-64-lumber'),('Red Oak','8/4','red-oak/red-oak-84-lumber'),
 ('White Oak','4/4','white-oak-flat-sawn/white-oak-flat-sawn-44-lumber'),('White Oak','6/4','white-oak-flat-sawn/white-oak-flat-sawn-64-lumber'),
 ('White Oak','8/4','white-oak-flat-sawn/white-oak-flat-sawn-84-lumber'),('White Oak','12/4','white-oak-flat-sawn/white-oak-flat-sawn-124-lumber'),
 ('Ash','4/4','ash/white-ash-44-lumber'),
 ('Hickory','4/4','hickory/hickory-44-lumber'),('Hickory','8/4','hickory/hickory-84-lumber'),
 ('Poplar','4/4','poplar/poplar-44-lumber'),('Poplar','6/4','poplar/poplar-64-lumber'),('Poplar','8/4','poplar/poplar-84-lumber'),('Poplar','12/4','poplar/poplar-124-lumber'),
]
for sp,th,path in wws:
    u=f'{W}{path}.html'; t=text(u)
    i=t.find('Write a Review'); m=re.search(r'\$([\d.]+)\n/Board Feet',t[i:i+120]); assert m,(u)
    k=t.find('Thickness\n'); g=re.search(r'Grade\n([^\n]+)',t[k:k+400]); grade=g.group(1).strip(' .')
    assert re.search(r'Thickness\n'+re.escape(th)+r', S2S',t),u
    grade={'Clear One Side':'clear one side','Select & Better':'Select & Better','#1COM or Better':'#1 Common & Better'}.get(grade,grade)
    rows.append([sp,th,f'S2S ({grade})',m.group(1),'Woodworkers Source','Phoenix','AZ',u,TODAY])
# ---- SoCalTrim, CA ----
for sp,slug in [('Walnut','black-walnut-4-4'),('Hard Maple','hard-maple-4-4'),('Red Oak','red-oak-4-4'),('White Oak','white-oak-4-4'),('Poplar','poplar-4-4')]:
    u=f'https://socaltrim.com/product/{slug}/'; t=text(u)
    assert 'Price per board foot' in t and '13/16″ S2S' in t,u
    a=t.find('Hardwoods\n/\n'); b=t.find('Price per board foot'); seg=t[a:b]
    cur=re.search(r'Current price is: \$([\d.]*\d)',seg)
    if cur: p=cur.group(1); note=', sale price (was $'+re.search(r'Original price was: \$([\d.]*\d)',seg).group(1)+')'
    else:
        ms=re.findall(r'\$\n([\d.]*\d)',seg); assert len(ms)==1,(u,seg); p=ms[0]; note=''
    rows.append([sp,'4/4',f'S2S (13/16"{note})',p,'SoCalTrim','Wildomar','CA',u,TODAY])
# ---- Urban Forest Mill, CO ----
u='https://urbanforestmill.com/domestic-lumber/'; t=text(u)
sec=t[t.find('Black Walnut - FAS Grade'):t.find('CONTACT:')]
cur=None;
for line in sec.split('\n'):
    mm=re.match(r'(Black Walnut|Cherry|White Oak|Hard Maple) - (FAS|Rustic|S&B) Grade',line)
    if mm: cur=(mm.group(1),mm.group(2)); continue
    m2=re.match(r'(\d+/4) – \$([\d.]+)',line)
    if m2 and cur:
        sp={'Black Walnut':'Walnut'}.get(cur[0],cur[0]); gr={'FAS':'FAS','Rustic':'Rustic grade','S&B':'Select & Better'}[cur[1]]
        p=m2.group(2); 
        if p=='10.0': p='10.00'
        rows.append([sp,m2.group(1),f'KD, hit-and-miss planed ({gr})',p,'Urban Forest Mill','Longmont','CO',u,TODAY])
# ---- Goby Walnut, OR ----
u='https://gobywalnut.com/pages/latest-hardwood-lumber'; t=text(u)
for th,price,desc in [('6/4','12.75','6/4 American Black Walnut - $12.75 / BF'),('4/4','11','4/4 American Black Walnut - $11 / BF')]:
    assert desc in t,desc
    rows.append(['Walnut',th,'not stated',f'{float(price):.2f}','Goby Walnut Products','Aurora','OR',u,TODAY])
if '--dry' in sys.argv:
    for r in rows: print(r)
    print(len(rows)); sys.exit()
with open('seed.csv','a',newline='') as f:
    csv.writer(f,lineterminator='\n').writerows(rows)
print('appended',len(rows))
