# تدقيق القدرات والفرص داخل المفاتيح/المزوّدين

> الغرض: فهم ما يمكن أن يفيد مشروع AI Earth من كل مزوّد، بدون حفظ الأسرار أو نشرها داخل الكود.

## تحذير أمان

المفاتيح أُرسلت داخل الشات، وبالتالي تعتبر مكشوفة. يجب عمل revoke/rotate لها بعد الانتهاء.

هذه الوثيقة **لا تحتوي أي مفتاح حقيقي**. التصنيف مبني على نوع المفتاح والمزوّد والوثائق العامة وبعض smoke tests المحدودة لـ OpenRouter فقط.

---

# 1. التصنيف العام حسب الأهمية لمشروعنا

## أعلى أولوية

1. **OpenRouter**  
   أفضل مزوّد لتجارب مقارنة النماذج بسرعة؛ يدعم routing، quantization filters، أسعار متعددة، وموديلات كثيرة.

2. **Google AI Studio / Gemini**  
   مهم جدًا لتجارب long-context، structured reasoning، وربما context caching.

3. **NVIDIA NIM**  
   مهم لتجارب سرعة/throughput وموديلات مفتوحة قوية عبر OpenAI-compatible endpoint.

4. **Firecrawl + Serper**  
   مهمان لجولات البحث الأونلاين: جمع أوراق، صفحات، مصادر، markdown، واستخراج structured evidence.

5. **Cloudflare AI Gateway / Workers AI**  
   مهم كطبقة orchestration: logging, caching, rate limiting, guardrails، وربما بوابة موحدة للموديلات.

## أولوية متوسطة

6. **Mistral Studio**  
   مفيد للتجارب structured outputs، reasoning models، Codestral، وربما verifier cross-family.

7. **SiliconFlow**  
   غالبًا بوابة لنماذج صينية/مفتوحة؛ مفيد كـ cross-family verifier أو generator بديل.

8. **GitHub token / GitHub Models**  
   خطر أمني عالي. مفيد فقط لو نحتاج GitHub Models أو repo automation، لكن لا يجب استخدامه داخل التجارب.

## أولوية منخفضة/غير واضحة

9. **llm7 / Agnes / Tinker**  
   نحتاج توثيق أو endpoint واضح قبل إدخالها في pipeline. لا تُستخدم في تجربة علمية قبل معرفة model list، pricing، logging، stability.

---

# 2. تحليل مزوّد بمزوّد

## 2.1 OpenRouter

### ما نعرفه

- مفاتيح متعددة.
- بعض المفاتيح أعطت 401/402 أثناء smoke test، لكن rotation وجد مفتاحًا شغالًا.
- مناسب جدًا للتجارب السريعة.

### الفرص المخفية المهمة

#### 1. تثبيت quantization

OpenRouter يسمح بتحديد quantization مثل `fp8`, `fp16`, `bf16`, `int8`, `int4` عبر `provider.quantizations`.

هذه فرصة مهمة جدًا لأن تدقيقنا v2 كشف أن عدم تثبيت quantization يهدد صلاحية التجربة.

**الاستخدام المقترح:**

```json
"provider": {
  "quantizations": ["fp16", "bf16"]
}
```

أو تجربة مقارنة:

- fp16/bf16
- fp8
- int4/int8

لرؤية أثر quantization على error topology.

#### 2. تثبيت provider routing

OpenRouter يحمّل الطلبات عبر مزوّدين حسب السعر/التوفر. هذا مفيد عمليًا، لكنه خطر علميًا.

**للإنتاج:** routing جيد.  
**للتجربة:** يجب تثبيته أو تسجيل provider metadata إن أمكن.

#### 3. فحص models/features

OpenRouter يعرض features مثل:

- tools
- json_mode
- structured_outputs
- logprobs
- web_search
- reasoning

**فرصة:** اختيار موديلات تدعم structured output لتقليل parsing failures في EXP13.

### أفضل استعمال في AI Earth

- مقارنة model families.
- قياس error topology.
- اختبار quantization effect.
- cross-family verifier experiments.

### المخاطر

- مفاتيح متعددة قد تعني accounts متعددة ورصيد غير متجانس.
- 401/402 موجودة.
- routing غير مثبت يلوث النتائج.

### قرار

استخدمه، لكن للتجارب العلمية يجب إضافة:

- provider constraints.
- quantization constraints.
- model metadata logging.

---

## 2.2 Google AI Studio / Gemini

### ما نعرفه

المفاتيح من نوعين:

