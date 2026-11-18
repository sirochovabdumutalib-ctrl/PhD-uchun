"""Farazlar bo'yicha mavjud ma'lumotlarda bajariladigan ajratuvchi tekshiruvlar (hypothesis-generation, 6-band).
H4: o'zgarmas (yil bo'yi bir xil) qatorlar quduq tubigacha zaxira kichik bo'lgan quduqlarda yuz beradi (quruq quduq izohi)
    — raqib: kuzatuvchi amaliyoti (zaxiraga bog'liq emas, massiv/kuzatuvchi bo'yicha to'planadi).
H3: Z.M.Bobur massividagi ko'tarilish — drenaj yetishmovchiligi izohi yozgi sathda (sug'orish mavsumida) kuchliroq bo'lishini,
    umumiy omil esa qish va yozda bir xil bo'lishini bashorat qiladi. Chiqish: results/hypothesis_checks.json"""
import re, json, numpy as np, pandas as pd, statsmodels.formula.api as smf
from scipy import stats
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin({2010, 2013, 2017})].copy(); L['well'] = L.well_no.map(norm)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
P = pd.read_csv('data/wells_passport.csv'); P['well'] = P.well_no.map(norm); P['depth'] = pd.to_numeric(P.depth_cm, errors='coerce') / 100
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm); mas = dict(zip(W.well, W.massif_map))
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count', 'mean']).reset_index(); g['const'] = (g['nunique'] == 1) & (g['count'] > 6)
g = g.merge(P[['well', 'depth']].drop_duplicates('well'), on='well', how='left'); g['massif'] = g.well.map(mas)
# zaxira: quduq chuqurligi − o'sha quduqning o'zgarmas bo'lmagan yillardagi o'rtacha sathi
ok = g[~g.const].groupby('well')['mean'].mean(); g['margin'] = g.depth - g.well.map(ok)
# o'zgarmas qiymat quduq tubiga qanchalik yaqin
g['const_gap'] = np.where(g.const, g.depth - g['mean'], np.nan)
R = {}
d = g.dropna(subset=['margin', 'massif']).copy(); d['c'] = d.const.astype(int)
m0 = smf.logit('c ~ margin', d).fit(disp=0); m1 = smf.logit('c ~ margin + C(massif)', d).fit(disp=0, method='bfgs', maxiter=500)
R['H4'] = dict(n_wellyears=len(d), n_const=int(d.c.sum()), or_per_m=round(float(np.exp(m0.params.margin)), 3), p=float(f'{m0.pvalues.margin:.2g}'),
               or_per_m_massif_fe=round(float(np.exp(m1.params.margin)), 3), p_fe=float(f'{m1.pvalues.margin:.2g}'),
               const_share_by_margin={str(k): round(float(v), 3) for k, v in d.groupby(pd.cut(d.margin, [-5, 0.5, 1, 1.5, 2, 10]))['c'].mean().items()},
               const_value_to_bottom_m=dict(median=round(float(g.const_gap.median()), 2), q25=round(float(g.const_gap.quantile(.25)), 2), q75=round(float(g.const_gap.quantile(.75)), 2), n=int(g.const_gap.notna().sum())))
# H3: Z.M.Bobur — qish (1–6 dekada) va yoz (19–24) bo'yicha 2009–2018 vs 2019–2024 o'zgarishi, boshqa massivlar bilan
g2 = g[['year', 'well', 'const']]; L2 = L.merge(g2, on=['year', 'well']); L2 = L2[~L2.const]; L2['massif'] = L2.well.map(mas)
def seas(q, a, b): return q[q.decade.between(a, b)].groupby(['well', 'year'])['level'].mean().reset_index()
res = {}
for nm, (a, b) in {'qish': (1, 6), 'yoz': (19, 24)}.items():
    s = seas(L2, a, b); s['massif'] = s.well.map(mas); s['post'] = (s.year >= 2019).astype(int)
    for grp, q in [('Z.M.Bobur', s[s.massif == 'З.М.Бобур']), ('boshqalar', s[(s.massif != 'З.М.Бобур') & s.massif.notna()])]:
        both = q.groupby('well').post.nunique(); q = q[q.well.isin(both[both == 2].index)]
        dd = q.groupby(['well', 'post'])['level'].mean().unstack().dropna(); diff = dd[1] - dd[0]
        res[f'{grp}_{nm}'] = dict(n=len(diff), change_m=round(float(diff.mean()), 3), ci=[round(float(x), 3) for x in stats.t.interval(.95, len(diff) - 1, diff.mean(), stats.sem(diff))])
R['H3'] = res
json.dump(R, open('results/hypothesis_checks.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
