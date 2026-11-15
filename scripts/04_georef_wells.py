"""Xaritadagi quduq belgilarini topadi, yozuvlar bilan juftlaydi, haqiqiy koordinatalar orqali
georeferensiya qiladi (affin, UTM 43N) va 2024-04-01 qiymatlarini quduqlarga biriktiradi.
Ishlatish: python3 scripts/04_georef_wells.py <prefix_level> <prefix_miner> <data_dir> <gis_dir>"""
import sys, json, csv, re, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS = None
pl, pm, DATA, GIS = sys.argv[1:5]
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ').replace('П3', 'ПЗ')
def symbols(prefix):
    a = np.asarray(Image.open(prefix + '_raster.png')).astype(int)
    m = (abs(a[:, :, 0] - 115) < 6) & (abs(a[:, :, 1] - 178) < 6) & (abs(a[:, :, 2] - 255) < 6)
    lab, n = ndi.label(ndi.binary_closing(m, iterations=2))
    sizes = ndi.sum(m, lab, range(1, n + 1)); cen = ndi.center_of_mass(m, lab, range(1, n + 1))
    return [(c[1], c[0]) for c, s in zip(cen, sizes) if 150 < s < 2500]
def labels(prefix):
    T = json.load(open(prefix + '_text.json'))
    hor = [t for t in T if abs(t['dir'][0]) > 0.99 and t['size'] < 9]
    return [t for t in hor if t['color'] == 0], [t for t in hor if t['color'] == 0xff0000]
def pair(sym, labs, maxd=90):
    out = {}
    for i, (x, y) in enumerate(sym):
        d = [((t['cx'] - x) ** 2 + (t['cy'] - y) ** 2) ** .5 for t in labs]
        if d and min(d) < maxd: out[i] = labs[int(np.argmin(d))]['text']
    return out
coords = {norm(r['well_no']): (float(r['lon']), float(r['lat']), r['well_no']) for r in csv.DictReader(open(DATA + '/wells_coords.csv', encoding='utf-8'))}
tr = Transformer.from_crs(4326, 32643, always_xy=True); inv = Transformer.from_crs(32643, 4326, always_xy=True)
res = {}
for key, prefix in (('level', pl), ('miner', pm)):
    sym = symbols(prefix); names, vals = labels(prefix)
    pn, pv = pair(sym, names), pair(sym, vals)
    res[key] = (sym, pn, pv); print(key, 'symbols', len(sym), 'named', len(pn), 'valued', len(pv))
sym, pn, pv = res['level']
P, Q, used = [], [], []
for i, nm in pn.items():
    if norm(nm) in coords:
        lon, lat, _ = coords[norm(nm)]; P.append(sym[i]); Q.append(tr.transform(lon, lat)); used.append(nm)
P, Q = np.array(P), np.array(Q)
def fit(P, Q):
    A = np.c_[P, np.ones(len(P))]; M, *_ = np.linalg.lstsq(A, Q, rcond=None); return M
M = fit(P, Q); r = np.linalg.norm(np.c_[P, np.ones(len(P))] @ M - Q, axis=1)
keep = r < max(150, 3 * np.median(r)); M = fit(P[keep], Q[keep]); r2 = np.linalg.norm(np.c_[P[keep], np.ones(keep.sum())] @ M - Q[keep], axis=1)
print('control points', len(P), 'kept', int(keep.sum()), 'RMSE m', round(float(np.sqrt((r2 ** 2).mean())), 1), 'median', round(float(np.median(r2)), 1), 'max', round(float(r2.max()), 1))
print('pixel size m', round(float(np.linalg.norm(M[0])), 3), round(float(np.linalg.norm(M[1])), 3), 'rejected', [u for u, k in zip(used, keep) if not k])
json.dump({'affine_px_to_utm43n': M.tolist(), 'rmse_m': float(np.sqrt((r2 ** 2).mean())), 'n_control': int(keep.sum())}, open(GIS + '/georef.json', 'w'))
# 2024 qiymatlari: sath (sm -> m) va minerallashuv
def num(s):
    try: return float(str(s).replace(',', '.'))
    except Exception: return None
msym, mpn, mpv = res['miner']; mval = {norm(mpn[i]): num(mpv[i]) for i in mpn if i in mpv}
feats, rows = [], []
for i, (x, y) in enumerate(sym):
    E, N = np.array([x, y, 1]) @ M; lon, lat = inv.transform(E, N); nm = pn.get(i)
    lv = num(pv.get(i)); lv = lv / 100 if lv is not None else None; mi = mval.get(norm(nm)) if nm else None
    known = coords.get(norm(nm)) if nm else None
    rows.append((nm, round(lon, 6), round(lat, 6), known[0] if known else '', known[1] if known else '', lv, mi))
    feats.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [round(lon, 6), round(lat, 6)]},
                  'properties': {'well_no': nm, 'level_m_2024_04_01': lv, 'miner_gl_2024_04_01': mi}})
json.dump({'type': 'FeatureCollection', 'features': feats}, open(GIS + '/wells_2024.geojson', 'w'), ensure_ascii=False)
with open(DATA + '/wells_map_2024.csv', 'w', newline='', encoding='utf-8') as f:
    cw = csv.writer(f); cw.writerow(['well_no', 'lon_map', 'lat_map', 'lon_table', 'lat_table', 'level_m', 'miner_gl']); cw.writerows(rows)
print('wells on map', len(rows), 'with name', sum(1 for r in rows if r[0]), 'in coords table', sum(1 for r in rows if r[3] != ''), 'level', sum(1 for r in rows if r[5] is not None), 'miner', sum(1 for r in rows if r[6] is not None))
