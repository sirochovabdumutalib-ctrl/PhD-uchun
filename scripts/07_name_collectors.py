"""Xaritadagi kollektor nomlarini chiziq bo'laklariga biriktiradi va kadastr (ta'mir yili, uzunlik) bilan bog'laydi.
Ishlatish: python3 scripts/07_name_collectors.py <prefix_level>   Chiqish: gis/collectors_named.geojson, data/collector_name_match.csv"""
import sys, json, csv, re, numpy as np
from shapely.geometry import shape, Point, mapping
from shapely.ops import transform
from pyproj import Transformer
tr = Transformer.from_crs(4326, 32643, always_xy=True).transform
M = np.array(json.load(open('gis/georef.json'))['affine_px_to_utm43n'])
def key(s):
    s = re.sub(r'[\s;]+', '', s).lower().replace('ё', 'е')
    s = re.sub(r'^\d+', '', s)                                     # "9;Навбахор;" turidagi kanal raqamlari
    for a, b in (('ғкз', 'зкд'), ('шкз', 'вкд'), ('шк-', 'вкд-'), ('ғз', 'зд'), ('мз', 'цд'), ('аз', 'ад'), ('шз', 'шд')):
        if s.startswith(a): s = b + s[len(a):]; break
    s = s.replace('-а', 'а')
    alias = {'ўқчи': 'ўқчи(охчи)', 'аравон': 'аровон', 'шўр': 'шор', 'ўнгжфк': 'жфкўнг', 'чапжфк': 'жфкчап', 'чапжфк-5': 'жфкчап-5',
             'қирғиз': 'юқорироввот(қиргизская)', 'кушчиташламаси': 'қушчи', 'зд-5а': 'зд-5а', 'бештентак': 'бештентак'}
    return alias.get(s, s)
cad = {}
for c in csv.DictReader(open('data/collectors.csv', encoding='utf-8')):
    cad[re.sub(r'\s+', '', c['name']).lower()] = c
wells = set(re.sub(r'\s+', '', r['well_no']).upper() for r in csv.DictReader(open('data/wells_map_2024.csv', encoding='utf-8')) if r['well_no'])
labels = []
for t in json.load(open(sys.argv[1] + '_text.json')):
    raw = t['text']
    if t['color'] != 0 or t['size'] > 9 or re.sub(r'\s+', '', raw).upper() in wells or re.fullmatch(r'[\d\s,\.]+', raw): continue
    k = key(raw)
    if k in cad:
        E, N = np.array([t['cx'], t['cy'], 1]) @ M; labels.append((k, Point(E, N), raw))
segs = [(transform(tr, shape(f['geometry'])), f) for f in json.load(open('gis/collectors.geojson'))['features']]
name = [None] * len(segs)
for k, p, raw in labels:                                           # 1) yozuv ustida turgan bo'lak
    d = [g.distance(p) for g, _ in segs]; i = int(np.argmin(d))
    if d[i] < 220: name[i] = k
def ends(g):
    c = np.array(g.coords); return [(c[0], c[0] - c[min(3, len(c) - 1)]), (c[-1], c[-1] - c[max(-4, -len(c))])]
E = [ends(g) for g, _ in segs]
changed = True
while changed:                                                     # 2) nomni to'g'ri davom etgan qo'shni bo'lakka uzatish
    changed = False
    for i in range(len(segs)):
        if name[i] is None: continue
        for pi, vi in E[i]:
            best, bj = 0.75, None
            for j in range(len(segs)):
                if j == i or name[j] is not None: continue
                for pj, vj in E[j]:
                    if np.hypot(*(pi - pj)) < 25:
                        cos = -float(vi @ vj) / (np.linalg.norm(vi) * np.linalg.norm(vj) + 1e-9)   # qarama-qarshi yo'nalish = davom
                        if cos > best: best, bj = cos, j
            if bj is not None: name[bj] = name[i]; changed = True
feats, agg = [], {}
for (g, f), k in zip(segs, name):
    c = cad.get(k) if k else None
    f['properties'].update({'cad_name': c['name'] if c else None, 'repair_year': int(c['repair_year']) if c and c['repair_year'].isdigit() else None,
                            'commissioned': c['commissioned'] if c else None})
    feats.append(f)
    if c: agg[c['name']] = agg.get(c['name'], 0) + g.length
json.dump({'type': 'FeatureCollection', 'features': feats}, open('gis/collectors_named.geojson', 'w'), ensure_ascii=False)
with open('data/collector_name_match.csv', 'w', newline='', encoding='utf-8') as fo:
    cw = csv.writer(fo); cw.writerow(['cad_name', 'cad_length_km', 'map_length_km', 'repair_year'])
    for c in cad.values(): cw.writerow([c['name'], c['length_km'], round(agg.get(c['name'], 0) / 1000, 2), c['repair_year']])
tot = sum(g.length for g, _ in segs); named = sum(g.length for (g, _), k in zip(segs, name) if k)
print('labels matched to cadastre', len(labels), 'distinct', len(set(k for k, _, _ in labels)), 'of', len(cad))
print('named length km', round(named / 1000, 1), 'of', round(tot / 1000, 1), '| collectors with map geometry', len(agg))
r = [(float(c['length_km']), agg[c['name']] / 1000) for c in cad.values() if c['name'] in agg]
print('cad vs map length: corr', round(float(np.corrcoef(np.array(r).T)[0, 1]), 2), 'sum cad', round(sum(a for a, _ in r), 1), 'sum map', round(sum(b for _, b in r), 1))
