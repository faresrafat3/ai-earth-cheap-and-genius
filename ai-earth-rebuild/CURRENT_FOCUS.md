# Current Focus — لا ننسى المسار

## الهدف الحالي

عدم التشتت. نحن الآن لسنا في مرحلة تدقيق إضافي ولا فلسفة جديدة.

نحن في مرحلة:

> بناء Resource Manager خفيف ثم تشغيل EXP13 Phase B real pilot.

---

## الفكرة الأساسية التي نختبرها

قبل تركيب أي تقنية، يجب قياس **بنية الخطأ**.

الفرضية الأساسية لـ EXP13:

> نجاح Self-Consistency يمكن التنبؤ به من `mode_margin` و `wrong_mode_dominance`.

### التعريفات

- `correct_count`: عدد العينات الصحيحة من k.
- `largest_wrong_count`: أكثر إجابة خاطئة تكرارًا.
- `mode_margin = correct_count - largest_wrong_count`.
- `wrong_mode_dominance = largest_wrong_count / k`.

### التوقع

- إذا `mode_margin > 0` → SC غالبًا ينجح.
- إذا `mode_margin <= 0` → SC غالبًا يفشل أو يقل مكسبه.

---

## EXP13 status

### Phase A — Simulation

تم تنفيذها بنجاح.

النتيجة: `mode_margin` فصل نجاح وفشل SC داخل المحاكاة.

ملف الكود:

`experiments/exp13_error_topology.py`

### Phase B — Real Pilot

الكود جاهز.

ملف الكود:

`experiments/exp13_real_pilot.py`

الإعداد المخطط:

- model: `meta-llama/llama-3.1-8b-instruct`
- n = 45 tasks
- 15 easy / 15 medium / 15 hard
- k = 10 samples/task
- temperature = 0.7

---

## الخطوة القادمة فقط

1. بناء Resource Manager خفيف جدًا.
2. ربطه لاحقًا بـ EXP13 real pilot.
3. تشغيل Phase B.

لا نفتح تدقيق جديد الآن.
لا نغير فرضية EXP13.
لا نوسع الموارد قبل Resource Manager.

---

## قاعدة التنفيذ

- Exploratory: fallback مسموح لكن مسجل.
- Confirmatory: fallback ممنوع إلا كـ deviation.

الآن نحن في **real pilot exploratory مضبوط**، وليس confirmatory نهائي.
