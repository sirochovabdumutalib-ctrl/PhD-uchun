"""3.6-§: Andijon viloyati tumanlari bo'yicha monitoring ma'lumotlari ishonchliligi va sizot rejimi ko'rsatkichlarini qiyoslash.
Kirish: data/region_levels_long.csv. Chiqish: results/ch3_region.json, figures/ch3_region.png"""
import json, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
import pymannkendall as mk
warnings.filterwarnings('ignore')
L = pd.read_csv('data/region_levels_long.csv'); L['well_no'] = L.well_no.astype(str)
L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m); L['unit'] = L.level_m > 20
R = {}; rows = []
for dist, D in L.groupby('district'):
    yrs = sorted(D.year.unique()); piv = {y: D[D.year == y].set_index(['well_no', 'decade']).level for y in yrs}
    piv = {y: s[~s.index.duplicated()] for y, s in piv.items()}
    noind = set()
    for i, a in enumerate(yrs):
        for b in yrs[i + 1:]:
            k = piv[a].index.intersection(piv[b].index)
            if len(k) > 300 and (piv[a][k] == piv[b][k]).mean() > 0.95: noind.add(b)
    E = D[~D.year.isin(noind)].copy()
    g = E.groupby(['year', 'well_no'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)]
    E = E.merge(cst[['year', 'well_no']].assign(c=1), on=['year', 'well_no'], how='left')
    n_all = len(D); valid = E[E.c.isna()]
    rnd = (np.round(valid.level * 10) == valid.level * 10).mean()  # 1 xonali yaxlit qiymatlar ulushi
    # stable panel: wells observed in all retained years w/o constant series
    ann = valid.groupby(['well_no', 'year'])['level'].mean().unstack(); ry = sorted(valid.year.unique())
    cw = set(cst.well_no); panel = [w for w in ann.index if ann.loc[w, ry].notna().all() and w not in cw]
    rec = dict(district=dist, years=len(yrs), noind_years=len(noind), wells=int(D.well_no.nunique()), obs=n_all,
               const_share=round(len(cst) / max(len(g), 1) * 100, 1), unit_obs=int(D.unit.sum()), valid_share=round(len(valid) / len(E) * 100, 1), noind_list=sorted(int(x) for x in noind),
               round_share=round(rnd * 100, 1), panel=len(panel))
    if len(panel) >= 5 and len(ry) >= 8:
        s = ann.loc[panel, ry].mean(); t = mk.original_test(s.values)
        rec.update(sen=round(stats.theilslopes(s.values, s.index)[0], 4), tau=round(t.Tau, 3), p=round(t.p, 4), first=round(s.iloc[0], 2), last=round(s.iloc[-1], 2))
    last = valid[valid.year >= 2019]; wl = last.groupby('well_no')['level'].mean(); ws = last[last.decade.between(19, 24)].groupby('well_no')['level'].mean()
    rec.update(level_med=round(wl.median(), 2), summer_med=round(ws.median(), 2), sh15_summer=round((ws < 1.5).mean() * 100, 1), sh20_summer=round((ws < 2.0).mean() * 100, 1),
               deep5=round((valid[valid.year >= 2019].level >= 5).mean() * 100, 1))
    prof = valid[valid.well_no.isin(panel) if panel else valid.well_no.notna()].groupby('decade')['level'].mean(); rec['amp'] = round(prof.max() - prof.min(), 2)
    rows.append(rec)
T = pd.DataFrame(rows).sort_values('valid_share', ascending=False); R['table'] = T.to_dict('records')
R['ranks'] = {c: int(T.sort_values(c, ascending=asc).reset_index(drop=True).query("district=='Marhamat'").index[0]) + 1 for c, asc in
              [('valid_share', False), ('const_share', True), ('level_med', True), ('sh20_summer', False), ('sen', False), ('summer_med', True)]}
R['rho_valid_level'] = [round(x, 3) for x in stats.spearmanr(T.valid_share, T.level_med)]
R['rho_const_deep'] = [round(x, 3) for x in stats.spearmanr(T.const_share, T.deep5)]
Ts = T.dropna(subset=['sen']); R['n_sig_deep'] = int(((Ts.sen > 0) & (Ts.p < .05)).sum()); R['n_sig_shallow'] = int(((Ts.sen < 0) & (Ts.p < .05)).sum()); R['n_trend'] = len(Ts)
R['region'] = dict(wells=int(L.groupby('district').well_no.nunique().sum()), obs=len(L), valid_med=round(T.valid_share.median(), 1), const_med=round(T.const_share.median(), 1),
                   sen_med=round(Ts.sen.median(), 4), level_med=round(T.level_med.median(), 2))
# figure
fig, ax = plt.subplots(1, 2, figsize=(12.5, 5))
c = ['#d6604d' if d == 'Marhamat' else '#4393c3' for d in T.district]
ax[0].barh(T.district, T.valid_share, color=c); ax[0].invert_yaxis(); ax[0].set_xlabel("Yaroqli o'lchovlar ulushi, %"); ax[0].set_xlim(min(60, T.valid_share.min() - 5), 100); ax[0].grid(alpha=.3, axis='x'); ax[0].set_title('a', loc='left')
for _, r in T.iterrows():
    ax[1].scatter(r.summer_med, r.get('sen', np.nan) * 100 if pd.notna(r.get('sen', np.nan)) else np.nan, s=60, c='#d6604d' if r.district == 'Marhamat' else '#4393c3', edgecolor='k', lw=.5)
    ax[1].annotate(r.district, (r.summer_med, r.get('sen', np.nan) * 100 if pd.notna(r.get('sen', np.nan)) else np.nan), fontsize=7, xytext=(4, 3), textcoords='offset points')
ax[1].axhline(0, color='#999', lw=.8); ax[1].set_xlabel('Iyul–avgustdagi sath medianasi, 2019–2023, m'); ax[1].set_ylabel('Barqaror panel bo\'yicha Sen qiyaligi, sm/yil'); ax[1].grid(alpha=.3); ax[1].set_title('b', loc='left')
fig.tight_layout(); fig.savefig('figures/ch3_region.png', dpi=150)
json.dump(R, open('results/ch3_region.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else (None if o != o else str(o)))
pd.set_option('display.width', 250); print(T.to_string()); print({k: v for k, v in R.items() if k != 'table'})
