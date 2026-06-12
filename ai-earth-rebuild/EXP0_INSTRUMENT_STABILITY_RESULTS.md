# EXP0 — Instrument Stability Calibration Results

## Run

- Directory: `ai-earth-rebuild/runs/exp0_20260612_054336/`
- Model: `meta-llama/llama-3.1-8b-instruct`
- Provider: OpenRouter
- Policy: exploratory
- Provider/quantization: unpinned
- Tasks: 20
  - 7 easy
  - 7 medium
  - 6 hard
- Sessions: 3
- Samples per task per session: k=10
- Total generations: 600
- Temperature: 0.7

---

## Main stability result

| metric | value |
|---|---:|
| top-answer stable across sessions | 100.0% |
| SC-answer stable across sessions | 100.0% |
| SC-correct stable across sessions | 100.0% |
| mean distribution overlap | 0.91 |
| mean mode-margin range | 1.60 |
| mean entropy range | 0.24 |

## By session

| session | single accuracy | SC accuracy | mean mode margin | mean entropy |
|---|---:|---:|---:|---:|
| 0 | 82.5% | 85.0% | 6.90 | 0.22 |
| 1 | 83.5% | 85.0% | 7.25 | 0.23 |
| 2 | 81.0% | 85.0% | 6.55 | 0.21 |

---

## Key finding

The operational stack produced **stable top answers and stable SC outcomes** across three independent sessions for all 20 tasks.

This means:

> For this specific operational setup, answer topology appears stable enough to justify moving to EXP13C, with caveats.

---

## Stable wrong attractors

Three tasks failed SC in every session. These are scientifically important because they show persistent wrong attractors.

### `medium_001`

- truth: `13937`
- SC answer every session: `13907`
- repeated wrong mode across sessions.

### `hard_002`

- truth: `13502`
- SC answer every session: `13402`
- wrong answer dominated every session.

### `hard_004`

- truth: `329828`
- SC answer every session: `329348`
- wrong answer dominated every session.

Interpretation:

> These are not random failures. They appear to be stable wrong attractors under this model/prompt/sampling setup.

This strengthens the new idea that SC amplifies the strongest attractor, whether correct or wrong.

---

## Operational metadata

| metric | value |
|---|---:|
| prompt tokens | 71,842 |
| completion tokens | 93,147 |
| mean latency | 2.92s |
| median latency | 2.69s |
| max latency | 9.42s |
| total retries | 225 |
| calls with retry | 225 |
| failure types | HTTP 401 × 150, HTTP 402 × 75 |

## Important caveat

The run used exploratory fallback. Many calls had retries due to invalid/out-of-quota keys.

Therefore:

- This is acceptable as operational calibration.
- It is not a fully fixed-instrument confirmatory run.
- However, despite fallback, top-answer and SC-correct outcomes were stable across sessions.

---

## Decision rule

Original threshold:

- top-answer stability ≥ 80%
- SC-correct stability ≥ 90%

Observed:

- top-answer stability = 100%
- SC-correct stability = 100%

## Decision

Preliminary pass.

We may proceed to EXP13C, but must retain caveats:

1. Provider/quantization still unpinned.
2. Exploratory fallback happened often.
3. EXP13C should either:
   - run with fixed policy and clean key, or
   - explicitly remain exploratory.

---

## What EXP0 changed

Before EXP0, the concern was:

> Maybe answer topology is unstable across sessions, so EXP13C would be meaningless.

After EXP0:

> In this operational setup, topology was surprisingly stable across sessions, including wrong attractors.

This makes EXP13C logically justified.

---

## Next step

Proceed to:

# EXP13C — Early Topology Prediction

Core question:

> Can topology measured from the first k0=3 samples predict SC@10 outcome?

EXP0 says this is now worth testing, because the answer distributions are stable enough across repeated sessions to be meaningful.
