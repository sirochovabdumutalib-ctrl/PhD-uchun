"""4.3-§ kengaytirilgan: event-study (oldingi/keyingi yillar), parallel tendensiya testi, plasebo, masofa bo'yicha ta'sir,
mavsumiy ko'tarilishga ta'sir. Kirish: data/repair_panel.csv, data/gw_levels_long.csv. Chiqish: results/ch4_repair_ext.json, figures/ch4_event_study.png"""
import re, json, numpy as np, pandas as pd, warnings, statsmodels.formula.api as smf, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
warnings.filterwarnings('ignore')
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
D = pd.read_csv('data/repair_panel.csv'); D['well'] = D.well.astype(str); R = {}
def fit(d, f, key):
    d = d.dropna(subset=[f.split('~')[0].strip()]); m = smf.ols(f, d).fit(cov_type='cluster', cov_kwds={'groups': d.well.astype('category').cat.codes}); return m
# 1) event study: bins et<=-4, -3, -2, (-1 ref), 0, 1, 2, 3, >=4
def b(e):
    if np.isnan(e): return 'ctrl'
    e = int(e); e = max(min(e, 4), -4); return 'ref' if e == -1 else f'e{e}'.replace('-', 'm')
D['eb'] = D.et.map(b)
m = fit(D, "level ~ C(eb, Treatment('ref')) + C(well) + C(year)", 'es')
names = [k for k in m.params.index if k.startswith('C(eb')]; es = []
for k in names:
    lab = k.split('[T.')[1].rstrip(']')
    if lab == 'ctrl': continue
    e = -int(lab[2:]) if lab.startswith('em') else int(lab[1:]); ci = m.conf_int().loc[k]
    es.append(dict(e=e, b=round(m.params[k], 3), lo=round(ci[0], 3), hi=round(ci[1], 3), p=round(m.pvalues[k], 3)))
es = sorted(es, key=lambda r: r['e']) + [dict(e=-1, b=0, lo=0, hi=0, p=None)]; es = sorted(es, key=lambda r: r['e']); R['event'] = es
pre = [k for k in names if 'em' in k]; R['pretrend_F'] = dict(F=round(float(m.f_test(' = '.join(pre) + ' = 0' if len(pre) == 1 else ', '.join(f'{k} = 0' for k in pre)).fvalue), 2),
                                                             p=round(float(m.f_test(', '.join(f'{k} = 0' for k in pre)).pvalue), 3))
# 2) placebo: shift repair year 3 years earlier, use only pre-repair years of treated
P = D[(D.grp == 'control') | (D.et < 0)].copy(); P['post'] = ((P.grp == 'treated') & (P.year > P.repair_year - 3)).astype(int)
mp = fit(P, 'level ~ post + C(well) + C(year)', 'pl'); ci = mp.conf_int().loc['post']; R['placebo'] = dict(b=round(mp.params.post, 3), lo=round(ci[0], 3), hi=round(ci[1], 3), p=round(mp.pvalues.post, 3), n=len(P))
# 3) distance bands
D['post_near'] = ((D.post == 1) & (D.dist <= 150)).astype(int); D['post_far'] = ((D.post == 1) & (D.dist > 150)).astype(int)
md = fit(D, 'level ~ post_near + post_far + C(well) + C(year)', 'dist')
R['dist'] = {k: dict(b=round(md.params[k], 3), lo=round(md.conf_int().loc[k][0], 3), hi=round(md.conf_int().loc[k][1], 3), p=round(md.pvalues[k], 3)) for k in ('post_near', 'post_far')}
R['dist_n'] = dict(near=int(D[(D.grp == 'treated') & (D.dist <= 150)].well.nunique()), far=int(D[(D.grp == 'treated') & (D.dist > 150)].well.nunique()))
# 4) cohorts
D['early'] = ((D.post == 1) & (D.repair_year <= 2017)).astype(int); D['late'] = ((D.post == 1) & (D.repair_year >= 2018)).astype(int)
mc = fit(D, 'level ~ early + late + C(well) + C(year)', 'coh')
R['cohort'] = {k: dict(b=round(mc.params[k], 3), p=round(mc.pvalues[k], 3)) for k in ('early', 'late')}
R['cohort_n'] = D[D.grp == 'treated'].drop_duplicates('well').repair_year.value_counts().sort_index().to_dict()
# 5) seasonal rise (winter - summer) per well-year
L = pd.read_csv('data/gw_levels_long.csv'); L['well'] = L.well_no.map(norm); L['lv'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
W = L[L.decade.between(1, 6)].groupby(['well', 'year'])['lv'].mean().rename('winter').reset_index()
D2 = D.merge(W, on=['well', 'year'], how='left'); D2['rise'] = D2.winter - D2.summer
ma = fit(D2, 'rise ~ post + C(well) + C(year)', 'rise'); ci = ma.conf_int().loc['post']
R['rise'] = dict(b=round(ma.params.post, 3), lo=round(ci[0], 3), hi=round(ci[1], 3), p=round(ma.pvalues.post, 3), n=int(D2.rise.notna().sum()), mean=round(D2.rise.mean(), 2))
# figure
E = pd.DataFrame(es); fig, ax = plt.subplots(figsize=(7, 4))
ax.axhline(0, color='#999'); ax.axvline(-0.5, color='#999', ls=':')
ax.errorbar(E.e, E.b, yerr=[E.b - E.lo, E.hi - E.b], fmt='o', color='#1f5fa8', capsize=3)
ax.set_xticks(range(-4, 5)); ax.set_xticklabels(['≤−4', '−3', '−2', '−1', '0', '1', '2', '3', '≥4'])
ax.set_xlabel('Ta\'mir yilidan beri o\'tgan yillar'); ax.set_ylabel('Nazoratga nisbatan sath farqi, m\n(musbat — chuqurlashish)'); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('figures/ch4_event_study.png', dpi=150)
json.dump(R, open('results/ch4_repair_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
