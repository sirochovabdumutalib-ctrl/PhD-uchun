"""Yozgi (iyul–avgust) sathning yagona ta'rifi (taqriz, kichik mulohaza m1): 2019–2024-yillar, 19–24-dekadalar (dekada raqami bo'yicha),
3.1-§ qoidasi bilan yaroqsiz quduq-yillar (7 tadan ortiq bir xil qiymat) chiqariladi; avval yil ichida, keyin yillar bo'yicha o'rtacha.
Faqat data/wells_metrics.csv dagi level_summer_m ustuni yangilanadi; boshqa ustunlarga tegilmaydi."""
import os, sys, numpy as np, pandas as pd
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, 'scripts')
from carto import nkey

def summer_levels():
    L = pd.read_csv('data/gw_levels_long.csv'); L = L[~L.year.isin({2010, 2013, 2017})].copy(); L['well'] = L.well_no.map(nkey)
    L['level'] = np.where(L.level_m > 20, L.level_m / 100, L.level_m)
    g = L.groupby(['year', 'well'])['level'].agg(['nunique', 'count']).reset_index()
    bad = g[(g['nunique'] == 1) & (g['count'] > 6)][['year', 'well']].assign(c=1)
    L = L.merge(bad, on=['year', 'well'], how='left'); L = L[L.c.isna() & (L.year >= 2019) & L.decade.between(19, 24)]
    return L.groupby(['well', 'year'])['level'].mean().groupby('well').mean()

if __name__ == '__main__':
    W = pd.read_csv('data/wells_metrics.csv'); old = W.level_summer_m.copy()
    W['level_summer_m'] = W.well_no.map(nkey).map(summer_levels()).round(3)
    W.to_csv('data/wells_metrics.csv', index=False)
    d = (W.level_summer_m - old).abs()
    print('n', int(W.level_summer_m.notna().sum()), '(oldin', int(old.notna().sum()), ') | <1,5 m:', int((W.level_summer_m < 1.5).sum()), '(oldin', int((old < 1.5).sum()), ')',
          '| o‘zgargan >0,05 m:', int((d > .05).sum()), 'max', round(float(d.max()), 3))
