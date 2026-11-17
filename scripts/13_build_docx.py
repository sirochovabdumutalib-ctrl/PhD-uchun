"""Dissertatsiya matnini (text/*.md) yagona Word fayliga yig'adi: out/Dissertatsiya_qoralama.docx
Rasmiylashtirish: A4, Times New Roman 14, 1,5 interval, hoshiyalar 30/15/20/20 mm."""
import re, subprocess, os, glob
from docx import Document
from docx.shared import Pt, Mm, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FIX = []  # eski tuzatishlar matnning o'ziga kiritilgan
IMG = {"Andijon viloyati tumanlari xaritasi": 'figures/fig312_region.png', "Minerallashuv xaritasi": 'figures/fig310_mineralization.png', "Yozgi sath va sayoz sath ehtimoli": 'figures/fig36_summer_prob.png', "Kriging xaritasi va standart xato": 'figures/fig35_kriging.png', "Sizot suvi sathi tendensiyasi xaritasi": 'figures/fig34_trend_map.png', "Geoma’lumotlar bazasining qatlamlari": 'figures/fig23_gis_layers.png', "Ustuvorlik guruhlari va chora-tadbirlar xaritasi": 'figures/map8_priority.png', "Ta'mir xarajatlari va meliorativ xavf xaritasi": 'figures/map7_repair_cost.png', "Kollektorlarning solishtirma sarfi va talab etiladigan drenaj moduli xaritasi": 'figures/map6_drainage_capacity.png', "Kollektorlarning yoshi va oxirgi ta'mir yili xaritasi": 'figures/map5_collector_age_repair.png', "Sho'rlanish xavfi xaritasi": 'figures/map4_salinity_risk.png', "Kollektorlardan masofa zonalari va sizot rejimi": 'figures/map3_collector_zones.png', "Monitoring ma’lumotlari ishonchliligining fazoviy taqsimoti": 'figures/map2_data_quality.png', "Marhamat tumanining joylashuvi, relyefi va meliorativ tizimi": 'figures/map1_location.png', "Ta'mir xarajatlari va meliorativ xavf massivlar bo'yicha": 'figures/ch4_cost_massif.png', "Ta'mir ta'sirining dinamik bahosi": 'figures/ch4_event_study.png', "Suv balansi va talab etiladigan drenaj moduli": 'figures/ch4_hydraulic.png', "Massivlar bo'yicha drenaj tarmog'ining solishtirma uzunligi va ichki zovurlar holati": 'figures/ch4_massif_reliability.png', "Andijon viloyati tumanlari bo'yicha ma'lumotlar ishonchliligi va sath tendensiyasi": 'figures/ch3_region.png', "Sizot suvlari minerallashuvining fazoviy taqsimoti va massivlar bo'yicha farqi": 'figures/ch3_miner.png', "Sizot suvi sathining kollektorgacha masofaga bog'liqligi": 'figures/ch3_network.png', "Sizot suvi sathining eksperimental va nazariy variogrammalari": 'figures/ch3_variogram.png', "Yozgi sizot suvi sathi va sayoz sath ehtimoli xaritalari": 'figures/ch3_summer_prob.png', "Kuzatuv tarmog'i zichligining kriging aniqligiga ta'siri": 'figures/ch3_density.png', "Sizot suvi sathining dinamikasi": 'figures/ch3_dynamics.png', "Kuzatuv quduqlari bo'yicha sizot suvi sathi tendensiyasi xaritasi": 'figures/ch3_trend_map.png', "Sizot suvi sathining massivlar bo'yicha mavsumiy yo'li": 'figures/ch3_season_massif.png', "Kuzatuv tarmog’i tarkibi va yaroqsiz o’lchovlar ulushi yillar bo’yicha": 'figures/ch3_audit.png', "Sizot suvi sathining ko'p yillik va mavsumiy dinamikasi": 'figures/ch3_dynamics.png', "Sizot suvi sathi va bahoning standart xatosi xaritalari": 'figures/ch3_kriging.png', "Xaritani joyiga bog’lash qoldiqlarining taqsimoti": 'figures/ch2_georef_residuals.png', "Marhamat tumani meliorativ tizimining geoma’lumotlar bazasi": 'figures/ch2_gis_layers.png', "Andijon meteostansiyasi bo’yicha yog’in, bug’lanuvchanlik va haroratning yillik yo’li": 'figures/ch2_climate.png', "Andijon meteostansiyasi bo'yicha yog'in, bug'lanuvchanlik va haroratning yillik yo'li": 'figures/ch2_climate.png', "Sizot suvi sathining ko'p yillik va mavsumiy dinamikasi": 'figures/ch3_dynamics.png', "Sizot suvi sathi va bahoning standart xatosi xaritalari": 'figures/ch3_kriging.png',
       "Kollektorlarning yoshi, ta'mir yillari va ta'mir narxi": 'figures/ch4_reliability_costs.png'}
