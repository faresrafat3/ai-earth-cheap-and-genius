# EXP13 — اختبار ذهني لهشاشة النتيجة

## السؤال

إذا غيّرنا شرطًا واحدًا بسيطًا في التجربة، هل تنهار النتيجة؟

النتيجة التي نختبر هشاشتها:

> `mode_margin` / error topology يفسر نجاح أو فشل Self-Consistency.

لكن بعد تدقيق الانحياز، الصياغة الأدق:

> `mode_margin` يصف outcome بعديًا، وربما يكون مفيدًا إذا أمكن تقديره مبكرًا.

---

# 1. مبدأ الاختبار

لا نغير كل شيء. نغير شرطًا واحدًا فقط في كل مرة.

إذا بقيت الإشارة الأساسية موجودة عبر تغييرات صغيرة، فالنتيجة أقوى.

إذا انهارت أو انعكست مع تغيير بسيط، فهي هشة وربما artifact.

---

# 2. الشرط الأكثر أهمية للاختبار الذهني: temperature

## لماذا temperature؟

لأن temperature يغير مباشرة:

- تنوع الإجابات D.
- جودة العينة Q.
- ترابط الأخطاء R.
- احتمال ظهور wrong modes.

أي أنه يمس قلب فرضيتنا.

---

# 3. الاختبار الذهني: ماذا يحدث إذا غيّرنا temperature؟

## الحالة الأصلية

- temperature = 0.7
- single accuracy = 90.2%
- SC accuracy = 97.8%
- أغلب المهام mode_margin > 0

---

## 3.1 لو خفضنا temperature إلى 0.2

### التوقع لو النتيجة قوية

إذا كانت error topology حقيقية وليست artifact، نتوقع:

- تنوع أقل.
- إجابات أكثر تكرارًا.
- إذا كان النموذج يعرف الإجابة، سيزداد correct mode.
- إذا كان النموذج لديه wrong mode منهجي، سيتعزز الخطأ.

إذن:

- SC قد يصبح أكثر ثقة، لكنه ليس دائمًا أكثر صحة.
- `mode_margin` يجب أن يظل يصف النجاح/الفشل.
- حالات wrong-mode collapse يجب أن تصبح أوضح عندما يكون الخطأ منهجيًا.

### التوقع لو النتيجة هشة

- كل العينات تصبح متطابقة تقريبًا.
- لا يعود لدينا topology مفيد.
- SC يصبح نسخة مكررة من single sample.
- `mode_margin` يصبح عاليًا دائمًا سواء صح أو غلط.

في هذه الحالة، النتيجة تعتمد على sampling diversity وليست عامة.

### علامة الهشاشة

إذا عند T=0.2:

```text
SC_gain ≈ 0
entropy ≈ 0
mode_margin مرتفع لكن لا يميز الصحة
```

فالنتيجة هشة تحت low-diversity regime.

---

## 3.2 لو رفعنا temperature إلى 1.0

### التوقع لو النتيجة قوية

- single accuracy ينخفض.
- diversity يزيد.
- correct_count قد ينخفض.
- wrong answers تتوزع على modes كثيرة.

إذا الأخطاء متفرقة، SC قد يظل مفيدًا لأن correct answer قد تبقى plurality.

في هذه الحالة:

- `answer_entropy` يزيد.
- `wrong_mode_dominance` قد ينخفض.
- SC ينجح إذا correct plurality محفوظة.

### التوقع لو النتيجة هشة

- correct answer تفقد plurality.
- الإجابات تصبح مشتتة.
- tie-breaking يسيطر.
- SC يتدهور أو يصبح عشوائيًا.

### علامة الهشاشة

إذا عند T=1.0:

```text
single accuracy ينخفض قليلًا
لكن SC accuracy ينهار كثيرًا
```

فهذا يعني أن SC كان يعتمد على نطاق temperature ضيق.

---

# 4. الشرط الثاني: طريقة القياس

## تغيير بسيط

بدل قياس `mode_margin` من k=10 كاملة، نقيس early topology من k0=3 فقط.

### لو النتيجة قوية

early topology يجب أن يعطي signal ولو أضعف:

- early agreement العالي على إجابة واحدة يتنبأ بثبات mode لاحقًا.
- early entropy العالي يتنبأ بعدم استقرار SC.

### لو النتيجة هشة

