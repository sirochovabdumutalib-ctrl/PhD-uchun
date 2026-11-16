# IV BOB. MELIORATIV TIZIM ELEMENTLARINING ISHONCHLILIGI VA TA'MIR SAMARADORLIGI

Ushbu bobda meliorativ tizim elementlarining ishonchliligi kadastr ma'lumotlari asosida baholanadi, kollektorlarning gidravlik ko'rsatkichlari tahlil qilinadi, ta'mirning sizot sathiga ta'siri va narxi o'rganiladi hamda monitoring tizimini takomillashtirish bo'yicha tavsiyalar beriladi.

*Izoh: bu birinchi qoralama. Raqamlar `scripts/08_repair_effect.py` va `scripts/11_chapter4_analysis.py` hisoblaridan olingan. Kvadrat qavsdagi joylar qo'shimcha ma'lumot talab qiladi. Adabiyotlarga havolalar hali qo'yilmagan.*

## 4.1-§. Kollektor va zovurlarning yoshi, ta'mir tarixi va ishonchlilik ko'rsatkichlari

Tizim elementlarining ishonchliligi 2021-yil 1-yanvar holatidagi meliorativ kadastr ma'lumotlari asosida baholandi. Kadastrda har bir kollektor va ichki zovur uchun uzunligi, foydalanishga topshirilgan yili va oxirgi ta'mir yili qayd etilgan. Shu uch ko'rsatkichdan ikkita ishonchlilik ko'rsatkichi hisoblandi: elementning yoshi va oxirgi ta'mirdan beri o'tgan muddat.

**Kollektorlar.** Tumanda davlat hisobidagi 90 ta kollektor bor, umumiy uzunligi 265,8 km. Ularning yoshi 36 yildan 103 yilgacha, medianasi 61 yil. Kollektorlarning 82 foizi (uzunlik bo'yicha 90 foizi) 50 yildan eski (4.1-jadval). Eng ko'p qurilish 1950–1960-yillarga to'g'ri keladi: shu ikki o'n yillikda 61 ta kollektor (159,3 km) foydalanishga topshirilgan.

*4.1-jadval. Kollektorlarning foydalanishga topshirilgan davri bo'yicha taqsimoti*

| Davr | Kollektorlar soni | Uzunligi, km |
| --- | --- | --- |
| 1910-yillar | 1 | 12,5 |
| 1940-yillar | 10 | 65,6 |
| 1950-yillar | 31 | 90,8 |
| 1960-yillar | 30 | 68,5 |
| 1970-yillar | 15 | 22,5 |
| 1980-yillar | 3 | 6,0 |

Shu bilan birga kollektorlarning barchasi 2010–2020-yillar oralig'ida kamida bir marta ta'mirlangan. Oxirgi ta'mirdan beri o'tgan muddatning medianasi 4 yil; uzunlikning 79,5 foizi so'nggi besh yilda ta'mirlangan. Ta'mirlar vaqt bo'yicha notekis: 55 ta kollektor (124,7 km) 2016–2018-yillarda, yana 13 tasi (65,0 km) 2019-yilda ta'mirlangan. Demak kollektorlar eski bo'lsa ham, ularga yaqinda xizmat ko'rsatilgan.

&#91;image: Kollektorlarning yoshi, ta'mir yillari va ta'mir narxi\]

*4.1-rasm. Kollektorlar uzunligining foydalanishga topshirilgan davr bo'yicha (chapda) va oxirgi ta'mir yili bo'yicha (o'rtada) taqsimoti; 1 km ta'mir narxining taqsimoti (o'ngda)*

**Ichki zovurlar.** Xo'jalik ichki tarmog'ida vaziyat boshqacha. 332 ta zovurning (370,7 km) yoshi kollektorlarniki bilan bir xil, medianasi 61 yil. Biroq ularning 217 tasida (239,7 km, uzunlikning 64,7 foizi) ta'mir umuman qayd etilmagan. Qolgan 115 tasi faqat 2017–2018-yillarda ta'mirlangan.

