"""Ta'mir ta'sirini aniqlash quvvati — Monte Karlo simulyatsiya (statistical-power skill, 2-band).
Ma'lumotlarga asoslangan jarayon: haqiqiy 85 ta quduqning (36 ta'sir + 49 nazorat) sath qatorlari quduqlar bo'yicha
qaytariladigan tanlov bilan olinadi (vaqt bo'yicha bog'liqlik va quduqlar orasidagi farq saqlanadi), har bir "ta'sir"
qudug'iga haqiqiy taqsimotdan ta'mir yili beriladi va ta'mirdan keyingi yillarga delta qo'shiladi; asosiy model
(quduq va yil qat'iy effektlari, quduqlar bo'yicha klasterli xato, ikki tomonlama alfa = 0,05) bilan baholanadi.
Haqiqiy ta'sir quduqlari qatorlari ham tanlovga kiradi, lekin ularning ta'mir yili tasodifan qayta beriladi.
Avval delta = 0 da I tur xato tekshiriladi. Chiqish: results/did_power_sim.json"""
import json, numpy as np, pandas as pd, warnings, statsmodels.api as sm
warnings.filterwarnings('ignore'); rng = np.random.default_rng(20261118)
D = pd.read_csv('data/repair_panel.csv'); D['well'] = D.well.astype(str); D = D.dropna(subset=['level'])
series = {w: q[['year', 'level']].values for w, q in D.groupby('well')}; wells = list(series)
ry = D[D.grp == 'treated'].drop_duplicates('well').repair_year.values
YRS = np.array(sorted(D.year.unique())); yidx = {y: i for i, y in enumerate(YRS)}
def one(nt, nc, delta):
    rows = []; tw = rng.choice(wells, nt); cw = rng.choice(wells, nc); k = 0
    for w in tw:
        r = rng.choice(ry); a = series[w]; post = (a[:, 0] >= r).astype(float)
        rows.append(np.c_[np.full(len(a), k), a[:, 0], a[:, 1] + delta * post, post]); k += 1
    for w in cw:
        a = series[w]; rows.append(np.c_[np.full(len(a), k), a[:, 0], a[:, 1], np.zeros(len(a))]); k += 1
    M = np.vstack(rows); g = M[:, 0].astype(int); y = M[:, 2]; post = M[:, 3]
    # ikki tomonlama qat'iy effektlar: o'zgaruvchilarni dummy orqali (tez: yil dummy + quduq bo'yicha demean emas, to'liq dummy)
    yd = np.eye(len(YRS))[[yidx[v] for v in M[:, 1]]][:, 1:]; wd = np.eye(k)[g][:, 1:]
    X = np.c_[np.ones(len(y)), post, yd, wd]
    m = sm.OLS(y, X).fit(cov_type='cluster', cov_kwds={'groups': g})
    return m.pvalues[1] < 0.05, m.bse[1]
def power(nt, nc, delta, S):
    r = [one(nt, nc, delta) for _ in range(S)]; p = np.mean([a for a, _ in r]); se = np.median([b for _, b in r])
    mc = 1.96 * np.sqrt(p * (1 - p) / S); return dict(nt=nt, nc=nc, delta=delta, power=round(p, 3), mc_ci=[round(max(0, p - mc), 3), round(min(1, p + mc), 3)], se_med=round(se, 3))
R = {'n_sims': 1000, 'type1': power(36, 49, 0.0, 2000)}; print(R['type1'])
R['grid'] = []
for nt, nc in [(36, 49), (60, 49), (78, 49), (100, 49), (78, 78), (100, 100), (150, 100)]:
    for d in (0.10, 0.15, 0.20, 0.30):
        r = power(nt, nc, d, 1000); R['grid'].append(r); print(r)
json.dump(R, open('results/did_power_sim.json', 'w'), indent=1)
