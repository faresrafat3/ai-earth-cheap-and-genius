# EXP13 — مقارنة التصميم الأصلي بما طُبّق فعلاً

## الهدف

هذه الوثيقة تقارن:

1. **المنهجية التي صممناها أولًا** في `EXP13_PREREGISTRATION_ERROR_TOPOLOGY.md` و `EXP13_DESIGN_REVIEW.md`.
2. **ما طبقناه فعليًا** في Phase A وPhase B real pilot.

السؤال:

> هل حدث انزياح غير مقصود؟ هل أضفنا متغيرًا؟ هل أغفلنا خطوة؟

---

# 1. ملخص الحكم

نعم، حدثت انزياحات. بعضها مقبول لأنه كان pilot، وبعضها مهم ويجب ألا يدخل في أي claim confirmatory.

أخطر 5 انزياحات:

1. حولنا `mode_margin` من diagnostic إلى predictor في التفسير.
2. لم ننتج طيفًا كافيًا من حالات `margin <= 0`.
3. استخدمنا fallback exploratory مع مفاتيح مختلفة، بينما confirmatory كان يحتاج تثبيت.
4. لم نقس cost/correct بالكامل في التقرير النهائي رغم أن التصميم ذكره.
5. لم ننفذ temperature sweep في real pilot كما كان في Phase A فقط، وهذا صحيح كقرار، لكن يجب عدم تعميم أثر temperature.

---

# 2. مقارنة تفصيلية

## 2.1 الفرضية

### التصميم الأصلي

> نجاح Self-Consistency يمكن التنبؤ به من `mode_margin` و `wrong_mode_dominance`.

### ما طبقناه

حسبنا `mode_margin` من نفس الـ k=10 عينات التي استخدمها SC.

### الانزياح

هذا يجعل `mode_margin` **diagnostic بعدي** وليس predictor قبلي.

### درجة الخطورة

🔴 عالية.

### التصحيح

إعادة الصياغة:

> EXP13 يقيس قدرة `mode_margin` على تفسير outcome بعديًا، لا التنبؤ به مسبقًا.

والتجربة التالية يجب أن تستخدم early-k predictor منفصل عن k النهائي.

---

## 2.2 العينة n

### التصميم الأصلي Phase B

- n = 45 tasks.
- 15 easy / 15 medium / 15 hard.

### ما طبقناه

تم تطبيقه كما هو.

### الانزياح

لا يوجد في العدد.

### الحكم

🟢 مطابق.

---

## 2.3 k

### التصميم الأصلي

- k = 10.

### ما طبقناه

- k = 10.

### الحكم

🟢 مطابق.

---

## 2.4 temperature

### التصميم الأصلي

- Phase A: 0.2 / 0.7 / 1.0.
- Phase B: 0.7 فقط.

### ما طبقناه

- Phase A استخدمت الثلاثة.
- Phase B استخدمت 0.7 فقط.

### الحكم

🟢 مطابق.

### ملاحظة

لا يجوز تعميم النتيجة على درجات temperature أخرى.

---

## 2.5 مستويات الصعوبة

### التصميم الأصلي

- easy = 5 steps.
- medium = 8 steps.
- hard = 11 steps.

### ما طبقناه

تم تطبيق ذلك.

### الانزياح

لا يوجد في التصميم، لكن ظهر بعد التطبيق أن الصعوبة غير كافية لإنتاج حالات فشل كافية.

### درجة الخطورة

🟡 متوسطة.

### التصحيح

لا نغير EXP13 بعد التنفيذ. نصمم EXP13B لاحقًا بصعوبة أعلى أو adversarial tasks.

---

## 2.6 الهدف من Phase B

### التصميم الأصلي

Phase B كان pilot صغيرًا:

> اختبار أولي على LLM حقيقي، لا تعميم.

### ما حدث في التفسير الأولي

كنا قريبين من تفسير النتيجة كدعم قوي للفرضية.

### الانزياح

تفسيري، لا تنفيذي.

### درجة الخطورة

🔴 عالية لو لم تُصحح.

### التصحيح

تم تصحيحه في `EXP13_CONFIRMATION_BIAS_AUDIT.md`.

---

## 2.7 تسجيل البيانات

### التصميم الأصلي

كل generation يجب أن يسجل:

- task_id
- difficulty
- prompt
- ground_truth
- sample_index
- temperature
- raw_output
- parsed_answer
- is_correct
- model
- provider
- tokens
- cost أو usage
- timestamp

### ما طبقناه

سجلنا أغلب ذلك:

- task_id ✅
- difficulty ✅
- prompt ✅
- ground_truth ✅
- sample_index ✅
- temperature ✅
- raw_output ✅
- parsed_answer ✅
- is_correct ✅
- model ✅
- provider ✅ لكن unpinned/openrouter
- prompt/completion tokens ✅
- timestamp ✅
- latency/retries/failures ✅ إضافة مفيدة

### ما نقص

- لم نسجل cost بالدولار لكل generation.
- لم نسجل provider الفعلي أو quantization الفعلي.

### درجة الخطورة

🟡 متوسطة.

### التصحيح

إضافة cost estimation وprovider metadata إن توفر من API.

---

## 2.8 استخدام Resource Manager

### التصميم الأصلي

لم يكن جزءًا من EXP13 الأصلي، لكنه أضيف قبل Phase B لضبط الموارد.

### ما طبقناه

استخدمنا Resource Manager وpolicy exploratory.

### هل هذا انزياح؟

نعم، لكنه انزياح مفيد لأنه زاد metadata وسجل fallback.

### درجة الخطورة

