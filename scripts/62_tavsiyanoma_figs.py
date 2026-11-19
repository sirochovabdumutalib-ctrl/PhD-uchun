"""Tavsiyanomadagi [173] 6, 7 va 8-rasmlarni dissertatsiya uslubida, lotin yozuvida qayta chizish (ilovalar uchun).
Sonlar tavsiyanomaning 5.1, 5.4, 5.5-jadvallaridan va 8-rasmidagi yozuvlardan olingan (meliorativ ekspeditsiya va viloyat ma'lumotlari).
Chiqish: figures/tv_water.*, figures/tv_drainage.*, figures/tv_region_ratio.*"""
import os, sys
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
import numpy as np
from chartkit import plt, OI, fig, panel, axes_commas, export, fmt, cm
from carto import gpd, pd, CRS, frame, label_halo, north_arrow, scale_bar, add_axes_cm, legend_box
from matplotlib.patches import Patch

SRC = 'Manba: tavsiyanoma [173], meliorativ ekspeditsiya hisobotlari asosida.'
Y = [2014, 2015, 2016, 2019, 2020, 2022, 2023, 2024, 2025]
X = np.array([0, 1, 2, 3.6, 4.6, 5.6, 6.6, 7.6, 8.6])
# 5.1-jadval
LIM = [151.1, 183.5, 213.5, 206.7, 174.1, 148.1, 167.9, 159.0, 148.0]
ACT = [157.6, 203.6, 203.4, 191.5, 159.8, 138.5, 153.4, 147.3, 147.3]
VEG = [142.4, 159.0, np.nan, 138.2, 121.6, 113.6, 120.5, 124.8, 109.3]
PHA = [8568, 11065, 11056, 10945, 9132, 7704, 8532, 8195, 8200]
VHA = [7745, 8639, np.nan, 7900, 6950, 6319, 6704, 6943, 6084]

f, (a, b) = fig(15.5, 6.6, ncols=2)
a.bar(X - .2, LIM, .4, color='#c9d3e0', label='Limit (yillik)')
a.bar(X + .2, ACT, .4, color=OI['sky'], label='Amalda olingan (yillik)')
a.bar(X + .2, VEG, .4, color=OI['blue'], label='shu jumladan vegetatsiya davrida')
for x, v in zip(X, ACT): a.text(x + .2, v + 3, fmt(v, 0), ha='center', fontsize=6)
a.set_xticks(X, Y, rotation=0, fontsize=6.5); a.set_ylabel('mln m³'); a.axvline(2.8, color='#999', lw=.6, ls='--')
a.legend(loc='upper center', bbox_to_anchor=(.5, -.1), ncol=2, fontsize=6); a.set_ylim(0, 230)
b.plot(X, PHA, 'o-', color=OI['blue'], ms=3.5, label='Yillik, m³/ga')
m = ~np.isnan(VHA)
for seg in (slice(0, 2), slice(3, 9)):
    b.plot(X[seg], np.array(VHA)[seg], 's--', color=OI['verm'], ms=3, label='Vegetatsiya davrida, m³/ga' if seg.start == 0 else None)
b.axhline(6600, color='#555', lw=.7, ls=':'); b.text(-.1, 6650, 'oʻrtacha sugʻorish meʼyori 6 600 m³/ga', ha='left', va='bottom', fontsize=6, color='#555')
b.set_xticks(X, Y, fontsize=6.5); b.set_ylabel('m³/ga'); b.axvline(2.8, color='#999', lw=.6, ls='--'); b.set_ylim(5000, 12000); b.legend(loc='upper center', bbox_to_anchor=(.5, -.1), ncol=2, fontsize=6)
b.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f'{v:,.0f}'.replace(',', ' ')))
axes_commas(a); panel(a, 'a'); panel(b, 'b')
f.text(.01, -.06, SRC + ' 2017, 2018 va 2021-yillar boʻyicha maʼlumot berilmagan.', fontsize=6, color='#555')
export(f, 'figures/tv_water', dict(raw_data='tavsiyanoma [173], 5.1-jadval', transformations=['qayta chizish, lotin yozuvi']),
       'Marhamat tumaniga olingan sug‘orish suvi (a) va gektariga olingan suv (b), 2014–2025-yillar')

