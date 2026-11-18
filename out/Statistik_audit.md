# Statistik audit (2-band: statistical-analysis)

Skript: `scripts/51_stat_audit.py` → `results/stat_audit.json`. Avvalgi bosqichdagi tekshiruvlar: 47 (fazoviy bog'liqlik), 48 (bosqichli DiD), 49 (kritik chuqurlik), 50 (qoidalar chegaralari).

| Xulosa | Tekshiruv | Natija | Matndagi o'zgarish |
| --- | --- | --- | --- |
| Panel trendi 0,033 m/yil (3.2-§) | Sen 95 % ishonch oralig'i: yillar va quduqlar bo'yicha bootstrap | 0,022–0,046 m/yil (ikkala usulda ham) | Oraliq qo'shildi |
| Mann–Kendall p = 0,0005 | Avtokorrelyatsiya: r₁ = 0,83; Hamed–Rao, Yue–Wang tuzatishlari, pre-whitening | Hamed–Rao p = 0,0005; pre-whitening p = 0,11 | «Avtokorrelyatsiya» bandi qo'shildi; pog'ona (0,30 m, Welch p < 0,001) bilan birga ifodalanadi |
| Massivlar trendlari (7 test) | Benjamini–Hochberg | Hammasi q < 0,05 da ahamiyatli qoladi | O'zgarish shart emas |
| ρ = +0,40 / −0,47 (3.4-§) | Fisher z oralig'i, blokli bootstrap, Moran I | 0,26–0,53 va −0,59…−0,34 | Oraliq qo'shildi |
| «To'rt baravar tez» (3.4-§) | Medianalar farqi, bootstrap, Mann–Whitney | 4,7 sm/yil, 95 % oraliq 0,4–7,8; p = 0,006; r_rb = 0,46 | «To'rt baravar» taxminiy deb belgilandi, xulosalarda oraliq berildi |
| Viloyat: ρ = +0,85, +0,76 (3.6-§) | 14 ta tuman, kichik n: oraliqlar; ma'lumot sifati bo'yicha xususiy korrelyatsiya | +0,85 [0,47; 0,97]; +0,76 [0,32; 0,93]. Sifat hisobga olinganda tezlik–sath bog'lanishi ahamiyatsiz (r = 0,35; p = 0,22) | «Yozgi sath medianasi» deb aniqlashtirildi, oraliq va xususiy korrelyatsiya qo'shildi |
| Regressiya modellari (32-ilova) | Qoldiqlar normalligi, Breusch–Pagan, VIF, Kuk masofasi, log-model | Qoldiqlar o'ngga qiyshiq; 2-modelda geteroskedastiklik (HC3 ishlatilgan — to'g'ri); VIF ≤ 1,12; log-modelda qoldiqlar normal va xulosa o'zgarmaydi; ta'sirchan nuqtalarsiz ham ahamiyatli | Ilovaga diagnostika izohi qo'shildi |
| Minerallashuvda massivlar farqi (3.5-§) | Kruskal–Wallis, ε² | H = 75,6; p < 0,001; ε² = 0,68 (katta) | Qo'shildi |

**Opponent so'rashi mumkin bo'lgan ochiq nuqtalar**
- Pre-whitening testida trend ahamiyatsiz (p = 0,11). Javob: qisqa (13 yil) va pog'onali qatorda bu usul kuchni yo'qotadi; pog'ona bahosi va quduqlar bo'yicha bootstrap oralig'i mustaqil dalil.
- Viloyat bo'yicha «chuqur tumanlarda tezroq chuqurlashadi» xulosasi ma'lumot sifatidan ajratib bo'lmaydi — matnda shunday yozildi.

# Quvvat tahlili (2-band: statistical-power)

Skript: `scripts/52_did_power_sim.py` → `results/did_power_sim.json`. Usul: haqiqiy 85 ta quduq qatorlari quduqlar bo'yicha qaytariladigan tanlov bilan olinadi, "ta'sir" quduqlariga haqiqiy taqsimotdan ta'mir yili beriladi, ta'mirdan keyingi yillarga Δ qo'shiladi, asosiy model (quduq va yil qat'iy effektlari, klasterli xato, G−1 erkinlik darajasi) bilan baholanadi. Har bir variant 1 000 takror; Δ = 0 da I tur xato 0,050 (0,041–0,060) — test to'g'ri sozlangan.

| Ta'sir / nazorat | Δ = 0,10 | 0,15 | 0,20 | 0,30 |
| --- | --- | --- | --- | --- |
| 36 / 49 (hozirgi) | 0,16 | 0,31 | 0,47 | 0,82 |
| 78 / 49 | 0,25 | 0,52 | 0,75 | 0,97 |
| 100 / 49 | 0,33 | 0,59 | 0,82 | 0,99 |
| 100 / 100 | 0,33 | 0,67 | 0,87 | 0,99 |
| 150 / 100 | 0,43 | 0,78 | 0,96 | 1,00 |

**Xulosa.** Hozirgi tarmoqda aniqlanadigan eng kichik ta'sir (80 % quvvat) ≈ 0,29–0,30 m — dissertatsiyadagi baho tasdiqlandi. 0,20 m uchun ilgari yozilgan 78 ta quduq yetarli emas (quvvat 75 %); taxminan 95 ta ta'sir qudug'i (nazorat 49 ta) yoki ikki guruhda 85 tadan kerak. 0,15 m ni mavjud tarmoq miqyosida (150/100) ham 80 % quvvat bilan aniqlab bo'lmaydi. Kuzatilgan ta'sir bo'yicha "kuzatilgan quvvat" hisoblanmadi (u p-qiymatni takrorlaydi); o'rniga sezgirlik tahlili berildi.

**Cheklov.** Simulyatsiya ta'sirni mahalliy va quduqlarni mustaqil deb oladi; ta'sir hududiy bo'lsa yoki ta'sir guruhi noto'g'ri tasniflangan bo'lsa, haqiqiy quvvat bundan past.
