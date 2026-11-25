"""STAR-Clarify item generator.

Writes items.jsonl: reasoning prompts that probe the edge cases the STAR prompt
clarifier is meant to handle. Every item is generated from a declared world, so
its expected behaviour and its answer under each reading are exact.

  python make_items.py            -> items.jsonl and summary
"""
import json, random, itertools
from collections import deque, Counter

random.seed(20261121)
ITEMS = []


def add(cat, sub, lang, prompt, expect, gold, star, notes="", readings=None, missing=None):
    """expect: answer | clarify | impossible | missing
    gold: the exact answer for 'answer' and 'impossible' items (string)
    readings: for 'clarify' items, {reading_name: answer or None}
    missing: for 'missing' items, the name of the quantity that must be asked for
    star: the STAR category where a wrong reading would sit"""
    ITEMS.append(dict(id=f"{cat}-{len([i for i in ITEMS if i['category'] == cat]) + 1:03d}",
                      category=cat, sub=sub, lang=lang, prompt=prompt.strip(), expect=expect,
                      gold=None if gold is None else str(gold), readings=readings, missing=missing,
                      star=star, notes=notes))


# --------------------------------------------------------------------------- domains
# (thing, unit, property noun, state noun, clear-property verb phrase, clear-state verb phrase,
#  role-ambiguous verb, space question)
DOM = [
    ("jug A", "litres", "capacity", "water", "can hold at most {c} litres", "has {w} litres of water in it right now",
     "holds {x} litres", "How many more litres of water can be poured into jug A?"),
    ("the bus", "passengers", "seats", "passengers", "has {c} seats", "is carrying {w} passengers right now",
     "takes {x} passengers", "How many more passengers can board the bus?"),
    ("the car park", "cars", "spaces", "cars", "has {c} parking spaces", "has {w} cars parked in it right now",
     "holds {x} cars", "How many more cars can park?"),
    ("the bookshelf", "books", "capacity", "books", "has room for {c} books in total", "has {w} books on it right now",
     "holds {x} books", "How many more books can be put on the bookshelf?"),
    ("the tank", "litres", "capacity", "fuel", "can take at most {c} litres", "has {w} litres of fuel in it right now",
     "holds {x} litres", "How many more litres of fuel can be added to the tank?"),
    ("the lift", "people", "capacity", "people", "is rated for at most {c} people", "has {w} people inside right now",
     "carries {x} people", "How many more people can get into the lift?"),
    ("the classroom", "students", "seats", "students", "has {c} seats", "has {w} students seated in it right now",
     "holds {x} students", "How many more students can sit down in the classroom?"),
    ("the freezer", "kilograms", "capacity", "food", "can store at most {c} kilograms", "has {w} kilograms of food in it right now",
     "holds {x} kilograms", "How many more kilograms of food can go into the freezer?"),
    ("the battery", "kilowatt-hours", "capacity", "charge", "can store at most {c} kilowatt-hours",
     "has {w} kilowatt-hours of charge right now", "holds {x} kilowatt-hours",
     "How many more kilowatt-hours can be charged into the battery?"),
    ("the hotel", "rooms", "rooms", "occupied rooms", "has {c} rooms", "has {w} rooms occupied tonight",
     "has {x} rooms", "How many more rooms can be booked tonight?"),
]


def cap1(t):
    return t[0].upper() + t[1:]


def pairs(n, lo=3, hi=60):
    out = set()
    while len(out) < n:
        c = random.randint(lo, hi); w = random.randint(0, c - 1)
        out.add((c, w))
    return sorted(out)


# --------------------------------------------------------------------------- C1 clear roles (controls)
for d in DOM:
    thing, unit, *_ , vp, vs, va, q = d
    for c, w in pairs(5):
        cap = f"{cap1(thing)} {vp.format(c=c)}."
        cur = f"{cap1(thing)} {vs.format(w=w)}."
        order = random.choice([0, 1])
        s = f"{cap} {cur}" if order == 0 else f"{cur} {cap}"
        add("C1", "clear-roles", "en", f"{s} {q}", "answer", c - w, "Thing/State",
            notes=f"control, order={'cap-first' if order == 0 else 'state-first'}")

