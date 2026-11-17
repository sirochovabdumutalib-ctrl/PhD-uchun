"""3.4-§ uchun fazoviy bog'liqlikka chidamlilik tekshiruvi (taqriz M3).
1) OLS qoldiqlarida Moran I (k=8 eng yaqin qo'shni, qatorlar bo'yicha normallangan; 999 ta tasodifiy almashtirish);
2) Spearman ρ uchun fazoviy blokli bootstrap (2x2 km kataklar, 2000 takror) — 95 % ishonch oralig'i;
3) massivlar ichidagi va quduqlar bo'yicha ko'p testlarga Benjamini–Hochberg (FDR) tuzatishi;
4) regressiya qiyaligi uchun 2x2 km kataklar bo'yicha klasterli standart xato.
Chiqish: results/spatial_robustness.json"""
import re, json, numpy as np, pandas as pd, warnings
from scipy import stats
from scipy.spatial import cKDTree
import statsmodels.formula.api as smf, pymannkendall as mk
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings('ignore'); rng = np.random.default_rng(2024)
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm)
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin({2010, 2013, 2017})].copy(); L['well'] = L.well_no.map(norm)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
ann = L.groupby(['well', 'year'])['level'].mean().unstack(); sen, mkp = {}, {}
for w in ann.index:
    s = ann.loc[w].dropna()
    if len(s) >= 8: sen[w] = stats.theilslopes(s.values, s.index)[0]; mkp[w] = mk.original_test(s.values).p
W['sen'] = W.well.map(sen); W['mkp'] = W.well.map(mkp)
D = W.dropna(subset=['level_2019_2024_m']).copy(); D['ldist'] = np.log10(D.dist_collector_m + 10); D['dens'] = D.collector_len_1km_m / 1000
R = {}

def weights(xy, k=8):
    d, i = cKDTree(xy).query(xy, k + 1); return i[:, 1:]
def moran(z, nb, perm=999):
    z = z - z.mean(); lag = z[nb].mean(1); I = (z * lag).sum() / (z ** 2).sum()
    sims = np.array([(zp * zp[nb].mean(1)).sum() / (zp ** 2).sum() for zp in (rng.permutation(z) for _ in range(perm))])
    return I, (1 + (sims >= I).sum()) / (perm + 1)
def block_boot(df, x, y, cell=2000, B=2000):
    c = (df.x_utm43 // cell).astype(int).astype(str) + '_' + (df.y_utm43 // cell).astype(int).astype(str)
    groups = [df.index[c == u] for u in c.unique()]; out = []
    for _ in range(B):
        idx = np.concatenate([groups[j] for j in rng.integers(0, len(groups), len(groups))])
        q = df.loc[idx]; out.append(stats.spearmanr(q[x], q[y])[0])
    return np.nanpercentile(out, [2.5, 97.5]), len(groups)
for name, sub, y, xs in [('level', D, 'level_2019_2024_m', ['dist_collector_m', 'collector_len_1km_m']),
                         ('summer', D.dropna(subset=['level_summer_m']), 'level_summer_m', ['dist_collector_m', 'collector_len_1km_m']),
                         ('trend', D.dropna(subset=['sen']), 'sen', ['dist_collector_m', 'collector_len_1km_m'])]:
    sub = sub.reset_index(drop=True); nb = weights(sub[['x_utm43', 'y_utm43']].values)
    Iy, py = moran(sub[y].values, nb)
    r = dict(n=len(sub), moran_y=[round(Iy, 3), round(py, 3)])
    for x in xs:
        f = f"{y} ~ np.log10({x} + 10)" if x == 'dist_collector_m' else f"{y} ~ I({x}/1000)"
        m = smf.ols(f, sub).fit(); Ir, pr = moran(m.resid.values, nb)
        mfe = smf.ols(f + ' + C(massif_map)', sub).fit(); Ife, pfe = moran(mfe.resid.values, nb)
        rho, p = stats.spearmanr(sub[x], sub[y]); ci, ncell = block_boot(sub, x, y)
        cell = (sub.x_utm43 // 2000).astype(int).astype(str) + '_' + (sub.y_utm43 // 2000).astype(int).astype(str)
        mc = smf.ols(f, sub).fit(cov_type='cluster', cov_kwds={'groups': pd.factorize(cell)[0]}); k = mc.params.index[1]
        r[x] = dict(rho=round(rho, 3), p=float(f'{p:.2g}'), moran_resid=[round(Ir, 3), round(pr, 3)], moran_resid_fe=[round(Ife, 3), round(pfe, 3)],
                    boot_ci=[round(v, 2) for v in ci], cells=ncell, slope=round(mc.params[k], 3), p_ols=float(f'{m.pvalues[k]:.2g}'), p_cluster=float(f'{mc.pvalues[k]:.2g}'))
    R[name] = r
# massivlar ichidagi testlar: BH-FDR
pv = []
for m, q in D.groupby('massif_map'):
    if len(q) >= 8: rho, p = stats.spearmanr(q.dist_collector_m, q.level_2019_2024_m); pv.append((m, len(q), round(rho, 2), p))
rej, padj, _, _ = multipletests([p for *_, p in pv], method='fdr_bh')
R['within_fdr'] = [dict(massif=m, n=n, rho=r, p=round(p, 3), q=round(qq, 3), sig=bool(s)) for (m, n, r, p), qq, s in zip(pv, padj, rej)]
# quduqlar bo'yicha MK testlari (3.2-§ dagi 122 ta quduq): kutiladigan tasodifiy natija va FDR
T = pd.DataFrame({'sen': pd.Series(sen), 'p': pd.Series(mkp)}); n = len(T); sig = T.p < .05
rej, padj, _, _ = multipletests(T.p, method='fdr_bh'); deep = (T.sen > 0).values
R['wells_mk'] = dict(n=n, sig05=int(sig.sum()), sig_deep=int((sig.values & deep).sum()), sig_shallow=int((sig.values & ~deep).sum()), expected_by_chance=round(.05 * n, 1),
                     fdr_sig=int(rej.sum()), fdr_deep=int((rej & deep).sum()), fdr_shallow=int((rej & ~deep).sum()),
                     binom_p=float(f"{stats.binomtest(int(sig.sum()), n, .05, alternative='greater').pvalue:.2g}"))
json.dump(R, open('results/spatial_robustness.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
