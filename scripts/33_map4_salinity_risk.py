"""4-xarita (3.5-§): sho'rlanish xavfi — yozgi sizot suvi sathi va minerallashuvning birgalikdagi bahosi.
a — quduqlar: ikki o'zgaruvchili (3×3) rang shkalasi + xavf guruhi marker shakli bilan;
b — massivlar: xavfli quduqlar ulushi (yozgi sath < 2,0 m va minerallashuv ≥ 1 g/l).
Hisob 20_ch3_miner_ext.py bilan bir xil: minerallashuv — 2004–2010 medianasi, yozgi sath — wells_metrics.level_summer_m (2019–2024, iyul–avgust).
Chiqish: figures/map4_salinity_risk.{png,pdf}, results/map4_wells.csv"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
from matplotlib.patches import Patch, Rectangle

m = pd.read_csv('data/miner_1999_2015.csv'); m['well'] = m.well_no.map(nkey); m = m[m.year.between(2004, 2010)].dropna(subset=['miner_gl'])
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(nkey)
D = W.merge(m.groupby('well').miner_gl.median().rename('mmed'), left_on='well', right_index=True).dropna(subset=['level_summer_m']).copy()
D['massif'] = D.massif_map.map(MASSIF_LAT)
D['row'] = np.select([D.level_summer_m < 1.5, D.level_summer_m < 2.0], [2, 1], 0)        # 0: ≥2,0 m; 1: 1,5–2,0; 2: <1,5 (sayoz)
D['colm'] = np.select([D.mmed >= 3, D.mmed >= 1], [2, 1], 0)                               # 0: <1; 1: 1–3; 2: ≥3 g/l
D['risk'] = np.select([(D.level_summer_m < 1.5) & (D.mmed >= 1), (D.level_summer_m < 2.0) & (D.mmed >= 1)], [2, 1], 0)
D.to_csv('results/map4_wells.csv', index=False)
xt = pd.crosstab(D.row, D.colm).reindex(index=[0, 1, 2], columns=[0, 1, 2], fill_value=0)
print('n', len(D), 'xavfli', int((D.risk >= 1).sum()), 'juda xavfli', int((D.risk == 2).sum())); print(xt)

# J.Stevens 3×3 ikki o'zgaruvchili palitrasi: ustun — minerallashuv (qizilga), qator — sayoz sath (ko'kka)
BIV = [['#e8e8e8', '#e4acac', '#c85a5a'],
       ['#b0d5df', '#ad9ea5', '#985356'],
       ['#64acbe', '#627f8c', '#574249']]
MKR = {0: 'o', 1: 'D', 2: '^'}; MS = {0: 11, 1: 17, 2: 24}

dist = load('district'); M = massifs()
FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 3.0; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
XY = D[['x_utm43', 'y_utm43']].values

# ---------- a) quduqlar
basemap(ax1, dist, M, pad=pad, label_fs=5.3, avoid_xy=XY)
for rk in (0, 1, 2):
    q = D[D.risk == rk]
    ax1.scatter(q.x_utm43, q.y_utm43, s=MS[rk], marker=MKR[rk], c=[BIV[r][c] for r, c in zip(q.row, q.colm)], ec='#1a1a1a', lw=.45, zorder=10 + rk)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
# 3×3 legenda-matritsa (kataklarda quduqlar soni)
lm = add_axes_cm(fig, 1.6, BM + .5, 1.7, 1.7, FW, FH)
for r in range(3):
    for c in range(3):
        lm.add_patch(Rectangle((c, r), 1, 1, fc=BIV[r][c], ec='white', lw=1.2))
        n = int(xt.loc[r, c]); lm.text(c + .5, r + .5, str(n), ha='center', va='center', fontsize=5.8, color='white' if (r + c) >= 3 else '#222', weight='bold')
lm.set_xlim(0, 3); lm.set_ylim(0, 3); lm.set_aspect(1)
lm.set_xticks([0, 1, 2, 3]); lm.set_xticklabels(['0', '1', '3', ''], fontsize=5.2); lm.set_yticks([0, 1, 2, 3]); lm.set_yticklabels(['', '2,0', '1,5', '0'], fontsize=5.2)
lm.tick_params(length=1.5, width=.4, pad=1)
for sp in lm.spines.values(): sp.set_visible(False)
lm.set_xlabel('Minerallashuv, g/l →', fontsize=5.4, labelpad=1.5); lm.set_ylabel('Yozgi sath, m\n(sayozlashadi →)', fontsize=5.4, labelpad=1.5)
fig.text(.35 / FW, (BM + LH - .2) / FH, 'Sath va minerallashuv (kataklarda quduqlar soni)', fontsize=5.8, weight='bold', va='top')
lgs = add_axes_cm(fig, 4.15, BM + .3, 3.7, 2.2, FW, FH); lgs.axis('off')
hs = [Line2D([], [], marker='^', ls='', mfc='#985356', mec='#1a1a1a', mew=.45, ms=5.3, label=f'Juda yuqori xavf ({int((D.risk == 2).sum())}):\nsath < 1,5 m, ≥ 1 g/l'),
      Line2D([], [], marker='D', ls='', mfc='#ad9ea5', mec='#1a1a1a', mew=.45, ms=4.3, label=f'Yuqori xavf ({int((D.risk == 1).sum())}):\nsath 1,5–2,0 m, ≥ 1 g/l'),
      Line2D([], [], marker='o', ls='', mfc='#e8e8e8', mec='#1a1a1a', mew=.45, ms=3.6, label=f'Qolganlari ({int((D.risk == 0).sum())})')]
legend_box(lgs, hs, title='Xavf guruhi (shakl)', loc='upper left', bbox_to_anchor=(0, 1), fs=5.4, borderaxespad=0)

# ---------- b) massivlar
g = D.groupby('massif').agg(n=('well', 'size'), hi=('risk', lambda s: int((s >= 1).sum())), vh=('risk', lambda s: int((s == 2).sum())))
g['share'] = 100 * g.hi / g.n
Mb = M.merge(g, left_on='name', right_index=True, how='left')
bnd = [0, 20, 40, 60, 80, 101]; YOR = ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026']
basemap(ax2, dist, M, pad=pad, labels=False, network=False)
for _, r in Mb.iterrows():
    if np.isnan(r.share):
        gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='white', ec='none', hatch='////', alpha=.9, zorder=1.5)
        gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='none', ec='#999', hatch='////', lw=0, zorder=1.6)
    else:
        k = np.digitize(r.share, bnd[1:-1]); gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc=YOR[k], ec='none', alpha=.92, zorder=1.5)
plot_lines(ax2, massif_lines(M, dist), color='#4a4a4a', lw=.6, zorder=3)
ax2.set_xlabel(''); ax2.set_ylabel('')
for _, r in Mb.iterrows():
    p = label_point(r.geometry, None)
    t = r['name'] + ('\nmaʼlumot yoʻq' if np.isnan(r.share) else f'\n{int(r.hi)}/{int(r.n)} ({r.share:.0f} %)')
    label_halo(ax2.text(p.x, p.y, t, ha='center', va='center', fontsize=5.4, weight='bold', color='#222', zorder=25, linespacing=1.1), 2.0)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH); lg2.axis('off')
h2 = [Patch(fc=c, ec='#666', lw=.4, label=l) for c, l in zip(YOR, ['< 20', '20–40', '40–60', '60–80', '≥ 80'])]
h2 += [Patch(fc='white', ec='#999', hatch='////', lw=.4, label='Minerallashuv\nmaʼlumoti yoʻq')]
legend_box(lg2, h2, title='Xavfli quduqlar ulushi, %\n(yozgi sath < 2,0 m va ≥ 1 g/l)', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.5, borderaxespad=0)
lg2.text(0, .2, 'Massiv yozuvida: xavfli quduqlar / minerallashuvi\nva yozgi sathi maʼlum quduqlar (ulush).', fontsize=5.3, color='#333', transform=lg2.transAxes, va='top')
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Minerallashuv — 2004–2010-yillar medianasi (3.5-§ boʻyicha ishonchli davr); yozgi sath — 2019–2024-yillar, iyul–avgust. '
         f'\n{len(D)} ta quduq. Ikki oʻzgaruvchili rang shkalasi — J.Stevens (3×3). Sath va minerallashuv turli davrlarga tegishli (3.5-§ dagi cheklov). Asos: Copernicus GLO-30 relyef soyasi.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/map4_salinity_risk', provenance={
    'raw_data': ['data/miner_1999_2015.csv (2004-2010)', 'data/wells_metrics.csv (level_summer_m)', 'gis/massifs.geojson', 'gis/district.geojson', 'gis/dem/marhamat_dem30_utm43.tif'],
    'transformations': ['well median mineralization 2004-2010', 'bivariate classes: summer level {>=2.0, 1.5-2.0, <1.5} m x mineralization {<1, 1-3, >=3} g/l',
                        'risk: very high = level<1.5 & >=1 g/l; high = 1.5<=level<2.0 & >=1 g/l', 'massif share = high+very high / wells with both values'],
    'check_vs_table_3.9': {'matrix_rows_ge2_15to2_lt15_x_cols_lt1_1to3_ge3': xt.values.tolist(), 'high_total': int((D.risk >= 1).sum()), 'very_high': int((D.risk == 2).sum())},
    'caveat': 'level (2019-2024) and mineralization (2004-2010) refer to different periods', 'per_well_table': 'results/map4_wells.csv'},
    alt_text=f"""Ikki panelli xarita, Marhamat tumani. a — {len(D)} ta quduq ikki oʻzgaruvchili rang shkalasida: koʻk tus yozgi sathning sayozligini, qizil tus minerallashuvni bildiradi;
uchburchaklar — juda yuqori xavf ({int((D.risk == 2).sum())} ta), romblar — yuqori xavf ({int((D.risk == 1).sum())} ta). Xavfli quduqlar shimoliy va gʻarbiy qismda
(Z.M.Bobur, Mashʼal, Istiqlol) toʻplangan, sharqiy va janubiy massivlarda kam. b — massivlar boʻyicha xavfli quduqlar ulushi: Mashʼal va Z.M.Bobur 74–81 foiz,
Istiqlol 63 foiz, U.Qoraboyev va T.Mirzayevda 8–11 foiz; Y.Oxunboboyev boʻyicha minerallashuv maʼlumoti yoʻq.""")
print(g)
