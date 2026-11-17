"""OAK hajm talabi (asosiy matn <= 120 bet) uchun 1.1, 2.1 va 3.10-jadvallarni ilovaga ko'chirish,
qolgan jadvallarni qayta raqamlash va ilovalarni matnda birinchi tilga olinish tartibida qayta raqamlash."""
import re, glob
import sys
MOVE = sys.argv[1:] or ['1.1-jadval', '2.1-jadval', '3.10-jadval']
F = {f: open(f, encoding='utf-8').read() for f in sorted(glob.glob('text/[0-6]_*.md'))}
def blocks(t): return re.split(r'\n\s*\n', t.strip('\n'))
new_app = {}
for lab in MOVE:
    f = f'text/{lab[0]}_bob.md'; B = blocks(F[f]); out = []; i = 0
    while i < len(B):
        m = re.match(r'^\*(\d\.\d+-jadval)\.\s*(.*?)\*\s*$', B[i])
        if m and m.group(1) == lab:
            grp = []; i += 1
            while i < len(B) and (B[i].startswith('|') or B[i].startswith('Izoh')): grp.append(B[i]); i += 1
            new_app[lab] = (m.group(2), grp); continue
        out.append(B[i]); i += 1
    F[f] = '\n\n'.join(out) + '\n'
# vaqtinchalik ilova belgilari
tmp = {lab: f'X{k}' for k, lab in enumerate(MOVE)}
mapping = {lab: f'{tmp[lab]}-ilova' for lab in MOVE}
for ch in '1234':
    f = f'text/{ch}_bob.md'; n = 0
    for c in re.findall(rf'^\*({ch}\.\d+-jadval)\.', F[f], flags=re.M):
        n += 1; new = f'{ch}.{n}-jadval'
        if c != new: mapping[c] = new
rx = re.compile(r'(?<![\d.])(\d\.\d+-jadval)')
for f in F: F[f] = rx.sub(lambda m: mapping.get(m.group(1), m.group(1)), F[f])
# ilova bo'limlariga qo'shish
A = F['text/6_ilovalar.md']
secs = re.split(r'(?m)^## ', A); head, secs = secs[0], secs[1:]
for lab in MOVE:
    title, grp = new_app[lab]; num = tmp[lab]
    secs.append(f'{num}-ilova\n\n*{num}-ilova. {title}*\n\n' + '\n\n'.join(grp) + '\n\n')
# birinchi tilga olinish tartibi (asosiy matnda)
main = ''.join(F[f] for f in F if not f.endswith('6_ilovalar.md'))
order = []
for m in re.finditer(r'(?<![\d.\w])(X\d|\d+)-ilova', main):
    if m.group(1) not in order: order.append(m.group(1))
labels = [re.match(r'(X\d|\d+)-ilova', s).group(1) for s in secs]
for l in labels:
    if l not in order: order.append(l)
ren = {old: str(k) for k, old in enumerate(order, 1)}
def rn(t): return re.sub(r'(?<![\d.\w])(X\d|\d+)-ilova', lambda m: ren.get(m.group(1), m.group(1)) + '-ilova', t)
secs = sorted(secs, key=lambda s: order.index(re.match(r'(X\d|\d+)-ilova', s).group(1)))
F['text/6_ilovalar.md'] = rn(head + ''.join('## ' + s if s.endswith('\n') else '## ' + s + '\n' for s in secs))
for f in F:
    if not f.endswith('6_ilovalar.md'): F[f] = rn(F[f])
for f, t in F.items(): open(f, 'w', encoding='utf-8').write(t)
print({k: v for k, v in mapping.items()}); print({k: v for k, v in ren.items() if k != v})