# 5.4 va 5.5-jadvallar
YD = [2016, 2019, 2020, 2022, 2023, 2024, 2025]
FLOW = [125.0, 200.1, 151.9, 90.1, 98.3, 98.2, 118.5]
RAT = [61.5, 104.5, 95.1, 65.1, 64.1, 66.7, 80.4]
MI = [.85, .60, .60, .38, .38, .40, .52]
MD = [.78, .81, .76, .66, .66, .75, .99]
SB = [4.10, -2.70, -1.12, -.38, -.37, -.91, -.60]
X = np.array([0, 1.6, 2.6, 3.6, 4.6, 5.6, 6.6])
f, (a, b) = fig(15.5, 6.6, ncols=2)
a.bar(X, RAT, .6, color=OI['orange'])
for x, r, q in zip(X, RAT, FLOW): a.text(x, r + 2, f'{fmt(r, 0)} %\n({fmt(q, 0)})', ha='center', fontsize=5.6)
a.set_xticks(X, YD, fontsize=6); a.set_ylabel('Zovur oqimi / olingan suv, %'); a.set_ylim(0, 125); a.axvline(.8, color='#999', lw=.6, ls='--')
f.text(.01, -.04, 'Qavs ichida — zovur oqimi, mln m³. 2014–2015-yillarda zovur oqimi toʻliq hisobga olinmagan. ' + SRC, fontsize=6, color='#555')
b2 = b.twinx(); b2.spines['right'].set_visible(True)
b2.bar(X, SB, .55, color=[OI['verm'] if v > 0 else OI['green'] for v in SB], alpha=.35, zorder=0)
b2.grid(False); b2.axhline(0, color='#999', lw=.6); b2.set_ylabel('Tuz balansi, t/ga'); b2.set_ylim(-3, 5)
b.plot(X, MI, 'o-', color=OI['blue'], ms=3.5, label='Sugʻorish suvi, g/l', zorder=3)
b.plot(X, MD, 's-', color=OI['orange'], ms=3.5, label='Zovur suvi, g/l', zorder=3)
b.set_zorder(b2.get_zorder() + 1); b.patch.set_visible(False)
b.set_xticks(X, YD, fontsize=6); b.set_ylabel('Minerallashuv, g/l'); b.set_ylim(0, 1.3); b.axvline(.8, color='#999', lw=.6, ls='--')
b.legend(handles=b.get_legend_handles_labels()[0] + [Patch(fc=OI['green'], alpha=.35, label='Tuz chiqishi'), Patch(fc=OI['verm'], alpha=.35, label='Tuz toʻplanishi')],
         loc='upper right', fontsize=6)
axes_commas(a, b, b2); panel(a, 'a'); panel(b, 'b')
export(f, 'figures/tv_drainage', dict(raw_data='tavsiyanoma [173], 5.4 va 5.5-jadvallar', transformations=['qayta chizish, lotin yozuvi']),
       'Zovur oqimining olingan suvga nisbati (a), sug‘orish va zovur suvining minerallashuvi hamda tuz balansi (b)')

# 8-rasm: tumanlarda berilgan suvning me'yorga nisbati (me'yor 6 600 m3/ga)
V = {'Paxtaobod': 116, 'Izboskan': 120, 'Baliqchi': 124, "Ulug'nor": 123, "Bo'ston": 122, 'Shahrixon': 132, "Oltinko'l": 132, 'Andijon': 121,
     'Jalaquduq': 127, "Qo'rg'ontepa": 120, 'Asaka': 118, 'Buloqboshi': 121, "Xo'jaobod": 130, 'Marhamat': 115}
