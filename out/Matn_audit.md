# Matn auditi (3-band: scientific-writing)

## 1. Raqamlarning manbaga bog'langanligi

`scripts/53_text_consistency.py` Kirish, bob xulosalari va Umumiy xulosalardagi har bir raqamni bob matni va ilovalar bilan solishtiradi (natija: `results/text_consistency.json`).

- Umumiy xulosalar va to'rtta bob xulosasi: bob matnida uchramaydigan raqam yo'q.
- Kirish: 2 ta raqam bob matnida takrorlanmaydi. Ikkalasi ham tashqi manbaga tegishli: FIK 0,63 dan 0,73 ga (davlat konsepsiyasi) va adabiyot raqami [131]. Bu to'g'ri holat.

`scripts/54_key_facts.py` 19 ta asosiy faktning matndagi barcha takrorlarini topib, ularni bir-biri va `results/*.json` bilan solishtiradi (natija: `results/key_facts.json`). Ko'rib chiqilgan ogohlantirishlar:

| Holat | Xulosa |
| --- | --- |
| 2-bobda 19 %, 3.3-§ da 23 % (yozda 1,5 m dan sayoz quduqlar) | Turli sanalar: 2024-yil 1-aprel va 2019–2024-yillarning iyul–avgusti. Ziddiyat emas. |
| 3.6-§ da 21,9 %, 3.3-§ da 23 % | Viloyat jadvallari 2019–2023-yillar bo'yicha. **Davr matnga qo'shildi.** |
| 68 va 90 ta kollektor | 68 tasi — 2016–2019-yillarda ta'mirlanganlar. Ziddiyat emas. |
| Sen 0,033 va 0,031 | Biri yillik, ikkinchisi yozgi qator. Ziddiyat emas. |
| Qolgan 15 ta fakt | Barcha takrorlar bir xil va manbaga mos. |

## 2. Atamalar va nomlar

- Massiv nomlari bir xilga keltirildi: «T.Mirzayev» (avval 28 joyda «T.Mirzaev»), «M.To'jiboyev» (avval 6 joyda «M.Tojiboyev»).
- Asosiy atamalar bir xil ishlatilgan: «sizot suvi sathi», «kollektor-drenaj», «minerallashuv», «kuzatuv quduqlari».
- Majburiy neytral ibora («mustaqil kuzatuv ma'lumotlari mavjud emas») saqlangan.

## 3. OAK tuzilmasi va Kirishning muvofiqligi

- Kirishdagi barcha bandlar o'rnida. «Natijalarning joriy qilinishi» bandi qoidaga ko'ra yo'q.
- Har bir vazifa bobda yoritilgan va Umumiy xulosalarda aks etgan (quyidagi jadval).
- Kirish taqriz va audit natijalariga moslashtirildi:
  - 22–44 % tejash stsenariy sharti bilan yozildi;
  - ilmiy yangilikka bosqichli dizaynga chidamli baholar qo'shildi;
  - «Ishonchliligi» bandiga fazoviy bog'liqlik, kritik chuqurlik va tekshiruv chegaralari bo'yicha sezgirlik qo'shildi.
- Kirishdagi hali bo'sh joylar: aprobatsiya va nashrlar soni. Ularni muallif to'ldiradi.

## 4. Dalillar xaritasi: Umumiy xulosalar

| Xulosa | Paragraf | Skript | Natija fayli |
| --- | --- | --- | --- |
| 1 | 1-bob | — (adabiyot tahlili) | — |
| 2 | 2.3-§ | 03–05, 07, 12 | gis/, data/collectors.csv |
| 3 | 3.1-§, 3.6-§, 2.4-§ | 16, 21–22, 50 | ch3_audit_ext.json, ch3_region.json, rule_sensitivity.json |
| 4 | 3.2-§, 3.6-§ | 10, 17, 51 | ch3_dyn_ext.json, stat_audit.json |
| 5 | 3.2-§ | 17 | ch3_dyn_ext.json |
| 6 | 3.3-§ | 18, 41–42, 49 | ch3_geo_ext.json, critical_depth_sensitivity.json |
| 7 | 3.4-§ | 19, 47, 51 | ch3_net_ext.json, spatial_robustness.json, stat_audit.json |
| 8 | 3.5-§ | 09, 20, 33 | ch3_miner_ext.json |
| 9 | 4.1-§ | 11, 23, 34 | ch4.json, ch4_rel_ext.json |
| 10 | 4.2-§ | 14, 24, 35 | ch4_hydraulic.json, ch4_drainage_modulus.csv |
| 11 | 4.3-§, 4.5-§ | 08, 25, 48, 52 | ch4_repair_ext.json, did_staggered.json, did_power_sim.json |
| 12 | 4.4-§, 4.6-§ | 26, 36, 37 | ch4_cost_ext.json, cost_2026.json |
| 13 | 4.5-§ | 38 | (qoidasi 4.5-§ matnida) |
| 14 | 4.5-§, 52-ilova | — | — |

## 5. Muallif tasdiqlashi kerak bo'lgan joylar

Bu ishlarni avtomatik bajarib bo'lmaydi.

- Adabiyotlar ro'yxatidagi har bir manbaning bibliografik ma'lumoti va matndagi havola mazmuni. Bu 4-band (citation-management) da tekshiriladi.
- Kirishdagi aprobatsiya va nashrlar soni.
- Davlat dasturi va konsepsiyadagi raqamlarning rasmiy manbasi, masalan FIK 0,63 → 0,73.
