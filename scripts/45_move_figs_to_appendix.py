"""OAK hajm talabi (asosiy matn ≤ 120 bet) uchun yordamchi grafiklarni ilovaga ko'chirish:
rasm bloki (image + izoh) ilovaga o'tadi, matndagi havolalar "N-ilova" ga almashadi, qolgan rasmlar bob ichida qayta raqamlanadi,
ilovalar matnda birinchi tilga olinish tartibida qayta raqamlanadi. Foydalanish: python3 scripts/45_move_figs_to_appendix.py 3.1-rasm 3.7-rasm ..."""
import re, glob, sys
MOVE = sys.argv[1:]
F = {f: open(f, encoding='utf-8').read() for f in sorted(glob.glob('text/[0-6]_*.md'))}
def blocks(t): return re.split(r'\n\s*\n', t.strip('\n'))
moved = {}
for lab in MOVE:
    f = f'text/{lab[0]}_bob.md'; B = blocks(F[f]); out = []; i = 0
    while i < len(B):
        if B[i].startswith('&#91;image:') and i + 1 < len(B):
            m = re.match(r'^\*(\d\.\d+-rasm)\.\s*(.*?)\*\s*$', B[i + 1], flags=re.S)
            if m and m.group(1) == lab:
                moved[lab] = (m.group(2), B[i]); i += 2; continue
        out.append(B[i]); i += 1
    assert lab in moved, lab
    F[f] = '\n\n'.join(out) + '\n'
tmp = {lab: f'X{k}' for k, lab in enumerate(MOVE)}
mapping = {lab: f'{tmp[lab]}-ilova' for lab in MOVE}
for ch in '1234':
    f = f'text/{ch}_bob.md'; n = 0
    for c in re.findall(rf'^\*({ch}\.\d+-rasm)\.', F[f], flags=re.M):
        n += 1; new = f'{ch}.{n}-rasm'
        if c != new: mapping[c] = new
rx = re.compile(r'(?<![\d.])(\d\.\d+-rasm)')
for f in F: F[f] = rx.sub(lambda m: mapping.get(m.group(1), m.group(1)), F[f])
A = F['text/6_ilovalar.md']; secs = re.split(r'(?m)^## ', A); head, secs = secs[0], secs[1:]
for lab in MOVE:
    title, img = moved[lab]; num = tmp[lab]
    secs.append(f'{num}-ilova\n\n*{num}-ilova. {title}*\n\n{img}\n\n')
main = ''.join(F[f] for f in F if not f.endswith('6_ilovalar.md'))
order = []
for m in re.finditer(r'(?<![\d.\w])(X\d|\d+)-ilova', main):
    if m.group(1) not in order: order.append(m.group(1))
labels = [re.match(r'(X\d|\d+)-ilova', s).group(1) for s in secs]
for l in labels:
    if l not in order: order.append(l)
ren = {old: str(k) for k, old in enumerate(order, 1)}
rn = lambda t: re.sub(r'(?<![\d.\w])(X\d|\d+)-ilova', lambda m: ren.get(m.group(1), m.group(1)) + '-ilova', t)
secs = sorted(secs, key=lambda s: order.index(re.match(r'(X\d|\d+)-ilova', s).group(1)))
F['text/6_ilovalar.md'] = rn(head + ''.join('## ' + (s if s.endswith('\n') else s + '\n') for s in secs))
for f in F:
    if not f.endswith('6_ilovalar.md'): F[f] = rn(F[f])
for f, t in F.items(): open(f, 'w', encoding='utf-8').write(t)
print({k: v for k, v in mapping.items()}); print('ilovalar:', len(secs), {k: v for k, v in ren.items() if k != v})
