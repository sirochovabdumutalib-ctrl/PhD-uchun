"""Minerallashuv 1999-2015 (yiliga 3 marta: 1-aprel, 1-iyul, 1-oktabr) ni uzun jadvalga ajratadi.
Ishlatish: python3 scripts/09_miner_extract.py <uploads_dir>   Chiqish: data/miner_1999_2015.csv"""
import sys, glob, os, csv, re, xlrd
f = [p for p in glob.glob(os.path.join(sys.argv[1], '*')) if '64104bb2' in os.path.basename(p)][0]
s = xlrd.open_workbook(f).sheet_by_index(0)
years = {}
for c in range(2, s.ncols):
    m = re.search(r'(\d{4})', str(s.cell_value(3, c)))
    if m: years[c] = int(m.group(1))
out, massif = [], ''
for i in range(6, s.nrows):
    g = str(s.cell_value(i, 0)).strip()
    if g.startswith('Условные'): break
    if g:
        m = re.search(r'\(([^)]+)\)', g); massif = m.group(1).strip() if m else g
    w = s.cell_value(i, 1)
    if w == '': continue
    w = str(int(w)) if isinstance(w, float) else str(w).strip()
    for c, y in years.items():
        for k, season in enumerate(('apr', 'jul', 'oct')):
            v = s.cell_value(i, c + k)
            if isinstance(v, float): out.append((y, season, w, massif, v))
with open('data/miner_1999_2015.csv', 'w', newline='', encoding='utf-8') as fo:
    cw = csv.writer(fo); cw.writerow(['year', 'season', 'well_no', 'massif', 'miner_gl']); cw.writerows(out)
print('rows', len(out), 'wells', len(set(o[2] for o in out)), 'years', sorted(set(o[0] for o in out)))