🟢 منخفضة، بشرط إعلان أن run exploratory.

---

## 2.9 سياسة fallback

### التصميم الأصلي

Phase B pilot يسمح ببعض المرونة، لكن يجب تسجيلها.

### ما طبقناه

استخدمنا exploratory fallback. حدث HTTP 402 في 45 calls، وتم fallback بنجاح.

### الانزياح

التجربة لم تكن fixed-provider ولا fixed-key.

### درجة الخطورة

🟡/🔴.

مقبول كـ pilot، غير مقبول كـ confirmatory.

### التصحيح

أي تجربة confirmatory يجب أن تستخدم:

- fixed policy.
- مفتاح/حساب صالح واحد أو provider ثابت.
- لا fallback غير مسجل.

---

## 2.10 provider/quantization

### التصميم الأصلي بعد التدقيق

كان مطلوبًا ضبط provider/quantization قدر الإمكان.

### ما طبقناه

لم نثبت provider ولا quantization.

### الانزياح

نعم.

### درجة الخطورة

🔴 عالية لأي claim confirmatory.

### التصحيح

- استخدام `--quantizations fp16,bf16` إن كان الموديل يدعم.
- تسجيل provider metadata إن توفر.
- أو إعلان صريح أن النتيجة pilot غير confirmatory.

---

## 2.11 parser review

### التصميم الأصلي

مراجعة يدوية لـ 5–10% من الحالات الخاطئة.

### ما طبقناه

لم نعمل مراجعة يدوية رسمية. لكن فحصنا failure الوحيد يدويًا من task_metrics.

### الانزياح

جزئي.

### درجة الخطورة

🟡.

لأن عدد الأخطاء قليل، لكن لا يزال يجب مراجعة عينة من raw outputs.

### التصحيح

قبل أي claim، نراجع:

- كل حالات SC failure.
- عينة من single-sample errors.
- عينة من correct parses.

---

## 2.12 cost/correct

### التصميم الأصلي

cost/correct متغير تابع ثانوي في real run.

### ما طبقناه

سجلنا tokens، لكن لم نحسب dollar cost/correct في التقرير.

### الانزياح

نعم، أغفلنا خطوة.

### درجة الخطورة

🟡 متوسطة.

### التصحيح

إضافة pricing lookup أو تقدير تكلفة يدوي من OpenRouter model pricing.

---

## 2.13 failure taxonomy

### التصميم الأصلي

إنتاج جدول failure taxonomy.

### ما طبقناه

Phase A فعل ذلك.

Phase B report لم يعرض taxonomy كامل، لكن وثيقة النتائج سجلت failure الوحيد.

### الانزياح

طفيف.

### التصحيح

إضافة failure taxonomy إلى real report أيضًا.

---

# 3. الانزياحات حسب النوع

## انزياحات تنفيذية

| الانزياح | الخطورة |
|---|---|
| provider/quantization غير مثبت | 🔴 |
| fallback حدث 45 مرة | 🟡/🔴 |
| لا cost بالدولار | 🟡 |
| لا مراجعة parser رسمية | 🟡 |

## انزياحات تفسيرية

| الانزياح | الخطورة |
|---|---|
| معاملته كـ predictor لا diagnostic | 🔴 |
| تفسير pilot كدعم قوي | 🔴 |
| التركيز على الفشل الوحيد أكثر من نقص bins | 🟡 |

## انزياحات مقبولة

| الانزياح | السبب |
|---|---|
| إضافة Resource Manager | زاد الضبط والتسجيل |
| Phase B temp واحدة | كان preregistered |
| exploratory fallback | مقبول في pilot فقط |

---

# 4. هل هذه الانزياحات تفسد EXP13؟

## لا تفسده كـ pilot

لأن هدف pilot كان:

- تشغيل pipeline على موديل حقيقي.
- رؤية أولية للـ signal.
- اختبار logging.

وقد تحقق ذلك.

## لكنها تمنع استخدامه كـ confirmatory evidence

لا يجوز استخدام EXP13 Phase B لإثبات قانون.

الصياغة الصحيحة:

> EXP13 Phase B pilot شغّل pipeline بنجاح وأظهر أن SC قوي وأن mode_margin يصف outcome، لكنه لم يختبر prediction بشكل مستقل ولم ينتج حالات فشل كافية.

---

# 5. ماذا يجب أن نصحح قبل التجربة التالية؟

## التصحيح 1 — predictor منفصل عن outcome

استخدم early-k:

- k0 = 3 للتنبؤ.
- k = 10 للتحقق.

## التصحيح 2 — إنتاج حالات borderline

استخدم:

- tasks أصعب.
- model أضعف.
- temperature أعلى.
- adversarial arithmetic.

## التصحيح 3 — منع resource drift

- fixed policy للتجارب التأكيدية.
- quantization/provider constraints إن أمكن.

## التصحيح 4 — cost/correct

- حساب تكلفة بالدولار.
- latency.
- retries.

## التصحيح 5 — parser validation

- review raw outputs لعينة محددة مسبقًا.

---

# 6. الحكم النهائي

حدثت انزياحات غير مقصودة، أهمها تفسيري لا تنفيذي:

> حوّلنا metric بعدي مشتق من نفس العينات إلى predictor في اللغة.

هذا كان أخطر خطأ.

لكن بما أننا صححناه الآن، تظل EXP13 Phase B مفيدة كـ pilot، لا كدليل نهائي.

الدرس:

> لا يكفي أن تكون التجربة مشغّلة صح؛ يجب أن يكون التفسير مطابقًا لما صممته فعلًا.
