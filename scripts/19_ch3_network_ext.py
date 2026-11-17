"""3.4-§ kengaytirilgan: kollektor xususiyatlari (yoshi, drenaj moduli), massiv ichidagi bog'lanish (qat'iy effektlar),
mavsumiy ko'tarilishning kollektorgacha masofaga bog'liqligi, bo'linma regressiya (ta'sir radiusi), tendensiya va tarmoq.
Chiqish: results/ch3_net_ext.json, figures/ch3_network.png"""
import re, json, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
from pyproj import Transformer
import statsmodels.formula.api as smf, pymannkendall as mk
warnings.filterwarnings('ignore')
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
tr = Transformer.from_crs(4326, 32643, always_xy=True); R = {}
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm)
# --- cleaned decade levels 2019-2024 -> winter (Jan-Feb), summer (Jul-Aug), amplitude ---
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin({2010, 2013, 2017})].copy(); L['well'] = L.well_no.map(norm)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
P = pd.read_csv('data/wells_passport.csv'); P['well'] = P.well_no.map(norm); P['depth'] = pd.to_numeric(P.depth_cm, errors='coerce') / 100
L = L.merge(P[['well', 'depth']].drop_duplicates('well'), on='well', how='left'); L['cens'] = L.depth.notna() & (L.level >= L.depth - 0.1)
Lr = L[L.year >= 2019]
# yagona ta'rif (46-skript): avval yil ichida, keyin yillar bo'yicha o'rtacha
win = Lr[Lr.decade.between(1, 6)].groupby(['well', 'year'])['level'].mean().groupby('well').mean(); sumr = Lr[Lr.decade.between(19, 24)].groupby(['well', 'year'])['level'].mean().groupby('well').mean()
cshare = Lr.groupby('well').cens.mean()
W['winter'] = W.well.map(win); W['summer'] = W.well.map(sumr); W['amp'] = W.winter - W.summer; W['cens_share'] = W.well.map(cshare)
# per-well Sen (years)
ann = L.groupby(['well', 'year'])['level'].mean().unstack(); sen = {}
for w in ann.index:
    s = ann.loc[w].dropna()
    if len(s) >= 8: sen[w] = stats.theilslopes(s.values, s.index)[0]
W['sen'] = W.well.map(sen)
# --- nearest named collector attributes ---
CL = pd.read_csv('data/collectors.csv'); CL['name_n'] = CL.name.str.strip(); CL['modulus'] = CL.q_end_m3s * 1000 / CL.service_ha; CL['spec_len'] = CL.length_km * 1000 / CL.service_ha
CL['age'] = 2024 - CL.commissioned; Cd = CL.set_index('name_n')
segs = []
for f in json.load(open('gis/collectors_named.geojson'))['features']:
    nm = f['properties']['cad_name']
    if not nm: continue
    x, y = tr.transform(*zip(*f['geometry']['coordinates'])); segs.append((nm.strip(), np.c_[x, y]))
def dseg(p, a, b):
    ab = b - a; t = np.clip(((p - a) * ab).sum(-1) / np.maximum((ab * ab).sum(-1), 1e-9), 0, 1); return np.hypot(*(a + t[:, None] * ab - p).T)
near = []
for _, r in W.iterrows():
    p = np.array([r.x_utm43, r.y_utm43]); best = (1e9, None)
    for nm, xy in segs:
        d = dseg(p, xy[:-1], xy[1:]).min()
        if d < best[0]: best = (d, nm)
    near.append(best)
W['dist_named'] = [d for d, _ in near]; W['near_name'] = [n for _, n in near]
for k in ('age', 'modulus', 'spec_len', 'q_end_m3s', 'service_ha', 'repair_year'): W['c_' + k] = W.near_name.map(lambda n: Cd[k].get(n, np.nan) if n in Cd.index else np.nan)
D = W.dropna(subset=['level_2019_2024_m']).copy(); D['ldist'] = np.log10(D.dist_collector_m + 10); D['dens'] = D.collector_len_1km_m / 1000; D['lcan'] = np.log10(D.dist_canal_m + 10)
R['n'] = len(D); R['named_match'] = int((D.dist_named < 500).sum())
# 1) within-massif: fixed effects
m_pool = smf.ols('level_2019_2024_m ~ dens', D).fit(cov_type='HC3'); m_fe = smf.ols('level_2019_2024_m ~ dens + C(massif_map)', D).fit(cov_type='HC3')
m_pool_d = smf.ols('level_2019_2024_m ~ ldist', D).fit(cov_type='HC3'); m_fe_d = smf.ols('level_2019_2024_m ~ ldist + C(massif_map)', D).fit(cov_type='HC3')
m_massif = smf.ols('level_2019_2024_m ~ C(massif_map)', D).fit()
R['fe'] = dict(dens_pool=[round(m_pool.params.dens, 3), round(m_pool.pvalues.dens, 4), round(m_pool.rsquared, 3)], dens_fe=[round(m_fe.params.dens, 3), round(m_fe.pvalues.dens, 4), round(m_fe.rsquared, 3)],
               ldist_pool=[round(m_pool_d.params.ldist, 3), round(m_pool_d.pvalues.ldist, 4), round(m_pool_d.rsquared, 3)], ldist_fe=[round(m_fe_d.params.ldist, 3), round(m_fe_d.pvalues.ldist, 4), round(m_fe_d.rsquared, 3)],
               r2_massif_only=round(m_massif.rsquared, 3))
