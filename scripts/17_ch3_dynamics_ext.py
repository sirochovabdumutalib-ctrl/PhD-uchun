"""3.2-§ kengaytirilgan: massivlar bo'yicha tendensiya, kesilgan qiymatlarga sezgirlik, quduqlar bo'yicha Sen qiyaligi xaritasi,
massivlar bo'yicha mavsumiy yo'l. Chiqish: results/ch3_dyn_ext.json, figures/ch3_trend_map.png, figures/ch3_season_massif.png"""
import re, json, numpy as np, pandas as pd, pymannkendall as mk, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
from pyproj import Transformer
warnings.filterwarnings('ignore')
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
EX = {2010, 2013, 2017}
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin(EX)].copy(); L['well'] = L.well_no.map(norm); L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
P = pd.read_csv('data/wells_passport.csv'); P['well'] = P.well_no.map(norm); P['depth'] = pd.to_numeric(P.depth_cm, errors='coerce') / 100
L = L.merge(P[['well', 'depth']].drop_duplicates('well'), on='well', how='left'); L['cens'] = L.depth.notna() & (L.level >= L.depth - 0.1)
M = pd.read_csv('data/wells_metrics.csv'); M['well'] = M.well_no.map(norm); mas = dict(zip(M.well, M.massif_map)); L['massif'] = L.well.map(mas)
yrs = sorted(L.year.unique()); everc = set(cst.well)
ann = L.groupby(['well', 'year'])['level'].mean().unstack(); annnc = L[~L.cens].groupby(['well', 'year'])['level'].mean().unstack()
panel = [w for w in ann.index if ann.loc[w, yrs].notna().all() and w not in everc]
R = {'panel': len(panel)}
def trend(s):
    t = mk.original_test(s.values); r = stats.linregress(s.index, s.values); return dict(tau=round(t.Tau, 3), p=round(t.p, 4), sen=round(stats.theilslopes(s.values, s.index)[0], 4), ols=round(r.slope, 4), r2=round(r.rvalue**2, 3), first=round(s.iloc[0], 2), last=round(s.iloc[-1], 2), pre=round(s[[y for y in s.index if y <= 2016]].mean(), 2), post=round(s[[y for y in s.index if y >= 2018]].mean(), 2))
R['district'] = trend(ann.loc[panel, yrs].mean())
pc = [w for w in panel if annnc.loc[w, yrs].notna().all()] if True else []
R['district_no_censored'] = trend(annnc.loc[panel, yrs].mean(skipna=True)); R['panel_cens_share'] = round(L[L.well.isin(panel)].cens.mean() * 100, 2)
R['massif'] = {}
for m in sorted(set(mas.values())):
    pw = [w for w in panel if mas.get(w) == m]
    if len(pw) >= 3: R['massif'][m] = dict(n=len(pw), **trend(ann.loc[pw, yrs].mean()))
    else: R['massif'][m] = dict(n=len(pw))
# per-well trends (wells with >=8 valid years)
rows = []
for w in ann.index:
    s = ann.loc[w].dropna()
    if len(s) >= 8:
        t = mk.original_test(s.values); rows.append(dict(well=w, n=len(s), sen=stats.theilslopes(s.values, s.index)[0], p=t.p, sig=t.h, massif=mas.get(w)))
T = pd.DataFrame(rows); T = T.merge(M[['well', 'x_utm43', 'y_utm43', 'dist_collector_m', 'level_2019_2024_m']], on='well', how='left')
R['wells_trend'] = dict(n=len(T), deep=int((T.sen > 0).sum()), shallow=int((T.sen < 0).sum()), sig_deep=int(((T.sen > 0) & T.sig).sum()), sig_shallow=int(((T.sen < 0) & T.sig).sum()),
                        sen_median=round(T.sen.median(), 4), sen_q25=round(T.sen.quantile(.25), 4), sen_q75=round(T.sen.quantile(.75), 4),
                        rho_sen_dist=[round(x, 3) for x in stats.spearmanr(T.sen, T.dist_collector_m, nan_policy='omit')], rho_sen_level=[round(x, 3) for x in stats.spearmanr(T.sen, T.level_2019_2024_m, nan_policy='omit')])