- مفاتيح `AIza...` وهي API keys تقليدية.
- سلاسل `AQ...` قد تكون OAuth/session-like وليست Gemini API keys مباشرة.

### الفرص

1. **long context**  
   Gemini مفيد جدًا لاختبار هل error correlation يتغير مع طول السياق.

2. **context caching**  
   مفيد لو نكرر نفس prompt/system/instructions كثيرًا لتقليل التكلفة.

3. **cross-family verifier**  
   Gemini كـ verifier لعينة من Llama outputs سيكون اختبارًا ممتازًا لـ family bias.

4. **structured outputs**  
   مفيد لتقليل parser artifacts.

### المخاطر

- API keys يجب تقييدها في Google Cloud/AI Studio.
- مفاتيح `AQ...` غير واضحة وقد لا تكون صالحة كـ API keys.
- لا نستخدم أي Google key قبل تصنيف نوعه.

### قرار

مفيد جدًا كـ cross-family verifier، لكن لا نستخدمه إلا بعد:

- تأكيد أن المفتاح API key صالح.
- تقييده على Generative Language API.
- تسجيل model/version.

---

## 2.3 NVIDIA NIM

### الفرص

- OpenAI-compatible endpoint.
- موديلات مفتوحة كثيرة.
- سرعة عالية محتملة.
- مناسب لتجارب large sample لأن throughput قد يكون أفضل.

### أفضل استعمال

1. تشغيل EXP13 بعدد عينات أكبر.
2. مقارنة سرعة/تكلفة/دقة ضد OpenRouter.
3. استخدام موديلات غير Llama كـ verifier أو generator.

### المخاطر

- credits محدودة.
- model catalog يتغير.
- يجب تسجيل model exact id.

### قرار

فرصة قوية جدًا لتجارب error topology واسعة إذا كان الرصيد كافيًا.

---

## 2.4 Firecrawl

### الفرص

- scrape صفحات إلى markdown.
- crawl مواقع.
- extract structured JSON من صفحات.
- مناسب لجولات online/offline التي طلبتها.

### أفضل استعمال في مشروعنا

1. جمع أوراق وروابط من صفحات arXiv/OpenReview/blogs.
2. تحويل صفحات لأدلة structured.
3. بناء evidence database.
4. استخراج claims/methods/metrics من الأوراق.

### المخاطر

- يستهلك credits بسرعة عند crawl واسع.
- قد يجلب محتوى noisy.

### قرار

مفيد جدًا كـ ingestion layer، لكنه ليس جزءًا من تجربة LLM reasoning نفسها.

---

## 2.5 Serper

### الفرص

- البحث السريع في Google results.
- مناسب لجولة online الأولى.
- أرخص/أسرع من scraping كامل.

### أفضل استعمال

Pipeline:

1. Serper لجلب candidates.
2. Firecrawl لجلب محتوى الصفحات المهمة.
3. LLM لتلخيص structured evidence.
4. offline audit لاستبعاد hype.

### المخاطر

- snippet-level evidence لا يكفي.
- لا نعتمد عليه وحده في الاستشهاد.

### قرار

ممتاز كـ discovery layer.

---

## 2.6 Cloudflare AI Gateway / Workers AI

### الفرص

- AI Gateway يوحد calling models عبر REST/OpenAI-compatible patterns.
- يعطي logging/caching/rate limiting/guardrails.
- ممكن يقلل التكلفة عبر caching.

### أفضل استعمال

1. وضع كل real-model experiments خلف gateway موحد.
2. تسجيل latency/cost/rate-limit مركزيًا.
3. تجربة caching للـ repeated prompts.
4. guardrails للحد من outputs غير صالحة.

### المخاطر

- يحتاج account_id وgateway config.
- قد يضيف طبقة أخرى تؤثر على reproducibility.

### قرار

مفيد كطبقة production/evaluation infrastructure، لكن ليس للـ confirmatory experiment الأولى إلا إذا ثبتنا إعداداته.

---

## 2.7 Mistral Studio

### الفرص

- cross-family verifier ممتاز ضد Llama.
- structured JSON outputs.
- Codestral للكود.
- reasoning models مثل Magistral حسب التوفر.

### أفضل استعمال

1. verifier cross-family.
2. structured extraction من outputs.
3. judge بديل لاختبار family self-preference.

### المخاطر

- pricing/model versions تحتاج ضبط.
- structured outputs تحتاج prompt واضح.

### قرار

أحد أفضل المرشحين لتجربة control ضد Llama-family verifier.

---

## 2.8 SiliconFlow

### الفرص

