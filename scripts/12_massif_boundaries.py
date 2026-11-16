"""Massiv chegaralarini tiklash: xaritadagi qizil chegara bo'laklari to'siq sifatida olinadi, har bir massiv
quduqlaridan (pasport bo'yicha) geodezik masofa hisoblanadi va piksel eng yaqin massivga biriktiriladi.
Ishlatish: python3 scripts/12_massif_boundaries.py <prefix_level>
Chiqish: gis/massifs.geojson, gis/district.geojson, data/massif_areas.csv, figures/massifs.png"""
import sys, json, csv, re, numpy as np, pandas as pd
from PIL import Image
from scipy import ndimage as ndi
from skimage.graph import MCP_Geometric
from skimage import measure
from shapely.geometry import Polygon, MultiPolygon, mapping
from shapely.ops import unary_union
from pyproj import Transformer
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
Image.MAX_IMAGE_PIXELS = None
F = 4                                                    # siyraklashtirish: 1 katak = 4 piksel ~ 16,9 m
a = np.asarray(Image.open(sys.argv[1] + '_raster.png')).astype(int)
M = np.array(json.load(open('gis/georef.json'))['affine_px_to_utm43n'])
H, W = a.shape[:2]
def col(rgb, tol=10): return (abs(a[:, :, 0] - rgb[0]) < tol) & (abs(a[:, :, 1] - rgb[1]) < tol) & (abs(a[:, :, 2] - rgb[2]) < tol)
red = (a[:, :, 0] > 200) & (a[:, :, 1] < 40) & (a[:, :, 2] < 40)
irr = np.zeros((H, W), bool)                              # sug'oriladigan yer: sath darajalari ranglari
for c in ((255, 235, 175), (190, 232, 255), (211, 255, 190), (255, 255, 115), (255, 190, 190), (232, 190, 255)): irr |= col(c)
settle = col((222, 158, 102))
nonwhite = ~((a[:, :, 0] > 245) & (a[:, :, 1] > 245) & (a[:, :, 2] > 245))
nonwhite[int(H * 0.70):, : int(W * 0.40)] = False         # shartli belgilar
nonwhite[: int(H * 0.12), :] = False; nonwhite[int(H * 0.93):, :] = False
def down(m): return m[: H // F * F, : W // F * F].reshape(H // F, F, W // F, F).any(axis=(1, 3))
nw, rd, ir, st = down(nonwhite), down(red), down(irr), down(settle)
body = ndi.binary_fill_holes(ndi.binary_closing(nw, iterations=4))
lab, n = ndi.label(ndi.binary_opening(body, iterations=3)); sizes = ndi.sum(body, lab, range(1, n + 1))
district = ndi.binary_fill_holes(ndi.binary_dilation(lab == (1 + int(np.argmax(sizes))), iterations=3) & body)
# quduqlar -> katak koordinatalari
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper()
Wl = pd.read_csv('data/wells_metrics.csv'); Wl = Wl[Wl.massif.notna()]
Ainv = np.linalg.inv(M[:2]); px = (Wl[['x_utm43', 'y_utm43']].values - M[2]) @ Ainv
Wl['c'] = (px[:, 0] / F).round().astype(int); Wl['r'] = (px[:, 1] / F).round().astype(int)
cost = np.where(district, 1.0, 1e6); cost[ndi.binary_dilation(rd, iterations=1) & district] = 400.0   # qizil chiziq = to'siq
names = sorted(Wl.massif.unique()); D = []
for nm in names:
    starts = [(int(r), int(c)) for r, c in Wl[Wl.massif == nm][['r', 'c']].values if 0 <= r < cost.shape[0] and 0 <= c < cost.shape[1] and district[r, c]]
    D.append(MCP_Geometric(cost).find_costs(starts)[0])
own = np.argmin(np.array(D), axis=0); own[~district] = -1
for k in range(len(names)):                               # mayda orolchalarni tozalash
    m = own == k; l2, n2 = ndi.label(m)
    if n2 > 1:
        s2 = ndi.sum(m, l2, range(1, n2 + 1)); own[m & (l2 != 1 + int(np.argmax(s2)))] = -2
if (own == -2).any():
    idx = ndi.distance_transform_edt(own == -2, return_distances=False, return_indices=True); own = np.where(own == -2, own[tuple(idx)], own)
inv = Transformer.from_crs(32643, 4326, always_xy=True)
def to_poly(mask):
    polys = []
    for cnt in measure.find_contours(np.pad(mask, 1).astype(float), 0.5):
        p = (cnt - 1)[:, ::-1] * F + F / 2; U = np.c_[p, np.ones(len(p))] @ M
        if len(U) >= 4: polys.append(Polygon(U).buffer(0))
    polys = [p for p in polys if p.area > 2e4]; polys.sort(key=lambda p: -p.area)
    out = polys[0]
    for p in polys[1:]: out = out.difference(p) if out.contains(p.representative_point()) else out.union(p)
    return out.simplify(15)
def ll(g): return json.loads(json.dumps(mapping(g)), parse_float=lambda x: round(float(x), 6)) if False else mapping(
    type(g)([Polygon([inv.transform(x, y) for x, y in q.exterior.coords], [[inv.transform(x, y) for x, y in i.coords] for i in q.interiors]) for q in g.geoms]) if g.geom_type == 'MultiPolygon'
    else Polygon([inv.transform(x, y) for x, y in g.exterior.coords], [[inv.transform(x, y) for x, y in i.coords] for i in g.interiors]))
cell_ha = (np.linalg.norm(M[0]) * F) * (np.linalg.norm(M[1]) * F) / 1e4
feats, rows = [], []
for k, nm in enumerate(names):
    m = own == k; g = to_poly(m); w = Wl[Wl.massif == nm]
    inside = int(sum(own[r, c] == k for r, c in w[['r', 'c']].values if 0 <= r < own.shape[0] and 0 <= c < own.shape[1]))
    rows.append((nm, round(m.sum() * cell_ha), round((m & ir).sum() * cell_ha), round((m & st).sum() * cell_ha), len(w), inside))
    feats.append({'type': 'Feature', 'properties': {'massif': nm, 'area_ha': rows[-1][1], 'irrigated_ha': rows[-1][2]}, 'geometry': ll(g)})
json.dump({'type': 'FeatureCollection', 'features': feats}, open('gis/massifs.geojson', 'w'), ensure_ascii=False)
json.dump({'type': 'FeatureCollection', 'features': [{'type': 'Feature', 'properties': {'name': 'Marhamat'}, 'geometry': ll(to_poly(district))}]}, open('gis/district.geojson', 'w'), ensure_ascii=False)
with open('data/massif_areas.csv', 'w', newline='', encoding='utf-8') as f:
    cw = csv.writer(f); cw.writerow(['massif', 'area_ha', 'irrigated_ha', 'settlement_ha', 'wells', 'wells_inside_own_polygon']); cw.writerows(rows)
print(pd.DataFrame(rows, columns=['massif', 'area_ha', 'irrigated_ha', 'settlement_ha', 'wells', 'inside']).to_string(index=False))
print('district ha', round(district.sum() * cell_ha), 'irrigated ha', round((district & ir).sum() * cell_ha), 'red barrier cells', int((rd & district).sum()))
# tekshiruv rasmi
fig, ax = plt.subplots(figsize=(8, 9)); show = np.ma.masked_where(own < 0, own); ax.imshow(show, cmap='tab10', alpha=.55)
ax.imshow(np.ma.masked_where(~rd, rd), cmap='autumn', alpha=1); cm = plt.get_cmap('tab10')
for k, nm in enumerate(names):
    w = Wl[Wl.massif == nm]; ax.scatter(w.c, w.r, s=10, color=cm(k / 9), edgecolor='k', lw=.4); rr, cc = np.nonzero(own == k); ax.text(cc.mean(), rr.mean(), nm, fontsize=8, ha='center', weight='bold')
r0, c0 = np.nonzero(district); ax.set_xlim(c0.min() - 20, c0.max() + 20); ax.set_ylim(r0.max() + 20, r0.min() - 20); ax.set_axis_off(); fig.savefig('figures/massifs.png', dpi=110, bbox_inches='tight')
