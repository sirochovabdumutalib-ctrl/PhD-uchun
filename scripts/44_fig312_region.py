"""3.12-rasm (3.6-§): Andijon viloyati tumanlari — a) monitoring ma'lumotlarining yaroqli o'lchovlar ulushi;
b) barqaror panel bo'yicha sath tendensiyasi (Sen qiyaligi) va yozgi sath medianasi. Manba: results/ch3_region.json (22-skript);
chegaralar — geoBoundaries gbOpen ADM2 (soddalashtirilgan). Chiqish: figures/fig312_region.{png,pdf}"""
import os, sys, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import *
from matplotlib.patches import Patch

R = json.load(open('results/ch3_region.json')); T = pd.DataFrame(R['table']).set_index('district')
GB = {"Oltinko'l": 'Altinkul', "Bo'ston": 'Boz', 'Shahrixon': 'Shakhrixan', "Ulug'nor": 'Ulugnar', 'Buloqboshi': 'Bulakbashi', 'Baliqchi': 'Balikchi',
      "Xo'jaobod": 'Khadjaabad', 'Izboskan': 'Izboskan', 'Marhamat': 'Markhamat', 'Andijon': 'Andijan', 'Jalaquduq': 'Djalalkuduk', "Qo'rg'ontepa": 'Kurgantepa',
      'Paxtaobod': 'Paxtaabad', 'Asaka': 'Asaka'}
NM = {k: k.replace("'", 'ʻ') for k in GB}
ADM = 'gis/admin/'
a2 = gpd.read_file(ADM + 'UZB_ADM2.geojson'); a1 = gpd.read_file(ADM + 'UZB_ADM1.geojson'); reg = a1[a1.shapeName == 'Andijan Region']
a2['rp'] = a2.representative_point(); A = a2[a2.rp.within(reg.geometry.iloc[0])].drop(columns='rp').to_crs(CRS)
inv = {v: k for k, v in GB.items()}; A['d'] = A.shapeName.map(inv)
missing = set(GB) - set(A.d.dropna()); assert not missing, missing
rg = gpd.GeoDataFrame(geometry=[A.geometry.union_all()], crs=CRS)  # viloyat chegarasi — tumanlar birlashmasidan (mos kelishi uchun)
_rg_unused = reg.to_crs(CRS); nb = a1[a1.shapeName.isin(['Namangan Region', 'Fergana Region'])].to_crs(CRS); kg = gpd.read_file(ADM + 'KGZ_ADM0.geojson').to_crs(CRS)
bx = rg.total_bounds; pb = 3500; EXT = (bx[0] - pb, bx[1] - pb, bx[2] + pb, bx[3] + pb)
FW = 16.0; PW = 15.3; PH = PW * (EXT[3] - EXT[1]) / (EXT[2] - EXT[0]); LH = 1.05; BM = .62
FH = BM + 2 * (PH + LH) + .3
fig = plt.figure(figsize=(cm(FW), cm(FH)))
ax1 = add_axes_cm(fig, .35, BM + LH + PH + LH + .05, PW, PH, FW, FH); ax2 = add_axes_cm(fig, .35, BM + LH, PW, PH, FW, FH)

def base(ax):
    kg.plot(ax=ax, fc='#e9e9e9', ec='#a0a0a0', lw=.4, zorder=0); nb.plot(ax=ax, fc='#f6f3ec', ec='#a0a0a0', lw=.4, zorder=0)
    frame(ax, EXT); ax.set_facecolor('#e9e9e9')
    for t, lo, la in [('QIRGʻIZISTON', 72.95, 40.55), ('Namangan viloyati', 71.85, 41.02), ('Fargʻona viloyati', 71.85, 40.62)]:
        x_, y_ = TO_UTM.transform(lo, la)
        if EXT[0] < x_ < EXT[2] and EXT[1] < y_ < EXT[3]: ax.text(x_, y_, t, ha='center', fontsize=5.6, color='#777', style='italic', zorder=1)

OFF = {}
def finish(ax, labels):
    A[A.d.isna()].plot(ax=ax, fc='white', ec='#999', hatch='////', lw=0, zorder=1.5)
    A.boundary.plot(ax=ax, color='#555', lw=.45, zorder=3); rg.boundary.plot(ax=ax, color='#222', lw=1.0, zorder=4)
    A[A.d == 'Marhamat'].boundary.plot(ax=ax, color='#111', lw=2.0, zorder=5)
    ax.set_xlabel(''); ax.set_ylabel('')
    for _, r in A.iterrows():
        p = r.geometry.representative_point()
        if pd.isna(r.d):
            continue
        t = NM[r.d] + '\n' + labels[r.d]
        dx, dy = OFF.get(r.d, (0, 0))
        label_halo(ax.text(p.x + dx, p.y + dy, t, ha='center', va='center', fontsize=5.0, weight='bold' if r.d == 'Marhamat' else 'normal', color='#111', zorder=25, linespacing=1.05), 1.7)
    north_arrow(ax, x=.965, y=.78, size=.13); scale_bar(ax, 20, x=.02, y=.05, segs=4, fs=5.5, h_frac=.018)

# a) yaroqli o'lchovlar ulushi (qizil — sifat past)
BA = [75, 85, 95]; CA = ['#bd0026', '#fd8d3c', '#fed976', '#ffffcc']; LA = ['< 75', '75–85', '85–95', '≥ 95']
base(ax1)
for _, r in A[A.d.notna()].iterrows():
    gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax1, fc=CA[np.digitize(T.loc[r.d, 'valid_share'], BA)], ec='none', zorder=1.5)
