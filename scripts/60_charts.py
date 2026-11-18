"""Dissertatsiyadagi grafiklarni (xaritalardan tashqari) yagona nashr uslubida qayta chizish (scientific-visualization skill).
Har bir rasm mavjud natija fayllaridan yoki xom ma'lumotdan eski skriptdagi bir xil hisob bilan olinadi; raqamlar o'zgarmaydi.
Ishlatish: python3 scripts/60_charts.py [nom ...]   (nomlar: climate georef audit density dynamics variogram network season hydraulic event massif costs)
Chiqish: figures/<eski nom>.{pdf,png,export.json,alt.txt}"""
import os, sys, re, json
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
import numpy as np, pandas as pd
from scipy.optimize import curve_fit
from matplotlib.ticker import MaxNLocator
from chartkit import plt, OI, SEQ7, MARK7, LS7, MONTHS, LAT, W_FULL, comma, fmt, panel, axes_commas, fig, export
J = lambda f: json.load(open(f'results/{f}.json'))
norm = lambda s: re.sub(r'[\s\.]+', '', str(s)).upper().replace('A', 'А').replace('B', 'Б').replace('ПЕЗ', 'ПЗ')


def climate():
    D = pd.read_csv('results/climate.csv'); x = np.arange(1, 13)
    f, (a, b) = fig(W_FULL, 6.2, ncols=2, gridspec_kw=dict(width_ratios=[1.6, 1]))
    a.bar(x - .2, D.precip, .4, color=OI['blue'], label='Yogʻin')
    a.bar(x + .2, D.et0_mm, .4, color=OI['orange'], hatch='///', edgecolor='white', lw=0, label='Etalon bugʻlanuvchanlik ET₀')
    a.set_xticks(x, MONTHS); a.set_ylabel('mm/oy'); a.legend(loc='upper left'); a.set_ylim(0, None); panel(a, 'a')
    b.plot(x, D.tmean, 'o-', color=OI['verm'], ms=3.5, lw=1.2); b.axhline(0, color='#999', lw=.6)
    b.set_xticks(x, MONTHS, rotation=60); b.set_ylabel('Oʻrtacha harorat, °C'); axes_commas(b); panel(b, 'b')
    export(f, 'figures/ch2_climate', dict(raw_data='results/climate.csv (14-skript: Andijon meteostansiyasi koʻp yillik oylik normalari)',
           transformations=['ET₀ — Hargreaves usuli (14-skript)'], uncertainty='koʻrsatilmagan (koʻp yillik normalar)', missing_data='yoʻq'),
           f'a — Andijon meteostansiyasi boʻyicha oylik yogʻin (koʻk) va etalon bugʻlanuvchanlik (toʻq sariq, chiziqli): yillik yogʻin {D.precip.sum():.0f} mm, ET₀ {D.et0_mm.sum():.0f} mm; '
           f'aprel–sentabrda bugʻlanuvchanlik yogʻindan bir necha baravar katta. b — oʻrtacha oylik harorat, yanvarda {fmt(D.tmean.min(),1)} °C dan iyulda {fmt(D.tmean.max(),1)} °C gacha.')


