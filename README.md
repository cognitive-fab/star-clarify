# STAR-Clarify

A benchmark and a skill for one question: when a prompt can be read in two ways, does a language model say so?

A reasoning prompt can state a number without stating what the number is. "The lift carries 34 people" gives a capacity or a head count. We call this the **role** of a value. STAR-Clarify measures what a model does when the role is open: ask, state the reading it takes, or pick one silently.

The paper is in `paper/star-clarify.pdf`.

## Main results

| | Claude Opus 5.5 | Qwen3-30B-A3B |
|---|---|---|
| Ambiguous prompts resolved silently, no skill | 20% | 65% |
| With the skill | 0% | 13% |
| With version 2 of the skill | 1% | 10% |
| With a control prompt (no STAR, same instruction to state the reading) | not run | 24% |

- An instruction to state the reading does most of the work.
- The STAR declaration adds the part on values whose role is open, including on verbs the skill never names.
- Asked to judge the wording, the smaller model calls 80% of the prompts it resolved silently unclear.
- Inside a planning problem, the skill removes an error on clear wording: the model alone plans with a stated capacity as an amount on 23 prompts of 30, and on none with the skill.
- Rules worded with "only" are not fixed by any version of the skill on the smaller model.

## The skill

The skill to use is `skill/star-prompt-clarifier/SKILL.md` (version 2). `skill/README.md` explains what it does, when to use it, what to expect, and what the other files are for.

In short: before answering, the model declares the Things, States, Actions and Relationships of the prompt, looks for values whose role is open, and asks or states the reading it takes.

Prompt: "The bookshelf holds 25 books. Then 10 books are removed. How many books are in the bookshelf now?"

| | Last line of the reply (Claude Opus 5.5) |
|---|---|
| Without the skill | `FINAL: 15` |
| With the skill | `FINAL: ASK: Does "the bookshelf holds 25 books" mean 25 books are on it now, or that it can fit at most 25 books?` |

Expect replies about twice as long, and 1 to 2% of needless questions on clear prompts.

## Contents

| Path | What it is |
|---|---|
| `items.jsonl` | The 396 prompts of the benchmark, with expected behavior and the answer under each reading |
| `items-heldout.jsonl` | 80 prompts with verbs that no version of the skill names |
| `items-neutral.jsonl` | 120 prompts in triples that differ only by the form of the verb |
| `items-plan.jsonl` | 90 planning prompts with a role-ambiguous value at three depths |
| `make_*.py` | The generators. Every prompt comes from a declared world, so its answers are computed |
| `skill/star-prompt-clarifier/SKILL.md` | The skill to use (version 2) |
| `skill/README.md` | What the skill does, when to use it, examples, what to expect |
| `skill/tested/` | The exact texts behind each condition: versions 1, 2 and 3, and the control prompt without STAR |
| `run.py` | Asks a model every prompt, in one or more conditions |
| `score.py` | Scores a run. Numbers and yes/no answers by code, questions and stated readings by a judge model |
| `probe.py` | Scores the recognition probe (code only) |
| `followup.py` | Answers the model's questions and checks that it then solves the prompt |
| `rewrite.py` | The rewrite-once test |
| `panel.py`, `panel.json` | Optional: several models on a sample, to check labels |
| `out/` | The replies and scores behind the paper |
| `paper/` | The paper and its LaTeX source |

## Running it

Python 3.10 or later, standard library only.

```
python make_items.py                      # regenerates items.jsonl
python run.py --dry-run                   # shows the count and one prompt
python run.py --model claude-opus-5-5 --conditions base,skill,skill2
python score.py out/<run folder>
```

An OpenAI-compatible server (llama.cpp, vLLM) works with:

```
python run.py --provider openai --base-url http://localhost:8080/v1 --key-env NONE --model <name> --conditions base,control,skill
```

Conditions: `base` (no system prompt), `skill`, `skill2`, `skill3`, `control`, `probe`. Add `-noprime` to drop the sentence that invites a question, or `-noask` to say that nobody can be asked.

Keys are read from environment variables (`ANTHROPIC_API_KEY`, and `MISTRAL_API_KEY` for the judge). Set them for the process only. Never write a key into a file.

`python score.py <folder> --judge cache` rescores from the saved judge verdicts, with no call. `python score.py <folder> --judge none` scores by code alone. It cannot see a reply that states its reading and then answers, so it undercounts handled ambiguities.

## Reply format

Every prompt ends with a request for one last line:

```
FINAL: <answer>
FINAL: ASK: <one question>
FINAL: IMPOSSIBLE: <one-line reason>
```

## Scoring

- A prompt expected to be clarified is **handled** when the reply asks about its ambiguity, or states the reading it takes and answers correctly under it.
- It is **resolved silently** when the reply follows one reading without saying so. This receives no credit, even when the number matches a reading.
- A reply that states a reading under which the answer is unknown ("20 is the capacity") and still gives an answer has added an assumption. It is counted apart (`stated-reading-assumed`) and receives no credit.
- A question on a clear prompt is counted as needless.

## Limits

- The author decided which prompts are ambiguous. No speaker judgments were collected.
- Two models were tested. The control, the added sets and the probe were run on the open-weight model only.
- The prompts are generated from a few dozen templates.
- The judge is a model. Its verdicts were not checked against a person's.

See the Limits section of the paper for the full list.

## Citation

J.-J. Dubray. STAR-Clarify: a role-ambiguity benchmark and a clarification skill for language models. 2026. https://github.com/cognitive-fab/star-clarify

## License

Code: MIT (`LICENSE`). Prompts, skill texts, results and paper: CC BY 4.0 (`LICENSE-DATA`).

## Glossary

- **STAR:** Things, States, Actions, Relationships. Four categories for declaring the world a prompt describes.
- **Thing:** an object, with properties that do not change during the problem (a jug and its capacity).
- **State:** a value that changes (the water in the jug now).
- **Role:** what a value stands for in the world of the prompt: a fixed property or a changing state.
- **Reading:** one declared world that fits the text of a prompt.
- **Ambiguous prompt:** a prompt that two declared worlds fit, with different answers to its question.
- **Declared world:** a problem written as a program, so that every answer is computed.
- **Silent resolution:** following one reading without saying so.
- **Control prompt:** a system prompt of similar length that keeps the instruction to state the reading and has no STAR content.
- **Recognition probe:** a condition in which the model judges the wording and does not solve.