# --------------------------------------------------------------------------- C2 one role-ambiguous statement
# The only number about the thing uses an ambiguous verb; a change follows. Contents reading gives an
# answer; capacity reading leaves the contents unknown.
for d in DOM[:8]:
    thing, unit, prop, statenoun, vp, vs, va, q = d
    for _ in range(5):
        x = random.randint(10, 60); r = random.randint(1, x - 1)
        s = f"{cap1(thing)} {va.format(x=x)}. Then {r} {unit} are removed. How many {unit} are in {thing} now?"
        add("C2", "ambiguous-verb", "en", s, "clarify", None, "Thing",
            readings={"contents": x - r, "capacity": None},
            notes=f"'{va.split()[0]}' can state the {prop} or the current amount; under the capacity reading the amount is unknown")

# --------------------------------------------------------------------------- C3 same verb for two roles, with order (the 'contient' case)
LANG3 = {
    "en": dict(cap="Jug A contains exactly {c} litres.", cur="Right now, jug A contains {w} litres of water.",
               q="How many more litres of water can be poured into jug A?"),
    "fr": dict(cap="La cruche A contient exactement {c} litres.", cur="En ce moment, la cruche A contient {w} litres d'eau.",
               q="Combien de litres d'eau peut-on encore verser dans la cruche A ?"),
    "es": dict(cap="La jarra A contiene exactamente {c} litros.", cur="En este momento, la jarra A contiene {w} litros de agua.",
               q="¿Cuántos litros de agua más se pueden echar en la jarra A?"),
    "de": dict(cap="Krug A enthält genau {c} Liter.", cur="Im Moment enthält Krug A {w} Liter Wasser.",
               q="Wie viele Liter Wasser kann man noch in Krug A gießen?"),
}
for lang, n in [("en", 20), ("fr", 20), ("es", 10), ("de", 10)]:
    t = LANG3[lang]
    for i, (c, w) in enumerate(pairs(n, 3, 9)):
        order = "state-first" if i % 2 == 0 else "cap-first"
        a, b = t["cap"].format(c=c), t["cur"].format(w=w)
        s = f"{b} {a} {t['q']}" if order == "state-first" else f"{a} {b} {t['q']}"
        # Reading 1: 'exactly' sentence = capacity -> c - w. Reading 2: both sentences state contents (contradiction or update).
        add("C3", f"same-verb-{order}", lang, s, "clarify", None, "Thing",
            readings={"exactly-is-capacity": c - w, "both-are-contents": None},
            notes="the same verb states the capacity and the contents; the paper's 30B model read the capacity as contents after a contents sentence")

# --------------------------------------------------------------------------- C4 'only' rules: narrow vs broad
ONLY = [
    ("Water can only be poured from jug X or jug Y into jug Z or jug T.",
     "Pours into jug Z or jug T may only come from jug X or jug Y; any other pour is allowed.",
     "Is it allowed to pour water from jug X into jug Y?", "no", "yes"),
    ("Only managers can approve refunds above 100 dollars.",
     "Refunds above 100 dollars need a manager's approval; any refund of 100 dollars or less can be approved by any employee or by a manager.",
     "Can a manager approve a refund of 50 dollars?", None, "yes"),
    ("Trucks may only use the left lane to overtake.",
     "When a truck overtakes, it must use the left lane; trucks may also use the left lane for other reasons.",
     "May a truck drive in the left lane when it is not overtaking?", "no", "yes"),
    ("Visitors can only enter the lab with a badge.",
     "A visitor without a badge may not enter the lab. A visitor with a badge may enter the lab.",
     "Can a visitor with a badge but no escort enter the lab?", "yes", "yes"),
    ("Robots may only carry boxes from shelf 1 to the dock.",
     "When a robot carries a box to the dock, the box must come from shelf 1; robots may carry boxes between other places too.",
     "May a robot carry a box from shelf 2 to shelf 3?", "no", "yes"),
    ("Interns can only push code to the test branch.",
     "Code pushed by interns must go to the test branch; other people may push to the test branch too.",
     "Can a senior engineer push code to the test branch?", "yes", "yes"),
    ("The crane can only lift blocks from the barge onto the ramp.",
     "Blocks put on the ramp by the crane must come from the barge; the crane may also lift blocks elsewhere.",
     "May the crane lift a block from the ramp back onto the barge?", "no", "yes"),
    ("Members can only borrow three books at a time.",
     "A member may have at most three borrowed books at any time.",
     "A member has two borrowed books. May she borrow one more?", "yes", "yes"),
    ("Payments can only be sent from the main account to suppliers.",
     "Payments to suppliers must be sent from the main account; the main account may also pay others.",
     "May the main account pay an employee's expense claim?", "no", "yes"),
    ("Only the night shift may restock the freezer.",
     "Restocking the freezer is done by the night shift and by no one else.",
     "May the day shift restock the freezer?", "no", "no"),
    ("Water can only flow from tank 1 to tank 2 through the valve.",
     "Any water going from tank 1 to tank 2 must pass through the valve; water may flow elsewhere without it.",
     "May water flow from tank 2 to tank 3 without passing through the valve?", "no", "yes"),
    ("Drones can only land on the roof pad at night.",
     "At night, drones must land on the roof pad; in the day they may land anywhere allowed.",
     "May a drone land on the roof pad at noon?", "no", "yes"),
    ("You can only park here on weekdays between 9 and 5.",
     "Parking here is allowed on weekdays between 9 and 5, and not at any other time.",
     "Can you park here on Saturday at 10?", "no", "no"),
]
for amb, clear, q, narrow, broad in ONLY:
    if narrow is not None and narrow != broad:
        add("C4", "only-ambiguous", "en", f"{amb} {q}", "clarify", None, "Relationship",
            readings={"narrow": narrow, "broad": broad}, notes="'only' can restrict the actor, the action or the target")
    else:
        add("C4", "only-unambiguous", "en", f"{amb} {q}", "answer", broad, "Relationship",
            notes="both readings give the same answer, so no question is needed")
    add("C4", "only-clear", "en", f"{clear} {q}", "answer", broad, "Relationship", notes="control")
