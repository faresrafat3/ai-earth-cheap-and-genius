# EXP13 Phase B Real Pilot Report

**Status:** real-model pilot. Exploratory unless run with preregistered full settings.

## Overall
| n tasks | single | SC | gain | margin | wrong_dom | entropy | err_agree |
|---|---|---|---|---|---|---|---|
| 45 | 90.2% | 97.8% | 7.6% | 8.24 | 0.08 | 0.21 | 0.08 |

## By Difficulty
| difficulty | n | single | SC | gain | margin | wrong_dom |
|---|---|---|---|---|---|---|
| easy | 15 | 99.3% | 100.0% | 0.7% | 9.87 | 0.01 |
| hard | 15 | 86.7% | 100.0% | 13.3% | 7.87 | 0.08 |
| medium | 15 | 84.7% | 93.3% | 8.7% | 7.00 | 0.15 |

## By mode-margin bin
| bin | n | single | SC | gain | wrong_dom | err_agree |
|---|---|---|---|---|---|---|
| margin > 0 | 44 | 92.3% | 100.0% | 7.7% | 0.06 | 0.06 |
| margin = 0 | 0 | 0.0% | 0.0% | 0.0% | 0.00 | 0.00 |
| margin < 0 | 1 | 0.0% | 0.0% | 0.0% | 1.00 | 1.00 |

## Preregistered readout
SC accuracy margin > 0: **100.0%** (n=44)
SC accuracy margin <= 0: **0.0%** (n=1)
Difference: **100.0%**

## Usage
calls: recorded per-generation in `generations.jsonl`
prompt_tokens/completion_tokens: recorded per-generation in `generations.jsonl`
latency/retries/failures: recorded per-generation in `generations.jsonl`

## Limitations
- Provider/quantization are not pinned; treat this as pilot evidence only.
- Prompt sensitivity not swept.
- Small n if smoke settings used.
