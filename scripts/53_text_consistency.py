"""Matn ichki muvofiqligi (scientific-writing skill, 3-band): Kirish, bob xulosalari va Umumiy xulosalardagi
har bir raqam bob matnida (xulosa bo'limlaridan tashqari) yoki ilovalarda uchrashini tekshiradi.
Chiqish: results/text_consistency.json (topilmagan raqamlar kontekst bilan)."""
import re, json, glob
T = {f: open(f, encoding='utf-8').read().replace('’', "'").replace('ʼ', "'") for f in sorted(glob.glob('text/[0-6]_*.md'))}
def split_concl(s):
    i = s.find('bo\'yicha xulosalar'); 
    if i < 0: return s, ''
    j = s.rfind('\n## ', 0, i); return s[:j], s[j:]
body, concl = {}, {}
for f in ('text/1_bob.md', 'text/2_bob.md', 'text/3_bob.md', 'text/4_bob.md'):
    body[f], concl[f] = split_concl(T[f])
ALL_BODY = ''.join(body.values()) + T['text/6_ilovalar.md']
NUM = re.compile(r'(?<![\w,.\-])[−+-]?\d[\d  ]*(?:,\d+)?(?![\w])')
def norm(x): return x.replace(' ', '').replace(' ', '').replace('−', '-').lstrip('+')
BODYNUMS = {norm(m.group()) for m in NUM.finditer(ALL_BODY)}
SKIP = {str(i) for i in range(0, 21)} | {'2009', '2024', '2010', '2016', '2018', '2019', '2004', '2017', '2020', '2026'}
out = {}
srcs = {'Kirish': T['text/0_kirish.md'], 'Umumiy xulosalar': T['text/5_xulosa.md'], **{f'{f[5]}-bob xulosalari': concl[f] for f in concl}}
for name, s in srcs.items():
    miss = []
    for m in NUM.finditer(s):
        v = norm(m.group())
        if v in SKIP or v in BODYNUMS or v.lstrip('-') in BODYNUMS: continue
        a = max(0, m.start() - 70); miss.append(dict(value=m.group().strip(), context=s[a:m.end() + 40].replace('\n', ' ')))
    out[name] = miss
json.dump(out, open('results/text_consistency.json', 'w'), ensure_ascii=False, indent=1)
for k, v in out.items():
    print(f'== {k}: {len(v)}')
    for r in v: print('  ', r['value'], '|', r['context'])
