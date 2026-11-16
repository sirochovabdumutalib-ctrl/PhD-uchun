"""III bob hisoblari: audit, ko'p yillik va mavsumiy dinamika, geostatistika, tarmoq bilan bog'liqlik.
Chiqish: results/ch3.json, figures/ch3_*.png"""
import csv, json, re, collections, numpy as np, pandas as pd, warnings
import pymannkendall as mk, statsmodels.formula.api as smf
from scipy import stats
from pykrige.ok import OrdinaryKriging
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
R = {}
L = pd.read_csv('data/gw_levels_long.csv'); L['well'] = L.well_no.map(norm)
# ---------- 3.1 audit ----------
raw_n = len(L); yrs = sorted(L.year.unique())
piv = {y: L[L.year == y].set_index(['well', 'decade']).level_m for y in yrs}
copied = []
for i, a in enumerate(yrs):
    for b in yrs[i + 1:]:
        k = piv[a].index.intersection(piv[b].index)
        if len(k) > 500 and (piv[a][k] == piv[b][k]).mean() > 0.95: copied.append((int(a), int(b)))
COPY = {b for a, b in copied}
unit = int((L.level_m > 20).sum()); L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count', 'mean']).reset_index()
const = g[(g['nunique'] == 1) & (g['count'] > 6)]
audit = pd.DataFrame({'wells': g.groupby('year').well.nunique(), 'obs': L.groupby('year').size(),
                      'const_wells': const.groupby('year').size()}).fillna(0).astype(int)
audit['copied_from'] = [next((a for a, b in copied if b == y), '') for y in audit.index]
audit.to_csv('results/ch3_audit_by_year.csv')
R['audit'] = dict(raw_obs=raw_n, wells=int(L.well.nunique()), copied_pairs=copied, unit_errors=unit,
                  const_well_years=int(len(const)), const_obs=int(const['count'].sum()),
                  obs_in_copied_years=int(L.year.isin(COPY).sum()))
C = L[~L.year.isin(COPY)].merge(const[['year', 'well']].assign(c=1), how='left', on=['year', 'well']); C = C[C.c.isna()]
R['audit']['clean_obs'] = int(len(C)); R['audit']['clean_share'] = round(len(C) / raw_n, 3)
# ---------- 3.2 dinamika ----------
ann = C.groupby(['well', 'year'])['level'].mean().unstack()
vy = [y for y in yrs if y not in COPY]
ever_const = set(const.well)
panel = [w for w in ann.index if ann.loc[w, vy].notna().all() and w not in ever_const]
ser = ann.loc[panel, vy].mean(); t = mk.original_test(ser.values); sl = stats.linregress(vy, ser.values)
naive = L[~L.year.isin(COPY)].groupby('year')['level'].mean(); tn = stats.linregress(naive.index, naive.values)
R['trend'] = dict(panel_wells=len(panel), years=[int(y) for y in vy], series={int(y): round(float(v), 3) for y, v in ser.items()},
                  sen_slope=round(float(t.slope), 4), mk_tau=round(float(t.Tau), 3), mk_p=round(float(t.p), 4),
                  ols_slope=round(float(sl.slope), 4), ols_r2=round(float(sl.rvalue ** 2), 3),
                  naive_slope_all_data=round(float(tn.slope), 4), naive_r2=round(float(tn.rvalue ** 2), 3),
                  naive_series={int(y): round(float(v), 3) for y, v in naive.items()})
ws = [(w, mk.original_test(ann.loc[w, vy].values)) for w in panel]
R['trend']['wells_deepening_sig'] = sum(1 for w, r in ws if r.h and r.slope > 0); R['trend']['wells_shallowing_sig'] = sum(1 for w, r in ws if r.h and r.slope < 0)
R['trend']['wells_deepening_any'] = sum(1 for w, r in ws if r.slope > 0); R['trend']['wells_shallowing_any'] = sum(1 for w, r in ws if r.slope < 0)
pre, post = [y for y in vy if y <= 2016], [y for y in vy if y >= 2018]
R['trend']['mean_2009_2016'] = round(float(ann.loc[panel, pre].mean().mean()), 3); R['trend']['mean_2018_2024'] = round(float(ann.loc[panel, post].mean().mean()), 3)
for nm, yy in (('pre', pre), ('post', post)):
    s2 = ann.loc[panel, yy].mean(); r2 = stats.linregress(yy, s2.values); R['trend'][f'slope_{nm}'] = round(float(r2.slope), 4); R['trend'][f'p_{nm}'] = round(float(r2.pvalue), 3)
