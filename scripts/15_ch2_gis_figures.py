"""2.3-§ rasmlari: geoma'lumotlar bazasi umumiy xaritasi va xaritani bog'lash qoldiqlari."""
import json, numpy as np, pandas as pd, re, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from shapely.geometry import shape
from pyproj import Transformer
tr = Transformer.from_crs(4326, 32643, always_xy=True)
def lines(n):
    out = []
    for f in json.load(open(f'gis/{n}.geojson'))['features']:
        x, y = tr.transform(*zip(*f['geometry']['coordinates'])); out.append((np.array(x) / 1000, np.array(y) / 1000, f['properties']))
    return out
fig, ax = plt.subplots(figsize=(8, 9.5))
cols = ['#fde0b0', '#cfe8c4', '#d6e4f5', '#f5d6e8', '#e8e0f5', '#fff2b3', '#d9f0ec', '#f0d9c9']
lat = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': 'M.Tojiboyev', 'Машъал': "Mash'al", 'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzaev', 'У.Қорабоев': 'U.Qoraboyev'}
for i, f in enumerate(json.load(open('gis/massifs.geojson'))['features']):
    g = shape(f['geometry']); polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    for p in polys:
        x, y = tr.transform(*p.exterior.xy); ax.fill(np.array(x) / 1000, np.array(y) / 1000, color=cols[i], ec='#c0392b', lw=1.2, zorder=1)
    c = g.representative_point(); cx, cy = tr.transform(c.x, c.y); ax.text(cx / 1000, cy / 1000, lat[f['properties']['massif']], ha='center', fontsize=8, weight='bold', zorder=5)
for x, y, p in lines('canals'): ax.plot(x, y, color='#1f6fd1', lw=.9, zorder=2)
for x, y, p in lines('collectors_named'): ax.plot(x, y, color='#2e8b2e' if p.get('cad_name') else '#7fbf7f', lw=1.3 if p.get('cad_name') else .8, zorder=3)
W = json.load(open('gis/wells_2024.geojson'))['features']; wx, wy = tr.transform([f['geometry']['coordinates'][0] for f in W], [f['geometry']['coordinates'][1] for f in W])
ax.scatter(np.array(wx) / 1000, np.array(wy) / 1000, s=12, c='k', zorder=4)
from matplotlib.lines import Line2D
h = [Line2D([], [], color='#2e8b2e', lw=1.5, label='Kollektorlar (kadastr nomi biriktirilgan)'), Line2D([], [], color='#7fbf7f', lw=1, label='Kollektorlar (nomi aniqlanmagan)'),
     Line2D([], [], color='#1f6fd1', lw=1, label='Sug’orish kanallari'), Line2D([], [], color='#c0392b', lw=1.2, label='Massiv chegaralari'), Line2D([], [], marker='o', ls='', color='k', ms=4, label='Kuzatuv quduqlari')]
ax.legend(handles=h, loc='lower left', fontsize=8, framealpha=.9); ax.set_aspect(1); ax.set_xlabel('X, km (WGS 84 / UTM 43N)'); ax.set_ylabel('Y, km'); ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig('figures/ch2_gis_layers.png', dpi=150)
# qoldiqlar
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
M = pd.read_csv('data/wells_map_2024.csv').dropna(subset=['lon_table'])
a = np.array(tr.transform(M.lon_map.values, M.lat_map.values)).T; b = np.array(tr.transform(M.lon_table.values, M.lat_table.values)).T; r = np.linalg.norm(a - b, axis=1)
print('n', len(r), 'median', round(np.median(r), 1), 'q90', round(np.quantile(r, .9), 1), 'share<5', round((r < 5).mean(), 3), 'share<20', round((r < 20).mean(), 3), 'share>50', round((r > 50).mean(), 3), 'max', round(r.max(), 1))
fig, ax = plt.subplots(figsize=(7, 3.5)); ax.hist(np.clip(r, 0, 130), bins=np.arange(0, 135, 5), color='#4a6fa5', edgecolor='white'); ax.set_xlabel('Qoldiq: xaritadagi va jadvaldagi koordinatalar farqi, m'); ax.set_ylabel('Quduqlar soni'); ax.grid(alpha=.3)
ax.axvline(np.median(r), color='#c0392b', ls='--'); ax.text(np.median(r) + 2, ax.get_ylim()[1] * .9, f'mediana {np.median(r):.1f} m'.replace('.', ','), color='#c0392b', fontsize=9)
fig.tight_layout(); fig.savefig('figures/ch2_georef_residuals.png', dpi=150)
# kadastr va xarita uzunliklari
K = pd.read_csv('data/collector_name_match.csv'); K = K[K.map_length_km > 0]; rr = K.map_length_km / K.cad_length_km
print('named', len(K), 'ratio median', round(rr.median(), 2), 'within ±25%', int(((rr > .75) & (rr < 1.25)).sum()), 'map<50%', int((rr < .5).sum()), 'map>150%', int((rr > 1.5).sum()))
