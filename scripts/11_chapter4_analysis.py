"""IV bob hisoblari: kollektor va zovurlarning yoshi va ta'mir tarixi, drenaj moduli, ta'mir narxi,
ta'mir samarasini aniqlash uchun zarur quduqlar soni. Chiqish: results/ch4.json, figures/ch4_*.png"""
import json, re, numpy as np, pandas as pd, warnings
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
warnings.filterwarnings('ignore'); R = {}; REF = 2021                      # kadastr 2021-01-01 holatiga
C = pd.read_csv('data/collectors.csv'); D = pd.read_csv('data/inner_drains.csv')
for T in (C, D):
    T['commissioned'] = pd.to_numeric(T.commissioned, errors='coerce'); T['repair_year'] = pd.to_numeric(T.repair_year, errors='coerce')
    T['age'] = REF - T.commissioned; T['since_repair'] = REF - T.repair_year
def desc(s): return dict(min=float(s.min()), q25=float(s.quantile(.25)), median=float(s.median()), q75=float(s.quantile(.75)), max=float(s.max()))
L = C.length_km.sum()
R['collectors'] = dict(n=len(C), length_km=round(L, 2), service_ha=float(C.service_ha.sum()), age=desc(C.age), share_over_50=round(float((C.age > 50).mean()), 3),
                       len_share_over_50=round(float(C[C.age > 50].length_km.sum() / L), 3), since_repair=desc(C.since_repair),
                       repaired_by_year={int(y): dict(n=int(len(g)), km=round(float(g.length_km.sum()), 1)) for y, g in C.groupby('repair_year')},
                       len_share_repaired_last5=round(float(C[C.since_repair <= 5].length_km.sum() / L), 3),
                       len_share_not_repaired_5plus=round(float(C[C.since_repair > 5].length_km.sum() / L), 3),
                       by_decade={f'{int(d)}': dict(n=int(len(g)), km=round(float(g.length_km.sum()), 1)) for d, g in C.groupby((C.commissioned // 10) * 10)})
LD = D.length_km.sum(); nr = D[D.repair_year.isna()]
R['inner'] = dict(n=len(D), length_km=round(LD, 2), age=desc(D.age), n_no_repair=int(len(nr)), len_no_repair_km=round(float(nr.length_km.sum()), 1), len_share_no_repair=round(float(nr.length_km.sum() / LD), 3),
                  by_system={k: dict(n=int(len(g)), km=round(float(g.length_km.sum()), 1), no_repair_share=round(float(g[g.repair_year.isna()].length_km.sum() / g.length_km.sum()), 2),
                                     median_age=float(g.age.median())) for k, g in D.groupby('massif')})
# ---- 4.2 drenaj moduli: kollektor oxiridagi sarf / xizmat maydoni ----
H = C[(C.q_end_m3s > 0) & (C.service_ha > 0)].copy(); H['modul'] = H.q_end_m3s * 1000 / H.service_ha; H['spec_len'] = H.length_km * 1000 / H.service_ha
R['hydraulic'] = dict(n=len(H), modul_lps_ha=desc(H.modul), spec_len_m_ha=desc(H.spec_len), total_q=round(float(C.q_end_m3s.sum()), 2),
                      district_modul=round(float(H.q_end_m3s.sum() * 1000 / H.service_ha.sum()), 3),
                      n_modul_lt_0_1=int((H.modul < 0.1).sum()), n_modul_gt_5=int((H.modul > 5).sum()),
                      open_density_m_ha=round(float((L + LD) * 1000 / C.service_ha.sum()), 1))
H[['name', 'length_km', 'service_ha', 'q_end_m3s', 'modul', 'spec_len', 'commissioned', 'repair_year']].round(3).to_csv('results/ch4_drainage_modulus.csv', index=False)
# ---- 4.4 ta'mir narxi ----
def pk(s):
    m = re.search(r'пк\s*(\d+)\s*-\s*(\d+)', str(s)); return (int(m.group(2)) - int(m.group(1))) / 10 if m else np.nan   # piket = 100 m
K = C[C.repair_cost_mln > 0].copy(); K['rep_km'] = K.repair_pk.map(pk); K['rep_km'] = K.rep_km.fillna(K.length_km); K['rep_km'] = np.minimum(K.rep_km, K.length_km).where(K.rep_km > 0, K.length_km)
K['cost_km'] = K.repair_cost_mln / K.rep_km
R['cost'] = dict(n=len(K), total_mln=float(K.repair_cost_mln.sum()), total_km=round(float(K.rep_km.sum()), 1), mean_weighted_mln_km=round(float(K.repair_cost_mln.sum() / K.rep_km.sum()), 1),
                 cost_km=desc(K.cost_km), by_year={int(y): dict(n=int(len(g)), mln=float(g.repair_cost_mln.sum()), km=round(float(g.rep_km.sum()), 1), mln_km=round(float(g.repair_cost_mln.sum() / g.rep_km.sum()), 1)) for y, g in K.groupby('repair_year')},
                 ratio_p90_p10=round(float(K.cost_km.quantile(.9) / K.cost_km.quantile(.1)), 1),
                 corr_cost_km_vs_q=round(float(np.corrcoef(np.log(K.cost_km), np.log(K.q_end_m3s.clip(lower=0.001)))[0, 1]), 2))
K[['name', 'length_km', 'rep_km', 'repair_year', 'repair_cost_mln', 'cost_km', 'q_end_m3s', 'repair_type']].round(2).to_csv('results/ch4_repair_costs.csv', index=False)
# ---- 4.5 ta'mir samarasini aniqlash uchun zarur quduqlar ----
P = pd.read_csv('data/repair_panel.csv'); se, nt = 0.105, P[P.grp == 'treated'].well.nunique()   # 08-skript: asosiy model SE
need = lambda eff: int(np.ceil(nt * (se / (eff / 2.8)) ** 2))                                  # 80 % quvvat, 5 % ahamiyat: SE <= eff / 2,8
R['power'] = dict(se_now=se, treated_now=int(nt), min_detectable_now=round(2.8 * se, 2), need_for_0_2=need(0.2), need_for_0_15=need(0.15), need_for_0_1=need(0.1))
W = pd.read_csv('data/wells_metrics.csv'); R['network_wells'] = dict(n=len(W), within_150=int((W.dist_collector_m < 150).sum()), within_300=int((W.dist_collector_m < 300).sum()), beyond_600=int((W.dist_collector_m >= 600).sum()))
json.dump(R, open('results/ch4.json', 'w'), ensure_ascii=False, indent=1)
fig, ax = plt.subplots(1, 3, figsize=(13, 3.8))
b = C.groupby((C.commissioned // 10) * 10).length_km.sum(); ax[0].bar(b.index.astype(int).astype(str), b.values, color='#1f5fa8'); ax[0].set_xlabel("Foydalanishga topshirilgan o'n yillik"); ax[0].set_ylabel('Kollektorlar uzunligi, km'); ax[0].tick_params(axis='x', rotation=45)
r = C.groupby('repair_year').length_km.sum(); ax[1].bar(r.index.astype(int).astype(str), r.values, color='#2a7a2a'); ax[1].set_xlabel("Oxirgi ta'mir yili"); ax[1].set_ylabel('Uzunlik, km'); ax[1].tick_params(axis='x', rotation=45)
_KF = {int(k): v for k, v in json.load(open('results/cost_2026.json'))['index']['factors'].items()}  # 37-skript: 2026-yil oktabr narxlariga koeffitsiyentlar
_c26 = K.cost_km * K.repair_year.map(_KF)
ax[2].hist(_c26, bins=np.logspace(np.log10(_c26.min()), np.log10(_c26.max()), 14), color='#b5651d'); ax[2].set_xscale('log'); ax[2].set_xlabel("Ta'mir narxi, mln so'm / km (2026-yil narxlarida)"); ax[2].set_ylabel('Kollektorlar soni')
for a in ax: a.grid(alpha=.3)
fig.tight_layout(); fig.savefig('figures/ch4_reliability_costs.png', dpi=150)
print(json.dumps(R, ensure_ascii=False, indent=1))
