---
name: "careful-reader-control"
description: "Control prompt for the STAR-Clarify ablation: general careful-reading advice plus the instruction to ask or state the reading. It has no STAR table and no list of wordings."
---

# Careful reading of a reasoning prompt

A reasoning prompt is a short text followed by a question. Most wrong answers to such prompts do not come from hard arithmetic. They come from reading too fast: a sentence is skipped, a number is copied wrongly, a condition is forgotten, or the question answered is not the question asked. This guide describes a way of working that avoids these errors.

## When to use

- Before solving a puzzle, a planning problem, a word problem, a scheduling or allocation task, or any prompt with numbers and conditions.
- Before writing or rewriting a prompt that somebody else will work from.
- When the prompt is in a language other than English, or was translated.
- Skip it for a one-line factual question.

## Procedure

### 1. Read the whole prompt before doing anything

Read the prompt from the first word to the last, once, without computing. Then read the question again on its own. Say to yourself, in one sentence, what is being asked for: a number, a yes or a no, a plan, or a judgment that something cannot be done. Do not start from the first number you see. A prompt often gives information in an order that is not the order in which it is needed.

### 2. Write down what the prompt gives you

Make a short list of the facts in the prompt, one line per sentence, in the order of the text. Copy each number with its unit. Do not round, convert or combine at this stage. If a sentence gives no information that the question needs, keep it in the list anyway and mark it as probably not needed: deciding too early that a sentence is noise is a common source of error.

Then write the question at the bottom of the list, in your own words.

### 3. Check your understanding of each line

Go through your list line by line and ask of each one: am I sure what this sentence means? Would another careful reader understand it the same way? If two careful readers could understand a line differently, and the difference would change the answer, mark that line.

### 4. Ask, or state the reading

- If the user is present and a marked line changes the answer, **ask one short question** that names the two ways of understanding it.
- If nobody can be asked, pick the most plausible way of understanding it, **state it in one line at the top** of the answer, and say what would change under the other one.
- Never resolve an ambiguity silently.

### 5. Rewrite the prompt (when the task is to write or fix a prompt)

Produce a clearer version:

- short sentences, one fact per sentence;
- every number with its unit;
- the conditions as a list;
- the question last, on its own line;
- anything you had to assume, marked as an assumption.

Keep the user's terms. Do not add conditions that the prompt does not imply.

### 6. Work step by step

- Solve the problem in small steps, and write each step on its own line.
- After each step, write what is true now. Do not keep intermediate results in your head.
- When a step uses a condition from the prompt, name the line of your list it comes from.
- If the problem asks for the smallest number of steps, do not stop at the first plan that works: check whether a shorter one exists.
- If you reach a point where no step is possible, do not force one. Go back and check whether the goal can be reached at all. Saying that something cannot be done is a valid answer when it is true.

### 7. Check the answer before giving it

- Read the question one more time and confirm that your answer is the thing asked for, in the unit asked for.
- Redo the arithmetic once, in a different order if possible.
- Confirm that every condition in your list was respected at every step, including the ones that seemed obvious.
- Confirm that you did not use a number that the prompt does not give.
- If the check fails, find the earliest step that is wrong and redo the work from there. The first mistake usually comes early and is not looked at again, so recheck the first steps first.

## Common mistakes

- Answering a question that is close to the one asked, but not the same.
- Using a number from the wrong sentence.
- Dropping a condition after the first few steps.
- Treating a sentence as unimportant because it comes late.
- Giving a long answer when a short one was asked for.

## Output format

Keep the answer short. Give, in this order:

1. the line you had to ask about, or the way you understood it, if there was one;
2. the list of facts, if it helps the reader follow;
3. the steps;
4. the answer, on its own line.

If you ask a question, ask only that question and wait for the reply: do not also give an answer under each possibility unless the user asked for it.
