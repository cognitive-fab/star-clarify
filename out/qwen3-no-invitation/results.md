# STAR-Clarify results: qwen3-30b-a3b-thinking-2507

Judge: mistral-large-latest (verdicts read from judge_cache.jsonl). Items: 206. Judge verdicts that could not be read (scored as no): 0.

## Summary

| Measure | base | base-noprime | skill | skill-noprime |
|---|---|---|---|---|
| STAR score (mean credit) | 0.558 | 0.478 | 0.913 | 0.813 |
| Clear items answered correctly | 89.5% (38) | 94.7% (38) | 89.5% (38) | 94.7% (38) |
| Over-asking on clear items | 2.6% (38) | 0.0% (38) | 10.5% (38) | 5.3% (38) |
| Ambiguity handled (asked or reading stated) | 30.4% (125) | 31.2% (125) | 88.8% (125) | 80.8% (125) |
| Ambiguity resolved silently | 65.6% (125) | 68.8% (125) | 10.4% (125) | 13.6% (125) |
| Missing quantity asked for | 100.0% (43) | 25.6% (43) | 100.0% (43) | 41.9% (43) |
| Missing quantity guessed silently | 0.0% (43) | 16.3% (43) | 0.0% (43) | 0.0% (43) |
| Impossible or contradictory detected | - | - | - | - |
| Mean output tokens | 816 | 730 | 3109 | 3192 |

## Paired comparison with base (same items)

| Condition | Better | Worse | Same | Sign test p |
|---|---|---|---|---|
| base-noprime | 26 | 55 | 125 | 0.0017 |
| skill | 79 | 6 | 121 | 0.0000 |
| skill-noprime | 71 | 31 | 104 | 0.0001 |

## By category (mean credit)

| category | n | base | base-noprime | skill | skill-noprime |
|---|---|---|---|---|---|
| C2 | 40 | 0.00 | 0.03 | 0.95 | 0.75 |
| C3 | 60 | 0.48 | 0.50 | 1.00 | 1.00 |
| C4 | 33 | 0.64 | 0.64 | 0.61 | 0.67 |
| C6 | 43 | 1.00 | 0.55 | 1.00 | 0.71 |
| C9 | 30 | 0.73 | 0.77 | 0.90 | 0.83 |

## By sub-case (mean credit)

| sub | n | base | base-noprime | skill | skill-noprime |
|---|---|---|---|---|---|
| ambiguous-verb | 40 | 0.00 | 0.03 | 0.95 | 0.75 |
| handoff-ambiguous | 3 | 0.33 | 0.00 | 0.00 | 0.33 |
| handoff-clear | 4 | 1.00 | 1.00 | 1.00 | 1.00 |
| missing-quantity | 43 | 1.00 | 0.55 | 1.00 | 0.71 |
| only-ambiguous | 7 | 0.14 | 0.00 | 0.00 | 0.00 |
| only-clear | 13 | 0.69 | 0.92 | 0.92 | 1.00 |
| only-unambiguous | 6 | 1.00 | 0.83 | 0.67 | 0.67 |
| pronoun-ambiguous | 15 | 0.47 | 0.53 | 0.87 | 0.67 |
| reference-clear | 15 | 1.00 | 1.00 | 0.93 | 1.00 |
| same-verb-cap-first | 30 | 0.20 | 0.63 | 1.00 | 1.00 |
| same-verb-state-first | 30 | 0.77 | 0.37 | 1.00 | 1.00 |

## By language (mean credit)

| lang | n | base | base-noprime | skill | skill-noprime |
|---|---|---|---|---|---|
| de | 10 | 0.40 | 0.20 | 1.00 | 1.00 |
| en | 160 | 0.59 | 0.45 | 0.91 | 0.77 |
| es | 12 | 0.50 | 0.58 | 0.92 | 1.00 |
| fr | 22 | 0.45 | 0.77 | 0.95 | 0.95 |
| zh | 2 | 0.50 | 0.50 | 0.50 | 0.50 |

## Outcomes

| Outcome | base | base-noprime | skill | skill-noprime |
|---|---|---|---|---|
| asked | 34 | 0 | 105 | 2 |
| asked-off-target | 0 | 0 | 1 | 1 |
| assumed | 0 | 25 | 0 | 25 |
| correct | 34 | 36 | 34 | 36 |
| false-impossible | 1 | 0 | 0 | 0 |
| flagged | 34 | 11 | 3 | 16 |
| no-final-line | 3 | 0 | 0 | 0 |
| over-ask | 1 | 0 | 4 | 2 |
| silent-guess | 0 | 7 | 0 | 0 |
| silent-pick | 82 | 86 | 13 | 17 |
| stated-reading | 13 | 39 | 46 | 101 |
| stated-reading-assumed | 0 | 0 | 0 | 6 |
| wrong | 4 | 2 | 0 | 0 |
