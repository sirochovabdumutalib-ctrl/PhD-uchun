"""Monitoring jadvallaridagi jami qatorlarini quduqdan ajratish.

Meliorativ ekspeditsiya jadvallarida 2019-yildan boshlab har bir massiv (uchastka) bloki oxirida «27 та» kabi qator turadi:
bu blokdagi quduqlar soni (27 ta) va ularning o'rtacha qiymatlari, quduq emas. Tuman blokining oxirgi qatori esa tumandagi
jami quduqlar sonini (masalan, Marhamatda «188») va tuman o'rtachasini beradi. Ikkalasi ham quduq sifatida o'qilmasligi kerak.
"""
import re

_TA = re.compile(r'^\d+\s*[тТ][аА]\.?$')


def is_ta_row(well):
    """«27 та», «27та» — massiv bloki bo'yicha jami qatori."""
    return bool(_TA.match(str(well).strip()))


def drop_summary(block, key=lambda r: r[0]):
    """block — bitta tuman bloki qatorlari (manbadagi tartibda). Qaytaradi: (quduq qatorlari, olib tashlangan nomlar).
    Olib tashlanadi: (1) «N та» qatorlari; (2) blokning oxirgi qatori, agar uning raqami blokdagi haqiqiy quduqlar soniga teng bo'lsa."""
    keep = [r for r in block if not is_ta_row(key(r))]
    dropped = [key(r) for r in block if is_ta_row(key(r))]
    if keep:
        last = str(key(keep[-1])).strip()
        n_other = len({str(key(r)).strip() for r in keep[:-1]})
        if last.isdigit() and int(last) == n_other:
            dropped.append(last); keep = keep[:-1]
    return keep, dropped
