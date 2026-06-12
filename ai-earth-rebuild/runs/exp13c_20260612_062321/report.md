# EXP13C Early Topology Prediction Report

Question: can first k0 samples predict SC@10 outcome?

## Overall
| tasks | generations | single | SC@10 | early unanimous | mean early entropy |
|---|---|---|---|---|---|
| 20 | 200 | 92.0% | 95.0% | 90.0% | 0.06 |

## By difficulty
| difficulty | n | single | SC@10 | early unanimous | early entropy |
|---|---|---|---|---|---|
| easy | 7 | 100.0% | 100.0% | 100.0% | -0.00 |
| hard | 6 | 88.3% | 100.0% | 83.3% | 0.11 |
| medium | 7 | 87.1% | 85.7% | 85.7% | 0.09 |

## By early topology bin (no ground truth)
| early bin | n | single | SC@10 | unanimous | entropy |
|---|---|---|---|---|---|
| early-unanimous | 18 | 97.8% | 100.0% | 100.0% | -0.00 |
| early-split-2 | 2 | 40.0% | 50.0% | 0.0% | 0.64 |
| early-scattered-3 | 0 | 0.0% | 0.0% | 0.0% | 0.00 |
| parse-risk | 0 | 0.0% | 0.0% | 0.0% | 0.00 |

## Diagnostic: early top correct vs SC@10
| bin | n | single | SC@10 |
|---|---|---|---|
| early_top_correct | 18 | 97.8% | 100.0% |
| early_top_wrong | 2 | 40.0% | 50.0% |

## SC@10 failures
| task | difficulty | truth | early_answers | full_answers | early_bin | full_margin |
|---|---|---|---|---|---|---|
| medium_002 | medium | 38540 | {'38500': 2, '38492': 1} | {'38500': 4, '38492': 1, '9605': 1, '9635': 1, '38540': 2, '38420': 1} | early-split-2 | -2 |

## Readout
Preliminary pattern: early topology separates some SC@10 outcomes.
