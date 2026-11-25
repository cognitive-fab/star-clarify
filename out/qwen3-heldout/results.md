# STAR-Clarify results: qwen3-30b-a3b-thinking-2507

Judge: mistral. Items: 80. Judge verdicts that could not be read (scored as no): 0.

## Summary

| Measure | base | control | skill | skill2 |
|---|---|---|---|---|
| STAR score (mean credit) | 0.500 | 0.637 | 0.863 | 0.887 |
| Clear items answered correctly | 100.0% (40) | 100.0% (40) | 100.0% (40) | 100.0% (40) |
| Over-asking on clear items | 0.0% (40) | 0.0% (40) | 0.0% (40) | 0.0% (40) |
| Ambiguity handled (asked or reading stated) | 0.0% (40) | 27.5% (40) | 72.5% (40) | 77.5% (40) |
| Ambiguity resolved silently | 100.0% (40) | 72.5% (40) | 25.0% (40) | 22.5% (40) |
| Missing quantity asked for | - | - | - | - |
| Missing quantity guessed silently | - | - | - | - |
| Impossible or contradictory detected | - | - | - | - |
| Mean output tokens | 260 | 1132 | 2916 | 2419 |

## Paired comparison with base (same items)

| Condition | Better | Worse | Same | Sign test p |
|---|---|---|---|---|
| control | 11 | 0 | 69 | 0.0010 |
| skill | 29 | 0 | 51 | 0.0000 |
| skill2 | 31 | 0 | 49 | 0.0000 |

## By category (mean credit)

| category | n | base | control | skill | skill2 |
|---|---|---|---|---|---|
| H1 | 40 | 1.00 | 1.00 | 1.00 | 1.00 |
| H2 | 40 | 0.00 | 0.28 | 0.72 | 0.78 |

## By sub-case (mean credit)

| sub | n | base | control | skill | skill2 |
|---|---|---|---|---|---|
| heldout-clear-accommodates | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-admits | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-hosts | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-houses | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-keeps | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-shelters | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-stocks | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-clear-transports | 5 | 1.00 | 1.00 | 1.00 | 1.00 |
| heldout-verb-accommodates | 5 | 0.00 | 1.00 | 0.80 | 1.00 |
| heldout-verb-admits | 5 | 0.00 | 0.20 | 0.40 | 0.20 |
| heldout-verb-hosts | 5 | 0.00 | 0.00 | 0.60 | 0.60 |
| heldout-verb-houses | 5 | 0.00 | 0.00 | 0.60 | 0.80 |
| heldout-verb-keeps | 5 | 0.00 | 0.20 | 1.00 | 1.00 |
| heldout-verb-shelters | 5 | 0.00 | 0.20 | 0.80 | 0.80 |
| heldout-verb-stocks | 5 | 0.00 | 0.00 | 0.60 | 0.80 |
| heldout-verb-transports | 5 | 0.00 | 0.60 | 1.00 | 1.00 |

## By language (mean credit)

| lang | n | base | control | skill | skill2 |
|---|---|---|---|---|---|
| en | 80 | 0.50 | 0.64 | 0.86 | 0.89 |

## Outcomes

| Outcome | base | control | skill | skill2 |
|---|---|---|---|---|
| asked | 0 | 3 | 3 | 3 |
| asked-off-target | 0 | 0 | 1 | 0 |
| correct | 40 | 40 | 40 | 40 |
| silent-pick | 40 | 29 | 10 | 9 |
| stated-reading | 0 | 8 | 26 | 28 |
