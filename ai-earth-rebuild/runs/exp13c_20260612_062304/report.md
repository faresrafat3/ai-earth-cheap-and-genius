# EXP13C Early Topology Prediction Report

Question: can first k0 samples predict SC@10 outcome?

## Overall
| tasks | generations | single | SC@10 | early unanimous | mean early entropy |
|---|---|---|---|---|---|
| 1 | 4 | 100.0% | 100.0% | 100.0% | -0.00 |

## By difficulty
| difficulty | n | single | SC@10 | early unanimous | early entropy |
|---|---|---|---|---|---|
| easy | 1 | 100.0% | 100.0% | 100.0% | -0.00 |

## By early topology bin (no ground truth)
| early bin | n | single | SC@10 | unanimous | entropy |
|---|---|---|---|---|---|
| early-unanimous | 1 | 100.0% | 100.0% | 100.0% | -0.00 |
| early-split-2 | 0 | 0.0% | 0.0% | 0.0% | 0.00 |
| early-scattered-3 | 0 | 0.0% | 0.0% | 0.0% | 0.00 |
| parse-risk | 0 | 0.0% | 0.0% | 0.0% | 0.00 |

## Diagnostic: early top correct vs SC@10
| bin | n | single | SC@10 |
|---|---|---|---|
| early_top_correct | 1 | 100.0% | 100.0% |
| early_top_wrong | 0 | 0.0% | 0.0% |

## SC@10 failures
No SC@10 failures.

## Readout
No failures occurred; this run cannot strongly test prediction. It only shows SC@10 is saturated on this task set.
