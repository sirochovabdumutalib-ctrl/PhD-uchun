"""2.3-rasm (2.3-§): tiklangan geoma'lumotlar bazasining tuzilishi — qatlamlar to'plami (haqiqiy geometriya, qiya proyeksiyada)
va har bir qatlamning atributlari hamda tashqi jadvallar bilan bog'lanish kalitlari. Chiqish: figures/fig23_gis_layers.{png,pdf}"""
import os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
from matplotlib.patches import Polygon as MP, FancyArrowPatch
from shapely import contains_xy

dist = load('district'); M = massifs(); can = load('canals'); col = load('collectors_named'); W = load('wells_2024')
x0, y0, x1, y1 = dist.total_bounds; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; S = max(x1 - x0, y1 - y0)
SH, SY = .5, .3          # qiya proyeksiya: x' = x + SH*y, y' = SY*y (+ qatlam siljishi)
def P(x, y, k):
    u = (np.asarray(x) - cx) / S; v = (np.asarray(y) - cy) / S
    return u + SH * v, SY * v + k * DY
DY = .40
LAY = ['dem', 'district', 'massifs', 'canals', 'collectors', 'wells']  # pastdan yuqoriga
FW, FH = 16.0, 15.6
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax = add_axes_cm(fig, .1, .55, 9.3, FH - .75, FW, FH); ax.axis('off')
plate = np.array([[-.58, -.58], [.58, -.58], [.58, .58], [-.58, .58]])

def draw_plate(k, fc):
    u, v = P(cx + plate[:, 0] * S, cy + plate[:, 1] * S, k)
    ax.add_patch(MP(np.c_[u, v], closed=True, fc=fc, ec='#555', lw=.6, alpha=.93, zorder=k * 10))
    return u, v

def lines(geoms, k, **kw):
    for g in geoms:
        for part in getattr(g, 'geoms', [g]):
            xs, ys = part.xy; u, v = P(xs, ys, k); ax.plot(u, v, zorder=k * 10 + 2, solid_capstyle='round', **kw)

def polys(gdf, k, colors, **kw):
    for (_, r), c in zip(gdf.iterrows(), colors):
        for part in getattr(r.geometry, 'geoms', [r.geometry]):
            u, v = P(*part.exterior.xy, k); ax.add_patch(MP(np.c_[u, v], closed=True, fc=c, zorder=k * 10 + 1, **kw))

# 0) DEM (raster)
k = 0; draw_plate(k, '#f4f4f4')
z, gx, gy, ext = dem(); st = 6
zz, xx, yy = z[::st, ::st], gx[::st, ::st], gy[::st, ::st]
ins = contains_xy(dist.geometry.iloc[0].buffer(2500), xx, yy)
import matplotlib.colors as mcolors
cmap = mcolors.LinearSegmentedColormap.from_list('h', ['#a9cf9a', '#ece9b5', '#ddb383', '#b58a80'])
u, v = P(xx[ins], yy[ins], k)
ax.scatter(u, v, c=zz[ins], cmap=cmap, vmin=500, vmax=1000, s=1.2, marker='s', lw=0, zorder=k * 10 + 1)
# 1) tuman chegarasi
k = 1; draw_plate(k, '#ffffff'); lines([dist.geometry.iloc[0].exterior], k, color=C['boundary'], lw=1.3)
# 2) massivlar
k = 2; draw_plate(k, '#ffffff')
mcol = ['#fde0b0', '#cfe8c4', '#d6e4f5', '#f5d6e8', '#e8e0f5', '#fff2b3', '#d9f0ec', '#f0d9c9']
polys(M, k, mcol, ec='#555', lw=.4)
# 3) kanallar
k = 3; draw_plate(k, '#ffffff'); lines([dist.geometry.iloc[0].exterior], k, color='#bbbbbb', lw=.5); lines(can.geometry, k, color=C['canal'], lw=.6)
# 4) kollektorlar
k = 4; draw_plate(k, '#ffffff'); lines([dist.geometry.iloc[0].exterior], k, color='#bbbbbb', lw=.5)
lines(col[col.cad_name.isna()].geometry, k, color='#7fae9a', lw=.5); lines(col[col.cad_name.notna()].geometry, k, color=C['collector'], lw=1.0)
# 5) quduqlar
k = 5; draw_plate(k, '#ffffff'); lines([dist.geometry.iloc[0].exterior], k, color='#bbbbbb', lw=.5)
u, v = P(W.geometry.x, W.geometry.y, k); ax.scatter(u, v, s=3.5, fc='white', ec='#111', lw=.4, zorder=k * 10 + 2)
for cxp, cyp in plate:          # qatlamlar bir koordinata tizimida ekanini ko'rsatuvchi burchak chiziqlari
    u0, v0 = P(cx + cxp * S, cy + cyp * S, 0); u5, v5 = P(cx + cxp * S, cy + cyp * S, 5)
    ax.plot([u0, u5], [v0, v5], color='#9a9a9a', lw=.4, ls=(0, (3, 2)), zorder=-1)
