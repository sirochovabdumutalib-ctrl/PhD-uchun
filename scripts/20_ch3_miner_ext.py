"""3.5-§ kengaytirilgan: minerallashuv (2004-2010 ishonchli davr) sinflari, tendensiyalar, mavsumiy farq, sath va tarmoq bilan bog'liqlik,
sho'rlanish xavfi matritsasi, yillik manba tekshiruvi. Chiqish: results/ch3_miner_ext.json, figures/ch3_miner.png"""
import re, json, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
from pyproj import Transformer
import pymannkendall as mk
warnings.filterwarnings('ignore'); tr = Transformer.from_crs(4326, 32643, always_xy=True)
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
R = {}
m = pd.read_csv('data/miner_1999_2015.csv'); m['well'] = m.well_no.map(norm); m = m[m.year.between(2004, 2010)].dropna(subset=['miner_gl'])
m['t'] = m.year + m.season.map({'apr': 0.25, 'jul': 0.5, 'oct': 0.75})
R['n'] = dict(obs=len(m), wells=int(m.well.nunique()))
cls = lambda s: pd.cut(s, [0, 1, 3, 5, 100], right=False, labels=['<1', '1-3', '3-5', '>=5'])
R['classes_by_year'] = {int(y): {k: round(v * 100, 1) for k, v in cls(q.miner_gl).value_counts(normalize=True).sort_index().items()} for y, q in m.groupby('year')}
R['classes_all'] = {k: round(v * 100, 1) for k, v in cls(m.miner_gl).value_counts(normalize=True).sort_index().items()}
med = m.groupby('year').miner_gl.median(); t = mk.original_test(med.values); R['district'] = dict(medians=med.round(2).to_dict(), tau=round(t.Tau, 3), p=round(t.p, 3), sen=round(stats.theilslopes(med.values, med.index)[0], 3))
R['season'] = m.groupby('season').miner_gl.median().round(2).to_dict()
# paired seasonal differences per well-year
pv = m.pivot_table(index=['well', 'year'], columns='season', values='miner_gl').dropna()
R['season_paired'] = dict(n=len(pv), jul_minus_apr=round((pv.jul - pv.apr).median(), 3), p1=round(stats.wilcoxon(pv.jul, pv.apr).pvalue, 4), oct_minus_jul=round((pv.oct - pv.jul).median(), 3), p2=round(stats.wilcoxon(pv.oct, pv.jul).pvalue, 4),
                        share_up_jul=round(((pv.jul - pv.apr) > 0).mean(), 2))
# per-well trends
rows = []
for w, q in m.groupby('well'):
    q = q.sort_values('t')
    if len(q) >= 12:
        r = mk.original_test(q.miner_gl.values); rows.append(dict(well=w, n=len(q), sen=stats.theilslopes(q.miner_gl.values, q.t.values)[0], sig=r.h, med=q.miner_gl.median(), cv=q.miner_gl.std() / q.miner_gl.mean()))
T = pd.DataFrame(rows); R['wells_trend'] = dict(n=len(T), up=int((T.sen > 0).sum()), down=int((T.sen < 0).sum()), sig_up=int(((T.sen > 0) & T.sig).sum()), sig_down=int(((T.sen < 0) & T.sig).sum()),
                                                 sen_med=round(T.sen.median(), 3), cv_med=round(T.cv.median(), 2))
# well medians joined with metrics
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm)
wm = m.groupby('well').miner_gl.median().rename('mmed'); D = W.merge(wm, left_on='well', right_index=True, how='inner')
R['join'] = len(D)
R['massif'] = [dict(massif=k, n=len(q), med=round(q.mmed.median(), 2), sh3=round((q.mmed >= 3).mean() * 100), lvl=round(q.level_2009_2016_m.mean(), 2)) for k, q in D.groupby('massif_map')]
R['massif_season'] = {k: q.groupby('season').miner_gl.median().round(2).to_dict() for k, q in m.merge(W[['well', 'massif_map']], on='well').groupby('massif_map')}
for k in ('level_2009_2016_m', 'level_summer_m', 'dist_collector_m', 'collector_len_1km_m', 'dist_canal_m'):
    q = D.dropna(subset=[k]); R['rho_' + k] = [round(x, 3) for x in stats.spearmanr(q[k], q.mmed)] + [len(q)]
