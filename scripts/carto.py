"""Dissertatsiya GAT xaritalari uchun umumiy kartografik vositalar.
Proyeksiya: WGS 84 / UTM 43N (EPSG:32643). Barcha xaritalar 300 dpi, Liberation Sans shrifti."""
import json, numpy as np, pandas as pd, geopandas as gpd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrow, Polygon as MplPolygon
from matplotlib.lines import Line2D
from pyproj import Transformer
from shapely.geometry import LineString, box

CRS = 32643
TO_LL = Transformer.from_crs(CRS, 4326, always_xy=True)
TO_UTM = Transformer.from_crs(4326, CRS, always_xy=True)
plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8, 'axes.linewidth': .8,
                     'savefig.dpi': 300, 'figure.dpi': 100, 'pdf.fonttype': 42})

MASSIF_LAT = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': 'M.Toʻjiboyev',
              'Машъал': 'Mashʼal', 'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzayev', 'У.Қорабоев': 'U.Qoraboyev'}
C = dict(collector='#1b7f5f', canal='#2c6fbb', boundary='#7a1f1f', massif='#5a5a5a', well='#111111',
         water='#bcd9f0', land='#f4f1ea', text='#1a1a1a')


def load(name):
    return gpd.read_file(f'gis/{name}.geojson').to_crs(CRS)


def massifs():
    m = load('massifs'); m['name'] = m.massif.map(MASSIF_LAT); return m


def frame(ax, bounds, pad=0.0):
    x0, y0, x1, y1 = bounds
    ax.set_xlabel(''); ax.set_ylabel('')
    ax.set_xlim(x0 - pad, x1 + pad); ax.set_ylim(y0 - pad, y1 + pad); ax.set_aspect(1)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_linewidth(1.0); s.set_color('#222')


def _fmt(v, lat):
    d = int(np.floor(v + 1e-9)); m = int(round((v - d) * 60))
    if m == 60: d, m = d + 1, 0
    return f"{d}°{m:02d}′{'N' if lat else 'E'}" if m else f"{d}°{'N' if lat else 'E'}"


def graticule(ax, step_min=5, label=True, color='#8a8a8a', fs=6.5, sides=('bottom', 'left')):
    """Geografik to'r (kenglik/uzunlik chiziqlari) va ramka chetidagi yozuvlar."""
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim()
    lons, lats = TO_LL.transform([x0, x1, x0, x1], [y0, y0, y1, y1])
    st = step_min / 60
    frm = box(x0, y0, x1, y1)
    edges = {'bottom': LineString([(x0, y0), (x1, y0)]), 'top': LineString([(x0, y1), (x1, y1)]),
             'left': LineString([(x0, y0), (x0, y1)]), 'right': LineString([(x1, y0), (x1, y1)])}
    def draw(coords, lat):
        xs, ys = TO_UTM.transform(*zip(*coords)); ln = LineString(zip(xs, ys)).intersection(frm)
        if ln.is_empty: return
        for g in getattr(ln, 'geoms', [ln]):
            ax.plot(*g.xy, color=color, lw=.35, ls=(0, (4, 3)), zorder=8)
        return LineString(zip(xs, ys))
    for lo in np.arange(np.floor(min(lons) / st) * st, max(lons) + st, st):
        L = draw([(lo, la) for la in np.linspace(min(lats) - .1, max(lats) + .1, 60)], False)
        if L is None or not label: continue
        for e in [e for e in ('bottom', 'top') if e in sides]:
            p = L.intersection(edges[e])
            if p.geom_type == 'Point':
                ax.annotate(_fmt(lo, False), (p.x, p.y), xytext=(0, -3 if e == 'bottom' else 3), textcoords='offset points',
                            ha='center', va='top' if e == 'bottom' else 'bottom', fontsize=fs, color='#333', annotation_clip=False)
    for la in np.arange(np.floor(min(lats) / st) * st, max(lats) + st, st):
        L = draw([(lo, la) for lo in np.linspace(min(lons) - .1, max(lons) + .1, 60)], True)
        if L is None or not label: continue
        for e in [e for e in ('left', 'right') if e in sides]:
            p = L.intersection(edges[e])
            if p.geom_type == 'Point':
                ax.annotate(_fmt(la, True), (p.x, p.y), xytext=(-3 if e == 'left' else 3, 0), textcoords='offset points',
                            ha='right' if e == 'left' else 'left', va='center', rotation=90, rotation_mode='anchor', fontsize=fs, color='#333', annotation_clip=False)


def north_arrow(ax, x=.93, y=.88, size=.07):
    ax.annotate('', xy=(x, y + size), xytext=(x, y), xycoords='axes fraction',
                arrowprops=dict(arrowstyle='-|>', lw=1.4, color='#111', mutation_scale=14), zorder=20)
    ax.text(x, y + size + .012, 'Sh', transform=ax.transAxes, ha='center', va='bottom', fontsize=9, weight='bold', zorder=20)


