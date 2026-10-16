# Baird Brothers Sawmill, Canfield OH: per-board-foot rough sawn list prices from product pages (checked 2026-10-16)
import csv,re,glob,subprocess,os
from bs4 import BeautifulSoup
B='https://www.bairdbrothers.com/'
UA='Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0'
keep={'Walnut':'Walnut','Cherry':'Cherry','Hard Maple':'Hard Maple','White Oak':'White Oak','Red Oak':'Red Oak','Ash':'Ash','Hickory':'Hickory','Poplar':'Poplar','Plain Sapele':'Sapele','African Mahogany':'Mahogany'}
cats={'Walnut':'bb_walnut.html','Cherry':'bbc_Cherry-C6393.html','Hard Maple':'bbc_Hard-Maple-C6392.html','White Oak':'bbc_White-Oak-C6397.html','Red Oak':'bbc_Red-Oak-C6391.html','Ash':'bbc_Ash-C6395.html','Hickory':'bbc_Hickory-C6394.html','Poplar':'bbc_Poplar-C6390.html','Plain Sapele':'bbc_Plain-Sapele-C6416.html','African Mahogany':'bbc_African-Mahogany-C6402.html'}
rows=[]
for cat,f in cats.items():
  s=BeautifulSoup(open('raw/'+f).read(),'html.parser')
  links=[]
  for a in s.find_all('a',href=True):
    if re.search(r'-P\d+\.aspx$',a['href']) and a['href'] not in links: links.append(a['href'])
  for h in links:
    fn='raw/bbp_'+os.path.basename(h)+'.html'
    if not os.path.exists(fn): subprocess.run(['curl','-sL','--compressed','-m','30','-A',UA,B+h.lstrip('/'),'-o',fn],check=True)
    x=BeautifulSoup(open(fn).read(),'html.parser').get_text(' ',strip=True)
    th=re.search(r'Code: (\d+/4)-',x).group(1)
    price=re.search(r'Price: \$([\d.]+)',x).group(1)
    length=re.search(r'Length (.*?) Status',x).group(1)
    status=re.search(r'Status (.*?) Grade',x).group(1)
    grade=re.search(r'Grade (.*?) Width',x).group(1)
    assert 'Rough Sawn' in x and status=='Kiln Dried',(h,status)
    first_len=length.split()[0]
    print(cat,th,price,'|',length,'|',status,'|',grade)
    rows.append([keep[cat],th,f'rough (KD, {grade}, {first_len})',price,'Baird Brothers Sawmill','Canfield','OH',B+h.lstrip('/'),'2026-10-16'])
old=list(csv.reader(open('seed.csv')));exist={tuple(r) for r in old[1:]}
new=[r for r in rows if tuple(r) not in exist]
with open('seed.csv','w',newline='') as f:
  w=csv.writer(f);w.writerows(old+new)
print(len(new),'added; total',len(old)-1+len(new))
