"""Tavsiyanoma [173] jadvallarini kirill yozuvidan lotin yozuviga o'girish (ilovalar uchun). Kirish: tavsiyanomadan olingan matn (t2.txt).
Chiqish: results/tavsiyanoma_tables.md — har bir jadval sarlavhasi va qatorlari."""
import re, sys
V = 'аеёиоуэюяўАЕЁИОУЭЮЯЎ'
M = {'а':'a','б':'b','в':'v','г':'g','д':'d','ж':'j','з':'z','и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r','с':'s','т':'t',
     'у':'u','ф':'f','х':'x','ц':'ts','ч':'ch','ш':'sh','щ':'sh','ъ':'ʼ','ы':'i','ь':'','э':'e','ю':'yu','я':'ya','ё':'yo','ў':'oʻ','қ':'q','ғ':'gʻ','ҳ':'h'}
def tr(s):
    out = []
    for i, ch in enumerate(s):
        lo = ch.lower(); up = ch != lo
        if lo == 'е':
            prev = s[i-1] if i else ' '
            r = 'ye' if (not prev.isalpha() or prev in V) else 'e'
        elif lo in M: r = M[lo]
        else: out.append(ch); continue
        if up and r:
            nxt = s[i+1] if i + 1 < len(s) else ' '
            r = r.upper() if (nxt.isupper() and len(r) > 1) else r[0].upper() + r[1:]
        out.append(r)
    return ''.join(out)
L = open(sys.argv[1], encoding='utf-8').read().split('\n')
out = []
for i, l in enumerate(L):
    if re.match(r'^\d\.\d-жадвал$', l):
        out.append('### ' + l.replace('жадвал', 'jadval') + ' — ' + tr(L[i + 1]))
        j = i + 2
        while j < len(L) and L[j].startswith('|'):
            out.append(tr(L[j])); j += 1
        out.append('')
open('results/tavsiyanoma_tables.md', 'w', encoding='utf-8').write('\n'.join(out))
print(len(out))

# --- jadvallarni Word faylidan (birlashtirilgan kataklar bir marta) o'qib, ilovalar uchun markdown bloklari ---
def tables_from_docx(path):
    import docx
    out = []
    for t in docx.Document(path).tables:
        rows = []
        for r in t.rows:
            seen, cells = [], []
            for c in r.cells:
                if c._tc in seen: continue
                seen.append(c._tc); cells.append(c.text.strip().replace('\n', ' '))
            rows.append(cells)
        out.append(rows)
    return out

FIX = [('[7], 12-jadval', 'tuman ME hisoboti, 12-jadval'), ('[7], 15-jadval', 'tuman ME hisoboti, 15-jadval'), ('| [14] |', '| tuproq-bonitet xaritasi |'),
       ('| [13] |', '| SRTM relyef modeli |'), ('ME jadvali [6]', 'Viloyat ME jadvali'), ('ilari aniqlanadi', 'ilgari aniqlanadi'), ('GIS', 'GAT')]
def md(rows):
    rows = [[tr(c) for c in r] for r in rows]
    n = len(rows[0]); s = ['| ' + ' | '.join(rows[0]) + ' |', '|' + ' --- |' * n]
    s += ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
    s = '\n'.join(s)
    for a, b in FIX: s = s.replace(a, b)
    return s

if len(sys.argv) > 2:
    T = tables_from_docx(sys.argv[2]); J = {k: md(T[i]) for k, i in zip(
        ['abbr', '1.1', '2.1', '3.1', '4.1', '4.2', '5.1', '5.2', '5.3', '5.4', '5.5', '6.1', '6.2', '6.3', '7.1', '8.1', '8.2'], range(1, 18))}
    import json
    json.dump(J, open('results/tavsiyanoma_tables.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('tables', len(J))