PB = '\n```{=openxml}\n<w:p><w:r><w:br w:type="page"/></w:r></w:p>\n```\n'
TOC = ('\n```{=openxml}\n<w:p><w:r><w:fldChar w:fldCharType="begin" w:dirty="true"/></w:r><w:r><w:instrText xml:space="preserve"> TOC \\o "1-2" \\h \\z \\u </w:instrText></w:r>'
       '<w:r><w:fldChar w:fldCharType="separate"/></w:r><w:r><w:t>Mundarijani hosil qilish uchun shu satr ustida sichqonchaning oʻng tugmasini bosib, «Maydonni yangilash» buyrugʻini tanlang.</w:t></w:r>'
       '<w:r><w:fldChar w:fldCharType="end"/></w:r></w:p>\n```\n')
def center(lines): return '\n'.join(f'::: {{custom-style="Markaz"}}\n{l or chr(160)}\n:::\n' for l in lines)
parts = [center(["O'ZBEKISTON RESPUBLIKASI QISHLOQ XO'JALIGI VAZIRLIGI", "ANDIJON QISHLOQ XO'JALIGI VA AGROTEXNOLOGIYALAR INSTITUTI", '', "Qo'lyozma huquqida", "UDK: \\_\\_\\_\\_\\_\\_\\_\\_", '',
                 '', '', "**SIROCHOV ABDUMUTALIB**", '', "**GAT TEXNOLOGIYALARI ASOSIDA MELIORATIV TIZIMLAR SAMARADORLIGI VA ISHONCHLILIGINI TA'MINLASH**", "**(Andijon viloyati Marhamat tumani misolida)**", '',
                 "05.09.06 — Gidrotexnika va melioratsiya qurilishi", "Texnika fanlari bo'yicha falsafa doktori (PhD) ilmiy darajasini olish uchun yozilgan", "**DISSERTATSIYA**", '', '',
                 "Ilmiy rahbar: t.f.n., dotsent A.Xakimov", '', '', '', '', '', '', "ANDIJON — 2026"]), PB, center(["**MUNDARIJA**"]), TOC]
def prep(t):
    for a, b in FIX:
        if a in t: t = t.replace(a, b)
    t = re.sub(r"^\*Izoh: bu birinchi qoralama\..*?\*\s*$", '', t, flags=re.M)
    t = re.sub(r"^&#91;image: (.+?)\\\]\s*$", lambda m: f"\n![]({IMG[m.group(1)]}){{width=15.5cm}}\n", t, flags=re.M)
    t = re.sub(r"```latex\n(.*?)\n```", lambda m: '$$' + m.group(1).strip() + '$$', t, flags=re.S)
    t = re.sub(r"^\*(\d+-ilova\..*?)\*\s*$", lambda m: f'\n::: {{custom-style="Sarlavha-jadval"}}\n{m.group(1)}\n:::\n', t, flags=re.M)
    return t
