# EXP13 — تحليل المتغير الثالث الخفي

## السؤال

افترض أن النتيجة التي رأيناها في EXP13 Phase B لم تكن بسبب `mode_margin` أو `wrong_mode_dominance`، بل بسبب متغير ثالث خفي.

ما أرجح هذا المتغير؟ وكيف نختبره في التجربة القادمة؟

---

# 1. النتيجة التي نريد تفسيرها

في Phase B:

- single accuracy = 90.2%
- SC accuracy = 97.8%
- 44/45 tasks كان فيها `mode_margin > 0`
- فشل واحد فقط، وكان wrong mode كامل

التفسير السطحي:

> mode_margin يفسر نجاح SC.

لكن هذا قد يخفي متغيرًا أعمق.

---

# 2. أرجح متغير خفي: سهولة المهمة بالنسبة للموديل

## المتغير الخفي المقترح

> **Model-relative task difficulty**

أي: مدى سهولة المهمة بالنسبة للموديل المحدد والـ prompt المحدد.

ليس “عدد الخطوات” فقط، بل صعوبة المهمة كما يراها الموديل فعليًا.

## لماذا هو الأرجح؟

لأن معظم المهام كانت سهلة جدًا للموديل:

- single accuracy = 90.2%
- easy = 99.3%
- medium = 84.7%
- hard = 86.7%

حتى “hard” لم يكن أصعب من medium فعليًا.

هذا يعني أن النموذج كان غالبًا يعرف الإجابة من البداية، وبالتالي:

- correct_count عالي.
- mode_margin موجب.
- SC ينجح.

بالتالي `mode_margin` قد لا يكون سببًا مستقلًا، بل **عرضًا** لسهولة المهمة.

---

# 3. النموذج السببي البديل

بدل:

```text
mode_margin → SC_success
```

قد يكون الواقع:

```text
model-relative task difficulty → single accuracy
model-relative task difficulty → mode_margin
model-relative task difficulty → SC_success
```

أي أن difficulty الخفية تسبب الثلاثة معًا.

`mode_margin` هنا ليس سببًا، بل مؤشر بعدي على أن المهمة كانت سهلة.

---

# 4. لماذا عدد الخطوات ليس كافيًا كمقياس صعوبة؟

كنا نظن:

- 5 steps = easy
- 8 steps = medium
- 11 steps = hard

لكن النتائج:

| difficulty | single accuracy |
|---|---:|
| easy | 99.3% |
| medium | 84.7% |
| hard | 86.7% |

hard كان أعلى من medium. إذن steps وحدها لا تقيس الصعوبة الحقيقية.

قد تكون الصعوبة الفعلية متأثرة بـ:

- عدد عمليات الضرب.
- موضع عملية الضرب.
- حجم الناتج النهائي.
- وجود أرقام سالبة.
- طول الناتج.
- تشابه الإجابات الخاطئة.
- قدرة الموديل على اتباع left-to-right.
- صياغة prompt.

---

# 5. متغيرات خفية بديلة أقل احتمالًا

## 5.1 Prompt clarity

ربما prompt كان واضحًا جدًا، فرفع الأداء العام وخنق الفشل.

كيف يفسر النتيجة؟

- prompt واضح → single accuracy عالية → margin موجب → SC ينجح.

## 5.2 Answer scale / magnitude

المهام التي تنتج أعدادًا صغيرة أو أنماطًا سهلة قد تكون أسهل.

## 5.3 Operation composition

ليست كل 11 خطوة متساوية. 11 خطوة أغلبها جمع/طرح أسهل من 8 خطوات فيها ضربات حرجة.

## 5.4 Provider/model variant

قد يكون backend المستخدم أقوى أو quantization أفضل من المتوقع.

## 5.5 Sampling collapse

ربما temperature فعليًا لم يعط تنوعًا كافيًا، فالعينات كانت متشابهة بسبب انخفاض entropy، لا لأن correct mode قوي معرفيًا.

لكن هذه أقل شمولًا من model-relative difficulty.

---

# 6. كيف نختبر وجود المتغير الخفي في التجربة القادمة؟

## الفكرة

نحتاج فصل أثر difficulty عن أثر mode_margin.

