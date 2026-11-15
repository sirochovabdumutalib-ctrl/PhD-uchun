"""Har bir quduq uchun tarmoq ko'rsatkichlari (eng yaqin kollektor va kanalgacha masofa, 1 km radiusdagi
kollektor uzunligi) va tozalangan ko'p yillik sathni hisoblaydi. Chiqish: data/wells_metrics.csv"""
import csv, json, re, collections, statistics as st, numpy as np
from shapely.geometry import shape, Point
from shapely.ops import unary_union, transform
from pyproj import Transformer
tr = Transformer.from_crs(4326, 32643, always_xy=True).transform
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
net = {n: unary_union([transform(tr, shape(f['geometry'])) for f in json.load(open(f'gis/{n}.geojson'))['features']]) for n in ('collectors', 'canals')}
COPIED = {2010, 2013, 2017}                       # boshqa yildan nusxa ko'chirilgan yillar
L = collections.defaultdict(lambda: collections.defaultdict(list))
for r in csv.DictReader(open('data/gw_levels_long.csv', encoding='utf-8')):
    y = int(r['year']); v = float(r['level_m'])
    if y in COPIED: continue
    L[norm(r['well_no'])][y].append(v / 100 if v > 20 else v)   # sm da yozilgan qiymatlar
passport = {norm(r['well_no']): r for r in csv.DictReader(open('data/wells_passport.csv', encoding='utf-8'))}
rows = []
for f in json.load(open('gis/wells_2024.geojson', encoding='utf-8'))['features']:
    nm = f['properties']['well_no']; k = norm(nm); p = transform(tr, Point(f['geometry']['coordinates']))
    yrs = L.get(k, {}); ok = {y: v for y, v in yrs.items() if len(set(v)) > 1}        # yil bo'yi o'zgarmas qatorlar chiqariladi
    mean_all = st.mean(st.mean(v) for v in ok.values()) if ok else None
    recent = [st.mean(v) for y, v in ok.items() if y >= 2019]; early = [st.mean(v) for y, v in ok.items() if y <= 2016]
    summer = [st.mean(v[18:24]) for y, v in ok.items() if len(v) >= 24 and y >= 2019]  # iyul-avgust
    pp = passport.get(k, {})
    rows.append((nm, pp.get('massif', ''), round(p.x, 1), round(p.y, 1), round(p.distance(net['collectors']), 1), round(p.distance(net['canals']), 1),
                 round(net['collectors'].intersection(p.buffer(1000)).length, 1), pp.get('built_year', ''), pp.get('depth_cm', ''),
                 len(yrs), len(ok), round(mean_all, 3) if mean_all else '', round(st.mean(recent), 3) if recent else '',
                 round(st.mean(early), 3) if early else '', round(st.mean(summer), 3) if summer else '',
                 f['properties']['level_m_2024_04_01'] or '', f['properties']['miner_gl_2024_04_01'] or ''))
hdr = ['well_no', 'massif', 'x_utm43', 'y_utm43', 'dist_collector_m', 'dist_canal_m', 'collector_len_1km_m', 'built_year', 'well_depth_cm',
       'n_years', 'n_valid_years', 'level_mean_m', 'level_2019_2024_m', 'level_2009_2016_m', 'level_summer_m', 'level_2024_04_m', 'miner_2024_04_gl']
with open('data/wells_metrics.csv', 'w', newline='', encoding='utf-8') as f: cw = csv.writer(f); cw.writerow(hdr); cw.writerows(rows)
print('wells', len(rows), 'with valid level', sum(1 for r in rows if r[11] != ''), 'with massif', sum(1 for r in rows if r[1]))