Ta'mirsiz qolgan zovurlar ulushi tizimlar bo'yicha keskin farq qiladi (4.2-jadval): Mash'al massivida 21 foiz, Markaziy zovur tizimi va Y.Oxunboboyev massivida 100 foiz.

*4.2-jadval. Ichki zovurlarning tizimlar bo'yicha holati*

| Tizim | Zovurlar soni | Uzunligi, km | Ta'mir qayd etilmagan uzunlik ulushi |
| --- | --- | --- | --- |
| Mash'al massivi | 72 | 92,0 | 21 % |
| T.Mirzaev massivi | 36 | 30,4 | 47 % |
| U.Qoraboyev massivi | 29 | 21,9 | 72 % |
| Istiqlol massivi | 57 | 70,2 | 74 % |
| Paxtakor massivi | 33 | 41,9 | 74 % |
| Z.M.Bobur massivi | 32 | 35,2 | 82 % |
| Markaziy zovur tizimi | 54 | 52,8 | 100 % |
| Y.Oxunboboyev massivi | 12 | 20,1 | 100 % |
| Xo'jaliklararo bo'rdoqichilik bazasi | 7 | 6,1 | 100 % |

Shunday qilib tizimning ishonchliligi bo'yicha eng zaif bo'g'in kollektorlar emas, xo'jalik ichki zovurlaridir: ular umumiy ochiq tarmoq uzunligining 58 foizini tashkil etadi, uchdan ikki qismida esa ta'mir qayd etilmagan.

