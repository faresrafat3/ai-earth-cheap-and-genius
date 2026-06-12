# EXP13 — Preregistration: هل بنية الأخطاء تتنبأ بنجاح Self-Consistency؟

## 0. الفكرة الأساسية

بعد كل التدقيق السابق، لم تعد الفكرة الأساسية هي: “أي تقنية أفضل؟”

الفكرة الأساسية الجديدة:

> أداء تقنيات مثل Self-Consistency لا يُفهم من اسم التقنية، بل من بنية الأخطاء: تنوع الإجابات، ترابط الأخطاء، وجود wrong mode مسيطر، والهامش بين الإجابة الصحيحة وأقوى إجابة خاطئة.

هذه التجربة تختبر هذه الفكرة مباشرة.

---

# 1. الفرضية المحددة القابلة للدحض

## H1 — الفرضية الأساسية

> مكسب Self-Consistency فوق العينة الواحدة يمكن التنبؤ به من **mode margin** و **wrong-mode dominance**.

حيث:

- `correct_count`: عدد العينات التي أعطت الإجابة الصحيحة ضمن k عينات.
- `largest_wrong_count`: أكبر عدد تكرار لإجابة خاطئة واحدة.
- `mode_margin = correct_count - largest_wrong_count`.
- `wrong_mode_dominance = largest_wrong_count / k`.

## الصياغة القابلة للدحض

إذا كان `mode_margin > 0` في أغلب المسائل، يجب أن ينجح Self-Consistency.

إذا كان `mode_margin <= 0` في نسبة كبيرة من المسائل، يجب أن يفشل Self-Consistency أو يقل مكسبه.

## الفرضية الكمية

على مستوى المسألة الواحدة:

> احتمال أن تكون إجابة SC صحيحة سيكون أعلى بكثير عندما يكون `mode_margin > 0` مقارنةً عندما يكون `mode_margin <= 0`.

وعلى مستوى توزيع المهام:

> مكسب SC = SC_accuracy - single_sample_accuracy يرتبط إيجابيًا بمتوسط `mode_margin` وسلبيًا بـ `wrong_mode_dominance`.

---

# 2. تصميم التجربة

## 2.1 المتغير المستقل

المتغير المستقل ليس “التقنية”، بل **بنية الأخطاء** المقاسة تجريبيًا.

المقاييس الأساسية:

1. `mode_margin`
2. `wrong_mode_dominance`
3. `answer_entropy`
4. `pairwise_error_agreement`
5. `distinct_answer_count`

### التعريفات

#### answer_entropy

يقيس مدى انتشار الإجابات بين العينات.

- entropy منخفض + إجابة خاطئة مسيطرة = خطر على SC.
- entropy متوسط مع correct plurality = SC مفيد.
- entropy عالي جدًا = العينات مشتتة وقد لا يفيد vote.

#### pairwise_error_agreement

نسبة أزواج العينات الخاطئة التي أعطت نفس الخطأ.

إذا كانت عالية، فالأخطاء مترابطة.

---

## 2.2 المتغير التابع

المتغيرات التابعة:

1. `SC_correct`: هل تصويت الأغلبية أعطى الإجابة الصحيحة؟
2. `single_sample_correct`: متوسط دقة العينة الواحدة.
3. `SC_gain = SC_accuracy - single_sample_accuracy`.
4. `cost_per_correct` لو شُغلت على موديل حقيقي.

---

## 2.3 العينة

### النسخة العملية المقترحة

- عدد المسائل: `n = 120`.
- عدد العينات لكل مسألة: `k = 10`.
- درجات الصعوبة: 3 مستويات.
  - easy: 5 خطوات.
  - medium: 8 خطوات.
  - hard: 11 خطوة.
- لكل مستوى: 40 مسألة.

الإجمالي:

> 120 tasks × 10 samples = 1200 generations.

يمكن تنفيذها على:

1. محاكاة مضبوطة أولًا لاختبار الكود.
2. موديل حقيقي لاحقًا بعينة أصغر إذا لزم الأمر.

---

## 2.4 الأدوات

### الأدوات البرمجية

- مولّد مهام arithmetic-chain موجود أو نسخة محسنة منه.
- LLM client ثابت.
- parser موحد للإجابة النهائية.
- ملف JSONL لتسجيل كل عينة.
- script لحساب metrics.

### الأدوات المفاهيمية

- لا نستخدم Reflexion.
- لا نستخدم verifier.
- لا نستخدم تركيبات.

الهدف هنا عزل SC وبنية الأخطاء فقط.

---

# 3. ما الذي يؤكد الفرضية وما الذي يدحضها؟

## 3.1 نتيجة تؤكد الفرضية

تُعتبر الفرضية مدعومة إذا تحققت الشروط الثلاثة:

### شرط 1 — فصل واضح على مستوى المسألة

المسائل ذات `mode_margin > 0` يكون فيها `SC_correct` أعلى بكثير من المسائل ذات `mode_margin <= 0`.

مثال مقبول:

- SC_correct عند margin > 0: ≥ 85%.
- SC_correct عند margin <= 0: ≤ 55%.

### شرط 2 — ارتباط واضح

يوجد ارتباط موجب بين `mode_margin` و `SC_correct` أو `SC_gain`.

ونتوقع ارتباطًا سالبًا بين `wrong_mode_dominance` و `SC_gain`.

### شرط 3 — تفسير failure cases

في أغلب حالات فشل SC، نجد أن:

- correct answer ليست plurality.
- أو wrong mode مسيطر.
- أو pairwise error agreement مرتفع.

إذا تحققت هذه الثلاثة، تكون الفرضية قوية داخل هذا النطاق.

