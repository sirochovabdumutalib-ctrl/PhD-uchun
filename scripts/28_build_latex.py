"""out/dissertatsiya.md (13_build_docx.py natijasi) asosida OAK talablariga mos LaTeX manbasi va PDF:
latex/Dissertatsiya.tex -> out/Dissertatsiya_Sirochov_A_OAK.pdf"""
import re, subprocess, os, shutil
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
md = open('out/dissertatsiya.md', encoding='utf-8').read()
md = md[md.index('# KIRISH'):]                                   # titul va Word mundarijasi LaTeX'da alohida
md = re.sub(r'```\{=openxml\}.*?```', '', md, flags=re.S)
open('latex/body.md', 'w', encoding='utf-8').write(md)
subprocess.run(['pandoc', 'latex/body.md', '-f', 'markdown+pipe_tables+fenced_divs+tex_math_dollars+raw_attribute',
                '-t', 'latex', '--lua-filter=latex/oak.lua', '-o', 'latex/body.tex'], check=True)
b = open('latex/body.tex', encoding='utf-8').read()
# jadvallar: to'liq to'r chiziqlar
def grid(m):
    t = m.group(0)
    t = re.sub(r'\\begin\{longtable\}\[\]\{@\{\}(.*?)@\{\}\}', lambda k: '\\begin{longtable}[]{|' + re.sub(r'(?<=\})\s*(?=>)', '|', k.group(1)) + '|}', t, count=1, flags=re.S)
    n = t.split('\\hline')[0].count('p{') or 1
    t = re.sub(r'- (\d+)\\tabcolsep\)', lambda k: '- %d\\tabcolsep - %d\\arrayrulewidth)' % (int(k.group(1)) + 2, n + 1), t)
    t = re.sub(r'\\(toprule|midrule|bottomrule)\\noalign\{\}', r'\\hline', t)
    t = re.sub(r'\\(toprule|midrule|bottomrule)', r'\\hline', t)
    t = re.sub(r'\\\\\n(?!\\hline|\\endhead|\\endfirsthead|\\endfoot|\\endlastfoot|\\end\{longtable\})', r'\\\\ \\hline\n', t)
    return t
b = re.sub(r'\\begin\{longtable\}.*?\\end\{longtable\}', grid, b, flags=re.S)
b = b.replace('\\begin{longtable}', '\\noindent\\begin{longtable}')
SUB = {'ᵢ': 'i', 'ₜ': 't', 'ₖ': 'k', 'ⱼ': 'j'}
b = re.sub(r'([A-Za-z])([ᵢₜₖⱼ]+)', lambda m: '$' + m.group(1) + '_{' + ''.join(SUB[c] for c in m.group(2)) + '}$', b)
pre = open('latex/preamble.tex', encoding='utf-8').read()
title = r"""
\begin{document}
\begin{titlepage}\setstretch{1.15}\centering
{\bfseries OʻZBEKISTON RESPUBLIKASI QISHLOQ XOʻJALIGI VAZIRLIGI\\[4pt] ANDIJON QISHLOQ XOʻJALIGI VA AGROTEXNOLOGIYALAR INSTITUTI\par}
\vspace{20mm}
\hfill\begin{tabular}{l}Qoʻlyozma huquqida\\ UDK: \toldir{\hspace{25mm}}\end{tabular}
\vspace{25mm}

{\bfseries SIROCHOV ABDUMUTALIB\par}
\vspace{12mm}
{\bfseries\fontsize{16}{20}\selectfont GAT TEXNOLOGIYALARI ASOSIDA MELIORATIV TIZIMLAR SAMARADORLIGI VA ISHONCHLILIGINI TAʼMINLASH\par}
\vspace{4mm}
{\bfseries (Andijon viloyati Marhamat tumani misolida)\par}
\vspace{14mm}
05.09.06 – Gidrotexnika va melioratsiya qurilishi\par
\vspace{10mm}
Texnika fanlari boʻyicha falsafa doktori (PhD)\\ dissertatsiyasi\par
\vfill
\hfill\begin{tabular}{l}Ilmiy rahbar:\\ t.f.n., dotsent A.Xakimov\end{tabular}
\vfill
ANDIJON – 2026
\end{titlepage}
\setcounter{page}{2}
\tableofcontents
"""
open('latex/Dissertatsiya.tex', 'w', encoding='utf-8').write(pre + title + b + '\n\\end{document}\n')
# rasmlar yo'li
if not os.path.exists('latex/figures'): os.symlink('../figures', 'latex/figures')
sk = os.path.abspath('.agents/skills/latex-document-skill/scripts/compile_latex.sh')
r = subprocess.run(['bash', sk, 'Dissertatsiya.tex', '--engine', 'xelatex', '--quiet'], cwd='latex')
shutil.copy('latex/Dissertatsiya.pdf', 'out/Dissertatsiya_Sirochov_A_OAK.pdf'); print('pdf ok')
