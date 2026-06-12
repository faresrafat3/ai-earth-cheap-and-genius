# EXP13 Phase B Real Pilot Report

**Status:** real-model pilot. Exploratory unless run with preregistered full settings.

## Overall
| n tasks | single | SC | gain | margin | wrong_dom | entropy | err_agree |
|---|---|---|---|---|---|---|---|
| 3 | 100.0% | 100.0% | 0.0% | 2.00 | 0.00 | -0.00 | 0.00 |

## By Difficulty
| difficulty | n | single | SC | gain | margin | wrong_dom |
|---|---|---|---|---|---|---|
| easy | 1 | 100.0% | 100.0% | 0.0% | 2.00 | 0.00 |
| hard | 1 | 100.0% | 100.0% | 0.0% | 2.00 | 0.00 |
| medium | 1 | 100.0% | 100.0% | 0.0% | 2.00 | 0.00 |

## By mode-margin bin
| bin | n | single | SC | gain | wrong_dom | err_agree |
|---|---|---|---|---|---|---|
| margin > 0 | 3 | 100.0% | 100.0% | 0.0% | 0.00 | 0.00 |
| margin = 0 | 0 | 0.0% | 0.0% | 0.0% | 0.00 | 0.00 |
| margin < 0 | 0 | 0.0% | 0.0% | 0.0% | 0.00 | 0.00 |

## Preregistered readout
SC accuracy margin > 0: **100.0%** (n=3)
SC accuracy margin <= 0: **0.0%** (n=0)
Difference: **100.0%**

## Usage
calls: 6
prompt_tokens: 736
completion_tokens: 964
failures: {'HTTP 402': 1, 'HTTP 401': 1}

## Limitations
- Provider/quantization are not pinned; treat this as pilot evidence only.
- Prompt sensitivity not swept.
- Small n if smoke settings used.