def georef():
    from pyproj import Transformer
    tr = Transformer.from_crs(4326, 32643, always_xy=True)
    M = pd.read_csv('data/wells_map_2024.csv').dropna(subset=['lon_table'])
    a_ = np.array(tr.transform(M.lon_map.values, M.lat_map.values)).T; b_ = np.array(tr.transform(M.lon_table.values, M.lat_table.values)).T
    r = np.sort(np.linalg.norm(a_ - b_, axis=1)); n = len(r); big = r > 50; sh5 = (r < 5).mean()
    f, (a, b) = fig(W_FULL, 6.0, ncols=2)
    a.hist(r[r <= 10], bins=np.arange(0, 10.5, .5), color=OI['blue'], edgecolor='white', lw=.4)
    a.axvline(5, color=OI['verm'], ls='--', lw=1); a.text(5.2, a.get_ylim()[1] * .9, f'{sh5*100:.0f} % nuqtada\n5 m dan kichik', color=OI['verm'], fontsize=7, va='top')
    a.set_xlabel('Qoldiq, m (10 m gacha)'); a.set_ylabel('Tayanch nuqtalar soni'); axes_commas(a, x=True); panel(a, 'a')
    rk = np.arange(1, n + 1)
    b.semilogy(rk[~big], r[~big], 'o', ms=2.2, color=OI['blue'], label=f'50 m gacha ({(~big).sum()} ta)')
    b.semilogy(rk[big], r[big], 'X', ms=4, color=OI['verm'], label=f'50 m dan katta ({big.sum()} ta)')
    b.axhline(5, color='#999', ls=':', lw=.8); b.text(3, 5.6, '5 m', fontsize=6.5, color='#555')
    b.set_xlabel('Tayanch nuqtalar (qoldiq boʻyicha tartiblangan)'); b.set_ylabel('Qoldiq, m (log shkala)'); b.legend(loc='upper left'); panel(b, 'b')
    b.yaxis.set_major_formatter(comma())
    export(f, 'figures/ch2_georef_residuals', dict(raw_data='data/wells_map_2024.csv (xaritadagi va jadvaldagi koordinatalar)', transformations=['WGS84 → UTM 43N', 'qoldiq = Evklid masofasi'],
           uncertainty='—', missing_data=f'jadval koordinatasi yoʻq quduqlar kiritilmagan; jami {n} ta nuqta'),
           f'Xaritani joyiga bogʻlashdagi {n} ta tayanch nuqtaning qoldiqlari (xaritadagi va jadvaldagi koordinatalar farqi). a — 10 m gacha boʻlgan qoldiqlar taqsimoti: '
           f'{sh5*100:.0f} foiz nuqtada qoldiq 5 m dan kichik. b — barcha qoldiqlar logarifmik shkalada, kattadan kichikka tartiblangan; 50 m dan katta {big.sum()} ta nuqta xoch bilan belgilangan.')
    return n, int(big.sum()), float(sh5)


def audit():
    A = pd.DataFrame(J('ch3_audit_ext')['by_year']); x = np.arange(len(A)); yl = A.year.astype(str)
    f, ax = fig(W_FULL, 9.5, nrows=3, sharex=True, gridspec_kw=dict(height_ratios=[1.1, 1, .8]))
    ax[0].bar(x, A.wells, color=OI['blue']); ax[0].set_ylabel('Kuzatilgan\nquduqlar'); panel(ax[0], 'a')
    for xi, v in zip(x, A.wells): ax[0].text(xi, v + 3, str(v), ha='center', fontsize=6.3)
    ax[0].set_ylim(0, A.wells.max() * 1.18)
    inv = 100 - A.valid_share
    ax[1].bar(x, inv, color=OI['orange'], hatch='///', edgecolor='white', lw=0); ax[1].set_ylabel('Yaroqsiz\noʻlchovlar, %'); axes_commas(ax[1]); panel(ax[1], 'b')
    ax[2].plot(x, A.deep5, 'o-', color=OI['verm'], ms=3); ax[2].set_ylabel('5 m dan chuqur\noʻlchovlar, %'); axes_commas(ax[2]); panel(ax[2], 'c')
    ax[2].set_xticks(x, yl); ax[2].set_ylim(bottom=0)
    for a in ax: a.axvline(5.5, color='#999', ls='--', lw=.7)
    ax[0].text(5.6, A.wells.max() * 1.1, 'tarmoq qayta tuzilgan', fontsize=6.5, color='#555')
    export(f, 'figures/ch3_audit', dict(raw_data='results/ch3_audit_ext.json (16-skript)', transformations=['yillar boʻyicha jamlash; mustaqil maʼlumoti boʻlmagan yillar tahlilga kiritilmagan'],
           uncertainty='—', missing_data='2010, 2013 va 2017-yillar oʻqda yoʻq'),
           f'Yillar boʻyicha: a — kuzatilgan quduqlar soni ({A.wells.min()}–{A.wells.max()} ta; 2018-yilda tarmoq kengaygan); b — yaroqsiz oʻlchovlar ulushi; '
           'c — 5 m dan chuqur oʻlchovlar ulushi, 2018-yildan keyin paydo boʻlgan. Uzuq chiziq — tarmoq tarkibi oʻzgargan yil.')


