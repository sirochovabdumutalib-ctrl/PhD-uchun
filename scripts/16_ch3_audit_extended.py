"""3.1-§ kengaytirilgan tekshiruv: massivlar va yillar bo'yicha ishonchlilik, kesilgan (quruq quduq) qiymatlar,
tarmoq tarkibi ko'rsatkichlari. Chiqish: results/ch3_audit_ext.json, figures/ch3_audit.png"""
import re, json, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
EXCL = {2010, 2013, 2017}
L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin(EXCL)].copy(); L['well'] = L.well_no.map(norm)
L['unit_err'] = L.level_m > 20; L['level'] = np.where(L.unit_err, L.level_m / 100, L.level_m)
g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); g['const'] = (g['nunique'] == 1) & (g['count'] > 6)
L = L.merge(g[['year', 'well', 'const']], on=['year', 'well'])
P = pd.read_csv('data/wells_passport.csv'); P['well'] = P.well_no.map(norm); P['depth_m'] = pd.to_numeric(P.depth_cm, errors='coerce') / 100
M = pd.read_csv('data/wells_metrics.csv'); M['well'] = M.well_no.map(norm); mas = dict(zip(M.well, M.massif_map))
L['massif'] = L.well.map(mas); L = L.merge(P[['well', 'depth_m']].drop_duplicates('well'), on='well', how='left')
L['censored'] = (~L.const) & L.depth_m.notna() & (L.level >= L.depth_m - 0.1)
L['valid'] = ~L.const
R = {}
R['total'] = dict(obs=len(L), wells=int(L.well.nunique()), const_obs=int(L.const.sum()), unit=int(L.unit_err.sum()), valid=int(L.valid.sum()), share_valid=round(L.valid.mean() * 100, 1),
                  with_depth=int(L.depth_m.notna().sum()), censored=int(L.censored.sum()), censored_share_of_valid_with_depth=round(L[L.valid & L.depth_m.notna()].censored.mean() * 100, 2))
# const values themselves
cv = L[L.const].groupby(['year', 'well'])['level'].first(); R['const_values'] = cv.round(2).value_counts().head(6).to_dict()
cvd = L[L.const].drop_duplicates(['year', 'well']); cvd = cvd[cvd.depth_m.notna()]; R['const_near_depth_share'] = round(((cvd.level >= cvd.depth_m - 0.3)).mean() * 100, 1)
R['const_vs_depth'] = dict(n=len(cvd), median_gap=round(float((cvd.depth_m - cvd.level).median()), 2))
bym = L.groupby('massif').agg(obs=('level', 'size'), wells=('well', 'nunique'), const=('const', 'sum'), censored=('censored', 'sum'))
bym['valid_share'] = (100 * (1 - bym.const / bym.obs)).round(1); bym['cens_share'] = (100 * bym.censored / (bym.obs - bym.const)).round(1); R['by_massif'] = bym.reset_index().to_dict('records')
by = L.groupby('year').agg(obs=('level', 'size'), wells=('well', 'nunique'), const=('const', 'sum'), censored=('censored', 'sum'), deep5=('level', lambda s: (s > 5).mean()))
by['valid_share'] = (100 * (1 - by.const / by.obs)).round(1); by['deep5'] = (by.deep5 * 100).round(1); R['by_year'] = by.reset_index().to_dict('records')
# well-level: how many wells ever const
wc = L.groupby('well').agg(yrs=('year', 'nunique'), cy=('const', lambda s: 0)).reset_index()
cyears = g[g.const].groupby('well').year.nunique(); wc['const_years'] = wc.well.map(cyears).fillna(0)
R['wells_ever_const'] = int((wc.const_years > 0).sum()); R['wells_const_ge3'] = int((wc.const_years >= 3).sum())
# network composition: wells entering/leaving
yrs = sorted(L.year.unique()); S = {y: set(L[L.year == y].well) for y in yrs}
R['turnover'] = [dict(year=int(b), new=len(S[b] - S[a]), gone=len(S[a] - S[b])) for a, b in zip(yrs, yrs[1:])]
json.dump(R, open('results/ch3_audit_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
fig, ax = plt.subplots(1, 2, figsize=(11, 3.8)); x = by.index.astype(str)
ax[0].bar(x, by.wells, color='#4a6fa5'); ax[0].set_ylabel('Kuzatilgan quduqlar soni'); ax[0].tick_params(axis='x', rotation=45); ax2 = ax[0].twinx(); ax2.plot(x, by.deep5, 'o-', color='#c0392b'); ax2.set_ylabel('5 m dan chuqur o’lchovlar, %', color='#c0392b')
ax[1].bar(x, 100 - by.valid_share, color='#d98c3a'); ax[1].set_ylabel('Yaroqsiz o’lchovlar ulushi, %'); ax[1].tick_params(axis='x', rotation=45)
for a in ax: a.grid(alpha=.3)
fig.tight_layout(); fig.savefig('figures/ch3_audit.png', dpi=150)
print(json.dumps(R, ensure_ascii=False, indent=0, default=str)[:4000])