**Cheklov.** Kadastrda faqat oxirgi ta'mir yili yozilgan; undan oldingi ta'mirlar va nosozliklar hisobi yo'q. Shuning uchun ishonchlilik nazariyasining klassik ko'rsatkichlarini (nosozliklar oqimi, nosozliklar orasidagi o'rtacha muddat) hisoblab bo'lmaydi. «Ta'mir qayd etilmagan» degan yozuv ta'mir bo'lmaganini ham, hisobga olinmaganini ham bildirishi mumkin.

## 4.2-§. Gidravlik hisob: drenaj moduli va kollektorlarning o'tkazish qobiliyati

*Bu paragraf to'liq emas: talab etiladigan drenaj moduli va o'tkazish qobiliyati hisobi uchun qo'shimcha ma'lumot kerak (paragraf oxirida ko'rsatilgan).*

**Kadastr bo'yicha haqiqiy ko'rsatkichlar.** Kadastrda har bir kollektor uchun oxiridagi suv sarfi va xizmat ko'rsatish maydoni berilgan. Ularning nisbati kollektor bo'yicha solishtirma sarfni (drenaj moduli ko'rsatkichini) beradi:

```latex
q = \frac{1000 \, Q}{F}
```

bu yerda q — solishtirma sarf, l/s·ga; Q — kollektor oxiridagi sarf, m³/s; F — xizmat ko'rsatish maydoni, ga.

90 ta kollektor bo'yicha solishtirma sarfning medianasi 0,53 l/s·ga, o'rta yarmi 0,19–1,35 l/s·ga oralig'ida. Chetki qiymatlar orasidagi farq juda katta: 0,03 dan 50 l/s·ga gacha. 13 ta kollektorda ko'rsatkich 0,1 l/s·ga dan kichik, 5 tasida 5 l/s·ga dan katta.

Bunday tarqoqlikning ikki sababi bor. Birinchidan, yirik kollektorlar (G'arbiy Qoraqo'rg'on, O'qchi, Polvontosh) o'z maydonidan tashqari yuqoridan keladigan tranzit va tashlama suvlarni ham o'tkazadi, shuning uchun ulardagi sarfni xizmat maydoniga bo'lish drenaj modulini bermaydi. Ikkinchidan, kadastr yozuvlarining o'zida nomuvofiqliklar bor: masalan, Jo'ga kollektorining uzunligi 5,0 km, xizmat maydoni esa 4 ga deb ko'rsatilgan.

**Tarmoq zichligi.** Kollektorlarning solishtirma uzunligi medianasi 33 m/ga. Kollektorlar va ichki zovurlar birgalikda (636,5 km) kadastrdagi xizmat maydoniga (11 079 ga) nisbatan 57,5 m/ga ni tashkil etadi.

**Talab etiladigan drenaj moduli.** Uni suv balansi tenglamasidan aniqlash rejalashtirilgan:

```latex
D = O + P + F_k - ET - \Delta W, \qquad q_t = \frac{D}{8{,}64 \, T}
```

bu yerda D — hisobiy davrda drenaj orqali chiqarilishi kerak bo'lgan suv qatlami, mm; O — sug'orish suvi, P — yog'in, F\_k — kanallardan filtratsiya, ET — umumiy bug'lanish, ΔW — tuproq namligi zaxirasining o'zgarishi (hammasi mm); T — hisobiy davr, sutka; q\_t — talab etiladigan drenaj moduli, l/s·ga.

Hisobni bajarish uchun quyidagilar kerak: \[sug'orish me'yorlari va suv olish hajmlari, eng yaqin meteostansiya bo'yicha yog'in va bug'lanish, kanallarning foydali ish koeffitsiyenti\]. Talab etiladigan modul aniqlangach, u kadastrdagi haqiqiy ko'rsatkich bilan solishtiriladi.

**O'tkazish qobiliyati.** Kollektorlarning o'tkazish qobiliyatini Shezi formulasi bo'yicha tekshirish uchun \[ko'ndalang kesim o'lchamlari, tub qiyaligi va g'adir-budurlik koeffitsiyenti\] zarur. Bu ma'lumotlar kadastrda yo'q; loyiha hujjatlari olinsa, loyihaviy va loyqalangan kesim uchun sarf solishtiriladi.

## 4.3-§. Kollektor ta'mirining sizot sathiga ta'sirini baholash

3.4-§ da ko'rsatilganidek, drenaj ta'sirini bir vaqtdagi fazoviy taqqoslash orqali aniqlab bo'lmaydi. Shuning uchun ta'mir samarasi vaqt bo'yicha taqqoslash orqali baholandi: bir xil quduqda ta'mirdan oldingi va keyingi sath solishtirildi, umumiy yillik o'zgarishlar esa nazorat quduqlari yordamida chiqarib tashlandi.

**Usul.** Xaritadagi kollektor chiziqlariga kadastrdagi nom va ta'mir yili biriktirildi; bu 60 ta kollektor uchun bajarildi. Quduqlar ikki guruhga ajratildi. Ta'sir guruhi: nomi va ta'mir yili ma'lum kollektordan 300 m gacha masofadagi quduqlar (36 ta, 28 ta kollektor yonida). Nazorat guruhi: har qanday kollektordan 600 m dan uzoqdagi quduqlar (49 ta). Jami 819 ta quduq-yil kuzatuvi. Model quyidagicha:

```latex
h_{it} = \alpha_i + \gamma_t + \beta \, D_{it} + \varepsilon_{it}
```

bu yerda h — i-quduqning t-yildagi o'rtacha sathi, m; α — quduqning doimiy xususiyati; γ — yilning umumiy ta'siri; D — ta'mirdan keyingi yillar uchun 1 ga, boshqa hollarda 0 ga teng ko'rsatkich; β — ta'mir ta'siri. Musbat β sathning chuqurlashganini bildiradi. Standart xatolar quduqlar bo'yicha klasterlangan.

**Natija.** Model olti variantda baholandi (4.3-jadval).

*4.3-jadval. Kollektor ta'mirining sizot sathiga ta'siri bahosi*

| Variant | β, m | 95 % ishonch oralig'i | p | Quduq-yillar |
| --- | --- | --- | --- | --- |
| Asosiy model, yillik o'rtacha sath | −0,12 | −0,33 … +0,09 | 0,26 | 819 |
| Yozgi sath (iyul–avgust) | −0,07 | −0,27 … +0,13 | 0,50 | 803 |
| Faqat hech qachon o'zgarmas qator bermagan quduqlar | −0,20 | −0,39 … −0,02 | 0,04 | 618 |
| Faqat 2009–2016-yillar | −0,03 | −0,14 … +0,08 | 0,61 | 289 |
| Faqat 2018–2024-yillar | −0,16 | −0,44 … +0,12 | 0,27 | 530 |
| Faqat ta'mirlangan kollektor yonidagi quduqlar | +0,08 | −0,08 … +0,25 | 0,33 | 424 |

Hech bir variantda ta'mirdan keyin sath chuqurlashgani aniqlanmadi. Asosiy model bo'yicha baho −0,12 m, ishonch oralig'i nolni o'z ichiga oladi. Oraliqning yuqori chegarasi +0,09 m: ya'ni ta'mirlangan kollektor yonidagi quduqlarda nazorat quduqlariga nisbatan 0,09 m dan ortiq chuqurlashish bo'lgani ehtimoldan uzoq. Variantlar orasida ishora o'zgaradi, bu barqaror ta'sir yo'qligini bildiradi. Bitta variantdagi manfiy va ahamiyatli baho (−0,20 m) nazorat guruhining 2018-yildan keyin kuchliroq chuqurlashgani bilan bog'liq va ta'mir ta'siri sifatida talqin qilinmaydi.

**Talqin va cheklovlar.** Natija «ta'mir samarasiz» degan xulosani bermaydi. U faqat mavjud ma'lumotda mahalliy ta'sir ko'rinmasligini bildiradi. Buning to'rt sababi bo'lishi mumkin.

- Namuna kichik. Ta'sir guruhida 36 ta quduq bor; bunday namuna bilan 0,29 m dan kichik ta'sirni ishonchli aniqlab bo'lmaydi (4.5-§).
- Ta'mir ta'siri mahalliy emas, hududiy bo'lishi mumkin. Kollektorlar yagona tarmoq bo'lib ishlaydi; 2016–2018-yillarda 55 ta kollektor birdaniga ta'mirlangan. Bunday holda nazorat quduqlari ham ta'sir ostida qoladi va farq yo'qoladi. 3.2-§ da aniqlangan 0,30 m lik umumiy pog'ona aynan shu davrga to'g'ri keladi.
- 2018-yilda kuzatuv tarmog'i o'zgargan, bu ta'mirlar bilan bir vaqtga to'g'ri kelib, ikki ta'sirni ajratishni imkonsiz qiladi.
- Kadastrda faqat oxirgi ta'mir yili bor; ilgarigi ta'mirlar hisobga olinmagan, ta'mir hajmi va turi esa ko'pchilik kollektorlar uchun ko'rsatilmagan.

Asosiy xulosa: tumanda 2017–2020-yillarda ta'mirga 21,3 mlrd so'm sarflangan (4.4-§), ammo mavjud monitoring tizimi bu ishlarning meliorativ natijasini o'lchashga imkon bermaydi.

## 4.4-§. Ta'mir xarajatlari tahlili

Kadastrda 53 ta kollektor bo'yicha 2017–2020-yillardagi ta'mir xarajati va ta'mirlangan uchastka (piketlar) ko'rsatilgan. Jami 163,3 km uchastkaga 21 314 mln so'm sarflangan. Uzunlik bo'yicha tortilgan o'rtacha narx 130,5 mln so'm/km, mediana 146,0 mln so'm/km.

*4.4-jadval. Kollektorlarni ta'mirlash xarajatlari yillar bo'yicha*

| Yil | Kollektorlar soni | Ta'mirlangan uzunlik, km | Xarajat, mln so'm | O'rtacha narx, mln so'm/km |
| --- | --- | --- | --- | --- |
| 2017 | 28 | 69,0 | 9 809 | 142,3 |
| 2018 | 9 | 15,6 | 2 742 | 175,8 |
| 2019 | 13 | 65,0 | 5 127 | 78,9 |
| 2020 | 3 | 13,8 | 3 636 | 263,5 |
| Jami | 53 | 163,3 | 21 314 | 130,5 |

Narxlar ikki guruhga aniq ajraladi. 2019-yilda ta'mirlangan sakkizta kollektorda (Qushchi, Nayman, G'arbiy, ND-2-1, Sho'r qishloq, Ambarquloq, Marhamat, ND-7) narx 15–30 mln so'm/km; bu yengil tozalash ishlariga mos keladi. Qolgan 45 ta kollektorda narx asosan 95–270 mln so'm/km oralig'ida; bu mexanizmlar bilan chuqurlashtirish va tiklash ishlariga mos keladi. Ikki guruh orasidagi farq taxminan sakkiz baravar. Eng yuqori narx To'rtko'l kollektorida qayd etilgan: 671,5 mln so'm/km.

Narx kollektorning suv sarfi bilan bog'liq emas (logarifmik korrelyatsiya −0,22): kichik zovurlarni ta'mirlash 1 km hisobida yirik kollektorlarnikidan arzon chiqmagan. Qisqa kollektorlarda (0,3–0,6 km) solishtirma narx eng yuqori, bu ish hajmiga bog'liq bo'lmagan doimiy xarajatlar ulushi bilan izohlanishi mumkin.

Ikki amaliy xulosa kelib chiqadi. Birinchidan, 1 km ta'mirning haqiqiy narxi (mediana 146 mln so'm) rejalashtirish hisoblari uchun asos bo'ladi. Ikkinchidan, yengil tozalash va kapital ta'mir orasidagi sakkiz baravarlik narx farqi ta'mir turini to'g'ri tanlashni muhim qiladi; lekin qaysi tur qancha meliorativ natija berishi o'lchanmagan ekan (4.3-§), bu tanlovni asoslab bo'lmaydi.

**Cheklov.** Kadastrda ta'mir turi faqat ikki kollektor uchun yozilgan; yengil tozalash va kapital ta'mirga ajratish narx bo'yicha qilingan taxmindir. Xarajatlar joriy narxlarda, inflyatsiyaga tuzatilmagan.

## 4.5-§. Monitoring tizimini takomillashtirish va amaliy tavsiyalar

III bob va 4.1–4.4-§ natijalari bitta umumiy xulosaga olib keladi: meliorativ tizim samaradorligini ta'minlashning birinchi sharti uni o'lchay olishdir. Quyidagi tavsiyalar shu maqsadga qaratilgan; har biri tadqiqotning aniq natijasiga tayanadi (4.5-jadval).

*4.5-jadval. Amaliy tavsiyalar va ularning asosi*

| № | Tavsiya | Asos |
| --- | --- | --- |
| T-1 | Monitoring jadvallarini qabul qilishda uch tekshiruv qoidasini majburiy qo'llash: yil ichidagi o'zgarmaslik, birlik xatosi, tarmoq tarkibi | O'lchovlarning 12,1 foizi ishonchsiz (3.1-§) |
| T-2 | Quduq qurigan yoki o'lchov o'tkazilmagan hollarda qiymat o'rniga maxsus belgi qo'yish | 270 ta quduq-yilda yil bo'yi bitta qiymat (3.1-§) |
| T-3 | Kuzatuv tarmog'idagi har bir o'zgarishni (yangi quduq, chuqurlashtirish, ko'chirish) sanasi bilan qayd etish | 2018-yildagi o'zgarish tendensiyani buzgan (3.2-§) |
| T-4 | Minerallashuvni aniqlash usulini hujjatlashtirish va muntazam o'lchovlarni tiklash | Ishonchli qator faqat 2004–2010-yillar uchun mavjud (3.5-§) |
| T-5 | Kollektor va zovurlar bo'yicha ta'mir daftarini yuritish: sana, piketlar, ish turi, hajmi, xarajati | Kadastrda faqat oxirgi ta'mir yili bor (4.1, 4.3-§) |
| T-6 | Ta'mir samarasini o'lchash uchun juft quduqlar: har bir ta'mirlanadigan kollektor yonida va undan uzoqda | Ta'sir guruhida atigi 36 ta quduq (4.3-§) |
| T-7 | Yangi quduqlarni bahoning standart xatosi eng katta bo'lgan joylarga qo'yish | Noaniqlik xaritasi (3.3-§) |
| T-8 | Drenaj ishini yillik o'rtacha bo'yicha emas, yozgi eng sayoz sath bo'yicha baholash | Mavsumiy amplituda 0,48 m (3.2-§) |
| T-9 | Xo'jalik ichki zovurlarini inventarizatsiya qilish va ta'mir rejasiga kiritish | 64,7 foizida ta'mir qayd etilmagan (4.1-§) |

**Ta'mir samarasini aniqlash uchun zarur quduqlar soni.** 4.3-§ dagi modelning standart xatosi 0,105 m, ta'sir guruhida 36 ta quduq. 5 foizlik ahamiyat darajasi va 80 foizlik quvvat uchun aniqlanadigan eng kichik ta'sir standart xatoning 2,8 baravariga teng, ya'ni hozir 0,29 m. Standart xato quduqlar sonining kvadrat ildiziga teskari mutanosib deb olinsa, zarur quduqlar soni quyidagicha (4.6-jadval).

*4.6-jadval. Ta'mir ta'sirini aniqlash uchun ta'sir guruhida zarur quduqlar soni*

| Aniqlanishi kerak bo'lgan ta'sir, m | Zarur quduqlar soni | Hozirgiga nisbatan |
| --- | --- | --- |
| 0,29 | 36 | hozirgi holat |
| 0,20 | 78 | 2,2 baravar |
| 0,15 | 139 | 3,9 baravar |
| 0,10 | 312 | 8,7 baravar |

Tumanda kollektorlardan 300 m gacha masofada 108 ta quduq bor, lekin ulardan faqat 36 tasi nomi va ta'mir yili aniqlangan kollektor yonida. Demak 0,20 m lik ta'sirni aniqlash uchun yangi quduq qurish shart emas: barcha kollektorlar bo'yicha ta'mir daftarini yuritish (T-5) va xaritada kollektor nomlarini to'liq ko'rsatish yetarli bo'lishi mumkin. 0,10 m lik ta'sirni aniqlash esa mavjud tarmoq bilan imkonsiz.

Bu hisob taxminiy: u quduqlar bir-biridan mustaqil va ta'sir mahalliy degan farazga tayanadi. Ta'sir hududiy bo'lsa (4.3-§), quduqlar sonini oshirish yetarli emas; bunday holda ta'mirni bosqichma-bosqich, tumanning bir qismida oldin, boshqa qismida keyin o'tkazish va shu ikki qismni solishtirish kerak bo'ladi.

## 4.6-§. Iqtisodiy samaradorlik

*Bu paragraf to'liq emas: tavsiyalarni joriy qilish xarajatlari bo'yicha ma'lumot kerak.*

Tavsiyalarning iqtisodiy ma'nosi sarflanayotgan mablag' bilan uning natijasini o'lchash xarajati orasidagi nisbatda ko'rinadi. Tumanda birgina 2017–2020-yillarda 53 ta kollektorni ta'mirlashga 21,3 mlrd so'm, ya'ni yiliga o'rtacha 5,3 mlrd so'm sarflangan. Bu mablag'ning meliorativ natijasi o'lchanmagan.

Tavsiyalarning ko'pchiligi (T-1, T-2, T-3, T-5, T-8) qo'shimcha mablag' talab qilmaydi: ular hisobot yuritish tartibini o'zgartiradi. Tekshiruv qoidalari dasturiy ravishda amalga oshirilgan va bir tuman ma'lumotini bir necha daqiqada tekshiradi. Mablag' talab qiladigan tavsiyalar: yangi quduqlar (T-6, T-7), minerallashuvni qayta aniqlash (T-4) va ichki zovurlarni inventarizatsiya qilish (T-9). Ularning qiymati \[bitta kuzatuv qudug'ini qurish narxi, laboratoriya tahlili narxi, inventarizatsiya ishlari smetasi\] asosida hisoblanadi.

Iqtisodiy samara ikki yo'l bilan yuzaga keladi. Birinchisi — ta'mir turini asosli tanlash: yengil tozalash va kapital ta'mir narxi sakkiz baravar farq qiladi (4.4-§); qaysi biri qayerda yetarli ekani o'lchab aniqlansa, bir xil mablag' bilan ko'proq uzunlikka xizmat ko'rsatish mumkin. Ikkinchisi — noto'g'ri qarorlarning oldini olish: tekshirilmagan ma'lumot tendensiyani 1,4 baravar oshirib ko'rsatadi (3.2-§), fazoviy taqqoslash esa tarmog'i zich hududlarni «yomon» deb ko'rsatadi (3.4-§).

Samarani so'mda ifodalash uchun ta'mir turlarining haqiqiy meliorativ natijasi ma'lum bo'lishi kerak; u esa aynan taklif etilgan monitoring joriy qilingandan keyin o'lchanadi. Shuning uchun bu bosqichda iqtisodiy samaraning aniq qiymati keltirilmaydi. \[Joriy qilish dalolatnomasi olingach, shu yerda tashkilot nomi, sana va joriy etilgan natijalar ko'rsatiladi.\]

## IV bob bo'yicha xulosalar

1. Tumandagi 90 ta kollektorning (265,8 km) yoshi medianasi 61 yil; uzunlikning 90 foizi 50 yildan eski. Shu bilan birga barcha kollektorlar 2010–2020-yillarda ta'mirlangan, uzunlikning 79,5 foizi so'nggi besh yilda.
2. Tizimning eng zaif bo'g'ini xo'jalik ichki zovurlaridir: 332 ta zovurning (370,7 km) 64,7 foizida ta'mir qayd etilmagan; tizimlar bo'yicha bu ulush 21 foizdan 100 foizgacha o'zgaradi.
3. Kadastr bo'yicha kollektorlarning solishtirma sarfi medianasi 0,53 l/s·ga, ammo 0,03 dan 50 l/s·ga gacha tarqalgan. Bu tranzit suvlar ta'siri va kadastr yozuvlaridagi nomuvofiqliklar bilan izohlanadi.
4. Kollektor ta'mirining sizot sathiga mahalliy ta'siri aniqlanmadi: baho −0,12 m, 95 foizlik ishonch oralig'i −0,33 dan +0,09 m gacha. Bu ta'mir samarasizligini emas, mavjud ma'lumot bilan uni o'lchab bo'lmasligini ko'rsatadi.
5. Ta'mirning haqiqiy narxi medianasi 146 mln so'm/km. Yengil tozalash (15–30 mln so'm/km) va kapital ta'mir (95–270 mln so'm/km) orasida taxminan sakkiz baravar farq bor.
6. 2017–2020-yillarda ta'mirga 21,3 mlrd so'm sarflangan, uning meliorativ natijasi esa o'lchanmagan.
7. Monitoring tizimini takomillashtirish bo'yicha to'qqizta tavsiya ishlab chiqildi; ularning beshtasi qo'shimcha mablag' talab qilmaydi.
8. 0,20 m lik ta'mir ta'sirini ishonchli aniqlash uchun ta'sir guruhida kamida 78 ta quduq kerak (hozir 36 ta). Buning uchun birinchi navbatda barcha kollektorlar bo'yicha ta'mir daftarini yuritish zarur.
