"""4.1-§ kengaytirilgan: ta'mir tartibi va yosh, ta'mir sikli, ichki zovurlar yoshi, massivlar bo'yicha ishonchlilik ko'rsatkichlari (GAT: kollektorlar-massivlar).
Chiqish: results/ch4_rel_ext.json, figures/ch4_massif_reliability.png"""
import json, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
from pyproj import Transformer
from matplotlib.path import Path
warnings.filterwarnings('ignore'); tr = Transformer.from_crs(4326, 32643, always_xy=True); R = {}
C = pd.read_csv('data/collectors.csv'); C['name'] = C.name.str.strip(); C['age'] = 2021 - C.commissioned; C['since'] = 2021 - C.repair_year
C['campaign'] = C.repair_year.between(2016, 2019)
# 1) repair order vs age / size
R['rho_repair_age'] = [round(x, 3) for x in stats.spearmanr(C.commissioned, C.repair_year)]
R['rho_repair_len'] = [round(x, 3) for x in stats.spearmanr(C.length_km, C.repair_year)]
R['rho_repair_q'] = [round(x, 3) for x in stats.spearmanr(C.q_end_m3s, C.repair_year)]
a, b = C[C.campaign].age, C[~C.campaign].age; R['age_campaign'] = dict(n_in=len(a), n_out=len(b), med_in=float(a.median()), med_out=float(b.median()), p=round(stats.mannwhitneyu(a, b).pvalue, 3))
R['old_vs_young'] = {g: dict(n=len(q), since_med=float(q.since.median()), share_last5=round((q.since <= 5).mean(), 2)) for g, q in C.groupby(pd.cut(C.age, [0, 55, 65, 200], labels=['<55', '55-65', '>65']))}
# 2) renewal cycle
per_year = C.groupby('repair_year').length_km.sum(); R['km_per_year_2010_2020'] = round(C.length_km.sum() / 11, 1); R['cycle_years'] = round(C.length_km.sum() / (C.length_km.sum() / 11), 1)
R['peak_share'] = round(C[C.repair_year.between(2016, 2019)].length_km.sum() / C.length_km.sum(), 3)
R['gini_years'] = round(per_year.max() / per_year.sum(), 3)
# 3) inner drains
I = pd.read_csv('data/inner_drains.csv'); I['age'] = 2021 - I.commissioned
I['dec'] = (I.commissioned // 10 * 10).astype(int)
R['inner_by_decade'] = {int(k): dict(n=len(q), km=round(q.length_km.sum(), 1), norep=round(q.repair_year.isna().mean(), 2)) for k, q in I.groupby('dec')}
R['inner_rep'] = dict(y2017=int((I.repair_year == 2017).sum()), y2018=int((I.repair_year == 2018).sum()), km2017=round(I[I.repair_year == 2017].length_km.sum(), 1), km2018=round(I[I.repair_year == 2018].length_km.sum(), 1))
a, b = I[I.repair_year.notna()].age, I[I.repair_year.isna()].age; R['inner_age_rep'] = dict(med_rep=float(a.median()), med_norep=float(b.median()), p=round(stats.mannwhitneyu(a, b).pvalue, 3))
R['inner_len'] = dict(rep=round(I[I.repair_year.notna()].length_km.median(), 2), norep=round(I[I.repair_year.isna()].length_km.median(), 2))
# 4) collectors -> massifs via named map segments
Cd = C.set_index('name'); mas = json.load(open('gis/massifs.geojson'))['features']; polys = {}
for f in mas:
    g = f['geometry']; pp = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    polys[f['properties']['massif']] = [Path(np.c_[tr.transform(*zip(*p[0]))]) for p in pp]
seg = []
for f in json.load(open('gis/collectors_named.geojson'))['features']:
    xy = np.c_[tr.transform(*zip(*f['geometry']['coordinates']))]; mid = (xy[:-1] + xy[1:]) / 2; ln = np.hypot(*(xy[1:] - xy[:-1]).T)
    nm = f['properties']['cad_name']; nm = nm.strip() if nm else None
    for m, ps in polys.items():
        ins = np.zeros(len(mid), bool)
        for p in ps: ins |= p.contains_points(mid)
        if ins.any(): seg.append(dict(massif=m, name=nm, km=ln[ins].sum() / 1000))
S = pd.DataFrame(seg); S['age'] = S.name.map(lambda n: Cd.age.get(n, np.nan) if n in Cd.index else np.nan); S['since'] = S.name.map(lambda n: Cd.since.get(n, np.nan) if n in Cd.index else np.nan)
MA = pd.read_csv('data/massif_areas.csv').set_index('massif')
imap = {'З.М.Бобур массиви': 'З.М.Бобур', 'Истиқлол массиви': 'Истиқлол', 'Й.Охунбобоев массиви': 'Й.Охунбобоев', 'Машъал массиви': 'Машъал', 'Пахтакор массиви': 'Пахтакор', 'Т.Мирзаев массиви': 'Т.Мирзаев', 'У.Қорабоев массиви': 'У.Қорабоев'}
I['m'] = I.massif.map(imap); rows = []
for m in MA.index:
    s = S[S.massif == m]; n = s.dropna(subset=['age']); ii = I[I.m == m]
    rows.append(dict(massif=m, irr_ha=int(MA.irrigated_ha[m]), coll_km=round(s.km.sum(), 1), named_share=round(n.km.sum() / max(s.km.sum(), 1e-9), 2), coll_m_ha=round(s.km.sum() * 1000 / MA.irrigated_ha[m], 1),
                     coll_age=round(np.average(n.age, weights=n.km), 0) if len(n) else None, coll_since=round(np.average(n.since, weights=n.km), 1) if len(n) else None,
                     inner_km=round(ii.length_km.sum(), 1), inner_m_ha=round(ii.length_km.sum() * 1000 / MA.irrigated_ha[m], 1), inner_norep=round(ii[ii.repair_year.isna()].length_km.sum() / max(ii.length_km.sum(), 1e-9), 2) if len(ii) else None,
                     inner_age=float(ii.age.median()) if len(ii) else None, open_m_ha=round((s.km.sum() + ii.length_km.sum()) * 1000 / MA.irrigated_ha[m], 1)))
M = pd.DataFrame(rows); R['massif'] = M.to_dict('records')
# composite: ranks (higher = weaker): low open density, high inner_norep, high coll_age, high coll_since
Z = M.set_index('massif'); comp = pd.concat([(-Z.open_m_ha).rank(), Z.inner_norep.rank(), Z.coll_age.rank(), Z.coll_since.rank()], axis=1).mean(axis=1)
R['composite_rank'] = comp.round(2).sort_values(ascending=False).to_dict()
lat = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': "M.To'jiboyev", 'Машъал': "Mash'al", 'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzayev', 'У.Қорабоев': 'U.Qoraboyev'}
fig, ax = plt.subplots(1, 2, figsize=(12, 4.3)); Mz = M.set_index('massif').loc[[k for k in lat if k in M.massif.values]]; xi = np.arange(len(Mz))
ax[0].bar(xi - .2, Mz.coll_m_ha, .4, color='#1f5fa8', label='Kollektorlar'); ax[0].bar(xi + .2, Mz.inner_m_ha, .4, color='#9ecae1', label='Ichki zovurlar')
ax[0].set_xticks(xi); ax[0].set_xticklabels([lat[k] for k in Mz.index], rotation=35, ha='right'); ax[0].set_ylabel('Solishtirma uzunlik, m/ga'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3, axis='y'); ax[0].set_title('a', loc='left')
ax[1].bar(xi, Mz.inner_norep.fillna(0) * 100, color=['#d6604d' if v >= .7 else '#4393c3' for v in Mz.inner_norep.fillna(0)]); ax[1].set_xticks(xi); ax[1].set_xticklabels([lat[k] for k in Mz.index], rotation=35, ha='right')
ax[1].set_ylabel('Ta\'mir qayd etilmagan ichki zovurlar, uzunlikning %i'); ax[1].grid(alpha=.3, axis='y'); ax[1].set_title('b', loc='left')
fig.tight_layout(); fig.savefig('figures/ch4_massif_reliability.png', dpi=150)
json.dump(R, open('results/ch4_rel_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
