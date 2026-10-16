# BoardFoot Index – Build Plan (zero spend)

## 1. Hosting (free, static)
- **GitHub Pages** (recommended start): free, custom domain optional, deploy = push repo.
- **Cloudflare Pages**: free unlimited bandwidth, fast CDN, good if traffic grows.
- **Netlify** free tier: also gives Netlify Forms (100 submissions/mo free) – simplest form option.
- Domain: use the free `*.github.io` / `*.pages.dev` subdomain first; buying a domain (~$10/yr) is optional and needs Harry's approval.

## 2. Price submissions (free form/DB)
- **Google Form → Google Sheet** (easiest, moderated manually, then exported to seed.csv).
- **Netlify Forms** (if hosting on Netlify).
- **Supabase free tier** (Postgres + REST; later allows live data + moderation flag). Free projects pause after inactivity.
- Workflow: submissions land unapproved → Harry/agent reviews weekly → approved rows merged into the CSV → site rebuild.

## 3. Page structure (SEO)
- `/` – search all prices (current prototype).
- `/species/{walnut}/` – national range, median by thickness, price chart over time.
- `/species/{walnut}/{state}/` – "Walnut price per board foot in Ohio" (main SEO target; species x state ≈ 15 x 50 pages, generated from CSV by a small build script; only publish pages with ≥3 data points to avoid thin content).
- `/dealers/{state}/` – dealers with sheets (later: paid featured pins).
- `/report/` monthly Lumber Price Report archive (also the newsletter); `/submit/`; `/about` + methodology + affiliate disclosure.
- schema.org Dataset/Product markup, sitemap.xml, monthly date-stamped updates.

## 4. Newsletter (free tiers)
- **Buttondown** (free up to 100 subs, markdown, simple embed).
- **Kit (ConvertKit) Newsletter** free plan (up to ~10k subs).
- **Beehiiv** free Launch plan (up to 2,500 subs; has its own ad network later).
- **MailerLite** free (up to 1,000 subs).
- Recommend Kit or Beehiiv for headroom; check current limits at sign-up.

## 5. Monetization later
Rockler (5%) & Woodcraft (3%, via CJ/Skimlinks) affiliates, Amazon Associates, featured-dealer listings, newsletter sponsors (e.g. online lumber sellers). Requires disclosure page.

## 6. Accounts Harry must create/connect (none created yet)
1. GitHub account (repo + Pages) – or Cloudflare / Netlify account.
2. Google account for Google Form/Sheet – or Supabase account (GitHub login).
3. Newsletter provider account (Kit/Beehiiv/Buttondown/MailerLite) – needs a sender identity/postal address per CAN-SPAM.
4. Later, optional: Google Search Console (verify site), affiliate applications (Rockler, CJ for Woodcraft, Amazon Associates) – these need a live site.
5. Optional purchase: custom domain.

## 7. Data
- seed.csv: real prices from public dealer sheets, 2026-10-16. Refresh monthly; keep source_url + date on every row.
