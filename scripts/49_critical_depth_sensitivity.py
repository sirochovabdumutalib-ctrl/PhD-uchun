"""Kritik chuqurlik va ehtimollik usuliga sezgirlik (taqriz: kritik chuqurlik, m10).
Kritik chuqurlik 1,5; 2,0; 2,5 m uchun: yozda sathi undan sayoz quduqlar ulushi, kriging xaritasidagi maydon,
P > 0,3 maydon (tuman va massivlar bo'yicha), sho'rlanish xavfli quduqlar (minerallashuv >= 1 g/l).
1,5 m uchun ehtimollik uch usulda: oddiy kriging (asosiy), log-kriging va indikator kriging.
Chiqish: results/critical_depth_sensitivity.json"""
import os, sys, re, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('k41', 'scripts/41_fig35_kriging.py'); k41 = importlib.util.module_from_spec(spec); spec.loader.exec_module(k41)
from carto import *
from scipy import stats
from shapely import contains_xy
from pykrige.ok import OrdinaryKriging
x, y, v, P, gx, gy, GX, GY, Z, SE, dmin = k41.krige('level_summer_m')
M = massifs(); near = dmin <= 1500; ins = {r['name']: contains_xy(r.geometry, GX, GY) & near for _, r in M.iterrows()}
anyin = np.zeros(Z.shape, bool)
for k in ins: anyin |= ins[k]
TOP = ['Mashʼal', 'Z.M.Bobur', 'Istiqlol']
def ok_vals(vals):
    p = k41.fitv(x, y, vals); o = OrdinaryKriging(x, y, vals, variogram_model='exponential', variogram_parameters={'psill': p[0], 'range': p[1], 'nugget': p[2]})
    z, s2 = o.execute('grid', gx, gy); return np.asarray(z), np.sqrt(np.asarray(s2))
def shares(PR):
    return dict(district=round(float((PR[anyin] > .3).mean()) * 100, 1), **{k: round(float((PR[ins[k]] > .3).mean()) * 100, 1) for k in ins})
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')
W = pd.read_csv('data/wells_metrics.csv'); W['well'] = W.well_no.map(norm)
mm = pd.read_csv('data/miner_1999_2015.csv'); mm['well'] = mm.well_no.map(norm); mm = mm[mm.year.between(2004, 2010)].dropna(subset=['miner_gl'])
Q = W.merge(mm.groupby('well').miner_gl.median().rename('mmed'), left_on='well', right_index=True).dropna(subset=['level_summer_m'])
R = {'n_wells': int(W.level_summer_m.notna().sum()), 'n_risk': len(Q), 'thresholds': {}}
for h in (1.5, 2.0, 2.5):
    PR = stats.norm.cdf((h - Z) / SE)
    R['thresholds'][str(h)] = dict(wells_pct=round(float((W.level_summer_m < h).mean() / W.level_summer_m.notna().mean()) * 100, 1),
                                   wells_n=int((W.level_summer_m < h).sum()), map_pct=round(float((Z[anyin] < h).mean()) * 100, 1),
                                   p30=shares(PR), risk_wells=int(((Q.level_summer_m < h) & (Q.mmed >= 1)).sum()))
# 1,5 m: muqobil ehtimollik usullari
lz, lse = ok_vals(np.log(v)); R['p30_log'] = shares(stats.norm.cdf((np.log(1.5) - lz) / lse))
iz, _ = ok_vals((v < 1.5).astype(float)); R['p30_indicator'] = shares(np.clip(iz, 0, 1)); R['p30_ok'] = R['thresholds']['1.5']['p30']
rank = lambda d: sorted([k for k in d if k != 'district'], key=lambda k: -d[k])[:3]
R['top3'] = {k: rank(R[k]) for k in ('p30_ok', 'p30_log', 'p30_indicator')}
json.dump(R, open('results/critical_depth_sensitivity.json', 'w'), ensure_ascii=False, indent=1); print(json.dumps(R, ensure_ascii=False, indent=1))