def density():
    G = J('ch3_geo_ext'); d = pd.DataFrame(G['density']); cv = G['level_2019_2024_m']['cv_mean']
    f, a = fig(W_FULL * .62, 6.5)
    a.errorbar(d.n, d.rmse, yerr=d.rmse_sd, fmt='o-', color=OI['blue'], ms=3.5, capsize=2.5, lw=1.1, label='Kriging xatosi (±1 SD, 40 takror)')
    a.axhline(cv, color=OI['verm'], ls='--', lw=1, label=f'Hududiy oʻrtacha bilan baho ({fmt(cv,2)} m)')
    for _, q in d.iterrows(): a.annotate(f"{int(q.nn_m)} m", (q.n, q.rmse), textcoords='offset points', xytext=(4, 5), fontsize=6.3, color='#444')
    a.set_xlabel('Modelga kiritilgan quduqlar soni'); a.set_ylabel('Nazorat quduqlaridagi xato (RMSE), m'); axes_commas(a, x=True); a.legend(loc='upper right')
    export(f, 'figures/ch3_density', dict(raw_data='results/ch3_geo_ext.json density (18-skript)', transformations=['34 ta nazorat qudugʻi; qolganlardan 25–100 % tanlab olish'],
           uncertainty='±1 SD, har bir zichlik uchun 40 tasodifiy takror', missing_data='—'),
           f'Kuzatuv tarmogʻi zichligining kriging xatosiga taʼsiri: quduqlar soni {int(d.n.min())} tadan {int(d.n.max())} taga oshganda xato {fmt(d.rmse.iloc[0],2)} m dan {fmt(d.rmse.min(),2)} m gacha kamayadi; '
           'taxminan 94 ta quduqdan keyin deyarli oʻzgarmaydi. Nuqtalar yonida — qoʻshni quduqlar orasidagi oʻrtacha masofa.')


def dynamics():
    t = J('ch3')['trend']; s = J('ch3')['season']['profile']
    yrs = np.array(sorted(map(int, t['series']))); ser = np.array([t['series'][str(y)] for y in yrs]); nai = np.array([t['naive_series'][str(y)] for y in yrs])
    f, (a, b) = fig(W_FULL, 6.3, ncols=2)
    a.plot(yrs, nai, 's--', color=OI['grey'], ms=3, lw=1, label='Xom maʼlumot, barcha quduqlar')
    a.plot(yrs, ser, 'o-', color=OI['blue'], ms=3.5, lw=1.3, label=f'Tekshirilgan, barqaror panel ({t["panel_wells"]} ta quduq)')
    a.invert_yaxis(); a.set_xlabel('Yil'); a.set_ylabel('Sizot suvi sathi, m'); a.legend(loc='lower left'); axes_commas(a, ydec=1); panel(a, 'a')
    a.set_xticks([2009, 2012, 2015, 2018, 2021, 2024]); a.xaxis.set_major_formatter(lambda v, _: f'{int(v)}')
    dd = np.array(sorted(map(int, s))); pv = np.array([s[str(k)] for k in dd])
    b.plot(dd, pv, 'o-', color=OI['blue'], ms=2.5, lw=1.2); b.invert_yaxis()
    b.set_xticks(range(2, 37, 3), MONTHS); b.set_ylabel('Sizot suvi sathi, m'); b.set_xlabel('Oʻn kunlik'); axes_commas(b, ydec=1); panel(b, 'b')
    b.axvspan(19, 24, color=OI['orange'], alpha=.15, lw=0); b.text(21.5, .03, 'iyul–avgust', ha='center', va='bottom', fontsize=6.5, color='#7a4a00', transform=b.get_xaxis_transform())
    export(f, 'figures/ch3_dynamics', dict(raw_data='results/ch3.json trend, season (10-skript)', transformations=['yillik oʻrtacha', 'oʻzgarmas qatorlar chiqarilgan', 'barqaror panel'],
           uncertainty='koʻrsatilmagan; tendensiya bahosi va oraligʻi matnda', missing_data='mustaqil maʼlumoti boʻlmagan yillar (2010, 2013, 2017) oʻqda yoʻq'),
           f'a — sizot suvi sathining yillik oʻrtachasi: tekshirilgan barqaror panel {fmt(ser[0],2)} m dan {fmt(ser[-1],2)} m gacha chuqurlashgan; xom maʼlumot sathni 0,3–0,5 m chuqur va tendensiyani tezroq koʻrsatadi. '
           f'b — yil ichidagi oʻrtacha yoʻl oʻn kunliklar boʻyicha: yanvar–fevralda eng chuqur, iyulda eng sayoz; amplituda {fmt(J("ch3")["season"]["amplitude"],2)} m.')


