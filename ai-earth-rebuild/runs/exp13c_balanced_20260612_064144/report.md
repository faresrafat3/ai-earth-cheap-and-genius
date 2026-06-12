# EXP13C-Balanced Report

Balanced pilot: pre-screen early topology, then complete selected tasks to SC@10.

## Screening pool bins
| bin | count |
|---|---|
| early-unanimous | 4 |
| early-scattered-3 | 1 |

## Selected set overall
| selected tasks | selected generations | single | SC@10 | mean early entropy |
|---|---|---|---|---|
| 2 | 10 | 70.0% | 50.0% | 0.55 |

## By early bin
| early bin | n | single | SC@10 | early entropy |
|---|---|---|---|---|
| early-unanimous | 1 | 100.0% | 100.0% | -0.00 |
| early-split-2 | 0 | 0.0% | 0.0% | 0.00 |
| early-scattered-3 | 1 | 40.0% | 0.0% | 1.10 |
| parse-risk | 0 | 0.0% | 0.0% | 0.00 |

## SC@10 failures
| task | steps | truth | early_bin | early_answers | full_answers | full_margin |
|---|---|---|---|---|---|---|
| pool_0001_s11 | 11 | 79093 | early-scattered-3 | {'78793': 1, '790': 1, '79093': 1} | {'78793': 2, '790': 1, '79093': 2} | 0 |

## Readout
SC@10 early-unanimous: **100.0%**
SC@10 non-unanimous/risky: **0.0%**
Preliminary support: non-unanimous early topology is riskier than early-unanimous.
