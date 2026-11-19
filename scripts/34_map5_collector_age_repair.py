"""5-xarita (4.1-§): kollektorlarning foydalanishga topshirilgan davri va oxirgi ta'mir yili.
Kadastrda nomi aniqlangan kollektor bo'laklari (gis/collectors_named.geojson, cad_name) kadastr yozuvlari bilan ranglangan;
qolgan bo'laklar — kulrang uzuq chiziq. b-panelda massiv yozuvlarida ta'mirsiz ichki zovurlar ulushi (4.2-jadval, results/ch4_rel_ext.json).
Chiqish: figures/map5_collector_age_repair.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib.patheffects as pe

dist = load('district'); M = massifs(); c = load('collectors_named')
K = pd.read_csv('data/collectors.csv'); K['name'] = K.name.str.strip(); kd = K.drop_duplicates('name').set_index('name')
c['nm'] = c.cad_name.str.strip()
c['comm'] = c.nm.map(kd.commissioned); c['rep'] = c.nm.map(kd.repair_year)
named = c[c.comm.notna()].copy(); other = c[c.comm.isna()]
print('nomi aniqlangan bo‘laklar', len(named), 'kollektorlar', named.nm.nunique(), 'km', round(named.length.sum() / 1e3, 1), '| qolgan km', round(other.length.sum() / 1e3, 1))
# tekshiruv: geojson dagi repair_year/commissioned bilan kadastr mosligi
chk = (pd.to_numeric(named.repair_year, errors='coerce') == named.rep).mean(), (pd.to_numeric(named.commissioned, errors='coerce') == named.comm).mean()
print('geojson=kadastr mosligi (ta’mir, qurilish):', [round(x, 3) for x in chk])
R = json.load(open('results/ch4_rel_ext.json'))
inner = {MASSIF_LAT[d['massif']]: d['inner_norep'] for d in R['massif']}

YOR = ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c']; LW = [2.0, 1.7, 1.4, 1.15]
A_B = [1950, 1960, 1970]; A_L = ['1950-yilgacha', '1950–1959', '1960–1969', '1970 va keyin']
R_B = [2015, 2017, 2019]; R_L = ['2010–2014', '2015–2016', '2017–2018', '2019–2020']
named['ka'] = np.digitize(named.comm, A_B)              # 0 = eng eski: < 1950 (qizil)
named['kr'] = np.digitize(named.rep, R_B)               # 0 = eng uzoq ta'mirlangan: 2010–2014 (qizil)

def draw(ax, key):
    plot_lines(ax, other.geometry, color='#9fb3a8', lw=.6, zorder=4)
    for i in (3, 2, 1, 0):
        q = named[named[key] == i]
        plot_lines(ax, q.geometry, color='#1a1a1a', lw=LW[i] + .7, solid_capstyle='round', zorder=5 + (3 - i) * .1)
        plot_lines(ax, q.geometry, color=YOR[i], lw=LW[i], solid_capstyle='round', zorder=5.05 + (3 - i) * .1)

def km(key):
    return [named[named[key] == i].length.sum() / 1e3 for i in range(4)]

FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.45; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH)
for a in (lg1, lg2): a.axis('off')
mid = np.array([[g.interpolate(.5, normalized=True).x, g.interpolate(.5, normalized=True).y] for g in c.geometry])

basemap(ax1, dist, M, pad=pad, network=False, label_fs=5.3, avoid_xy=mid)
draw(ax1, 'ka')
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
def handles(labels, kms):
    h = [Line2D([], [], color=YOR[i], lw=LW[i], path_effects=[pe.Stroke(linewidth=LW[i] + .7, foreground='#1a1a1a'), pe.Normal()],
                label=f'{l} ({k:.1f} km)'.replace('.', ',')) for i, (l, k) in enumerate(zip(labels, kms))]
    h += [Line2D([], [], color='#9fb3a8', lw=.8, label=f'Kadastr maʼlumoti\nbiriktirilmagan ({other.length.sum() / 1e3:.1f} km)'.replace('.', ','))]
    return h
legend_box(lg1, handles(A_L, km('ka')), title='Foydalanishga topshirilgan yil', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.5, borderaxespad=0, columnspacing=.9)

txt = {k: f'{k}\n{v * 100:.0f} %' if not np.isnan(v) else f'{k}\n—' for k, v in inner.items()}
basemap(ax2, dist, M, pad=pad, network=False, label_fs=5.3, avoid_xy=mid, massif_text=txt)
draw(ax2, 'kr')
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
legend_box(lg2, handles(R_L, km('kr')), title='Oxirgi taʼmir yili (kadastr)', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.5, borderaxespad=0, columnspacing=.9)
lg2.text(0, .36, 'Massiv yozuvida: taʼmir qayd etilmagan xoʻjalik ichki zovurlari\nulushi, uzunlik boʻyicha (45-ilova); «—» — zovurlar kadastrda yoʻq.', fontsize=5.3, color='#333', transform=lg2.transAxes, va='top')
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Rang va chiziq qalinligi: qizil va qalin — eskiroq (a) yoki uzoqroq taʼmirlangan (b). Kadastr nomi xarita boʻlaklariga 2.3-§ dagi tartibda biriktirilgan;' +
         (f'\nxaritadagi {c.length.sum() / 1e3:.1f} km kollektor-zovurdan {named.length.sum() / 1e3:.1f} km ga ({named.nm.nunique()} ta kollektor) kadastr maʼlumoti biriktirilgan').replace('.', ',') + '. Xoʻjalik ichki zovurlari xaritada alohida qatlam sifatida yoʻq. Asos: Copernicus GLO-30.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/map5_collector_age_repair', provenance={
    'raw_data': ['gis/collectors_named.geojson', 'data/collectors.csv (kadastr, 2021)', 'results/ch4_rel_ext.json (inner_norep)', 'gis/massifs.geojson', 'gis/district.geojson'],
    'transformations': ['join map segments to cadastre by cad_name', 'classes commissioned {<1950,1950-59,1960-69,>=1970}; last repair {2010-14,2015-16,2017-18,2019-20}',
                        'class km = sum of mapped segment lengths (not cadastre lengths)'],
    'check_geojson_vs_cadastre': [round(x, 3) for x in chk], 'missing_data': 'segments without cadastre name drawn grey dashed; inner drains not mapped'},
    alt_text=f"""Ikki panelli xarita, Marhamat tumani kollektorlari. a — {named.nm.nunique()} ta kadastr nomi aniqlangan kollektor foydalanishga topshirilgan davri boʻyicha:
1950-yilgacha qurilganlari (qizil, 38,6 km) Z.M.Bobur, Mashʼal va Istiqlol massivlarida koʻp, 1970-yildan keyingilari kam (13,8 km). b — oxirgi taʼmir yili: koʻp kollektorlar 2017–2018-yillarda taʼmirlangan (44,4 km), massivlar boʻyicha bloklarga ajraladi;
taʼmir yili kollektor yoshi va joylashuvi bilan bogʻlanmagan. Massiv yozuvlarida taʼmirsiz ichki zovurlar ulushi: Mashʼalda 21 foiz, Z.M.Bobur 82 foiz, Y.Oxunboboyev 100 foiz.""")
print('a km:', [round(x, 1) for x in km('ka')], 'b km:', [round(x, 1) for x in km('kr')])
# o'z-o'zini tekshirish: sinf belgilari kadastr yillariga mos kelishi shart
for key, col_, edges in (('ka', 'comm', [0] + A_B + [3000]), ('kr', 'rep', [0] + R_B + [3000])):
    for i in range(4):
        q = named[named[key] == i][col_]
        assert q.empty or (q.min() >= edges[i] and q.max() < edges[i + 1]), (key, i, q.min(), q.max())
print('sinflar tekshiruvi: OK')
