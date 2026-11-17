"""4.3-§: bosqichli (staggered) ta'mir dizayniga chidamli baholar (taqriz M2).
1) Callaway–Sant'Anna (2021) g'oyasi: har bir ta'mir yili kogortasi g va kuzatuv yili t uchun ATT(g,t) —
   faqat hech qachon ta'mirlanmagan nazorat quduqlari bilan, asos — g dan oldingi eng yaqin mavjud yil; keyin
   ta'mirdan keyingi (t >= g) kataklar kogorta hajmi bo'yicha o'rtachalanadi.
2) Imputatsiya bahosi (Borusyak, Jaravel, Spiess, 2024): quduq va yil qat'iy effektlari faqat ta'sirlanmagan
   kuzatuvlarda baholanadi, ta'sirlangan kuzatuvlar uchun kontrfaktual sath tiklanadi.
Ishonch oraliqlari — quduqlar bo'yicha klasterli bootstrap (999 takror). Chiqish: results/did_staggered.json"""
import json, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore'); rng = np.random.default_rng(7)
D0 = pd.read_csv('data/repair_panel.csv'); D0['well'] = D0.well.astype(str)
def cs(D, y='level', hmax=99):
    D = D.dropna(subset=[y]); C = D[D.grp == 'control']; T = D[D.grp == 'treated']
    yrs = sorted(D.year.unique()); cells = []
    cm = C.pivot_table(index='well', columns='year', values=y)
    for g, Tg in T.groupby('repair_year'):
        pre = [t for t in yrs if t < g]
        if not pre: continue
        base = max(pre); tm = Tg.pivot_table(index='well', columns='year', values=y)
        if base not in tm: continue
        for t in yrs:
            if t < g or t - g > hmax or t not in tm or t not in cm: continue
            a = (tm[t] - tm[base]).dropna(); c = (cm[t] - cm[base]).dropna()
            if len(a) and len(c) >= 5: cells.append((g, t, a.mean() - c.mean(), len(a)))
    if not cells: return np.nan, 0
    w = np.array([c[3] for c in cells], float); v = np.array([c[2] for c in cells]); return float((w * v).sum() / w.sum()), len(cells)
def imput(D, y='level'):
    import statsmodels.formula.api as smf
    D = D.dropna(subset=[y]).copy(); U = D[D.post == 0]; Tp = D[D.post == 1]
    m = smf.ols(f'{y} ~ C(well) + C(year)', U).fit()
    Tp = Tp[Tp.well.isin(U.well.unique()) & Tp.year.isin(U.year.unique())]
    return float((Tp[y] - m.predict(Tp)).mean()), len(Tp)
def boot(fun, D, B=999, **kw):
    wells = D.well.unique(); g = {w: D[D.well == w] for w in wells}; out = []
    for _ in range(B):
        s = rng.choice(wells, len(wells)); parts = []
        for j, w in enumerate(s): q = g[w].copy(); q['well'] = f'{w}_{j}'; parts.append(q)
        out.append(fun(pd.concat(parts), **kw)[0])
    out = np.array(out); out = out[~np.isnan(out)]; return np.percentile(out, [2.5, 97.5]), out
R = {}
for name, fun in [('cs', cs), ('imputation', imput)]:
    for y in ('level', 'summer'):
        est, k = fun(D0, y=y); ci, bs = boot(fun, D0, B=499 if name == 'imputation' else 999, y=y)
        p = float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean())))
        R[f'{name}_{y}'] = dict(att=round(est, 3), lo=round(float(ci[0]), 3), hi=round(float(ci[1]), 3), p=round(p, 3), cells_or_obs=k)
        print(name, y, R[f'{name}_{y}'])
est, k = cs(D0, hmax=3); ci, bs = boot(cs, D0, hmax=3); p = float(min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean())))
R['cs_level_h0_3'] = dict(att=round(est, 3), lo=round(float(ci[0]), 3), hi=round(float(ci[1]), 3), p=round(p, 3), cells_or_obs=k); print('cs h<=3', R['cs_level_h0_3'])
# misclassification: share of 'treated' wells whose collector repair section is unknown -> attenuation toward 0
json.dump(R, open('results/did_staggered.json', 'w'), ensure_ascii=False, indent=1)
