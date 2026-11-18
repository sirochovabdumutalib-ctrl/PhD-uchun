"""Dissertatsiya grafiklari uchun yagona uslub (scientific-visualization skill).
Xaritalar bilan bir xil shrift (Liberation Sans 8 pt), Okabe–Ito palitrasi, o'nli vergul, a/b/c panel belgilari.
Eksport carto.export orqali: PDF (vektor) + PNG 600 dpi + provenance + alt-matn."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from carto import export, cm  # noqa: F401  (carto rcParams ham shu yerda o'rnatiladi)

plt.rcParams.update({'font.family': 'Liberation Sans', 'font.size': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5,
                     'legend.fontsize': 7, 'axes.linewidth': .7, 'xtick.major.width': .6, 'ytick.major.width': .6,
                     'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': '#dddddd', 'grid.linewidth': .5,
                     'axes.axisbelow': True, 'legend.frameon': False, 'pdf.fonttype': 42, 'figure.facecolor': 'white', 'savefig.facecolor': 'white'})
# Okabe–Ito
OI = dict(blue='#0072B2', orange='#E69F00', verm='#D55E00', green='#009E73', sky='#56B4E9', purple='#CC79A7', yellow='#F0E442', black='#000000', grey='#7F7F7F')
SEQ7 = [OI['blue'], OI['orange'], OI['green'], OI['verm'], OI['purple'], OI['sky'], OI['black']]
MARK7 = ['o', 's', '^', 'D', 'v', 'P', 'X']
LS7 = ['-', '--', '-.', ':', '-', '--', '-.']
MONTHS = ['Yan', 'Fev', 'Mar', 'Apr', 'May', 'Iyn', 'Iyl', 'Avg', 'Sen', 'Okt', 'Noy', 'Dek']
LAT = {'З.М.Бобур': 'Z.M.Bobur', 'Истиқлол': 'Istiqlol', 'Й.Охунбобоев': 'Y.Oxunboboyev', 'М.Тожибоев': 'M.Toʻjiboyev', 'Машъал': 'Mashʼal',
       'Пахтакор': 'Paxtakor', 'Т.Мирзаев': 'T.Mirzayev', 'У.Қорабоев': 'U.Qoraboyev'}
W_FULL = 15.5  # cm, matn kengligi


def comma(dec=None):
    """O'nli vergul bilan o'q yozuvlari; minus — haqiqiy minus belgisi."""
    def f(v, _):
        s = (f'{v:.{dec}f}' if dec is not None else f'{v:g}').replace('.', ',')
        return s.replace('-', '−')
    return FuncFormatter(f)


def fmt(v, dec=2):
    return f'{v:.{dec}f}'.replace('.', ',').replace('-', '−')


def panel(ax, letter, x=-0.02, y=1.02):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=9, fontweight='bold', ha='right', va='bottom')


def axes_commas(*axs, xdec=None, ydec=None, x=False):
    """O'nli vergul: y o'qiga doim, x o'qiga faqat x=True yoki xdec berilganda (toifali yozuvlarni buzmaslik uchun)."""
    for a in axs:
        a.yaxis.set_major_formatter(comma(ydec))
        if x or xdec is not None: a.xaxis.set_major_formatter(comma(xdec))


def fig(w_cm, h_cm, **kw):
    return plt.subplots(figsize=(cm(w_cm), cm(h_cm)), layout='constrained', **kw)