# within-massif Spearman
R['within'] = {m: dict(n=len(q), rho_dist=round(stats.spearmanr(q.dist_collector_m, q.level_2019_2024_m)[0], 2), p=round(stats.spearmanr(q.dist_collector_m, q.level_2019_2024_m)[1], 3))
               for m, q in D.groupby('massif_map') if len(q) >= 10}
# 2) seasonal: summer, winter, amplitude vs distance
A = D.dropna(subset=['amp', 'winter', 'summer']).copy(); bins = [0, 150, 400, 800, 1e5]; A['bin'] = pd.cut(A.dist_collector_m, bins, right=False)
R['season_by_dist'] = [dict(bin=str(b), n=len(q), winter=round(q.winter.mean(), 2), summer=round(q.summer.mean(), 2), amp=round(q.amp.mean(), 2), amp_med=round(q.amp.median(), 2),
                            sh15_summer=round((q.summer < 1.5).mean(), 2), cens=round(q.cens_share.mean() * 100, 1)) for b, q in A.groupby('bin')]
R['season_rho'] = {k: [round(x, 3) for x in stats.spearmanr(A.dist_collector_m, A[k])] for k in ('winter', 'summer', 'amp')}
R['season_rho_dens'] = {k: [round(x, 3) for x in stats.spearmanr(A.collector_len_1km_m, A[k])] for k in ('winter', 'summer', 'amp')}
m_amp = smf.ols('amp ~ ldist + winter', A).fit(cov_type='HC3'); R['amp_model'] = {k: [round(m_amp.params[k], 3), round(m_amp.pvalues[k], 4)] for k in m_amp.params.index}; R['amp_model']['r2'] = round(m_amp.rsquared, 3)
# summer capped at shallow: share of wells whose summer level < 1.0 m
R['summer_lt1'] = int((A.summer < 1.0).sum())
# 3) segmented regression level ~ distance (breakpoint search)
best = None; xx = D.dist_collector_m.values; yy = D.level_2019_2024_m.values
for bp in range(100, 1501, 25):
    X = np.c_[np.ones_like(xx), np.minimum(xx, bp), np.maximum(xx - bp, 0)]; b, res, *_ = np.linalg.lstsq(X, yy, rcond=None); sse = ((yy - X @ b) ** 2).sum()
    if best is None or sse < best[0]: best = (sse, bp, b)
sse0 = ((yy - np.polyval(np.polyfit(xx, yy, 1), xx)) ** 2).sum(); n = len(yy); F = ((sse0 - best[0]) / 2) / (best[0] / (n - 4))
# bootstrap breakpoint CI
rng = np.random.default_rng(1); bps = []
for _ in range(500):
    i = rng.integers(0, n, n); xb, yb = xx[i], yy[i]; bb = None
    for bp in range(100, 1501, 25):
        X = np.c_[np.ones_like(xb), np.minimum(xb, bp), np.maximum(xb - bp, 0)]; b = np.linalg.lstsq(X, yb, rcond=None)[0]; s = ((yb - X @ b) ** 2).sum()
        if bb is None or s < bb[0]: bb = (s, bp)
    bps.append(bb[1])
R['segmented'] = dict(bp=best[1], slope1_per100=round(best[2][1] * 100, 3), slope2_per100=round(best[2][2] * 100, 3), F=round(F, 2), p=round(1 - stats.f.cdf(F, 2, n - 4), 4),
                      ci=[int(np.percentile(bps, 5)), int(np.percentile(bps, 95))])
# 4) collector attributes (wells within 500 m of a named collector)
N = D[(D.dist_named < 500)].copy()
R['coll_attr'] = dict(n=len(N), n_coll=int(N.near_name.nunique()),
                      rho_age=[round(x, 3) for x in stats.spearmanr(N.c_age, N.level_2019_2024_m)], rho_mod=[round(x, 3) for x in stats.spearmanr(N.c_modulus, N.level_2019_2024_m)],
                      rho_spec=[round(x, 3) for x in stats.spearmanr(N.c_spec_len, N.level_2019_2024_m)], rho_svc=[round(x, 3) for x in stats.spearmanr(N.c_service_ha, N.level_2019_2024_m)],
                      mod_q=[round(x, 3) for x in N.drop_duplicates('near_name').c_modulus.quantile([.25, .5, .75])],
                      age_q=[int(x) for x in N.drop_duplicates('near_name').c_age.quantile([.25, .5, .75])])
