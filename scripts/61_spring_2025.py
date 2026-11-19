"""2025-yil mart va aprel oylaridagi kuzatuv quduqlari o'lchovlarini o'qish (meliorativ ekspeditsiya, «2025 йил март/апрел холатига»).
Natija: data/gw_2025_spring.csv (well_no, massif, month, d1, d2, d3, mean, prev_col). Jami qatorlari («Массив буйича», «Туман буйича») olinmaydi."""
import sys, re, openpyxl, pandas as pd
MAS = {'З.М.Бобур':'З.М.Бобур','У.Корабоев':'У.Қорабоев','Истиклол':'Истиқлол','М.Тожибоев':'М.Тожибоев','Пахтакор':'Пахтакор',
       'Машъал':'Машъал','Т.Мирзаев':'Т.Мирзаев','Й Охунбобоев':'Й.Охунбобоев'}
rows = []
for path, month in [(sys.argv[1], 3), (sys.argv[2], 4)]:
    ws = openpyxl.load_workbook(path, data_only=True).active
    cur = 'З.М.Бобур'  # birinchi blok nomi 13-qatorda yozilgan
    for r in ws.iter_rows(min_row=6, values_only=True):
        name = str(r[1]).strip() if r[1] else ''
        if name in MAS: cur = MAS[name]
        if name.startswith('Массив') or name.startswith('Туман') or name.startswith('Кудук') or name == 'майдон': continue
        if r[0] is None or r[3] is None or cur is None: continue
        rows.append(dict(well_no=str(r[3]).strip(), massif=cur, month=month, area_ha=r[2], d1=r[4], d2=r[5], d3=r[6], prev_col=r[8]))
df = pd.DataFrame(rows)
for c in ['d1','d2','d3','prev_col','area_ha']: df[c] = pd.to_numeric(df[c].astype(str).str.replace(',', '.').str.strip(), errors='coerce')
df['mean'] = df[['d1','d2','d3']].mean(axis=1)
df.to_csv('data/gw_2025_spring.csv', index=False)
print(df.groupby('month').well_no.nunique().to_dict(), df.groupby(['month','massif']).size().unstack(0).to_dict())

# --- 2025-yil bahorini 2009–2024-yillarning shu oylari (mart–aprel, 7–12-dekadalar) bilan solishtirish ---
import numpy as np, json
g = pd.read_csv('data/gw_levels_long.csv', dtype={'well_no': str}); g = g[g.decade.between(7, 12) & ~g.year.isin([2010, 2013, 2017])]  # mustaqil kuzatuv ma'lumotlari mavjud bo'lmagan yillar (3.1-§)
l = df.melt(id_vars=['well_no', 'month'], value_vars=['d1', 'd2', 'd3'], var_name='d', value_name='level_m')
l['decade'] = (l.month - 1) * 3 + l.d.str[1].astype(int); l['year'] = 2025
a = pd.concat([g[['year', 'well_no', 'decade', 'level_m']], l[['year', 'well_no', 'decade', 'level_m']]])
a = a.merge(df[df.month == 4][['well_no', 'massif']], on='well_no')
def q(x):
    v = x.level_m.dropna(); v = v[v > 0]
    return pd.Series(dict(n=len(v), const=bool(len(v) >= 5 and v.nunique() == 1), mean=v.mean() if len(v) else np.nan))
w = a.groupby(['year', 'well_no', 'massif']).apply(q, include_groups=False).reset_index()
yr = w[w.n > 0].groupby('year').agg(wells=('n', 'size'), const_share=('const', 'mean'))
v = w[(~w.const) & w['mean'].notna()]
cnt = v.groupby('well_no').year.nunique(); pan = cnt[cnt >= 10].index
p = v[v.well_no.isin(pan)]
lev = p.groupby('year')['mean'].agg(['size', 'mean', 'median'])
mas = p.pivot_table(index='massif', columns='year', values='mean', aggfunc='median')
sh = v[v.year.isin([2023, 2024, 2025])].groupby(['massif', 'year'])['mean'].apply(lambda s: (s < 2).mean() * 100).unstack()
out = dict(wells_2025=int(df.well_no.nunique()), const_share=yr.const_share.round(3).to_dict(), n_wells=yr.wells.to_dict(),
           panel_wells=int(len(pan)), spring_level=lev.round(2).to_dict('index'), massif_median=mas.round(2).to_dict('index'),
           share_lt2_valid=sh.round(1).to_dict('index'))
json.dump(out, open('results/spring_2025.json', 'w'), ensure_ascii=False, indent=1, default=float)
print(yr.T.round(3)); print(lev.round(2).T); print(mas.round(2)); print(sh.round(1))
