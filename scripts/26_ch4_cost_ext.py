"""4.4-§ kengaytirilgan: ta'mir narxi va balans qiymati, hajm samarasi, xizmat maydoniga nisbatan xarajat, xarajatlarning massivlar bo'yicha taqsimoti (GAT).
Chiqish: results/ch4_cost_ext.json, figures/ch4_cost_massif.png"""
import json, numpy as np, pandas as pd, warnings, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from scipy import stats
from pyproj import Transformer
from matplotlib.path import Path
warnings.filterwarnings('ignore'); tr = Transformer.from_crs(4326, 32643, always_xy=True); R = {}
C = pd.read_csv('data/collectors.csv'); C['name'] = C.name.str.strip()
K = pd.read_csv('results/ch4_repair_costs.csv'); K['name'] = K.name.str.strip(); K = K.merge(C[['name', 'service_ha', 'balance_value', 'commissioned']], on='name', how='left')
K['cost_ha'] = K.repair_cost_mln / K.service_ha; K['to_balance'] = K.repair_cost_mln / K.balance_value
R['n'] = len(K)
R['to_balance'] = dict(med=round(K.to_balance.median(), 2), q25=round(K.to_balance.quantile(.25), 2), q75=round(K.to_balance.quantile(.75), 2), total=round(K.repair_cost_mln.sum() / K.balance_value.sum(), 2))
R['balance_total_all'] = round(C.balance_value.sum()); R['balance_repaired'] = round(K.balance_value.sum())
R['cost_ha'] = dict(med=round(K.cost_ha.median(), 2), q25=round(K.cost_ha.quantile(.25), 2), q75=round(K.cost_ha.quantile(.75), 2), total=round(K.repair_cost_mln.sum() / K.service_ha.sum(), 2), ha=round(K.service_ha.sum()))
s = stats.linregress(np.log10(K.rep_km), np.log10(K.cost_km)); R['scale'] = dict(slope=round(s.slope, 3), p=round(s.pvalue, 4), r2=round(s.rvalue ** 2, 3))
R['rho_cost_age'] = [round(x, 3) for x in stats.spearmanr(2021 - K.commissioned, K.cost_km)]
R['by_len'] = {str(k): dict(n=len(q), cost_km=round(q.cost_km.median(), 1)) for k, q in K.groupby(pd.cut(K.rep_km, [0, 1, 3, 100], labels=['<1 km', '1-3 km', '>3 km']))}
# massif assignment by majority of named segment length
mas = json.load(open('gis/massifs.geojson'))['features']; polys = {}
for f in mas:
    g = f['geometry']; pp = g['coordinates'] if g['type'] == 'MultiPolygon' else [g['coordinates']]
    polys[f['properties']['massif']] = [Path(np.c_[tr.transform(*zip(*p[0]))]) for p in pp]
seg = []
for f in json.load(open('gis/collectors_named.geojson'))['features']:
    nm = f['properties']['cad_name']
    if not nm: continue
    xy = np.c_[tr.transform(*zip(*f['geometry']['coordinates']))]; mid = (xy[:-1] + xy[1:]) / 2; ln = np.hypot(*(xy[1:] - xy[:-1]).T)
    for m, ps in polys.items():
        ins = np.zeros(len(mid), bool)
        for p in ps: ins |= p.contains_points(mid)
        if ins.any(): seg.append(dict(name=nm.strip(), massif=m, km=ln[ins].sum() / 1000))
S = pd.DataFrame(seg).groupby(['name', 'massif']).km.sum().reset_index()
share = S.assign(sh=S.km / S.groupby('name').km.transform('sum'))
KM = K.merge(share, on='name', how='left'); KM['cost_m'] = KM.repair_cost_mln * KM.sh
R['mapped'] = dict(n=int(KM.dropna(subset=['massif']).name.nunique()), cost=round(KM.cost_m.sum()), share=round(KM.cost_m.sum() / K.repair_cost_mln.sum(), 3))
MA = pd.read_csv('data/massif_areas.csv').set_index('massif')
by = KM.dropna(subset=['massif']).groupby('massif').agg(cost=('cost_m', 'sum'), n=('name', 'nunique')).reindex(MA.index).fillna(0)
by['irr_ha'] = MA.irrigated_ha; by['cost_per_ha'] = (by.cost / by.irr_ha * 1000).round(0)  # ming so'm/ga
risk = {'З.М.Бобур': 17, 'Истиқлол': 12, 'Й.Охунбобоев': None, 'М.Тожибоев': 4, 'Машъал': 17, 'Пахтакор': 4, 'Т.Мирзаев': 1, 'У.Қорабоев': 1}
p30 = {'З.М.Бобур': 58, 'Истиқлол': 55, 'Й.Охунбобоев': 0, 'М.Тожибоев': 17, 'Машъал': 71, 'Пахтакор': 21, 'Т.Мирзаев': 28, 'У.Қорабоев': 19}
by['risk_wells'] = pd.Series(risk); by['p30'] = pd.Series(p30)
R['by_massif'] = by.reset_index().round(1).to_dict('records')
q = by.dropna(subset=['risk_wells']); R['rho_cost_risk'] = [round(x, 3) for x in stats.spearmanr(q.cost_per_ha, q.p30)]
lat = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': "M.To'jiboyev", 'Машъал': "Mash'al", 'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzayev', 'У.Қорабоев': 'U.Qoraboyev'}
fig, ax = plt.subplots(figsize=(6.5, 4.5))
for m, r in by.iterrows():
    ax.scatter(r.p30, r.cost_per_ha, s=40 + r.irr_ha / 30, c='#1f5fa8', alpha=.7, edgecolor='k'); ax.annotate(lat[m], (r.p30, r.cost_per_ha), xytext=(5, 4), textcoords='offset points', fontsize=8)
ax.set_xlabel("Yozda sath 1,5 m dan sayoz bo'lish ehtimoli 0,3 dan katta maydon, %"); ax.set_ylabel("Ta'mir xarajati, ming so'm/ga (2017–2020)"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig('figures/ch4_cost_massif.png', dpi=150)
json.dump(R, open('results/ch4_cost_ext.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