N['age_grp'] = pd.cut(N.c_age, [0, 55, 65, 200], labels=['<55', '55-65', '>65'])
R['by_age'] = [dict(grp=str(k), n=len(q), n_coll=int(q.near_name.nunique()), level=round(q.level_2019_2024_m.mean(), 2), summer=round(q.summer.mean(), 2)) for k, q in N.groupby('age_grp')]
N['mod_grp'] = pd.qcut(N.c_modulus, 3, labels=['past', "o'rta", 'yuqori'])
R['by_mod'] = [dict(grp=str(k), n=len(q), lo=round(q.c_modulus.min(), 3), hi=round(q.c_modulus.max(), 3), level=round(q.level_2019_2024_m.mean(), 2), summer=round(q.summer.mean(), 2)) for k, q in N.groupby('mod_grp')]
mN = smf.ols('level_2019_2024_m ~ ldist + np.log10(c_modulus) + c_age', N).fit(cov_type='HC3'); R['coll_model'] = {k: [round(mN.params[k], 4), round(mN.pvalues[k], 4)] for k in mN.params.index}; R['coll_model']['r2'] = round(mN.rsquared, 3)
# 5) trend vs network
T = D.dropna(subset=['sen']); R['trend_net'] = dict(n=len(T), rho_dist=[round(x, 3) for x in stats.spearmanr(T.dist_collector_m, T.sen)], rho_dens=[round(x, 3) for x in stats.spearmanr(T.collector_len_1km_m, T.sen)])
T['bin'] = pd.cut(T.dist_collector_m, bins, right=False)
R['trend_by_dist'] = [dict(bin=str(b), n=len(q), sen_med=round(q.sen.median(), 4), share_deep=round((q.sen > 0).mean(), 2)) for b, q in T.groupby('bin')]
mt = smf.ols('sen ~ ldist + C(massif_map)', T).fit(cov_type='HC3'); R['trend_fe'] = [round(mt.params.ldist, 4), round(mt.pvalues.ldist, 4)]
# figure
fig, ax = plt.subplots(1, 3, figsize=(14, 4.2))
ax[0].scatter(D.dist_collector_m, D.level_2019_2024_m, s=12, c='#1f5fa8', alpha=.7); xs = np.linspace(0, xx.max(), 200); b = best[2]
ax[0].plot(xs, b[0] + b[1] * np.minimum(xs, best[1]) + b[2] * np.maximum(xs - best[1], 0), 'r-', lw=2); ax[0].axvline(best[1], color='r', ls=':')
ax[0].invert_yaxis(); ax[0].set_xlabel('Kollektorgacha masofa, m'); ax[0].set_ylabel('Sath, 2019–2024 o\'rtacha, m'); ax[0].grid(alpha=.3); ax[0].set_title('a', loc='left')
sb = pd.DataFrame(R['season_by_dist']); lab = ['0–150', '150–400', '400–800', '>800']; xi = np.arange(4)
ax[1].bar(xi - .2, sb.winter, .4, color='#9ecae1', label='Yanvar–fevral'); ax[1].bar(xi + .2, sb.summer, .4, color='#1f5fa8', label='Iyul–avgust')
ax[1].set_xticks(xi); ax[1].set_xticklabels(lab); ax[1].invert_yaxis(); ax[1].set_xlabel('Kollektorgacha masofa, m'); ax[1].set_ylabel('Sath, m'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3, axis='y'); ax[1].set_title('b', loc='left')
for i, a in enumerate(sb.amp): ax[1].text(i, 0.3, 'A = ' + f'{a:.2f}'.replace('.', ',') + ' m', ha='center', fontsize=8)
tb = pd.DataFrame(R['trend_by_dist']); ax[2].bar(xi, tb.sen_med * 100, color=['#d6604d' if v < 0 else '#4393c3' for v in tb.sen_med]); ax[2].set_xticks(xi); ax[2].set_xticklabels(lab)
ax[2].set_xlabel('Kollektorgacha masofa, m'); ax[2].set_ylabel('Sen qiyaligi medianasi, sm/yil'); ax[2].grid(alpha=.3, axis='y'); ax[2].set_title('c', loc='left')
fig.tight_layout(); fig.savefig('figures/ch3_network.png', dpi=150)
json.dump(R, open('results/ch3_net_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
