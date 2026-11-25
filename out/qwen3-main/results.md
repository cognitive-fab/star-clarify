# STAR-Clarify results: qwen3-30b-a3b-thinking-2507

Judge: mistral. Items: 396. Judge verdicts that could not be read (scored as no): 0.

## Summary

| Measure | base | skill | skill2 |
|---|---|---|---|
| STAR score (mean credit) | 0.753 | 0.927 | 0.944 |
| Clear items answered correctly | 95.3% (191) | 93.7% (191) | 95.3% (191) |
| Over-asking on clear items | 0.5% (191) | 4.2% (191) | 1.0% (191) |
| Ambiguity handled (asked or reading stated) | 31.2% (125) | 87.2% (125) | 89.6% (125) |
| Ambiguity resolved silently | 64.8% (125) | 12.8% (125) | 10.4% (125) |
| Missing quantity asked for | 100.0% (43) | 100.0% (43) | 100.0% (43) |
| Missing quantity guessed silently | 0.0% (43) | 0.0% (43) | 0.0% (43) |
| Impossible or contradictory detected | 91.9% (37) | 97.3% (37) | 100.0% (37) |
| Mean output tokens | 1695 | 3882 | 3546 |

## Paired comparison with base (same items)

| Condition | Better | Worse | Same | Sign test p |
|---|---|---|---|---|
| skill | 80 | 11 | 305 | 0.0000 |
| skill2 | 83 | 7 | 306 | 0.0000 |

## By category (mean credit)

| category | n | base | skill | skill2 |
|---|---|---|---|---|
| C1 | 50 | 1.00 | 0.96 | 0.98 |
| C10 | 40 | 1.00 | 1.00 | 0.95 |
| C2 | 40 | 0.00 | 0.88 | 0.88 |
| C3 | 60 | 0.50 | 1.00 | 1.00 |
| C4 | 33 | 0.61 | 0.64 | 0.76 |
| C5 | 30 | 0.93 | 0.87 | 0.90 |
| C6 | 43 | 1.00 | 1.00 | 1.00 |
| C7 | 40 | 0.93 | 0.95 | 0.95 |
| C8 | 30 | 0.90 | 0.97 | 1.00 |
| C9 | 30 | 0.77 | 0.90 | 0.97 |

## By sub-case (mean credit)

| sub | n | base | skill | skill2 |
|---|---|---|---|---|
| ambiguous-verb | 40 | 0.00 | 0.88 | 0.88 |
| clear-roles | 50 | 1.00 | 0.96 | 0.98 |
| committed-state | 30 | 0.93 | 0.87 | 0.90 |
| contradiction | 15 | 0.80 | 0.93 | 1.00 |
| distractor | 40 | 0.93 | 0.95 | 0.95 |
| handoff-ambiguous | 3 | 0.00 | 0.00 | 0.00 |
| handoff-clear | 4 | 1.00 | 1.00 | 1.00 |
| missing-quantity | 43 | 1.00 | 1.00 | 1.00 |
| only-ambiguous | 7 | 0.14 | 0.14 | 0.43 |
| only-clear | 13 | 0.69 | 0.92 | 0.92 |
| only-unambiguous | 6 | 1.00 | 0.67 | 1.00 |
| plan-clear | 40 | 1.00 | 1.00 | 0.95 |
| pronoun-ambiguous | 15 | 0.53 | 0.87 | 0.93 |
| reference-clear | 15 | 1.00 | 0.93 | 1.00 |
| same-verb-cap-first | 30 | 0.20 | 1.00 | 1.00 |
| same-verb-state-first | 30 | 0.80 | 1.00 | 1.00 |
| unreachable-goal | 15 | 1.00 | 1.00 | 1.00 |

## By language (mean credit)

| lang | n | base | skill | skill2 |
|---|---|---|---|---|
| de | 20 | 0.70 | 1.00 | 1.00 |
| en | 320 | 0.77 | 0.92 | 0.94 |
| es | 22 | 0.68 | 0.95 | 0.95 |
| fr | 32 | 0.66 | 0.97 | 0.94 |
| zh | 2 | 0.50 | 0.50 | 0.50 |

## Outcomes

| Outcome | base | skill | skill2 |
|---|---|---|---|
| asked | 34 | 106 | 100 |
| correct | 204 | 201 | 204 |
| false-impossible | 4 | 0 | 2 |
| flagged | 46 | 17 | 22 |
| missed | 3 | 1 | 0 |
| no-final-line | 3 | 0 | 1 |
| over-ask | 1 | 8 | 2 |
| silent-pick | 81 | 16 | 13 |
| stated-reading | 14 | 43 | 48 |
| wrong | 6 | 4 | 4 |
