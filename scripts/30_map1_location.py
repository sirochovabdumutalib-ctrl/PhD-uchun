"""1-xarita (2.1-§): tadqiqot hududining joylashuvi.
a — Markaziy Osiyo; b — Andijon viloyati tumanlari; c — Marhamat tumani: relyef (Copernicus GLO-30), massivlar,
kollektor-drenaj tarmog'i, sug'orish kanallari va kuzatuv quduqlari. Chiqish: figures/map1_location.png"""
import os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib.colors as mcolors
from scipy.ndimage import gaussian_filter
from shapely import contains_xy

dist = load('district'); M = massifs(); col = load('collectors_named'); can = load('canals'); W = load('wells_2024')
ADM = 'gis/admin/'
adm2 = gpd.read_file(ADM + 'UZB_ADM2.geojson'); adm1 = gpd.read_file(ADM + 'UZB_ADM1.geojson')
reg = adm1[adm1.shapeName == 'Andijan Region']
adm2['rp'] = adm2.representative_point(); andi = adm2[adm2.rp.within(reg.geometry.iloc[0])].drop(columns='rp')
UZ = {'Andijan': 'Andijon', 'Ulugnar': 'Ulugʻnor', 'Khadjaabad': 'Xoʻjaobod', 'Markhamat': 'Marhamat', 'Asaka': 'Asaka', 'Shakhrixan': 'Shahrixon',
      'Boz': 'Boʻz', 'Djalalkuduk': 'Jalaquduq', 'Bulakbashi': 'Buloqboshi', 'Kurgantepa': 'Qoʻrgʻontepa', 'Balikchi': 'Baliqchi',
      'Altinkul': 'Oltinkoʻl', 'Izboskan': 'Izboskan', 'Paxtaabad': 'Paxtaobod'}

# ---------- sahifa joylashuvi (sm)
x0, y0, x1, y1 = dist.total_bounds; pad = 1000
mx0, my0, mx1, my1 = x0 - pad, y0 - pad, x1 + pad, y1 + pad
FW = 16.0; MW = 10.3; MH = MW * (my1 - my0) / (mx1 - mx0); RX = 0.55 + MW + 0.35; RW = FW - RX - 0.15
BM = 1.25; FH = MH + BM + .15
fig = plt.figure(figsize=(cm(FW), cm(FH)))
axc = add_axes_cm(fig, .55, BM, MW, MH, FW, FH)
LAEA = '+proj=laea +lat_0=41 +lon_0=66 +datum=WGS84 +units=m'
A_EXT = (-1.02e6, -.62e6, 1.08e6, .78e6); AH = RW * (A_EXT[3] - A_EXT[1]) / (A_EXT[2] - A_EXT[0])
rg = reg.to_crs(CRS); bx = rg.total_bounds; pb = 5000; B_EXT = (bx[0] - pb, bx[1] - pb, bx[2] + pb, bx[3] + pb)
BH = RW * (B_EXT[3] - B_EXT[1]) / (B_EXT[2] - B_EXT[0])
top = BM + MH
axa = add_axes_cm(fig, RX, top - AH, RW, AH, FW, FH)
axb = add_axes_cm(fig, RX, top - AH - .45 - BH, RW, BH, FW, FH)
axl = add_axes_cm(fig, RX, BM, RW, top - AH - .45 - BH - .45 - BM, FW, FH); axl.axis('off')

# ---------- a) Markaziy Osiyo
TL = Transformer.from_crs(4326, LAEA, always_xy=True)
cty = {c: gpd.read_file(f'{ADM}{c}_ADM0.geojson').to_crs(LAEA) for c in ['UZB', 'KAZ', 'KGZ', 'TJK', 'TKM', 'AFG']}
for c, g in cty.items():
    g.plot(ax=axa, fc='#f6e7c8' if c == 'UZB' else '#e9e9e9', ec='#4a4a4a' if c == 'UZB' else '#a0a0a0', lw=.6 if c == 'UZB' else .35, zorder=2 if c == 'UZB' else 1)
