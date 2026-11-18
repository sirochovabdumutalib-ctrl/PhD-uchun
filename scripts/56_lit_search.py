"""Adabiyotlar qidiruvi (literature-review, 5-band): Crossref, 2020–2026, jurnal maqolalari.
Har bir so'rov, sana va natijalar sources/lit_search_<kod>.json ga yoziladi; birlashtirilgan, takrorsiz ro'yxat sources/lit_candidates.json"""
import json, time, datetime, requests, re
S = requests.Session(); S.headers['User-Agent'] = 'thesis-literature-search/1.0'
Q = {
 'A_gw_uz':   'groundwater table depth irrigated Uzbekistan',
 'B_fergana': 'Fergana Valley groundwater salinity irrigation',
 'C_drain':   'collector drainage network Central Asia performance',
 'D_krig':    'kriging groundwater level depth interpolation irrigated',
 'E_monit':   'groundwater monitoring network design optimization wells',
 'F_rehab':   'drainage rehabilitation impact evaluation irrigation',
 'G_rs_sal':  'remote sensing soil salinity Uzbekistan',
 'H_gis_rec': 'GIS land reclamation assessment irrigated lands Uzbekistan',
 'I_trend':   'groundwater level trend Mann-Kendall irrigated',
 'J_aral':    'Amu Darya Syr Darya irrigation drainage water salt balance',
}
allr = {}
for k, q in Q.items():
    r = S.get('https://api.crossref.org/works', params={'query.bibliographic': q, 'filter': 'from-pub-date:2020-01-01,until-pub-date:2026-12-31,type:journal-article', 'rows': 40,
        'select': 'DOI,title,container-title,issued,author,abstract,is-referenced-by-count,volume,issue,page,article-number'}, timeout=60)
    items = r.json()['message']['items']
    json.dump(dict(query=q, source='Crossref', date=str(datetime.date.today()), filter='2020–2026, journal-article', n=len(items), items=items), open(f'sources/lit_search_{k}.json', 'w'), ensure_ascii=False, indent=1)
    for it in items:
        d = it['DOI'].lower(); allr.setdefault(d, dict(doi=d, title=(it.get('title') or [''])[0], journal=(it.get('container-title') or [''])[0],
            year=it['issued']['date-parts'][0][0], cites=it.get('is-referenced-by-count'), abstract=re.sub('<[^>]+>', '', it.get('abstract') or '')[:1500],
            authors=[a.get('family') for a in it.get('author', [])][:6], queries=[]))['queries'].append(k)
    print(k, len(items)); time.sleep(1)
json.dump(list(allr.values()), open('sources/lit_candidates.json', 'w'), ensure_ascii=False, indent=1); print('jami takrorsiz', len(allr))