ax.set_xlim(-.9, .9); ax.set_ylim(-.22, 5 * DY + .22); ax.set_aspect(1)

# ---------- o'ng tomonda: qatlamlar tavsifi
TXT = {
 5: ('Kuzatuv quduqlari', 'nuqta · 202 ta', 'quduq raqami; sath va minerallashuv (2024-04-01);\npasport; kollektor/kanalgacha masofa; 1 km radiusdagi\nkollektorlar uzunligi; 2009–2024 tekshirilgan oʻrtacha sath'),
 4: ('Kollektorlar', 'chiziq · 332 boʻlak · 214,6 km', 'boʻlak uzunligi; kadastrdagi nomi (130 boʻlak,\n60 kollektor); foydalanishga topshirilgan va\noxirgi taʼmir yili'),
 3: ('Sugʻorish kanallari', 'chiziq · 426 boʻlak · 170,9 km', 'boʻlak uzunligi'),
 2: ('Massivlar', 'poligon · 8 ta', 'nomi; umumiy va sugʻoriladigan maydon'),
 1: ('Tuman chegarasi', 'poligon · 1 ta', '329 km² (xarita boʻyicha)'),
 0: ('Relyef modeli (qoʻshimcha)', 'raster · 30 m', 'Copernicus GLO-30, UTM 43N ga\nqayta proyeksiyalangan'),
}
tx = add_axes_cm(fig, 9.55, .55, FW - 9.7, FH - .75, FW, FH); tx.axis('off'); tx.set_xlim(0, 1); tx.set_ylim(*ax.get_ylim())
for k, (t, g, a) in TXT.items():
    yy_ = k * DY + .1
    tx.text(0, yy_, t, fontsize=7.2, weight='bold', va='bottom')
    tx.text(0, yy_ - .012, g, fontsize=6, color='#7a1f1f', va='top')
    tx.text(0, yy_ - .065, a, fontsize=5.6, color='#333', va='top', linespacing=1.2)
fig.text(.1 / FW, .12 / FH, 'Barcha vektor qatlamlar GeoJSON formatida, WGS 84 da saqlanadi; hisoblar WGS 84 / UTM 43N da bajariladi. Monitoring jadvallari (2009–2024) qatlamga quduq raqami, '
         '\nmeliorativ kadastr (2021) kollektor nomi orqali bogʻlanadi (2.3-§). Qatlamlar haqiqiy geometriya boʻyicha, qiya proyeksiyada (masshtabsiz) koʻrsatilgan.', fontsize=5.2, color='#555', va='bottom')
rep = export(fig, 'figures/fig23_gis_layers', provenance={
    'raw_data': ['gis/district.geojson', 'gis/massifs.geojson', 'gis/canals.geojson', 'gis/collectors_named.geojson', 'gis/wells_2024.geojson', 'gis/dem/marhamat_dem30_utm43.tif'],
    'transformations': ['UTM 43N, then schematic oblique transform x+0.55y, 0.42y per layer (no scale)', 'DEM subsampled every 6th cell for display'],
    'counts': {'wells': len(W), 'collector_segments': len(col), 'collectors_km': round(col.length.sum() / 1e3, 1), 'canal_segments': len(can), 'canals_km': round(can.length.sum() / 1e3, 1)}},
    alt_text="""Geomaʼlumotlar bazasining tuzilishi: oltita qatlam bir-birining ustida qiya tekisliklarda koʻrsatilgan. Pastdan yuqoriga: relyef modeli (Copernicus GLO-30, 30 m),
tuman chegarasi, sakkizta massiv, sugʻorish kanallari (426 boʻlak, 170,9 km), kollektorlar (332 boʻlak, 214,6 km; 60 tasiga kadastr nomi biriktirilgan) va
202 ta kuzatuv qudugʻi. Har bir qatlam yonida geometriya turi, obyektlar soni va atributlari yozilgan.""")