seas = C[C.well.isin(panel)].groupby('decade')['level'].mean()
R['season'] = dict(profile={int(d): round(float(v), 3) for d, v in seas.items()}, shallowest_decade=int(seas.idxmin()), deepest_decade=int(seas.idxmax()),
                   amplitude=round(float(seas.max() - seas.min()), 3))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8))
ax[0].plot(naive.index, naive.values, 'o--', color='#999', label="Xom ma'lumot, barcha quduqlar"); ax[0].plot(vy, ser.values, 'o-', color='#1f5fa8', label=f"Tozalangan, barqaror {len(panel)} ta quduq")
ax[0].invert_yaxis(); ax[0].set_xlabel('Yil'); ax[0].set_ylabel('Sizot suvi sathi, m'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
ax[1].plot(seas.index, seas.values, 'o-', color='#1f5fa8'); ax[1].invert_yaxis(); ax[1].set_xticks(range(2, 37, 3)); ax[1].set_xticklabels(['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'])
ax[1].set_ylabel('Sizot suvi sathi, m'); ax[1].grid(alpha=.3); fig.tight_layout(); fig.savefig('figures/ch3_dynamics.png', dpi=150)
# ---------- 3.3 geostatistika ----------
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm)
A = pd.read_csv('data/gw_annual.csv'); A['well'] = A.well_no.map(norm); z = A[A.z_m.notna()].groupby('well').z_m.last(); W['z'] = W.well.map(z)
K = W.dropna(subset=['level_2019_2024_m']).copy(); x, y, v = K.x_utm43.values, K.y_utm43.values, K.level_2019_2024_m.values
res = {}
for model in ('spherical', 'exponential', 'gaussian'):
    ok = OrdinaryKriging(x, y, v, variogram_model=model, nlags=12, enable_plotting=False)
    e, se = [], []
    for i in range(len(x)):
        m = np.arange(len(x)) != i
        o = OrdinaryKriging(x[m], y[m], v[m], variogram_model=model, variogram_parameters=list(ok.variogram_model_parameters), nlags=12)
        p, s2 = o.execute('points', x[i:i + 1], y[i:i + 1]); e.append(float(p[0]) - v[i]); se.append(float(np.sqrt(s2[0])))
    e, se = np.array(e), np.array(se); psill, rng, nug = [float(q) for q in ok.variogram_model_parameters]
    res[model] = dict(nugget=round(nug, 3), sill=round(psill + nug, 3), range_m=round(rng), me=round(float(e.mean()), 3), rmse=round(float(np.sqrt((e ** 2).mean())), 3),
                      rmsse=round(float(np.sqrt(((e / se) ** 2).mean())), 3), nugget_ratio=round(nug / (psill + nug), 2))
best = min(res, key=lambda k: res[k]['rmse']); R['kriging'] = dict(n=len(x), models=res, best=best, sd_data=round(float(v.std()), 3),
                                                                   nn_dist_median=round(float(np.median([np.sort(np.hypot(x - a, y - b))[1] for a, b in zip(x, y)]))))
