"""2.1-§ uchun iqlim jadvali: Andijon meteostansiyasi 1961-1990 me'yorlari (Meteo-TV) va Hargreaves-Samani
usulida etalon bug'lanuvchanlik (FAO-56, 52-tenglama). Chiqish: results/climate.csv, figures/ch2_climate.png"""
import numpy as np, pandas as pd, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
TMAX = [2, 5, 12, 21, 27, 32, 33, 31, 27, 19, 11, 4]
TMIN = [-7, -5, 2, 9, 14, 17, 19, 16, 11, 6, 0, -4]
P = [29, 36, 45, 46, 38, 17, 12, 6, 7, 32, 27, 28]
LAT = np.radians(40.53); DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]; MID = [15, 46, 74, 105, 135, 166, 196, 227, 258, 288, 319, 349]
rows = []
for m in range(12):
    J = MID[m]; dr = 1 + 0.033 * np.cos(2 * np.pi * J / 365); d = 0.409 * np.sin(2 * np.pi * J / 365 - 1.39)
    ws = np.arccos(-np.tan(LAT) * np.tan(d)); Ra = 24 * 60 / np.pi * 0.082 * dr * (ws * np.sin(LAT) * np.sin(d) + np.cos(LAT) * np.cos(d) * np.sin(ws))
    tm = (TMAX[m] + TMIN[m]) / 2; et0 = 0.0023 * (tm + 17.8) * np.sqrt(TMAX[m] - TMIN[m]) * 0.408 * Ra
    rows.append(dict(month=m + 1, tmax=TMAX[m], tmin=TMIN[m], tmean=tm, precip=P[m], Ra_MJ=round(Ra, 1), et0_mm_day=round(et0, 2), et0_mm=round(et0 * DAYS[m]), deficit=round(et0 * DAYS[m] - P[m])))
D = pd.DataFrame(rows); D.to_csv('results/climate.csv', index=False)
print(D.to_string(index=False)); print('year: tmean', round(D.tmean.mean(), 1), 'P', D.precip.sum(), 'ET0', D.et0_mm.sum(), 'deficit', D.deficit.sum(), 'P/ET0', round(D.precip.sum() / D.et0_mm.sum(), 3),
      'Apr-Sep ET0', D.et0_mm[3:9].sum(), 'Apr-Sep P', D.precip[3:9].sum())
G = pd.read_csv('data/gw_levels_long.csv'); G = G[~G.year.isin([2010, 2013, 2017])]; G['m'] = (G.decade - 1) // 3 + 1; G['level'] = np.where(G.level_m > 20, G.level_m / 100, G.level_m)
gm = G.groupby('m')['level'].mean()
fig, ax = plt.subplots(figsize=(9, 4)); x = np.arange(1, 13); lab = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']
ax.bar(x - 0.2, D.precip, 0.4, color='#4a90d9', label="Yog'in, mm"); ax.bar(x + 0.2, D.et0_mm, 0.4, color='#e0a040', label="Bug'lanuvchanlik (ET0), mm")
ax.set_ylabel('mm'); ax.set_xticks(x); ax.set_xticklabels(lab); ax2 = ax.twinx(); ax2.plot(x, D.tmean, 'o-', color='#c0392b', label="O'rtacha harorat, °C"); ax2.set_ylabel('°C')
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels(); ax.legend(h1 + h2, l1 + l2, fontsize=8, loc='upper left'); ax.grid(alpha=.3); fig.tight_layout(); fig.savefig('figures/ch2_climate.png', dpi=150)
print('gw monthly', gm.round(2).to_dict())