- غالبًا يوفر موديلات Qwen/DeepSeek وغيرها.
- مفيد جدًا كـ cross-family endpoint.

### أفضل استعمال

- Qwen verifier ضد Llama actor.
- Qwen actor ضد Mistral/Gemini verifier.

### المخاطر

- نحتاج توثيق endpoint/model list/pricing.
- لا ندخله في تجربة confirmatory قبل smoke tests.

### قرار

واعد، لكن يحتاج discovery آمن أولًا.

---

## 2.9 GitHub token / GitHub Models

### الخطر

هذا أخطر مفتاح أرسلته. قد يعطي صلاحيات repositories/packages/models حسب scopes.

### الفرص

- GitHub Models إن كان token يدعمها.
- repo automation.
- CI experiments.

### القرار الأمني

لا أستخدم هذا المفتاح هنا. يجب revoke فورًا.

إذا أردنا GitHub Models، الأفضل إنشاء fine-grained token جديد بصلاحية محدودة جدًا.

---

## 2.10 llm7 / Agnes / Tinker

### الحالة

غير واضحة بما يكفي.

### المطلوب قبل الاستخدام

- base URL.
- auth method.
- model list.
- pricing.
- rate limits.
- هل OpenAI-compatible؟
- هل returns token usage؟

### القرار

لا تدخل في تجارب علمية قبل توثيقها.

---

# 3. الفرص الجديدة التي ظهرت من التدقيق

## فرصة 1 — تجربة quantization effect

بسبب OpenRouter provider routing، يمكن تصميم تجربة صغيرة:

> نفس model id، نفس prompt، نفس tasks، لكن quantization مختلف.

نقيس:

- single accuracy.
- error topology.
- mode margin.
- wrong-mode dominance.

هذه تجربة مهمة لأن quantization قد يغير بنية الأخطاء.

## فرصة 2 — cross-family verifier matrix

بدل verifier أقوى فقط، نختبر:

| actor | verifier |
|---|---|
| Llama | Llama |
| Llama | Mistral |
| Llama | Gemini |
| Llama | Qwen/SiliconFlow |

الهدف:

> هل اختلاف العائلة يقلل FPR ويرفع verifier gain؟

## فرصة 3 — Evidence ingestion pipeline

استخدام:

- Serper = discovery.
- Firecrawl = full-page markdown/extract.
- LLM = structured summary.
- Offline audit = strict classification.

هذا يطبّق بالضبط بروتوكول online/offline/repeat.

## فرصة 4 — Cloudflare Gateway كطبقة قياس

لو ضُبط جيدًا، يمكنه تسجيل:

- latency.
- caching.
- rate limits.
- gateway-level logs.

وهذا يحسن Q5: التكلفة ليست tokens فقط، بل latency وretries.

## فرصة 5 — Gemini long-context stress

اختبار SC في long-context حيث positional/correlation bias يظهر أقوى.

---

# 4. الخريطة العملية للمفاتيح

## للـ EXP13 الحالي

استخدم فقط:

- OpenRouter

لأن الكود جاهز.

## للتجربة التالية بعد EXP13

استخدم:

- OpenRouter + Mistral/Gemini/SiliconFlow

لبناء cross-family verifier matrix.

## لجولات البحث

استخدم:

- Serper + Firecrawl

## للبنية التحتية لاحقًا

استخدم:

- Cloudflare AI Gateway

## لا تستخدم الآن

- GitHub PAT
- llm7
- Agnes
- Tinker

إلا بعد تدوير المفاتيح وتوثيق الصلاحيات.

---

# 5. توصية فورية

قبل تشغيل أي تجربة أكبر:

1. اعمل revoke لكل المفاتيح المكشوفة.
2. أنشئ مفاتيح جديدة محدودة الصلاحية:
   - OpenRouter فقط للتجارب.
   - Serper/Firecrawl فقط للبحث.
   - لا تستخدم GitHub PAT عام.
3. أضف ملف محلي خارج repo:
   - `/tmp/ai_earth_keys.env`
4. عدّل clients لتسجيل:
   - model id.
   - provider إن توفر.
   - quantization إن توفر.
   - token usage.
   - latency.
   - status/retry count.

---

# 6. القرار النهائي

أكبر فرصة مكتشفة ليست “مفتاح فيه رصيد”.

أكبر فرصة هي:

> استخدام تعدد المزوّدين لا كاحتياط فقط، بل كأداة علمية لاختبار family effects وquantization effects وverification gain.

يعني المفاتيح نفسها تتحول من مجرد access إلى **تصميم تجريبي**.
