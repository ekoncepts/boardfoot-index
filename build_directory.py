#!/usr/bin/env python3
"""Build the public North American Hardwood Dealers CSV and the hidden review queue.

Reads the ChatGPT source workbook (or a path given as argv[1]) and writes:
  directory/dealers-directory.csv          (website-verified, public)
  directory-review-queue.csv               (everything else; gitignored)
  /workspace/boardfoot/directory-price-sheet-leads.csv
      (public listings not on the Index that have a published email; do not send)
"""
import csv, re, sys
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

try:
    import openpyxl
except ImportError:
    sys.exit('openpyxl is required')

HERE = Path(__file__).resolve().parent
DEFAULT_XLSX = Path('/home/box/agent-data/agents/6668a5d1-4680-45de-b8ab-f0e7e5af5aeb/attachments/c8ca79d407ec21375c9d1aab1e457259aedc271e6f149a7c8e74745c52c08b16.xlsx')
INDEX_CSV = Path('/workspace/boardfoot/dealers.csv')
if not INDEX_CSV.exists():
    INDEX_CSV = HERE / 'dealers.csv'
LEADS_CSV = Path('/workspace/boardfoot/directory-price-sheet-leads.csv')
OUTREACH_CSV = Path('/workspace/boardfoot/outreach-log.csv')
if not OUTREACH_CSV.exists():
    OUTREACH_CSV = HERE / 'outreach-log.csv'

PUBLIC_CSV = HERE / 'directory' / 'dealers-directory.csv'
QUEUE_CSV = HERE / 'directory-review-queue.csv'

FIELDS = ['name','category','trade_only','country','state_prov','city','address','postal',
          'phone','toll_free','fax','email','website','contact_form','verification_source',
          'checked_date','status']
# leftover published contact (hours, extra phones) — kept for the page and the spreadsheet
EXTRA = 'other'

CATEGORY = {
    'Retailers': 'Retail hardwood dealers',
    'Wholesalers / distributors': 'Wholesalers and distributors',
    'Small / independent': 'Small businesses and independents',
    'Hobbyist / woodworking shops': 'Hobbyist and woodworking suppliers',
    'Sawmills': 'Sawmills',
}

THIRD_PARTY_HOSTS = {
    'hardwooddirectory.com','www.hardwooddirectory.com',
    'canadianwoodworking.com','www.canadianwoodworking.com',
    'hardwoodscanada.ca','www.hardwoodscanada.ca',
    'members.nhla.com','nhla.com','www.nhla.com',
    'builderssupplyland.ca',  # only when it's the source directory, not the YT dealer itself
}

TRADE_RE = re.compile(
    r'no retail sales|no retail|'
    r'not (open )?to the public|'
    r'(wholesale|trade) only|'
    r'to the trade only|'
    r'does not sell retail|'
    r'no public sales|'
    r'not sell to (the )?public',
    re.I)
EMAIL_RE = re.compile(r'[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}', re.I)
FAKE_EMAIL_RE = re.compile(r'(mysite\.com|example\.com|email\.com|domain\.com)$', re.I)

def clean(v):
    if v is None:
        return ''
    if not isinstance(v, str):
        v = str(v)
    return re.sub(r'\s+', ' ', v).strip()

def load_rows(xlsx):
    wb = openpyxl.load_workbook(xlsx, data_only=True)
    ws = wb['All Dealers']
    headers = [clean(ws.cell(4, c).value) for c in range(1, ws.max_column + 1)]
    rows = []
    for r in range(5, ws.max_row + 1):
        d = {headers[c-1]: clean(ws.cell(r, c).value) for c in range(1, len(headers)+1)}
        if d.get('Business name'):
            rows.append(d)
    return rows

def is_public(r):
    v = r.get('Contact verification', '')
    if 'permanent closure' in v.lower():
        return False
    return v.startswith('Published on dealer website')

def origin_url(u):
    u = clean(u)
    if not u:
        return ''
    if not re.match(r'^https?://', u, re.I):
        if '.' in u and ' ' not in u:
            u = 'https://' + u
        else:
            return ''
    try:
        p = urlparse(u)
    except ValueError:
        return ''
    if p.scheme not in ('http', 'https') or not p.netloc:
        return ''
    host = p.netloc.lower()
    if host in THIRD_PARTY_HOSTS or host.endswith('.hardwooddirectory.com'):
        return ''
    return f"{p.scheme}://{p.netloc}"

