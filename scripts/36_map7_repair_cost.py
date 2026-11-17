"""7-xarita (4.4-§): kollektorlar ta'mir xarajatlari (2017–2020) va meliorativ xavf, massivlar bo'yicha.
a — massivlar: 1 ga sug'oriladigan maydonga xarajat (ming so'm/ga) + 2017–2020-yillarda ta'mirlangan kollektorlar ta'mir turi bo'yicha;
b — massivlar: yozda sath 1,5 m dan sayoz bo'lish ehtimoli 0,3 dan katta maydon ulushi (3.3-§) + doiralar: xarajat, ming so'm/ga (doira yuzasi mutanosib).
Manba: results/ch4_cost_ext.json (26-skript; 4.5-jadval), results/ch4_repair_costs.csv. Chiqish: figures/map7_repair_cost.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Circle

R = json.load(open('results/ch4_cost_ext.json'))
B = pd.DataFrame(R['by_massif']); B['name'] = B.massif.map(MASSIF_LAT); B = B.set_index('name')
print(B[['cost', 'irr_ha', 'cost_per_ha', 'p30', 'risk_wells']])
Kc = pd.read_csv('results/ch4_repair_costs.csv'); Kc['name'] = Kc.name.str.strip(); kc = Kc.set_index('name')
dist = load('district'); M = massifs(); c = load('collectors_named'); c['nm'] = c.cad_name.str.strip()
c['cost_km'] = c.nm.map(kc.cost_km); c['ry'] = c.nm.map(kc.repair_year)
rep = c[c.cost_km.notna()]; light = rep[rep.cost_km < 50]; heavy = rep[rep.cost_km >= 50]; rest = c[c.cost_km.isna()]
print('xaritadagi ta’mirlangan (narxi bor) kollektorlar:', rep.nm.nunique(), '| yengil:', light.nm.nunique(), 'kapital:', heavy.nm.nunique())

FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 2.55; BM = .62
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
lg1 = add_axes_cm(fig, .35, BM, PW, LH - .3, FW, FH); lg2 = add_axes_cm(fig, .35 + PW + .5, BM, PW, LH - .3, FW, FH)
for a in (lg1, lg2): a.axis('off')

def fill(ax, values, bnd, cols, nodata_mask=None):
    for _, r in M.iterrows():
        v = values.get(r['name'], np.nan)
        if (nodata_mask is not None and nodata_mask.get(r['name'], False)) or np.isnan(v):
            gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax, fc='white', ec='#999', hatch='////', lw=0, alpha=.9, zorder=1.5)
        else:
            gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax, fc=cols[np.digitize(v, bnd[1:-1])], ec='none', alpha=.92, zorder=1.5)
    plot_lines(ax, massif_lines(M, dist), color='#4a4a4a', lw=.6, zorder=3)
    ax.set_xlabel(''); ax.set_ylabel('')

# ---------- a) xarajat ming so'm/ga + ta'mir turi
BA = [0, 500, 1000, 1500, 1e9]; CA = ['#edf8fb', '#b3cde3', '#8c96c6', '#88419d']  # ColorBrewer BuPu (4)
basemap(ax1, dist, M, pad=pad, labels=False, network=False)
fill(ax1, B.cost_per_ha.to_dict(), BA, CA, nodata_mask=(B.cost == 0).to_dict())
plot_lines(ax1, rest.geometry, color='#8c8c8c', lw=.5, zorder=4)
plot_lines(ax1, heavy.geometry, color='white', lw=2.2, zorder=5); plot_lines(ax1, heavy.geometry, color='#1a1a1a', lw=1.4, zorder=5.1)
plot_lines(ax1, light.geometry, color='white', lw=2.0, zorder=5.2); plot_lines(ax1, light.geometry, color='#d95f02', lw=1.3, ls=(0, (2.2, 1.2)), zorder=5.3)
mid = np.array([[g.interpolate(.5, normalized=True).x, g.interpolate(.5, normalized=True).y] for g in c.geometry])
for _, r in M.iterrows():
    p = label_point(r.geometry, mid); v = B.loc[r['name']]
    t = r['name'] + ('\nkollektor yoʻq' if v.cost == 0 else f'\n{v.cost_per_ha:,.0f}'.replace(',', ' ') + ' ming soʻm/ga')
    label_halo(ax1.text(p.x, p.y, t, ha='center', va='center', fontsize=5.0, weight='bold', color='#222', zorder=25, linespacing=1.1), 2.0)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
h1 = [Patch(fc=cc, ec='#666', lw=.4, label=l) for cc, l in zip(CA, ['< 500', '500–1 000', '1 000–1 500', '≥ 1 500'])]
h1 += [Patch(fc='white', ec='#999', hatch='////', lw=.4, label='Kollektor yoʻq')]
h1 += [Line2D([], [], color='#1a1a1a', lw=1.4, path_effects=[pe.Stroke(linewidth=2.2, foreground='white'), pe.Normal()], label=f'Kapital taʼmir, ≥ 50 mln soʻm/km ({heavy.nm.nunique()})'),
       Line2D([], [], color='#d95f02', lw=1.3, ls=(0, (2.2, 1.2)), label=f'Yengil tozalash, < 50 mln soʻm/km ({light.nm.nunique()})'),
       Line2D([], [], color='#8c8c8c', lw=.6, label='Xarajat qayd etilmagan')]
legend_box(lg1, h1, title='Taʼmir xarajati 2017–2020, ming soʻm/ga', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.2, borderaxespad=0, columnspacing=.7)

# ---------- b) meliorativ xavf (fon) + xarajat (doira yuzasi)
BB = [0, 20, 40, 60, 101]; CB = ['#ffffb2', '#fecc5c', '#fd8d3c', '#e31a1c']
basemap(ax2, dist, M, pad=pad, labels=False, network=False)
fill(ax2, B.p30.astype(float).to_dict(), BB, CB, nodata_mask={'Y.Oxunboboyev': True})
REF = 1500.0; RMAX = 1700.0  # 1500 ming so'm/ga doirasining radiusi, m; yuza xarajatga mutanosib
for _, r in M.iterrows():
    v = B.loc[r['name']]; p = label_point(r.geometry, None, inset=900)
    if v.cost_per_ha > 0:
        rad = RMAX * np.sqrt(v.cost_per_ha / REF)
        ax2.add_patch(Circle((p.x, p.y), rad, fc='#3f007d', ec='white', lw=1.6, alpha=.55, zorder=8))
        ax2.add_patch(Circle((p.x, p.y), rad, fc='none', ec='#3f007d', lw=.6, zorder=8.1))
    t = r['name'] + ('' if r['name'] == 'Y.Oxunboboyev' else f"\nxavf {v.p30:.0f} %")
    label_halo(ax2.text(p.x, p.y - (RMAX * np.sqrt(max(v.cost_per_ha, 1) / REF) + 250 if v.cost_per_ha > 0 else 0), t, ha='center', va='top' if v.cost_per_ha > 0 else 'center',
                        fontsize=5.0, weight='bold', color='#222', zorder=25, linespacing=1.1), 2.0)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
h2 = [Patch(fc=cc, ec='#666', lw=.4, label=l) for cc, l in zip(CB, ['< 20', '20–40', '40–60', '≥ 60'])]
h2 += [Patch(fc='white', ec='#999', hatch='////', lw=.4, label='Baho yoʻq')]
legend_box(lg2, h2, title='Meliorativ xavf: yozda sath < 1,5 m boʻlish\nehtimoli > 0,3 boʻlgan maydon, % (3.3-§)', loc='upper left', bbox_to_anchor=(0, 1), ncol=2, fs=5.3, borderaxespad=0)
# doira o'lchamlari legendasi (haqiqiy masshtabda: ax2 bilan bir xil m/sm)
la = add_axes_cm(fig, .35 + PW + .5 + 4.35, BM + .05, 3.1, 1.75, FW, FH); la.axis('off')
mpc = (ax2.get_xlim()[1] - ax2.get_xlim()[0]) / PW  # metr / sm
la.set_xlim(0, 3.1 * mpc); la.set_ylim(0, 1.75 * mpc); la.set_aspect(1)
xb = .75 * mpc; yb = .15 * mpc
for v in (1500, 750, 250):
    rad = RMAX * np.sqrt(v / REF)
    la.add_patch(Circle((xb, yb + rad), rad, fc='#3f007d', ec='white', lw=.6, alpha=.55)); la.add_patch(Circle((xb, yb + rad), rad, fc='none', ec='#3f007d', lw=.5))
    la.plot([xb, xb + 1.0 * mpc], [yb + 2 * rad] * 2, color='#555', lw=.4); la.text(xb + 1.05 * mpc, yb + 2 * rad, f'{v:,}'.replace(',', ' '), fontsize=5.2, va='center')
la.text(0, 1.72 * mpc, 'Xarajat, ming soʻm/ga\n(doira yuzasi)', fontsize=5.4, weight='bold', va='top')
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Xarajat kollektor xaritadagi boʻlaklarining massivlardagi uzunligiga mutanosib taqsimlangan (36 ta kollektor, umumiy xarajatning 81 foizi); '
         '\njoriy narxlarda. Taʼmir turi narx boʻyicha ajratilgan (4.4-§). Spearman ρ (xarajat ~ xavf) = +0,39; p = 0,38; n = 7. Asos: Copernicus GLO-30 relyef soyasi.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep_ = export(fig, 'figures/map7_repair_cost', provenance={
    'raw_data': ['results/ch4_cost_ext.json (by_massif; table 4.5)', 'results/ch4_repair_costs.csv', 'gis/collectors_named.geojson', 'gis/massifs.geojson'],
    'transformations': ['cost per ha = allocated cost / irrigated ha (thousand UZS/ha)', 'repair type: cost_km < 50 mln UZS/km = light cleaning, else capital',
                        'circle area proportional to cost per ha (radius = 1700 m * sqrt(v/1500))', 'risk fill = p30 from 3.3-§'],
    'check_vs_table_4.5': {k: int(v) for k, v in B.cost_per_ha.items()}, 'caveat': 'current prices; 19% of cost not allocated to massifs'},
    alt_text="""Ikki panelli xarita, Marhamat tumani massivlari. a — 2017–2020-yillardagi kollektorlar taʼmir xarajati 1 ga ga: Istiqlol 1 576, U.Qoraboyev 1 214, Mashʼal 1 069,
T.Mirzayev 851, Z.M.Bobur 776, Paxtakor 614, M.Toʻjiboyev 125 ming soʻm/ga, Y.Oxunboboyevda kollektor yoʻq; kapital taʼmirlangan kollektorlar qora, yengil tozalanganlari
toʻq sariq uzuq chiziq. b — fonda meliorativ xavf (yozda sayoz sath ehtimoli), doiralar xarajatni bildiradi: xavf eng yuqori Mashʼal va Z.M.Bobur massivlarida, xarajat esa
Istiqlol va U.Qoraboyevda eng katta; U.Qoraboyevda xavf past (19 %), lekin xarajat yuqori.""")
