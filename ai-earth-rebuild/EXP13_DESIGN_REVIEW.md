# EXP13 — مراجعة نهائية قبل التنفيذ

هذه مراجعة قصيرة وحاسمة لتصميم EXP13 قبل كتابة الكود. الهدف: منعنا من الوقوع مرة أخرى في forking paths أو تجربة واسعة غير قابلة للتفسير.

---

## 1. هل الفرضية جيدة؟

### الفرضية

> نجاح Self-Consistency يمكن التنبؤ به من بنية توزيع الإجابات، خصوصًا `mode_margin` و `wrong_mode_dominance`.

### الحكم

✅ جيدة لأنها:

- محددة.
- قابلة للدحض.
- لا تعتمد على تفسير “استدلال” داخلي.
- تختبر المتغير الكامن الأهم: error topology.
- تضرب جذر السؤال: متى يكفي التصويت ومتى يفشل؟

### الصياغة النهائية قبل التنفيذ

نثبتها هكذا:

> على arithmetic-chain tasks، ومع k=10 عينات لكل مسألة، تكون احتمالية نجاح SC أعلى بوضوح عندما يكون `mode_margin > 0` مقارنةً بـ `mode_margin <= 0`.

---

## 2. هل n=120 مناسب؟

### التصميم المقترح

- 120 مهمة.
- 40 easy.
- 40 medium.
- 40 hard.
- k=10 عينات لكل مهمة.
- 3 درجات temperature.

### المشكلة

لو طبقنا 120 × 10 × 3 temperatures = 3600 generation.

ده كثير لو على موديل حقيقي، لكنه مناسب لمحاكاة أو local/cheap model.

### القرار

نقسم التنفيذ إلى مرحلتين:

#### Phase A — Offline/Simulation Dry Run

- n=120.
- k=10.
- temperatures = 0.2, 0.7, 1.0.
- الهدف: اختبار الكود، metrics، والتحليل.

#### Phase B — Real Model Pilot

- n=45.
- 15 easy / 15 medium / 15 hard.
- k=10.
- temperature واحدة أولًا: 0.7.
- الهدف: قياس هل الظاهرة تظهر على موديل حقيقي بتكلفة قليلة.

بعد Phase B فقط نقرر هل نوسع إلى درجات temperature متعددة.

---

## 3. هل k=10 مناسب؟

### الحكم

✅ مناسب كحد أدنى.

أسباب:

- يسمح بقياس mode structure.
- يكشف wrong mode مكرر.
- ليس مكلفًا جدًا.

### القيد

k=10 قد لا يكفي لتقدير entropy بدقة عالية، لكنه كافٍ لاختبار `mode_margin` أوليًا.

### القرار

نثبت k=10 ولا نغيره بعد رؤية النتائج.

---

## 4. هل مستويات الصعوبة 5/8/11 مناسبة؟

### الحكم

✅ مناسبة كبداية.

لأن تجاربنا السابقة أظهرت:

- 4–5 خطوات: قد تكون سهلة جدًا.
- 7–8 خطوات: منطقة وسطى.
- 11 خطوة: أصعب وتظهر فشلًا أكثر.

### الخطر

لو easy كلها 100%، لن تفيد في اختبار الفرضية.

### القرار

نحتفظ بها لأن وجود ceiling في easy ليس مشكلة إذا medium/hard ينتجان failures.

---

## 5. هل temperatures الثلاثة مناسبة؟

### 0.2

تقيس collapse / low diversity.

### 0.7

تقيس الإعداد العملي الشائع لـ SC.

### 1.0

تقيس high diversity وربما انخفاض Q.

### القرار

في المحاكاة أو dry run: نستخدم الثلاثة.

في real pilot: نبدأ بـ 0.7 فقط لتقليل التكلفة، ثم نوسع لاحقًا.

---

## 6. ما الذي يجب ألا نغيره بعد التشغيل؟

بعد بدء Phase B ممنوع تغيير:

- n.
- k.
- prompt.
- parser.
- difficulty split.
- success criteria.
- primary metrics.

أي تغيير بعد التشغيل يُسجل كـ exploratory ولا يدخل في النتيجة الأساسية.

---

## 7. المقاييس الأساسية المثبتة

### Primary metrics

1. `SC_correct` حسب `mode_margin` bins:
   - margin > 0
   - margin = 0
   - margin < 0

2. `SC_gain = SC_accuracy - single_sample_accuracy`

3. `wrong_mode_dominance`

### Secondary metrics

4. `answer_entropy`
5. `distinct_answer_count`
6. `pairwise_error_agreement`
7. cost/correct في real run

---

## 8. شروط دعم الفرضية

تُعتبر الفرضية مدعومة إذا:

1. SC accuracy عند `mode_margin > 0` أعلى بوضوح من `mode_margin <= 0`.
2. أغلب فشل SC يقع في حالات:
   - no correct samples.
   - correct not plurality.
   - largest wrong mode >= correct count.
3. `wrong_mode_dominance` يرتبط سلبيًا بمكسب SC.

لا نشترط p-value قوي في pilot الصغير. نطلب pattern واضح.

---

## 9. شروط دحض الفرضية

تضعف الفرضية أو تُدحض إذا:

1. `mode_margin` لا يميز نجاح SC من فشله.
2. SC يفشل رغم margin موجب في كثير من الحالات.
3. SC ينجح رغم margin سالب في كثير من الحالات بسبب parser أو tie-breaking أو عامل آخر.
4. أغلب failures سببها parsing لا error topology.

---

## 10. قرار التنفيذ النهائي

ننفذ EXP13 على مرحلتين:

### Phase A — بناء الكود + محاكاة

الهدف:

- التأكد أن logging صحيح.
- التأكد أن metrics صحيحة.
- إنتاج تقرير sample.

### Phase B — Real pilot صغير

الهدف:

- اختبار أولي على LLM حقيقي.
- لا تعميم.
- فقط نرى هل mode-margin signal يظهر.

---

## 11. النتيجة المطلوبة من التنفيذ

ليس المطلوب أن نثبت قانونًا عامًا.

المطلوب فقط:

> هل error topology يعطي signal مفيدًا كفاية ليستحق أن يكون أساس AI Earth الجديد؟

إذا نعم، ننتقل من مقارنة التقنيات إلى بناء **diagnostic layer**.

إذا لا، نبحث عن متغير كامن آخر.
