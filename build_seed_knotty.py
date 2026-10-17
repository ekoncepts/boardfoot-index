#!/usr/bin/env python3
"""Add The Knotty Lumber Co. (Hamilton, ON; affiliate partner) per-bf prices to seed.csv and dealers.csv.
Source: Knotty's US storefront (/en-us/, which Shopify reports as USD; JSON-LD priceCurrency=USD). Only the
'10 Board Feet' variant of each plain by-size dimensional listing is used, so $/bf = variant price / 10 with no guessing.
Idempotent: removes earlier Knotty rows first. Re-reads the live listing and asserts it is in stock, in USD and not on sale."""
import csv,json,re,subprocess,sys,os
UA="Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
TODAY='2026-10-17'
DEALER='The Knotty Lumber Co. (affiliate)'
BASEU='https://theknottylumberco.ca/en-us/products/'
LIST=[ # species, thickness, handle
 ('Walnut','4/4','4-4-black-walnut'),('Walnut','8/4','8-4-black-walnut-lumber'),
 ('Cherry','4/4','4-4-cherry-lumber'),('Cherry','8/4','8-4-cherry-lumber'),
 ('Hard Maple','4/4','4-4-hard-maple-lumber'),('Hard Maple','8/4','8-4-hard-maple-lumber'),
 ('White Oak','4/4','4-4-white-oak-lumber'),('White Oak','8/4','8-4-white-oak'),
 ('Red Oak','4/4','4-4-red-oak-lumber'),('Red Oak','8/4','8-4-red-oak-lumber'),
 ('Hickory','4/4','4-4-hickory-lumber'),('Hickory','8/4','8-4-hickory-lumber'),
 ('Ash','4/4','4-4-ash-lumber'),('Ash','8/4','8-4-ash-lumber'),
 ('Poplar','4/4','4-4-poplar-lumber')]
import time
def get(u):
    for i in range(4):
        o=subprocess.run(['curl','-sL','--compressed','-m','40','-A',UA,u],capture_output=True,text=True).stdout
        if o.strip(): return o
        time.sleep(2*(i+1))
    raise SystemExit('empty response: '+u)
os.makedirs('raw/knotty/products',exist_ok=True)
new=[]
for sp,th,h in LIST:
    j=json.loads(get(BASEU+h+'.js'))
    open(f'raw/knotty/products/{h}.js.json','w').write(json.dumps(j,indent=1))
    html=get(BASEU+h);open(f'raw/knotty/products/{h}.html','w').write(html)
    assert '"priceCurrency": "USD"' in html or 'currencyCode":"USD"' in html,(h,'not USD')
    v=[x for x in j['variants'] if x['title'].strip().lower()=='10 board feet']
    assert len(v)==1,(h,'no unique 10 BF variant')
    v=v[0];assert v['available'],(h,'sold out');assert not v.get('compare_at_price'),(h,'on sale')
    price=v['price']/100/10
    new.append(dict(species=sp,thickness=th,surfacing='not stated',price_per_bf=f'{price:.2f}',dealer=DEALER,city='Hamilton',state='ON',source_url=BASEU+h,date_checked=TODAY))
    print(sp,th,h,v['price']/100,'->',f'{price:.2f}')
# seed.csv: byte-preserving (the file has mixed line endings): drop old Knotty lines, append new ones
import io
cols=list(csv.DictReader(open('seed.csv')).fieldnames)
lines=open('seed.csv',newline='').read().splitlines(keepends=True)
lines=[l for l in lines if (DEALER not in l)]
if not lines[-1].endswith('\n'): lines[-1]+='\n'
buf=io.StringIO();w=csv.DictWriter(buf,fieldnames=cols,lineterminator='\n');w.writerows(new)
open('seed.csv','w',newline='').write(''.join(lines)+buf.getvalue())
# dealers.csv (adds an 'affiliate' column; blank for everyone else)
dl=list(csv.DictReader(open('dealers.csv')));dcols=list(csv.DictReader(open('dealers.csv')).fieldnames)
if 'affiliate' not in dcols: dcols.append('affiliate')
dl=[d for d in dl if d['dealer']!=DEALER]
for d in dl: d.setdefault('affiliate','')
dl.append(dict(dealer=DEALER,city='Hamilton',state='ON',ships='Yes (US and Canada)',
 shipping_note="Free shipping to the US and Canada applies to products advertised as free-shipping (lumber packs and bundles); the by-size lumber priced here shows 'Shipping calculated at checkout'. Ships by freight broker, often within 5 business days. Orders to the US may be charged import duties, tariffs or brokerage fees by the carrier, paid by the buyer and not included in the price. Returns carry a 20% restocking fee. Prices are as shown on its US storefront (USD).",
 shipping_source_url='https://theknottylumberco.ca/en-us/pages/free-north-america-wide-shipping-policy',date_checked=TODAY,affiliate='yes'))
with open('dealers.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=dcols,lineterminator='\n');w.writeheader();w.writerows(dl)
print(len(new),'rows added')