# the hand-off rule in four languages (the paper's Chinese narrowing)
HAND = {
    "en": ("Water can only be poured from jug X or jug Y into jug Z or jug T. Is it allowed to pour water from jug X into jug Y?",
           "The water in jugs Z and T can only be poured in from jug X or jug Y. Is it allowed to pour water from jug X into jug Y?"),
    "fr": ("On ne peut verser de l'eau que de la cruche X ou de la cruche Y dans la cruche Z ou la cruche T. Peut-on verser de l'eau de la cruche X dans la cruche Y ?",
           "L'eau des cruches Z et T ne peut y être versée que depuis la cruche X ou la cruche Y. Peut-on verser de l'eau de la cruche X dans la cruche Y ?"),
    "es": ("Solo se puede echar agua de la jarra X o de la jarra Y en la jarra Z o en la jarra T. ¿Se puede echar agua de la jarra X en la jarra Y?",
           "El agua de las jarras Z y T solo puede venir de la jarra X o de la jarra Y. ¿Se puede echar agua de la jarra X en la jarra Y?"),
    "zh": ("只能从X或Y往Z或T里倒水。可以从X往Y里倒水吗？",
           "Z和T里的水只能从X或Y倒进去。可以从X往Y里倒水吗？"),
}
for lang, (amb, clear) in HAND.items():
    add("C4", "handoff-ambiguous", lang, amb, "clarify", None, "Relationship",
        readings={"narrow": "no", "broad": "yes"}, notes="the narrowed hand-off rule of the grammar paper")
    add("C4", "handoff-clear", lang, clear, "answer", "yes", "Relationship", notes="the final wording of the grammar paper")

# --------------------------------------------------------------------------- jug solver
def bfs(caps, goal, store=False):
    """Fewest actions to get exactly `goal` litres in any jug (store=False), or into the store (store=True,
    a container that receives pours from the jugs and can never be emptied). Actions: fill a jug from the
    tap, empty a jug into the sink, pour one container into another until the source is empty or the
    target is full. Returns None if unreachable."""
    n = len(caps)
    start = tuple([0] * n + ([0] if store else []))
    seen = {start: 0}; dq = deque([start])
    while dq:
        s = dq.popleft(); d = seen[s]
        if (not store and goal in s[:n]) or (store and s[n] == goal):
            return d
        nxt = []
        for i in range(n):
            t = list(s); t[i] = caps[i]; nxt.append(tuple(t))
            t = list(s); t[i] = 0; nxt.append(tuple(t))
            for j in range(n):
                if i != j:
                    t = list(s); m = min(t[i], caps[j] - t[j]); t[i] -= m; t[j] += m; nxt.append(tuple(t))
            if store:
                t = list(s); t[n] += t[i]; t[i] = 0
                if t[n] <= goal: nxt.append(tuple(t))
        for t in nxt:
            if t not in seen:
                seen[t] = d + 1; dq.append(t)
    return None

