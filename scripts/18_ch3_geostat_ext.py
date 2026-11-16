"""3.3-§ kengaytirilgan geostatistika: taqsimot, anizotropiya, trendli kriging (UK, RK) bilan qiyos, yozgi sath xaritasi,
sayoz sath ehtimoli xaritasi, massivlar bo'yicha maydon ulushlari, tarmoq zichligi tajribasi.
Chiqish: results/ch3_geo_ext.json, figures/ch3_variogram.png, figures/ch3_summer_prob.png, figures/ch3_density.png"""
import json, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from matplotlib.path import Path
from scipy import stats
from scipy.spatial import cKDTree
from pykrige.ok import OrdinaryKriging
from pykrige.uk import UniversalKriging
from pyproj import Transformer
import statsmodels.api as sm
warnings.filterwarnings('ignore'); rng = np.random.default_rng(42)
D = lambda q: {'psill': q[0], 'range': q[1], 'nugget': q[2]}  # pykrige: ro'yxat [to'liq plato, radius, nagget] deb o'qiladi, shuning uchun lug'at
tr = Transformer.from_crs(4326, 32643, always_xy=True)
W = pd.read_csv('data/wells_metrics.csv')
R = {}

def loo(x, y, v, model, params, drift=None):
    e, s = [], []
    for i in range(len(x)):
        m = np.arange(len(x)) != i
        if drift is None:
            o = OrdinaryKriging(x[m], y[m], v[m], variogram_model=model, variogram_parameters=D(params))
        else:
            o = UniversalKriging(x[m], y[m], v[m], variogram_model=model, variogram_parameters=D(params), drift_terms=[drift])
        p, s2 = o.execute('points', x[i:i + 1], y[i:i + 1]); e.append(float(p[0]) - v[i]); s.append(float(np.sqrt(max(s2[0], 1e-9))))
    e, s = np.array(e), np.array(s)
    return dict(me=round(e.mean(), 3), rmse=round(np.sqrt((e ** 2).mean()), 3), rmsse=round(np.sqrt(((e / s) ** 2).mean()), 3))

from scipy.optimize import curve_fit
VG = {'exponential': lambda h, ps, r, n: n + ps * (1 - np.exp(-h / r)),
      'spherical': lambda h, ps, r, n: n + ps * np.where(h < r, 1.5 * h / r - 0.5 * (h / r) ** 3, 1.0),
      'gaussian': lambda h, ps, r, n: n + ps * (1 - np.exp(-(h / r) ** 2))}
def empv(x, y, v, maxd=10000, step=500):
    h = np.hypot(x[:, None] - x[None], y[:, None] - y[None]); g = 0.5 * (v[:, None] - v[None]) ** 2; iu = np.triu_indices(len(v), 1); h, g = h[iu], g[iu]
    lags = np.arange(0, maxd + 1, step); mid, gam, npr = [], [], []
    for k in range(len(lags) - 1):
        m = (h > lags[k]) & (h <= lags[k + 1])
        if m.sum() >= 20: mid.append(h[m].mean()); gam.append(g[m].mean()); npr.append(m.sum())
    return np.array(mid), np.array(gam), np.array(npr)
def fitv(x, y, v, model):
    mid, gam, npr = empv(x, y, v); f = VG[model]; sig = gam / np.sqrt(npr)
    pr = {'exponential': 3000, 'spherical': 8000, 'gaussian': 4000}[model]
    p, _ = curve_fit(f, mid, gam, p0=[gam.max() - gam.min(), pr, gam.min()], sigma=sig, bounds=([0.01, 300, 0], [5, 30000, 2]), maxfev=20000)
    return [float(q) for q in p]
