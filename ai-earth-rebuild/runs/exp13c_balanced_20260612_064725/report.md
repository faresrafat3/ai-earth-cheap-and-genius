# EXP13C-Balanced Report

Balanced pilot: pre-screen early topology, then complete selected tasks to SC@10.

## Screening pool bins
| bin | count |
|---|---|
| early-scattered-3 | 8 |
| early-unanimous | 7 |
| early-split-2 | 5 |

## Selected set overall
| selected tasks | selected generations | single | SC@10 | mean early entropy |
|---|---|---|---|---|
| 15 | 150 | 48.7% | 53.3% | 0.58 |

## By early bin
| early bin | n | single | SC@10 | early entropy |
|---|---|---|---|---|
| early-unanimous | 5 | 96.0% | 100.0% | -0.00 |
| early-split-2 | 5 | 48.0% | 60.0% | 0.64 |
| early-scattered-3 | 5 | 2.0% | 0.0% | 1.10 |
| parse-risk | 0 | 0.0% | 0.0% | 0.00 |

## SC@10 failures
| task | steps | truth | early_bin | early_answers | full_answers | full_margin |
|---|---|---|---|---|---|---|
| pool_0005_s17 | 17 | 2481576 | early-split-2 | {'8': 1, '13': 2} | {'8': 1, '13': 3, '221': 1, '7': 2, '3': 1, '2481576': 1, '22157': 1} | -2 |
| pool_0006_s14 | 14 | 187848 | early-split-2 | {'3912': 2, '187848': 1} | {'3912': 2, '187848': 2, '14': 3, '6': 3} | -1 |
| pool_0000_s17 | 17 | 319365 | early-scattered-3 | {'3042': 1, '9126': 1, '13': 1} | {'3042': 2, '9126': 1, '13': 1, '912': 1, '3': 3, '6': 1, '76': 1} | -3 |
| pool_0003_s17 | 17 | 219384 | early-scattered-3 | {'6': 1, '274': 1, '1136': 1} | {'6': 3, '274': 1, '1136': 1, '114': 1, '4': 1, '14': 1, '1142': 1, '13': 1} | -3 |
| pool_0008_s14 | 14 | 705686688 | early-scattered-3 | {'176096532': 1, '326006': 1, '7': 1} | {'176096532': 1, '326006': 1, '7': 3, '326104': 1, '8': 1, '325': 1, '12': 1, '326': 1} | -3 |
| pool_0009_s14 | 14 | 107901 | early-scattered-3 | {'6': 1, '13': 1, '107901': 1} | {'6': 1, '13': 2, '107901': 1, '7197': 1, '35960': 1, '35969': 1, '7': 2, '9': 1} | -1 |
| pool_0010_s14 | 14 | 11430818 | early-scattered-3 | {'1632969': 1, '13': 1, '11420925': 1} | {'1632969': 3, '13': 2, '11420925': 1, '163297': 2, '163': 2} | -3 |

## Readout
SC@10 early-unanimous: **100.0%**
SC@10 non-unanimous/risky: **30.0%**
Preliminary support: non-unanimous early topology is riskier than early-unanimous.
