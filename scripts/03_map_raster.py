"""PDF xaritaning rastr qismini (yozuvlarsiz) 300 dpi da yig'adi va quduq belgilarini, yozuvlarini ajratadi.
Ishlatish: python3 scripts/03_map_raster.py <pdf> <out_prefix>"""
import sys, json, re, numpy as np, pymupdf
from PIL import Image
pdf, out = sys.argv[1], sys.argv[2]
doc = pymupdf.open(pdf); p = doc[0]; S = 300 / 72
# Yozuvlarni (BT...ET) kontent oqimidan olib tashlab, sahifani to'liq chizamiz: rastr bo'laklari to'g'ri joylashadi.
spans_page = pymupdf.open(pdf)[0]
for xref in p.get_contents():
    stream = doc.xref_stream(xref)
    doc.update_stream(xref, re.sub(rb'BT\b.*?\bET\b', b'', stream, flags=re.S))
pix = p.get_pixmap(matrix=pymupdf.Matrix(S, S), alpha=False)
canvas = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
canvas.save(out + '_raster.png')
spans = []
for b in spans_page.get_text('dict')['blocks']:
    for l in b.get('lines', []):
        txt = ''.join(s['text'] for s in l['spans']).strip()
        if not txt: continue
        s0 = l['spans'][0]; bb = l['bbox']
        spans.append({'text': txt, 'color': s0['color'], 'size': round(s0['size'], 1), 'dir': [round(x, 3) for x in l['dir']],
                      'cx': (bb[0] + bb[2]) / 2 * S, 'cy': (bb[1] + bb[3]) / 2 * S})
json.dump(spans, open(out + '_text.json', 'w'), ensure_ascii=False)
print(canvas.size, 'spans', len(spans))
