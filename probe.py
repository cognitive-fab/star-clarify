"""Recognition probe for STAR-Clarify: does the model call a prompt unclear when asked to judge it,
and does that match what it did when asked to solve it?

  python probe.py out\\<probe run>                         recognition rates
  python probe.py out\\<probe run> --solved out\\<scored run> [more scored runs]
        adds: of the prompts the model resolved silently when solving, how many it calls unclear here

Scored by code only (no judge): the last line is FINAL: CLEAR or FINAL: UNCLEAR: ...
"""
import argparse, json, pathlib
from collections import defaultdict
HERE = pathlib.Path(__file__).parent

def verdict(text):
    for line in reversed(text.strip().splitlines()):
        l = line.strip().strip("*").strip()
        if l.upper().startswith("FINAL:"):
            u = l[6:].strip().strip("*").strip().upper()
            return "unclear" if u.startswith("UNCLEAR") else "clear" if u.startswith("CLEAR") else "noformat"
    return "noformat"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--items", nargs="+", default=[str(HERE / "items.jsonl"), str(HERE / "items-heldout.jsonl"), str(HERE / "items-neutral.jsonl"), str(HERE / "items-plan.jsonl")])
    ap.add_argument("--solved", nargs="*", default=[], help="scored run folders (scored.jsonl) of the same model")
    a = ap.parse_args()
    items = {}
    for f in a.items:
        if pathlib.Path(f).exists():
            for l in open(f, encoding="utf-8"):
                i = json.loads(l); items[i["id"]] = i
    v = {}
    for l in open(pathlib.Path(a.run) / "responses.jsonl", encoding="utf-8"):
        r = json.loads(l)
        if r["condition"] == "probe": v[r["id"]] = verdict(r["response"])
    L = ["# STAR-Clarify recognition probe", "", f"Prompts judged: {len(v)}. Without a readable last line: {sum(x == 'noformat' for x in v.values())}.", "",
         "## Share of prompts called unclear", "", "| Expected behaviour | n | called unclear |", "|---|---|---|"]
    by = defaultdict(list)
    for i, x in v.items(): by[items[i]["expect"]].append(x == "unclear")
    for e in ("answer", "clarify", "missing", "impossible"):
        if by[e]: L.append(f"| {e} | {len(by[e])} | {100 * sum(by[e]) / len(by[e]):.1f}% |")
    L += ["", "## By category", "", "| Category | Expected | n | called unclear |", "|---|---|---|---|"]
    bc = defaultdict(list)
    for i, x in v.items(): bc[(items[i]["category"], items[i]["expect"])].append(x == "unclear")
    for k in sorted(bc): L.append(f"| {k[0]} | {k[1]} | {len(bc[k])} | {100 * sum(bc[k]) / len(bc[k]):.1f}% |")
    if a.solved:
        out = defaultdict(dict)
        for d in a.solved:
            for l in open(pathlib.Path(d) / "scored.jsonl", encoding="utf-8"):
                r = json.loads(l); out[r["condition"]][r["id"]] = r["outcome"]
        L += ["", "## Recognition against behaviour (prompts expected to be clarified)", "",
              "| Condition when solving | Outcome when solving | n | called unclear in the probe |", "|---|---|---|---|"]
        for c in sorted(out):
            g = defaultdict(list)
            for i, o in out[c].items():
                if i in v and items[i]["expect"] == "clarify": g[o].append(v[i] == "unclear")
            for o in sorted(g): L.append(f"| {c} | {o} | {len(g[o])} | {100 * sum(g[o]) / len(g[o]):.1f}% |")
    (pathlib.Path(a.run) / "probe.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))

if __name__ == "__main__":
    main()
