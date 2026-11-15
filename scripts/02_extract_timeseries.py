"""2009-2024 yillik varaqlardan Marhamat tumani quduqlari bo'yicha o'n kunlik sizot sathi
va yillik minerallashuvni ajratadi. Ishlatish: python3 scripts/02_extract_timeseries.py <uploads_dir> <out_dir>
Chiqish: gw_levels_long.csv (yil, quduq, dekada, sath) va gw_annual.csv (yil, quduq, koordinata, o'rtacha, minerallashuv)."""
import sys, csv, glob, os, re, xlrd
U, OUT = sys.argv[1], sys.argv[2]
DISTRICTS = ['андижон', 'асака', 'балик', 'балиқ', 'булок', 'булоқ', 'бустон', 'жалакудук', 'жалақудуқ', 'избоскан', 'улугнор',
             'улуғнор', 'мархамат', 'марҳамат', 'олтинк', 'пахтаобод', 'худжаобод', 'хужаобод', 'хўжаобод', 'шахрихон', 'кургонтепа', 'қўрғонтепа']
def wellno(v):
    if isinstance(v, float): return str(int(v)) if v == int(v) else str(v)
    return re.sub(r'\s+', ' ', str(v)).strip()
def num(v):
    return v if isinstance(v, (int, float)) and v != '' else None
def is_district(row):
    for v in row[:2]:
        if isinstance(v, str) and any(v.strip().lower().startswith(d) for d in DISTRICTS): return v.strip().lower()
    return None
def extract(path, has_xy):
    wb = xlrd.open_workbook(path, on_demand=True); ann, lon = [], []
    c0 = 6 if has_xy else 2
    for sh in wb.sheet_names():
        s = wb.sheet_by_name(sh); on = False; group = ''
        for i in range(5, s.nrows):
            r = s.row_values(i); d = is_district(r)
            if d and all(not isinstance(v, float) for v in r[c0:c0 + 6]):
                on = d.startswith('мархамат') or d.startswith('марҳамат'); group = ''; continue
            if not on or r[1] in ('', None): continue
            if isinstance(r[0], str) and len(r[0].strip()) > 2: group = r[0].strip()
            lv = [num(v) for v in r[c0:c0 + 36]]
            if not any(v is not None for v in lv): continue
            w = wellno(r[1])
            xy = (num(r[2]), num(r[3]), num(r[4]), num(r[5])) if has_xy else (None,) * 4
            miner = num(r[c0 + 37]) if has_xy and len(r) > c0 + 37 else None
            ann.append((int(sh), w, group, *xy, num(r[c0 + 36]), miner, sum(v is not None for v in lv)))
            lon += [(int(sh), w, k + 1, v) for k, v in enumerate(lv) if v is not None]
        wb.unload_sheet(sh)
    return ann, lon
def find(p): return [f for f in glob.glob(os.path.join(U, '*')) if p in os.path.basename(f)][0]
ann, lon = extract(find('379248cf'), True)
with open(os.path.join(OUT, 'gw_annual.csv'), 'w', newline='', encoding='utf-8') as f:
    cw = csv.writer(f); cw.writerow(['year', 'well_no', 'group', 'lon', 'lat', 'z_m', 'area_ha', 'mean_level_m', 'miner_gl', 'n_obs']); cw.writerows(ann)
with open(os.path.join(OUT, 'gw_levels_long.csv'), 'w', newline='', encoding='utf-8') as f:
    cw = csv.writer(f); cw.writerow(['year', 'well_no', 'decade', 'level_m']); cw.writerows(lon)
ann2, lon2 = extract(find('7285b57a'), False)
with open(os.path.join(OUT, 'gw_annual_file2.csv'), 'w', newline='', encoding='utf-8') as f:
    cw = csv.writer(f); cw.writerow(['year', 'well_no', 'group', 'lon', 'lat', 'z_m', 'area_ha', 'mean_level_m', 'miner_gl', 'n_obs']); cw.writerows(ann2)
print('file1 annual', len(ann), 'decadal obs', len(lon), '| file2 annual', len(ann2), 'decadal obs', len(lon2))