def variogram():
    W = pd.read_csv('data/wells_metrics.csv').dropna(subset=['level_2019_2024_m']); x, y, v = W.x_utm43.values, W.y_utm43.values, W.level_2019_2024_m.values
    VG = {'exponential': lambda h, ps, r, n: n + ps * (1 - np.exp(-h / r)), 'spherical': lambda h, ps, r, n: n + ps * np.where(h < r, 1.5 * h / r - .5 * (h / r) ** 3, 1.0)}
    dx, dy = x[:, None] - x[None], y[:, None] - y[None]; h = np.hypot(dx, dy); g = .5 * (v[:, None] - v[None]) ** 2
    ang = (np.degrees(np.arctan2(dx, dy)) + 180) % 180; iu = np.triu_indices(len(v), 1); h, g, ang = h[iu], g[iu], ang[iu]
    def fitv(model):
        lg = np.arange(0, 10001, 500); mid, gam, npr = [], [], []
        for k in range(len(lg) - 1):
            m = (h > lg[k]) & (h <= lg[k + 1])
            if m.sum() >= 20: mid.append(h[m].mean()); gam.append(g[m].mean()); npr.append(m.sum())
        mid, gam, npr = map(np.array, (mid, gam, npr)); pr = {'exponential': 3000, 'spherical': 8000}[model]
        return curve_fit(VG[model], mid, gam, p0=[gam.max() - gam.min(), pr, gam.min()], sigma=gam / np.sqrt(npr), bounds=([.01, 300, 0], [5, 30000, 2]), maxfev=20000)[0]
    lags = np.arange(0, 8001, 500); mid = (lags[:-1] + lags[1:]) / 2
    omni = [g[(h > lags[k]) & (h <= lags[k + 1])].mean() for k in range(len(lags) - 1)]
    f, (a, b) = fig(W_FULL, 6.5, ncols=2, sharey=True)
    hh = np.linspace(0, 8000, 300)
    a.plot(mid / 1000, omni, 'o', color=OI['black'], ms=3.5, label='Empirik (barcha yoʻnalishlar)')
    a.plot(hh / 1000, VG['exponential'](hh, *fitv('exponential')), '-', color=OI['blue'], lw=1.3, label='Eksponensial model')
    a.plot(hh / 1000, VG['spherical'](hh, *fitv('spherical')), '--', color=OI['orange'], lw=1.3, label='Sferik model')
    a.axhline(v.var(), color=OI['grey'], ls=':', lw=1, label='Maʼlumotlar dispersiyasi')
    a.set_xlabel('Masofa, km'); a.set_ylabel('Yarimvariogramma, m²'); a.legend(loc='lower right'); axes_commas(a, x=True); panel(a, 'a')
    names = [('Sh–J (0°)', 0), ('ShSh–JGʻ (45°)', 45), ('Gʻ–Sh (90°)', 90), ('ShGʻ–JSh (135°)', 135)]
    for i, (nm, a0) in enumerate(names):
        da = np.minimum(np.abs(ang - a0), 180 - np.abs(ang - a0)); m = da <= 22.5
        vv = [g[m & (h > lags[k]) & (h <= lags[k + 1])].mean() for k in range(len(lags) - 1)]
        b.plot(mid / 1000, vv, marker=MARK7[i], ls=LS7[i], color=SEQ7[i], ms=3, lw=1, label=nm)
    b.set_xlabel('Masofa, km'); b.legend(loc='upper left', ncol=2); axes_commas(b, x=True); b.tick_params(labelleft=True); panel(b, 'b')
    export(f, 'figures/ch3_variogram', dict(raw_data='data/wells_metrics.csv level_2019_2024_m (168 quduq)', transformations=['0,5 km qadamli lag sinflari', 'model: vaznli eng kichik kvadratlar (18-skript bilan bir xil)', 'yoʻnalishlar ±22,5°'],
           uncertainty='—', missing_data='—'),
           'a — 2019–2024-yillardagi oʻrtacha sath boʻyicha empirik yarimvariogramma, eksponensial va sferik modellar; nagget umumiy dispersiyaning qariyb yarmiga teng. '
           'b — toʻrt yoʻnalish boʻyicha yarimvariogrammalar: 5 km gacha yoʻnalishlar orasida tizimli farq yoʻq, yaʼni anizotropiya kuchsiz.')


