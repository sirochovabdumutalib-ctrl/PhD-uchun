# Dissertatsiya bo'yicha doimiy qoidalar

- Meliorativ ekspeditsiya ma'lumotlarida ko'chirilgan yillar haqida yozilmaydi; faqat "mustaqil kuzatuv ma'lumotlari mavjud emas" kabi neytral ibora ishlatiladi.
- Joriy qilish dalolatnomasi (2027-yil OAK talabidan olib tashlanadi) dissertatsiyaga kiritilmaydi; "natijalarning joriy qilinishi" bandi yozilmaydi.
- Asosiy matn (Kirish – Umumiy xulosalar) 120 betdan oshmasligi kerak. Matn oʻzgarganda Word va OAK PDF da hajmni qayta tekshirish kerak (sahifa ajratgich 13-skriptda balandligi ~0 qilib berilgan).
- `scripts/06_well_network_metrics.py` qayta ishga tushirilmasin (wells_metrics.csv ni buzadi); yozgi sath 46-skript bilan hisoblanadi.
- Monitoring jadvallaridagi «N та» (massiv bloki jami) va tuman jami («188») qatorlari quduq emas: 02 va 21-skriptlar ularni `summary_rows.py` bilan olib tashlaydi. Marhamatda kuzatuv quduqlari 188 ta.
- 10, 16, 17-skriptlar eski uslubdagi `ch3_dynamics`, `ch3_audit`, `ch3_season_massif` rasmlarini qayta yozadi: ularni ishga tushirgandan keyin `python3 scripts/60_charts.py dynamics audit season` bajarilsin.
