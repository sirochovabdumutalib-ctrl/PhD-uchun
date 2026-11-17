"""2-xarita (3.1-§): monitoring ma'lumotlari ishonchliligining fazoviy taqsimoti.
a — quduqlar bo'yicha yaroqli o'lchovlar ulushi (2009–2024, mustaqil kuzatuvsiz yillar chiqarilgan);
b — quduq chuqurligining zaxirasi: pasportdagi chuqurlik bilan 2019–2024-yillardagi o'rtacha sath orasidagi farq.
Chiqish: figures/map2_data_quality.png, results/map2_wells.csv"""
import os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib.colors as mcolors

EXCL = {2010, 2013, 2017}
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin(EXCL)].copy(); L['well'] = L.well_no.map(nkey)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); g['const'] = (g['nunique'] == 1) & (g['count'] > 6)
L = L.merge(g[['year', 'well', 'const']], on=['year', 'well'])
w = L.groupby('well').agg(n=('level', 'size'), yrs=('year', 'nunique'), valid=('const', lambda s: 100 * (1 - s.mean())),
                          const_years=('const', lambda s: 0)).reset_index()
w['const_years'] = w.well.map(g[g.const].groupby('well').year.nunique()).fillna(0).astype(int)
lv = L[(~L.const) & (L.year >= 2019)].groupby('well')['level'].mean(); w['level_19_24'] = w.well.map(lv)
P = pd.read_csv('data/wells_passport.csv'); P['well'] = P.well_no.map(nkey); P['depth_m'] = pd.to_numeric(P.depth_cm, errors='coerce') / 100
w = w.merge(P[['well', 'depth_m']].drop_duplicates('well'), on='well', how='left'); w['margin'] = w.depth_m - w.level_19_24
# koordinatalar: wells_metrics (UTM) + wells_coords (WGS 84)
Mt = pd.read_csv('data/wells_metrics.csv'); Mt['well'] = Mt.well_no.map(nkey)
xy = Mt[['well', 'x_utm43', 'y_utm43']].drop_duplicates('well')
Cc = pd.read_csv('data/wells_coords.csv'); Cc['well'] = Cc.well_no.map(nkey); Cc = Cc[~Cc.well.isin(xy.well)].drop_duplicates('well')
cx, cy = TO_UTM.transform(Cc.lon.values, Cc.lat.values); xy = pd.concat([xy, pd.DataFrame(dict(well=Cc.well, x_utm43=cx, y_utm43=cy))])
w = w.merge(xy, on='well', how='inner')
dist = load('district'); M = massifs()
from shapely import contains_xy
w = w[contains_xy(dist.geometry.iloc[0].buffer(300), w.x_utm43.values, w.y_utm43.values)]
w['massif'] = None
for _, r in M.iterrows(): w.loc[contains_xy(r.geometry.buffer(150), w.x_utm43.values, w.y_utm43.values) & w.massif.isna(), 'massif'] = r['name']
w.to_csv('results/map2_wells.csv', index=False)
bym = w.groupby('massif').agg(valid=('valid', 'mean'), margin=('margin', 'median'), n=('well', 'size'))
# massiv bo'yicha yaroqli o'lchovlar ulushi 3.1-§ dagi rasmiy hisobdan (o'lchovlar soni bo'yicha) olinadi
import json
R = json.load(open('results/ch3_audit_ext.json'))
vm = {MASSIF_LAT.get(d['massif'], d['massif']): d['valid_share'] for d in R['by_massif']}

FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.25; BM = .55
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .35, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .35, FW, FH)
for a in (lg1, lg2): a.axis('off')