def network():
    W = pd.read_csv('data/wells_metrics.csv').dropna(subset=['level_2019_2024_m']); N = J('ch3_net_ext'); bp = N['segmented']['bp']
    X = np.c_[np.ones(len(W)), np.minimum(W.dist_collector_m, bp), np.maximum(W.dist_collector_m - bp, 0)]; b0 = np.linalg.lstsq(X, W.level_2019_2024_m.values, rcond=None)[0]
    f, ax = fig(W_FULL, 6.3, ncols=3, gridspec_kw=dict(width_ratios=[1.3, 1, 1]))
    a = ax[0]; a.scatter(W.dist_collector_m, W.level_2019_2024_m, s=6, color=OI['blue'], alpha=.65, lw=0)
    xs = np.linspace(0, W.dist_collector_m.max(), 300); a.plot(xs, b0[0] + b0[1] * np.minimum(xs, bp) + b0[2] * np.maximum(xs - bp, 0), '-', color=OI['verm'], lw=1.4)
    a.axvline(bp, color=OI['verm'], ls=':', lw=.9); a.text(bp + 60, W.level_2019_2024_m.max() * .97, f'{bp} m', color=OI['verm'], fontsize=6.5)
    a.invert_yaxis(); a.set_xlabel('Kollektorgacha masofa, m'); a.set_ylabel('Sath, 2019–2024-yillar oʻrtachasi, m'); axes_commas(a); a.xaxis.set_major_formatter(lambda v, _: f'{v:.0f}'); panel(a, 'a')
    sb = pd.DataFrame(N['season_by_dist']); lab = ['0–150', '150–400', '400–800', '>800']; xi = np.arange(4)
    b = ax[1]; b.bar(xi - .2, sb.winter, .4, color=OI['sky'], label='Yanvar–fevral'); b.bar(xi + .2, sb.summer, .4, color=OI['blue'], hatch='///', edgecolor='white', lw=0, label='Iyul–avgust')
    b.set_xticks(xi, lab, rotation=30, ha='right'); b.set_ylim(sb.winter.max() * 1.25, 0); b.set_xlabel('Kollektorgacha masofa, m'); b.set_ylabel('Sath, m'); axes_commas(b); b.legend(loc='lower left'); panel(b, 'b')
    for i, (w_, am) in enumerate(zip(sb.winter, sb.amp)): b.text(i, w_ + .12, 'A = ' + fmt(am, 2), ha='center', va='top', fontsize=6)
    tb = pd.DataFrame(N['trend_by_dist']); c = ax[2]; c.bar(xi, tb.sen_med * 100, color=OI['orange'])
    for i, (v_, n_) in enumerate(zip(tb.sen_med * 100, tb.n)): c.text(i, v_ + .1, f'{fmt(v_,1)}\nn = {n_}', ha='center', va='bottom', fontsize=6)
    c.set_xticks(xi, lab, rotation=30, ha='right'); c.set_ylim(0, (tb.sen_med * 100).max() * 1.35); c.set_xlabel('Kollektorgacha masofa, m'); c.set_ylabel('Sen qiyaligi medianasi, sm/yil'); axes_commas(c); panel(c, 'c')
    export(f, 'figures/ch3_network', dict(raw_data='data/wells_metrics.csv; results/ch3_net_ext.json (19-skript)', transformations=[f'boʻlinma regressiya, uzilish {bp} m', 'masofa sinflari 0–150–400–800 m'],
           uncertainty='CI matnda va ilovada (blokli bootstrap)', missing_data='—'),
           f'a — 168 ta quduqda sath va kollektorgacha masofa; qizil chiziq — boʻlinma regressiya, uzilish {bp} m. b — masofa sinflari boʻyicha qishki va yozgi sath (A — mavsumiy koʻtarilish). '
           'c — sath tendensiyasining Sen qiyaligi medianasi: kollektordan 800 m dan uzoqda chuqurlashish eng tez.')


