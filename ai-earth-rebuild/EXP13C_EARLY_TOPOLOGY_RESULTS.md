# EXP13C — Early Topology Prediction Results

## Run

- Directory: `ai-earth-rebuild/runs/exp13c_20260612_062321/`
- Model: `meta-llama/llama-3.1-8b-instruct`
- Provider: OpenRouter
- Policy: exploratory
- Tasks: 20
  - 7 easy
  - 7 medium
  - 6 hard
- k0 = 3 early samples
- k = 10 full samples
- Temperature: 0.7
- Total generations: 200

---

## Main result

| metric | value |
|---|---:|
| single-sample accuracy | 92.0% |
| SC@10 accuracy | 95.0% |
| early-unanimous tasks | 90.0% |
| mean early entropy | 0.06 |

## By difficulty

| difficulty | single | SC@10 | early unanimous |
|---|---:|---:|---:|
| easy | 100.0% | 100.0% | 100.0% |
| medium | 87.1% | 85.7% | 85.7% |
| hard | 88.3% | 100.0% | 83.3% |

---

## Early topology bins without ground truth

| early bin | n | single | SC@10 |
|---|---:|---:|---:|
| early-unanimous | 18 | 97.8% | 100.0% |
| early-split-2 | 2 | 40.0% | 50.0% |
| early-scattered-3 | 0 | — | — |
| parse-risk | 0 | — | — |

## Diagnostic with ground truth

| bin | n | single | SC@10 |
|---|---:|---:|---:|
| early top correct | 18 | 97.8% | 100.0% |
| early top wrong | 2 | 40.0% | 50.0% |

---

## SC@10 failure

One failure occurred:

```text
task: medium_002
truth: 38540
early answers: 38500 ×2, 38492 ×1
full answers:
  38500 ×4
  38540 ×2
  38492 ×1
  9605 ×1
  9635 ×1
  38420 ×1
full mode margin: -2
SC answer: 38500
```

Interpretation:

- Early topology already showed risk: no unanimity and early top answer was wrong.
- Full SC failed because a wrong answer remained the strongest mode.

---

## Operational metadata

| metric | value |
|---|---:|
| prompt tokens | 23,940 |
| completion tokens | 30,694 |
| mean latency | 3.66s |
| median latency | 3.05s |
| max latency | 15.91s |
| total retries | 45 |
| calls with retry | 45 |
| failure types | HTTP 402 ×23, HTTP 401 ×22 |

---

## Interpretation

EXP13C partially supports the practical idea:

> Early topology can flag some risky tasks before completing k=10.

Specifically:

- 18/18 early-unanimous tasks succeeded at SC@10.
- 1/2 early-split tasks failed.
- The only SC failure was already non-unanimous in the first 3 samples.

However, this is still not strong confirmatory evidence because:

- 90% of tasks were early-unanimous.
- Only 2 tasks were non-unanimous early.
- Only 1 SC@10 failure occurred.
- Provider/quantization were unpinned.
- Policy was exploratory with retries.

---

## What changed relative to EXP13?

EXP13 was diagnostic:

> full k=10 topology describes SC@10.

EXP13C is closer to predictive:

> k0=3 topology gave a warning signal for the only SC@10 failure.

But the sample is still too easy to claim a robust predictor.

---

## Decision

EXP13C gives a promising but underpowered signal.

The next scientifically necessary improvement is not more theory. It is a **balanced early-topology test** that intentionally samples enough non-unanimous early cases.

Proposed next step:

# EXP13C-Balanced

Procedure:

1. Generate a larger task pool.
2. Take k0=3 samples.
3. Stratify tasks into:
   - early-unanimous
   - early-split-2
   - early-scattered-3
4. Select balanced groups.
5. Complete each task to k=10.
6. Test whether early topology predicts SC@10 within a balanced set.

This avoids saturation and directly tests the predictive value of early topology.
