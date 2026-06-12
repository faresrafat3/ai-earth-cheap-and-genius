# EXP0 Instrument Stability Calibration Report

This is a calibration run: it tests whether answer topology is stable across repeated sessions.

## Overall stability
| tasks | generations | top-answer stable | SC-answer stable | SC-correct stable | mean dist overlap | mean margin range | mean entropy range |
|---|---|---|---|---|---|---|---|
| 1 | 4 | 100.0% | 100.0% | 100.0% | 1.00 | 0.00 | 0.00 |

## By session
| session | tasks | single | SC | mean margin | mean entropy |
|---|---|---|---|---|---|
| 0 | 1 | 100.0% | 100.0% | 2.00 | -0.00 |
| 1 | 1 | 100.0% | 100.0% | 2.00 | -0.00 |

## Unstable tasks
No unstable tasks by top-answer or SC-correct criteria.

## Decision rule
Preliminary pass: instrument stability is sufficient to proceed to EXP13C, with caveats about unpinned provider/quantization.

## Caveats
- OpenRouter provider/quantization may be unpinned unless explicit constraints were used.
- This calibrates the operational stack used, not a pure model in isolation.
- If exploratory fallback occurred, inspect generations.jsonl failures/retries.
