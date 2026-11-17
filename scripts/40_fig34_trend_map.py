"""3.4-rasm (3.2-§): sizot suvi sathi tendensiyasi.
a — quduqlar bo'yicha Sen qiyaligi (kamida 8 yil yaroqli ma'lumot, 17-skript bilan bir xil hisob), Mann–Kendall ahamiyatliligi;
b — massivlar bo'yicha barqaror panel tendensiyasi (3.3-jadval), markazi 0 bo'lgan ikki tomonlama shkala.
Chiqish: figures/fig34_trend_map.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
from scipy import stats
import pymannkendall as mk
import matplotlib as mpl
from matplotlib.patches import Patch

EX = {2010, 2013, 2017}
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin(EX)].copy(); L['well'] = L.well_no.map(nkey); L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
Mt = pd.read_csv('data/wells_metrics.csv'); Mt['well'] = Mt.well_no.map(nkey)
ann = L.groupby(['well', 'year'])['level'].mean().unstack(); rows = []
for w_ in ann.index:
    s = ann.loc[w_].dropna()
    if len(s) >= 8: rows.append(dict(well=w_, n=len(s), sen=stats.theilslopes(s.values, s.index)[0], sig=mk.original_test(s.values).h))
T = pd.DataFrame(rows).merge(Mt[['well', 'x_utm43', 'y_utm43']], on='well', how='left')
chk = dict(n=len(T), deep=int((T.sen > 0).sum()), shallow=int((T.sen < 0).sum()), sig_deep=int(((T.sen > 0) & T.sig).sum()), sig_shallow=int(((T.sen < 0) & T.sig).sum()), no_xy=int(T.x_utm43.isna().sum()))
print('3.2-§ bilan tekshiruv (122/86/36/54/9):', chk)
T = T.dropna(subset=['x_utm43'])
D = json.load(open('results/ch3_dyn_ext.json'))
MS = {MASSIF_LAT[k]: v for k, v in D['massif'].items()}
SH = {MASSIF_LAT[r['massif']]: r for r in D['wells_trend_by_massif']}

dist = load('district'); M = massifs()
FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.45; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg1.axis('off')
XY = T[['x_utm43', 'y_utm43']].values

# ---------- a) quduqlar (3.8-rasm b bilan bir xil kodlash)
RB = ['#b2182b', '#f7f7f7', '#92c5de', '#4393c3', '#2166ac']; MB = ['^', 'o', 'v', 'v', 'v']; SB = [18, 10, 12, 16, 22]
basemap(ax1, dist, M, pad=pad, network=True, label_fs=5.3, avoid_xy=XY)
tv = T.sen.values * 100; kt = np.digitize(tv, [-1, 1, 3, 6]); sig = T.sig.values.astype(bool)
for i in range(5):
    for sg in (False, True):
        m = (kt == i) & (sig == sg)
        if not m.any(): continue
        if sg: ax1.scatter(XY[m, 0], XY[m, 1], s=SB[i], marker=MB[i], c=RB[i], ec='#1a1a1a', lw=.45, zorder=12)
        else: ax1.scatter(XY[m, 0], XY[m, 1], s=SB[i], marker=MB[i], fc='white', ec=RB[i] if i != 1 else '#555', lw=.9, zorder=11)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
cnt = [int((kt == i).sum()) for i in range(5)]
h1 = [Line2D([], [], marker=MB[i], ls='', mfc=RB[i], mec='#1a1a1a', mew=.45, ms=np.sqrt(SB[i]) * 1.15, label=f'{l} ({cnt[i]})')
      for i, l in enumerate(['< −1 (koʻtarilish)', '−1…+1', '+1…+3', '+3…+6', '> +6 (chuqurlashish)'])]
h1 += [Line2D([], [], marker='v', ls='', mfc='white', mec='#4393c3', mew=.9, ms=4.4, label='Boʻsh belgi: p ≥ 0,05')]
legend_box(lg1, h1, title=f'Sen qiyaligi, sm/yil ({len(T)} ta quduq, ≥ 8 yil);\ntoʻldirilgan belgi: Mann–Kendall p < 0,05', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.4, borderaxespad=0, columnspacing=.8)

# ---------- b) massivlar (barqaror panel, 3.3-jadval)
norm = mpl.colors.TwoSlopeNorm(vmin=-4, vcenter=0, vmax=6); cmap = mpl.colormaps['RdBu']
basemap(ax2, dist, M, pad=pad, labels=False, network=False)
for _, r in M.iterrows():
    v = MS.get(r['name'], {})
    if 'sen' in v: gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc=mpl.colors.to_hex(cmap(norm(v['sen'] * 100))), ec='none', alpha=.95, zorder=1.5)
    else: gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='white', ec='#999', hatch='////', lw=0, zorder=1.5)
plot_lines(ax2, massif_lines(M, dist), color='#3a3a3a', lw=.7, zorder=3); ax2.set_xlabel(''); ax2.set_ylabel('')
for _, r in M.iterrows():
    v = MS.get(r['name'], {}); p = label_point(r.geometry, None, inset=700)
    if 'sen' in v:
        sh = SH.get(r['name'], {})
        pv = '< 0,001' if v['p'] < .001 else f"= {v['p']:.3f}".replace('.', ',')
        fmt = lambda x, f: format(x, f).replace('.', ',').replace('-', '−')
        t = f"{r['name']}\n{fmt(v['sen'] * 100, '+.1f')} sm/yil\nτ = {fmt(v['tau'], '.2f')}; p {pv}; n = {v['n']}"
    else: t = f"{r['name']}\npanel quduqlari yoʻq"
    label_halo(ax2.text(p.x, p.y, t, ha='center', va='center', fontsize=5.1, weight='bold', color='#1a1a1a', zorder=25, linespacing=1.1), 1.8)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
cax = add_axes_cm(fig, .35 + PW + .5 + .3, BM + 1.35, PW - .6, .22, FW, FH)
cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm, cmap=cmap), cax=cax, orientation='horizontal', ticks=[-4, -2, 0, 2, 4, 6])
cb.ax.set_xticklabels(['−4', '−2', '0', '+2', '+4', '+6']); cb.ax.tick_params(labelsize=5.4, length=1.5, width=.4); cb.outline.set_linewidth(.4)
cb.ax.set_title('Massiv boʻyicha Sen qiyaligi, sm/yil (barqaror panel, 3.3-jadval)', fontsize=5.8, weight='bold', pad=3)
fig.text((.35 + PW + .5 + .3) / FW, (BM + .98) / FH, '← sath koʻtarilmoqda', fontsize=5.2, color='#b2182b', va='top')
fig.text((.35 + 2 * PW + .5 - .3) / FW, (BM + .98) / FH, 'sath chuqurlashmoqda →', fontsize=5.2, color='#2166ac', va='top', ha='right')
fig.text((.35 + PW + .5 + .3) / FW, (BM + .62) / FH, 'Massiv yozuvida: Sen qiyaligi; Mann–Kendall τ va p; panel quduqlari soni (n).', fontsize=5.0, color='#333', va='top')
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Tekshirilgan oʻlchovlar (3.1-§): 2010, 2013, 2017-yillar va oʻzgarmas qatorlar chiqarilgan. Tendensiya yillik oʻrtachalar boʻyicha.'
         f'\n≥ 8 yillik qatorli {chk["n"]} ta quduqdan {chk["no_xy"]} tasining koordinatasi yoʻq (xaritada {len(T)} ta). Y.Oxunboboyev massivida barqaror panel shartiga mos quduq yoʻq. Asos: Copernicus GLO-30.', fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/fig34_trend_map', provenance={
    'raw_data': ['data/gw_levels_long.csv', 'data/wells_metrics.csv', 'results/ch3_dyn_ext.json (massif panel trends, table 3.3)', 'gis/*.geojson'],
    'transformations': ['QC as 3.1-§', 'per-well Sen slope on annual means, wells with >=8 years; Mann-Kendall', 'classes {<-1,-1..1,1..3,3..6,>6} cm/yr (same as fig 3.8b)',
                        'massif fill: panel Sen slope, TwoSlopeNorm(-4, 0, 6) cm/yr'], 'check_vs_text_3.2': chk},
    alt_text=f"""Ikki panelli xarita, Marhamat tumani. a — {len(T)} ta kuzatuv qudugʻi boʻyicha sizot suvi sathi tendensiyasi: koʻpchilik quduqlarda sath chuqurlashgan (koʻk, pastga
qaragan uchburchaklar), sath koʻtarilayotgan quduqlar (qizil uchburchaklar) asosan shimoldagi Z.M.Bobur massivida. b — massivlar boʻyicha barqaror panel tendensiyasi:
Z.M.Bobur yiliga −3,1 sm (koʻtarilish, qizil), qolgan massivlar +3,1…+5,3 sm/yil (chuqurlashish, koʻk); Y.Oxunboboyevda panel quduqlari yoʻq.""")
