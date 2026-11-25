"""Held-out items for STAR-Clarify: verbs and things that appear in no version of the skill
and in no item of items.jsonl.

  python make_heldout.py     -> items-heldout.jsonl

H2: one role-ambiguous statement, same template as C2, with a held-out verb (expect: clarify).
H1: the same things with a clear property sentence and a clear state sentence (expect: answer).
"""
import json, random
random.seed(20261124)

# thing, unit, ambiguous verb phrase, clear property, clear state, space question, what leaves
DOM = [
    ("the granary", "sacks", "stocks {x} sacks", "has floor space for {c} sacks in total",
     "has {w} sacks on its floor right now", "How many more sacks can be brought into the granary?"),
    ("the shelter", "dogs", "houses {x} dogs", "has kennels for {c} dogs in total",
     "has {w} dogs in its kennels right now", "How many more dogs can the shelter take in?"),
    ("the server", "websites", "hosts {x} websites", "is licensed for at most {c} websites",
     "has {w} websites running on it right now", "How many more websites can be added to the server?"),
    ("the ferry", "cars", "transports {x} cars", "has deck space for {c} cars in total",
     "has {w} cars on its deck right now", "How many more cars can drive onto the ferry?"),
    ("the barn", "cows", "shelters {x} cows", "has stalls for {c} cows in total",
     "has {w} cows in its stalls right now", "How many more cows can be put in the barn?"),
    ("the cellar", "bottles", "keeps {x} bottles", "has rack space for {c} bottles in total",
     "has {w} bottles on its racks right now", "How many more bottles can be put in the cellar?"),
    ("the hostel", "guests", "accommodates {x} guests", "has beds for {c} guests in total",
     "has {w} guests checked in right now", "How many more guests can check in at the hostel?"),
    ("the theatre", "spectators", "admits {x} spectators", "has chairs for {c} spectators in total",
     "has {w} spectators sitting in it right now", "How many more spectators can sit down in the theatre?"),
]
ITEMS = []
def cap1(t): return t[0].upper() + t[1:]
def add(cat, sub, prompt, expect, gold, notes, readings=None):
    n = len([i for i in ITEMS if i["category"] == cat]) + 1
    ITEMS.append(dict(id=f"{cat}-{n:03d}", category=cat, sub=sub, lang="en", prompt=prompt, expect=expect,
                      gold=None if gold is None else str(gold), readings=readings, missing=None, star="Thing", notes=notes))

for thing, unit, va, vp, vs, q in DOM:
    verb = va.split()[0]
    for _ in range(5):
        x = random.randint(10, 60); r = random.randint(2, x - 1)
        add("H2", f"heldout-verb-{verb}", f"{cap1(thing)} {va.format(x=x)}. Then {r} {unit} are removed. How many {unit} are in {thing} now?",
            "clarify", None, f"'{verb}' can state how many {unit} {thing} has room for or how many are in it now; under the first reading the current number is unknown",
            readings={"contents": x - r, "capacity": None})
    for _ in range(5):
        c = random.randint(10, 60); w = random.randint(0, c - 1)
        a, b = f"{cap1(thing)} {vp.format(c=c)}.", f"{cap1(thing)} {vs.format(w=w)}."
        s = f"{a} {b}" if random.random() < 0.5 else f"{b} {a}"
        add("H1", f"heldout-clear-{verb}", f"{s} {q}", "answer", c - w, "control: clear property and clear state, held-out thing")

with open("items-heldout.jsonl", "w", encoding="utf-8") as f:
    for i in ITEMS: f.write(json.dumps(i, ensure_ascii=False) + "\n")
print(len(ITEMS), "items"); print(ITEMS[0]["prompt"]); print(ITEMS[5]["prompt"])