reg.to_crs(LAEA).plot(ax=axa, fc='#c0392b', ec='#7a1f1f', lw=.4, zorder=3)
frame(axa, A_EXT); axa.set_facecolor('#dce8f2')
for t, lo, la, fw in [('OʻZBEKISTON', 63.6, 41.9, 'bold'), ('QOZOGʻISTON', 66.5, 44.7, 'normal'), ('QIRGʻIZISTON', 74.6, 41.95, 'normal'),
                      ('TOJIKISTON', 71.2, 38.6, 'normal'), ('TURKMANISTON', 59.4, 38.85, 'normal'), ('AFGʻONISTON', 67.0, 36.35, 'normal')]:
    x, y = TL.transform(lo, la); label_halo(axa.text(x, y, t, ha='center', va='center', fontsize=5.0, weight=fw, color='#333', zorder=5), 1.4)
ax_, ay_ = TL.transform(72.3, 40.75)
axa.annotate('Andijon viloyati', (ax_, ay_), xytext=(ax_ - 2.6e5, ay_ + 2.9e5), fontsize=5.0, ha='center', color='#7a1f1f', weight='bold',
             arrowprops=dict(arrowstyle='-', lw=.5, color='#7a1f1f', shrinkA=0, shrinkB=1), zorder=6)
axa.text(.035, .95, 'a', transform=axa.transAxes, fontsize=9, weight='bold', va='top')

# ---------- b) Andijon viloyati
a2 = andi.to_crs(CRS)
nb = adm1[adm1.shapeName.isin(['Namangan Region', 'Fergana Region'])].to_crs(CRS); kg = cty['KGZ'].to_crs(CRS)
kg.plot(ax=axb, fc='#e9e9e9', ec='#a0a0a0', lw=.35); nb.plot(ax=axb, fc='#f5f1e8', ec='#a0a0a0', lw=.35)
a2.plot(ax=axb, fc='#f6e7c8', ec='#9b8866', lw=.35)
a2[a2.shapeName == 'Markhamat'].plot(ax=axb, fc='#c0392b', ec='#7a1f1f', lw=.5)
rg.boundary.plot(ax=axb, color='#333', lw=.8)
frame(axb, B_EXT); axb.set_facecolor('#e9e9e9')
for _, r in a2.iterrows():
    n = UZ.get(r.shapeName)
    if n is None or n == 'Marhamat': continue
    p = r.geometry.representative_point()
    if n in ('Xoʻjaobod', 'Boʻz'): continue
    dx, dy = {'Qoʻrgʻontepa': (-5500, 0), 'Shahrixon': (1500, -1200)}.get(n, (0, 0))
    label_halo(axb.text(p.x + dx, p.y + dy, n, ha='center', va='center', fontsize=4.3, color='#333', zorder=6), 1.1)
mp = a2[a2.shapeName == 'Markhamat'].geometry.iloc[0].representative_point()
axb.annotate('Marhamat', (mp.x, mp.y), xytext=(mp.x - 30000, mp.y - 14000), fontsize=5.2, weight='bold', color='#7a1f1f', ha='center', va='center',
             arrowprops=dict(arrowstyle='-', lw=.5, color='#7a1f1f', shrinkA=1, shrinkB=0), zorder=7)
for t, lo, la in [('QIRGʻIZISTON', 73.0, 40.36), ('Namangan v.', 71.85, 41.02)]:
    x, y = TO_UTM.transform(lo, la)
    if B_EXT[0] < x < B_EXT[2] and B_EXT[1] < y < B_EXT[3]: axb.text(x, y, t, ha='center', fontsize=4.4, color='#666', style='italic', zorder=6)
scale_bar(axb, 20, x=.62, y=.06, segs=2, fs=4.6, h_frac=.03)
axb.text(.035, .95, 'b', transform=axb.transAxes, fontsize=9, weight='bold', va='top')

