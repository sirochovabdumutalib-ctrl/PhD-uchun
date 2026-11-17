"""3.6-rasm (3.3-§): iyul–avgustdagi sizot suvi sathi (kriging) va sathning 1,5 m dan sayoz bo'lish ehtimoli P = Φ((1,5 − ẑ)/σ_K).
Hisob 18-skript bilan bir xil; massivlar bo'yicha ulushlar results/ch3_geo_ext.json (summer_map) bilan solishtiriladi.
Chiqish: figures/fig36_summer_prob.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
import importlib.util
spec = importlib.util.spec_from_file_location('k41', 'scripts/41_fig35_kriging.py'); k41 = importlib.util.module_from_spec(spec); spec.loader.exec_module(k41)
from carto import *
import matplotlib as mpl
from scipy import stats
from shapely import contains_xy
from shapely.geometry import MultiPoint, Point
from matplotlib.patches import PathPatch
from matplotlib.path import Path as MPath

x, y, v, P, gx, gy, GX, GY, Z, SE, dmin = k41.krige('level_summer_m')
PR = stats.norm.cdf((1.5 - Z) / SE)
dist = load('district'); M = massifs()
near = dmin <= 1500
# 18-skriptdagi kabi: massivlar bo'yicha ulushlar
ref = json.load(open('results/ch3_geo_ext.json'))['summer_map']; chk = {}
anyin = np.zeros(Z.shape, bool)
for _, r in M.iterrows():
    ins = contains_xy(r.geometry, GX, GY); anyin |= ins; m = ins & near
    old = ref['by_massif'][[k for k, vv in MASSIF_LAT.items() if vv == r['name']][0]]
    chk[r['name']] = dict(p30=round(float((PR[m] > .3).mean()), 3), p30_ref=old['p30'], sh20=round(float((Z[m] < 2).mean()), 3), sh20_ref=old['sh20'])
m = anyin & near
tot = dict(sh15=round(float((Z[m] < 1.5).mean()), 3), sh20=round(float((Z[m] < 2).mean()), 3), p30=round(float((PR[m] > .3).mean()), 3), p50=round(float((PR[m] > .5).mean()), 3), cover=round(float(m.sum() / anyin.sum()), 3))
print('tuman:', tot, '| ref:', {k: ref[k] for k in ('sh15', 'sh20', 'p30', 'p50', 'cover')}); print(chk)

AREA = MultiPoint(np.c_[x, y]).buffer(1500, quad_segs=24).intersection(dist.geometry.iloc[0])
def clip_patch(ax):
    verts, codes = [], []
    for pg in getattr(AREA, 'geoms', [AREA]):
        for ring in [pg.exterior] + list(pg.interiors):
            xy = np.asarray(ring.coords); verts += xy.tolist(); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
    pp = PathPatch(MPath(verts, codes), transform=ax.transData, fc='none', ec='none'); ax.add_patch(pp); return pp

FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 1.55; BM = .75
FH = BM + LH + PH + .25
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
ext = (gx[0] - 75, gx[-1] + 75, gy[0] - 75, gy[-1] + 75)
# a) yozgi sath — 3.5-rasm bilan bir xil shkala
LV = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 5.0]; CL = ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2', '#e5ecc9']
cmapA = mpl.colors.ListedColormap(CL); normA = mpl.colors.BoundaryNorm(LV, cmapA.N)
basemap(ax1, dist, M, pad=pad, network=False, labels=False)
im = ax1.imshow(Z, extent=ext, origin='lower', cmap=cmapA, norm=normA, interpolation='bilinear', alpha=.92, zorder=1.5); im.set_clip_path(clip_patch(ax1))
cs = ax1.contour(GX, GY, Z, levels=[1.5, 2.0, 2.5, 3.0, 3.5], colors='#4d4d4d', linewidths=.35, zorder=1.7); cs.set_clip_path(clip_patch(ax1))
for t in list(ax1.clabel(cs, fontsize=4.6, fmt=lambda q: f'{q:.1f}'.replace('.', ','), inline=True, inline_spacing=1)):
    if not AREA.buffer(-150).contains(Point(*t.get_position())): t.remove()
    else: label_halo(t, 1.0)
# b) ehtimollik — 0,3 chegarasi (3.5, 4.5, 4.7-jadvallarda ishlatilgan) qalin chiziq bilan
LP = [0, .1, .3, .5, .7, 1.0]; CP = ['#fff5f0', '#fcbba1', '#fb6a4a', '#cb181d', '#67000d']
cmapB = mpl.colors.ListedColormap(CP); normB = mpl.colors.BoundaryNorm(LP, cmapB.N)
basemap(ax2, dist, M, pad=pad, network=False, labels=False)
im = ax2.imshow(PR, extent=ext, origin='lower', cmap=cmapB, norm=normB, interpolation='bilinear', alpha=.95, zorder=1.5); im.set_clip_path(clip_patch(ax2))
c3 = ax2.contour(GX, GY, PR, levels=[.3], colors='#111', linewidths=.9, zorder=1.8); c3.set_clip_path(clip_patch(ax2))
col = load('collectors')
for a in (ax1, ax2):
    col.plot(ax=a, color='#00442a', lw=.45, alpha=.85, zorder=4); a.set_xlabel(''); a.set_ylabel('')
    a.scatter(x, y, s=4, c='#111', lw=0, zorder=12)
    plot_lines(a, [dist.geometry.iloc[0].exterior], color='#3a3a3a', lw=1.1, zorder=9)
north_arrow(ax1, x=.92, y=.86, size=.07); scale_bar(ax1, 5, x=.05, y=.035, segs=5, fs=5.6)
north_arrow(ax2, x=.92, y=.86, size=.07); scale_bar(ax2, 5, x=.05, y=.035, segs=5, fs=5.6)
for _, r in M.iterrows():
    p = label_point(r.geometry, np.c_[x, y])
    label_halo(ax1.text(p.x, p.y, r['name'], ha='center', va='center', fontsize=5.1, weight='bold', color='#222', zorder=25), 1.8)
    c_ = chk[r['name']]['p30']
    label_halo(ax2.text(p.x, p.y, f"{r['name']}\n{c_ * 100:.0f} %", ha='center', va='center', fontsize=5.1, weight='bold', color='#222', zorder=25, linespacing=1.1), 1.8)
ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top'); ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
for a_x, cmap_, norm_, ticks, lab, ttl in ((.35, cmapA, normA, LV[:-1], [f'{t:g}'.replace('.', ',') for t in LV[:-1]], 'Iyul–avgustdagi sizot suvi sathi (2019–2024), m'),
                                           (.35 + PW + .5, cmapB, normB, LP, ['0', '0,1', '0,3', '0,5', '0,7', '1'], 'Sath 1,5 m dan sayoz boʻlish ehtimoli (qora chiziq — 0,3)')):
    cax = add_axes_cm(fig, a_x + .3, BM + .75, PW - .6, .22, FW, FH)
    cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm_, cmap=cmap_), cax=cax, orientation='horizontal', ticks=ticks, spacing='uniform')
    cb.ax.set_xticklabels(lab); cb.ax.tick_params(labelsize=5.4, length=1.5, width=.4); cb.outline.set_linewidth(.4); cb.ax.set_title(ttl, fontsize=5.9, weight='bold', pad=3)
fig.text(.35 / FW, .1 / FH, 'Proyeksiya: WGS 84 / UTM 43N. Oddiy kriging, eksponensial variogramma (qisman plato ' + f'{P[0]:.2f}'.replace('.', ',') + ' m², radius ' + f'{P[1] / 1000:.0f}' + ' km, nagget ' + f'{P[2]:.2f}'.replace('.', ',') + ' m²); P = Φ((1,5 − ẑ)/σ_K).'
         + f'\n{len(v)} ta quduq. Xarita eng yaqin quduqqacha 1,5 km dan oshmaydigan va tuman ichidagi hudud uchun koʻrsatilgan. Chiziqlar — kollektorlar.'
         + '\nb da massiv yozuvida — ehtimollik 0,3 dan katta maydon ulushi.',
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/fig36_summer_prob', provenance={
    'raw_data': ['data/wells_metrics.csv (level_summer_m)', 'gis/collectors.geojson', 'gis/district.geojson', 'gis/massifs.geojson'],
    'transformations': ['ordinary kriging as script 18', 'P = Phi((1.5 - z)/SE)', 'display: nearest well <=1.5 km and inside district', 'massif shares: inside massif & nearest well <=1.5 km (as script 18)'],
    'check_vs_results': dict(district=tot, massifs=chk)},
    alt_text=f"""Ikki panelli xarita. a — iyul–avgustdagi sizot suvi sathining kriging xaritasi (2019–2024): koʻp qismida sath 1,5–2,5 m, 1,5 m dan sayoz maydon juda kichik ({tot['sh15'] * 100:.1f} foiz).
b — sathning 1,5 m dan sayoz boʻlish ehtimoli: ehtimollik 0,3 dan katta maydon tumanning {tot['p30'] * 100:.0f} foizi; Mashʼal ({chk['Mashʼal']['p30'] * 100:.0f} %), Z.M.Bobur ({chk['Z.M.Bobur']['p30'] * 100:.0f} %)
va Istiqlol ({chk['Istiqlol']['p30'] * 100:.0f} %) massivlarida eng katta.""")
