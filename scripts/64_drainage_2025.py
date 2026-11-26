"""2025-yil: Marhamat tumani xo'jaliklararo kollektorlaridan chiqqan suv va uning minerallashuvi (meliorativ uchastka, 17a-jadval)
hamda 2024–2025-yillar suv-tuz balansi. Sonlar hisobot fotonusxasidan qo'lda ko'chirilgan; skript yig'indilarni tekshiradi
va 4.2-§ dagi talab etiladigan drenaj moduli bilan solishtiradi.
Chiqish: results/drainage_2025.json, figures/ch4_drainage_2025.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
import numpy as np

M = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']
DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
# nomi: (massiv, sarf m3/s, chiqqan suv mln m3, quruq qoldiq g/l, yillik: sarf, hajm, minerallashuv)
D = {
 "Polvontosh": ("Mash'al", [.49, .49, .67, .81, .70, .74, .79, .78, .76, .74, .72, .75], [1.31, 1.19, 1.79, 2.10, 1.87, 1.92, 2.12, 2.09, 1.97, 1.98, 1.87, 2.01],
                [.83, .60, .77, .81, 1.97, 1.00, 2.70, 2.30, 2.13, 1.28, 1.25, 1.19], (.70, 22.22, 1.40)),
 "G'arbiy": ("Paxtakor", [1.31, 1.29, 1.33, 1.42, 1.43, 1.65, 1.67, 1.69, 1.47, 1.49, 1.42, 1.48], [3.51, 3.12, 3.56, 3.68, 3.83, 4.27, 4.47, 4.53, 3.80, 3.99, 3.68, 3.97],
             [.84, .71, .89, .70, 2.60, .98, 2.70, 2.26, 1.47, 1.28, 1.13, .76], (1.47, 46.41, 1.36)),
 "O'qchi": ("Z.M.Bobur", [.73, .80, 1.12, 1.23, .81, 1.25, 1.44, 1.31, 1.15, 1.43, 2.08, 1.24], [1.95, 1.94, 3.00, 3.19, 2.17, 3.24, 3.86, 3.51, 2.88, 3.83, 5.39, 3.32],
            [.84, .72, .70, .81, .72, .91, .66, .61, .87, .72, .72, .68], (1.22, 38.28, .75)),
 "Aravon": ("Z.M.Bobur", [.60, .65, .65, .45, .40, .59, .67, .71, .50, .84, 1.23, .73], [1.61, 1.57, 1.74, 1.16, 1.07, 1.53, 1.79, 1.90, 1.30, 2.25, 3.19, 1.95],
            [.82, .63, .63, .73, .89, .89, .64, .61, .74, .68, .68, .72], (.67, 21.06, .72)),
 "Beshtentak": ("Z.M.Bobur", [.19, .31, .47, 1.00, .51, .87, 1.00, 1.26, 1.00, 1.06, 1.67, 1.00], [.51, .75, 1.26, 2.59, 1.37, 2.25, 2.68, 3.37, 2.59, 2.84, 4.33, 2.68],
                [.74, .58, .67, .81, .74, .89, .64, .74, .81, .72, .72, 1.00], (.86, 27.22, .76)),
 "Istiqlol GKK": ("Istiqlol", [3.17, 3.27, 3.62, 3.97, 3.61, 4.19, 3.39, 4.19, 3.88, 4.73, 4.26, 4.46], [8.49, 7.91, 9.69, 10.29, 9.67, 10.86, 9.08, 11.22, 10.05, 12.66, 11.04, 11.94],
                                  [.87, .69, .81, 1.02, 1.12, .51, 1.10, 1.10, 1.06, 1.02, 1.00, 1.13], (3.89, 122.9, .95)),
}
T = dict(q=[4.58, 4.87, 5.88, 7.01, 5.63, 7.05, 6.62, 7.54, 6.79, 7.96, 8.73, 7.45], v=[12.26, 11.79, 15.74, 18.17, 15.62, 18.27, 17.74, 20.19, 17.49, 21.31, 22.63, 19.95],
         s=[.82, .66, .75, .81, 1.34, .86, 1.41, 1.27, 1.18, .95, .91, .91], year=(6.67, 211.16, .99))
SALT = {'2024': dict(intake=143.33, mi=.40, cl_in=.03, salt_in=57.33, cl_salt_in=4.30, drain=98.18, md=.75, cl_d=.07, salt_out=73.64, cl_out=6.87, bal=-16.30, cl_bal=-1.68),
        '2025': dict(intake=147.31, mi=.52, cl_in=.03, salt_in=76.60, cl_salt_in=4.42, drain=118.50, md=.99, cl_d=.06, salt_out=87.37, cl_out=6.37, bal=-10.77, cl_bal=-1.95)}

chk = {}
for k, (mas, q, v, s, (qy, vy, sy)) in D.items():
    vq = sum(qi * d * 86400 / 1e6 for qi, d in zip(q, DAYS))
    chk[k] = dict(sum_v=round(sum(v), 2), year_v=vy, mean_q=round(np.mean(q), 2), year_q=qy, v_from_q=round(vq, 1))
    assert abs(sum(v) - vy) < .06 and abs(np.mean(q) - qy) < .015, (k, chk[k])
assert abs(sum(T['v']) - T['year'][1]) < .02 and abs(np.mean(T['q']) - T['year'][0]) < .01
sum_coll = round(sum(d[4][1] for d in D.values()), 2)

IRR = {'ME hisoboti': 17965, 'xarita': 20662}
REQ = {'o\'rta, takroriy ekinlarsiz': .26, 'o\'rta, takroriy ekinlar bilan': .43, 'yuqori': .16, 'past (takroriy bilan)': .66}
jul = T['q'][6]; mod = {k: round(jul * 1000 / a, 3) for k, a in IRR.items()}
modmax = {k: round(max(T['q']) * 1000 / a, 3) for k, a in IRR.items()}
res = dict(source="Marhamat tuman meliorativ uchastkasi: 2025-yilda xo'jaliklararo kollektorlardan chiqqan suv (17a-jadval); suv-tuz balansi 2024–2025",
           collectors={k: dict(massif=v[0], q_year=v[4][0], v_year=v[4][1], s_year=v[4][2], s_jul=v[3][6], s_max=max(v[3]), s_max_month=M[int(np.argmax(v[3]))]) for k, v in D.items()},
           district=dict(q_year=T['year'][0], v_year=T['year'][1], s_year=T['year'][2], q_jul=jul, q_max=max(T['q']), q_max_month=M[int(np.argmax(T['q']))],
                         q_min=min(T['q']), q_min_month=M[int(np.argmin(T['q']))], s_max=max(T['s']), s_max_month=M[int(np.argmax(T['s']))]),
           sum_of_collectors_v=sum_coll, modulus_july=mod, modulus_max_month=modmax, required_july=REQ,
           drain_to_intake_pct=round(T['year'][1] / SALT['2025']['intake'] * 100, 1), salt=SALT, checks=chk)
json.dump(res, open('results/drainage_2025.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps({k: res[k] for k in ['district', 'sum_of_collectors_v', 'modulus_july', 'modulus_max_month', 'drain_to_intake_pct']}, ensure_ascii=False))
for k, v in res['collectors'].items(): print(k, v)

# rasm: a — tuman bo'yicha oylik oqim va talab etiladigan modul; b — kollektorlar bo'yicha oylik minerallashuv
from chartkit import plt, OI, fig, panel, axes_commas, export, fmt, SEQ7, MARK7
f, (a, b) = fig(15.5, 6.4, ncols=2)
x = np.arange(12)
qa = [qi * 1000 / IRR['ME hisoboti'] for qi in T['q']]
a.bar(x, qa, .65, color=OI['sky'], zorder=3, label='Oʻlchangan: tuman boʻyicha zovur oqimi')
a.axhspan(.26, .43, color=OI['orange'], alpha=.25, lw=0, zorder=1, label='Talab, iyul (oʻrta samaradorlik, 4.1-jadval)')
a.set_xticks(x, M, rotation=60); a.set_ylabel('Drenaj moduli, l/(s·ga)'); a.set_ylim(0, .62)
a.legend(loc='upper left', fontsize=6); axes_commas(a, ydec=2); panel(a, 'a')
for i, (k, v) in enumerate(D.items()):
    b.plot(x, v[3], marker=MARK7[i % 7], ms=3, lw=1, color=SEQ7[i % 7], label=f"{k} ({v[0]})")
b.set_xticks(x, M, rotation=60); b.set_ylabel('Zovur suvi minerallashuvi, g/l'); b.legend(fontsize=5.6, loc='upper left', ncol=1); axes_commas(b); panel(b, 'b')
f.text(.01, -.03, "Manba: Marhamat tuman meliorativ uchastkasi, 2025-yil (17a-jadval). Modul tuman oqimini sugʻoriladigan maydonga (17 965 ga) boʻlib hisoblangan; "
       "u qoʻshni hududlardan keladigan suvni ham oʻz ichiga oladi.", fontsize=5.8, color='#555')
export(f, 'figures/ch4_drainage_2025', dict(raw_data='17a-jadval (2025), qoʻlda koʻchirilgan; scripts/64_drainage_2025.py', transformations=['oylik sarf / 17 965 ga']),
       'Marhamat tumani: 2025-yilda zovur oqimi boʻyicha drenaj moduli oylar boʻyicha va kollektorlar suvining minerallashuvi')