def website_of(r):
    w = clean(r.get('Website', ''))
    if w:
        if not re.match(r'^https?://', w, re.I):
            w = 'https://' + w
        return w
    # Recover from contact form / source when the Website column was left blank
    for cand in (r.get('Contact form', ''), r.get('Contact information source', '')):
        o = origin_url(cand)
        if o:
            return o + '/'
    return ''

def emails_of(r):
    found = []
    seen = set()
    def add(text):
        for e in EMAIL_RE.findall(text or ''):
            if FAKE_EMAIL_RE.search(e):
                continue
            key = e.lower()
            if key not in seen:
                seen.add(key)
                found.append(e)
    add(r.get('Email', ''))
    add(r.get('Other contact information', ''))
    # research notes only if they mention a published email already captured pattern
    return '; '.join(found)

def trade_only(r):
    blob = ' '.join([
        r.get('Products / services', ''),
        r.get('Other contact information', ''),
        r.get('Contact / research notes', ''),
    ])
    return 'yes' if TRADE_RE.search(blob) else ''

def queue_status(r):
    v = (r.get('Contact verification') or '').lower()
    notes = (r.get('Contact / research notes') or '').lower()
    if 'permanent closure' in v or 'closed' in v:
        return 'closed'
    if 'classification requires correction' in v or 'classification warning' in notes:
        return 'classification-review'
    if 'staging contact page' in v:
        return 'staging-page-only'
    if 'not researched' in v or 'not researched/confirmed' in v:
        return 'not-researched' if website_of(r) or r.get('Website') else 'no-website'
    if 'not checked on dealer website' in v or 'external directory' in v or 'third-party' in v:
        return 'third-party'
    if 'not accessible' in v or 'no verifiable' in v or 'attempted' in v:
        return 'website-inaccessible'
    return 'needs-review'

def other_of(r):
    # Keep published extra contact (hours, extra lines) but drop research-process notes
    return r.get('Other contact information', '')

def record(r, status):
    src = r.get('Contact information source', '') or r.get('Contact form', '') or website_of(r)
    rec = {
        'name': r['Business name'],
        'category': CATEGORY.get(r.get('Primary category', ''), r.get('Primary category', '')),
        'trade_only': trade_only(r),
        'country': r.get('Country', ''),
        'state_prov': r.get('State / province', ''),
        'city': r.get('City / area', ''),
        'address': r.get('Street address', ''),
        'postal': r.get('ZIP / postal code', ''),
        'phone': r.get('Telephone', ''),
        'toll_free': r.get('Toll-free telephone', ''),
        'fax': r.get('Fax', ''),
        'email': emails_of(r),
        'website': website_of(r),
        'contact_form': r.get('Contact form', ''),
        'verification_source': src,
        'checked_date': r.get('Contact checked date', '') or '2026-11-20',
        'status': status,
        'other': other_of(r),
    }
    return rec

def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS + [EXTRA], extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)

def strip_idx(n):
    return re.sub(r'\s*\((affiliate|FAS grade|[^)]*BF tier)\)$', '', n, flags=re.I).strip()

def tokens(n):
    n = n.lower()
    n = re.sub(r"[.,'()/&+]", ' ', n)
    n = re.sub(r'\b(inc|llc|ltd|ltee|co|company|corp|corporation|limited|the|of)\b', '', n)
    return [t for t in n.split() if t]

STOP = {'lumber','hardwood','hardwoods','wood','woods','products','sawmill','mill','millworks','fine','group','supply'}