- early metrics لا تتنبأ بأي شيء.
- signal يظهر فقط بعد استخدام كل k=10، أي أنه diagnostic لا predictive.

### علامة الهشاشة

إذا:

```text
early topology لا يتنبأ بـ SC@10 إطلاقًا
```

فالفكرة العملية تنهار كـ predictive tool، لكنها تبقى diagnostic فقط.

---

# 5. الشرط الثالث: طريقة التصويت

## تغيير بسيط

بدل majority/plurality vote، نستخدم:

- ranked vote إن أمكن.
- random tie-break.
- numeric clustering قريب من الإجابة.
- median للنتائج الرقمية.

### لو النتيجة قوية

إذا error topology هو العامل الحقيقي، تغيير voting rule يجب ألا يقلب النتيجة كليًا إلا في حالات tie/near-tie.

### لو النتيجة هشة

إذا تغيّر صغير في tie-break أو vote rule يغير SC accuracy كثيرًا، فالنتيجة تعتمد على artifact في selection.

### علامة الهشاشة

```text
SC accuracy يتغير كثيرًا دون تغير في samples نفسها
```

إذن selection rule هو المتغير الحقيقي، لا topology وحدها.

---

# 6. الشرط الرابع: prompt wording

## تغيير بسيط

نغير فقط صياغة التعليمة:

من:

> Apply operations left-to-right. ANSWER <integer>.

إلى:

> Compute the final value step by step and give only the final integer.

### لو النتيجة قوية

رغم تغير accuracy العام، العلاقة بين topology وSC success يجب أن تبقى.

### لو النتيجة هشة

- prompt يغير single accuracy بشدة.
- prompt يغير نوع الأخطاء.
- mode_margin distribution يتغير كليًا.

### علامة الهشاشة

لو prompt واحد ينتج غالبًا positive margins، وآخر ينتج wrong-mode collapse، فالنتيجة prompt-specific.

---

# 7. الشرط الخامس: صعوبة المهمة

## تغيير بسيط

نزيد steps من 11 إلى 14 فقط.

### لو النتيجة قوية

- تظهر حالات failure أكثر.
- لكن داخل كل regime، wrong-mode dominance يفسر الفشل.

### لو النتيجة هشة

- SC ينهار فجأة.
- كل العينات تصبح خاطئة أو مشتتة.
- لا يعود mode_margin مفيدًا لأنه لا توجد correct samples أصلًا.

### علامة الهشاشة

```text
no-correct-samples dominates failures
```

في هذه الحالة المشكلة ليست topology، بل Q منخفض جدًا.

---

# 8. مصفوفة الهشاشة

| الشرط المتغير | إذا النتيجة قوية | إذا النتيجة هشة |
|---|---|---|
| temperature ↓ 0.2 | collapse يكشف wrong modes | لا تنوع، SC=single |
| temperature ↑ 1.0 | diversity يساعد إذا correct plurality | SC ينهار أو ties كثيرة |
| early k0=3 | يعطي signal مبدئي | لا يتنبأ بشيء |
| vote rule | لا يتغير إلا في ties | accuracy يتقلب بشدة |
| prompt wording | العلاقة topology→SC تبقى | التوزيع كله يتغير |
| steps ↑ 14 | failures أكثر ومفسرة | no-correct dominates |

---

# 9. الاختبار الذهني الأهم

أهم تغيير واحد:

> قياس topology من k0=3 بدل k=10.

لماذا؟

لأنه يختبر هل الفكرة predictive أم diagnostic.

## إذا صمدت

هذا يرفع قيمة المشروع جدًا:

> نستطيع تقدير هل SC يستحق قبل دفع تكلفة k=10.

## إذا انهارت

فالفكرة تظل مفيدة فقط بعد وقوع الحدث:

> نفهم لماذا نجح SC، لكن لا نعرف هل نشغله مسبقًا.

---

# 10. الخلاصة

النتيجة الحالية هشة محتملًا أمام 3 تغييرات:

1. temperature.
2. prompt wording.
3. early-vs-full measurement.

لكن التغيير الأكثر حسمًا هو:

> فصل predictor عن outcome باستخدام k0=3.

لذلك التجربة القادمة يجب ألا تكون فقط أصعب، بل يجب أن تختبر:

> هل topology المبكرة تتنبأ بـ SC@10؟

هذا هو اختبار القوة الحقيقي.