GB = {"Oltinko'l": 'Altinkul', "Bo'ston": 'Boz', 'Shahrixon': 'Shakhrixan', "Ulug'nor": 'Ulugnar', 'Buloqboshi': 'Bulakbashi', 'Baliqchi': 'Balikchi',
      "Xo'jaobod": 'Khadjaabad', 'Izboskan': 'Izboskan', 'Marhamat': 'Markhamat', 'Andijon': 'Andijan', 'Jalaquduq': 'Djalalkuduk', "Qo'rg'ontepa": 'Kurgantepa',
      'Paxtaobod': 'Paxtaabad', 'Asaka': 'Asaka'}
ADM = 'gis/admin/'
a2 = gpd.read_file(ADM + 'UZB_ADM2.geojson'); a1 = gpd.read_file(ADM + 'UZB_ADM1.geojson'); reg = a1[a1.shapeName == 'Andijan Region']
a2['rp'] = a2.representative_point(); A = a2[a2.rp.within(reg.geometry.iloc[0])].drop(columns='rp').to_crs(CRS)
A['d'] = A.shapeName.map({v: k for k, v in GB.items()})
kg = gpd.read_file(ADM + 'KGZ_ADM0.geojson').to_crs(CRS); nb = a1[a1.shapeName.isin(['Namangan Region', 'Fergana Region'])].to_crs(CRS)
bx = A.total_bounds; EXT = (bx[0] - 3000, bx[1] - 3000, bx[2] + 3000, bx[3] + 3000)
FW = 15.5; PW = 15.0; PH = PW * (EXT[3] - EXT[1]) / (EXT[2] - EXT[0]); FH = PH + 1.6
f = plt.figure(figsize=(cm(FW), cm(FH))); ax = add_axes_cm(f, .25, 1.3, PW, PH, FW, FH)
kg.plot(ax=ax, fc='#e9e9e9', ec='#a0a0a0', lw=.4); nb.plot(ax=ax, fc='#f6f3ec', ec='#a0a0a0', lw=.4); frame(ax, EXT); ax.set_facecolor('#e9e9e9'); ax.set_xlabel(''); ax.set_ylabel('')
BR = [118, 122, 126, 130]; CL = ['#fef0d9', '#fdcc8a', '#fc8d59', '#e34a33', '#b30000']; LB = ['< 118', '118–122', '122–126', '126–130', '≥ 130']
for _, r in A.iterrows():
    fc = 'white' if pd.isna(r.d) else CL[np.digitize(V[r.d], BR)]
    gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax, fc=fc, ec='#555', lw=.45, hatch='////' if pd.isna(r.d) else None)
    if not pd.isna(r.d):
        p = r.geometry.representative_point()
        label_halo(ax.text(p.x, p.y, f"{r.d.replace(chr(39), 'ʻ')}\n{V[r.d]} %", ha='center', va='center', fontsize=5.6,
                           weight='bold' if r.d == 'Marhamat' else 'normal', zorder=25), 1.7)
A[A.d == 'Marhamat'].boundary.plot(ax=ax, color='#111', lw=2.0, zorder=5)
ax.set_xlabel(''); ax.set_ylabel('')
north_arrow(ax, x=.965, y=.80, size=.13); scale_bar(ax, 20, x=.02, y=.05, segs=4, fs=5.5, h_frac=.018)
la = add_axes_cm(f, .25, .45, PW, .8, FW, FH); la.axis('off')
legend_box(la, [Patch(fc=c, ec='#666', lw=.4, label=l) for c, l in zip(CL, LB)], title='Berilgan suvning meʼyorga nisbati, % (meʼyor 6 600 m³/ga)',
           loc='center left', ncol=5, fs=5.6, borderaxespad=0)
f.text(.25 / FW, .08 / FH, SRC + ' Chegaralar: geoBoundaries (CC BY 4.0, soddalashtirilgan).', fontsize=5.2, color='#555')
export(f, 'figures/tv_region_ratio', dict(raw_data='tavsiyanoma [173], 8-rasm yozuvlari', transformations=['qayta chizish, lotin yozuvi']),
       'Andijon viloyati tumanlarida berilgan sug‘orish suvining me’yorga nisbati')
print('ok')
