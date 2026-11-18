# Farazlar va raqib izohlar (6-band: hypothesis-generation)

Bu hujjat dissertatsiyaning asosiy kuzatishlarini va ularning raqib izohlarini ajratadi. Barcha farazlar ma'lumotlar ko'rilgandan **keyin** shakllantirilgan, ya'ni ular tadqiqot natijasi emas, keyingi tekshiruv uchun nomzodlardir. Mavjud ma'lumotda bajarilgan tekshiruvlar: `scripts/57_hypothesis_checks.py` → `results/hypothesis_checks.json`.

## 1. Kuzatishlar (talqinsiz)

| Kod | Kuzatish | Manba |
| --- | --- | --- |
| K1 | Barqaror panelda sath 2009–2016-yillarda o'rtacha 1,63 m, 2018–2024-yillarda 1,92 m; pog'ona 2016-yildan keyin | 3.2-§ |
| K2 | Kollektorga yaqin va tarmoq zich joyda sath sayozroq (ρ = +0,40 / −0,47) | 3.4-§ |
| K3 | Z.M.Bobur massivida sath ko'tarilgan (yiliga −0,031 m), boshqa massivlarda chuqurlashgan | 3.2-§ |
| K4 | 270 ta quduq-yilda yil bo'yi bir xil qiymat yozilgan | 3.1-§ |
| K5 | Ta'mirdan keyin kollektor yaqinida sath nazoratga nisbatan chuqurlashmagan (−0,12 m; −0,33 … +0,09) | 4.3-§ |

## 2. Raqib izohlar va ajratuvchi bashoratlar

To'liq jadval dissertatsiyaning 52-ilovasida. Bu yerda faqat bajarilgan tekshiruvlar keltirilgan.

**K4 — o'zgarmas qatorlar.**
- **Izoh A:** quruq quduqda shartli qiymat yoziladi.
- **Izoh B:** kuzatuvchining hisobot amaliyoti.
- **Ajratuvchi bashorat:** A to'g'ri bo'lsa, o'zgarmas qator quduq tubigacha zaxira kichik bo'lganda to'planadi; B to'g'ri bo'lsa, zaxiraga bog'liq bo'lmaydi.
- **Natija** (1 924 ta quduq-yil): zaxira 0,5 m dan kam bo'lganda 44 % qator o'zgarmas, 1,5–2,0 m bo'lganda 2 %. Har 1 m zaxirada imkoniyatlar nisbati (OR) 0,31 (p < 0,001), massiv omili bilan 0,41. O'zgarmas qiymat quduq tubidan mediana bo'yicha 0,25 m yuqori.
- **Xulosa:** A izohi qo'llab-quvvatlanadi. Zaxirasi 2 m dan katta quduqlarda ham 9 % o'zgarmas qator bor, demak B qisman ta'sir qiladi.
- **Dissertatsiyada:** natija 3.1-§ ga qo'shildi.

**K3 — Z.M.Bobur.**
- **Izoh A:** drenaj quvvati yetishmaydi.
- **Raqib izohlar:** yer foydalanish o'zgargan yoki tarmoq tarkibi o'zgargan.
- **Bashorat:** A to'g'ri bo'lsa, ko'tarilish sug'orish mavsumida (yozda) kuchliroq bo'ladi.
- **Natija** (26 ta quduq, 2009–2018 va 2019–2024): qishda −0,16 m (−0,49 … +0,17), yozda −0,07 m (−0,29 … +0,15). Taqqoslash uchun boshqa massivlarda qishda +0,41 m, yozda +0,26 m.
- **Xulosa:** natija noaniq va A izohini tasdiqlamaydi. Tarmoq tarkibi izohi qisman istisno qilingan, chunki barqaror panelda ham ko'tarilish ahamiyatli. Yer foydalanish izohi tekshirilmagan.

**K1 — pog'ona.**
- **Raqib izohlar:** suv ta'minoti, ta'mir, o'lchash tartibi, iqlim.
- **Holat:**
  - ta'mir izohiga qarshi ikki dalil bor (3.4-§, 4.3-§), lekin ta'sirni aniqlash quvvati past;
  - suv ta'minoti va iqlim izohlarini yillik qatorlarsiz tekshirib bo'lmaydi (loyihada faqat ko'p yillik oylik normalar bor);
  - o'lchash tartibi izohini barqaror panel to'liq istisno qilmaydi.

**K2 — kollektor yaqinida sayoz sath.** Teskari bog'liqlik izohi qurilishgacha bo'lgan ma'lumotlarsiz bevosita tekshirilmaydi. Hozircha u dalillarga zid emas: bog'lanish massiv ichida saqlanadi va relyef ta'siri kuchsiz.

## 3. Tekshiruv rejasi (kelajak uchun)

| Faraz | Zarur ma'lumot | Usul | Natijani tasdiqlamaydigan holat |
| --- | --- | --- | --- |
| K1-A (suv ta'minoti) | 2009–2024-yillar kanallar suv olish hajmi (BTIB) | Yillik sath o'zgarishining suv olish bilan regressiyasi, tumanlar paneli | Suv olish kamaymagan yillarda ham pog'ona |
| K1-D (iqlim) | 2009–2024-yillar Andijon meteostansiyasi | Yog'in va ET₀ anomaliyalari bilan solishtirish | Anomaliya 2016–2018-yillarga to'g'ri kelmasa |
| K3-A (drenaj) | Massiv kollektorlarining oxiridagi sarf, o'zan ko'rigi | Sarf va talab etiladigan modul solishtiruvi | Sarf talabni qoplasa |
| K3-B (yer foydalanish) | Sentinel-2 / Landsat, 2015–2024 | Sug'oriladigan maydon va o'simlik indekslari dinamikasi | Maydon va ekin tarkibi o'zgarmagan bo'lsa |
| K5 (ta'mir) | Ta'mir daftari, juft quduqlar | Bosqichli DiD, quvvat ≥ 0,8 uchun ≈ 95 ta ta'sir qudug'i | — |

Tekshiruvlar oldindan ro'yxatdan o'tkazilishi va ma'lumot ko'rilgunga qadar qayd etilishi tavsiya etiladi.

## 4. Dissertatsiyadagi o'zgarishlar

- **3.1-§:** o'zgarmas qatorlar bo'yicha raqib izohlar tekshiruvi qo'shildi.
- **52-ilova** (yangi): kuzatishlar, raqib izohlar, ajratuvchi bashoratlar va ularning holati jadvali.
- **Umumiy xulosalardagi «Tadqiqotni davom ettirish yo'nalishlari»** farazlar asosida qayta yozildi.
- **Kirish:** ilovalar soni 52 ga yangilandi.
