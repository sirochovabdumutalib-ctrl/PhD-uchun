"""Yakuniy Word uchun matnga ishlov: tutuq belgilari (oʻ, gʻ, ʼ), nomlarning yagona yozilishi,
adabiyotlar ro'yxatini tozalash, bo'limlarga ajratish, alifbo tartibi va matndagi havolalarni qayta raqamlash,
to'ldiriladigan joylarni belgilash."""
import re
NAMES = [('**D****issertatsiya', '**Dissertatsiya'), ('M.Tojiboyev', "M.To'jiboyev"), ('T.Mirzaev', 'T.Mirzayev'), ('S.Ye.Mirsxulava', 'Ts.Ye.Mirtsxulava')]
PROTECT = re.compile(r"```.*?```|\$\$.*?\$\$|https?://\S+|\]\([^)]*\)|\{[^{}]*\}", re.S)
def _apos(s):
    s = re.sub(r"([oOgG])['’‘`]", '\\1ʻ', s)
    s = re.sub(r"(?<=[A-Za-zʻ])['’‘`](?=[A-Za-z])", 'ʼ', s)
    return s
def typo(t):
    for a, b in NAMES: t = t.replace(a, b)
    out, last = [], 0
    for m in PROTECT.finditer(t):
        out.append(_apos(t[last:m.start()])); out.append(m.group(0)); last = m.end()
    out.append(_apos(t[last:])); return ''.join(out)
CIT = re.compile(r'\\\[(\d+(?:\s*[–-]\s*\d+)?(?:\s*[;,]\s*\d+(?:\s*[–-]\s*\d+)?)*)\\\]')
def _expand(c):
    s = []
    for p in re.split(r'[;,]', c):
        p = p.strip()
        if re.search(r'[–-]', p): a, b = [int(x) for x in re.split(r'\s*[–-]\s*', p)]; s += list(range(a, b + 1))
        else: s.append(int(p))
    return s
def _compress(nums):
    nums = sorted(set(nums)); out = []; i = 0
    while i < len(nums):
        j = i
        while j + 1 < len(nums) and nums[j + 1] == nums[j] + 1: j += 1
        out.append(f'{nums[i]}–{nums[j]}' if j - i >= 2 else ', '.join(str(x) for x in nums[i:j + 1])); i = j + 1
    return ', '.join(out)
NORM_LAW = [134, 1, 3, 135, 2]; NORM_STD = [4, 7, 144]; WEB = [153, 154, 155]; UZ_REFS = {1, 2, 3, 4, 5, 134, 135, 155}
def refs_build(texts, refs):
    """texts: list of chapter strings; refs: list (old order, 1-based). Returns new texts, refs markdown."""
    used = set()
    for t in texts:
        for m in CIT.finditer(t): used |= set(_expand(m.group(1)))
    def key(i):
        s = re.sub(r'^[^\wА-Яа-яЁё]+', '', refs[i - 1]).lower().replace('ҳ', 'х').replace('ё', 'е').replace('ў', 'у').replace('қ', 'к').replace('ғ', 'г')
        return s
    law = [i for i in NORM_LAW if i in used]; std = [i for i in NORM_STD if i in used]; web = [i for i in WEB if i in used]
    rest = [i for i in sorted(used) if i not in law + std + web]
    cyr = sorted([i for i in rest if re.match(r'[А-Яа-яЁё]', refs[i - 1])], key=key)
    lat = sorted([i for i in rest if i not in cyr], key=key)
    order = law + std + cyr + lat + web; new = {o: k for k, o in enumerate(order, 1)}
    def fix(t): return CIT.sub(lambda m: '\\[' + _compress([new[x] for x in _expand(m.group(1))]) + '\\]', t)
    out = [fix(t) for t in texts]
    def item(o):
        r = refs[o - 1].replace('–-', '–').replace(' -- ', ' – ')
        return f'{new[o]}. ' + (typo(r) if o in UZ_REFS else r)
    md = ['# FOYDALANILGAN ADABIYOTLAR ROʻYXATI', '', '**I. Normativ-huquqiy hujjatlar va meʼyoriy hujjatlar**', '']
    md += [item(o) for o in law + std]
    md += ['', '**II. Ilmiy adabiyotlar**', ''] + [item(o) for o in cyr + lat]
    md += ['', '**III. Internet resurslari**', ''] + [item(o) for o in web]
    return out, '\n\n'.join(x for x in md if x is not None).replace('\n\n\n', '\n\n'), dict(n_old=len(refs), n_new=len(order), dropped=sorted(set(range(1, len(refs) + 1)) - used))
PH = re.compile(r'\\\[([^\]\\]*?[A-Za-zʻʼ][^\]\\]*?)\\\]')
def mark_placeholders(t):
    return PH.sub(lambda m: m.group(0) if re.search(r'[()/=−]', m.group(1)) else '[\\[' + m.group(1) + '\\]]{custom-style="Toldirish"}', t)