def scale_bar(ax, length_km, x=.06, y=.05, segs=4, h_frac=.012, fs=6.5):
    """Kesmali masshtab chizg'ichi (km)."""
    x0, x1 = ax.get_xlim(); y0, y1 = ax.get_ylim(); W, H = x1 - x0, y1 - y0
    bx, by, h = x0 + x * W, y0 + y * H, h_frac * H; L = length_km * 1000; s = L / segs
    ax.add_patch(Rectangle((bx - .015 * W, by - .035 * H), L + .05 * W, .075 * H, fc='white', ec='none', alpha=.85, zorder=19))
    for i in range(segs):
        ax.add_patch(Rectangle((bx + i * s, by), s, h, fc='#111' if i % 2 == 0 else 'white', ec='#111', lw=.6, zorder=20))
    for i in (0, segs // 2, segs):
        v = length_km * i / segs
        ax.text(bx + i * s, by + h * 1.6, (f'{v:g}').replace('.', ','), ha='center', va='bottom', fontsize=fs, zorder=20)
    ax.text(bx + L + .012 * W, by + h / 2, 'km', ha='left', va='center', fontsize=fs, zorder=20)


def hillshade(z, dx, az=315, alt=45, zf=3.0):
    gy, gx = np.gradient(z * zf, dx)
    slope = np.pi / 2 - np.arctan(np.hypot(gx, gy)); aspect = np.arctan2(-gx, gy)
    a, al = np.radians(360 - az + 90), np.radians(alt)
    return np.clip(np.sin(al) * np.sin(slope) + np.cos(al) * np.cos(slope) * np.cos(a - aspect), 0, 1)


def elevation_grid(district, res=60, smoothing=40, support=1500):
    """Kuzatuv quduqlarining mutlaq belgilari bo'yicha relyef yuzasi (thin-plate spline, silliqlangan)."""
    from scipy.interpolate import RBFInterpolator
    from shapely import contains_xy
    p = pd.read_csv('data/wells_passport.csv'); w = load('wells_2024')
    nrm = lambda s: str(s).strip().upper().replace(' ', '')
    p['k'] = p.well_no.map(nrm); w['k'] = w.well_no.map(nrm); w['x_utm43'] = w.geometry.x; w['y_utm43'] = w.geometry.y
    d = p.merge(pd.DataFrame(w[['k', 'x_utm43', 'y_utm43']]), on='k').dropna(subset=['abs_mark_raw', 'x_utm43'])
    d['z'] = d.abs_mark_raw / 1000
    x0, y0, x1, y1 = district.total_bounds
    gx, gy = np.meshgrid(np.arange(x0 - 2000, x1 + 2000, res), np.arange(y0 - 2000, y1 + 2000, res))
    f = RBFInterpolator(d[['x_utm43', 'y_utm43']].values, d.z.values, kernel='thin_plate_spline', smoothing=smoothing)
    z = f(np.c_[gx.ravel(), gy.ravel()]).reshape(gx.shape)
    z = np.clip(z, d.z.min() - 5, d.z.max() + 5)
    inside = contains_xy(district.geometry.union_all(), gx, gy)
    from scipy.spatial import cKDTree
    dd, _ = cKDTree(d[['x_utm43', 'y_utm43']].values).query(np.c_[gx.ravel(), gy.ravel()])
    supported = (dd.reshape(gx.shape) <= support) & inside
    return gx, gy, z, inside, d, supported


def legend_box(ax, handles, title=None, loc='lower right', ncol=1, fs=6.8, **kw):
    lg = ax.legend(handles=handles, title=title, loc=loc, ncol=ncol, fontsize=fs, title_fontsize=fs + .4, frameon=True,
                   fancybox=False, edgecolor='#444', framealpha=.95, borderpad=.6, labelspacing=.45, handlelength=1.8, **kw)
    lg.get_frame().set_linewidth(.6); lg.set_zorder(30)
    if title: lg.get_title().set_fontweight('bold')
    return lg


def source_note(fig, text, y=.006):
    fig.text(.012, y, text, fontsize=5.8, color='#555', ha='left', va='bottom')


def label_halo(txt, w=2.2):
    import matplotlib.patheffects as pe
    txt.set_path_effects([pe.withStroke(linewidth=w, foreground='white')]); return txt


def plot_lines(ax, geoms, **kw):
    """Chiziqlarni (shu jumladan poligon chegaralarini) matplotlib orqali chizish: ixtiyoriy shtrix uslubi bilan."""
    for g in geoms:
        if g is None or g.is_empty: continue
        for part in getattr(g, 'geoms', [g]):
            ax.plot(*part.xy, **kw)


def dem(path='gis/dem/marhamat_dem30_utm43.tif'):
    """Copernicus GLO-30 DEM, UTM 43N ga qayta proyeksiyalangan (30 m). Qaytaradi: z, gx, gy, extent."""
    import rasterio
    with rasterio.open(path) as s:
        z = s.read(1); t = s.transform
    H, W = z.shape
    xs = t.c + t.a * (np.arange(W) + .5); ys = t.f + t.e * (np.arange(H) + .5)
    gx, gy = np.meshgrid(xs, ys)
    return z, gx, gy, (t.c, t.c + t.a * W, t.f + t.e * H, t.f)


def cm(v): return v / 2.54


def add_axes_cm(fig, x, y, w, h, fw, fh):
    return fig.add_axes([x / fw, y / fh, w / fw, h / fh])


def massif_lines(M, district=None):
    """Massivlar chegaralari: umumiy chegaralar bir marta, tuman chegarasiga to'g'ri keladiganlari olib tashlangan."""
    from shapely import unary_union, line_merge, set_precision
    u = line_merge(unary_union([set_precision(b, 5) for b in M.boundary]))
    if district is not None: u = u.difference(district.boundary.union_all().buffer(40))
    return list(getattr(u, 'geoms', [u]))