def season():
    EX = {2010, 2013, 2017}
    L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin(EX)].copy(); L['well'] = L.well_no.map(norm); L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
    g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index(); cst = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
    L = L.merge(cst, on=['year', 'well'], how='left'); L = L[L.c.isna()]
    M = pd.read_csv('data/wells_metrics.csv'); M['well'] = M.well_no.map(norm); L['massif'] = L.well.map(dict(zip(M.well, M.massif_map)))
    yrs = sorted(L.year.unique()); ann = L.groupby(['well', 'year'])['level'].mean().unstack()
    panel_w = [w for w in ann.index if ann.loc[w, yrs].notna().all() and w not in set(cst.well)]
    S = L[L.well.isin(panel_w)].groupby(['massif', 'decade'])['level'].mean().unstack()
    nw = L[L.well.isin(panel_w)].groupby('massif').well.nunique()
    f, a = fig(W_FULL, 7.5)
    for i, (m, r) in enumerate(S.iterrows()):
        a.plot(r.index, r.values, ls=LS7[i], marker=MARK7[i], markevery=3, ms=3, lw=1.1, color=SEQ7[i], label=f'{LAT.get(m, m)} ({nw[m]})')
    a.invert_yaxis(); a.set_xticks(range(2, 37, 3), MONTHS); a.set_ylabel('Sizot suvi sathi, m'); a.set_xlabel('Oʻn kunlik'); axes_commas(a, ydec=1)
    a.legend(ncol=4, loc='lower center', title='Massiv (panel quduqlari soni)', title_fontsize=7)
    export(f, 'figures/ch3_season_massif', dict(raw_data='data/gw_levels_long.csv (17-skript bilan bir xil tozalash)', transformations=['oʻzgarmas qatorlar chiqarilgan', 'barqaror panel', 'massiv va oʻn kunlik boʻyicha oʻrtacha'],
           uncertainty='—', missing_data='Y.Oxunboboyev massivida panel qudugʻi yoʻq'),
           'Sizot suvi sathining yil ichidagi yoʻli massivlar boʻyicha (barqaror panel quduqlari). Barcha massivlarda sath yanvar–martda eng chuqur, may–avgustda eng sayoz; '
           'amplituda T.Mirzayevda eng kichik, U.Qoraboyevda eng katta. Chiziqlar rang, chiziq turi va marker bilan farqlanadi.')


def hydraulic():
    Hj = J('ch4_hydraulic'); mo = Hj['monthly']; m = np.arange(1, 13)
    ETc = np.array([mo[str(k)]['etc'] for k in m]); Pe = np.array([mo[str(k)]['pe'] for k in m]); NIR = np.array([mo[str(k)]['nir'] for k in m])
    H = pd.read_csv('results/ch4_drainage_modulus.csv'); sc = Hj['scenarios']; dr = Hj['design_range']
    f, (a, b) = fig(W_FULL, 8.0, ncols=2)
    a.bar(m - .2, ETc, .4, color=OI['blue'], label='Ekinlar bugʻlanishi ETc'); a.bar(m + .2, Pe, .4, color=OI['sky'], hatch='...', edgecolor='white', lw=0, label='Samarali yogʻin')
    a.plot(m, NIR, 'o-', color=OI['black'], ms=3, lw=1.1, label='Sof sugʻorish talabi'); a.set_xticks(m, MONTHS, rotation=60); a.set_ylabel('mm/oy'); a.set_ylim(0, max(ETc.max(), NIR.max()) * 1.5); a.legend(loc='upper left'); panel(a, 'a')
    bins = np.linspace(np.log10(H.modul.min()), np.log10(H.modul.max()), 21)
    b.hist(np.log10(H.modul), bins=bins, color='#c8c8c8', edgecolor='#666', lw=.5, label=f'Kadastr: kollektorlar ({len(H)} ta)')
    b.axvspan(np.log10(dr[0]), np.log10(dr[1]), color=OI['blue'], alpha=.1, lw=0, label='Loyihaviy oraliq 1–3 mm/sut')
    nm = {'yuqori': 'yuqori', 'oʻrta': 'oʻrta', "o'rta": 'oʻrta', 'past': 'past'}
    for i, s_ in enumerate(sc):
        b.axvline(np.log10(s_['q_july']), color=[OI['green'], OI['orange'], OI['verm']][i], ls=['-', '--', '-.'][i], lw=1.4,
                  label=f"Talab, iyul ({nm.get(s_['name'], s_['name'])} samaradorlik): {fmt(s_['q_july'],2)}")
    tk = [0.03, 0.1, 0.3, 1, 3, 10, 30]; b.set_xticks(np.log10(tk), [fmt(t, 2 if t < .1 else (1 if t < 1 else 0)) for t in tk])
    b.set_xlabel('Solishtirma sarf, l/(s·ga), log shkala'); b.set_ylabel('Kollektorlar soni'); b.legend(loc='upper center', bbox_to_anchor=(.45, -.2), fontsize=6.2, ncol=1); panel(b, 'b')
    export(f, 'figures/ch4_hydraulic', dict(raw_data='results/ch4_hydraulic.json; results/ch4_drainage_modulus.csv (24-skript)', transformations=['FAO-56 ekin koeffitsiyentlari', 'solishtirma sarf = oxirgi sarf / xizmat maydoni', 'log10 shkala'],
           uncertainty='stsenariylar (sugʻorish samaradorligi) boʻyicha oraliq', missing_data='—'),
           'a — oylik ekinlar bugʻlanishi, samarali yogʻin va sof sugʻorish talabi; talab may–avgustda eng katta. '
           f'b — kadastrdagi {len(H)} ta kollektorning solishtirma sarfi (log shkala) va uch stsenariy boʻyicha iyuldagi talab etiladigan drenaj moduli; chiziqlar rang va chiziq turi bilan farqlanadi.')