finish(ax1, {d: f"{T.loc[d, 'valid_share']:.1f} %".replace('.', ',') for d in GB})
ax1.text(.012, .97, 'a', transform=ax1.transAxes, fontsize=10, weight='bold', va='top')
# b) Sen qiyaligi (barcha tumanlarda chuqurlashish) — ketma-ket ko'k shkala; ahamiyatsiz — nuqtali shtrix
BB = [1, 2, 4, 6]; CB = ['#eff3ff', '#bdd7e7', '#6baed6', '#3182bd', '#08519c']; LB = ['< 1', '1–2', '2–4', '4–6', '≥ 6']
base(ax2)
for _, r in A[A.d.notna()].iterrows():
    v = T.loc[r.d, 'sen'] * 100; gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc=CB[np.digitize(v, BB)], ec='none', zorder=1.5)
    if T.loc[r.d, 'p'] >= .05: gpd.GeoSeries([r.geometry], crs=CRS).plot(ax=ax2, fc='none', ec='#555', hatch='....', lw=0, zorder=1.6)
OFF.update({"Xo'jaobod": (3500, -2500), 'Buloqboshi': (-2500, 1500)})
finish(ax2, {d: (f"{T.loc[d, 'sen'] * 100:+.1f} sm/yil\n{T.loc[d, 'summer_med']:.2f} m").replace('.', ',') for d in GB})
ax2.text(.012, .97, 'b', transform=ax2.transAxes, fontsize=10, weight='bold', va='top')
# legendalar
la = add_axes_cm(fig, .35, BM + LH + PH + .02, PW, LH, FW, FH); la.axis('off')
legend_box(la, [Patch(fc=c, ec='#666', lw=.4, label=l) for c, l in zip(CA, LA)] + [Patch(fc='white', ec='#999', hatch='////', lw=.4, label='Shahar (alohida hisoblanmagan)')],
           title='Yaroqli oʻlchovlar ulushi, %', loc='center left', ncol=5, fs=5.4, borderaxespad=0, columnspacing=1.0)
lb = add_axes_cm(fig, .35, BM + .02, PW, LH, FW, FH); lb.axis('off')
legend_box(lb, [Patch(fc=c, ec='#666', lw=.4, label=l) for c, l in zip(CB, LB)] + [Patch(fc='white', ec='#555', hatch='....', lw=.4, label='p ≥ 0,05')],
           title='Sathning oʻzgarish tezligi (doimiy kuzatilgan quduqlar), sm/yil — chuqurlashish; yozuvda: oʻzgarish tezligi va yozgi sath medianasi (2019–2023)', loc='center left', ncol=6, fs=5.4, borderaxespad=0, columnspacing=1.0)
fig.text(.35 / FW, .1 / FH, "Proyeksiya: WGS 84 / UTM 43N. Manba: viloyat meliorativ ekspeditsiyasi monitoring jadvallari (14 ta tuman, "
         + f"{R['region']['wells']:,}".replace(",", " ") + " ta quduq, " + f"{R['region']['obs']:,}".replace(",", " ") + " ta oʻlchov), 3.1-§ dagi tekshiruv."
         + "\nTumanlar boʻyicha yaroqli oʻlchovlar ulushi va yozgi sath orasida ρ = " + "−" + f"{abs(R['rho_valid_level'][0]) + 1e-9:.2f}".replace(".", ",")
         + "; Marhamat tumani qalin chiziq bilan. Chegaralar: geoBoundaries (CC BY 4.0, soddalashtirilgan).",
         fontsize=5.0, color='#555', ha='left', va='bottom')
rep = export(fig, 'figures/fig312_region', provenance={
    'raw_data': ['results/ch3_region.json (script 22)', 'gis/admin/UZB_ADM2.geojson, UZB_ADM1.geojson, KGZ_ADM0.geojson (geoBoundaries)'],
    'transformations': ['district names matched to geoBoundaries ADM2 (Boz = Bo\'ston)', 'classes: valid share {<75,75-85,85-95,>=95}; Sen {<1,1-2,2-4,4-6,>=6} cm/yr', 'p>=0.05 hatched'],
    'note': 'bar chart with truncated axis replaced by choropleth maps'},
    alt_text="""Ikki panelli xarita, Andijon viloyatining 14 ta tumani. a — monitoring maʼlumotlarining yaroqli oʻlchovlar ulushi: shimoli-gʻarbdagi Oltinkoʻl, Boʻston, Shahrixon,
Ulugʻnor, Baliqchi tumanlarida 96–100 foiz, janubi-sharqdagi Asaka, Paxtaobod, Qoʻrgʻontepa, Jalaquduq tumanlarida 71–80 foiz; Marhamat 88,3 foiz. b — barqaror panel boʻyicha
sath tendensiyasi: barcha tumanlarda sath chuqurlashmoqda, eng tez Paxtaobod (+10,6 sm/yil) va Asakada (+6,4), eng sekin Ulugʻnor, Boʻston, Oltinkoʻlda (Boʻston va Oltinkoʻlda
ahamiyatsiz); Marhamat +3,3 sm/yil, yozgi sath 1,95 m.""")
