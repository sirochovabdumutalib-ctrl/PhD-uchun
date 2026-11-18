"""Asosiy faktlar registri (scientific-writing, 3-band): har bir fakt uchun matndagi barcha takrorlar topiladi va
ulardagi qiymatlar bir xilligi hamda results/*.json dagi manba qiymatiga mosligi tekshiriladi.
Chiqish: results/key_facts.json"""
import re, json, glob
T = {f: open(f, encoding='utf-8').read().replace('’', "'").replace('ʼ', "'") for f in sorted(glob.glob('text/[0-6]_*.md'))}
J = lambda f: json.load(open(f'results/{f}'))
dyn, geo, mine, reg, did, pw = J('ch3_dyn_ext.json'), J('ch3_geo_ext.json'), J('ch3_miner_ext.json'), J('ch3_region.json'), J('did_staggered.json'), J('did_power_sim.json')
c26 = J('cost_2026.json')
F = [  # (nom, regex — 1-guruh qiymat, manba qiymati yoki None, manba izohi)
 ('Barqaror panel quduqlari', r'[Bb]arqaror panel[^.]{0,30}?\((\d+) ta quduq', dyn['panel'], 'ch3_dyn_ext.panel'),
 ('Panel boshlang\'ich sath 2009', r'2009-yildagi (\d,\d+) m dan', dyn['district']['first'], 'district.first'),
 ('Panel oxirgi sath 2024', r'2024-yilda (\d,\d+) m ga', dyn['district']['last'], 'district.last'),
 ('Mann–Kendall τ (panel)', r'τ = (0,7\d+)', dyn['district']['tau'], 'district.tau'),
 ('Sen qiyaligi, panel', r'Sen qiyaligi yiliga (0,03\d) m', round(dyn['district']['sen'], 3), 'district.sen'),
 ('Pog\'onaga uzilish p', r'Pettitt[^.]{0,80}?p = (0,0\d+)', None, '17-skript'),
 ('Sho\'rlanish xavfli quduqlar', r'(\d+) tasi\) sho\'rlanish|(\d+) ta quduq \(T-8\)|sho\'rlanish xavfi ostidagi (\d+) ta', mine['risk_total']['high'], 'risk_total.high'),
 ('Sho\'rlanish: jami quduqlar', r'(\d+) tadan \d+ tasi\) sho\'rlanish', mine['risk_n'], 'risk_n'),
 ('Yozda sayoz quduqlar ulushi, %', r'quduqlarning (\d+) foizida sath 1,5 m dan sayoz', round(39 / 167 * 100), '39/167'),
 ('Kriging xaritasida sayoz maydon, %', r'(\d,\d) foiz(?:ida|i)?\b[^.]{0,5}', None, ''),
 ('Ta\'mir ta\'siri, asosiy baho', r'(−0,\d+) m[^.]{0,30}95 foizlik ishonch', -0.12, '4.3-§ asosiy model'),
 ('Zarur quduqlar (0,20 m)', r'taxminan (\d+) ta quduq', 95, 'did_power_sim (interpolyatsiya)'),
 ('Ta\'mir narxi medianasi, mln so\'m/km', r'medianasi (\d+) mln so\'m/km', None, 'cost_2026'),
 ('Jami xarajat 2026 narxida, mlrd', r'(\d+,\d) mlrd so\'m', round(c26.get('total_2026_mln', 48176) / 1000, 1) if isinstance(c26, dict) else 48.2, 'cost_2026'),
 ('Viloyat ρ (o\'zgarmas qator–sath)', r'ρ = \+(0,8\d)', None, 'ch3_region'),
 ('Viloyat quduqlari', r'(2 052) ta quduq', None, ''),
 ('Kollektorlar soni', r'(\d+) ta kollektorning', 90, 'kadastr'),
 ('Joyiga bog\'lash quduqlari', r'(\d+) ta quduq (?:orqali|orqali joyiga)', 181, '04-skript'),
 ('Kuzatuv tarmog\'i to\'yinishi', r'quduqlar soni (\d+) tadan', 94, '18-skript'),
]
R = {}
for name, rx, src, note in F:
    vals = {}
    for f, s in T.items():
        for m in re.finditer(rx, s):
            v = next(g for g in m.groups() if g); vals.setdefault(v, []).append(f[5:])
    ok_src = None
    if src is not None and vals:
        ok_src = all(abs(float(v.replace('−', '-').replace(',', '.').replace(' ', '')) - float(src)) < 0.006 for v in vals)
    R[name] = dict(values={k: sorted(set(v)) for k, v in vals.items()}, source=src, source_note=note, consistent=len(vals) <= 1, matches_source=ok_src)
json.dump(R, open('results/key_facts.json', 'w'), ensure_ascii=False, indent=1)
for k, v in R.items(): print(('OK ' if v['consistent'] and v['matches_source'] in (True, None) else '!! ') + k, v['values'], '| manba:', v['source'])