import os, sys
sys.path.insert(0, 'scripts'); import finalize_lib as FL
files = sorted(glob.glob('text/[0-5]_*.md')) + (['text/6_ilovalar.md'] if os.path.exists('text/6_ilovalar.md') else [])
texts = [open(f, encoding='utf-8').read() for f in files]
refs = [re.sub(r'^\d+\.\s*', '', l.strip()) for l in open('text/refs_old.txt', encoding='utf-8') if l.strip()]
texts, refs_md, refs_info = FL.refs_build(texts, refs); print('adabiyotlar:', refs_info)
def finish(t):
    t = re.sub(r"^\*Izoh: bu birinchi qoralama\..*?\*\s*$", '', t, flags=re.M)
    t = re.sub(r"^&#91;image: (.+?)\\\]\s*$", lambda m: f"\n![]({IMG[m.group(1)]}){{width=15.5cm}}\n", t, flags=re.M)
    t = re.sub(r"```latex\n(.*?)\n```", lambda m: '$$' + m.group(1).strip() + '$$', t, flags=re.S)
    t = re.sub(r"^\*\d+-ilova\.\s*(.*?)\*\s*$", lambda m: f'\n::: {{custom-style="Sarlavha-jadval"}}\n**{m.group(1)}**\n:::\n', t, flags=re.M)
    t = re.sub(r"^\*(\d\.\d+-jadval)\.\s*(.*?)\*\s*$", lambda m: f'\n::: {{custom-style="Jadval-raqam"}}\n{m.group(1)}\n:::\n\n::: {{custom-style="Sarlavha-jadval"}}\n**{m.group(2)}**\n:::\n', t, flags=re.M)
    t = re.sub(r"^\*(\d\.\d+-rasm\..*?)\*\s*$", lambda m: f'\n::: {{custom-style="Sarlavha-rasm"}}\n{m.group(1)}\n:::\n', t, flags=re.M)
    return FL.mark_placeholders(FL.typo(t))
def eqnum(t):  # formulalarni bob ichida raqamlash: (2.1), (2.2) ...
    ch, k = 0, 0
    out = []
    for line in t.split('\n'):
        m = re.match(r'^# ([IV]+) BOB', line)
        if m: ch = {'I': 1, 'II': 2, 'III': 3, 'IV': 4}[m.group(1)]; k = 0
        elif line.startswith('# '): ch = 0
        if line.startswith('$$') and line.endswith('$$') and ch:
            k += 1; line = line[:-2] + r' \qquad\qquad (' + f'{ch}.{k}' + ')$$'
        out.append(line)
    return '\n'.join(out)
body = [finish(t) for t in texts]
has_app = files[-1].endswith('6_ilovalar.md')
for t in (body[:-1] if has_app else body): parts += [PB, t]
parts += [PB, refs_md]
if has_app: parts += [PB, body[-1]]
parts[0] = FL.typo(parts[0])
open('out/dissertatsiya.md', 'w', encoding='utf-8').write(eqnum('\n\n'.join(parts)))
# --- andoza (reference.docx)
subprocess.run('pandoc -o out/ref.docx --print-default-data-file reference.docx', shell=True, check=True)
d = Document('out/ref.docx')
class _S:
    def __init__(s, d): s.d = d
    def __getitem__(s, n): return next(x for x in s.d.styles if x.name == n)
    def add_style(s, n, t): return s.d.styles.add_style(n, t)
st = _S(d)
def setfont(s, size=14, bold=None, italic=None):
    s.font.name = 'Times New Roman'; s.font.size = Pt(size); s.font.color.rgb = RGBColor(0, 0, 0)
    rpr = s.element.get_or_add_rPr(); rf = rpr.find(qn('w:rFonts'))
    if rf is None: rf = OxmlElement('w:rFonts'); rpr.append(rf)
    for a in ('w:ascii', 'w:hAnsi', 'w:cs', 'w:eastAsia'): rf.set(qn(a), 'Times New Roman')
    for a in ('w:asciiTheme', 'w:hAnsiTheme', 'w:cstheme', 'w:eastAsiaTheme'):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    if bold is not None: s.font.bold = bold
    if italic is not None: s.font.italic = italic
def para(s, align=WD_ALIGN_PARAGRAPH.JUSTIFY, indent=1.25, before=0, after=0, spacing=1.5):
    pf = s.paragraph_format; pf.alignment = align; pf.first_line_indent = Cm(indent); pf.space_before = Pt(before); pf.space_after = Pt(after); pf.line_spacing = spacing
for n in ('Normal', 'Body Text', 'First Paragraph', 'Compact'):
    setfont(st[n]); para(st[n])
