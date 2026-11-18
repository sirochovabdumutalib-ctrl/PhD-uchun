# Adabiyotlar auditi (4-band: citation-management)

Skriptlar: `scripts/55_check_refs_crossref.py` → `results/refs_crossref.json`. Tekshiruv Crossref (api.crossref.org) va doi.org orqali bajarildi. Buning uchun shu repozitoriy uchun alohida «PhD-uchun» muhiti yaratildi; unda faqat shu uch manzil ochiq.

## 1. Ro'yxat va matn mosligi

- Matnda ro'yxatda yo'q havola topilmadi; ro'yxatda takror yozuv yo'q.
- 59 va 72-manbalar faqat ilovadagi adabiyotlar jadvalida keltirilgan. Bu qabul qilinadi.
- Muallif yoki usul nomi bilan keltirilgan 61 ta havola tekshirildi. Hammasi to'g'ri manbaga ishora qiladi. Tekshiruv belgilagan 6 ta holat xato emas: «Manning» so'zi «Mann» deb, «Sen» esa yonidagi Pettitt havolasi bilan noto'g'ri bog'langan, qolganlari kirill va lotin yozuvidagi bir xil mualliflar.

## 2. Xorijiy jurnal maqolalarining Crossref bilan solishtiruvi (48 ta)

| Natija | Soni | Izoh |
| --- | --- | --- |
| Yil, jurnal, jild, sahifa to'liq mos | 43 | 37 tasi avtomatik, 6 tasi qo'lda tasdiqlandi |
| Kichik farq, xato emas | 3 | 28-manba: onlayn 2011, bosma 2012 (bosma yil to'g'ri); 30, 75: jild «2» va «02» |
| Crossref'da yozuvi yo'q, DOI'siz | 3 | 71 (kichik jurnal), 74 (Krige, 1951), 102 (Rouse, 1974): muallif asl nashr bo'yicha tasdiqlashi kerak |

Matnga kiritilgan tuzatishlar:
- **DOI qo'shildi.** Avval 5 ta manbada DOI bor edi, endi 46 tasida bor (4 tasi yangi qo'shilgan manbalar). Har bir DOI Crossref yozuvi bilan solishtirilgan.
- **DOI yozilishi bir xillashtirildi:** hammasi «https://doi.org/…» ko'rinishida.
- **76-manba:** sarlavhaga tushib qolgan qism qo'shildi (« : Performance and impact factors»).
- **80-manba:** noto'g'ri tire («–-») tuzatildi.
- **95 va 103-manbalar:** sahifa o'rnidagi maqola raqami «Art.» bilan yozildi.

## 3. Qo'shilgan manbalar (shu sessiyada qo'shilgan usullar uchun)

| Manba | Qayerda keltirilgan |
| --- | --- |
| Callaway, Sant'Anna 2021, J. Econometrics 225(2) | 4.3-§, bosqichli dizaynga chidamli baho |
| Borusyak, Jaravel, Spiess 2024, Rev. Econ. Stud. 91(6) | 4.3-§, imputatsiya bahosi |
| Benjamini, Hochberg 1995, JRSS B 57(1) | 3.2-§, ko'p testlar tuzatishi |
| Moran 1950, Biometrika 37(1–2) | 3.4-§, qoldiqlardagi fazoviy avtokorrelyatsiya |

Ro'yxat 125 tadan 129 taga yetdi; Kirishdagi hajm bandi yangilandi.

## 4. Muallif to'ldirishi kerak bo'lgan joylar

Bu ma'lumotlarni o'ylab topib bo'lmaydi.

- **Murojaat sanasi yo'q:** 1-manba (PF-158) va 4-manba (PQ-250, lex.uz).
- **Kitob va hisobotlarda bet soni yo'q:** 6 (ShNQ), 8 (GOST 27.002), 14 (Духовный, Соколов), 15 (Егоров), 48 (Ernst), 112 (Skaggs), 116 (Tilekeyev), 120 (Vlotman, 2020), 123 (WMO-No. 168).
- **DOI'siz, asl nashr bo'yicha tasdiqlanishi kerak:** 71, 74, 102.
- **Rus va o'zbek tilidagi manbalar** (taxminan 70 ta) Crossref'da indekslanmagan. Ularni eLibrary yoki kutubxona katalogi bo'yicha tekshirish kerak. Bu tarmoqdan ruxsat etilmagan.

Raqamlar yakuniy, 129 ta manbali ro'yxat bo'yicha.
