"""3.5-rasm (3.3-§): 2019–2024-yillardagi o'rtacha sizot suvi sathining oddiy kriging xaritasi (a) va bahoning standart xatosi (b).
Kriging 18-skript bilan bir xil: eksponensial variogramma (fitv), panjara 150 m, ko'rsatish hududi — eng yaqin quduqqacha ≤ 1,5 km.
Chiqish: figures/fig35_kriging.{png,pdf}, results/fig35_stats.json"""
import os, sys, json, warnings
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
import matplotlib as mpl
from scipy.spatial import cKDTree
from scipy.optimize import curve_fit
from pykrige.ok import OrdinaryKriging
from shapely import contains_xy
warnings.filterwarnings('ignore')

VG = {'exponential': lambda h, ps, r, n: n + ps * (1 - np.exp(-h / r))}
def empv(x, y, v, maxd=10000, step=500):
    h = np.hypot(x[:, None] - x[None], y[:, None] - y[None]); g = 0.5 * (v[:, None] - v[None]) ** 2; iu = np.triu_indices(len(v), 1); h, g = h[iu], g[iu]
    lags = np.arange(0, maxd + 1, step); mid, gam, npr = [], [], []
    for k in range(len(lags) - 1):
        m = (h > lags[k]) & (h <= lags[k + 1])
        if m.sum() >= 20: mid.append(h[m].mean()); gam.append(g[m].mean()); npr.append(m.sum())
    return np.array(mid), np.array(gam), np.array(npr)
def fitv(x, y, v):
    mid, gam, npr = empv(x, y, v)
    p, _ = curve_fit(VG['exponential'], mid, gam, p0=[gam.max() - gam.min(), 3000, gam.min()], sigma=gam / np.sqrt(npr), bounds=([0.01, 300, 0], [5, 30000, 2]), maxfev=20000)
    return [float(q) for q in p]
def krige(var):
    W = pd.read_csv('data/wells_metrics.csv'); K = W.dropna(subset=[var]); x, y, v = K.x_utm43.values, K.y_utm43.values, K[var].values
    P = fitv(x, y, v); o = OrdinaryKriging(x, y, v, variogram_model='exponential', variogram_parameters={'psill': P[0], 'range': P[1], 'nugget': P[2]})
    gx = np.arange(x.min() - 500, x.max() + 500, 150); gy = np.arange(y.min() - 500, y.max() + 500, 150); Z, S2 = o.execute('grid', gx, gy)
    GX, GY = np.meshgrid(gx, gy); dmin = cKDTree(np.c_[x, y]).query(np.c_[GX.ravel(), GY.ravel()])[0].reshape(Z.shape)
    return x, y, v, P, gx, gy, GX, GY, np.asarray(Z), np.sqrt(np.asarray(S2)), dmin

