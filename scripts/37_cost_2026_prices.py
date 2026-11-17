"""Ta'mir xarajatlarini 2026-yil oktabr narxlariga keltirish (4.4, 4.6-§, 7-xarita).
Indeks: O'zbekiston iste'mol narxlari indeksi (Milliy statistika qo'mitasi), dekabr/dekabr:
2017 14,4; 2018 14,3; 2019 15,2; 2020 11,1; 2021 9,98; 2022 12,3; 2023 8,77; 2024 9,8; 2025 7,3 foiz; 2026-yil yanvar–oktabr 4,8 foiz.
Y-yil xarajati shu yilning o'rtacha narxlarida deb qabul qilinadi: k(Y) = sqrt(1+π_Y) · Π_{t=Y+1..2025}(1+π_t) · 1,048.
Avval nominal narxlarda matndagi raqamlar qayta hosil qilinadi (tekshiruv), so'ng xuddi shu hisob 2026-yil narxlarida bajariladi.
Chiqish: results/cost_2026.json"""
import os, json, numpy as np, pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PI = {2017: .144, 2018: .143, 2019: .152, 2020: .111, 2021: .0998, 2022: .123, 2023: .0877, 2024: .098, 2025: .073}; YTD26 = .048
def k(y):
    f = np.sqrt(1 + PI[y])
    for t in range(y + 1, 2026): f *= 1 + PI[t]
    return f * (1 + YTD26)
KF = {y: round(k(y), 3) for y in (2017, 2018, 2019, 2020)}
C = pd.read_csv('data/collectors.csv'); C['name'] = C.name.str.strip()
K = pd.read_csv('results/ch4_repair_costs.csv'); K['name'] = K.name.str.strip()
K = K.merge(C[['name', 'service_ha']], on='name', how='left')
K['f'] = K.repair_year.map(KF)

def stats(cost):
    d = K.assign(c=cost); d['ckm'] = d.c / d.rep_km
    light = d[d.cost_km < 50]; cap = d[d.cost_km >= 50]          # tur bo'yicha ajratish nominal narx bo'yicha (4.4-§)
    short = d[d.rep_km < 1]; mid = d[(d.rep_km >= 1) & (d.rep_km < 3)]
    alt = short.rep_km.sum() * mid.ckm.median()
    w_cap = cap.c.sum() / cap.rep_km.sum(); w_light = light.c.sum() / light.rep_km.sum()
    return dict(total=round(d.c.sum()), per_year=round(d.c.sum() / 4), by_year={int(y): round(q.c.sum()) for y, q in d.groupby('repair_year')},
                km=round(d.rep_km.sum(), 1), wmean_km=round(d.c.sum() / d.rep_km.sum(), 1), med_km=round(d.ckm.median(), 1),
                light_range=[round(light.ckm.min(), 1), round(light.ckm.max(), 1)], cap_p10_p90=[round(cap.ckm.quantile(.1)), round(cap.ckm.quantile(.9))],
                max_km=[d.loc[d.ckm.idxmax(), 'name'], round(d.ckm.max(), 1)],
                bins={b: round(q.ckm.median()) for b, q in d.groupby(pd.cut(d.rep_km, [0, 1, 3, 100], labels=['<1', '1-3', '>3']), observed=True)},
                per_ha_w=round(d.c.sum() / d.service_ha.sum(), 2), per_ha_med=round((d.c / d.service_ha).median(), 2),
                short=dict(n=len(short), km=round(short.rep_km.sum(), 1), cost=round(short.c.sum()), mid_price=round(mid.ckm.median()), alt=round(alt), saving=round(short.c.sum() - alt),
                           saving_pct=round(100 * (1 - alt / short.c.sum()))),
                cap=dict(n=len(cap), km=round(cap.rep_km.sum(), 1), w=round(w_cap)), light=dict(n=len(light), km=round(light.rep_km.sum(), 1), w=round(w_light)),
                save25=round(.25 * cap.rep_km.sum() * (w_cap - w_light) / 1000, 1), save50=round(.5 * cap.rep_km.sum() * (w_cap - w_light) / 1000, 1),
                save_pct=[round(100 * .25 * cap.rep_km.sum() * (w_cap - w_light) / d.c.sum()), round(100 * .5 * cap.rep_km.sum() * (w_cap - w_light) / d.c.sum())])

R = dict(index=dict(cpi_dec_dec=PI, ytd_2026_oct=YTD26, factors=KF, method='mid-year of repair year -> October 2026'),
         nominal=stats(K.repair_cost_mln), prices2026=stats(K.repair_cost_mln * K.f))
# massivlar bo'yicha (26-skriptdagi taqsimot ulushlari bilan)
from pyproj import Transformer
from matplotlib.path import Path
tr = Transformer.from_crs(4326, 32643, always_xy=True)
polys = {}
for f in json.load(open('gis/massifs.geojson'))['features']:
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
S = pd.DataFrame(seg).groupby(['name', 'massif']).km.sum().reset_index(); S['sh'] = S.km / S.groupby('name').km.transform('sum')
KM = K.merge(S, on='name', how='inner'); KM['nom'] = KM.repair_cost_mln * KM.sh; KM['r26'] = KM.repair_cost_mln * KM.f * KM.sh
MA = pd.read_csv('data/massif_areas.csv').set_index('massif')
by = KM.groupby('massif').agg(nom=('nom', 'sum'), r26=('r26', 'sum'), n=('name', 'nunique')).reindex(MA.index).fillna(0)
by['irr_ha'] = MA.irrigated_ha; by['nom_ha'] = (by.nom / by.irr_ha * 1000).round(); by['r26_ha'] = (by.r26 / by.irr_ha * 1000).round()
R['massif'] = by.round(1).reset_index().to_dict('records')
R['massif_total'] = dict(nom=round(by.nom.sum()), r26=round(by.r26.sum()), nom_ha=round(by.nom.sum() / by.irr_ha.sum() * 1000), r26_ha=round(by.r26.sum() / by.irr_ha.sum() * 1000))
json.dump(R, open('results/cost_2026.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps(R, ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
