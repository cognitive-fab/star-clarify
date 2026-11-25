# STAR-Clarify results: claude-opus-5-5

Judge: mistral. Items: 396. Judge verdicts that could not be read (scored as no): 0.

## Summary

| Measure | base | skill | skill2 |
|---|---|---|---|
| STAR score (mean credit) | 0.924 | 0.980 | 0.987 |
| Clear items answered correctly | 97.4% (191) | 96.3% (191) | 97.9% (191) |
| Over-asking on clear items | 1.6% (191) | 3.1% (191) | 1.6% (191) |
| Ambiguity handled (asked or reading stated) | 80.0% (125) | 99.2% (125) | 99.2% (125) |
| Ambiguity resolved silently | 20.0% (125) | 0.0% (125) | 0.8% (125) |
| Missing quantity asked for | 100.0% (43) | 100.0% (43) | 100.0% (43) |
| Missing quantity guessed silently | 0.0% (43) | 0.0% (43) | 0.0% (43) |
| Impossible or contradictory detected | 100.0% (37) | 100.0% (37) | 100.0% (37) |
| Mean output tokens | 380 | 915 | 783 |

## Paired comparison with base (same items)

| Condition | Better | Worse | Same | Sign test p |
|---|---|---|---|---|
| skill | 25 | 3 | 368 | 0.0000 |
| skill2 | 27 | 2 | 367 | 0.0000 |

## By category (mean credit)

| category | n | base | skill | skill2 |
|---|---|---|---|---|
| C1 | 50 | 1.00 | 1.00 | 1.00 |
| C10 | 40 | 1.00 | 1.00 | 0.97 |
| C2 | 40 | 0.57 | 1.00 | 1.00 |
| C3 | 60 | 1.00 | 1.00 | 1.00 |
| C4 | 33 | 0.64 | 0.79 | 0.88 |
| C5 | 30 | 1.00 | 0.97 | 1.00 |
| C6 | 43 | 1.00 | 1.00 | 1.00 |
| C7 | 40 | 0.97 | 1.00 | 1.00 |
| C8 | 30 | 1.00 | 1.00 | 1.00 |
| C9 | 30 | 1.00 | 1.00 | 1.00 |

## By sub-case (mean credit)

| sub | n | base | skill | skill2 |
|---|---|---|---|---|
| ambiguous-verb | 40 | 0.57 | 1.00 | 1.00 |
| clear-roles | 50 | 1.00 | 1.00 | 1.00 |
| committed-state | 30 | 1.00 | 0.97 | 1.00 |
| contradiction | 15 | 1.00 | 1.00 | 1.00 |
| distractor | 40 | 0.97 | 1.00 | 1.00 |
| handoff-ambiguous | 3 | 0.00 | 0.67 | 1.00 |
| handoff-clear | 4 | 0.50 | 0.00 | 0.75 |
| missing-quantity | 43 | 1.00 | 1.00 | 1.00 |
| only-ambiguous | 7 | 0.29 | 1.00 | 0.86 |
| only-clear | 13 | 1.00 | 1.00 | 1.00 |
| only-unambiguous | 6 | 0.67 | 0.67 | 0.67 |
| plan-clear | 40 | 1.00 | 1.00 | 0.97 |
| pronoun-ambiguous | 15 | 1.00 | 1.00 | 1.00 |
| reference-clear | 15 | 1.00 | 1.00 | 1.00 |
| same-verb-cap-first | 30 | 1.00 | 1.00 | 1.00 |
| same-verb-state-first | 30 | 1.00 | 1.00 | 1.00 |
| unreachable-goal | 15 | 1.00 | 1.00 | 1.00 |

## By language (mean credit)

| lang | n | base | skill | skill2 |
|---|---|---|---|---|
| de | 20 | 1.00 | 1.00 | 0.95 |
| en | 320 | 0.92 | 0.99 | 0.99 |
| es | 22 | 0.95 | 0.91 | 1.00 |
| fr | 32 | 0.94 | 0.97 | 1.00 |
| zh | 2 | 0.00 | 0.50 | 0.50 |

## Outcomes

| Outcome | base | skill | skill2 |
|---|---|---|---|
| asked | 59 | 136 | 115 |
| correct | 208 | 206 | 209 |
| false-impossible | 1 | 0 | 0 |
| flagged | 15 | 15 | 15 |
| no-final-line | 0 | 1 | 0 |
| over-ask | 3 | 6 | 3 |
| silent-pick | 25 | 0 | 1 |
| stated-reading | 84 | 31 | 52 |
| stated-reading-wrong | 0 | 1 | 0 |
| wrong | 1 | 0 | 1 |