# --------------------------------------------------------------------------- C5 committed (irreversible) state
for _ in range(30):
    a, b = random.sample(range(3, 10), 2)
    g = random.randint(1, a + b + 4)
    steps = bfs((a, b), g, store=True)
    s = (f"Jug A can hold exactly {a} litres and jug B exactly {b} litres; both start empty. There is a tap and a sink. "
         f"You may fill a jug from the tap, empty a jug into the sink, pour one jug into the other until the first is empty "
         f"or the second is full, or pour a jug completely into a store. Water poured into the store can never be taken back. "
         f"What is the smallest number of actions that leaves exactly {g} litres in the store? "
         f"If it cannot be done, say that it is impossible.")
    add("C5", "committed-state", "en", s, "answer" if steps is not None else "impossible",
        steps if steps is not None else "impossible", "State",
        notes="the store's content is part of every later state; it cannot be reduced")

# --------------------------------------------------------------------------- C6 missing information (ask for it)
MISS = [
    ("Jug A has {w} litres of water in it. How many more litres can be poured into jug A?", "the capacity of jug A", "{w}"),
    ("A shop sells pens in boxes. Maria buys {x} boxes. How many pens does she have?", "the number of pens per box", "{x}"),
    ("The bus is carrying {w} passengers. At the next stop {r} get off and some get on. How many passengers are on the bus now?",
     "how many passengers get on", "{w} {r}"),
    ("A recipe needs {x} grams of flour for each cake. How much flour is needed for the party?", "the number of cakes", "{x}"),
    ("A car uses {x} litres of fuel per 100 kilometres. How much fuel does the trip use?", "the length of the trip", "{x}"),
    ("A worker earns {x} dollars per hour plus a bonus. How much does she earn in a {r}-hour week?", "the size of the bonus", "{x} {r}"),
    ("Tom is {x} years older than his sister. How old is Tom?", "the sister's age", "{x}"),
    ("A tank is being filled at {x} litres per minute. How long until it is full?", "the tank's capacity and current contents", "{x}"),
    ("Each worker can pack {x} boxes per hour. How many hours will the team need to pack {r} boxes?", "the number of workers", "{x} {r}"),
]
for tmpl, miss, _ in MISS:
    for _ in range(5):
        x = random.randint(5, 50); w = random.randint(2, 30); r = random.randint(1, max(2, w - 1)) if "{r}" in tmpl else 0
        if "{r}" in tmpl and "pack" in tmpl: r = random.randint(50, 400)
        if "bonus" in tmpl: r = random.randint(20, 45)
        add("C6", "missing-quantity", "en", tmpl.format(x=x, w=w, r=r), "missing", None, "State/Thing", missing=miss,
            notes="one quantity needed for the answer is not given")

# --------------------------------------------------------------------------- C7 distractors (irrelevant facts, some with ambiguous verbs)
DIST = [
    "Jug B, which is not used here, holds {z} litres.",
    "The tap was installed {z} years ago.",
    "A second jug on the shelf contains {z} litres.",
    "Yesterday, jug A had {z} litres of water in it.",
    "The sink can drain {z} litres per minute.",
]
for k in range(40):
    c, w = random.randint(4, 40), 0
    w = random.randint(0, c - 1); z = random.randint(2, 60)
    dsent = DIST[k % len(DIST)].format(z=z)
    s = f"Jug A can hold at most {c} litres. {dsent} Jug A has {w} litres of water in it right now. How many more litres of water can be poured into jug A?"
    add("C7", "distractor", "en", s, "answer", c - w, "Thing",
        notes="the extra sentence is irrelevant, sometimes with a role-ambiguous verb on another thing or another time")

# --------------------------------------------------------------------------- C8 impossible or contradictory
for _ in range(15):  # unreachable goals (gcd)
    while True:
        a, b = random.randint(3, 12), random.randint(3, 12)
        from math import gcd
        if a != b and gcd(a, b) > 1: break
    g = random.choice([x for x in range(1, max(a, b)) if x % gcd(a, b) != 0])
    s = (f"Jug A can hold exactly {a} litres and jug B exactly {b} litres; both start empty. You may fill a jug from the tap, "
         f"empty a jug into the sink, or pour one jug into the other until the first is empty or the second is full. "
         f"What is the smallest number of actions that leaves exactly {g} litres in one of the jugs? If it cannot be done, say that it is impossible.")
    add("C8", "unreachable-goal", "en", s, "impossible", "impossible", "Relationship", notes=f"gcd({a},{b})={gcd(a,b)} does not divide {g}")
