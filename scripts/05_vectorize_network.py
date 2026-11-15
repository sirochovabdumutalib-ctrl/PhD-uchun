"""Xarita rastridan kollektor (yashil) va kanal (ko'k) chiziqlarini ajratib, skeletlab, GeoJSON ga yozadi.
Ishlatish: python3 scripts/05_vectorize_network.py <prefix> <gis_dir>"""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, remove_small_objects
from pyproj import Transformer
Image.MAX_IMAGE_PIXELS = None
prefix, GIS = sys.argv[1], sys.argv[2]
a = np.asarray(Image.open(prefix + '_raster.png')).astype(int)
M = np.array(json.load(open(GIS + '/georef.json'))['affine_px_to_utm43n'])
inv = Transformer.from_crs(32643, 4326, always_xy=True)
def mask(rgb, tol=8): return (abs(a[:, :, 0] - rgb[0]) < tol) & (abs(a[:, :, 1] - rgb[1]) < tol) & (abs(a[:, :, 2] - rgb[2]) < tol)
well = ndi.binary_dilation(mask((115, 178, 255)) | mask((0, 0, 0)), iterations=3)   # quduq belgilari chiziqni uzadi
legend_cut = int(a.shape[0] * 0.70)
def trace(sk):
    """Skelet piksellaridan polyliniyalar: tugun = qo'shnilari soni != 2 bo'lgan piksel."""
    ys, xs = np.nonzero(sk); pts = set(zip(ys.tolist(), xs.tolist()))
    nb = lambda p: [(p[0] + dy, p[1] + dx) for dy in (-1, 0, 1) for dx in (-1, 0, 1) if (dy or dx) and (p[0] + dy, p[1] + dx) in pts]
    deg = {p: len(nb(p)) for p in pts}; nodes = {p for p, d in deg.items() if d != 2}
    lines, seen = [], set()
    for n in nodes:
        for q in nb(n):
            if (n, q) in seen: continue
            path = [n, q]; seen.add((n, q)); prev, cur = n, q
            while cur not in nodes:
                nx = [r for r in nb(cur) if r != prev and r not in path[-3:]]
                if not nx: break
                prev, cur = cur, nx[0]; path.append(cur)
            seen.add((path[-1], path[-2])); lines.append(path)
    # tugunsiz halqalar
    return lines
def layer(rgb, name, bridge):
    m = mask(rgb); m[legend_cut:, : int(a.shape[1] * 0.35)] = False            # shartli belgilar qismini chiqarish
    m = m | (ndi.binary_dilation(m, iterations=bridge) & well)                  # belgi ostidagi uzilishlarni ulash
    m = ndi.binary_closing(m, iterations=2); m = remove_small_objects(m, 300)
    sk = skeletonize(m); lines = trace(sk); feats = []; total = 0
    for path in lines:
        if len(path) < 2: continue
        P = np.array([(x, y) for y, x in path], float)
        if len(P) > 6: P = np.r_[P[:1], P[3:-3:3], P[-1:]]                       # siyraklashtirish
        U = np.c_[P, np.ones(len(P))] @ M; L = float(np.linalg.norm(np.diff(U, axis=0), axis=1).sum())
        if L < 40: continue                                                       # skelet "soqollari"
        lon, lat = inv.transform(U[:, 0], U[:, 1]); total += L
        feats.append({'type': 'Feature', 'properties': {'layer': name, 'length_m': round(L, 1)},
                      'geometry': {'type': 'LineString', 'coordinates': [[round(x, 6), round(y, 6)] for x, y in zip(lon, lat)]}})
    json.dump({'type': 'FeatureCollection', 'features': feats}, open(f'{GIS}/{name}.geojson', 'w'))
    print(name, 'segments', len(feats), 'total km', round(total / 1000, 2), 'mask px', int(m.sum()))
layer((76, 230, 0), 'collectors', 12)
layer((0, 112, 255), 'canals', 12)
