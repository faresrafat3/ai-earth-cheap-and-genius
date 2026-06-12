# EXP13 Phase A Report — Error Topology Dry Run

**Status:** simulation/dry-run only. This validates the measurement pipeline; it is not evidence about real LLMs.

## 1. Overall
| n task-temp cells | single acc | SC acc | SC gain | mean margin | wrong dom | entropy | err agree |
|---|---|---|---|---|---|---|---|
| 30 | 64.7% | 76.7% | 12.0% | 1.83 | 0.28 | 0.51 | 0.24 |

## 2. By Difficulty
| difficulty | n | single | SC | gain | margin | wrong_dom |
|---|---|---|---|---|---|---|
| easy | 10 | 90.0% | 100.0% | 10.0% | 4.10 | 0.08 |
| hard | 10 | 36.0% | 40.0% | 4.0% | -0.90 | 0.54 |
| medium | 10 | 68.0% | 90.0% | 22.0% | 2.30 | 0.22 |

## 2. By Temperature
| temperature | n | single | SC | gain | margin | wrong_dom |
|---|---|---|---|---|---|---|
| 0.2 | 15 | 69.3% | 73.3% | 4.0% | 2.07 | 0.28 |
| 0.7 | 15 | 60.0% | 80.0% | 20.0% | 1.60 | 0.28 |

## 3. By mode-margin bin
| bin | n | single | SC | gain | wrong_dom | err_agree |
|---|---|---|---|---|---|---|
| margin > 0 | 21 | 81.9% | 100.0% | 18.1% | 0.12 | 0.05 |
| margin = 0 | 2 | 40.0% | 100.0% | 60.0% | 0.40 | 0.33 |
| margin < 0 | 7 | 20.0% | 0.0% | -20.0% | 0.71 | 0.80 |

## 4. Failure taxonomy
| reason | count |
|---|---|
| SC correct | 23 |
| wrong mode >= correct mode | 5 |
| no correct samples | 2 |

## 5. Preregistered readout
SC accuracy when margin > 0: **100.0%** (n=21)
SC accuracy when margin <= 0: **22.2%** (n=9)
Difference: **77.8%**

**Dry-run pattern:** supports the measurement logic: mode_margin separates SC success from failure in the simulator.

## 6. Files
- `generations.jsonl`: every sample.
- `task_metrics.jsonl`: per task × temperature metrics.