أي نسأل:

> عندما نثبت مستوى الصعوبة الفعلي، هل يبقى mode_margin قادرًا على تفسير SC_success؟

أو:

> هل mode_margin يضيف معلومات فوق single-sample accuracy؟

---

# 7. تجربة مقترحة: EXP13D — Difficulty-Controlled Error Topology

## 7.1 المرحلة الأولى: تقدير الصعوبة

لكل task، نأخذ عينة صغيرة أولية `k0 = 3`.

نحسب:

- early single accuracy estimate إذا كان ground truth معروفًا في التحليل.
- early agreement.
- answer entropy.
- output length.
- maybe model confidence/logprob إن توفر.

ثم نصنف المهام إلى bins حسب صعوبة فعلية:

- easy-for-model
- borderline
- hard-for-model

الأهم: التصنيف يكون قبل استخدام العينات 4–10.

---

## 7.2 المرحلة الثانية: اختبار SC الكامل

نأخذ العينات 4–10 ونحسب SC@10.

ثم نختبر داخل كل difficulty bin:

- هل mode_margin ما زال يميز نجاح SC؟
- هل wrong_mode_dominance ما زال يفسر الفشل؟

---

# 8. اختبار إحصائي أبسط

حتى بدون نموذج معقد، نستخدم regression أو stratified table:

```text
SC_success ~ early_difficulty + mode_margin
```

لكن انتبه:

- إذا mode_margin محسوب من كل k=10، فهو لا يزال diagnostic.
- الأفضل استخدام early predictors فقط.

صيغة أفضل:

```text
SC@10_success ~ early_entropy + early_agreement + early_difficulty
```

ثم نرى هل early topology يتنبأ بـ SC@10.

---

# 9. اختبار عملي مباشر للمتغير الخفي

## التصميم

نولد مهام كثيرة، ثم لا نختارها عشوائيًا فقط. نعمل pre-screening:

1. شغّل 3 عينات لكل task.
2. صنّف task حسب early difficulty:
   - all 3 correct = too easy
   - 1–2 correct = borderline
   - 0 correct = hard
3. اختر عينة متوازنة:
   - 30 too easy
   - 30 borderline
   - 30 hard
4. ثم شغل k=10 على هذه المهام.

## ماذا يختبر؟

إذا كانت النتيجة السابقة سببها السهولة، فبعد balancing ستظهر حالات margin سالب/صفر أكثر.

إذا ظل mode topology يفصل النجاح والفشل داخل كل bin، فالفرضية أقوى.

---

# 10. كيف نعرف أن المتغير الخفي كان هو السبب؟

## دليل لصالح hidden difficulty confound

لو وجدنا:

- أغلب نجاح SC يحدث في easy-for-model فقط.
- داخل borderline/hard، mode_margin لا يضيف تفسيرًا.
- early single accuracy وحدها تتنبأ بكل شيء.

فهذا يعني أن `mode_margin` كان مجرد proxy لصعوبة المهمة.

## دليل ضد hidden difficulty confound

لو وجدنا:

- داخل نفس difficulty bin، اختلاف mode topology يغير SC_success.
- tasks بنفس early accuracy لكن wrong-mode dominance مختلف تعطي نتائج SC مختلفة.

فهذا يعني أن error topology تضيف معلومات فوق difficulty.

---

# 11. الخلاصة

أرجح متغير خفي هو:

> **سهولة المهمة بالنسبة للموديل والـ prompt**.

وليس عدد الخطوات، بل difficulty فعلية كما تظهر في أداء العينة الواحدة.

التجربة القادمة يجب أن تختبر:

> هل error topology يضيف تفسيرًا فوق model-relative difficulty؟

إذا نعم، ففكرة error topology قوية.

إذا لا، فـ mode_margin ليس إلا proxy لصعوبة المهمة.

---

# 12. القرار المنهجي

لا ننتقل مباشرة إلى EXP13B الأصعب فقط.

الأدق:

> EXP13D يجب أن يوازن المهام حسب difficulty الفعلية أولًا، ثم يختبر topology داخل كل bin.

بهذا نعزل المتغير الخفي بدل أن نضيف صعوبة عشوائيًا.
