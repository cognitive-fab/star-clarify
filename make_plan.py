"""Role ambiguity inside a planning problem, at three depths, with the two fully specified versions of each prompt.

  python make_plan.py     -> items-plan.jsonl   (90 items)

World: jug A and jug B, a sink, no tap. Actions: pour jug A into jug B until A is empty or B is full; empty jug B
into the sink. Goal: exactly g litres in jug B. The number of actions needed (1, 3 or 5) is the depth.

P2  "Jug A holds a litres."                               two readings            expect: clarify
P3  "Jug A has a litres of water in it right now."        the amount is stated    expect: answer (fewest actions)
P4  "Jug A is empty and can hold at most a litres."       the capacity is stated  expect: impossible (no water, no tap)
"""
import json, random
from collections import deque
random.seed(20261126)

def fewest(a, b, g):
    start = (a, 0); seen = {start: 0}; dq = deque([start])
    while dq:
        s = dq.popleft(); d = seen[s]
        if s[1] == g: return d
        x, y = s; m = min(x, b - y)
        for t in ((x - m, y + m), (x, 0)):
            if t not in seen: seen[t] = d + 1; dq.append(t)
    return None

REST = (" Jug B is empty and can hold at most {b} litres. There is a sink and no tap. You may pour jug A into jug B until "
        "jug A is empty or jug B is full, or empty jug B into the sink. What is the smallest number of actions that leaves "
        "exactly {g} litres of water in jug B?")
ITEMS = []
def add(cat, sub, prompt, expect, gold=None, notes="", readings=None):
    n = len([i for i in ITEMS if i["category"] == cat]) + 1
    ITEMS.append(dict(id=f"{cat}-{n:03d}", category=cat, sub=sub, lang="en", prompt=prompt, expect=expect,
                      gold=None if gold is None else str(gold), readings=readings, missing=None, star="Thing", notes=notes))
seen = set()
for depth in (1, 3, 5):
    k = 0
    while k < 10:
        b = random.randint(3, 12)
        a = {1: random.randint(b, 3 * b), 3: random.randint(b + 1, 2 * b - 1), 5: random.randint(2 * b + 1, 3 * b - 1)}[depth]
        g = {1: b, 3: a - b, 5: a - 2 * b}[depth]
        if (a, b, g) in seen or fewest(a, b, g) != depth or a == b: continue
        seen.add((a, b, g)); k += 1
        rest = REST.format(b=b, g=g)
        add("P2", f"plan-ambiguous-depth{depth}", f"Jug A holds {a} litres." + rest, "clarify",
            notes=f"'holds {a} litres' can state the water in jug A now or its capacity; under the capacity reading the amount of water is not given",
            readings={"contents": depth, "capacity": None})
        add("P3", f"plan-state-depth{depth}", f"Jug A has {a} litres of water in it right now." + rest, "answer", gold=depth,
            notes="control: the amount is stated")
        add("P4", f"plan-capacity-depth{depth}", f"Jug A is empty and can hold at most {a} litres." + rest, "impossible",
            notes="control: the capacity is stated and there is no water")
with open("items-plan.jsonl", "w", encoding="utf-8") as f:
    for i in ITEMS: f.write(json.dumps(i, ensure_ascii=False) + "\n")
print(len(ITEMS), "items"); print(ITEMS[60]["prompt"], "->", ITEMS[60]["readings"])
