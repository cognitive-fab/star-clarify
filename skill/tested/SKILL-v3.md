---
name: "star-prompt-clarifier"
description: "Use before solving or rewriting a reasoning prompt (puzzles, plans, word problems, specs, agent instructions): fill its STAR structure (Things, States, Actions, Relationships), and ask only when a needed slot is empty or a value fits two slots."
---

# STAR prompt clarifier

A reasoning prompt describes a small world. That world has a structure: Things, States, Actions and Relationships (STAR). A prompt is clear when it fills that structure one way. It needs a question when the structure is incomplete, or when a value can go in two places.

This skill does not look for suspicious words. It fills the structure and looks at what is left open.

## When to use

- Before solving a puzzle, planning problem, word problem, scheduling or allocation task, or any prompt with quantities, limits and rules.
- Before writing or rewriting a prompt that another model or agent will reason over.
- Skip it for a one-line factual question.

## Procedure

### 1. Fill the structure

Write the structure from the prompt, in a few lines. Use only the slots the question needs.

| Element | Slots to fill | Example (a concert hall) |
|---|---|---|
| **Thing** | name; each fixed property the question needs, with its value | the hall; number of seats = 200 |
| **State** | each changing quantity, with its starting value | people seated now = 140 |
| **Action** | what is done; source; target; precondition; effect | a group enters if enough seats are free; seated people go up by the group size |
| **Relationship** | which actions or values the rule covers; what it requires of them; what holds for the ones it does not cover | people seated never exceed the number of seats |
| **Goal** | the quantity or the yes/no the question asks for | how many more people can sit down |

A fixed property (number of seats, size, price, limit) and a changing state (people seated, position, balance) are different slots, even when the prompt uses the same verb for both.

### 2. Test the structure

Go through the slots, not through the words.

1. **Empty slot.** A slot the goal needs has no value (no capacity, no starting amount, no count per box). The structure is incomplete.
2. **Value with two slots.** A number or a name can fill two different slots: "the warehouse stores 300 pallets" can be its size (Thing) or what is in it now (State); "it" can be either of two Things just named. Fill it each way.
3. **Rule with an open scope.** Write each rule in three parts: what it covers, what it requires, what holds for everything else. "Parcels may only be sent from depot 1 or depot 2 to the north hub" covers parcels sent to the north hub. It does not say whether other shipments (depot 1 to depot 2) are allowed. If the third part is not stated and the question is about a case outside what the rule covers, the scope is open. Fill it each way: everything else is forbidden, or everything else is allowed.
4. **Conflict.** Two slots cannot both be true (250 people seated in a hall with 200 seats; one quantity given two values).
5. **Unreachable goal.** The actions cannot produce the goal from the starting state (every amount the actions can produce is even, and the goal is odd).

A sentence that fills its slot one way passes the test, whatever words it uses. "The disk has a size of 500 GB" is a property. "120 GB are in use" is a state. "Only members may use the pool" covers using the pool and excludes everyone else. None of these needs a question.

Facts about Things the goal does not use are ignored. They do not open any slot.

### 3. Decide

- **Structure complete, one filling:** answer. Do not ask anything.
- **Two fillings (cases 2 and 3):** work out the answer under each. If the answers are the same, answer. If they differ, ask one short question that names the two fillings: "Is 300 pallets the size of the warehouse, or what is in it now?"
- **Empty slot (case 1):** ask for that value. Do not invent it.
- **Conflict (case 4):** name the two statements that conflict. Do not pick one.
- **Unreachable goal (case 5):** say it is impossible and give the reason.

If nobody can be asked, choose the most plausible filling, state it in one line at the top of the answer, and say what the answer would be under the other.

Never choose between two fillings without saying so.

### 4. Reason on the structure

- Write each step as an Action applied to the current State, and the State it produces.
- Something that cannot be undone (goods shipped, money spent) stays in the State from then on.
- At the end, check: no property was used as a state, every step's precondition held, no Relationship was broken, and the goal is met exactly.

### 5. Rewrite the prompt (when the task is to write or fix a prompt)

Write one sentence per filled slot: each Thing with its properties labelled ("seats: 200"), each starting State with a different verb ("140 people are seated now"), each Action with its precondition and effect, each Relationship with all three parts. Keep the user's terms. Do not add rules the prompt does not imply.

## Output format

Keep it short. For a reasoning task:
1. **Structure:** the filled slots, a few lines.
2. **Open points:** none, or the empty slot, the two fillings, or the conflict.
3. **Question or answer:** the one question, or the reasoning and the answer.

## Glossary

- **STAR:** States, Things, Actions, Relationships.
- **Thing:** an object, with properties that do not change during the problem (a hall and its number of seats).
- **State:** a quantity that changes as actions are taken (the people seated now).
- **Action:** something that can be done, with a source, a target, a precondition and an effect.
- **Relationship:** a rule that links things, states and actions, including what it leaves open.
- **Slot:** one place in the structure that a value fills (the number of seats of the hall).
- **Filling:** one way to put the prompt's values into the slots.
- **Open scope:** a rule that does not say what holds for the cases it does not cover.
