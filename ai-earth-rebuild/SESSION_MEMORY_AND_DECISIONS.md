# Session Memory & Decisions — AI Earth Research Track

> هذا الملف يحفظ الخيط الفكري والمنهجي حتى لا ننسى أين وصلنا، ولماذا وصلنا إليه.
> لا يحتوي أي مفاتيح أو أسرار.

---

## 1. الرؤية الأصلية

بدأ المشروع من رؤية واسعة:

> تجميع ذكاء الأرض من الأبحاث المنشورة في كيان قابل للتركيب والتطوّر.

بعد النقد والتجارب، تغيّرت الصياغة الأنضج إلى:

> بناء منهجية/مختبر يقيس متى تكون تقنيات LLM المركبة مفيدة، ومتى تكون وهمًا أو غير مستحقة التكلفة.

القيمة لم تعد في “عدد القطع” أو “التركيب بحد ذاته”، بل في:

- تقييم الادعاءات.
- كشف الـ confounds.
- قياس التكلفة.
- فهم بنية الأخطاء.
- منع الانخداع بالهندسة المعقدة.

---

## 2. التحول المفاهيمي الأكبر

انتقلنا من دراسة أسماء تقنيات:

- CoT
- Self-Consistency
- Reflexion
- Debate
- Tree-of-Thoughts
- Verifier

إلى دراسة متغيرات كامنة:

- `Q`: جودة العينة الفردية.
- `D`: تنوع العينات.
- `R`: ترابط الأخطاء.
- `F`: جودة التغذية الراجعة.
- `S`: جودة الاختيار/التصويت.
- `C`: التكلفة.
- `T`: بنية المهمة.
- `E`: شكل فضاء الأخطاء.

الصياغة الأعمق:

> كل تقنية LLM هي تدخل على متغيرات كامنة. لا نحكم على التقنية باسمها، بل بقياس أثرها على هذه المتغيرات وتكلفتها.

---

## 3. أهم نتائج التجارب السابقة

### 3.1 المحاكاة

المحاكاة أفادت في بناء pipeline وتوليد فرضيات، لكنها لم تعد دليلًا على قوانين.

السبب:

- افترضت استقلال الأخطاء.
- افترضت أن CoT يحسن الخطأ.
- افترضت أن reflection يحسن دائمًا.
- استخدمت نموذج أخطاء مخترع.

الحكم:

> المحاكاة تولّد فرضيات، لا تثبت قوانين.

---

### 3.2 real-model experiments قبل EXP13

لاحظنا:

- CoT قد يكون أسوأ من Direct على arithmetic chains.
- Self-Consistency كان قويًا.
- self-verification كان ضعيفًا/ضارًا.
- verifier قوي حسّن التركيب مقارنةً بـ weak verifier، لكن لم يهزم SC النقي عند حساب التكلفة.

الحكم:

> baseline بسيط مثل SC قد يكون أصعب كثيرًا في الهزيمة من التركيبات المعقدة.

---

## 4. EXP13 — Error Topology

### 4.1 الفرضية الأصلية

> نجاح Self-Consistency يمكن التنبؤ به من `mode_margin` و `wrong_mode_dominance`.

التعريفات:

- `correct_count`: عدد العينات الصحيحة.
- `largest_wrong_count`: أكبر تكرار لإجابة خاطئة.
- `mode_margin = correct_count - largest_wrong_count`.
- `wrong_mode_dominance = largest_wrong_count / k`.

---

### 4.2 Phase A — Simulation

الكود:

`ai-earth-rebuild/experiments/exp13_error_topology.py`

النتيجة:

- الـ pipeline يعمل.
- المقاييس تعمل.
- `mode_margin` فصل نجاح وفشل SC داخل المحاكاة.

لكن:

> هذه نتيجة عن الـ simulator فقط، لا عن LLMs.

---

### 4.3 Phase B — Real Pilot

الكود:

`ai-earth-rebuild/experiments/exp13_real_pilot.py`

النتائج الأساسية:

- tasks: 45
- k = 10
- model: Llama 3.1 8B عبر OpenRouter
- temperature = 0.7
- single accuracy = 90.2%
- SC accuracy = 97.8%
- SC gain = +7.6
- 44/45 tasks لها `mode_margin > 0`
- failure واحد فقط، وكان wrong mode كامل.

حالة الفشل:

```text
task_id: medium_010
truth: 1499
all 10 samples: 1489
mode_margin: -10
wrong_mode_dominance: 1.0
```

---

## 5. إعادة التقييم بعد EXP13

### 5.1 الانحياز التأكيدي

اكتشفنا أن هناك خطرًا كبيرًا:

> عاملنا `mode_margin` كـ predictor، بينما هو محسوب من نفس العينات التي يستخدمها SC.

بالتالي هو:

> diagnostic بعدي، لا predictor قبلي.

الصياغة الصحيحة:

> `mode_margin` يفسّر outcome بعد وقوعه، لكنه لم يثبت بعد أنه يتنبأ قبل دفع تكلفة k=10.

---

### 5.2 protocol deviation

أهم الانزياحات:

1. تحويل metric بعدي إلى predictor في اللغة.
2. نقص حالات `margin <= 0`.
3. استخدام fallback exploratory.
4. عدم تثبيت provider/quantization.
5. عدم حساب dollar cost/correct في report النهائي.

