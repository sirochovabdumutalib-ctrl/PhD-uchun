"""6-xarita (4.2-§): kollektorlarning kadastr bo'yicha solishtirma sarfi va iyuldagi talab etiladigan drenaj moduli.
q = 1000·Q/F (l/(s·ga)); chegaralar 4.3-jadvaldan: 0,26 (o'rta stsenariy), 0,43 (o'rta, takroriy ekinlar bilan), 0,66 (past samaradorlik, takroriy ekinlar bilan).
a — kollektorlar sinflar bo'yicha (tranzit kollektorlar alohida); b — massivlar: kadastr nomi aniqlangan kollektorlar uzunligining 0,43 dan past qismi.
Chiqish: figures/map6_drainage_capacity.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib.patheffects as pe
from matplotlib.patches import Patch

H = json.load(open('results/ch4_hydraulic.json'))
T1, T2, T3 = [round(s['q_july'], 2) for s in H['scenarios'] if s['name'] == "o'rta"][0], [round(s['q_july_rep'], 2) for s in H['scenarios'] if s['name'] == "o'rta"][0], \
             [round(s['q_july_rep'], 2) for s in H['scenarios'] if s['name'] == 'past'][0]
TRANSIT = [t['name'] for t in H['cad']['transit']]
K = pd.read_csv('data/collectors.csv'); K['name'] = K.name.str.strip(); K['q'] = K.q_end_m3s * 1000 / K.service_ha
chk = dict(below=[int((K.q < t).sum()) for t in (T1, T2, T3)], area=[int(K.loc[K.q < t, 'service_ha'].sum()) for t in (T1, T2, T3)])
print('chegaralar', T1, T2, T3, '| 4.2-§ bilan tekshiruv:', chk)
kd = K.drop_duplicates('name').set_index('name')
dist = load('district'); M = massifs(); c = load('collectors_named'); c['nm'] = c.cad_name.str.strip(); c['q'] = c.nm.map(kd.q)
named = c[c.q.notna()].copy(); other = c[c.q.isna()]
named['k'] = np.where(named.nm.isin(TRANSIT), 4, np.digitize(named.q, [T1, T2, T3]))
print('xaritadagi kollektorlar sinflar bo‘yicha:', named.drop_duplicates('nm').k.value_counts().sort_index().to_dict())

COL = ['#b2182b', '#f4a582', '#fddbc7', '#4393c3', '#2d2d2d']; LW = [2.0, 1.75, 1.5, 1.2, 1.6]
LAB = [f'< {T1:.2f}'.replace('.', ',') + ' — oʻrta stsenariyda ham yetmaydi', f'{T1:.2f}–{T2:.2f}'.replace('.', ',') + ' — takroriy ekinlar bilan yetmaydi',
       f'{T2:.2f}–{T3:.2f}'.replace('.', ',') + ' — past samaradorlikda yetmaydi', f'≥ {T3:.2f}'.replace('.', ',') + ' — barcha stsenariylarda yetadi',
       'Tranzit kollektorlar (q drenaj\nmodulini bermaydi)']

def draw(ax):
    plot_lines(ax, other.geometry, color='#9fb3a8', lw=.6, zorder=4)
    for i in (3, 4, 2, 1, 0):
        q = named[named.k == i]
        plot_lines(ax, q.geometry, color='#1a1a1a' if i != 4 else 'white', lw=LW[i] + .7, solid_capstyle='round', zorder=5 + (4 - i) * .1)
        plot_lines(ax, q.geometry, color=COL[i], lw=LW[i], solid_capstyle='round', ls='-' if i != 4 else (0, (3, 1.5)), zorder=5.05 + (4 - i) * .1)

# b uchun: massivlar bo'yicha (uzunlik bilan vaznlangan)
o = gpd.overlay(named[['nm', 'k', 'geometry']], M[['name', 'geometry']], how='intersection', keep_geom_type=True); o['km'] = o.length / 1e3
o = o[o.k != 4]
g = o.groupby('name').apply(lambda q: pd.Series(dict(km=q.km.sum(), low=q[q.k <= 1].km.sum())), include_groups=False); g['share'] = 100 * g.low / g.km
print(g.round(1))

FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.7; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH)
for a in (lg1, lg2): a.axis('off')
mid = np.array([[gg.interpolate(.5, normalized=True).x, gg.interpolate(.5, normalized=True).y] for gg in c.geometry])

basemap(ax1, dist, M, pad=pad, network=False, label_fs=5.3, avoid_xy=mid)
draw(ax1)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
cnt = named.drop_duplicates('nm').k.value_counts()
h1 = [Line2D([], [], color=COL[i], lw=LW[i], ls='-' if i != 4 else (0, (3, 1.5)),
             path_effects=[pe.Stroke(linewidth=LW[i] + .7, foreground='#1a1a1a' if i != 4 else 'white'), pe.Normal()], label=f'{LAB[i]} ({int(cnt.get(i, 0))})') for i in range(5)]
h1 += [Line2D([], [], color='#9fb3a8', lw=.8, label='Kadastr maʼlumoti biriktirilmagan')]
legend_box(lg1, h1, title='Solishtirma sarf q, l/(s·ga), va iyuldagi talab', loc='upper left', bbox_to_anchor=(0, 1), fs=5.3, borderaxespad=0)

# b) massivlar
bnd = [0, 20, 40, 60, 101]; SEQ = ['#fef0d9', '#fdcc8a', '#fc8d59', '#d7301f']
basemap(ax2, dist, M, pad=pad, labels=False, network=False)
for _, r in M.iterrows():
    if r['name'] in g.index and g.loc[r['name'], 'km'] > 0:
        k = np.digitize(g.loc[r['name'], 'share'], bnd[1:-1]); gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc=SEQ[k], ec='none', alpha=.92, zorder=1.5)
    else:
        gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='white', ec='#999', hatch='////', lw=0, alpha=.9, zorder=1.5)
plot_lines(ax2, massif_lines(M, dist), color='#4a4a4a', lw=.6, zorder=3)
plot_lines(ax2, named[named.k <= 1].geometry, color='#1a1a1a', lw=.9, zorder=4)
ax2.set_xlabel(''); ax2.set_ylabel('')
for _, r in M.iterrows():
    p = label_point(r.geometry, mid)
    t = r['name'] + (f"\n{g.loc[r['name'], 'share']:.0f} % ({g.loc[r['name'], 'low']:.1f} / {g.loc[r['name'], 'km']:.1f} km)".replace('.', ',') if r['name'] in g.index and g.loc[r['name'], 'km'] > 0 else '\nmaʼlumot yoʻq')
    label_halo(ax2.text(p.x, p.y, t, ha='center', va='center', fontsize=5.1, weight='bold', color='#222', zorder=25, linespacing=1.1), 2.0)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
h2 = [Patch(fc=cc, ec='#666', lw=.4, label=l) for cc, l in zip(SEQ, ['< 20', '20–40', '40–60', '≥ 60'])]
h2 += [Patch(fc='white', ec='#999', hatch='////', lw=.4, label='Kadastr nomi aniqlangan\nkollektor yoʻq'),
       Line2D([], [], color='#1a1a1a', lw=.9, label=f'q < {T2:.2f} kollektorlar'.replace('.', ','))]
legend_box(lg2, h2, title=f'Kollektorlar uzunligining q < {T2:.2f} l/(s·ga)\nboʻlgan qismi, % (tranzitsiz)'.replace('0.', '0,'), loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.4, borderaxespad=0)
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. q = 1000·Q/F — kadastrdagi kollektor oxiridagi sarf (Q) va xizmat maydoni (F) boʻyicha; talab etiladigan modul — 4.3-jadval (iyul). '
         f'\nXaritada kadastr nomi aniqlangan {named.nm.nunique()} ta kollektor (90 tadan); kadastrdagi sarfning ishonchliligi tekshirilmagan (4.2-§). Asos: Copernicus GLO-30 relyef soyasi.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/map6_drainage_capacity', provenance={
    'raw_data': ['data/collectors.csv (Q, F)', 'results/ch4_hydraulic.json (q_july scenarios, transit list)', 'gis/collectors_named.geojson', 'gis/massifs.geojson'],
    'transformations': ['q = 1000*Q/F l/(s*ha)', f'classes by required July modulus {T1}, {T2}, {T3} (table 4.3)', '5 transit collectors shown separately',
                        f'massif share = length of named collectors with q<{T2} / named non-transit length (overlay with massif polygons)'],
    'check_vs_text_4.2': chk, 'caveat': 'cadastre discharge reliability unknown (e.g. Jo\'ga 5 km / 4 ha)'},
    alt_text=f"""Ikki panelli xarita, Marhamat tumani kollektorlari. a — {named.nm.nunique()} ta kollektor solishtirma sarfi boʻyicha: toʻq qizil — oʻrta stsenariy talabidan ({T1} l/(s·ga)) ham past,
och qizil va pushti — takroriy ekinlar yoki past samaradorlik stsenariysida yetmaydi, koʻk — barcha stsenariylarda yetadi; besh ta yirik tranzit kollektor qora uzuq chiziq.
b — massivlar boʻyicha talabdan ({T2} l/(s·ga)) past kollektorlar uzunligi ulushi.""")
