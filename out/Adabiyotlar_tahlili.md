# Adabiyotlar tahlili (5-band: literature-review)

## 1. Mavjud ro'yxatning qamrovi (qidiruvdan oldin)

129 ta manbaning eng so'nggi yili bo'yicha taqsimoti: 1940–1990-yillar — 60 ta, 2000-yillar — 29 ta, 2010-yillar — 18 ta, 2020-yillar — 22 ta. 2020-yillardagi 22 ta manbaning ko'pi normativ hujjatlar, usullar bo'yicha ishlar va internet resurslari. Mintaqaga oid 2020-yildan keyingi ilmiy maqolalar atigi 4 ta edi.

## 2. Qidiruv (qayta takrorlanadigan)

- Skript: `scripts/56_lit_search.py`. Manba: Crossref. Sana: 2026-11-18.
- Filtr: 2020–2026-yillar, jurnal maqolalari.
- OpenAlex so'rovlar chekloviga tushdi (429). U faqat annotatsiyalarni to'ldirish uchun ishlatildi.
- Har bir so'rov va uning natijasi `sources/lit_search_*.json` fayllarida saqlangan.

| Kod | So'rov |
| --- | --- |
| A | groundwater table depth irrigated Uzbekistan |
| B | Fergana Valley groundwater salinity irrigation |
| C | collector drainage network Central Asia performance |
| D | kriging groundwater level depth interpolation irrigated |
| E | groundwater monitoring network design optimization wells |
| F | drainage rehabilitation impact evaluation irrigation |
| G | remote sensing soil salinity Uzbekistan |
| H | GIS land reclamation assessment irrigated lands Uzbekistan |
| I | groundwater level trend Mann-Kendall irrigated |
| J | Amu Darya Syr Darya irrigation drainage water salt balance |

## 3. Saralash oqimi

| Bosqich | Soni |
| --- | --- |
| Topilgan yozuvlar (10 so'rov × 40 ta) | 400 |
| Takrorlar olib tashlangandan keyin | 390 |
| Sarlavha bo'yicha mos: mintaqa va mavzu | 65 |
| Sarlavha bo'yicha mos: usul (kriging, kuzatuv tarmog'i, drenaj ta'siri) | 61 |
| Annotatsiyasi o'qilgani | 15 |
| Kiritilgani | 8 |

Chiqarish sabablari: mavzudan tashqari (muzliklar, baliqlar, tarix); ishonchliligi past nashrlar (masalan, 10.37547 prefiksli «American Journal of …» seriyasi); annotatsiyasi topilmagani — mazmunini tekshirib bo'lmaydi (masalan, Omonov va boshq. 2024, Koriyev va boshq. 2025); usul jihatidan dissertatsiya savollariga yaqin emasligi.

Cheklov: saralashni bitta tekshiruvchi bajargan; kiritish faqat annotatsiya asosida qilingan. Matnga faqat annotatsiyada aytilgan natijalar yozildi.

## 4. Kiritilgan manbalar va ularning o'rni

| Manba | Dissertatsiyadagi o'rni | Foydalanilgan natija (annotatsiyadan) |
| --- | --- | --- |
| Pan va boshq., 2020, Water 12(10):2869 | 1.1-§, 2-ilova | Amudaryo deltasida sath 1999–2002-yillarda 1,89 m dan 3,50 m gacha pasaygan, 2017-yilgacha 2,11 m ga qaytgan; sug'orish bilan bog'liq |
| Measho va boshq., 2022, Remote Sensing 14(10):2501 | 1.1-§ | 1990–2018-yillarda Markaziy Osiyoda tuproqning elektr o'tkazuvchanligi 6,86 % ga oshgan |
| Yang va boshq., 2022, Agriculture 12(12):2167 | 1.1-§ | Yopiq drenaj sathni chuqurlashtirgan va tebranishini kamaytirgan; drenlar orasi qisqarganda ta'sir kuchaygan |
| Hamidov va boshq., 2022, Sustainability 14(14):8375 | 1.2-§ | Suv tejovchi texnologiyalarda tejamni yo'qqa chiqaruvchi «qaytish samarasi» bo'lishi mumkin |
| Cui va boshq., 2021, Environ. Model. Softw. 144:105170 | 1.3-§ | Gauss jarayonlari bahoning noaniqligini miqdoran ko'rsatadi va xavfga asoslangan qaror qabul qilishga imkon beradi |
| Teimoori va boshq., 2023, J. Hydrol. 625:130145 | 1.3-§ | Sath kuzatuv tarmoqlarini loyihalash sifat tarmoqlariga qaraganda kam o'rganilgan |
| Kulmatov va boshq., 2024, BIO Web Conf. 93:04014 | 1.3-§, 2-ilova | Xo'jayli tumanida 142 ta quduq bo'yicha sath va minerallashuv IDW usulida xaritalangan |
| Duan va boshq., 2022, Agronomy 12(8):1912 | 1.3-§, 2-ilova | Sho'rlanishni kanal va drenajgacha masofa eng ko'p tushuntiradi |

Barcha DOI va bibliografik ma'lumotlar Crossref'dan olingan (`sources/lit_selected_meta.json`).

## 5. Dissertatsiya natijalari bilan bog'lanish

**Mos keladigan natijalar:**
- Duan va boshq.: tarmoqgacha masofa meliorativ holatning asosiy omillaridan biri. Bu 3.4-§ dagi masofa bilan bog'lanishga mos.
- Teimoori va boshq.: sath kuzatuv tarmog'i kam o'rganilgan. Bu 3.3-§ va 4.5-§ dagi tarmoq to'yinishi tahlilining dolzarbligini asoslaydi.
- Cui va boshq.: noaniqlikka asoslangan xarita. Bu sayoz sath ehtimoli xaritasi g'oyasiga yaqin.

**Farqli natijalar:**
- Kulmatov va boshq. Xo'jayli tumanida iyulda sathni apreldan chuqurroq qayd etgan; Marhamat tumanida esa yozda sath eng sayoz. Bu farqning sababi (sug'orish rejimi, hududning gidrogeologik sharoiti) annotatsiyadan aniqlanmaydi, shuning uchun matnda talqin qilinmadi.
- Yang va boshq. natijasi nazorat qilinadigan dala tajribasidan olingan. Bu 4.3-§ dagi «kuzatuv ma'lumotlarida ta'sir aniqlanmadi» degan natijaga zid emas: matnda bu farq ko'rsatildi.

Ro'yxat 129 tadan 137 taga yetdi; Kirishdagi hajm bandi yangilandi.

## 6. Muallif uchun

- Kiritilgan maqolalarning to'liq matnini o'qib, keltirilgan natijalarni tasdiqlash tavsiya etiladi.
- eLibrary va CyberLeninka bazalarida rus tilidagi yangi ishlar qidirilmadi, chunki tarmoqdan ruxsat yo'q. Bunday qidiruv qamrovni yanada yaxshilaydi.
