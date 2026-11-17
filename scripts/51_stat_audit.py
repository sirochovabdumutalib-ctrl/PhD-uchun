"""Statistik audit (statistical-analysis skill, 2-band): asosiy xulosalar uchun ishonch oraliqlari, effekt kattaliklari,
avtokorrelyatsiyaga chidamli trend testlari, regressiya diagnostikasi, ko'p testlar tuzatishi.
Chiqish: results/stat_audit.json"""
import re, json, numpy as np, pandas as pd, warnings, pymannkendall as mk
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.multitest import multipletests
warnings.filterwarnings('ignore'); rng = np.random.default_rng(11); R = {}
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
def fz(r, n):  # Spearman uchun Fisher z oralig'i (Bonett–Wright standart xatosi)
    z = np.arctanh(r); se = np.sqrt((1 + r ** 2 / 2) / (n - 3)); return [round(float(np.tanh(z - 1.96 * se)), 2), round(float(np.tanh(z + 1.96 * se)), 2)]
# --- A. barqaror panel trendi (3.2-§)
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin({2010, 2013, 2017})].copy(); L['well'] = L.well_no.map(norm)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
yrs = sorted(L.year.unique()); ann = L.groupby(['well', 'year'])['level'].mean().unstack()
panel = [w for w in ann.index if ann.loc[w, yrs].notna().all() and w not in set(cst.well)]; s = ann.loc[panel, yrs].mean()
ts = stats.theilslopes(s.values, s.index); r1 = float(pd.Series(s.values).autocorr(1))
pre, post = s[s.index <= 2016].values, s[s.index >= 2018].values
# quduqlar bo'yicha klasterli bootstrap: panel trendining noaniqligi quduqlar tanlanmasidan
bs = []
for _ in range(2000):
    q = ann.loc[rng.choice(panel, len(panel)), yrs].mean(); bs.append(stats.theilslopes(q.values, q.index)[0])
R['panel_trend'] = dict(n_years=len(s), n_wells=len(panel), sen=round(ts[0], 4), sen_ci_years=[round(ts[2], 4), round(ts[3], 4)], sen_ci_wells_boot=[round(float(np.percentile(bs, 2.5)), 4), round(float(np.percentile(bs, 97.5)), 4)],
                        lag1_acf=round(r1, 2), mk_p=round(mk.original_test(s.values).p, 4), hamed_rao_p=round(mk.hamed_rao_modification_test(s.values).p, 4),
                        yue_wang_p=round(mk.yue_wang_modification_test(s.values).p, 4), prewhiten_p=round(mk.pre_whitening_modification_test(s.values).p, 4),
                        step=dict(pre_mean=round(pre.mean(), 3), post_mean=round(post.mean(), 3), diff=round(post.mean() - pre.mean(), 3),
                                  welch_p=float(f"{stats.ttest_ind(post, pre, equal_var=False).pvalue:.2g}"), hedges_g=round(float((post.mean() - pre.mean()) / np.sqrt(((len(pre) - 1) * pre.var(ddof=1) + (len(post) - 1) * post.var(ddof=1)) / (len(pre) + len(post) - 2)) * (1 - 3 / (4 * (len(pre) + len(post)) - 9))), 2),
                                  mwu_p=round(stats.mannwhitneyu(post, pre).pvalue, 4)))
# massivlar bo'yicha trend testlari: FDR
D3 = json.load(open('results/ch3_dyn_ext.json'))['massif']; mp = {k: v for k, v in D3.items() if 'p' in v}
rej, q, _, _ = multipletests([v['p'] for v in mp.values()], method='fdr_bh')
R['massif_trend_fdr'] = {k: dict(n=v['n'], sen=v['sen'], p=v['p'], q=round(float(qq), 4), sig=bool(rr)) for (k, v), qq, rr in zip(mp.items(), q, rej)}
# --- B. viloyat (3.6-§): 14 ta tuman, kichik n — ishonch oraliqlari
T = pd.DataFrame(json.load(open('results/ch3_region.json'))['table']); n = len(T)
def rb(x, y):
    r = stats.spearmanr(T[x], T[y])[0]; b = []
    for _ in range(5000):
        i = rng.integers(0, n, n); b.append(stats.spearmanr(T[x].values[i], T[y].values[i])[0])
    return dict(rho=round(r, 2), p=float(f'{stats.spearmanr(T[x], T[y])[1]:.2g}'), ci_fisher=fz(r, n), ci_boot=[round(float(np.nanpercentile(b, 2.5)), 2), round(float(np.nanpercentile(b, 97.5)), 2)])
