"""Andijon viloyati tumanlari bo'yicha 2009-2023 kuzatuv quduqlari (o'n kunlik sath) jadvalini uzun formatga o'tkazish.
Kirish: viloyat xls fayli (argument). Chiqish: data/region_levels_long.csv (year, district, well_no, decade, level_m)"""
import sys, re, numpy as np, pandas as pd, warnings
warnings.filterwarnings('ignore')
src = sys.argv[1]; X = pd.read_excel(src, sheet_name=None, header=None); rows = []
NAMES = {'андижон': 'Andijon', 'асака': 'Asaka', 'баликчи': 'Baliqchi', 'бустон': "Bo'ston", 'жалакудук': 'Jalaquduq', 'жалақудуқ': 'Jalaquduq', 'избоскан': 'Izboskan', 'улугнор': "Ulug'nor",
         'мархамат': 'Marhamat', 'марҳамат': 'Marhamat', 'олтинкул': "Oltinko'l", 'пахтаобод': 'Paxtaobod', 'худжаобод': "Xo'jaobod", 'хужаобод': "Xo'jaobod", 'шахрихон': 'Shahrixon',
         'кургонтепа': "Qo'rg'ontepa", 'қўрғонтепа': "Qo'rg'ontepa", 'булокбоши': "Buloqboshi", 'булоқбоши': "Buloqboshi"}
def dname(s):
    s = str(s).strip().lower().replace('тумани', '').strip()
    for k, v in NAMES.items():
        if s.startswith(k[:6]): return v
    return None
for sh, d in X.items():
    year = int(sh); cur = None
    for _, r in d.iterrows():
        c0, c1 = r.iloc[0], r.iloc[1]; vals = pd.to_numeric(r.iloc[2:38], errors='coerce').values
        if isinstance(c0, str) and pd.isna(c1) and np.isnan(vals).all():
            n = dname(c0)
            if n: cur = n
            continue
        if cur is None or pd.isna(c1): continue
        for k, v in enumerate(vals):
            if not np.isnan(v): rows.append((year, cur, str(c1).strip(), k + 1, float(v)))
L = pd.DataFrame(rows, columns=['year', 'district', 'well_no', 'decade', 'level_m'])
L.to_csv('data/region_levels_long.csv', index=False)
print(L.groupby(['district']).agg(years=('year', 'nunique'), wells=('well_no', 'nunique'), obs=('level_m', 'size')))
print(L.groupby('year').district.nunique().to_dict())