def matches_index(rec, index_rows):
    """Same-state match with equal/subset significant name tokens, or a substantial substring."""
    ti = tokens(rec['name'])
    sig = set(ti) - STOP
    city = (rec['city'] or '').lower()
    hits = []
    for d in index_rows:
        if d['state'] != rec['state_prov']:
            continue
        dn = strip_idx(d['dealer'])
        tr = tokens(dn)
        sr = set(tr) - STOP
        why = ''
        if ti == tr or (sig and sig == sr) or (sig and sr and (sig <= sr or sr <= sig)):
            why = 'tokens'
        else:
            ni, nr = ' '.join(ti), ' '.join(tr)
            if ni and nr and len(ni) > 6 and len(nr) > 6 and (ni in nr or nr in ni):
                why = 'substr'
        if not why:
            continue
        dcity = (d['city'] or '').lower()
        city_ok = bool(city and dcity and (city in dcity or dcity in city))
        if city_ok or why == 'tokens':
            hits.append((city_ok, dn, d['dealer']))
    hits.sort(key=lambda x: (not x[0], x[1].lower()))
    return hits[0] if hits else None

def main():
    xlsx = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_XLSX
    if not xlsx.exists():
        sys.exit(f'source workbook not found: {xlsx}')
    raw = load_rows(xlsx)
    public, queue = [], []
    for r in raw:
        if is_public(r):
            public.append(record(r, 'verified'))
        else:
            queue.append(record(r, queue_status(r)))

    def sort_key(rec):
        # US first, then Canada; then state code, then name without leading The
        country = 0 if rec['country'] == 'United States' else 1
        name = re.sub(r'^the\s+', '', rec['name'], flags=re.I).lower()
        return (country, rec['state_prov'], rec['city'].lower(), name)

    public.sort(key=sort_key)
    queue.sort(key=lambda r: (r['status'], r['country'], r['state_prov'], r['name'].lower()))

    write_csv(PUBLIC_CSV, public)
    write_csv(QUEUE_CSV, queue)

    index_rows = list(csv.DictReader(open(INDEX_CSV))) if INDEX_CSV.exists() else []
    matched = []
    unmatched_index = []
    pub_matched_names = set()
    for d in index_rows:
        # reverse match to report Index dealers not in the public set
        pass
    for rec in public:
        hit = matches_index(rec, index_rows)
        if hit:
            matched.append((rec['name'], hit[1], rec['city'], rec['state_prov']))
            pub_matched_names.add(rec['name'])

    outreach = []
    if OUTREACH_CSV.exists():
        outreach = list(csv.DictReader(open(OUTREACH_CSV)))
    outreach_emails = {re.sub(r'\s','', (row.get('email') or '')).lower() for row in outreach}

    leads = []
    for rec in public:
        if rec['name'] in pub_matched_names:
            continue
        if not rec['email']:
            continue
        emails = [e.strip() for e in rec['email'].split(';') if e.strip()]
        already = '; '.join(e for e in emails if e.lower() in outreach_emails)
        leads.append({
            'name': rec['name'],
            'category': rec['category'],
            'city': rec['city'],
            'state_prov': rec['state_prov'],
            'country': rec['country'],
            'email': rec['email'],
            'website': rec['website'],
            'contact_form': rec['contact_form'],
            'already_contacted_email': already,
        })
    if LEADS_CSV.parent.exists():
        with LEADS_CSV.open('w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(leads[0].keys()) if leads else
                               ['name','category','city','state_prov','country','email','website','contact_form','already_contacted_email'])
            w.writeheader()
            w.writerows(leads)

    print(f'Source rows: {len(raw)}')
    print(f'Public (website-verified): {len(public)}')
    print('  by country:', dict(Counter(r['country'] for r in public)))
    print('  by category:', dict(Counter(r['category'] for r in public)))
    print(f'  trade/wholesale only: {sum(1 for r in public if r["trade_only"]=="yes")}')
    print(f'Review queue: {len(queue)}')
    print('  by status:', dict(Counter(r['status'] for r in queue)))
    print(f'Index cross-links in public set: {len(matched)}')
    for m in matched:
        print(f'    {m[0]} ({m[2]}, {m[3]}) <-> Index: {m[1]}')
    print(f'Price-sheet leads (public, not on Index, has email): {len(leads)}')
    print(f'  unique emails: {len({e.strip().lower() for row in leads for e in row["email"].split(";") if e.strip()})}')
    print(f'  already in outreach-log: {sum(1 for row in leads if row["already_contacted_email"])}')
    print(f'Wrote {PUBLIC_CSV}')
    print(f'Wrote {QUEUE_CSV}')
    if LEADS_CSV.parent.exists():
        print(f'Wrote {LEADS_CSV}')

if __name__ == '__main__':
    main()