# risk matrix: summer level 2019-2024 x mineralization 2004-2010
Q = D.dropna(subset=['level_summer_m']).copy()
Q['lc'] = pd.cut(Q.level_summer_m, [0, 1.5, 2.0, 3.0, 100], right=False, labels=['<1,5', '1,5-2,0', '2,0-3,0', '>=3,0']); Q['mc'] = pd.cut(Q.mmed, [0, 1, 3, 100], right=False, labels=['<1', '1-3', '>=3'])
R['risk_matrix'] = pd.crosstab(Q.lc, Q.mc).astype(int).to_dict(); R['risk_n'] = len(Q)
Q['high'] = (Q.level_summer_m < 2.0) & (Q.mmed >= 1); Q['very'] = (Q.level_summer_m < 1.5) & (Q.mmed >= 1)
R['risk_massif'] = [dict(massif=k, n=len(q), high=int(q.high.sum()), very=int(q.very.sum())) for k, q in Q.groupby('massif_map')]
R['risk_total'] = dict(high=int(Q.high.sum()), very=int(Q.very.sum()))
# annual source audit 2009-2024
a = pd.read_csv('data/gw_annual.csv'); a = a.dropna(subset=['miner_gl'])
R['annual_audit'] = {int(y): dict(n=len(q), med=round(q.miner_gl.median(), 2), q25=round(q.miner_gl.quantile(.25), 2), q75=round(q.miner_gl.quantile(.75), 2), uniq=int(q.miner_gl.nunique())) for y, q in a.groupby('year')}
# figure
mas = json.load(open('gis/massifs.geojson'))['features']
fig, ax = plt.subplots(1, 2, figsize=(12, 5.4), gridspec_kw=dict(width_ratios=[1.1, 1]))
for f in mas:
    g = f['geometry']; polys = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    for p in polys:
        x, y = tr.transform(*zip(*p[0])); ax[0].plot(np.array(x) / 1000, np.array(y) / 1000, color='#666', lw=.7)
colors = {'<1': '#4393c3', '1-3': '#fdb863', '3-5': '#e66101', '>=5': '#8b0000'}; D['c'] = cls(D.mmed).astype(str)
for k, c in colors.items():
    q = D[D.c == k]; ax[0].scatter(q.x_utm43 / 1000, q.y_utm43 / 1000, s=28, c=c, edgecolor='k', lw=.4, label=f'{k} g/l ({len(q)})'.replace('>=', '≥'))
ax[0].set_aspect(1); ax[0].legend(fontsize=8, title='Minerallashuv medianasi', title_fontsize=8); ax[0].set_xlabel('X, km (UTM 43N)'); ax[0].set_ylabel('Y, km'); ax[0].set_title('a', loc='left')
order = D.groupby('massif_map').mmed.median().sort_values().index.tolist(); lat = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': "M.To'jiboyev", 'Машъал': "Mash'al", 'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzaev', 'У.Қорабоев': 'U.Qoraboyev'}
ax[1].boxplot([D[D.massif_map == k].mmed for k in order], vert=False, tick_labels=[lat[k] for k in order], showfliers=True); ax[1].axvline(3, color='r', ls=':'); ax[1].axvline(1, color='#4393c3', ls=':')
ax[1].set_xlabel('Quduq bo\'yicha minerallashuv medianasi, g/l (2004–2010)'); ax[1].grid(alpha=.3, axis='x'); ax[1].set_title('b', loc='left')
fig.tight_layout(); fig.savefig('figures/ch3_miner.png', dpi=150)
json.dump(R, open('results/ch3_miner_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