# ---------- c) Marhamat tumani
z, gx, gy, ext = dem()
inside = contains_xy(dist.geometry.union_all(), gx, gy)
hs = hillshade(z, 30, zf=2.5)
levels = [500, 525, 550, 575, 600, 625, 650, 700, 800, 900, 1000, 1300]
cols = ['#a9cf9a', '#c3dca4', '#dbe6b0', '#ece9b5', '#f0dca2', '#e9c992', '#ddb383', '#d4a982', '#c99c80', '#bf9283', '#b58a80']
cmap = mcolors.ListedColormap(cols); norm = mcolors.BoundaryNorm(levels, cmap.N)
rgb = cmap(norm(z))[..., :3]
shade = rgb * (.55 + .45 * hs[..., None])
outside = np.dstack([np.full_like(z, .93)] * 3) * (.80 + .20 * hs[..., None])
img = np.where(inside[..., None], shade, outside)
axc.imshow(img, extent=ext, origin='upper', interpolation='bilinear', zorder=1)
zs = gaussian_filter(z, 2.0)
cs = axc.contour(gx, gy, np.where(inside, zs, np.nan), levels=[525, 550, 575, 600, 625, 650, 700, 800, 900, 1000, 1100, 1200],
                 colors='#7d5b3e', linewidths=.3, alpha=.8, zorder=2)
cl = axc.clabel(cs, fontsize=4.4, fmt='%d', inline=True, inline_spacing=1)
for t in cl: t.set_color('#5e4430'); label_halo(t, 1.0)
plot_lines(axc, massif_lines(M, dist), color='#3d3d3d', lw=.65, ls=(0, (5, 2.2)), zorder=4)
can.plot(ax=axc, color='white', lw=1.35, alpha=.9, zorder=5)
can.plot(ax=axc, color=C['canal'], lw=.7, zorder=5)
named = col[col.cad_name.notna()]; other = col[col.cad_name.isna()]
other.plot(ax=axc, color=C['collector'], lw=.5, alpha=.9, zorder=6); named.plot(ax=axc, color=C['collector'], lw=1.2, zorder=6)
axc.scatter(W.geometry.x, W.geometry.y, s=6, marker='o', fc='white', ec=C['well'], lw=.5, zorder=8)
dist.boundary.plot(ax=axc, color='white', lw=2.6, alpha=.85, zorder=9)
dist.boundary.plot(ax=axc, color=C['boundary'], lw=1.5, zorder=9)
frame(axc, (mx0, my0, mx1, my1))
off = {'Y.Oxunboboyev': (0, 2500), 'M.Toʻjiboyev': (600, 0)}
for _, r in M.iterrows():
    p = r.geometry.representative_point(); dx, dy = off.get(r['name'], (0, 0))
    label_halo(axc.text(p.x + dx, p.y + dy, r['name'], ha='center', va='center', fontsize=6.4, weight='bold', color='#222', zorder=12), 2.2)
from shapely.geometry import box as _box
_ext = _box(mx0, my0, mx1, my1); _d = dist.geometry.iloc[0].buffer(600)
nbrs = [(UZ.get(r.shapeName, r.shapeName) + ' t.', r.geometry) for _, r in a2.iterrows() if r.shapeName != 'Markhamat']
label_halo(axc.text(mx1 - 1300, my0 + .42 * (my1 - my0), 'QIRGʻIZISTON', rotation=90, ha='center', va='center', fontsize=6, color='#555', style='italic', weight='bold', zorder=12), 1.6)
for t, g in nbrs:
    part = g.intersection(_ext).difference(_d)
    if part.is_empty or part.area < 6e6: continue
    p = part.representative_point()
    label_halo(axc.text(p.x, p.y, t, ha='center', va='center', fontsize=5.4 if t[0].isupper() and t.isupper() else 5.2,
                        color='#555', style='italic', weight='bold' if t.isupper() else 'normal', zorder=12), 1.6)
graticule(axc, step_min=5, fs=6)
north_arrow(axc, x=.945, y=.035, size=.065); scale_bar(axc, 5, x=.05, y=.035, segs=5)
axc.text(.022, .985, 'c', transform=axc.transAxes, fontsize=10, weight='bold', va='top')