def event():
    E = pd.DataFrame(J('ch4_repair_ext')['event']).sort_values('e'); pre = J('ch4_repair_ext')['pretrend_F']
    f, a = fig(W_FULL * .65, 6.3)
    a.axhline(0, color='#888', lw=.8); a.axvline(-.5, color='#888', ls=':', lw=.8)
    ref = E.e == -1
    a.errorbar(E.e[~ref], E.b[~ref], yerr=[E.b[~ref] - E.lo[~ref], E.hi[~ref] - E.b[~ref]], fmt='o', color=OI['blue'], ms=4, capsize=2.5, lw=1.1, label='Baho va 95 % ishonch oraligʻi')
    a.plot(E.e[ref], E.b[ref], 'o', mfc='white', mec=OI['blue'], ms=4, label='Asos yil (−1)')
    a.set_xticks(range(-4, 5), ['≤−4', '−3', '−2', '−1', '0', '1', '2', '3', '≥4']); axes_commas(a, ydec=1)
    a.set_xlabel('Taʼmir yilidan beri oʻtgan yillar'); a.set_ylabel('Nazoratga nisbatan sath farqi, m\n(musbat — chuqurlashish)'); a.legend(loc='lower left')
    a.text(-4.3, a.get_ylim()[1] * .9, f'taʼmirdan oldin: F = {fmt(pre["F"],2)}; p = {fmt(pre["p"],2)}', fontsize=6.5, color='#444')
    export(f, 'figures/ch4_event_study', dict(raw_data='data/repair_panel.csv; results/ch4_repair_ext.json (25-skript)', transformations=['quduq va yil qatʼiy effektlari', 'asos: taʼmirdan bir yil oldin'],
           uncertainty='95 % ishonch oraligʻi, quduqlar boʻyicha klasterlangan standart xato', missing_data='mustaqil maʼlumoti boʻlmagan yillar chiqarilgan'),
           'Kollektor taʼmirining sizot sathiga dinamik taʼsiri: taʼmir yiliga nisbatan har bir yil uchun nazorat quduqlariga nisbatan sath farqi va 95 % ishonch oraligʻi. '
           'Taʼmirdan oldingi koeffitsiyentlar nolga yaqin; keyingi yillarda ham chuqurlashish kuzatilmaydi, faqat 4 va undan koʻp yildan keyin baho −0,25 m.')


def massif():
    M = pd.DataFrame(J('ch4_rel_ext')['massif']).set_index('massif'); M = M.loc[[k for k in LAT if k in M.index]]; xi = np.arange(len(M)); nm = [LAT[k] for k in M.index]
    f, (a, b) = fig(W_FULL, 7.0, ncols=2)
    a.bar(xi - .2, M.coll_m_ha, .4, color=OI['blue'], label='Kollektorlar'); a.bar(xi + .2, M.inner_m_ha, .4, color=OI['sky'], hatch='///', edgecolor='white', lw=0, label='Ichki zovurlar')
    a.set_xticks(xi, nm, rotation=35, ha='right'); a.set_ylabel('Solishtirma uzunlik, m/ga'); a.legend(loc='upper right'); panel(a, 'a')
    v = M.inner_norep * 100; hi = v >= 70
    b.bar(xi[hi.values], v[hi], color=OI['verm'], hatch='xx', edgecolor='white', lw=0, label='70 % dan yuqori')
    b.bar(xi[~hi.values & v.notna().values], v[~hi & v.notna()], color=OI['blue'], label='70 % gacha')
    for i, q in enumerate(v):
        b.text(i, (0 if np.isnan(q) else q) + 1.5, 'zovur\nyoʻq' if np.isnan(q) else f'{q:.0f}', ha='center', va='bottom', fontsize=6)
    b.set_xticks(xi, nm, rotation=35, ha='right'); b.set_ylim(0, 112); b.set_ylabel('Taʼmir qayd etilmagan ichki zovurlar,\nuzunlikdan %'); b.legend(loc='upper right', bbox_to_anchor=(1, .97)); panel(b, 'b')
    export(f, 'figures/ch4_massif_reliability', dict(raw_data='results/ch4_rel_ext.json massif (23-skript)', transformations=['uzunlik / sugʻoriladigan maydon', '70 % chegarasi — T-14 tavsiyasi'],
           uncertainty='—', missing_data='M.Toʻjiboyev massivida ichki zovurlar qatlami yoʻq'),
           'Massivlar boʻyicha: a — kollektorlar va xoʻjalik ichki zovurlarining solishtirma uzunligi; b — taʼmiri qayd etilmagan ichki zovurlar ulushi, 70 foizdan yuqori boʻlgan beshta massiv toʻq sariq va xoch bilan belgilangan.')


