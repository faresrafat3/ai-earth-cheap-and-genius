# EXP13 Phase B — Real Model Pilot Results

## Run

- Run directory: `ai-earth-rebuild/runs/exp13_real_20260612_033534/`
- Model: `meta-llama/llama-3.1-8b-instruct`
- Provider: OpenRouter, unpinned provider/quantization
- Policy: exploratory
- Tasks: 45 total
  - 15 easy
  - 15 medium
  - 15 hard
- Samples per task: `k = 10`
- Temperature: `0.7`
- Total generations: 450

## Main result

| metric | value |
|---|---:|
| single-sample accuracy | 90.2% |
| self-consistency accuracy | 97.8% |
| SC gain | +7.6 pts |
| mean mode margin | 8.24 |
| mean wrong-mode dominance | 0.08 |
| mean answer entropy | 0.21 |
| mean pairwise error agreement | 0.08 |

## By difficulty

| difficulty | single | SC | gain | mean margin | wrong dominance |
|---|---:|---:|---:|---:|---:|
| easy | 99.3% | 100.0% | +0.7 | 9.87 | 0.01 |
| medium | 84.7% | 93.3% | +8.7 | 7.00 | 0.15 |
| hard | 86.7% | 100.0% | +13.3 | 7.87 | 0.08 |

## By mode-margin bin

| bin | n | single | SC | gain | wrong dominance | error agreement |
|---|---:|---:|---:|---:|---:|---:|
| `mode_margin > 0` | 44 | 92.3% | 100.0% | +7.7 | 0.06 | 0.06 |
| `mode_margin = 0` | 0 | — | — | — | — | — |
| `mode_margin < 0` | 1 | 0.0% | 0.0% | 0.0 | 1.00 | 1.00 |

## Preregistered readout

- SC accuracy when `mode_margin > 0`: **100.0%** (`n=44`)
- SC accuracy when `mode_margin <= 0`: **0.0%** (`n=1`)
- Difference: **+100 pts**

## Single SC failure

Only one task had SC failure:

```text
task_id: medium_010
truth: 1499
all 10 samples: 1489
mode_margin: -10
wrong_mode_dominance: 1.0
SC answer: 1489
```

Interpretation: this is exactly the failure pattern predicted by the hypothesis: a dominant wrong mode fully captured the vote.

## Usage / operational metadata

| metric | value |
|---|---:|
| prompt tokens | 54,167 |
| completion tokens | 70,805 |
| mean latency | 2.8s |
| median latency | 2.5s |
| max latency | 9.87s |
| total retry count | 45 |
| calls with retry | 45 |
| repeated failure type | HTTP 402 |

Interpretation: one OpenRouter key/account appeared out of quota and was skipped repeatedly. Because policy was exploratory, fallback succeeded. This is acceptable for pilot, not for confirmatory.

## Evidence strength

This pilot **supports the measurement idea**, but does **not** fully confirm the hypothesis.

Why?

- Almost all tasks landed in `mode_margin > 0`.
- There was only one negative-margin task.
- Therefore, the experiment did not produce enough hard failure cases to robustly estimate separation.

## What is supported

We can say:

> In this real-model pilot, whenever the correct answer was the dominant mode, SC succeeded; the only SC failure occurred when a wrong answer dominated all samples.

This supports the intuition that error topology is relevant.

## What is not yet supported

We cannot yet say:

> mode_margin reliably predicts SC success across a broad range of regimes.

Because we need more tasks where `mode_margin <= 0` or near zero.

## Next design implication

The next run should not simply increase `n`. It should deliberately create more borderline/hard cases.

Options:

1. Increase task difficulty beyond 11 steps.
2. Add division or parentheses.
3. Use larger numbers.
4. Raise temperature to 1.0.
5. Switch to a weaker or more error-prone model.
6. Construct adversarial arithmetic chains likely to induce systematic wrong modes.

## Scientific conclusion

This pilot is a **positive smoke/pilot result** for the error-topology hypothesis, but it is not a confirmatory test.

The key next requirement is:

> Generate enough `mode_margin <= 0` and near-zero cases to test whether the separation holds under genuine ambiguity/failure.