# a) yaroqli o'lchovlar ulushi
basemap(ax1, dist, M, pad=pad, massif_text={k: f'{k}\n{str(round(v)).replace(".", ",")} %' for k, v in vm.items()}, label_fs=5.3)
b1 = [0, 50, 75, 90, 99.9, 100.01]; c1 = ['#b2182b', '#ef8a62', '#fddbc7', '#92c5de', '#2166ac']
lab1 = ['< 50', '50–75', '75–90', '90–99,9', '100']
cls = np.digitize(w.valid.values, b1[1:-1], right=False)
cls = np.where(w.valid.values >= 99.9, 4, np.digitize(w.valid.values, [50, 75, 90]))
order = np.argsort(-cls)
ax1.scatter(w.x_utm43.values[order], w.y_utm43.values[order], s=13, c=[c1[i] for i in cls[order]], ec='#222', lw=.35, zorder=10)
dry = w[w.const_years >= 3]
ax1.scatter(dry.x_utm43, dry.y_utm43, s=46, fc='none', ec='#111', lw=.7, zorder=11)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
h1 = [Line2D([], [], marker='o', ls='', mfc=c, mec='#222', mew=.35, ms=4.2, label=l) for c, l in zip(c1, lab1)]
h1 += [Line2D([], [], marker='o', ls='', mfc='none', mec='#111', mew=.7, ms=7, label='≥ 3 yil oʻzgarmas qator')]
legend_box(lg1, h1, title='Yaroqli oʻlchovlar ulushi, %', loc='upper left', bbox_to_anchor=(0, 1.0), ncol=2, fs=5.6, borderaxespad=0, columnspacing=1.0)

# b) quduq chuqurligining zaxirasi
basemap(ax2, dist, M, pad=pad, label_fs=5.3,
        massif_text={k: f'{k}\n{str(round(v, 1)).replace(".", ",")} m' for k, v in bym.margin.dropna().items()})
b2 = [-10, .5, 1.0, 1.5, 2.0, 20]; c2 = ['#7f0000', '#d7301f', '#fc8d59', '#fdd49e', '#fff7ec'][::1]
c2 = ['#99000d', '#e34a33', '#fdae6b', '#c7e9c0', '#41ab5d']
lab2 = ['< 0,5', '0,5–1,0', '1,0–1,5', '1,5–2,0', '> 2,0']
ww = w.dropna(subset=['margin']); k2 = np.digitize(ww.margin.values, b2[1:-1])
o2 = np.argsort(-k2)
ax2.scatter(ww.x_utm43.values[o2], ww.y_utm43.values[o2], s=13, c=[c2[i] for i in k2[o2]], ec='#222', lw=.35, zorder=10)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
h2 = [Line2D([], [], marker='o', ls='', mfc=c, mec='#222', mew=.35, ms=4.2, label=l) for c, l in zip(c2, lab2)]
legend_box(lg2, h2, title='Quduq tubigacha zaxira, m\n(chuqurlik − 2019–2024-yillar oʻrtacha sathi)', loc='upper left', bbox_to_anchor=(0, 1.0), ncol=2, fs=5.6, borderaxespad=0, columnspacing=1.0)
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Massiv yozuvlarida: a — yaroqli oʻlchovlar ulushi (3.1-§), b — zaxira medianasi. '
         '\nKuzatuv davri 2009–2024 (mustaqil kuzatuvsiz yillar chiqarilgan); koordinatasi aniqlangan 188 ta quduq. Asos: Copernicus GLO-30 relyef soyasi.', fontsize=5.0, color='#555', ha='left', va='bottom')
fig.savefig('figures/map2_data_quality.png', dpi=300)
from scipy.stats import spearmanr
m = w.dropna(subset=['margin'])
print('quduqlar', len(w), 'zaxira bor', len(m), 'yaroqli<75%:', int((w.valid < 75).sum()), '≥3 yil o‘zgarmas:', len(dry))
print('Spearman valid~margin', spearmanr(m.valid, m.margin))
print('zaxira <1 m:', int((m.margin < 1).sum()), 'ulardan yaroqli<75%:', int(((m.margin < 1) & (m.valid < 75)).sum()))
print(bym.round(2))
