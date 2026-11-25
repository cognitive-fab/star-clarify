---
name: "star-prompt-clarifier"
description: "Use before solving or rewriting a reasoning prompt (puzzles, plans, word problems, specs, agent instructions): declare its Things, States, Actions and Relationships, find ambiguous wording, and ask or restate."
---

# STAR prompt clarifier

A reasoning prompt describes a small world. Language models reason about it with the categories of human language: Things, States, Actions and Relationships (STAR). Our studies of how frontier and open models reason found three facts this skill is built on:

1. **Errors live in one category.** Nearly every wrong answer starts in a single category: a Thing misread, a State that leaves something out, an Action whose rule is misapplied, or a Relationship read too narrowly.
2. **A role is carried by the words around a value, not by the value.** Inside the model, "7" holds the value; "litres of water in jug A" or "-litre jug" holds its role (capacity or contents). One ambiguous word next to a value can move it to the wrong role, and what was read earlier decides which way it falls (French "contient" read a capacity as contents after a sentence about contents).
3. **Models never ask.** Given an ambiguous rule, no model asked what it meant; each silently picked one reading.

So: declare the world before reasoning, make every value's role explicit in the words next to it, and ask (or state the reading chosen) when a word can carry two roles.

## When to use

- Before solving a puzzle, planning problem, word problem, scheduling or allocation task, or any prompt with quantities, limits and rules.
- Before writing or rewriting a prompt that another model or agent will reason over.
- When a translated prompt, or a prompt in a second language, is involved.
- Skip it for a one-line factual question.

## Procedure

### 1. Declare the world as STAR

Write a short table from the prompt, before any reasoning:

| Category | What to list | Example (water jugs) |
|---|---|---|
| **Things** | each object, with its fixed properties | jug A, capacity 5 L; jug B, capacity 3 L; tap; sink |
| **States** | what changes, with the starting value of each | contents of A = 0 L; contents of B = 0 L |
| **Actions** | what can be done, with each one's precondition and effect | fill X from the tap; empty X into the sink; pour X into Y until X is empty or Y is full |
| **Relationships** | rules and constraints linking them, and the goal | contents never exceed capacity; goal: exactly 4 L in A |

Rules for the table:
- Keep **fixed properties** (capacity, size, price, deadline) apart from **changing states** (contents, position, balance, status). This is the confusion that one word can trigger.
- Give every value its role in the words right next to it: "capacity: 5 L", "currently contains: 0 L". Never leave a bare number whose role depends on a verb elsewhere.
- List what the prompt forbids as well as what it allows. If it says "only X", write out what is excluded.
- If an action, thing or rule needed to solve the problem is not stated, list it as an **assumption**, marked as such.

### 2. Check each value and rule for a second reading

Go through the prompt line by line and flag:

- **Role-ambiguous verbs next to a value:** holds, contains, has, takes, carries, "contient", "tient". Each can state a capacity or a current amount. Check which one the sentence means, and whether an earlier sentence used the same verb for the other role.
- **The same word used for two roles** in one prompt ("contains 3 L" for contents, then "contains exactly 5 L" for capacity). Reword one of them.
- **Rules with "only", "can", "must", "from ... to"**: write both the narrow and the broad reading. If they lead to different allowed actions, it is ambiguous.
- **Translated wording:** back-translate the rule, then ask the narrow-versus-broad question in the target language too. Back-translation alone did not reveal a narrowed rule in our studies.
- **Hidden state:** anything that, once done, cannot be undone (water handed off, money spent, a message sent) must be part of the state from then on.
- **Missing values:** a quantity the answer needs is not given (a capacity, a count per box, a starting amount). Ask for it. Never invent it; if you must go on, state the value you assume.
- **Contradictions:** a stated state breaks a stated property (12 L in a 5 L jug), or two sentences give one value two different numbers. Name the conflict instead of choosing one silently.
- **Unclear references:** "it", "the jug", "that one" when two Things fit. Ask which one, or name the one you chose.
- **Irrelevant facts:** list them as Things not used. A role-ambiguous verb in an irrelevant sentence must not change the role of a value that matters.

### 3. Ask, or state the reading

- **Ask only when the readings lead to different answers.** If every reading gives the same answer, or the prompt is clear, answer without a question: needless questions are errors too.
- If the user is present and a flagged ambiguity changes the answer, **ask one short question** naming the two readings. Example: "'Jug A contains 5 L': is 5 L its capacity or the water in it now?"
- If nobody can be asked, pick the most plausible reading, **state it in one line at the top** of the answer, and say what would change under the other reading.
- Never resolve an ambiguity silently.
- If the goal cannot be reached under the declared rules, say so and give the reason (for example, every reachable amount is a multiple of 2).

### 4. Rewrite the prompt (when the task is to write or fix a prompt)

Produce a clarified version:
- one sentence per Thing, with its fixed properties labelled by role;
- one sentence per starting State, with a different verb from the property sentences;
- the allowed Actions as a list, each with its precondition and effect;
- the Relationships and the goal, with every "only" spelled out;
- the assumptions, marked.

Keep the user's terms. Do not add rules the prompt does not imply.

### 5. Reason against the declaration, then check by category

- Write each step as an Action applied to the current State, and the State it produces.
- At the end, check the answer category by category:
  - **Things:** no property was read as a state, or the reverse;
  - **States:** everything committed or irreversible is still in the state;
  - **Actions:** every step's precondition held;
  - **Relationships:** no constraint was broken, and the goal is met exactly.
- If a check fails, name the category and the step where the error started. The first wrong reading usually comes early and is not revisited, so recheck the first steps first.

## Output format

For a reasoning task:
1. **STAR declaration** (the table).
2. **Ambiguities**: each one, its two readings, and the question asked or the reading chosen.
3. **Reasoning**: Action and resulting State, step by step.
4. **Answer**, then the **category check**.

For a short problem, keep the declaration to a few lines; the table is a tool, not a deliverable.

For a prompt-writing task: the STAR declaration, the ambiguities found, and the clarified prompt.

## Glossary

- **STAR:** States, Things, Actions, Relationships, the four categories human languages share for describing a world.
- **Thing:** an object, with properties that do not change during the problem (a jug and its capacity).
- **State:** a value that changes as actions are taken (the water in the jug now).
- **Action:** something that can be done, with a precondition and an effect.
- **Relationship:** a rule or constraint that links things and states, including the goal.
- **Role:** what a value means in the world (capacity or contents), carried by the words around it.
- **Declared world:** a problem stated so that every thing, state, action and rule is explicit, so the answer can be checked exactly.