para(st['Compact'], indent=0)
setfont(st['Heading 1'], bold=True); para(st['Heading 1'], WD_ALIGN_PARAGRAPH.CENTER, 0, 0, 12); st['Heading 1'].paragraph_format.keep_with_next = True
setfont(st['Heading 2'], bold=True); para(st['Heading 2'], WD_ALIGN_PARAGRAPH.CENTER, 0, 12, 6); st['Heading 2'].paragraph_format.keep_with_next = True
for n, al, sp in (('Markaz', WD_ALIGN_PARAGRAPH.CENTER, 1.5), ('Sarlavha-jadval', WD_ALIGN_PARAGRAPH.CENTER, 1.0), ('Sarlavha-rasm', WD_ALIGN_PARAGRAPH.CENTER, 1.0), ('Jadval-raqam', WD_ALIGN_PARAGRAPH.RIGHT, 1.0)):
    s = st.add_style(n, 1); s.base_style = st['Normal']; setfont(s, italic=False); para(s, al, 0, 0 if n in ('Markaz', 'Sarlavha-jadval') else 6, 0 if n in ('Markaz', 'Jadval-raqam') else 6, spacing=sp); s.paragraph_format.keep_with_next = n in ('Sarlavha-jadval', 'Jadval-raqam')
for sec in d.sections:
    sec.page_width, sec.page_height = Mm(210), Mm(297); sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Mm(30), Mm(15), Mm(20), Mm(20)
from docx.enum.style import WD_STYLE_TYPE
_hl = d.styles.add_style('Toldirish', WD_STYLE_TYPE.CHARACTER); _rpr = _hl.element.get_or_add_rPr(); _h = OxmlElement('w:highlight'); _h.set(qn('w:val'), 'yellow'); _rpr.append(_h)
d.save('out/ref.docx')
subprocess.run('pandoc out/dissertatsiya.md -f markdown+pipe_tables+fenced_divs+tex_math_dollars+raw_attribute -o out/Dissertatsiya_qoralama.docx --reference-doc=out/ref.docx --resource-path=.', shell=True, check=True)
# --- yakuniy ishlov: jadvallar, rasmlar, sahifa raqami
d = Document('out/Dissertatsiya_qoralama.docx')
for t in d.tables:
    tblPr = t._tbl.tblPr; b = OxmlElement('w:tblBorders')
    for e in ('top', 'left', 'bottom', 'right', 'insideH', 'insideV'):
        x = OxmlElement(f'w:{e}'); x.set(qn('w:val'), 'single'); x.set(qn('w:sz'), '4'); x.set(qn('w:space'), '0'); x.set(qn('w:color'), '000000'); b.append(x)
    tblPr.append(b)
    for old in tblPr.findall(qn('w:tblW')): tblPr.remove(old)
    w = OxmlElement('w:tblW'); w.set(qn('w:type'), 'pct'); w.set(qn('w:w'), '5000'); tblPr.append(w)
    nxt = t._tbl.getnext()
    if nxt is not None and nxt.tag == qn('w:p'):
        from docx.text.paragraph import Paragraph
        Paragraph(nxt, t._parent).paragraph_format.space_before = Pt(8)
    for ri, row in enumerate(t.rows):
        for c in row.cells:
            for p in c.paragraphs:
                p.paragraph_format.first_line_indent = Cm(0); p.paragraph_format.line_spacing = 1.0; p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs: r.font.size = Pt(12); r.font.name = 'Times New Roman'; r.font.bold = True if ri == 0 else r.font.bold
for p in d.paragraphs:
    if p._p.xpath('.//w:drawing'): p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.first_line_indent = Cm(0)
    if p._p.xpath('.//m:oMathPara') or p._p.xpath('.//m:oMath'): p.paragraph_format.first_line_indent = Cm(0)
for sec in d.sections:                                    # sahifa raqami pastki o'ng burchakda
    sec.different_first_page_header_footer = True
    fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.RIGHT; r = fp.add_run()
    for typ, txt in (('begin', None), (None, 'PAGE'), ('end', None)):
        if typ: e = OxmlElement('w:fldChar'); e.set(qn('w:fldCharType'), typ)
        else: e = OxmlElement('w:instrText'); e.text = txt
        r._r.append(e)
    r.font.size = Pt(12); r.font.name = 'Times New Roman'
from docx.enum.text import WD_COLOR_INDEX
for p in d.paragraphs:
    for r in p.runs:
        if r.style is not None and r.style.name == 'Toldirish': r.font.highlight_color = WD_COLOR_INDEX.YELLOW
d.save('out/Dissertatsiya_qoralama.docx'); print('tables', len(d.tables), 'paragraphs', len(d.paragraphs))
