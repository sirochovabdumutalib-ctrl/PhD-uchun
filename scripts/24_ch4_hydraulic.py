"""4.2-§: talab etiladigan drenaj moduli (suv balansi: ET0 x Kc, samarali yog'in, sug'orish samaradorligi stsenariylari),
sizot sathining mavsumiy ko'tarilishi bo'yicha tekshiruv, kadastr moduli bilan qiyos, Manning bo'yicha o'tkazish qobiliyati sezgirligi, hudud nishabligi.
Chiqish: results/ch4_hydraulic.json, figures/ch4_hydraulic.png"""
import json, re, numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
R = {}
cl = pd.read_csv('results/climate.csv').set_index('month'); days = np.array([31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31])
# crop shares from cadastre contours (district total row)
c = pd.read_csv('data/contours.csv'); tot = c[c.massif.astype(str).str.startswith('Массив жами') & (c.massif.astype(str).str.strip() == 'Массив жами')][['area_ha', 'cotton_ha', 'grain_ha']].sum()
sh = dict(cotton=tot.cotton_ha / tot.area_ha, grain=tot.grain_ha / tot.area_ha); sh['other'] = 1 - sh['cotton'] - sh['grain']; R['crop_share'] = {k: round(v, 3) for k, v in sh.items()}; R['contour_area'] = round(tot.area_ha)
# FAO-56 based monthly Kc (Jan..Dec)
KC = dict(cotton=[0, 0, 0, .35, .45, .85, 1.15, 1.15, .80, .60, 0, 0],
          grain=[.40, .45, .75, 1.10, 1.15, .50, 0, 0, 0, .40, .45, .40],
          other=[0, 0, .50, .70, .85, .95, .95, .95, .85, .70, 0, 0])
Kc = sum(np.array(KC[k]) * sh[k] for k in KC); ETc = Kc * cl.et0_mm.values
P = cl.precip.values; Pe = np.where(P < 250, P * (125 - 0.2 * P) / 125, 125 + 0.1 * P)
NIR = np.maximum(ETc - Pe, 0)
R['monthly'] = pd.DataFrame(dict(et0=cl.et0_mm.values, kc=Kc.round(2), etc=ETc.round(0), p=P, pe=Pe.round(0), nir=NIR.round(0)), index=range(1, 13)).to_dict('index')
R['annual'] = dict(et0=round(cl.et0_mm.sum()), etc=round(ETc.sum()), pe=round(Pe.sum()), nir=round(NIR.sum()), nir_veg=round(NIR[3:9].sum()))
# drainage load scenarios: field application efficiency Ea, on-farm conveyance Ec, share of losses reaching groundwater beta
# variant with repeat crops after grain (Jul-Sep)
KC2 = dict(KC); KC2['grain'] = KC['grain'][:6] + [.85, .90, .70] + KC['grain'][9:]
Kc2 = sum(np.array(KC2[k]) * sh[k] for k in KC2); ETc2 = Kc2 * cl.et0_mm.values; NIR2 = np.maximum(ETc2 - Pe, 0)
R['annual_repeat'] = dict(etc=round(ETc2.sum()), nir=round(NIR2.sum()), nir_july=round(NIR2[6]), kc_july=round(Kc2[6], 2))
sc = []
for name, Ea, Ec in (('yuqori', 0.75, 0.85), ("o'rta", 0.65, 0.80), ('past', 0.55, 0.75)):
    gross = NIR / (Ea * Ec); fl = NIR / Ea - NIR; cl_ = gross - NIR / Ea; beta = 0.7
    D = beta * (fl + cl_); q = D / days / 8.64  # l/s*ha  (1 mm/day = 0.1157 l/s*ha -> mm/day /8.64*1)
    D2 = beta * (NIR2 / Ea - NIR2 + NIR2 / (Ea * Ec) - NIR2 / Ea); q2 = D2 / days / 8.64
    sc.append(dict(q_july_rep=round(q2[6], 3), D_year_rep=round(D2.sum()), gross_rep=round((NIR2 / (Ea * Ec)).sum()), name=name, Ea=Ea, Ec=Ec, gross=round(gross.sum()), D_year=round(D.sum()), D_veg=round(D[3:9].sum()), q_july=round(q[6] * 1, 3), q_veg=round(D[3:9].sum() / days[3:9].sum() / 8.64, 3), q_year=round(D.sum() / 365 / 8.64, 3)))
R['scenarios'] = sc
# groundwater-based check: seasonal rise (3.2-§) 0.48 m over ~120 days, specific yield 0.05-0.15
rise = 0.478; dur = 120; R['gw_check'] = {f'mu_{mu}': dict(mm=round(mu * rise * 1000), q=round(mu * rise * 1000 / dur / 8.64, 3)) for mu in (0.05, 0.10, 0.15)}
# literature design range 1-3 mm/day
R['design_range'] = [round(1 / 8.64, 3), round(3 / 8.64, 3)]
# cadastre modulus comparison
H = pd.read_csv('results/ch4_drainage_modulus.csv'); H = H[(H.modul > 0)]
qs = sc[1]['q_july']
R['cad'] = dict(n=len(H), med=round(H.modul.median(), 3), below_req=int((H.modul < qs).sum()), below_01=int((H.modul < 0.1).sum()), above_5=int((H.modul > 5).sum()),
                transit=H.sort_values('q_end_m3s', ascending=False).head(5)[['name', 'q_end_m3s', 'service_ha', 'modul']].round(3).to_dict('records'),
                district_q=round(H.q_end_m3s.sum(), 2), district_modul=round(H.q_end_m3s.sum() * 1000 / H.service_ha.sum(), 3))
