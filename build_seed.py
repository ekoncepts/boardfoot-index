import csv
D='2026-10-16'
rows=[]
wv={'Walnut':[('4/4','11.80','S2S'),('8/4','13.30','not stated')],
'Cherry':[('4/4','7.25','not stated'),('5/4','7.30','not stated'),('6/4','7.40','not stated'),('8/4','7.60','not stated')],
'Hard Maple':[('4/4','8.80',''),('5/4','8.65',''),('6/4','8.85',''),('8/4','9.00','')],
'White Oak':[('4/4','9.25',''),('5/4','10.20',''),('6/4','10.50',''),('8/4','12.85','')],
'Red Oak':[('4/4','7.20',''),('5/4','7.45',''),('6/4','7.70',''),('8/4','7.95','')],
'Ash':[('4/4','7.25',''),('5/4','7.50',''),('6/4','7.75',''),('8/4','7.85','')],
'Hickory':[('4/4','8.00',''),('5/4','8.75',''),('8/4','9.50','')],
'Soft Maple':[('4/4','6.80',''),('5/4','7.35',''),('6/4','7.20',''),('8/4','7.60','')],
'Sapele':[('4/4','10.50',''),('5/4','10.50',''),('6/4','10.80',''),('8/4','10.65','')],
'Mahogany':[('4/4','14.75',''),('6/4','14.85',''),('8/4','14.75','')]}
slug={'Hard Maple':'hard-maple','White Oak':'white-oak','Red Oak':'red-oak','Soft Maple':'soft-maple'}
for s,l in wv.items():
  for t,p,f in l: rows.append([s,t,f or 'not stated',p,'Wood Vendors (100-249 BF tier)','Vancouver','WA',f'https://woodvendors.com/{slug.get(s,s.lower())}-lumber/',D])
ho=[('Ash','4/4','4.50'),('Cherry','4/4','4.25'),('Cherry','8/4','5.25'),('Hickory','4/4','4.00'),('Hickory','8/4','6.00'),('Hard Maple','4/4','5.50'),('Hard Maple','6/4','6.50'),('Hard Maple','8/4','7.25'),('Soft Maple','4/4','4.75'),('Soft Maple','8/4','5.50'),('Red Oak','4/4','3.75'),('Red Oak','5/4','4.00'),('Red Oak','6/4','4.75'),('Red Oak','8/4','5.95'),('White Oak','4/4','7.50'),('White Oak','6/4','8.50'),('White Oak','8/4','12.00'),('Poplar','4/4','3.65'),('Poplar','6/4','4.00'),('Poplar','8/4','5.00'),('Walnut','4/4','9.75'),('Walnut','5/4','10.00'),('Walnut','6/4','10.50'),('Walnut','8/4','11.50')]
for s,t,p in ho: rows.append([s,t,'rough (KD, Sel&Btr)',p,'Hickory & Oak Lumber','Decatur','MI','https://hickoryandoak.com/prices.php',D])
for s,p in [('Walnut','14.00'),('Hard Maple','8.50'),('Cherry','8.50'),('White Oak','14.00'),('Ash','8.00'),('Mahogany','15.00'),('Sapele','15.00')]:
  rows.append([s,'not stated','S2S/S3S (FAS)',p,'The Wood Shed','Arlington','TX','https://img1.wsimg.com/blobby/go/85b7b81b-7200-43f8-9f91-b351a10519eb/Wood_Shed_Lumber_Price_List_FINAL.pdf',D])
with open('seed.csv','w',newline='') as f:
  w=csv.writer(f);w.writerow('species,thickness,surfacing,price_per_bf,dealer,city,state,source_url,date_checked'.split(','));w.writerows(rows)
print(len(rows),len({r[0] for r in rows}))
