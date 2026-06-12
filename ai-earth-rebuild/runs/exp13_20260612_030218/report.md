# EXP13 Phase A Report — Error Topology Dry Run

**Status:** simulation/dry-run only. This validates the measurement pipeline; it is not evidence about real LLMs.

## 1. Overall
| n task-temp cells | single acc | SC acc | SC gain | mean margin | wrong dom | entropy | err agree |
|---|---|---|---|---|---|---|---|
| 360 | 53.8% | 75.6% | 21.8% | 2.91 | 0.25 | 1.01 | 0.24 |

## 2. By Difficulty
| difficulty | n | single | SC | gain | margin | wrong_dom |
|---|---|---|---|---|---|---|
| easy | 120 | 77.1% | 99.2% | 22.1% | 6.45 | 0.13 |
| hard | 120 | 31.9% | 41.7% | 9.8% | -0.60 | 0.38 |
| medium | 120 | 52.4% | 85.8% | 33.4% | 2.87 | 0.24 |

## 2. By Temperature
| temperature | n | single | SC | gain | margin | wrong_dom |
|---|---|---|---|---|---|---|
| 0.2 | 120 | 63.4% | 81.7% | 18.2% | 3.77 | 0.26 |
| 0.7 | 120 | 53.4% | 77.5% | 24.1% | 2.89 | 0.25 |
| 1.0 | 120 | 44.6% | 67.5% | 22.9% | 2.05 | 0.24 |

## 3. By mode-margin bin
| bin | n | single | SC | gain | wrong_dom | err_agree |
|---|---|---|---|---|---|---|
| margin > 0 | 254 | 65.5% | 100.0% | 34.5% | 0.18 | 0.19 |
| margin = 0 | 39 | 33.6% | 46.2% | 12.6% | 0.34 | 0.32 |
| margin < 0 | 67 | 21.2% | 0.0% | -21.2% | 0.47 | 0.41 |

## 4. Failure taxonomy
| reason | count |
|---|---|
| SC correct | 272 |
| wrong mode >= correct mode | 84 |
| no correct samples | 4 |

## 5. Preregistered readout
SC accuracy when margin > 0: **100.0%** (n=254)
SC accuracy when margin <= 0: **17.0%** (n=106)
Difference: **83.0%**

**Dry-run pattern:** supports the measurement logic: mode_margin separates SC success from failure in the simulator.

## 6. Files
- `generations.jsonl`: every sample.
- `task_metrics.jsonl`: per task × temperature metrics.