for _ in range(15):  # stated contents above stated capacity
    c = random.randint(3, 20); w = c + random.randint(1, 10)
    s = f"Jug A can hold at most {c} litres. Jug A has {w} litres of water in it right now. How many more litres of water can be poured into jug A?"
    add("C8", "contradiction", "en", s, "impossible", "contradiction", "Thing/State",
        notes="the stated contents exceed the stated capacity; the answer should name the contradiction")

# --------------------------------------------------------------------------- C9 reference ambiguity (which Thing)
for _ in range(15):
    a, b = random.sample(range(3, 10), 2)
    w = random.randint(1, min(a, b) - 1)
    s = (f"Jug A can hold at most {a} litres and jug B at most {b} litres. Jug A is poured into jug B, and then it has {w} litres of water in it. "
         f"How many more litres can be poured into it?")
    add("C9", "pronoun-ambiguous", "en", s, "clarify", None, "Thing",
        readings={"it=A": a - w, "it=B": b - w} if a != b else {"it=A": a - w, "it=B": b - w},
        notes="'it' can be jug A or jug B")
for _ in range(15):
    a, b = random.randint(3, 9), random.randint(3, 9); w = random.randint(0, b - 1)
    s = (f"Jug A can hold at most {a} litres and jug B at most {b} litres. Jug A is poured into jug B, and then jug B has {w} litres of water in it. "
         f"How many more litres can be poured into jug B?")
    add("C9", "reference-clear", "en", s, "answer", b - w, "Thing", notes="control")

# --------------------------------------------------------------------------- C10 jug planning, clear wording, four languages
PLAN = {
    "en": "Jug A can hold exactly {a} litres and jug B exactly {b} litres; both start empty. You may fill a jug from the tap, empty a jug into the sink, or pour one jug into the other until the first is empty or the second is full. What is the smallest number of actions that leaves exactly {g} litres in one of the jugs?",
    "fr": "La cruche A a une capacité de {a} litres et la cruche B de {b} litres ; les deux sont vides au départ. On peut remplir une cruche au robinet, vider une cruche dans l'évier, ou verser une cruche dans l'autre jusqu'à ce que la première soit vide ou la seconde pleine. Quel est le plus petit nombre d'actions qui laisse exactement {g} litres dans l'une des cruches ?",
    "es": "La jarra A tiene una capacidad de {a} litros y la jarra B de {b} litros; las dos empiezan vacías. Se puede llenar una jarra en el grifo, vaciar una jarra en el fregadero o echar una jarra en la otra hasta que la primera quede vacía o la segunda llena. ¿Cuál es el menor número de acciones que deja exactamente {g} litros en una de las jarras?",
    "de": "Krug A fasst genau {a} Liter und Krug B genau {b} Liter; beide sind anfangs leer. Man kann einen Krug am Hahn füllen, einen Krug in die Spüle leeren oder einen Krug in den anderen gießen, bis der erste leer oder der zweite voll ist. Was ist die kleinste Zahl von Aktionen, nach der genau {g} Liter in einem der Krüge sind?",
}
base = []
while len(base) < 10:
    a, b = random.sample(range(3, 14), 2)
    from math import gcd
    if gcd(a, b) != 1: continue
    g = random.choice([x for x in range(1, max(a, b)) if x not in (a, b)])
    base.append((a, b, g, bfs((a, b), g)))
for lang, t in PLAN.items():
    for a, b, g, st in base:
        add("C10", "plan-clear", lang, t.format(a=a, b=b, g=g), "answer", st, "Action/State",
            notes="clear wording; the same ten instances in four languages")

# --------------------------------------------------------------------------- dedupe and renumber
seen, out = set(), []
for it in ITEMS:
    if it["prompt"] not in seen:
        seen.add(it["prompt"]); out.append(it)
n = Counter()
for it in out:
    n[it["category"]] += 1; it["id"] = f"{it['category']}-{n[it['category']]:03d}"
ITEMS = out

# --------------------------------------------------------------------------- write
with open("items.jsonl", "w", encoding="utf-8") as f:
    for it in ITEMS:
        f.write(json.dumps(it, ensure_ascii=False) + "\n")
print(len(ITEMS), "items")
print(Counter(i["category"] for i in ITEMS))
print(Counter(i["expect"] for i in ITEMS))
print(Counter(i["lang"] for i in ITEMS))
