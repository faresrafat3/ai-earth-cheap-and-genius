# EXP13C — Early Topology Prediction Preregistration

## لماذا EXP13C؟

EXP13 أظهر أن `mode_margin` بعد k=10 يصف نجاح SC، لكنه كان diagnostic لا predictive.

EXP0 أظهر أن answer topology مستقرة مبدئيًا عبر sessions.

لذلك التجربة الحتمية الآن:

> هل topology محسوبة من أول k0=3 عينات تتنبأ بنتيجة SC@10؟

---

## الفرضية

### H1C

> مؤشرات topology المبكرة من أول 3 عينات — خصوصًا early top-answer dominance وearly entropy وearly distinct count — تتنبأ بنجاح أو فشل SC عند k=10.

---

## التصميم

- tasks: 20 نفس حجم EXP0 كبداية مضبوطة.
- k0 = 3 عينات مبكرة.
- k = 10 عينات كاملة.
- temperature = 0.7.
- model = `meta-llama/llama-3.1-8b-instruct`.
- provider = OpenRouter.
- policy = exploratory في هذا pilot، مع تسجيل retries/failures.

---

## المتغيرات المستقلة المبكرة

محسوبة من أول 3 عينات فقط:

1. `early_top_dominance = count(top_answer_at_3) / 3`
2. `early_distinct_count`
3. `early_entropy`
4. `early_unanimous` هل أول 3 عينات متطابقة؟
5. `early_parse_failure_count`

اختياري diagnostic فقط، وليس predictor عملي:

6. `early_correct_count` لأن ground truth معروف لنا في التحليل، لكنه ليس متاحًا في deployment.

---

## المتغير التابع

بعد k=10:

- `SC10_correct`
- `SC10_answer`
- `full_mode_margin`
- `full_wrong_mode_dominance`

---

## ما الذي يدعم الفرضية؟

الفرضية تُدعم إذا:

1. early unanimous / high dominance يتنبأ بثبات SC@10.
2. early entropy العالي أو early distinct count العالي يرتبط بانخفاض استقرار SC أو زيادة failure.
3. predictor عملي بدون ground truth يميز على الأقل بين high-confidence وrisky cases.

---

## ما الذي يدحض الفرضية؟

تضعف الفرضية إذا:

1. early topology لا يميز SC@10 إطلاقًا.
2. أول 3 عينات مضللة كثيرًا.
3. SC@10 يتغير بشكل لا يمكن توقعه من early distribution.
4. كل signal يحتاج ground truth، فيفقد القيمة العملية.

---

## ملاحظة مهمة

إذا كانت كل المهام سهلة جدًا وSC@10 ينجح تقريبًا دائمًا، فلن تختبر التجربة الفرضية جيدًا.

في هذه الحالة، النتيجة ليست فشلًا للفرضية، بل تقول إن task set غير كافٍ، ونحتاج نسخة borderline-balanced لاحقًا.

---

## Success criteria في pilot

بما أن هذه نسخة pilot، لا نطلب p-value.

نطلب:

- وجود حالات SC failure أو at least risky cases.
- early topology يميزها نوعيًا.
- أو يثبت أن المهمة سهلة جدًا ويجب بناء EXP13C-Balanced.

---

## القرار بعد التجربة

### إذا early topology مفيد

نبني policy:

> إذا early topology عالي الثقة، لا تكمل k=10. إذا risky، كمل SC أو استخدم verifier.

### إذا غير مفيد

نستنتج أن topology لا تصبح عملية إلا بعد تكلفة أكبر، ونبحث عن predictors أخرى مثل:

- logprobs.
- confidence.
- task features.
- symbolic difficulty features.
