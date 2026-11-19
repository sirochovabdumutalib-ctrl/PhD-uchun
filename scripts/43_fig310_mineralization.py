"""3.10-rasm (3.5-§): sizot suvlari minerallashuvi, 2004–2010-yillar (ishonchli davr).
a — quduqlar bo'yicha mediana (20-skript bilan bir xil: koordinatasi ma'lum 113 ta quduq); b — massivlar bo'yicha mediana (3.8-jadval).
Chiqish: figures/fig310_mineralization.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
from matplotlib.patches import Patch

m = pd.read_csv('data/miner_1999_2015.csv'); m['well'] = m.well_no.map(nkey); m = m[m.year.between(2004, 2010)].dropna(subset=['miner_gl'])
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(nkey)
D = W.merge(m.groupby('well').miner_gl.median().rename('mmed'), left_on='well', right_index=True, how='inner')
R = json.load(open('results/ch3_miner_ext.json'))
G = {MASSIF_LAT[d['massif']]: d for d in R['massif']}
chk = dict(n=len(D), lt1=int((D.mmed < 1).sum()), b13=int(((D.mmed >= 1) & (D.mmed < 3)).sum()), ge3=int((D.mmed >= 3).sum()))
print('20-skript bilan tekshiruv (113: 27/82/4):', chk)
BND = [1.0, 1.5, 2.0, 3.0]; LAB = ['< 1,0 (chuchuk)', '1,0–1,5', '1,5–2,0', '2,0–3,0', '≥ 3,0']
COL = ['#ffffd4', '#fed98e', '#fe9929', '#d95f0e', '#993404']; MK = ['o', 'o', 's', 'D', '^']; SZ = [10, 12, 13, 15, 22]
k = np.digitize(D.mmed.values, BND)

dist = load('district'); M = massifs()
FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.1; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH)
for a in (lg1, lg2): a.axis('off')
XY = D[['x_utm43', 'y_utm43']].values
# a) quduqlar
basemap(ax1, dist, M, pad=pad, network=True, label_fs=5.3, avoid_xy=XY)
for i in range(5):
    q = k == i; ax1.scatter(XY[q, 0], XY[q, 1], s=SZ[i], marker=MK[i], c=COL[i], ec='#1a1a1a', lw=.45, zorder=10 + i)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
h1 = [Line2D([], [], marker=MK[i], ls='', mfc=COL[i], mec='#1a1a1a', mew=.45, ms=np.sqrt(SZ[i]) * 1.15, label=f'{LAB[i]} ({int((k == i).sum())})') for i in range(5)]
legend_box(lg1, h1, title=f'Quduq boʻyicha minerallashuv medianasi, g/l\n(2004–2010; {len(D)} ta quduq)', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.5, borderaxespad=0, columnspacing=.8)
# b) massivlar
basemap(ax2, dist, M, pad=pad, labels=False, network=False)
for _, r in M.iterrows():
    g = G.get(r['name'])
    if g: gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc=COL[int(np.digitize(g['med'], BND))], ec='none', alpha=.95, zorder=1.5)
    else: gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='white', ec='#999', hatch='////', lw=0, zorder=1.5)
plot_lines(ax2, massif_lines(M, dist), color='#3a3a3a', lw=.7, zorder=3); ax2.set_xlabel(''); ax2.set_ylabel('')
for _, r in M.iterrows():
    g = G.get(r['name']); p = label_point(r.geometry, None, inset=700)
    t = f"{r['name']}\n" + (f"{g['med']:.2f} g/l".replace('.', ',') + f"\n≥ 3 g/l: {g['sh3']} %; n = {g['n']}" if g else 'oʻlchanmagan')
    label_halo(ax2.text(p.x, p.y, t, ha='center', va='center', fontsize=5.1, weight='bold', color='#1a1a1a', zorder=25, linespacing=1.1), 1.9)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
h2 = [Patch(fc=COL[i], ec='#666', lw=.4, label=LAB[i]) for i in range(5)] + [Patch(fc='white', ec='#999', hatch='////', lw=.4, label='2004–2010-yillarda\noʻlchanmagan')]
legend_box(lg2, h2, title='Massiv boʻyicha mediana, g/l (37-ilova)', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.5, borderaxespad=0, columnspacing=.8)
lg2.text(0, .02, 'Massiv yozuvida: mediana; 3 g/l dan yuqori quduqlar ulushi; quduqlar soni.', fontsize=5.1, color='#333', transform=lg2.transAxes)
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Minerallashuv — 1-aprel, 1-iyul va 1-oktabr holatiga oʻlchovlar; 2004–2010-yillar ishonchli davr deb topilgan (3.5-§, 20-ilova).'
         '\nSinflar: < 1 g/l — chuchuk, 1–3 g/l — kam minerallashgan, ≥ 3 g/l — oʻrtacha minerallashgan suv [17]. Asos: Copernicus GLO-30 relyef soyasi.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/fig310_mineralization', provenance={
    'raw_data': ['data/miner_1999_2015.csv (2004-2010)', 'data/wells_metrics.csv', 'results/ch3_miner_ext.json (massif medians, table 3.8)', 'gis/*.geojson'],
    'transformations': ['well median of all 2004-2010 values', 'classes <1, 1-1.5, 1.5-2, 2-3, >=3 g/l'], 'check_vs_script20': chk},
    alt_text=f"""Ikki panelli xarita. a — {len(D)} ta kuzatuv qudugʻi boʻyicha 2004–2010-yillardagi sizot suvi minerallashuvi medianasi: chuchuk suv (1 g/l dan kam) asosan sharq va janubda
(U.Qoraboyev, M.Toʻjiboyev, T.Mirzayev), minerallashganroq suv gʻarb va shimolda (Mashʼal, Z.M.Bobur). b — massivlar boʻyicha mediana: Mashʼal 2,47, Z.M.Bobur 1,41,
Paxtakor 1,40, Istiqlol 1,22, M.Toʻjiboyev 1,03, U.Qoraboyev 0,84, T.Mirzayev 0,80 g/l; Y.Oxunboboyevda oʻlchanmagan.""")
