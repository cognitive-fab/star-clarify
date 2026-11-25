# STAR-Clarify results: qwen3-30b-a3b-thinking-2507

Judge: mistral. Items: 100. Judge verdicts that could not be read (scored as no): 0.

## Summary

| Measure | base | skill | skill3 |
|---|---|---|---|
| STAR score (mean credit) | 0.760 | 0.950 | 0.880 |
| Clear items answered correctly | 95.8% (48) | 97.9% (48) | 93.8% (48) |
| Over-asking on clear items | 2.1% (48) | 0.0% (48) | 6.2% (48) |
| Ambiguity handled (asked or reading stated) | 32.3% (31) | 87.1% (31) | 74.2% (31) |
| Ambiguity resolved silently | 64.5% (31) | 12.9% (31) | 22.6% (31) |
| Missing quantity asked for | 100.0% (10) | 100.0% (10) | 100.0% (10) |
| Missing quantity guessed silently | 0.0% (10) | 0.0% (10) | 0.0% (10) |
| Impossible or contradictory detected | 90.9% (11) | 100.0% (11) | 90.9% (11) |
| Mean output tokens | 1876 | 3975 | 2641 |

## Paired comparison with base (same items)

| Condition | Better | Worse | Same | Sign test p |
|---|---|---|---|---|
| skill | 20 | 1 | 79 | 0.0000 |
| skill3 | 17 | 5 | 78 | 0.0169 |

## By category (mean credit)

| category | n | base | skill | skill3 |
|---|---|---|---|---|
| C1 | 10 | 1.00 | 1.00 | 1.00 |
| C10 | 10 | 1.00 | 1.00 | 1.00 |
| C2 | 10 | 0.00 | 0.90 | 0.90 |
| C3 | 10 | 0.60 | 1.00 | 0.90 |
| C4 | 10 | 0.50 | 0.70 | 0.50 |
| C5 | 10 | 1.00 | 0.90 | 1.00 |
| C6 | 10 | 1.00 | 1.00 | 1.00 |
| C7 | 10 | 1.00 | 1.00 | 1.00 |
| C8 | 10 | 0.90 | 1.00 | 0.90 |
| C9 | 10 | 0.60 | 1.00 | 0.60 |

## By sub-case (mean credit)

| sub | n | base | skill | skill3 |
|---|---|---|---|---|
| ambiguous-verb | 10 | 0.00 | 0.90 | 0.90 |
| clear-roles | 10 | 1.00 | 1.00 | 1.00 |
| committed-state | 10 | 1.00 | 0.90 | 1.00 |
| contradiction | 6 | 0.83 | 1.00 | 0.83 |
| distractor | 10 | 1.00 | 1.00 | 1.00 |
| handoff-ambiguous | 1 | 0.00 | 0.00 | 0.00 |
| handoff-clear | 2 | 1.00 | 1.00 | 0.00 |
| missing-quantity | 10 | 1.00 | 1.00 | 1.00 |
| only-ambiguous | 2 | 0.00 | 0.00 | 0.50 |
| only-clear | 4 | 0.50 | 1.00 | 1.00 |
| only-unambiguous | 1 | 1.00 | 1.00 | 0.00 |
| plan-clear | 10 | 1.00 | 1.00 | 1.00 |
| pronoun-ambiguous | 8 | 0.50 | 1.00 | 0.50 |
| reference-clear | 2 | 1.00 | 1.00 | 1.00 |
| same-verb-cap-first | 5 | 0.20 | 1.00 | 0.80 |
| same-verb-state-first | 5 | 1.00 | 1.00 | 1.00 |
| unreachable-goal | 4 | 1.00 | 1.00 | 1.00 |

## By language (mean credit)

| lang | n | base | skill | skill3 |
|---|---|---|---|---|
| de | 3 | 1.00 | 1.00 | 1.00 |
| en | 84 | 0.76 | 0.95 | 0.89 |
| es | 5 | 0.80 | 1.00 | 0.80 |
| fr | 8 | 0.62 | 0.88 | 0.75 |

## Outcomes

| Outcome | base | skill | skill3 |
|---|---|---|---|
| asked | 9 | 25 | 21 |
| asked-off-target | 0 | 0 | 1 |
| correct | 51 | 52 | 50 |
| false-impossible | 1 | 0 | 0 |
| flagged | 12 | 7 | 8 |
| missed | 1 | 0 | 1 |
| over-ask | 1 | 0 | 3 |
| silent-pick | 20 | 4 | 7 |
| stated-reading | 4 | 11 | 9 |
| wrong | 1 | 1 | 0 |