R['vgm_fit'] = {}
for var in ('level_2019_2024_m', 'level_summer_m'):
    K = W.dropna(subset=[var]).copy(); x, y, v = K.x_utm43.values, K.y_utm43.values, K[var].values
    r = dict(n=len(v), mean=round(v.mean(), 3), median=round(np.median(v), 3), sd=round(v.std(), 3), skew=round(stats.skew(v), 2),
             shapiro_p=round(stats.shapiro(v).pvalue, 4), skew_log=round(stats.skew(np.log(v)), 2), shapiro_log_p=round(stats.shapiro(np.log(v)).pvalue, 4))
    # trend surface
    X = sm.add_constant(np.c_[(x - x.mean()) / 1000, (y - y.mean()) / 1000]); ts = sm.OLS(v, X).fit()
    r['trend'] = dict(r2=round(ts.rsquared, 3), bx=round(ts.params[1], 4), by=round(ts.params[2], 4), px=round(ts.pvalues[1], 4), py=round(ts.pvalues[2], 4))
    # OK exponential
    comp = {}
    for mdl in ('spherical', 'exponential', 'gaussian'):
        q = fitv(x, y, v, mdl); cv = loo(x, y, v, mdl, q); comp[mdl] = dict(psill=round(q[0], 3), range_m=round(q[1]), nugget=round(q[2], 3), sill=round(q[0] + q[2], 3), nug_ratio=round(q[2] / (q[0] + q[2]), 2), **cv)
    R['vgm_fit'][var] = comp; best = min(comp, key=lambda k: comp[k]['rmse']); r['best'] = best
    P = fitv(x, y, v, 'exponential')
    r['ok_params'] = dict(psill=round(P[0], 3), range_m=round(P[1]), nugget=round(P[2], 3))
    r['cv_ok'] = loo(x, y, v, 'exponential', P)
    # OK on residuals of trend (variogram of residuals) -> UK with regional linear drift
    Pr = fitv(x, y, np.asarray(ts.resid), 'exponential')
    r['res_params'] = dict(psill=round(Pr[0], 3), range_m=round(Pr[1]), nugget=round(Pr[2], 3), nug_ratio=round(Pr[2] / (Pr[0] + Pr[2]), 2))
    r['cv_uk'] = loo(x, y, v, 'exponential', Pr, drift='regional_linear')
    # regression kriging with network covariates (log distance to collector, collector density)
    Xc = sm.add_constant(np.c_[np.log10(K.dist_collector_m + 10), K.collector_len_1km_m / 1000]); e, s = [], []
    for i in range(len(v)):
        m = np.arange(len(v)) != i; f = sm.OLS(v[m], Xc[m]).fit(); res = v[m] - f.predict(Xc[m])
        o = OrdinaryKriging(x[m], y[m], res, variogram_model='exponential', variogram_parameters=D(Pr))
        p, s2 = o.execute('points', x[i:i + 1], y[i:i + 1]); e.append(f.predict(Xc[i:i + 1])[0] + float(p[0]) - v[i]); s.append(np.sqrt(s2[0]))
    e = np.array(e); r['cv_rk'] = dict(me=round(e.mean(), 3), rmse=round(np.sqrt((e ** 2).mean()), 3), rmsse=round(np.sqrt(((e / np.array(s)) ** 2).mean()), 3))
    # nearest-neighbour and mean baselines
    d, j = cKDTree(np.c_[x, y]).query(np.c_[x, y], k=2); r['cv_nn'] = round(np.sqrt(((v[j[:, 1]] - v) ** 2).mean()), 3)
    r['cv_mean'] = round(np.sqrt((((v.sum() - v) / (len(v) - 1) - v) ** 2).mean()), 3)
    R[var] = r
    if var == 'level_2019_2024_m':
        # anisotropy: directional semivariance at lags 0.5-5 km
        dx, dy = x[:, None] - x[None], y[:, None] - y[None]; h = np.hypot(dx, dy); g = 0.5 * (v[:, None] - v[None]) ** 2
        ang = (np.degrees(np.arctan2(dx, dy)) + 180) % 180; iu = np.triu_indices(len(v), 1)
        h, g, ang = h[iu], g[iu], ang[iu]; lags = np.arange(0, 8001, 500); emp = {}
        for name, a0 in (('Sh–J (0°)', 0), ('ShSh–JG\' (45°)', 45), ('G\'–Sh (90°)', 90), ('ShG\'–JSh (135°)', 135)):
            da = np.minimum(np.abs(ang - a0), 180 - np.abs(ang - a0)); m = da <= 22.5
            emp[name] = [float(g[m & (h > lags[k]) & (h <= lags[k + 1])].mean()) for k in range(len(lags) - 1)]
        omni = [float(g[(h > lags[k]) & (h <= lags[k + 1])].mean()) for k in range(len(lags) - 1)]
        npairs = [int(((h > lags[k]) & (h <= lags[k + 1])).sum()) for k in range(len(lags) - 1)]
        R['aniso'] = {k: round(float(np.mean(vv[:6])), 3) for k, vv in emp.items()}; R['omni_first'] = [round(q, 3) for q in omni[:6]]; R['npairs_first'] = npairs[:6]
        mid = (lags[:-1] + lags[1:]) / 2
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        ax[0].plot(mid / 1000, omni, 'ko', label='Empirik (barcha yo\'nalishlar)')
        hh = np.linspace(0, 8000, 200); ax[0].plot(hh / 1000, P[2] + P[0] * (1 - np.exp(-hh / P[1])), 'b-', label='Eksponensial model')
        ax[0].plot(hh / 1000, VG['spherical'](hh, *fitv(x, y, v, 'spherical')), 'g-.', label='Sferik model')
        ax[0].axhline(v.var(), color='#999', ls=':', label='Ma\'lumot dispersiyasi'); ax[0].set_xlabel('Masofa, km'); ax[0].set_ylabel('Yarimvariogramma, m²'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3)
        for (k, vv), c in zip(emp.items(), ['#1f5fa8', '#d95f02', '#1b9e77', '#7570b3']): ax[1].plot(mid / 1000, vv, 'o-', color=c, label=k, ms=4)
        ax[1].set_xlabel('Masofa, km'); ax[1].set_ylabel('Yarimvariogramma, m²'); ax[1].legend(fontsize=8); ax[1].grid(alpha=.3)
        fig.tight_layout(); fig.savefig('figures/ch3_variogram.png', dpi=150); plt.close(fig)
        # network density experiment
        test_n = 34; out = []
        for frac in (0.25, 0.4, 0.55, 0.7, 0.85, 1.0):
            errs, nnd = [], []
            for rep in range(40):
                idx = rng.permutation(len(v)); te, trn = idx[:test_n], idx[test_n:]; trn = trn[:max(12, int(round(frac * len(trn))))]
                o = OrdinaryKriging(x[trn], y[trn], v[trn], variogram_model='exponential', variogram_parameters=D(P))
                p, _ = o.execute('points', x[te], y[te]); errs.append(np.sqrt(((p - v[te]) ** 2).mean()))
                nnd.append(np.median(cKDTree(np.c_[x[trn], y[trn]]).query(np.c_[x[trn], y[trn]], k=2)[0][:, 1]))
            out.append(dict(frac=frac, n=int(round(frac * (len(v) - test_n))), nn_m=round(float(np.mean(nnd))), rmse=round(float(np.mean(errs)), 3), rmse_sd=round(float(np.std(errs)), 3)))
        R['density'] = out
        o = OrdinaryKriging(x, y, v, variogram_model='exponential', variogram_parameters=D(P))
        gx = np.arange(x.min() - 500, x.max() + 500, 150); gy = np.arange(y.min() - 500, y.max() + 500, 150); Z, S2 = o.execute('grid', gx, gy); SE = np.sqrt(S2)
        GX, GY = np.meshgrid(gx, gy); dmin = cKDTree(np.c_[x, y]).query(np.c_[GX.ravel(), GY.ravel()])[0].reshape(Z.shape); mask = dmin > 1500
        R['annual_map'] = dict(se_min=round(float(SE[~mask].min()), 2), se_max=round(float(SE[~mask].max()), 2), sh20=round(float((Z[~mask] < 2.0).mean()), 3), sh15=round(float((Z[~mask] < 1.5).mean()), 3),
                               zmin=round(float(Z[~mask].min()), 2), zmax=round(float(Z[~mask].max()), 2), var_ratio=round(float(np.var(o.execute('points', x, y)[0]) / v.var()), 2))
        net = json.load(open('gis/collectors.geojson'))['features']
        fig, ax = plt.subplots(1, 2, figsize=(12, 5.6))
        for a, data, cm, lab in ((ax[0], np.ma.masked_where(mask, Z), 'RdYlBu', 'Sizot suvi sathi, m'), (ax[1], np.ma.masked_where(mask, SE), 'YlOrRd', 'Bahoning standart xatosi, m')):
            im = a.pcolormesh(gx / 1000, gy / 1000, data, cmap=cm, shading='auto'); plt.colorbar(im, ax=a, label=lab, shrink=.8)
            for f in net:
                cx, cy = tr.transform(*zip(*f['geometry']['coordinates'])); a.plot(np.array(cx) / 1000, np.array(cy) / 1000, color='#2a7a2a', lw=.6)
            a.scatter(x / 1000, y / 1000, s=6, c='k'); a.set_aspect(1); a.set_xlabel('X, km (UTM 43N)'); a.set_ylabel('Y, km')
        fig.tight_layout(); fig.savefig('figures/ch3_kriging.png', dpi=150); plt.close(fig)
        fig, a = plt.subplots(figsize=(6, 4)); dd = pd.DataFrame(out)
        a.errorbar(dd.n, dd.rmse, yerr=dd.rmse_sd, fmt='o-', color='#1f5fa8', capsize=3); a.axhline(r['cv_mean'], color='#999', ls=':', label='O\'rtacha qiymat bilan baho')
        for _, q in dd.iterrows(): a.annotate(f"{int(q.nn_m)} m", (q.n, q.rmse), textcoords='offset points', xytext=(4, 6), fontsize=8)
        a.set_xlabel('Modelga kiritilgan quduqlar soni'); a.set_ylabel('Nazorat quduqlaridagi xato (RMSE), m'); a.legend(fontsize=8); a.grid(alpha=.3)
        fig.tight_layout(); fig.savefig('figures/ch3_density.png', dpi=150); plt.close(fig)
    else:
        # summer map + probability of shallow level, by massif
        o = OrdinaryKriging(x, y, v, variogram_model='exponential', variogram_parameters=D(P))
        gx = np.arange(x.min() - 500, x.max() + 500, 150); gy = np.arange(y.min() - 500, y.max() + 500, 150); Z, S2 = o.execute('grid', gx, gy); SE = np.sqrt(S2)
        GX, GY = np.meshgrid(gx, gy); dmin = cKDTree(np.c_[x, y]).query(np.c_[GX.ravel(), GY.ravel()])[0].reshape(Z.shape)
        Pr15 = stats.norm.cdf((1.5 - Z) / SE); mask = dmin > 1500
        Zm, Pm = np.ma.masked_where(mask, Z), np.ma.masked_where(mask, Pr15)
        mas = json.load(open('gis/massifs.geojson'))['features']; byM = {}; inside_any = np.zeros(Z.shape, bool)
        for f in mas:
            geom = f['geometry']; polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
            ins = np.zeros(Z.shape, bool)
            for poly in polys:
                cx, cy = tr.transform(*zip(*poly[0])); ins |= Path(np.c_[cx, cy]).contains_points(np.c_[GX.ravel(), GY.ravel()]).reshape(Z.shape)
            inside_any |= ins; m = ins & ~mask
            byM[f['properties']['massif']] = dict(cover=round(m.sum() / max(ins.sum(), 1), 2), mean=round(float(Z[m].mean()), 2) if m.any() else None,
                                                  sh15=round(float((Z[m] < 1.5).mean()), 3) if m.any() else None, sh20=round(float((Z[m] < 2.0).mean()), 3) if m.any() else None,
                                                  p50=round(float((Pr15[m] > 0.5).mean()), 3) if m.any() else None, p30=round(float((Pr15[m] > 0.3).mean()), 3) if m.any() else None,
                                                  se=round(float(SE[m].mean()), 2) if m.any() else None)
        m = inside_any & ~mask
        R['summer_map'] = dict(sh15=round(float((Z[m] < 1.5).mean()), 3), sh20=round(float((Z[m] < 2.0).mean()), 3), p50=round(float((Pr15[m] > 0.5).mean()), 3), p30=round(float((Pr15[m] > 0.3).mean()), 3),
                               cover=round(float(m.sum() / inside_any.sum()), 3), se_min=round(float(SE[m].min()), 2), se_max=round(float(SE[m].max()), 2), by_massif=byM)
        net = json.load(open('gis/collectors.geojson'))['features']
        fig, ax = plt.subplots(1, 2, figsize=(12, 5.6))
        for a, data, cm, lab, vmin, vmax in ((ax[0], Zm, 'RdYlBu', 'Iyul–avgustdagi sath, m', 0.8, 4.0), (ax[1], Pm, 'Reds', 'Sath 1,5 m dan sayoz bo\'lish ehtimoli', 0, 1)):
            im = a.pcolormesh(gx / 1000, gy / 1000, data, cmap=cm, shading='auto', vmin=vmin, vmax=vmax); plt.colorbar(im, ax=a, label=lab, shrink=.8)
            for f in mas:
                geom = f['geometry']; polys = geom['coordinates'] if geom['type'] == 'MultiPolygon' else [geom['coordinates']]
                for poly in polys:
                    cx, cy = tr.transform(*zip(*poly[0])); a.plot(np.array(cx) / 1000, np.array(cy) / 1000, color='#444', lw=.7)
            for f in net:
                cx, cy = tr.transform(*zip(*f['geometry']['coordinates'])); a.plot(np.array(cx) / 1000, np.array(cy) / 1000, color='#2a7a2a', lw=.5)
            a.scatter(x / 1000, y / 1000, s=5, c='k'); a.set_aspect(1); a.set_xlabel('X, km (UTM 43N)'); a.set_ylabel('Y, km')
        fig.tight_layout(); fig.savefig('figures/ch3_summer_prob.png', dpi=150); plt.close(fig)
json.dump(R, open('results/ch3_geo_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o))[:6000])