R['region'] = dict(n=n, const_vs_level=rb('const_share', 'level_med'), valid_vs_level=rb('valid_share', 'level_med'), sen_vs_level=rb('sen', 'level_med'), sen_vs_valid=rb('sen', 'valid_share'))
rk = T[['sen', 'level_med', 'valid_share']].rank(); res = lambda a, b: smf.ols(f'{a} ~ {b}', rk).fit().resid
pr = stats.pearsonr(res('sen', 'valid_share'), res('level_med', 'valid_share'))
R['region']['partial_sen_level_given_valid'] = dict(r=round(pr[0], 2), p=round(pr[1], 3))
# --- C. 3.4-§: sath, tarmoq; "to'rt baravar" tezlik farqi
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm)
sen = {w: stats.theilslopes(ann.loc[w].dropna().values, ann.loc[w].dropna().index)[0] for w in ann.index if ann.loc[w].notna().sum() >= 8}
W['sen'] = W.well.map(sen); Tn = W.dropna(subset=['sen', 'level_2019_2024_m'])
near, far = Tn[Tn.dist_collector_m < 150].sen.values, Tn[Tn.dist_collector_m >= 800].sen.values
bd, br = [], []
for _ in range(5000):
    a = rng.choice(near, len(near)); b = rng.choice(far, len(far)); bd.append(np.median(b) - np.median(a))
u = stats.mannwhitneyu(far, near)
R['near_far_trend'] = dict(n_near=len(near), n_far=len(far), med_near_cm=round(np.median(near) * 100, 1), med_far_cm=round(np.median(far) * 100, 1),
                           diff_cm=round((np.median(far) - np.median(near)) * 100, 1), diff_ci_cm=[round(float(np.percentile(bd, 2.5)) * 100, 1), round(float(np.percentile(bd, 97.5)) * 100, 1)],
                           mwu_p=round(u.pvalue, 4), rank_biserial=round(1 - 2 * u.statistic / (len(near) * len(far)) * -1 - 1 + 0, 2) if False else round(2 * u.statistic / (len(near) * len(far)) - 1, 2))
D = W.dropna(subset=['level_2019_2024_m']); R['level_rho'] = {k: dict(rho=round(stats.spearmanr(D[k], D.level_2019_2024_m)[0], 2), ci=fz(stats.spearmanr(D[k], D.level_2019_2024_m)[0], len(D)), n=len(D))
                                                            for k in ('dist_collector_m', 'collector_len_1km_m', 'dist_canal_m')}
# --- D. 30-ilova regressiyalari: diagnostika
A = pd.read_csv('data/gw_annual.csv'); A['well'] = A.well_no.map(norm); W['z'] = W.well.map(A[A.z_m.notna()].groupby('well').z_m.last())
Dm = W.dropna(subset=['level_2019_2024_m', 'z']).copy(); Dm['ldist'] = np.log10(Dm.dist_collector_m + 10); Dm['dens'] = Dm.collector_len_1km_m / 1000; Dm['lcan'] = np.log10(Dm.dist_canal_m + 10)
R['regression'] = {}
for nm, f, xs in [('m1', 'level_2019_2024_m ~ ldist + lcan + z', ['ldist', 'lcan', 'z']), ('m2', 'level_2019_2024_m ~ dens + lcan + z', ['dens', 'lcan', 'z']),
                  ('m1_log', 'np.log(level_2019_2024_m) ~ ldist + lcan + z', ['ldist', 'lcan', 'z'])]:
    m = smf.ols(f, Dm).fit(); X = m.model.exog; infl = m.get_influence(); cook = infl.cooks_distance[0]
    mh = m.get_robustcov_results('HC3'); k = xs[0]; i = list(m.params.index).index(k)
    keep = cook < 4 / len(Dm); mr = smf.ols(f, Dm[keep]).fit(cov_type='HC3')
    R['regression'][nm] = dict(n=int(m.nobs), r2=round(m.rsquared, 3), adj_r2=round(m.rsquared_adj, 3), coef=round(float(m.params[k]), 3), ci_hc3=[round(float(c), 3) for c in mh.conf_int()[i]],
                               p_hc3=float(f'{mh.pvalues[i]:.2g}'), shapiro_resid_p=float(f'{stats.shapiro(m.resid)[1]:.2g}'), skew_resid=round(float(stats.skew(m.resid)), 2),
                               bp_p=float(f'{het_breuschpagan(m.resid, X)[1]:.2g}'), vif_max=round(max(variance_inflation_factor(X, j) for j in range(1, X.shape[1])), 2),
                               n_cook=int((~keep).sum()), coef_wo_influential=round(float(mr.params[k]), 3), p_wo_influential=float(f'{mr.pvalues[k]:.2g}'))
# --- E. 3.5-§: minerallashuv massivlar bo'yicha (Kruskal–Wallis, epsilon^2)
m = pd.read_csv('data/miner_1999_2015.csv'); m['well'] = m.well_no.map(norm); m = m[m.year.between(2004, 2010)].dropna(subset=['miner_gl'])
Q = W.merge(m.groupby('well').miner_gl.median().rename('mmed'), left_on='well', right_index=True).dropna(subset=['massif_map'])
grp = [q.mmed.values for _, q in Q.groupby('massif_map') if len(q) >= 5]; H, p = stats.kruskal(*grp); N = sum(len(x) for x in grp)
R['miner_massif'] = dict(n=N, k=len(grp), H=round(H, 2), p=float(f'{p:.2g}'), epsilon2=round(H / (N - 1), 2),
                         medians={k: round(q.mmed.median(), 2) for k, q in Q.groupby('massif_map')})
json.dump(R, open('results/stat_audit.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
