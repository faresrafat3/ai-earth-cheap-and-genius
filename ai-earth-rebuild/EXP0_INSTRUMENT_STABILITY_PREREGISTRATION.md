# EXP0 — Instrument Stability Calibration

## الهدف

قبل دراسة error topology أو early prediction، يجب التأكد أن أداة إنتاج البيانات نفسها مستقرة.

السؤال:

> هل نفس task ونفس prompt ونفس model id ونفس sampling settings تنتج answer distribution مستقرة عبر جلسات مستقلة؟

إذا لم تكن answer topology مستقرة، فلا معنى لاستخدامها كـ predictor في EXP13C.

---

## الفرضية

### H0-stability

عند تثبيت:

- task
- prompt
- model id
- temperature
- k

يكون توزيع الإجابات مستقرًا بدرجة كافية عبر 3 sessions مستقلة.

---

## التصميم

- tasks: 20
  - 7 easy
  - 7 medium
  - 6 hard
- sessions: 3
- samples per task per session: k = 10
- temperature = 0.7
- model: `meta-llama/llama-3.1-8b-instruct`
- provider: OpenRouter
- policy: exploratory في هذا التشغيل الأول، مع تسجيل retries/failures

الإجمالي:

```text
20 tasks × 3 sessions × 10 samples = 600 generations
```

---

## المتغير المستقل

`session_id`

أي إعادة القياس في جلسة مستقلة.

---

## المتغيرات التابعة

لكل task × session:

- top answer
- SC answer
- SC correctness
- mode margin
- wrong-mode dominance
- answer entropy
- distinct answer count
- pairwise error agreement

ثم عبر الجلسات:

- top-answer stability
- SC-answer stability
- SC-correct stability
- mode-margin range
- entropy range
- distribution overlap

---

## شروط السماح بالانتقال إلى EXP13C

نعتبر الأداة مستقرة مبدئيًا إذا:

1. top-answer stability ≥ 80%
2. SC-correct stability ≥ 90%
3. لا توجد علاقة واضحة بين retries/failures وتغير النتائج
4. mode_margin لا يتقلب جذريًا في أغلب المهام

---

## شروط إيقاف EXP13C

إذا وجدنا:

- top answer يتغير كثيرًا بين الجلسات
- SC outcome يتقلب
- mode_margin غير مستقر
- failure regimes تظهر وتختفي بلا نمط

فلا ننتقل إلى EXP13C. ندرس instrument variance أولًا.

---

## ملاحظة مهمة

هذا التشغيل الأول سيكون calibration عمليًا عبر OpenRouter غير مثبت provider/quantization. لذلك إذا ظهر عدم استقرار، لا نعرف فورًا هل سببه الموديل أم provider/routing. لكن هذا بحد ذاته نتيجة مهمة: الأداة كما نستخدمها غير مستقرة بما يكفي.
