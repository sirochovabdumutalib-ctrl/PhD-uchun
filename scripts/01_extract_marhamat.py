"""Xom kadastr fayllaridan Marhamat tumaniga tegishli ma'lumotlarni ajratib, toza CSV ga yozadi.
Ishlatish: python3 -I scripts/01_extract_marhamat.py <uploads_dir> <out_dir>"""
import sys, csv, glob, os, openpyxl
U, OUT = sys.argv[1], sys.argv[2]
def find(pat):
    return [f for f in glob.glob(os.path.join(U, '*')) if pat in os.path.basename(f)][0]
def num(v):
    try: return float(str(v).replace(',', '.'))
    except Exception: return None
def isM(v): return v is not None and 'архамат' in str(v).lower().replace('ҳ', 'х')
def w(name, header, rows):
    with open(os.path.join(OUT, name), 'w', newline='', encoding='utf-8') as f:
        cw = csv.writer(f); cw.writerow(header); cw.writerows(rows)
    print(name, len(rows))

# 1) quduqlar koordinatalari (GAT eksporti)
ws = openpyxl.load_workbook(find('b6aefc4f'), read_only=True, data_only=True)['Лист1']
w('wells_coords.csv', ['objectid', 'lon', 'lat', 'well_no'],
  [(r[0], r[3], r[4], str(r[6]).strip()) for r in ws.iter_rows(min_row=2, values_only=True) if isM(r[5])])

wb = openpyxl.load_workbook(find('79f46d33'), read_only=True, data_only=True)
# 2) quduqlar pasporti (21-jadval)
rows = [r for r in wb['Кузатув қудуқ'].iter_rows(min_row=11, values_only=True) if isM(r[12])]
w('wells_passport.csv', ['well_no', 'massif', 'built_year', 'depth_cm', 'diam_mm', 'material', 'area_ha', 'abs_mark_raw'],
  [(str(r[0]).strip(), str(r[1]).strip(), r[5], r[6], r[7], r[8], r[9], r[10]) for r in rows])
# 3) kollektorlar (18-jadval)
rows = [r for r in wb['18 ж'].iter_rows(min_row=11, values_only=True) if isM(r[3])]
w('collectors.csv', ['no', 'name', 'class', 'q_end_m3s', 'length_km', 'service_ha', 'commissioned', 'operator',
                     'repair_type', 'repair_pk', 'repair_year', 'repair_org', 'repair_cost_mln', 'balance_value'],
  [(r[0], str(r[1]).strip(), r[4], num(r[6]), num(r[7]), num(r[8]), r[9], r[10], r[11], r[12], r[13], r[14], num(r[15]), num(r[16])) for r in rows])
# 4) ichki zovurlar (massiv sarlavhalari bilan)
out, massif, on = [], None, False
for r in wb['ички зовурлар '].iter_rows(min_row=11, values_only=True):
    a = str(r[0]).strip() if r[0] is not None else ''
    if a.endswith('тумани'): on = isM(a); continue
    if not on: continue
    if 'массив' in a.lower() or (a and num(a) is None and r[1] is None): massif = a; continue
    if num(a) is not None and r[1]:
        out.append((r[0], str(r[1]).strip(), massif, num(r[6]), num(r[7]), num(r[8]), r[9], r[10], r[13]))
w('inner_drains.csv', ['no', 'name', 'massif', 'length_km', 'q_end_m3s', 'service_ha', 'commissioned', 'operator', 'repair_year'], out)

# 5) konturlar: bonitet va maydon (0-ж-по контур)
ws = openpyxl.load_workbook(find('71f23066'), read_only=True, data_only=True)['0-ж-по контур']
out, massif, farm = [], None, None
for r in ws.iter_rows(min_row=9, values_only=True):
    b = str(r[1]).strip() if r[1] is not None else ''
    if 'массив' in b.lower(): massif = b; continue
    if b and 'жами' in b.lower(): continue
    if b: farm = b
    if num(r[4]) is not None and num(r[5]) is not None:
        out.append((massif, farm, r[2], num(r[3]), r[4], num(r[5]), num(r[10]), num(r[15])))
w('contours.csv', ['massif', 'farm', 'direction', 'bonitet', 'contour_no', 'area_ha', 'cotton_ha', 'grain_ha'], out)
