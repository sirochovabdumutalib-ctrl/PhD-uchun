"""3-xarita (3.4-§): kollektorlardan masofa zonalari va sizot rejimi.
a — zonalar (0–150, 150–400, 400–800, >800 m) va quduqlar bo'yicha yozgi (iyul–avgust) sath, 2019–2024;
b — zonalar va quduqlar bo'yicha sath tendensiyasi (Sen qiyaligi, Mann–Kendall ahamiyatliligi bilan).
Hisob 19_ch3_network_ext.py bilan bir xil: tekshirilgan o'lchovlar, masofa gis/collectors.geojson bo'yicha (wells_metrics.dist_collector_m).
Chiqish: figures/map3_collector_zones.{png,pdf}, results/map3_wells.csv, results/map3_zones.json"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
from scipy import stats
import pymannkendall as mk
from shapely import unary_union

# ---------- ma'lumot (19-skript bilan bir xil filtrlar)
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(nkey)
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin({2010, 2013, 2017})].copy(); L['well'] = L.well_no.map(nkey)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index()
cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
Lr = L[L.year >= 2019]
W['summer'] = W.well.map(Lr[Lr.decade.between(19, 24)].groupby(['well', 'year'])['level'].mean().groupby('well').mean())  # 46-skript ta'rifi
ann = L.groupby(['well', 'year'])['level'].mean().unstack(); sen, pv = {}, {}
for w_ in ann.index:
    s = ann.loc[w_].dropna()
    if len(s) >= 8: sen[w_] = stats.theilslopes(s.values, s.index)[0]; pv[w_] = mk.original_test(s.values).p
W['sen'] = W.well.map(sen); W['p'] = W.well.map(pv)
D = W.dropna(subset=['level_2019_2024_m']).copy()
bins = [0, 150, 400, 800, 1e5]; lab = ['0–150', '150–400', '400–800', '> 800']
D['zone'] = pd.cut(D.dist_collector_m, bins, right=False, labels=range(4)).astype(int)
T = D.dropna(subset=['sen'])
chk = dict(summer=D.groupby('zone').summer.mean().round(2).tolist(), n=D.groupby('zone').size().tolist(),
           sen_med_cm=(T.groupby('zone').sen.median() * 100).round(1).tolist(), n_trend=T.groupby('zone').size().tolist())
print('3.6-jadval bilan tekshiruv:', chk)

# ---------- zonalar (buferlar), tuman ichida
dist = load('district'); M = massifs(); col = load('collectors')
net = unary_union(col.geometry.values); D0 = dist.geometry.iloc[0]
rings, prev = [], None
for b in [150, 400, 800]:
    bf = net.buffer(b, quad_segs=8).intersection(D0)
    rings.append(bf if prev is None else bf.difference(prev)); prev = bf
rings.append(D0.difference(prev))
area = np.array([r.area for r in rings]); share = 100 * area / D0.area
json.dump(dict(zones=lab, area_km2=(area / 1e6).round(1).tolist(), share_pct=share.round(1).tolist(), check=chk), open('results/map3_zones.json', 'w'), ensure_ascii=False, indent=1)
D[['well_no', 'massif_map', 'x_utm43', 'y_utm43', 'dist_collector_m', 'zone', 'summer', 'level_2019_2024_m', 'sen', 'p']].to_csv('results/map3_wells.csv', index=False)
print('zona maydonlari, %:', share.round(1), 'km2', (area / 1e6).round(1))

ZC = ['#9ecae1', '#c6dbef', '#e6eff8', None]  # yaqindan uzoqqa: to'qroq -> ochroq; > 800 m — fon (bo'yalmagan)

def zones(ax):
    for r, c in zip(rings, ZC):
        if c is None: continue
        gpd.GeoSeries([r], crs=CRS).plot(ax=ax, color=c, lw=0, zorder=1.5)
    plot_lines(ax, [r.boundary for r in rings[:3]], color='#6a8fb3', lw=.25, zorder=1.6)
    col.plot(ax=ax, color='#00442a', lw=.6, zorder=4)
    ax.set_xlabel(''); ax.set_ylabel('')

# ---------- maket
FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 3.05; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH)
for a in (lg1, lg2): a.axis('off')
XY = D[['x_utm43', 'y_utm43']].values
zone_h = [Patch(fc=c if c else '#f3f3f3', ec='#6a8fb3', lw=.4, label=f'{l} m ({s:.0f} %)'.replace('.', ',')) for c, l, s in zip(ZC, lab, share)] if False else None
from matplotlib.patches import Patch
zone_h = [Patch(fc=c if c else '#f3f3f3', ec='#6a8fb3', lw=.4, label=f'{l} m — {s:.0f} %') for c, l, s in zip(ZC, lab, share)]

# a) yozgi sath — sayoz = xavfli (YlOrRd teskari), marker shakli ikki karra kodlash
YOR = ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2']; MK_ = ['v', 'D', 's', 'o', 'o']; SZ = [22, 15, 14, 12, 9]
basemap(ax1, dist, M, pad=pad, network=False, label_fs=5.3, avoid_xy=XY)
zones(ax1)
k = np.digitize(D.summer.values, [1.5, 2.0, 2.5, 3.0]); ok = ~np.isnan(D.summer.values)
for i in range(4, -1, -1):
    m = ok & (k == i); ax1.scatter(XY[m, 0], XY[m, 1], s=SZ[i], marker=MK_[i], c=YOR[i], ec='#1a1a1a', lw=.4, zorder=10 + (5 - i))
nos = ~ok; ax1.scatter(XY[nos, 0], XY[nos, 1], s=8, marker='o', fc='white', ec='#777', lw=.5, zorder=9)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
h1 = [Line2D([], [], marker=MK_[i], ls='', mfc=YOR[i], mec='#1a1a1a', mew=.4, ms=np.sqrt(SZ[i]) * 1.15, label=l)
      for i, l in enumerate(['< 1,5', '1,5–2,0', '2,0–2,5', '2,5–3,0', '> 3,0'])]
h1 += [Line2D([], [], marker='o', ls='', mfc='white', mec='#777', mew=.5, ms=3.2, label=f'Yozgi oʻlchov yoʻq ({int(nos.sum())})')]
l1 = legend_box(lg1, h1, title='Yozgi sath (iyul–avgust,\n2019–2024), m', loc='upper left', bbox_to_anchor=(0, 1.0), ncol=2, fs=5.5, borderaxespad=0, columnspacing=.8)
legend_box(lg1, zone_h, title='Kollektorgacha masofa\n(tuman maydonidan ulushi)', loc='upper right', bbox_to_anchor=(1.0, 1.0), fs=5.5, borderaxespad=0)
lg1.add_artist(l1)

# b) tendensiya — diverging, markaz 0 (ko'tarilish / chuqurlashish); ahamiyatli — to'ldirilgan, ahamiyatsiz — bo'sh
RB = ['#b2182b', '#f7f7f7', '#92c5de', '#4393c3', '#2166ac']; MB = ['^', 'o', 'v', 'v', 'v']; SB = [16, 9, 11, 15, 21]
basemap(ax2, dist, M, pad=pad, network=False, label_fs=5.3, avoid_xy=XY)
zones(ax2)
tv = D.sen.values * 100; okt = ~np.isnan(tv); kt = np.digitize(np.nan_to_num(tv), [-1, 1, 3, 6]); sig = (D.p.values < .05)
for i in range(5):
    for sg in (False, True):
        m = okt & (kt == i) & (sig == sg)
        if not m.any(): continue
        if sg: ax2.scatter(XY[m, 0], XY[m, 1], s=SB[i], marker=MB[i], c=RB[i], ec='#1a1a1a', lw=.45, zorder=12)
        else: ax2.scatter(XY[m, 0], XY[m, 1], s=SB[i], marker=MB[i], fc='white', ec=RB[i] if i != 1 else '#555', lw=.9, zorder=11)
nt = ~okt; ax2.scatter(XY[nt, 0], XY[nt, 1], s=5, marker='.', c='#888', zorder=9)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
h2 = [Line2D([], [], marker=MB[i], ls='', mfc=RB[i], mec='#1a1a1a', mew=.45, ms=np.sqrt(SB[i]) * 1.15, label=l)
      for i, l in enumerate(['< −1 (koʻtarilish)', '−1…+1', '+1…+3', '+3…+6', '> +6 (chuqurlashish)'])]
h2 += [Line2D([], [], marker='v', ls='', mfc='white', mec='#4393c3', mew=.9, ms=4.4, label='Boʻsh belgi: p ≥ 0,05'),
       Line2D([], [], marker='.', ls='', c='#888', ms=4, label=f'Qator < 8 yil ({int(nt.sum())})')]
l2 = legend_box(lg2, h2, title='Sathning oʻzgarish tezligi (Sen qiyaligi),\nsm/yil; toʻldirilgan: p < 0,05', loc='upper left', bbox_to_anchor=(0, 1.0), ncol=1, fs=5.5, borderaxespad=0)
legend_box(lg2, zone_h, title='Kollektorgacha masofa\n(tuman maydonidan ulushi)', loc='upper right', bbox_to_anchor=(1.0, 1.0), fs=5.5, borderaxespad=0)
lg2.add_artist(l2)
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Zonalar — tumandagi barcha kollektor va zovurlardan bufer (2.3-§ qatlami); quduqgacha masofa shu qatlam boʻyicha. '
         f'\nTekshirilgan oʻlchovlar (3.1-§); oʻzgarish tezligi — yillik oʻrtachalar boʻyicha Sen qiyaligi, Mann–Kendall mezoni; {len(D)} ta quduq. Asos: Copernicus GLO-30 relyef soyasi.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/map3_collector_zones', provenance={
    'raw_data': ['data/gw_levels_long.csv', 'data/wells_metrics.csv', 'gis/collectors.geojson', 'gis/district.geojson', 'gis/massifs.geojson', 'gis/dem/marhamat_dem30_utm43.tif'],
    'transformations': ['same QC as 3.1-§ (excluded years 2010/2013/2017, constant well-years removed, cm->m)', 'summer = mean of decades 19-24 (Jul-Aug), 2019-2024',
                        'Sen slope on annual means, wells with >=8 years; Mann-Kendall p', 'zones = buffers 150/400/800 m around union of collector lines, clipped to district',
                        'classes a {<1.5,1.5-2,2-2.5,2.5-3,>3} m; b {<-1,-1..1,1..3,3..6,>6} cm/yr'],
    'check_vs_table_3.6': chk, 'missing_data': 'wells without summer values / <8 years shown with separate grey symbols',
    'per_well_table': 'results/map3_wells.csv'},
    alt_text=f"""Ikki panelli xarita, Marhamat tumani. Ikkala panelda kollektorlar atrofidagi masofa zonalari koʻk tuslarda: 0–150 m ({share[0]:.0f} %), 150–400 m ({share[1]:.0f} %),
400–800 m ({share[2]:.0f} %), 800 m dan uzoq ({share[3]:.0f} %, asosan janubdagi Y.Oxunboboyev massivi va tuman chekkalari). a — {len(D)} ta quduqda yozgi sath: 1,5 m dan sayoz
quduqlar (qizil uchburchaklar) kollektorlarga yaqin zonalarda, 3 m dan chuqurlari uzoq zonalarda. b — sath tendensiyasi: koʻpchilik quduqlarda sath chuqurlashgan
(koʻk pastga qaragan uchburchaklar), eng tez chuqurlashish kollektorlardan uzoq quduqlarda.""")
