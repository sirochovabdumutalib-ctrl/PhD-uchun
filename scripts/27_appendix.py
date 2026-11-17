"""Asosiy matndan yordamchi jadval va rasmlarni ilovaga ko'chirish va qolganlarini qayta raqamlash.
Kirish/chiqish: text/2_bob.md, text/3_bob.md, text/4_bob.md -> o'zgartiriladi; text/6_ilovalar.md yaratiladi; results/appendix_map.json"""
import re, json
MOVE = {'2': ['2.6-jadval', '2.7-jadval', '2.9-jadval', '2.10-jadval', '2.3-rasm'], '3': ['3.1-jadval', '3.2-jadval', '3.6-jadval', '3.7-jadval', '3.4-rasm', '3.8-jadval', '3.9-jadval', '3.5-rasm', '3.13-jadval', '3.15-jadval', '3.16-jadval', '3.17-jadval', '3.21-jadval'],
        '4': ['4.2-jadval', '4.3-jadval', '4.5-jadval', '4.7-jadval', '4.9-jadval', '4.13-jadval']}
DROP_SUMMARY = {'2': False, '3': True, '4': False}
app, mapping = [], {}
def blocks(t): return re.split(r'\n\s*\n', t.strip('\n'))
for ch in ('2', '3', '4'):
    p = f'text/{ch}_bob.md'; B = blocks(open(p, encoding='utf-8').read()); out = []; i = 0
    cap = lambda b: re.match(r'^\*(\d\.\d+-(?:jadval|rasm))\.', b)
    while i < len(B):
        b = B[i]; m = cap(b)
        if DROP_SUMMARY[ch] and b.startswith("**Paragraf bo'yicha umumlashma.**"): i += 1; continue
        # image placeholder followed by rasm caption
        if b.startswith('&#91;image:') and i + 1 < len(B) and cap(B[i + 1]) and cap(B[i + 1]).group(1) in MOVE[ch]:
            lab = cap(B[i + 1]).group(1); app.append(dict(label=lab, blocks=[b, B[i + 1]])); i += 2; continue
        if m and m.group(1) in MOVE[ch] and 'jadval' in m.group(1):
            grp = [b]; i += 1
            while i < len(B) and (B[i].startswith('|') or B[i].startswith('Izoh')): grp.append(B[i]); i += 1
            app.append(dict(label=m.group(1), blocks=grp)); continue
        out.append(b); i += 1
    open(p, 'w', encoding='utf-8').write('\n\n'.join(out) + '\n')
# appendix numbers in order of appearance
for k, a in enumerate(app, 1): mapping[a['label']] = f'{k}-ilova'
# renumber remaining per chapter
for ch in ('2', '3', '4'):
    p = f'text/{ch}_bob.md'; t = open(p, encoding='utf-8').read()
    for kind in ('jadval', 'rasm'):
        caps = re.findall(rf'^\*({ch}\.\d+)-{kind}\.', t, flags=re.M); n = 0
        for c in caps:
            n += 1; new = f'{ch}.{n}-{kind}'
            if f'{c}-{kind}' != new: mapping[f'{c}-{kind}'] = new
    t2 = re.sub(r'(?<![\d.])(\d\.\d+)-(jadval|rasm)', lambda m: '@@' + mapping.get(f'{m.group(1)}-{m.group(2)}', f'{m.group(1)}-{m.group(2)}') + '@@', t)
    # "N-ilova" references inside text: fix grammar of suffixes is preserved (e.g. -jadvalda -> -ilovada)
    t2 = t2.replace('@@', ''); open(p, 'w', encoding='utf-8').write(t2)
# write appendix
L = ['# ILOVALAR', '']
for a in app:
    num = mapping[a['label']]; bl = list(a['blocks'])
    ci = next(j for j, b in enumerate(bl) if re.match(r'^\*\d\.\d+-(jadval|rasm)\.', b))
    title = re.sub(r'^\*\d\.\d+-(?:jadval|rasm)\.\s*', '', bl[ci]).rstrip('*').strip()
    bl.pop(ci); L += [f'## {num}', '', f'*{num}. {title}*', ''] + [x + '\n' for x in bl]
open('text/6_ilovalar.md', 'w', encoding='utf-8').write('\n'.join(L))
json.dump(mapping, open('results/appendix_map.json', 'w'), ensure_ascii=False, indent=1)
print(json.dumps(mapping, ensure_ascii=False))
