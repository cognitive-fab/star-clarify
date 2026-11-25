# STAR-Clarify results: qwen3-30b-a3b-thinking-2507

Judge: mistral-large-latest (verdicts read from judge_cache.jsonl). Items: 90. Judge verdicts that could not be read (scored as no): 0.

## Summary

| Measure | base | control | skill | skill2 |
|---|---|---|---|---|
| STAR score (mean credit) | 0.511 | 0.567 | 0.756 | 0.800 |
| Clear items answered correctly | 100.0% (30) | 100.0% (30) | 100.0% (30) | 100.0% (30) |
| Over-asking on clear items | 0.0% (30) | 0.0% (30) | 0.0% (30) | 0.0% (30) |
| Ambiguity handled (asked or reading stated) | 33.3% (30) | 13.3% (30) | 33.3% (30) | 46.7% (30) |
| Ambiguity resolved silently | 66.7% (30) | 76.7% (30) | 16.7% (30) | 16.7% (30) |
| Missing quantity asked for | - | - | - | - |
| Missing quantity guessed silently | - | - | - | - |
| Impossible or contradictory detected | 20.0% (30) | 56.7% (30) | 93.3% (30) | 93.3% (30) |
| Mean output tokens | 4213 | 3433 | 5227 | 4747 |

## Paired comparison with base (same items)

| Condition | Better | Worse | Same | Sign test p |
|---|---|---|---|---|
| control | 16 | 11 | 63 | 0.4421 |
| skill | 26 | 4 | 60 | 0.0001 |
| skill2 | 32 | 6 | 52 | 0.0000 |

## By category (mean credit)

| category | n | base | control | skill | skill2 |
|---|---|---|---|---|---|
| P2 | 30 | 0.33 | 0.13 | 0.33 | 0.47 |
| P3 | 30 | 1.00 | 1.00 | 1.00 | 1.00 |
| P4 | 30 | 0.20 | 0.57 | 0.93 | 0.93 |

## By sub-case (mean credit)

| sub | n | base | control | skill | skill2 |
|---|---|---|---|---|---|
| plan-ambiguous-depth1 | 10 | 0.40 | 0.10 | 0.20 | 0.60 |
| plan-ambiguous-depth3 | 10 | 0.20 | 0.20 | 0.40 | 0.40 |
| plan-ambiguous-depth5 | 10 | 0.40 | 0.10 | 0.40 | 0.40 |
| plan-capacity-depth1 | 10 | 0.30 | 0.90 | 1.00 | 1.00 |
| plan-capacity-depth3 | 10 | 0.10 | 0.30 | 0.90 | 1.00 |
| plan-capacity-depth5 | 10 | 0.20 | 0.50 | 0.90 | 0.80 |
| plan-state-depth1 | 10 | 1.00 | 1.00 | 1.00 | 1.00 |
| plan-state-depth3 | 10 | 1.00 | 1.00 | 1.00 | 1.00 |
| plan-state-depth5 | 10 | 1.00 | 1.00 | 1.00 | 1.00 |

## By language (mean credit)

| lang | n | base | control | skill | skill2 |
|---|---|---|---|---|---|
| en | 90 | 0.51 | 0.57 | 0.76 | 0.80 |

## Outcomes

| Outcome | base | control | skill | skill2 |
|---|---|---|---|---|
| asked | 0 | 0 | 5 | 5 |
| correct | 36 | 47 | 58 | 58 |
| flagged | 0 | 0 | 0 | 1 |
| no-final-line | 1 | 0 | 0 | 0 |
| over-ask | 0 | 9 | 2 | 2 |
| silent-pick | 20 | 23 | 5 | 5 |
| stated-reading | 10 | 4 | 5 | 8 |
| stated-reading-assumed | 0 | 3 | 15 | 11 |
| wrong | 23 | 4 | 0 | 0 |
