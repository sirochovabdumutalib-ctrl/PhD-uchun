"""8-xarita (4.5-§): massivlarning ustuvorlik guruhlari (4.7-jadval) va birinchi navbatdagi chora-tadbirlar joylashuvi (4.6-jadval).
a — ustuvorlik guruhlari (I, II, III, monitoring) va asosiy ko'rsatkichlar;
b — chora-tadbirlar: T-8 minerallashuvni o'lchash (sho'rlanish xavfli quduqlar, 4-xarita), T-5 quduqlarni chuqurlashtirish (tubigacha zaxira < 0,5 m, 2-xarita),
    T-9/T-10 kollektor holati va sarfini tekshirish (q < 0,43 l/(s·ga), 6-xarita), T-14 ichki zovurlar inventarizatsiyasi (ta'mirsiz ulush ≥ 70 %, 4.2-jadval).
Chiqish: figures/map8_priority.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib.patheffects as pe
from matplotlib.patches import Patch

dist = load('district'); M = massifs()
# 4.7-jadval (matndan; xarajat 2026-yil narxlarida — results/cost_2026.json)
PR = {'Z.M.Bobur': 'I', 'Istiqlol': 'I', 'Mashʼal': 'II', 'U.Qoraboyev': 'III', 'T.Mirzayev': 'III', 'Paxtakor': 'III', 'M.Toʻjiboyev': 'III', 'Y.Oxunboboyev': 'M'}
P30 = {'Z.M.Bobur': 58, 'Istiqlol': 55, 'Mashʼal': 71, 'U.Qoraboyev': 19, 'T.Mirzayev': 28, 'Paxtakor': 21, 'M.Toʻjiboyev': 17, 'Y.Oxunboboyev': None}
RW = {'Z.M.Bobur': 17, 'Istiqlol': 12, 'Mashʼal': 17, 'U.Qoraboyev': 1, 'T.Mirzayev': 1, 'Paxtakor': 4, 'M.Toʻjiboyev': 4, 'Y.Oxunboboyev': None}
TR = {'Z.M.Bobur': '↑', 'Istiqlol': '↓', 'Mashʼal': '↓', 'U.Qoraboyev': '↓', 'T.Mirzayev': '↓', 'Paxtakor': '↓', 'M.Toʻjiboyev': '↓', 'Y.Oxunboboyev': '—'}
# ichki zovurlar va kollektorlar
REL = json.load(open('results/ch4_rel_ext.json')); inner = {MASSIF_LAT[d['massif']]: d['inner_norep'] for d in REL['massif']}
m4 = pd.read_csv('results/map4_wells.csv'); risk = m4[m4.risk >= 1]
m2 = pd.read_csv('results/map2_wells.csv'); deep = m2[m2.margin < .5]
H = json.load(open('results/ch4_hydraulic.json')); T2 = round([s['q_july_rep'] for s in H['scenarios'] if s['name'] == "o'rta"][0], 2)
TRANSIT = [t['name'] for t in H['cad']['transit']]
K = pd.read_csv('data/collectors.csv'); K['name'] = K.name.str.strip(); K['q'] = K.q_end_m3s * 1000 / K.service_ha; kd = K.drop_duplicates('name').set_index('name')
c = load('collectors_named'); c['nm'] = c.cad_name.str.strip(); c['q'] = c.nm.map(kd.q)
low = c[(c.q < T2) & ~c.nm.isin(TRANSIT)]
print('T-8:', len(risk), '| T-5:', len(deep), '| T-9/10 kollektorlar:', low.nm.nunique(), round(low.length.sum() / 1e3, 1), 'km | T-14 massivlar:', [k for k, v in inner.items() if v == v and v >= .7])

FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.6; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH)
for a in (lg1, lg2): a.axis('off')

# ---------- a) ustuvorlik guruhlari
GC = {'I': '#bd0026', 'II': '#fd8d3c', 'III': '#ffeda0'}
basemap(ax1, dist, M, pad=pad, labels=False, network=False)
for _, r in M.iterrows():
    g = PR[r['name']]
    if g == 'M': gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax1, fc='#f2f2f2', ec='#888', hatch='....', lw=0, zorder=1.5)
    else: gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax1, fc=GC[g], ec='none', alpha=.9, zorder=1.5)
plot_lines(ax1, massif_lines(M, dist), color='#3a3a3a', lw=.7, zorder=3); ax1.set_xlabel(''); ax1.set_ylabel('')
for _, r in M.iterrows():
    p = label_point(r.geometry, None, inset=700); g = PR[r['name']]
    sub = 'monitoring' if g == 'M' else f"{g} guruh\n{P30[r['name']]} % · {RW[r['name']]} q. · {TR[r['name']]}"
    label_halo(ax1.text(p.x, p.y, f"{r['name']}\n{sub}", ha='center', va='center', fontsize=5.1, weight='bold', color='#1a1a1a', zorder=25, linespacing=1.1), 2.0)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
h1 = [Patch(fc=GC['I'], ec='#555', lw=.4, label='I — birinchi navbat: xavf yuqori,\ntarmoq zaif yoki oʻrta'),
      Patch(fc=GC['II'], ec='#555', lw=.4, label='II — xavf yuqori, tarmoq yaxshi'),
      Patch(fc=GC['III'], ec='#555', lw=.4, label='III — xavf past, sath chuqurlashmoqda'),
      Patch(fc='#f2f2f2', ec='#888', hatch='....', lw=.4, label='Monitoringni tiklash (maʼlumot yetarli emas)')]
legend_box(lg1, h1, title='Ustuvorlik guruhi (4.3-jadval)', loc='upper left', bbox_to_anchor=(0, 1), fs=5.4, borderaxespad=0)
lg1.text(0, .05, 'Massiv yozuvida: yozda sath < 1,5 m boʻlish ehtimoli > 0,3 boʻlgan maydon, %;\nshoʻrlanish xavfli quduqlar soni; sathning oʻzgarishi (↑ koʻtarilish, ↓ chuqurlashish).',
         fontsize=5.0, color='#333', transform=lg1.transAxes, va='bottom')

# ---------- b) chora-tadbirlar
basemap(ax2, dist, M, pad=pad, network=True, label_fs=5.0, avoid_xy=np.r_[risk[['x_utm43', 'y_utm43']].values, deep[['x_utm43', 'y_utm43']].values])
for _, r in M.iterrows():
    v = inner.get(r['name'], np.nan)
    if v == v and v >= .7:
        gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='none', ec='#7a5195', hatch='////', lw=0, zorder=1.6)
plot_lines(ax2, low.geometry, color='white', lw=2.4, zorder=5); plot_lines(ax2, low.geometry, color='#1b4f8a', lw=1.5, zorder=5.1)
ax2.scatter(risk.x_utm43, risk.y_utm43, s=20, marker='^', c='#d7301f', ec='#1a1a1a', lw=.45, zorder=12)
ax2.scatter(deep.x_utm43, deep.y_utm43, s=17, marker='s', c='#ffd92f', ec='#1a1a1a', lw=.45, zorder=11)
ax2.set_xlabel(''); ax2.set_ylabel('')
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
h2 = [Line2D([], [], marker='^', ls='', mfc='#d7301f', mec='#1a1a1a', mew=.45, ms=5, label=f'T-8: minerallashuvni oʻlchash — shoʻrlanish\nxavfli quduqlar ({len(risk)})'),
      Line2D([], [], marker='s', ls='', mfc='#ffd92f', mec='#1a1a1a', mew=.45, ms=4.3, label=f'T-5: quduqni chuqurlashtirish — tubigacha\nzaxira < 0,5 m ({len(deep)})'),
      Line2D([], [], color='#1b4f8a', lw=1.5, path_effects=[pe.Stroke(linewidth=2.4, foreground='white'), pe.Normal()],
             label=f'T-9, T-10: holati va sarfini tekshirish —\nq < {T2:.2f} l/(s·ga) kollektorlar ({low.nm.nunique()})'.replace('0.', '0,')),
      Patch(fc='white', ec='#7a5195', hatch='////', lw=.4, label='T-14: ichki zovurlarni inventarizatsiya —\ntaʼmirsiz ulush ≥ 70 % massivlar')]
legend_box(lg2, h2, title='Birinchi navbatdagi chora-tadbirlar (52-ilova)', loc='upper left', bbox_to_anchor=(0, 1), fs=5.3, borderaxespad=0)
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Manbalar: 4.3-jadval; shoʻrlanish xavfi — 3.5-§ (yozgi sath < 2,0 m va ≥ 1 g/l); zaxira — 3.1-§; kollektorlar sarfi — 4.2-§ '
         '\n(tranzit kollektorlarsiz, kadastr nomi aniqlanganlari); ichki zovurlar — 4.1-§. Asos: Copernicus GLO-30 relyef soyasi.', fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/map8_priority', provenance={
    'raw_data': ['text/4_bob.md table 4.7 (priority, p30, risk wells, trend)', 'results/map4_wells.csv (risk>=1)', 'results/map2_wells.csv (margin<0.5)',
                 'data/collectors.csv + results/ch4_hydraulic.json (q<0.43, transit excluded)', 'results/ch4_rel_ext.json (inner_norep>=0.7)', 'gis/*.geojson'],
    'transformations': ['priority groups as in table 4.7', 'action layers derived from maps 2, 4, 6 and table 4.2 with stated thresholds'],
    'counts': dict(T8=len(risk), T5=len(deep), T9_10=int(low.nm.nunique()), T14=[k for k, v in inner.items() if v == v and v >= .7])},
    alt_text=f"""Ikki panelli xarita, Marhamat tumani. a — ustuvorlik guruhlari: I guruh (toʻq qizil) Z.M.Bobur va Istiqlol, II guruh (toʻq sariq) Mashʼal, III guruh (och sariq)
U.Qoraboyev, T.Mirzayev, Paxtakor, M.Toʻjiboyev; Y.Oxunboboyev — monitoringni tiklash. b — chora-tadbirlar joylashuvi: {len(risk)} ta shoʻrlanish xavfli quduq (qizil uchburchak,
asosan shimol va gʻarbda), {len(deep)} ta chuqurlashtirish kerak quduq (sariq kvadrat, asosan janubi-sharqda), {low.nm.nunique()} ta talabni qoplamaydigan kollektor (koʻk chiziq),
ichki zovurlari asosan taʼmirsiz massivlar shtrixlangan.""")