R['wells_trend_by_massif'] = T.groupby('massif').agg(n=('sen', 'size'), median_sen=('sen', 'median'), share_deep=('sen', lambda s: (s > 0).mean()), sig_deep=('sig', lambda s: int((s & (T.loc[s.index, 'sen'] > 0)).sum()))).round(3).reset_index().to_dict('records')
# seasonal by massif (panel wells)
S = L[L.well.isin(panel)].groupby(['massif', 'decade'])['level'].mean().unstack()
R['season_massif'] = {m: dict(amp=round(r.max() - r.min(), 2), deep_dec=int(r.idxmax()), shallow_dec=int(r.idxmin()), shallowest=round(r.min(), 2), deepest=round(r.max(), 2)) for m, r in S.iterrows()}
# interannual: wettest/driest years by panel summer mean
summ = L[L.well.isin(panel) & L.decade.between(19, 24)].groupby('year')['level'].mean(); R['summer_series'] = summ.round(2).to_dict(); R['summer_trend'] = trend(summ)
for a,b,k in [(2009,2016,'pre'),(2018,2024,'post')]:
    q = ann.loc[panel, [y for y in yrs if a <= y <= b]].mean(); t = mk.original_test(q.values); R['sub_'+k] = dict(sen=round(stats.theilslopes(q.values, q.index)[0], 4), p=round(t.p, 3))
json.dump(R, open('results/ch3_dyn_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
inv = Transformer.from_crs(32643, 4326, always_xy=True)
fig, ax = plt.subplots(figsize=(7.5, 8.5))
for f in json.load(open('gis/massifs.geojson'))['features']:
    from shapely.geometry import shape
    gg = shape(f['geometry']); tr = Transformer.from_crs(4326, 32643, always_xy=True)
    for p in ([gg] if gg.geom_type == 'Polygon' else gg.geoms):
        x, y = tr.transform(*p.exterior.xy); ax.plot(np.array(x) / 1000, np.array(y) / 1000, color='#999', lw=.8)
v = T.sen.clip(-0.15, 0.15); sc = ax.scatter(T.x_utm43 / 1000, T.y_utm43 / 1000, c=v, cmap='RdBu', vmin=-0.15, vmax=0.15, s=np.where(T.sig, 55, 22), edgecolor=np.where(T.sig, 'k', 'none'), lw=.6)
plt.colorbar(sc, ax=ax, shrink=.7, label='Sen qiyaligi, m/yil (musbat — chuqurlashish)'); ax.set_aspect(1); ax.set_xlabel('X, km'); ax.set_ylabel('Y, km'); ax.grid(alpha=.2)
fig.tight_layout(); fig.savefig('figures/ch3_trend_map.png', dpi=150)
fig, ax = plt.subplots(figsize=(9, 4)); lab = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': "M.To'jiboyev", 'Машъал': "Mash'al", 'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzayev', 'У.Қорабоев': 'U.Qoraboyev'}
for m, r in S.iterrows(): ax.plot(r.index, r.values, label=lab.get(m, m))
ax.invert_yaxis(); ax.set_xticks(range(2, 37, 3)); ax.set_xticklabels(['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']); ax.set_ylabel('Sizot suvi sathi, m'); ax.legend(fontsize=7, ncol=4); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('figures/ch3_season_massif.png', dpi=150)
print(json.dumps(R, ensure_ascii=False, default=str)[:3500])
# qo'shimcha: Hamed-Rao tuzatishi va Z.M.Bobur yillik qatori
hr = mk.hamed_rao_modification_test(ann.loc[panel, yrs].mean().values); print('HR', round(hr.p, 4))
zb = [w for w in panel if mas.get(w) == 'З.М.Бобур']; print('ZMB', ann.loc[zb, yrs].mean().round(2).to_dict())
