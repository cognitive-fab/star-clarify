# The STAR prompt clarifier

## Which file to use

Use `star-prompt-clarifier/SKILL.md`. It is version 2, the version the results support best.

| Path | What it is | Use it? |
|---|---|---|
| `star-prompt-clarifier/SKILL.md` | The skill, version 2 | Yes |
| `tested/SKILL.md` | Version 1, the first version tested | Only to reproduce the paper |
| `tested/SKILL-v2.md` | Version 2, same text as the file above | Only to reproduce the paper |
| `tested/SKILL-v3.md` | Version 3, a shorter variant. Not better than version 1 on 100 prompts | No |
| `tested/CONTROL.md` | A prompt of similar length with the instruction to state the reading and no STAR content. The comparison point of the paper | No |

The `tested` folder holds the exact texts behind each condition of `run.py`. They are kept so that every number in the paper can be reproduced.

## What it does

The skill makes the model do three things before it answers a reasoning prompt:

1. **Declare the world of the prompt** in four categories: Things (objects and their fixed properties), States (values that change), Actions (what can be done) and Relationships (rules and constraints).
2. **Look for values whose role is open.** "The tank holds 500 litres" gives a capacity or a current amount. The declaration has one slot for each, so the model has to choose, and the choice becomes visible.
3. **Ask, or state the reading it takes.** It never picks a reading silently. When the prompt cannot be satisfied, it says so.

## When to use it

- Before a model solves a word problem, a plan, a puzzle or a spec that contains quantities, limits or rules.
- Before an agent acts on an instruction written by someone else (a ticket, a task description, the output of another agent).
- When a model rewrites or improves a prompt for another model.
- When nobody can be asked (an unattended agent): the skill then states its reading in the reply, so the choice can be checked later.

It is not useful for prompts with no quantities, states or rules (a translation, a summary, casual chat). It adds length there and nothing else.

## How to use it

- **As a Claude skill:** copy the `star-prompt-clarifier` folder into your skills folder.
- **With any other model:** send the text of `SKILL.md` (below the header between the `---` lines) as the system prompt.

## Example 1: a question

Prompt:

> The bookshelf holds 25 books. Then 10 books are removed. How many books are in the bookshelf now?

Without the skill (Claude Opus 5.5):

```
The bookshelf holds 25 books, and 10 are removed:

25 − 10 = 15 books

FINAL: 15
```

With the skill (same model):

```
STAR declaration
- Thing: a bookshelf. Its capacity is unclear (see below).
- State: books on the shelf now. The starting value is unclear (see below).
- Action: remove 10 books.
- Goal: the number of books on the shelf after the removal.

Ambiguity
"Holds 25 books" can mean two different things, and they give different answers:
- Current contents: 25 books are on the shelf now, so 25 − 10 = 15 remain.
- Capacity: the shelf can fit 25 books, but we aren't told how many are on it,
  so the answer can't be worked out.

FINAL: ASK: Does "the bookshelf holds 25 books" mean 25 books are on it now,
or that it can fit at most 25 books?
```

Most readers take 25 as the number of books here. The point is not that 15 is wrong. The point is that the model chose and did not say so. In a spec ("the server handles 200 requests per second"), the same silent choice decides whether 200 is the limit or the current load.

## Example 2: an impossible plan

Prompt (shortened):

> Jug A is empty and can hold at most 24 litres. Jug B is empty and can hold at most 10 litres. There is a sink and no tap. [...] What is the smallest number of actions that leaves exactly 10 litres of water in jug B?

Without the skill (Qwen3-30B-A3B): `FINAL: 2`. The model plans with the 24 litres as if they were water.

With the skill: `FINAL: IMPOSSIBLE: No source of water to fill the jugs (no tap and no other source provided).`

## What to expect

Measured on the benchmark of this repository (see the paper for the tables).

| | Claude Opus 5.5 | Qwen3-30B-A3B |
|---|---|---|
| Ambiguous prompts resolved silently, no skill | 20% | 65% |
| With the skill (version 2) | 1% | 10% |
| Clear prompts answered correctly, no skill / with the skill | 97% / 98% | 95% / 95% |
| Needless questions on clear prompts, no skill / with the skill | 2% / 2% | 0.5% / 1% |

Other results on the smaller model:

- **Verbs the skill never names** (stocks, houses, shelters): 31 of 40 ambiguities handled, against 0 without the skill.
- **Nobody to ask:** 62% handled against 28% (version 1).
- **Planning:** on clear wording, the model alone plans with a stated capacity as an amount on 23 prompts of 30. With the skill: 0.

Costs and limits:

- **Replies are about twice as long** (the declaration comes first).
- **A plain instruction does part of the work.** The control prompt alone brings silent resolution from 65% to 24%. The STAR declaration adds the cases where the role of a value is open.
- **The model can still fill a gap with an assumption.** In planning prompts it often writes "20 is a capacity" and then assumes the jug starts full. The choice is visible, but nobody was asked.
- **Rules worded with "only"** are not fixed on the smaller model.
- **Two models were tested.** Results on other models are not known.

## Glossary

- **STAR:** Things, States, Actions, Relationships.
- **Role:** what a value stands for: a fixed property (a capacity) or a changing state (a current amount).
- **Reading:** one way to understand a prompt that fits its text.
- **Silent resolution:** following one reading without saying so.
- **Control prompt:** a prompt with the same instruction and no STAR content, used for comparison.
