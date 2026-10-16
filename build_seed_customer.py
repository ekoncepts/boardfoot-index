# Harry's own Baird Brothers (Canfield OH) purchases: per-piece S4S prices converted to $/bf using NOMINAL size.
import csv
from decimal import Decimal as Dn, ROUND_HALF_UP
# (species, nominal thickness inches, width in, length ft, piece price)
P=[('Red Oak',Dn('1.25'),10,4,'33.16'),('Red Oak',1,12,2,'15.40'),('Red Oak',1,8,2,'7.90'),('Red Oak',1,4,2,'3.94'),('Red Oak',1,3,2,'2.96'),
   ('Red Oak',2,2,2,'6.78'),('Red Oak',2,2,2,'6.16'),
   ('Poplar',1,4,3,'4.40'),('Poplar',1,4,5,'7.34'),('Poplar',1,2,3,'2.61'),('Poplar',1,8,3,'9.48'),('Poplar',1,3,3,'3.69')]
q={4:'4/4',Dn('1.25'):'5/4',2:'8/4'}
rows=[]
for sp,t,w,l,price in P:
  bf=Dn(t)*w*l/12
  ppb=(Dn(price)/bf).quantize(Dn('0.01'),ROUND_HALF_UP)
  th={1:'4/4',Dn('1.25'):'5/4',2:'8/4'}[Dn(t)]
  note=f"S4S unfinished; per-piece ${price} for {t}x{w}x{l}ft nominal ({bf.quantize(Dn('0.0001'))} bf) converted to $/bf; order date unknown"
  rows.append([sp,th,note,str(ppb),'Baird Brothers Sawmill','Canfield','OH','customer-reported','2026-10-16'])
  print(sp,th,f"{t}x{w}x{l}",price,'=>',bf.quantize(Dn('0.0001')),'bf =>',ppb)
old=list(csv.reader(open('seed.csv')));ex={tuple(r) for r in old[1:]}
new=[r for r in rows if tuple(r) not in ex]
with open('seed.csv','w',newline='') as f: csv.writer(f).writerows(old+new)
print(len(new),'added; total',len(old)-1+len(new))
