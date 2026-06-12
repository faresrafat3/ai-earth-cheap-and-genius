# EXP13C-Balanced — Results

## Run

- Directory: `ai-earth-rebuild/runs/exp13c_balanced_20260612_064725/`
- Model: `meta-llama/llama-3.1-8b-instruct`
- Provider: OpenRouter
- Policy: exploratory
- Temperature: 0.7
- k0 = 3
- k = 10
- max_pool = 80
- target_per_bin = 5
- step options: 8, 11, 14, 17

## Why this run matters

EXP13C was saturated:

- 18 early-unanimous
- 2 early-split
- 0 early-scattered

EXP13C-Balanced intentionally selected a balanced-ish set after pre-screening to test whether early topology is actually predictive.

---

## Screening pool

The pre-screening stopped after 20 tasks because it already found enough examples:

| early bin | count in screened pool |
|---|---:|
| early-unanimous | 7 |
| early-split-2 | 5 |
| early-scattered-3 | 8 |

Selected set:

- 5 early-unanimous
- 5 early-split-2
- 5 early-scattered-3

---

## Main result

| early bin | n | single accuracy | SC@10 accuracy | early entropy |
|---|---:|---:|---:|---:|
| early-unanimous | 5 | 96.0% | 100.0% | 0.00 |
| early-split-2 | 5 | 48.0% | 60.0% | 0.64 |
| early-scattered-3 | 5 | 2.0% | 0.0% | 1.10 |

Overall:

| metric | value |
|---|---:|
| selected tasks | 15 |
| selected generations | 150 |
| single accuracy | 48.7% |
| SC@10 accuracy | 53.3% |
| mean early entropy | 0.58 |

---

## Readout

- SC@10 early-unanimous: **100.0%**
- SC@10 non-unanimous/risky: **30.0%**

This is the strongest evidence so far that early topology has predictive value.

Unlike EXP13, this is not purely diagnostic, because the predictor uses only k0=3 early samples, while the outcome is SC@10.

---

## SC@10 failures

Failures were concentrated in early-split and early-scattered bins.

Examples:

### early-split failure

```text
task: pool_0005_s17
truth: 2481576
early answers: 8 ×1, 13 ×2
SC@10 answer: 13
full margin: -2
```

### early-scattered failure

```text
task: pool_0000_s17
truth: 319365
early answers: 3042 ×1, 9126 ×1, 13 ×1
SC@10 answer: 3
full margin: -3
```

### early-scattered with correct present early but still failed

```text
task: pool_0009_s14
truth: 107901
early answers: 6 ×1, 13 ×1, 107901 ×1
SC@10 answer: 13 or 7 mode region
full margin: -1
```

Interpretation:

> Seeing the correct answer once in k0=3 is not enough. The key is whether there is early stability/dominance.

---

## Operational metadata

| metric | value |
|---|---:|
| API generations | 165 |
| prompt tokens | 23,382 |
| completion tokens | 33,693 |
| mean latency | 4.22s |
| median latency | 4.00s |
| max latency | 13.85s |
| total retries | 38 |
| calls with retry | 38 |
| failure types | HTTP 402 ×19, HTTP 401 ×19 |

Caveat: exploratory fallback was active. This remains a pilot, not fixed-instrument confirmatory evidence.

---

## Scientific interpretation

EXP13C-Balanced changes the status of the early topology idea.

Before:

> Early topology was promising but underpowered.

Now:

> Early topology meaningfully separates safe vs risky regimes in a deliberately balanced sample.

The strongest practical signal is:

- early-unanimous → very safe in this run.
- early-scattered → very risky.
- early-split → intermediate.

---

## What this does NOT prove

It does not prove a general law because:

- n is small: 15 selected tasks.
- task selection was based on pre-screening.
- provider/quantization unpinned.
- only one model family.
- only arithmetic-chain tasks.

But it does prove that the next research direction is no longer just diagnostic.

We now have a candidate practical policy:

> Use k0=3 as a cheap routing probe. If early-unanimous, SC@10 may be unnecessary. If early-split/scattered, escalate.

---

## Next logical step

Not more theory.

The next experiment should test a routing policy:

# EXP14 — Early Topology Routing Policy

Policy:

- If k0=3 early-unanimous: stop early and use the unanimous answer.
- If early-split/scattered: escalate to k=10 or verifier.

Compare:

1. Always single sample.
2. Always SC@10.
3. Early-topology routing.

Primary metric:

- accuracy per generation or cost/correct.

This would test whether early topology is not only predictive, but economically useful.
