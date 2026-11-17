"""Tekshiruv qoidalari chegaralariga sezgirlik (taqriz m4).
1-qoida: quduq-yilda barcha o'n kunlik qiymatlar bir xil va o'lchovlar soni > k (k = 3, 6, 9, 12) — chiqarilgan quduq-yillar va
barqaror panel bo'yicha Sen qiyaligi; kesilgan qiymat: sath quduq chuqurligiga d dan yaqin (d = 0,05; 0,1; 0,2; 0,3 m).
Chiqish: results/rule_sensitivity.json"""
import re, json, numpy as np, pandas as pd, pymannkendall as mk
from scipy import stats
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
L0 = pd.read_csv('data/gw_levels_long.csv'); L0 = L0[~L0.year.isin({2010, 2013, 2017})].copy(); L0['well'] = L0.well_no.map(norm)
L0['level'] = np.where(L0.level_m > 20, L0.level_m / 100, L0.level_m)
P = pd.read_csv('data/wells_passport.csv'); P['well'] = P.well_no.map(norm); P['depth'] = pd.to_numeric(P.depth_cm, errors='coerce') / 100
g = L0.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); R = {'rule1': [], 'censor': []}
yrs = sorted(L0.year.unique())
for k in (3, 6, 9, 12):
    cst = g[(g['nunique'] == 1) & (g['count'] > k)][['year', 'well']].assign(c=1)
    L = L0.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
    ann = L.groupby(['well', 'year'])['level'].mean().unstack(); ever = set(cst.well)
    panel = [w for w in ann.index if ann.loc[w, yrs].notna().all() and w not in ever]; s = ann.loc[panel, yrs].mean()
    R['rule1'].append(dict(k=k, flagged=len(cst), share_obs=round(1 - len(L) / len(L0), 4), panel=len(panel),
                           sen=round(stats.theilslopes(s.values, s.index)[0], 4), p=round(mk.original_test(s.values).p, 4)))
cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
L = L0.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()].merge(P[['well', 'depth']].drop_duplicates('well'), on='well', how='left')
ann = L.groupby(['well', 'year'])['level'].mean().unstack(); panel = [w for w in ann.index if ann.loc[w, yrs].notna().all() and w not in set(cst.well)]
for d in (0.05, 0.1, 0.2, 0.3):
    c = L.depth.notna() & (L.level >= L.depth - d); Q = L[~c & L.well.isin(panel)]
    s = Q.groupby(['well', 'year'])['level'].mean().unstack().mean()
    R['censor'].append(dict(d=d, share_valid=round(float(c.mean()) * 100, 1), sen_no_cens=round(stats.theilslopes(s.values, s.index)[0], 4)))
json.dump(R, open('results/rule_sensitivity.json', 'w'), indent=1); print(json.dumps(R, indent=1))
