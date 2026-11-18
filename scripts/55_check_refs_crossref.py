"""Adabiyotlar tekshiruvi (citation-management, 4-band): xorijiy jurnal maqolalari Crossref bilan solishtiriladi
(sarlavha + birinchi muallif bo'yicha qidiruv; yil, jurnal, jild, birinchi sahifa, DOI). Faqat tekshiradi, ro'yxatni o'zgartirmaydi.
Kirish: out/dissertatsiya.md; chiqish: results/refs_crossref.json"""
import re, json, time, sys, difflib, requests
md = open('out/dissertatsiya.md', encoding='utf-8').read(); a = md.index('FOYDALANILGAN ADABIYOTLAR'); b = md.index('ILOVALAR', a)
items = re.findall(r'^(\d+)\.\s+(.*)$', md[a:b], re.M)
S = requests.Session(); S.headers['User-Agent'] = 'thesis-reference-check/1.0'
def norm(s): return re.sub(r'[^a-z0-9]', '', s.lower())
out = []
for n, t in items:
    if '//' not in t or not re.search(r'Vol\.|Art\.', t): continue
    auth, rest = t.split(' ', 1)[0].rstrip(','), t
    title = re.split(r'\s//\s', re.sub(r'^([^.]+?\.\s*)+?(?=[A-Z][a-z])', '', t, count=0))[0]
    m = re.match(r'^(.*?[A-Z]\.(?:\s?[A-Z]\.)*(?:,\s*[^,]+?[A-Z]\.(?:\s?[A-Z]\.)*)*(?:\set al\.)?)\s+(.*?)\s//\s(.*)$', t)
    if not m: out.append(dict(n=int(n), status='parse_fail')); continue
    authors, title, src = m.groups(); fam = authors.split()[0].rstrip(',')
    yr = re.search(r'–\s*(\d{4})\.', src); vol = re.search(r'Vol\.\s*([\w-]+)', src); pg = re.search(r'P\.\s*S?(\d+)|Art\.\s*(\w+)', src)
    try:
        r = S.get('https://api.crossref.org/works', params={'query.bibliographic': title, 'query.author': fam, 'rows': 3}, timeout=30).json()['message']['items']
    except Exception as e:
        out.append(dict(n=int(n), status='error', err=str(e)[:80])); continue
    best = max(r, key=lambda it: difflib.SequenceMatcher(None, norm(title), norm((it.get('title') or [''])[0])).ratio()) if r else None
    if not best: out.append(dict(n=int(n), status='not_found')); continue
    sim = difflib.SequenceMatcher(None, norm(title), norm((best.get('title') or [''])[0])).ratio()
    cy = (best.get('issued', {}).get('date-parts') or [[None]])[0][0]
    rec = dict(n=int(n), sim=round(sim, 2), doi=best.get('DOI'), cr_title=(best.get('title') or [''])[0][:120], cr_journal=(best.get('container-title') or [''])[0],
               cr_year=cy, cr_volume=best.get('volume'), cr_page=best.get('page') or best.get('article-number'),
               ref_year=yr and yr.group(1), ref_volume=vol and vol.group(1), ref_page=pg and (pg.group(1) or pg.group(2)), has_doi_in_ref='doi.org' in t or '10.' in t)
    issues = []
    if sim >= 0.85:
        if rec['ref_year'] and cy and int(rec['ref_year']) != cy: issues.append(f'yil {rec["ref_year"]}≠{cy}')
        if rec['ref_volume'] and rec['cr_volume'] and rec['ref_volume'] != rec['cr_volume']: issues.append(f'jild {rec["ref_volume"]}≠{rec["cr_volume"]}')
        if rec['ref_page'] and rec['cr_page'] and not str(rec['cr_page']).lstrip('S').startswith(rec['ref_page']): issues.append(f'sahifa {rec["ref_page"]}≠{rec["cr_page"]}')
        rec['status'] = 'mismatch' if issues else 'ok'
    else: rec['status'] = 'uncertain'
    rec['issues'] = issues; out.append(rec); print(n, rec['status'], rec['sim'], issues, rec['doi'], flush=True); time.sleep(1)
json.dump(out, open('results/refs_crossref.json', 'w'), ensure_ascii=False, indent=1)