if __name__ == '__main__':
    x, y, v, P, gx, gy, GX, GY, Z, SE, dmin = krige('level_2019_2024_m')
    dist = load('district'); M = massifs()
    near = dmin <= 1500; ind = contains_xy(dist.geometry.iloc[0], GX, GY); show = near & ind
    st = dict(params=dict(psill=round(P[0], 3), range_m=round(P[1]), nugget=round(P[2], 3)),
              text_mask=dict(zmin=round(float(Z[near].min()), 2), zmax=round(float(Z[near].max()), 2), sh20=round(float((Z[near] < 2).mean()), 3), se_min=round(float(SE[near].min()), 2), se_max=round(float(SE[near].max()), 2)),
              district_mask=dict(zmin=round(float(Z[show].min()), 2), zmax=round(float(Z[show].max()), 2), sh20=round(float((Z[show] < 2).mean()), 3), se_min=round(float(SE[show].min()), 2), se_max=round(float(SE[show].max()), 2),
                                 cover=round(float(show.sum() / ind.sum()), 3)))
    json.dump(st, open('results/fig35_stats.json', 'w'), indent=1); print(st)

    FW = 16.0; x0, y0, x1, y1 = dist.total_bounds; pad = 700
    PW = 7.55; PH = PW * (y1 - y0 + 2 * pad) / (x1 - x0 + 2 * pad); LH = 1.55; BM = .62
    FH = BM + LH + PH + .25
    fig = plt.figure(figsize=(cm(FW), cm(FH)))
    ax1 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35 + PW + .5, BM + LH, PW, PH, FW, FH)
    ext = (gx[0] - 75, gx[-1] + 75, gy[0] - 75, gy[-1] + 75)
    from shapely.geometry import MultiPoint
    from matplotlib.patches import PathPatch
    from matplotlib.path import Path as MPath
    AREA = MultiPoint(np.c_[x, y]).buffer(1500, quad_segs=24).intersection(dist.geometry.iloc[0])   # ko'rsatish hududi
    def clip_patch(ax):
        verts, codes = [], []
        for pg in getattr(AREA, 'geoms', [AREA]):
            for ring in [pg.exterior] + list(pg.interiors):
                xy = np.asarray(ring.coords); verts += xy.tolist(); codes += [MPath.MOVETO] + [MPath.LINETO] * (len(xy) - 2) + [MPath.CLOSEPOLY]
        pp = PathPatch(MPath(verts, codes), transform=ax.transData, fc='none', ec='none'); ax.add_patch(pp); return pp
    # a) sath — sayoz = xavfli (qizil), 0,5 m li sinflar
    LV = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 5.0]; CL = ['#bd0026', '#f03b20', '#fd8d3c', '#fecc5c', '#ffffb2', '#e5ecc9']
    cmapA = mpl.colors.ListedColormap(CL); normA = mpl.colors.BoundaryNorm(LV, cmapA.N)
    basemap(ax1, dist, M, pad=pad, network=False, labels=False)
    im = ax1.imshow(Z, extent=ext, origin='lower', cmap=cmapA, norm=normA, interpolation='bilinear', alpha=.92, zorder=1.5); im.set_clip_path(clip_patch(ax1))
    cs = ax1.contour(GX, GY, Z, levels=[1.5, 2.0, 2.5, 3.0, 3.5], colors='#4d4d4d', linewidths=.35, zorder=1.7)
    cs.set_clip_path(clip_patch(ax1))
    cl = ax1.clabel(cs, fontsize=4.6, fmt=lambda q: f'{q:.1f}'.replace('.', ','), inline=True, inline_spacing=1)
    from shapely.geometry import Point as _Pt
    for t in list(cl):
        if not AREA.buffer(-150).contains(_Pt(*t.get_position())): t.remove()
        else: label_halo(t, 1.0)
    # b) standart xato
    LS = [.75, .8, .85, .9, .95, 1.0, 1.2]; CS = ['#f2f0f7', '#dadaeb', '#bcbddc', '#9e9ac8', '#756bb1', '#54278f']
    cmapB = mpl.colors.ListedColormap(CS); normB = mpl.colors.BoundaryNorm(LS, cmapB.N)
    basemap(ax2, dist, M, pad=pad, network=False, labels=False)
    im = ax2.imshow(SE, extent=ext, origin='lower', cmap=cmapB, norm=normB, interpolation='bilinear', alpha=.95, zorder=1.5); im.set_clip_path(clip_patch(ax2))
    col = load('collectors')
    for a in (ax1, ax2):
        col.plot(ax=a, color='#00442a', lw=.45, alpha=.85, zorder=4); a.set_xlabel(''); a.set_ylabel('')
        a.scatter(x, y, s=4, c='#111', lw=0, zorder=12)
        plot_lines(a, [dist.geometry.iloc[0].exterior], color='#3a3a3a', lw=1.1, zorder=9)
        for _, r in M.iterrows():
            p = label_point(r.geometry, np.c_[x, y]); label_halo(a.text(p.x, p.y, r['name'], ha='center', va='center', fontsize=5.1, weight='bold', color='#222', zorder=25), 1.8)
        north_arrow(a, x=.92, y=.86, size=.07); scale_bar(a, 5, x=.05, y=.035, segs=5, fs=5.6)
    ax1.text(.03, .985, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top'); ax2.text(.03, .985, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
    for a_x, cmap_, norm_, ticks, ttl in ((.35, cmapA, normA, LV[:-1], 'Sizot suvi sathi (2019–2024-yillar oʻrtachasi), m'),
                                          (.35 + PW + .5, cmapB, normB, LS[:-1], 'Bahoning standart xatosi, m')):
        cax = add_axes_cm(fig, a_x + .3, BM + .75, PW - .6, .22, FW, FH)
        cb = fig.colorbar(mpl.cm.ScalarMappable(norm=norm_, cmap=cmap_), cax=cax, orientation='horizontal', ticks=ticks, spacing='uniform')
        cb.ax.set_xticklabels([f'{t:g}'.replace('.', ',') for t in ticks]); cb.ax.tick_params(labelsize=5.4, length=1.5, width=.4); cb.outline.set_linewidth(.4)
        cb.ax.set_title(ttl, fontsize=5.9, weight='bold', pad=3)
    fig.text(.35 / FW, .1 / FH, f'Proyeksiya: WGS 84 / UTM 43N. Oddiy kriging, eksponensial variogramma (qisman plato {P[0]:.2f} m², radius {P[1] / 1000:.0f} km, nagget {P[2]:.2f} m²), panjara 150 m; '.replace('.', ',')
             + f'\n{len(v)} ta quduq (nuqtalar). Xarita eng yaqin quduqqacha 1,5 km dan oshmaydigan va tuman ichidagi hudud uchun koʻrsatilgan (tuman maydonining {st["district_mask"]["cover"] * 100:.0f} foizi). Chiziqlar — kollektorlar.',
             fontsize=5.0, color='#555', ha='left', va='bottom')
    rep = export(fig, 'figures/fig35_kriging', provenance={
        'raw_data': ['data/wells_metrics.csv (level_2019_2024_m)', 'gis/collectors.geojson', 'gis/district.geojson', 'gis/massifs.geojson'],
        'transformations': ['ordinary kriging, exponential variogram fitted as in script 18', 'grid 150 m; display where nearest well <=1.5 km and inside district',
                            'classes: level 0.5 m; SE 0.05 m'], 'stats': st},
        alt_text=f"""Ikki panelli xarita. a — 2019–2024-yillardagi oʻrtacha sizot suvi sathining kriging xaritasi: sath {st['district_mask']['zmin']:.2f}–{st['district_mask']['zmax']:.2f} m; sayoz sath (qizil, 2 m dan sayoz)
shimoliy-sharqdan janubi-gʻarbga choʻzilgan, kollektorlar zich hududda; chuqur sath (sariq) janub va sharqda. b — bahoning standart xatosi
{st['district_mask']['se_min']:.2f}–{st['district_mask']['se_max']:.2f} m; quduqlar siyrak chekka hududlarda eng katta.""")
