# Research Loop Round 1 — Error Topology, Verification, and LLM Composition

## اختيار موضوع X

اخترت أعلى موضوع أولوية مرتبط بكل التجارب السابقة:

> **بنية أخطاء LLMs: ترابط الأخطاء، تنوع العينات، وموثوقية التحقق/verifiers كشرط لفهم Self-Consistency وReflexion والتركيب.**

سبب الاختيار: هذا هو الجذر الذي تتفرع منه كل أسئلتنا: هل SC يعمل؟ متى يفشل؟ هل verifier مفيد؟ هل Reflexion له معنى؟ هل التركيب يستحق التكلفة؟

## Round 1 Online — 10 أعمال حديثة

> النطاق: آخر ~12 شهرًا تقريبًا، مع قبول بعض الأوراق الحديثة جدًا/قيد المراجعة إذا كانت مركزية للموضوع.

| # | العنوان | الرابط | الملخص المختصر |
|---|---|---|---|
| 1 | Consensus is Not Verification: Why Crowd Wisdom Strategies Fail for LLM Truthfulness | https://arxiv.org/abs/2603.06612 | يهاجم افتراض أن الإجماع = الحقيقة. يبيّن أن أخطاء النماذج مترابطة، وأن زيادة العينات قد تزيد consensus لا truth. مهم جدًا لـ SC. |
| 2 | Self-Consistency Falls Short! The Adverse Effects of Positional Bias on LLM-Based Long-Context Reasoning | https://direct.mit.edu/tacl/article/doi/10.1162/TACL.a.625/136156/Self-Consistency-Falls-Short-The-Adverse-Effects | يثبت أن SC قد يضخّم الأخطاء عندما تكون الأخطاء مترابطة بسبب positional bias في long-context. |
| 3 | When Does Verification Pay Off? A Closer Look at LLMs as Solution Verifiers | https://arxiv.org/abs/2512.02304 | دراسة واسعة لـ 37 موديل و9 benchmarks. تقدم verifier gain وتجد أن cross-family verification أفضل، وself-verification غالبًا أضعف. |
| 4 | Variation in Verification: Understanding Verification Dynamics Across Models, Domains, and Reasoning Processes | https://arxiv.org/html/2509.17995v1 | يدرس ديناميكيات verifier عبر generator strength وtask difficulty. يبيّن أن أخطاء النماذج الأقوى أصعب في الكشف. |
| 5 | Chain-of-Thought Reasoning In The Wild Is Not Always Faithful | https://openreview.net/forum?id=emjPKK11Oo | يبين أن CoT قد يكون غير أمين حتى في سياقات غير مصطنعة، مع rationalization بعدي. مهم لتفسير Reflexion وCoT. |
| 6 | FaithCoT-Bench: Benchmarking Instance-Level Faithfulness of Chain-of-Thought | https://arxiv.org/html/2510.04040v1 | يقدم benchmark على مستوى الحالات الفردية لاكتشاف عدم أمانة CoT. مهم لأن CoT لا يجب افتراضه تفسيرًا داخليًا. |
| 7 | Reasoning Models Will Sometimes Lie About Their Reasoning | https://arxiv.org/html/2601.07663v4 | يدرس misrepresentation في reasoning models ويعزز أن سلاسل reasoning ليست دائمًا نافذة صادقة. |
| 8 | The Self-Correction Illusion: LLMs Correct Others but Not Themselves | https://arxiv.org/html/2606.05976 | يفرّق بين قدرة النموذج على تصحيح خطأ خارجي وبين عجزه عن تصحيح نفسه. مهم جدًا لفكرة self-verification. |
| 9 | How LLMs Detect and Correct Their Own Errors: The Role of Internal Confidence | https://arxiv.org/html/2604.22271v1 | يقدم رؤية أكثر دقة: قد توجد إشارات داخلية للثقة/اكتشاف الخطأ، لكن السلوك الخارجي لا يكفي دائمًا. |
| 10 | When Chain of Thought is Necessary, Language Models Can Reveal Their Reasoning | https://arxiv.org/pdf/2507.05246 | يقدّم نتيجة مضادة جزئيًا: CoT قد يكون أكثر monitorable عندما تكون المهمة تتطلبه فعلًا، لا مجرد prompting شكلي. |

## Offline Analysis — الفحص الصارم

### التصنيف العلمي

#### A. نواة حاسمة للمشروع

1. **Consensus is Not Verification**  
   السبب: يهاجم جوهر SC: الاستقلال وترابط الأخطاء.

2. **Self-Consistency Falls Short**  
   السبب: يقدّم حالة فشل مباشرة لـ SC بسبب correlated errors.

3. **When Does Verification Pay Off?**  
   السبب: يقدّم مقياس verifier gain ويعالج self/intra/cross-family verification.

4. **Variation in Verification**  
   السبب: يربط verifier performance بـ task difficulty وgenerator strength.

هذه الأربعة هي العمود الفقري لأي تجربة تالية.

#### B. مهمة لكن تفسيرية/تحذيرية

5. **Chain-of-Thought Reasoning In The Wild Is Not Always Faithful**  
6. **FaithCoT-Bench**  
7. **Reasoning Models Will Sometimes Lie About Their Reasoning**  
8. **When Chain of Thought is Necessary...**  

هذه لا تختبر SC مباشرة، لكنها تمنعنا من تفسير CoT وReflexion بسطحية.

#### C. مثيرة لكن ليست أساس التجربة التالية

9. **The Self-Correction Illusion**  
   قوية جدًا، لكنها تركز على addressability/self-correction أكثر من error topology.

10. **How LLMs Detect and Correct Their Own Errors**  
   مهمة نظريًا، لكنها تدخل في internal activations/PANL، وهو أعمق من نطاق تجربتنا القادمة.

## ما استبعدناه أو خفّضنا أولويته

- أي مقال إعلامي أو blog يضخم “multi-agent consensus” دون قياس error correlation.
- أي عمل يكتفي بزيادة accuracy دون cost أو verifier false positives.
- أي عمل عن self-consistency لا يقيس correlation أو wrong-mode structure.
- أي عمل عن CoT يفترض faithfulness بدل قياسها.

## Repeat Round — مصادر نابعة من التحليل الأوفلاين فقط

التحليل الأوفلاين أشار إلى 3 محاور فقط للبحث التالي:

1. **error correlation / consensus is not verification**
2. **verifier gain / cross-family verification**
3. **CoT faithfulness / monitorability**

نتيجة الجولة الثانية: هذه المحاور أكدت أن التجربة التالية لا يجب أن تبدأ بتركيب جديد، بل بقياس:

- answer diversity
- wrong-mode dominance
- pairwise error correlation
- verifier gain
- CoT faithfulness كتحذير تفسيري

## القرار الناتج

لا نبدأ بتجربة “هل التركيب يكسب؟”.

نبدأ بتجربة:

> هل نستطيع التنبؤ بقوة SC أو فشله من error topology؟

لأن هذا هو الافتراض المركزي الذي لو ثبت، يحدد متى نحتاج verifier/depth أصلًا.
