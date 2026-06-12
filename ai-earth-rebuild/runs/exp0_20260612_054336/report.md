# EXP0 Instrument Stability Calibration Report

This is a calibration run: it tests whether answer topology is stable across repeated sessions.

## Overall stability
| tasks | generations | top-answer stable | SC-answer stable | SC-correct stable | mean dist overlap | mean margin range | mean entropy range |
|---|---|---|---|---|---|---|---|
| 20 | 600 | 100.0% | 100.0% | 100.0% | 0.91 | 1.60 | 0.24 |

## By session
| session | tasks | single | SC | mean margin | mean entropy |
|---|---|---|---|---|---|
| 0 | 20 | 82.5% | 85.0% | 6.90 | 0.22 |
| 1 | 20 | 83.5% | 85.0% | 7.25 | 0.23 |
| 2 | 20 | 81.0% | 85.0% | 6.55 | 0.21 |

## Unstable tasks
No unstable tasks by top-answer or SC-correct criteria.

## Decision rule
Preliminary pass: instrument stability is sufficient to proceed to EXP13C, with caveats about unpinned provider/quantization.

## Caveats
- OpenRouter provider/quantization may be unpinned unless explicit constraints were used.
- This calibrates the operational stack used, not a pure model in isolation.
- If exploratory fallback occurred, inspect generations.jsonl failures/retries.