# ---------- shartli belgilar
h = [Line2D([], [], color=C['boundary'], lw=1.5, label='Tuman chegarasi'),
     Line2D([], [], color='#3d3d3d', lw=.7, ls=(0, (5, 2.2)), label='Massivlar chegarasi'),
     Line2D([], [], color=C['collector'], lw=1.2, label='Kollektorlar (kadastr\nnomi biriktirilgan)'),
     Line2D([], [], color=C['collector'], lw=.55, label='Boshqa kollektor\nva zovurlar'),
     Line2D([], [], color=C['canal'], lw=.8, label='Sugʻorish kanallari'),
     Line2D([], [], marker='o', ls='', mfc='white', mec='k', mew=.55, ms=3.2, label='Kuzatuv quduqlari'),
     Line2D([], [], color='#7d5b3e', lw=.4, label='Gorizontallar, m')]
legend_box(axl, h, title='Shartli belgilar', loc='upper left', bbox_to_anchor=(0, 1.0), fs=5.6, borderaxespad=0)
cax = axl.inset_axes([.03, .02, .94, .05])
cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal', ticks=[500, 550, 600, 650, 700, 900, 1300], spacing='uniform')
cb.ax.set_title('Mutlaq balandlik, m', fontsize=5.8, pad=2); cb.ax.tick_params(labelsize=4.8, length=1.5, width=.4, pad=1); cb.outline.set_linewidth(.4)
fig.text(.55 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Manbalar: tiklangan geomaʼlumotlar bazasi (2.3-§); relyef — Copernicus GLO-30 DEM (© ESA/DLR), soyasi vertikal 2,5 marta boʻrttirilgan;\n'
         'maʼmuriy chegaralar (a, b) — geoBoundaries (CC BY 4.0).', fontsize=5.2, color='#555', ha='left', va='bottom', linespacing=1.25)
rep = export(fig, 'figures/map1_location', provenance={
    'raw_data': ['gis/district.geojson', 'gis/massifs.geojson', 'gis/collectors_named.geojson', 'gis/canals.geojson', 'gis/wells_2024.geojson',
                 'gis/dem/marhamat_dem30_utm43.tif (Copernicus GLO-30, N40E072)', 'gis/admin/*.geojson (geoBoundaries gbOpen, simplified)'],
    'transformations': ['WGS 84 -> UTM 43N (EPSG:32643)', 'DEM bilinear resampling to 30 m', 'hillshade az=315 alt=45, vertical exaggeration 2.5',
                        'contours from DEM smoothed with Gaussian sigma=2 px', 'hypsometric classes 500-1300 m (BoundaryNorm)'],
    'missing_data': 'none; DEM has no voids inside district', 'uncertainty': 'DEM vs well passport marks: median -1.1 m, MAD 5.6 m (n=172)'},
    alt_text="""Uch panelli xarita. a — Markaziy Osiyo: Oʻzbekiston och sariq, Andijon viloyati qizil bilan ajratilgan. b — Andijon viloyati tumanlari, Marhamat tumani qizil.
c — Marhamat tumani: relyef 504 m (shimol) dan 1276 m (janub) gacha, gipsometrik ranglar va relyef soyasi bilan; sakkizta massiv chegarasi va nomi,
kollektorlar (toʻq yashil), sugʻorish kanallari (koʻk), 202 ta kuzatuv qudugʻi (oq doiralar), gorizontallar. Kollektor-drenaj tarmogʻi va quduqlar
shimoliy va markaziy tekis qismda zich, janubdagi Y.Oxunboboyev massivi togʻ oldi qiyaligida joylashgan.""")
print('export:', [f.get('path') for f in rep.get('files', [])] if isinstance(rep, dict) else rep)
zi = z[inside]; print('DEM tuman ichida: min', round(float(np.nanmin(zi))), 'max', round(float(np.nanmax(zi))), 'median', round(float(np.nanmedian(zi))))