الحكم:

> EXP13 Phase B مفيد كـ pilot، لا كـ confirmatory evidence.

---

### 5.3 المتغير الخفي

أرجح متغير خفي:

> model-relative task difficulty

أي أن المهام كانت سهلة للموديل، فظهرت `mode_margin > 0` طبيعيًا.

النموذج السببي البديل:

```text
model-relative difficulty → mode_margin
model-relative difficulty → SC_success
```

---

### 5.4 اختبار الهشاشة

أهم اختبار هشاشة:

> هل early topology من k0=3 تتنبأ بـ SC@10؟

لو نعم، لدينا قيمة عملية.
لو لا، فـ `mode_margin` مجرد diagnostic.

---

## 6. الحلقة المغلقة التي كشفناها

نعم، كنا قريبين من حلقة مغلقة:

```text
SC ينجح إذا correct mode يسيطر.
mode_margin يقيس أن correct mode يسيطر.
إذن mode_margin يفسر SC.
```

هذه قريبة من tautology.

النتيجة الحالية لا تضيف نظرية سببية جديدة إلا إذا خرجنا إلى:

1. predictor قبلي.
2. intervention سببي.
3. تعميم خارج المجال.

الحكم:

> EXP13 الحالي diagnostic، لا predictive.

---

## 7. الفكرة الجديدة المخفية

النتيجة المخالفة لتوقعنا:

> لم نستطع جعل SC يفشل بسهولة؛ SC كان قويًا جدًا.

الفرضية الجديدة:

> SC لا يفشل لمجرد أن المهمة أصعب، بل يفشل عندما يوجد wrong attractor قوي يجذب العينات إلى إجابة خاطئة مشتركة.

المفهوم الجديد:

# Wrong Attractor

SC ليس أداة تحقق من الحقيقة، بل:

> أداة تضخيم لأقوى attractor في توزيع الإجابات.

إذا كان correct attractor هو الأقوى، ينجح.
إذا كان wrong attractor هو الأقوى، يفشل بثقة.

---

## 8. قلب السبب والنتيجة

قد لا تكون topology سببًا سابقًا للنتيجة.

قد تكون:

```text
sampling policy → answer topology → SC outcome
```

أي أن topology نفسها ناتجة عن:

- temperature
- top-p
- prompt
- model
- provider
- decoding dynamics

الفكرة الجديدة:

> لا نكتفي بقياس topology؛ يمكن أن نحاول تشكيلها.

من:

```text
Measure topology → decide SC
```

إلى:

```text
Shape topology → make SC useful
```

---

## 9. التجربة التالية المنطقية

التجربة التي تفرضها النتيجة ليست verifier ولا Reflexion ولا تركيب.

هي:

# EXP13C — Early Topology Prediction

السؤال:

> هل نستطيع من أول k0=3 عينات أن نتنبأ بنتيجة SC@10؟

التصميم:

1. خذ 3 عينات.
2. احسب early topology:
   - early entropy
   - early agreement
   - early top-answer dominance
   - distinct count
3. لا تستخدم العينات 4–10 في التنبؤ.
4. أكمل إلى k=10.
5. اختبر هل early metrics تتنبأ بـ SC@10.

هذه التجربة تكسر الدائرية.

---

## 10. حدود التعميم الحالية

لا يجوز تعميم EXP13 إلا داخل النطاق الضيق:

- Llama 3.1 8B
- OpenRouter unpinned
- arithmetic-chain tasks
- prompt محدد
- temperature 0.7
- k=10
- pilot exploratory

لا نعمم على:

- LLMs عمومًا.
- reasoning عمومًا.
- tasks أخرى.
- temperatures أخرى.
- k أخرى.
- provider/quantization أخرى.

---

## 11. Resource Layer

بُني Resource Manager خفيف:

`ai-earth-rebuild/core/resource_manager.py`

يدعم:

- OpenRouter
- exploratory policy
- fixed policy
- quantization constraints
- metadata logging

القاعدة:

> المرونة للاستكشاف، التثبيت للإثبات.

---

## 12. الملفات الأساسية الحالية

- `CURRENT_FOCUS.md`
- `EXP13_PREREGISTRATION_ERROR_TOPOLOGY.md`
- `EXP13_DESIGN_REVIEW.md`
- `EXP13_PHASE_B_REAL_PILOT_RESULTS.md`
- `EXP13_CONFIRMATION_BIAS_AUDIT.md`
- `EXP13_PROTOCOL_DEVIATION_AUDIT.md`
- `EXP13_HIDDEN_CONFOUNDER_ANALYSIS.md`
- `EXP13_SENSITIVITY_THOUGHT_TEST.md`
- `RESOURCE_FLEXIBILITY_LAYER.md`
- `KEYS_CAPABILITY_AUDIT.md`
- `core/resource_manager.py`
- `experiments/exp13_error_topology.py`
- `experiments/exp13_real_pilot.py`

---

## 13. قاعدة حفظ المستقبل

أي طلب قادم مهم يجب أن يتحول إلى ملف مستقل أو تحديث لهذا الملف، حتى لا يضيع الخيط.

لكن لا نفتح تجربة جديدة إلا إذا كانت:

1. predictive
2. interventional
3. cross-domain

وإلا سنعيد نفس الحلقة المغلقة.