---

## 3.2 نتيجة تدحض الفرضية

تُدحض الفرضية إذا حدث أحد الآتي:

### دحض 1

`mode_margin` لا يميز بين نجاح وفشل SC.

أي أن SC ينجح ويفشل بنسب متقاربة سواء كان margin موجبًا أو سالبًا.

### دحض 2

`wrong_mode_dominance` لا يرتبط بفشل SC.

أي أن wrong mode مسيطر، ومع ذلك SC ينجح كثيرًا، أو العكس.

### دحض 3

العامل الحقيقي يظهر أنه شيء آخر، مثل:

- parsing failures.
- prompt artifact.
- deterministic collapse.
- provider instability.

حينها تكون بنية الأخطاء كما قسناها غير كافية.

---

# 4. ثلاث طرق قد تفشل بها التجربة منهجيًا وكيف نتجنبها

## الفشل المنهجي 1 — عدم استقلال العينات بسبب إعدادات sampling

### المشكلة

لو temperature منخفض جدًا، كل العينات ستكون شبه متطابقة. سنستنتج أن الأخطاء مترابطة، لكن السبب أننا لم نسمح بتنوع أصلاً.

### الوقاية

نثبت 3 درجات temperature:

- 0.2
- 0.7
- 1.0

ونحلل كل درجة على حدة.

إذا SC لا يعمل عند 0.2، فهذا متوقع ولا يُستخدم كدليل عام ضد SC.

---

## الفشل المنهجي 2 — parsing أو normalization خاطئ للإجابات

### المشكلة

قد يعطي النموذج الإجابة الصحيحة بصيغة مختلفة، والـ parser يعتبرها خطأ.

### الوقاية

- توحيد prompt: “اكتب السطر الأخير: ANSWER <number>”.
- parser robust يلتقط آخر رقم بعد ANSWER.
- حفظ النص الخام لكل generation.
- مراجعة يدوية لعينة 5–10% من الحالات الخاطئة.

---

## الفشل المنهجي 3 — مهمة واحدة لا تكشف wrong-mode الحقيقي

### المشكلة

لو المهام سهلة جدًا، لن تظهر wrong modes. لو صعبة جدًا، قد تنهار كل الطرق.

### الوقاية

استخدام 3 مستويات صعوبة.

الهدف ليس أعلى دقة، بل ظهور spectrum:

- مسائل ينجح فيها SC.
- مسائل يفشل فيها.
- مسائل فيها wrong mode واضح.

لو لم يظهر هذا الطيف، نعيد ضبط الصعوبة قبل أي استنتاج.

---

# 5. تسجيل الملاحظات وقياس النتائج

## 5.1 شكل التسجيل

كل generation تُحفظ كسطر JSONL:

```json
{
  "task_id": "medium_017",
  "difficulty": "medium",
  "prompt": "START ... OP ...",
  "ground_truth": 42,
  "sample_index": 3,
  "temperature": 0.7,
  "raw_output": "... ANSWER 41",
  "parsed_answer": 41,
  "is_correct": false,
  "model": "...",
  "provider": "... if available",
  "prompt_tokens": 123,
  "completion_tokens": 45,
  "usd": 0.0000012,
  "timestamp": "..."
}
```

## 5.2 ملف تجميع لكل task

بعد جمع العينات:

```json
{
  "task_id": "medium_017",
  "k": 10,
  "correct_count": 3,
  "largest_wrong_answer": 41,
  "largest_wrong_count": 5,
  "mode_margin": -2,
  "wrong_mode_dominance": 0.5,
  "distinct_answer_count": 4,
  "answer_entropy": 1.21,
  "pairwise_error_agreement": 0.44,
  "sc_answer": 41,
  "sc_correct": false,
  "single_sample_accuracy": 0.3
}
```

## 5.3 التحليل النهائي

ننتج 5 جداول:

### جدول 1 — الأداء العام

- single accuracy.
- SC accuracy.
- SC gain.
- cost/correct.

### جدول 2 — حسب الصعوبة

نفس المقاييس لكل difficulty.

### جدول 3 — حسب temperature

نفس المقاييس لكل temperature.

### جدول 4 — mode margin bins

تقسيم المسائل حسب:

- margin > 0
- margin = 0
- margin < 0

ونقيس SC accuracy في كل bin.

### جدول 5 — failure taxonomy

لحالات فشل SC:

- wrong mode dominance.
- high entropy.
- parsing failure.
- no correct samples.
- correct present but not plurality.

---

# 6. قرار التجربة

## إذا نجحت الفرضية

ننتقل من سؤال “هل SC قوي؟” إلى سياسة:

> استخدم SC عندما يكون mode margin المتوقع موجبًا أو عندما تكون الأخطاء متنوعة وغير مترابطة.

ثم نبحث عن طريقة رخيصة لتقدير mode margin قبل صرف k=10 كامل.

## إذا فشلت الفرضية

نستنتج أن error topology كما عرفناها غير كافية، ونبحث عن متغيرات أخرى:

- prompt sensitivity.
- latent confidence.
- task features.
- model-family effects.
- verifier-based selection.

---

# 7. الصياغة النهائية للتجربة

هذه التجربة لا تختبر “ذكاء” ولا “تركيب”.

إنها تختبر سؤالًا أعمق:

> هل شكل توزيع إجابات النموذج يفسر متى يفيد التصويت ومتى يفشل؟

إذا كانت الإجابة نعم، فهذا يؤسس حجر الأساس لمنهج AI Earth الجديد:

> قبل تركيب التقنيات، قِس بنية الخطأ.
