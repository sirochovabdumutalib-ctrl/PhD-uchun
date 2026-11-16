"""Kollektor ta'mirining sizot sathiga ta'siri: quduq va yil qat'iy effektli model (difference-in-differences).
Davolangan quduq: nomi aniqlangan kollektordan <= NEAR m masofada; nazorat: har qanday kollektordan >= FAR m uzoqda.
Chiqish: data/repair_panel.csv va ekranga natijalar."""
import csv, json, re, collections, statistics as st, numpy as np, pandas as pd, statsmodels.formula.api as smf, warnings
from shapely.geometry import shape, Point
from shapely.ops import transform, unary_union
from pyproj import Transformer
warnings.filterwarnings('ignore')
NEAR, FAR = 300, 600
COPIED = {2010, 2013, 2017}; SUSPECT = {'Машъал', 'Юқори Роввот (Қиргизская)'}
tr = Transformer.from_crs(4326, 32643, always_xy=True).transform
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
F = json.load(open('gis/collectors_named.geojson', encoding='utf-8'))['features']
segs = [(transform(tr, shape(f['geometry'])), f['properties']) for f in F]
allnet = unary_union([g for g, _ in segs])
named = [(g, p) for g, p in segs if p['cad_name'] and p['repair_year'] and p['cad_name'] not in SUSPECT]
L = collections.defaultdict(lambda: collections.defaultdict(list))
for r in csv.DictReader(open('data/gw_levels_long.csv', encoding='utf-8')):
    y = int(r['year']); v = float(r['level_m'])
    if y not in COPIED: L[norm(r['well_no'])][y].append(v / 100 if v > 20 else v)
rows = []
for f in json.load(open('gis/wells_2024.geojson', encoding='utf-8'))['features']:
    k = norm(f['properties']['well_no']); p = transform(tr, Point(f['geometry']['coordinates']))
    d_all = p.distance(allnet); dn = [(g.distance(p), pr) for g, pr in named]; dmin, pr = min(dn, key=lambda x: x[0]) if dn else (9e9, None)
    if dmin <= NEAR and dmin <= d_all + 30: grp, ry, cn = 'treated', pr['repair_year'], pr['cad_name']
    elif d_all >= FAR: grp, ry, cn = 'control', None, None
    else: continue
    ever_const = any(len(set(v)) == 1 for v in L[k].values())
    for y, v in L[k].items():
        if len(set(v)) == 1: continue
        rows.append(dict(well=k, year=y, level=st.mean(v), summer=st.mean(v[18:24]) if len(v) >= 24 else np.nan, grp=grp, repair_year=ry,
                         collector=cn, dist=round(dmin if grp == 'treated' else d_all), ever_const=ever_const,
                         post=int(ry is not None and y > ry), et=(y - ry) if ry else np.nan))
D = pd.DataFrame(rows); D.to_csv('data/repair_panel.csv', index=False)
print('wells treated', D[D.grp == 'treated'].well.nunique(), 'control', D[D.grp == 'control'].well.nunique(), 'well-years', len(D), 'collectors', D.collector.nunique())
print('treated wells by repair year', D[D.grp == 'treated'].drop_duplicates('well').repair_year.value_counts().sort_index().to_dict())
def twfe(d, y='level', lab=''):
    d = d.dropna(subset=[y]); m = smf.ols(f'{y} ~ post + C(well) + C(year)', d).fit(cov_type='cluster', cov_kwds={'groups': d.well.astype('category').cat.codes})
    ci = m.conf_int().loc['post']; print(f'{lab:52s} beta={m.params["post"]:+.3f} m  SE={m.bse["post"]:.3f}  95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]  p={m.pvalues["post"]:.3f}  n={len(d)} wells={d.well.nunique()}')
twfe(D, lab='1) asosiy model (yillik o\'rtacha sath)')
twfe(D, 'summer', '2) yozgi sath (iyul-avgust)')
twfe(D[~D.ever_const], lab='3) faqat hech qachon o\'zgarmas bo\'lmagan quduqlar')
twfe(D[D.year <= 2016], lab='4) faqat 2009-2016 (tarmoq o\'zgarishidan oldin)')
twfe(D[D.year >= 2018], lab='5) faqat 2018-2024')
twfe(D[(D.grp == 'treated')], lab='6) faqat ta\'mirlangan kollektor yonidagilar')
# hodisa vaqti bo'yicha: yil effektidan tozalangan o'rtacha
ctrl = D[D.grp == 'control'].groupby('year')['level'].mean(); T = D[D.grp == 'treated'].copy()
T['adj'] = T.level - T.year.map(ctrl); T['adj'] -= T.groupby('well').adj.transform(lambda s: s[T.loc[s.index, 'et'] < 0].mean())
print('\nhodisa vaqti (ta\'mirdan necha yil): nazorat guruhiga nisbatan sath o\'zgarishi, m')
print(T[(T.et >= -4) & (T.et <= 5)].groupby('et').adj.agg(['mean', 'sem', 'count']).round(3).to_string())