ok = OrdinaryKriging(x, y, v, variogram_model=best, nlags=12)
gx = np.arange(x.min() - 500, x.max() + 500, 150); gy = np.arange(y.min() - 500, y.max() + 500, 150); Z, S2 = ok.execute('grid', gx, gy); SE = np.sqrt(S2)
from scipy.spatial import cKDTree
dmin = cKDTree(np.c_[x, y]).query(np.c_[np.repeat(gx[None], len(gy), 0).ravel(), np.repeat(gy[:, None], len(gx), 1).ravel()])[0].reshape(Z.shape)
Zm, SEm = np.ma.masked_where(dmin > 1500, Z), np.ma.masked_where(dmin > 1500, SE)
R['kriging']['se_min'] = round(float(SEm.min()), 2); R['kriging']['se_max'] = round(float(SEm.max()), 2); R['kriging']['area_shallow_1_5_share'] = round(float((Zm < 1.5).mean()), 3); R['kriging']['area_2_share'] = round(float((Zm < 2.0).mean()), 3)
net = json.load(open('gis/collectors.geojson'))['features']
from pyproj import Transformer; tr = Transformer.from_crs(4326, 32643, always_xy=True)
fig, ax = plt.subplots(1, 2, figsize=(12, 5.6))
for a, data, cm, lab in ((ax[0], Zm, 'RdYlBu', 'Sizot suvi sathi, m'), (ax[1], SEm, 'YlOrRd', 'Bahoning standart xatosi, m')):
    im = a.pcolormesh(gx / 1000, gy / 1000, data, cmap=cm, shading='auto'); plt.colorbar(im, ax=a, label=lab, shrink=.8)
    for f in net:
        cx, cy = tr.transform(*zip(*f['geometry']['coordinates'])); a.plot(np.array(cx) / 1000, np.array(cy) / 1000, color='#2a7a2a', lw=.6)
    a.scatter(x / 1000, y / 1000, s=6, c='k'); a.set_aspect(1); a.set_xlabel('X, km (UTM 43N)'); a.set_ylabel('Y, km')
fig.tight_layout(); fig.savefig('figures/ch3_kriging.png', dpi=150)
# ---------- 3.4 tarmoq bilan bog'liqlik ----------
Dm = W.dropna(subset=['level_2019_2024_m', 'z']).copy(); Dm['ldist'] = np.log10(Dm.dist_collector_m + 10); Dm['dens'] = Dm.collector_len_1km_m / 1000; Dm['lcan'] = np.log10(Dm.dist_canal_m + 10)
sp = {k: [round(float(q), 4) for q in stats.spearmanr(Dm[k], Dm.level_2019_2024_m)] for k in ('dist_collector_m', 'collector_len_1km_m', 'dist_canal_m', 'z')}
m1 = smf.ols('level_2019_2024_m ~ ldist + lcan + z', Dm).fit(cov_type='HC3'); m2 = smf.ols('level_2019_2024_m ~ dens + lcan + z', Dm).fit(cov_type='HC3'); m0 = smf.ols('level_2019_2024_m ~ z', Dm).fit()
R['network'] = dict(n=len(Dm), spearman=sp, r2_relief_only=round(float(m0.rsquared), 3),
                    model_dist={k: [round(float(m1.params[k]), 4), round(float(m1.pvalues[k]), 4)] for k in m1.params.index}, r2_dist=round(float(m1.rsquared), 3),
                    model_dens={k: [round(float(m2.params[k]), 4), round(float(m2.pvalues[k]), 4)] for k in m2.params.index}, r2_dens=round(float(m2.rsquared), 3))
bins = [0, 150, 400, 800, 1e5]; Dm['bin'] = pd.cut(W.loc[Dm.index, 'dist_collector_m'], bins, right=False)
R['network']['by_distance'] = [dict(bin=str(b), n=int(len(q)), mean=round(float(q.level_2019_2024_m.mean()), 2), share_lt_1_5=round(float((q.level_2019_2024_m < 1.5).mean()), 2)) for b, q in W.dropna(subset=['level_2019_2024_m']).assign(bin=lambda d: pd.cut(d.dist_collector_m, bins, right=False)).groupby('bin')]
# massivlar bo'yicha
R['massif'] = {k: dict(n=int(len(q)), level=round(float(q.level_2019_2024_m.mean()), 2), dist=round(float(q.dist_collector_m.mean()))) for k, q in W.dropna(subset=['level_2019_2024_m', 'massif']).groupby('massif')}
json.dump(R, open('results/ch3.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(R, ensure_ascii=False, indent=1)[:6000])
