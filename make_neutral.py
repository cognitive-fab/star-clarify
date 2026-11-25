"""Neutral-question items for STAR-Clarify: minimal triples on the verb form.

  python make_neutral.py     -> items-neutral.jsonl

The C2 template ends with "Then r are removed", which presupposes that something is there and so favours
the contents reading. Here the question follows the statement directly, and only the verb form changes:

N2  simple present   "The lift carries 34 people."                  two readings        expect: clarify
N3  progressive      "The lift is carrying 34 people right now."    current amount      expect: answer (34)
N4  modal            "The lift can carry at most 34 people."        property only       expect: missing (current amount)
"""
import json, random
random.seed(20261125)
# thing, counted noun, simple present, progressive, modal, question
DOM = [
    ("the lift", "people", "carries", "is carrying", "can carry", "How many people are in the lift right now?"),
    ("jug A", "litres of water", "holds", "is holding", "can hold", "How many litres of water are in jug A right now?"),
    ("the car park", "cars", "holds", "is holding", "can hold", "How many cars are in the car park right now?"),
    ("the shelter", "dogs", "houses", "is housing", "can house", "How many dogs are in the shelter right now?"),
    ("the server", "websites", "hosts", "is hosting", "can host", "How many websites are on the server right now?"),
    ("the ferry", "cars", "transports", "is transporting", "can transport", "How many cars are on the ferry right now?"),
    ("the barn", "cows", "shelters", "is sheltering", "can shelter", "How many cows are in the barn right now?"),
    ("the hostel", "guests", "accommodates", "is accommodating", "can accommodate", "How many guests are in the hostel right now?"),
]
ITEMS = []
def cap1(t): return t[0].upper() + t[1:]
def add(cat, sub, prompt, expect, gold=None, notes="", readings=None, missing=None):
    n = len([i for i in ITEMS if i["category"] == cat]) + 1
    ITEMS.append(dict(id=f"{cat}-{n:03d}", category=cat, sub=sub, lang="en", prompt=prompt, expect=expect,
                      gold=None if gold is None else str(gold), readings=readings, missing=missing, star="Thing", notes=notes))
for thing, noun, sp, prog, modal, q in DOM:
    for x in random.sample(range(10, 61), 5):
        add("N2", f"neutral-simple-{sp}", f"{cap1(thing)} {sp} {x} {noun}. {q}", "clarify",
            notes=f"'{sp} {x} {noun}' can state what is in or on {thing} now, or what {thing} can take; under the second reading the current number is not given",
            readings={"contents": x, "capacity": None})
        add("N3", f"neutral-progressive-{sp}", f"{cap1(thing)} {prog} {x} {noun} right now. {q}", "answer", gold=x,
            notes="control: the progressive and 'right now' give the current amount")
        add("N4", f"neutral-modal-{sp}", f"{cap1(thing)} {modal} at most {x} {noun}. {q}", "missing",
            notes="control: the modal gives the capacity only", missing=f"the number of {noun} in or on {thing} right now")
with open("items-neutral.jsonl", "w", encoding="utf-8") as f:
    for i in ITEMS: f.write(json.dumps(i, ensure_ascii=False) + "\n")
print(len(ITEMS), "items")
for i in ITEMS[:3] + ITEMS[60:63]: print(i["id"], i["expect"], "|", i["prompt"])
