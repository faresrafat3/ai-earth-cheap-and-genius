# طبقة مرونة استخدام الموارد العلمية — Scientific Resource Flexibility Layer

## الهدف

المفاتيح والمزوّدون الموجودون عندنا ليسوا مجرد “quota backup”. هم **موارد علمية** يمكن استخدامها لاختبار فرضيات مختلفة:

- هل اختلاف عائلة الموديل يغير جودة verifier؟
- هل quantization يغير error topology؟
- هل provider routing يلوث النتائج؟
- هل search/scrape pipeline يرفع جودة جولات البحث؟
- هل gateway/caching يقلل التكلفة أو يغير latency؟

لكن المرونة بدون ضبط قد تفسد التجربة. لذلك نحتاج طبقة تفصل بين:

1. **الاستكشاف**: نستخدم كل الموارد بمرونة لاكتشاف فرص.
2. **التجربة العلمية**: نثبت الموارد ونمنع fallback غير مسجل.
3. **الإنتاج/البحث الطويل**: نستخدم routing وfallback بذكاء لتقليل التكلفة.

---

# 1. المبدأ الأساسي

## المرونة مسموحة في الاستكشاف، ممنوعة داخل المقارنة العلمية إلا إذا كانت مسجلة

مثال:

- في exploratory run: يمكن استخدام OpenRouter + Gemini + Mistral + NVIDIA للبحث عن أرخص/أفضل موديل.
- في confirmatory run: نثبت actor، verifier، provider، quantization، prompt، temperature.

أي fallback أو تغيير provider أثناء confirmatory run يجب أن يُسجل كـ deviation.

---

# 2. تقسيم الموارد حسب الدور العلمي

## A. موارد توليد الإجابات — Generators

تُستخدم كـ actor لإنتاج عينات.

| المورد | الدور | الاستخدام العلمي |
|---|---|---|
| OpenRouter | generator عام | مقارنة موديلات كثيرة بسرعة |
| Gemini | generator طويل السياق | long-context / structured tasks |
| NVIDIA NIM | generator عالي السرعة | عينات كثيرة وthroughput |
| Mistral | generator بديل | cross-family comparison |
| SiliconFlow | generator بديل | Qwen/DeepSeek style families |
| Cloudflare Workers AI | generator/gateway | تشغيل موحد مع logging/caching |

## B. موارد التحقق — Verifiers

تُستخدم لفحص إجابات actor.

| المورد | لماذا مهم؟ |
|---|---|
| Llama via OpenRouter | same-family verifier baseline |
| Mistral | cross-family verifier مهم جدًا |
| Gemini | cross-family verifier قوي، long-context |
| Qwen/DeepSeek عبر SiliconFlow أو OpenRouter | verifier من عائلة مختلفة |
| NVIDIA NIM models | verifier سريع أو قوي حسب catalog |

## C. موارد البحث وجمع الأدلة — Evidence Ingestion

| المورد | الدور |
|---|---|
| Serper | search/discovery |
| Firecrawl | scrape/crawl/extract markdown/JSON |
| LLM summarizer | تلخيص structured evidence |
| Offline audit | استبعاد hype وتصنيف صارم |

## D. موارد البنية التحتية — Infrastructure

| المورد | الدور |
|---|---|
| Cloudflare AI Gateway | logging/caching/rate limiting/guardrails |
| GitHub | versioning/CI فقط، لا يستخدم كمفتاح عام داخل التجارب |

---

# 3. أوضاع التشغيل الثلاثة

## Mode 1 — Exploratory Mode

الهدف: البحث عن فرص، مقارنة سريعة، smoke tests.

مسموح:

- fallback بين مفاتيح.
- fallback بين موديلات.
- تجربة أكثر من provider.
- تغيير temperature أو prompt مع التسجيل.

الشرط:

> كل شيء يسجل في metadata، والنتائج لا تُسمى confirmatory.

## Mode 2 — Confirmatory Mode

الهدف: اختبار فرضية preregistered.

ممنوع:

- fallback غير مسجل.
- تغيير model/provider/quantization.
- تغيير prompt/parser بعد التشغيل.
- تغيير n/k/temperature بعد رؤية النتائج.

مطلوب:

- provider ثابت قدر الإمكان.
- quantization ثابت إن أمكن.
- model exact id.
- seed/task set ثابت.
- cost logging.

## Mode 3 — Production Research Mode

الهدف: تشغيل جولات بحث طويلة بكفاءة.

مسموح:

- routing ذكي.
- caching.
- retry.
- استخدام أرخص موديل للمهام السهلة وأقوى موديل للمهام الصعبة.

لكن:

> لا نستخدم نتائجه كدليل علمي صارم إلا بعد إعادة confirmatory.

---

# 4. Resource Registry Schema

كل مورد يجب أن يوصف بهذا الشكل:

```json
{
  "id": "openrouter-main",
  "provider": "openrouter",
  "role": ["generator", "verifier"],
  "auth_env": "OPENROUTER_KEYS",
  "base_url": "https://openrouter.ai/api/v1",
  "api_style": "openai-compatible",
  "models": ["meta-llama/llama-3.1-8b-instruct"],
  "capabilities": {
    "chat": true,
    "structured_outputs": "model-dependent",
    "logprobs": "model-dependent",
    "tools": "model-dependent",
    "reasoning": "model-dependent"
  },
  "scientific_controls": {
    "pin_provider": "recommended",
    "pin_quantization": "critical if available",
    "record_latency": true,
    "record_tokens": true,
    "allow_fallback_in_confirmatory": false
  },
  "best_use": ["model sweep", "quantization study", "cross-family verifier"],
  "risks": ["provider routing", "quantization drift", "key/account heterogeneity"]
}
```

---

# 5. Routing policies

## 5.1 FixedScientificPolicy

يستخدم في confirmatory experiments.

- model ثابت.
- provider ثابت إن أمكن.
- quantization ثابت إن أمكن.
- لا fallback إلا إذا كان مسجلًا كفشل للتجربة.

## 5.2 ExploratoryFallbackPolicy

يستخدم في التجارب الاستكشافية.

- جرّب المفاتيح كلها.
- جرّب موديلات بديلة.
- سجّل كل fallback.
- لا تستنتج قانونًا.

## 5.3 CostOptimizedPolicy

يستخدم في البحث الطويل.

- موديل رخيص أولًا.
- escalation إلى موديل أقوى عند انخفاض الثقة.
- caching إن أمكن.
- مناسب لجولات online/offline.

## 5.4 CrossFamilyPolicy

يستخدم لاختبار verifier bias.

- actor من عائلة.
- verifier من عائلة مختلفة.
- يمنع نفس العائلة إلا كـ baseline.

---

# 6. كيف نستخدم كل مورد علميًا؟

## OpenRouter

### أفضل استخدام

1. model family sweep.
2. quantization experiment.
3. quick pilots.
4. cross-family verifier matrix.

### ضوابط علمية

- لا تستخدم fallback في confirmatory.
- سجل model id.
- حاول ضبط `provider.quantizations`.
- سجل failures وHTTP status.

---

## Gemini

### أفضل استخدام

1. cross-family verifier.
2. long-context stress.
3. structured outputs.
4. tasks تحتاج سياق كبير.

### ضوابط

- افصل AIza keys عن أي tokens أخرى.
- لا تستخدم مفاتيح غير واضحة النوع.
- سجل model version.

---

## NVIDIA NIM

### أفضل استخدام

1. high-throughput sampling.
2. large-k SC experiments.
3. fast verifier/generator tests.

### ضوابط

- سجل exact model id.
- سجل throughput وlatency.
- لا تخلط مع OpenRouter داخل نفس confirmatory arm.

---

## Mistral

### أفضل استخدام

1. cross-family verifier ضد Llama.
2. structured JSON output.
3. code/reasoning variants.

### ضوابط

- استخدمه كـ verifier control.
- قارن same-family vs cross-family.

---

## SiliconFlow

### أفضل استخدام

1. Qwen/DeepSeek family access.
2. cross-family actor/verifier.

### ضوابط

- لا يدخل confirmatory قبل smoke test.
- سجل model list/pricing.

---

## Serper

### أفضل استخدام

- discovery layer لجولات البحث.

### ضوابط

- لا تعتمد على snippets كدليل نهائي.
- استخدم Firecrawl لجلب الصفحة كاملة.

---

## Firecrawl

### أفضل استخدام

- scrape/crawl/extract structured evidence.

### ضوابط

- سجل URL ووقت الجلب.
- سجل raw markdown.
- استخدم schemas لاستخراج claims.

---

## Cloudflare Gateway

### أفضل استخدام

- production research mode.
- logging/caching/rate limiting.

### ضوابط

- لا تدخله في confirmatory إلا إذا ثبتنا إعداداته.
- سجل gateway id وcache hits.

---

## GitHub

### أفضل استخدام

- versioning.
- CI.
- حفظ outputs.

### ضوابط

- لا تستخدم PAT عام.
- أنشئ fine-grained token جديد لو احتجت.
- لا تدخل GitHub token في أي experiment runner.

---

# 7. تطبيق مباشر على EXP13

## Phase B الحالي

نستخدم OpenRouter فقط.

السياسة:

- ExploratoryFallbackPolicy في smoke tests.
- FixedScientificPolicy لاحقًا إذا أمكن pin provider/quantization.

## بعد EXP13

نبني تجربتين:

### Experiment Q — Quantization Effect

- actor ثابت.
- نفس tasks.
- quantization مختلف.
- قياس error topology.

### Experiment V — Cross-Family Verifier Matrix

- Llama actor.
- verifiers: Llama, Mistral, Gemini, Qwen.
- قياس verifier gain وFPR.

---

# 8. القرار النهائي

نضيف مرونة استخدام كل الموارد، لكن ليس كـ chaos fallback.

القاعدة:

> كل مورد يدخل النظام بدور واضح، وسياسة routing واضحة، وmetadata كاملة. المرونة للاستكشاف؛ التثبيت للإثبات.

بهذا تتحول المفاتيح من مجرد “رصيد” إلى **مختبر موارد علمية**.