Hn = H[H.modul <= 5]; R['cad_no_transit'] = dict(n=len(Hn), med=round(Hn.modul.median(), 3), q25=round(Hn.modul.quantile(.25), 3), q75=round(Hn.modul.quantile(.75), 3), weighted=round(Hn.q_end_m3s.sum() * 1000 / Hn.service_ha.sum(), 3))
# Manning sensitivity, trapezoid b=1.0 m, m=1.5, depth h=1.2 m, slope S
def Q(b, m, h, n, S):
    A = (b + m * h) * h; Pw = b + 2 * h * np.sqrt(1 + m * m); return A / n * (A / Pw) ** (2 / 3) * S ** .5
rows = []
for S in (0.0005, 0.001):
    base = Q(1.0, 1.5, 1.2, 0.025, S)
    for lab, n, sil in (("Toza o'zan", 0.025, 0), ("O'simlik bilan qoplangan", 0.035, 0), ("O'simlik + 0,3 m loyqa", 0.035, 0.3), ("O'simlik + 0,5 m loyqa", 0.040, 0.5)):
        # silt reduces depth and raises bed: effective depth h-sil, bottom width b+2*m*sil
        q = Q(1.0 + 2 * 1.5 * sil, 1.5, 1.2 - sil, n, S); rows.append(dict(S=S, case=lab, n=n, silt=sil, Q=round(q, 2), rel=round(q / base * 100)))
R['manning'] = rows
# terrain gradient from well elevations
W = pd.read_csv('data/wells_metrics.csv'); A = pd.read_csv('data/gw_annual.csv')
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper()
z = A.dropna(subset=['z_m']).assign(w=lambda d: d.well_no.map(norm)).groupby('w').z_m.last(); W['z'] = W.well_no.map(norm).map(z)
Wz = W.dropna(subset=['z']); Wz = Wz[Wz.z < 700]
X = np.c_[np.ones(len(Wz)), Wz.x_utm43 / 1000, Wz.y_utm43 / 1000]; b = np.linalg.lstsq(X, Wz.z.values, rcond=None)[0]
R['terrain'] = dict(n=len(Wz), zmin=round(Wz.z.min()), zmax=round(Wz.z.max()), gx=round(b[1], 2), gy=round(b[2], 2), grad_m_km=round(np.hypot(b[1], b[2]), 2), slope=round(np.hypot(b[1], b[2]) / 1000, 4),
                    dir_deg=round((np.degrees(np.arctan2(-b[1], -b[2])) + 360) % 360))
# figure
fig, ax = plt.subplots(1, 2, figsize=(12, 4.2)); m = np.arange(1, 13)
ax[0].bar(m - .2, ETc, .4, color='#1f5fa8', label='Ekinlar bug\'lanishi ETc'); ax[0].bar(m + .2, Pe, .4, color='#9ecae1', label='Samarali yog\'in')
ax[0].plot(m, NIR, 'ko-', ms=4, label='Sof sug\'orish talabi'); ax[0].set_xticks(m); ax[0].set_xticklabels(['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek'])
ax[0].set_ylabel('mm/oy'); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3, axis='y'); ax[0].set_title('a', loc='left')
hm = H[H.modul <= 5].modul; ax[1].hist(np.log10(H.modul), bins=20, color='#bbb', edgecolor='k', label='Kadastr: kollektorlar (90 ta)')
for s_, c_ in zip(sc, ['#1a9850', '#fdae61', '#d73027']): ax[1].axvline(np.log10(s_['q_july']), color=c_, lw=2, label=f"Talab, iyul ({s_['name']} samaradorlik): {s_['q_july']:.2f}".replace('.', ','))
ax[1].axvspan(np.log10(1 / 8.64), np.log10(3 / 8.64), color='#1f5fa8', alpha=.12, label='Loyihaviy oraliq 1–3 mm/sut')
ax[1].set_xlabel('Solishtirma sarf, l/(s·ga), log shkala'); ax[1].set_xticks(np.log10([0.03, 0.1, 0.3, 1, 3, 10, 50])); ax[1].set_xticklabels(['0,03', '0,1', '0,3', '1', '3', '10', '50'])
ax[1].set_ylabel('Kollektorlar soni'); ax[1].legend(fontsize=7); ax[1].grid(alpha=.3); ax[1].set_title('b', loc='left')
fig.tight_layout(); fig.savefig('figures/ch4_hydraulic.png', dpi=150)
json.dump(R, open('results/ch4_hydraulic.json', 'w'), ensure_ascii=False, indent=1, default=lambda o: o.item() if hasattr(o, 'item') else str(o))
print(json.dumps({k: v for k, v in R.items() if k != 'monthly'}, ensure_ascii=False, default=lambda o: o.item() if hasattr(o, 'item') else str(o)))
for k, v in R['monthly'].items(): print(k, v)
