# EXP13C-Balanced — Preregistration

## لماذا هذه التجربة؟

EXP13C أظهر إشارة واعدة لكن العينة كانت مشبعة:

- 18 early-unanimous
- 2 early-split
- 0 early-scattered

لذلك لم نختبر early topology بقوة.

EXP13C-Balanced لا يترك توزيع early topology للصدفة. بل يصنع pool، يفرز المهام حسب أول 3 عينات، ثم يختار عينة متوازنة قدر الإمكان.

---

## السؤال

> هل early topology من أول k0=3 عينات تتنبأ بـ SC@10 عندما تكون العينة متوازنة بين early-unanimous وearly-split وearly-scattered؟

---

## الفرضية

### H1C-balanced

> المهام ذات early topology أقل استقرارًا — early-split أو early-scattered — سيكون لديها احتمال فشل SC@10 أعلى من early-unanimous.

---

## التصميم

### المرحلة 1 — Pre-screening

- نولّد pool من المهام.
- لكل task نأخذ k0=3 عينات.
- نصنف:
  - `early-unanimous`: الثلاث عينات نفس الإجابة.
  - `early-split-2`: إجابتان مميزتان بين الثلاث.
  - `early-scattered-3`: ثلاث إجابات مختلفة.

### المرحلة 2 — Balanced selection

نختار حتى `target_per_bin` من كل bin.

إذا لم نستطع ملء bin معين، نسجل ذلك كـ result مهم وليس فشل تشغيل.

### المرحلة 3 — Complete to k=10

للمهام المختارة فقط:

- نستخدم أول 3 عينات الموجودة.
- نأخذ 7 عينات إضافية.
- نحسب SC@10.

---

## الإعدادات

- model: `meta-llama/llama-3.1-8b-instruct`
- temperature: 0.7
- k0 = 3
- k = 10
- target_per_bin = 10
- max_pool = 150 tasks
- difficulty steps sampled from: 8, 11, 14, 17

استخدام صعوبات أعلى مقصود لأن EXP13C السابق كان سهلًا ومشبعًا.

---

## ما يؤكد الفرضية؟

- SC@10 في early-unanimous أعلى من early-split/early-scattered.
- معظم failures تأتي من split/scattered.
- early top answer wrong أو instability تظهر قبل الفشل.

---

## ما يضعفها؟

- early-split/scattered لا يزيدان خطر الفشل.
- early-unanimous يفشل كثيرًا.
- SC@10 ينجح بالتساوي في كل bins.
- أو لا نستطيع إنتاج split/scattered حتى بعد max_pool، مما يعني أن هذا model/task/prompt regime شديد الاستقرار.

---

## الحكم المتوقع

هذه تجربة pilot-balanced، وليست confirmatory نهائية بسبب:

- OpenRouter provider/quantization غير مثبتين.
- policy exploratory.
- pool selection مبني على pre-screening.

لكنها تكسر saturation الذي ظهر في EXP13C.