def costs():
    C = pd.read_csv('data/collectors.csv'); K = pd.read_csv('results/ch4_repair_costs.csv')
    KF = {int(k): v for k, v in J('cost_2026')['index']['factors'].items()}; c26 = (K.cost_km * K.repair_year.map(KF)).dropna()
    f, ax = fig(W_FULL, 6.3, ncols=3)
    b_ = C.groupby((C.commissioned // 10) * 10).length_km.sum(); ax[0].bar(b_.index.astype(int).astype(str), b_.values, color=OI['blue'])
    ax[0].set_xlabel('Foydalanishga topshirilgan oʻn yillik'); ax[0].set_ylabel('Kollektorlar uzunligi, km'); ax[0].tick_params(axis='x', rotation=45); panel(ax[0], 'a')
    r = C.groupby('repair_year').length_km.sum(); ax[1].bar(r.index.astype(int).astype(str), r.values, color=OI['green'])
    ax[1].set_xlabel('Oxirgi taʼmir yili'); ax[1].set_ylabel('Uzunlik, km'); ax[1].tick_params(axis='x', rotation=45); panel(ax[1], 'b')
    bins = np.logspace(np.log10(c26.min()), np.log10(c26.max()), 14); ax[2].hist(c26, bins=bins, color=OI['orange'], edgecolor='white', lw=.4); ax[2].set_xscale('log')
    ax[2].axvline(c26.median(), color=OI['black'], ls='--', lw=1); ax[2].set_ylim(0, ax[2].get_ylim()[1] * 1.25); ax[2].text(c26.median() * 1.12, ax[2].get_ylim()[1] * .97, f'mediana {c26.median():.0f}', fontsize=6.3, va='top')
    ax[2].set_xlabel('Taʼmir narxi, mln soʻm/km\n(2026-yil narxlarida, log shkala)'); ax[2].set_ylabel('Kollektorlar soni'); ax[2].xaxis.set_major_formatter(comma()); ax[2].yaxis.set_major_locator(MaxNLocator(integer=True)); panel(ax[2], 'c')
    export(f, 'figures/ch4_reliability_costs', dict(raw_data='data/collectors.csv; results/ch4_repair_costs.csv; results/cost_2026.json (37-skript)', transformations=['oʻn yillik va yillar boʻyicha uzunlik yigʻindisi', '2026-yil narxlariga isteʼmol narxlari indeksi bilan keltirish'],
           uncertainty='—', missing_data='narxi koʻrsatilmagan kollektorlar c panelga kiritilmagan'),
           f'a — kollektorlar uzunligining foydalanishga topshirilgan oʻn yillik boʻyicha taqsimoti (asosan 1940–1960-yillar); b — oxirgi taʼmir yili boʻyicha (2016–2019-yillarda choʻqqi); '
           f'c — 1 km taʼmir narxi 2026-yil narxlarida ({len(c26)} ta kollektor, mediana {c26.median():.0f} mln soʻm/km); yengil tozalash va kapital taʼmir ikki guruhni hosil qiladi.')


ALL = dict(climate=climate, georef=georef, audit=audit, density=density, dynamics=dynamics, variogram=variogram, network=network, season=season,
           hydraulic=hydraulic, event=event, massif=massif, costs=costs)
if __name__ == '__main__':
    for k in (sys.argv[1:] or ALL):
        out = ALL[k](); print(k, 'ok', out if out else '')
