"""STAR-Clarify model panel: do several models find the "ambiguous" items ambiguous?

A substitute for human labellers. Each panel model reads every ambiguous item and an
equal number of clear controls, with no mention of STAR or of the expected label, and
says whether the wording allows two readings with different answers.

  python panel.py --dry-run
  python panel.py                      (models listed in panel.json)
  python panel.py --report-only        (rebuild panel/panel.md from saved labels)

Add a model by adding an entry to panel.json, for example a local one:
  {"name": "qwen3-30b", "provider": "openai", "base_url": "http://<amd-box>:8000/v1", "model": "Qwen/Qwen3-30B-A3B", "key_env": "NONE"}
"""
import argparse, json, pathlib, random, sys, types
from collections import defaultdict
import run as R

HERE = pathlib.Path(__file__).parent
ASK = ("Here is a short problem as it was given to a reader.\n\n---\n{p}\n---\n\n"
       "Does its wording allow two reasonable readings that lead to different answers? "
       "Judge the wording only; do not solve the problem at length. Reply with JSON only:\n"
       '{{"label": "clear" or "ambiguous", "readings": "<if ambiguous: the two readings, in one sentence>"}}')


def label_of(text):
    try:
        i, j = text.find("{"), text.rfind("}")
        v = json.loads(text[i:j + 1]).get("label", "").strip().lower()
        return v if v in ("clear", "ambiguous") else "unreadable"
    except Exception:
        t = text.lower()
        return "ambiguous" if '"ambiguous"' in t else "clear" if '"clear"' in t else "unreadable"


def report(out, items, models):
    L = defaultdict(dict)
    for l in open(out / "labels.jsonl", encoding="utf-8"):
        r = json.loads(l); L[r["id"]][r["model"]] = r["label"]
    names = [m["name"] for m in models if any(m["name"] in v for v in L.values())]
    rows = [(it, L[it["id"]]) for it in items if len(L[it["id"]]) == len(names)]
    if not rows:
        sys.exit("No complete labels yet.")
    gold = lambda it: "ambiguous" if it["expect"] == "clarify" else "clear"
    T = [f"# STAR-Clarify model panel", "", f"Panel: {', '.join(names)}. Items labelled by every model: {len(rows)}.",
         "", "This panel replaces human labellers. Models can share blind spots, so agreement here is weaker evidence than agreement between people.", "",
         "## Agreement with the benchmark's labels", "", "| Model | Ambiguous items called ambiguous | Clear items called clear |", "|---|---|---|"]
    def pct(xs): return f"{100 * sum(xs) / len(xs):.0f}% ({len(xs)})" if xs else "-"
    for n in names:
        T.append(f"| {n} | {pct([v[n] == 'ambiguous' for it, v in rows if gold(it) == 'ambiguous'])} | {pct([v[n] == 'clear' for it, v in rows if gold(it) == 'clear'])} |")
    def maj(v):
        a = sum(x == "ambiguous" for x in v.values()); return "ambiguous" if a * 2 > len(v) else "clear" if a * 2 < len(v) else "split"
    T += ["", "## Panel verdict by sub-case", "", "| Category | Sub-case | Benchmark label | n | Panel agrees | Panel split | Panel disagrees | All models agree with each other |", "|---|---|---|---|---|---|---|---|"]
    G = defaultdict(list)
    for it, v in rows: G[(it["category"], it["sub"], gold(it))].append(v)
    for (c, s, g), vs in sorted(G.items()):
        m = [maj(v) for v in vs]
        T.append(f"| {c} | {s} | {g} | {len(vs)} | {sum(x == g for x in m)} | {sum(x == 'split' for x in m)} | {sum(x not in (g, 'split') for x in m)} | {sum(len(set(v.values())) == 1 for v in vs)} |")
    bad = [(it, v) for it, v in rows if maj(v) not in (gold(it), "split")]
    T += ["", f"## Items where the panel majority disagrees with the benchmark ({len(bad)})", "",
          "Candidates to drop or reword. Their ids are also in `panel/disputed.txt`.", ""]
    for it, v in bad[:60]:
        T.append(f"- `{it['id']}` ({gold(it)} in the benchmark): {it['prompt'][:160]}")
    (out / "disputed.txt").write_text("\n".join(it["id"] for it, _ in bad) + "\n", encoding="utf-8")
    (out / "panel.md").write_text("\n".join(T) + "\n", encoding="utf-8")
    print("\n".join(T[:14 + len(names)]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=str(HERE / "items.jsonl"))
    ap.add_argument("--panel", default=str(HERE / "panel.json"))
    ap.add_argument("--budget", type=float, default=10.0, help="USD per model")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--report-only", action="store_true")
    a = ap.parse_args()
    items = [json.loads(l) for l in open(a.items, encoding="utf-8")]
    amb = [i for i in items if i["expect"] == "clarify"]
    clear = [i for i in items if i["expect"] == "answer" and i["category"] in ("C1", "C4", "C7", "C9")]
    random.Random(11).shuffle(clear)
    items = amb + clear[:len(amb)]
    random.Random(12).shuffle(items)
    models = json.load(open(a.panel, encoding="utf-8"))
    out = HERE / "panel"; out.mkdir(exist_ok=True)
    print(f"{len(items)} items ({len(amb)} ambiguous, {len(items) - len(amb)} clear) x {len(models)} models")
    if a.dry_run:
        print(ASK.format(p=items[0]["prompt"])); return
    if not a.report_only:
        done = set()
        if (out / "labels.jsonl").exists():
            for l in open(out / "labels.jsonl", encoding="utf-8"):
                r = json.loads(l); done.add((r["id"], r["model"]))
        with open(out / "labels.jsonl", "a", encoding="utf-8") as f:
            for m in models:
                ns = types.SimpleNamespace(provider=m["provider"], model=m["model"], base_url=m.get("base_url", ""),
                                           key_env=m.get("key_env", "NONE"), max_tokens=600, temperature=None,
                                           price_in=m.get("price_in", 0.0), price_out=m.get("price_out", 0.0), dry_run=False)
                s = R.Subject(ns)
                for n, it in enumerate(items, 1):
                    if (it["id"], m["name"]) in done: continue
                    if s.spent >= a.budget:
                        print(f"{m['name']}: budget reached, re-run to resume"); break
                    text, _, _ = s.ask(None, ASK.format(p=it["prompt"]))
                    f.write(json.dumps({"id": it["id"], "model": m["name"], "label": label_of(text), "raw": text[:600]}, ensure_ascii=False) + "\n"); f.flush()
                    if n % 50 == 0: print(f"{m['name']} {n}/{len(items)}  ${s.spent:.2f}")
    report(out, items, models)


if __name__ == "__main__":
    main()
