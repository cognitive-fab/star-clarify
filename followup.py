"""Close the loop on clarifying questions: when the model asked, give it the author's answer and check
that it then solves the prompt. Code only, no judge.

  python followup.py run out\\<run folder> [provider options as run.py]     second turn for every reply that ended with a question
  python followup.py score out\\<run folder>

The author's answer always picks the reading that has an exact answer:
  ambiguous verb (C2, H2, N2): the number is the amount there now
  same verb (C3):          the 'exactly' sentence is the capacity
  'only' rules (C4):       the broad reading, given as the clear wording of the same rule
  reference (C9):          'it' is jug A
"""
import argparse, json, pathlib, re, sys, time
import run as R
from score import final_line, kind, same
HERE = pathlib.Path(__file__).parent
NEXT = "\n\nNow give your answer. End your reply with exactly one last line, in English: FINAL: <your answer>"
# with the second reading the right reply can be a question or a report, so the three forms are offered again
NEXT_OTHER = ("\n\nNow give your answer. End your reply with exactly one last line, in English, in one of these forms:\n"
              "FINAL: <your answer>\nFINAL: ASK: <your one question>\nFINAL: IMPOSSIBLE: <one-line reason>")

def load_items(files):
    L = []
    for f in files:
        if pathlib.Path(f).exists(): L += [json.loads(l) for l in open(f, encoding="utf-8")]
    return L

def author_answer(it, items, other=False):
    """Returns (text, gold) or None. other=True gives the second reading: gold None means the amount is then unknown
    (or the statements conflict), and the expected reply is a question or a report of the problem."""
    rd = it["readings"] or {}
    c = it["category"]
    if c in ("C2", "H2", "N2", "P2"):
        x = re.search(r"\d+", it["prompt"]).group()
        if other:
            return (f"The number {x} in the first sentence is the most it can take. It is not the amount that is there right now.", rd["capacity"])
        return (f"The number {x} in the first sentence is the amount that is there right now. It is not the most it can take.", rd["contents"])
    if c == "C3":
        if other:
            return ("Both sentences give the water that is in jug A right now. Neither gives its capacity.", rd["both-are-contents"])
        return ("The sentence with 'exactly' gives the capacity of jug A. The other sentence gives the water that is in jug A right now.", rd["exactly-is-capacity"])
    if c == "C4":
        i = items.index(it)
        sib = items[i + 1] if i + 1 < len(items) else None
        if not sib or sib["category"] != "C4" or sib["expect"] != "answer": return None
        a, b = it["prompt"], sib["prompt"]; n = 0
        while n < min(len(a), len(b)) and a[-1 - n] == b[-1 - n]: n += 1
        rule = b[:len(b) - n].strip()
        if not rule: return None
        if other:
            return ("I mean the strict reading: nothing is allowed except exactly what the rule states.", rd["narrow"])
        return (f"I mean this: {rule}", rd["broad"])
    if c == "C9":
        if other: return ("In both places, 'it' is jug B.", rd["it=B"])
        return ("In both places, 'it' is jug A.", rd["it=A"])
    return None

def ask2(s, system, msgs):
    a = s.a
    if a.provider == "anthropic":
        body = {"model": a.model, "max_tokens": a.max_tokens, "messages": msgs}
        if a.temperature is not None: body["temperature"] = a.temperature
        if system: body["system"] = system
        r = R.post("https://api.anthropic.com/v1/messages", body,
                   {"x-api-key": s.key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
        u = r.get("usage", {}); fam = next((k for k in R.PRICES if k in a.model), "opus")
        s.spent += (u.get("input_tokens", 0) * R.PRICES[fam][0] + u.get("output_tokens", 0) * R.PRICES[fam][1]) / 1e6
        return "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text"), u.get("output_tokens", 0)
    body = {"model": a.model, "max_tokens": a.max_tokens, "messages": ([{"role": "system", "content": system}] if system else []) + msgs}
    if a.temperature is not None: body["temperature"] = a.temperature
    h = {"Content-Type": "application/json"}
    if s.key: h["Authorization"] = f"Bearer {s.key}"
    r = R.post(a.base_url.rstrip("/") + "/chat/completions", body, h)
    return r["choices"][0]["message"].get("content") or "", r.get("usage", {}).get("completion_tokens", 0)

def channel(c):
    return R.CHANNEL_NOPRIME if c.endswith("-noprime") else R.CHANNEL

def run(a):
    R.TIMEOUT = a.timeout
    items = load_items(a.items); by = {i["id"]: i for i in items}
    out = pathlib.Path(a.run)
    todo = []
    for l in open(out / "responses.jsonl", encoding="utf-8"):
        r = json.loads(l); it = by.get(r["id"])
        if not it or it["expect"] != "clarify" or r["condition"] == "probe" or r["condition"].endswith("-noask"): continue
        if kind(final_line(r["response"])) != "ask": continue
        aa = author_answer(it, items, a.reading == "other")
        if aa: todo.append((r, it, aa))
    print(f"{len(todo)} replies ended with a question on a prompt expected to be clarified, model {a.model}")
    if a.dry_run: return
    path = out / ("followups-other.jsonl" if a.reading == "other" else "followups.jsonl")
    done = {(json.loads(l)["id"], json.loads(l)["condition"]) for l in open(path, encoding="utf-8")} if path.exists() else set()
    skills = {"skill": "SKILL.md", "skill2": "SKILL-v2.md", "skill3": "SKILL-v3.md", "control": "CONTROL.md"}
    s = R.Subject(a)
    with open(path, "a", encoding="utf-8") as f:
        for n, (r, it, (ans, gold)) in enumerate(todo, 1):
            if (r["id"], r["condition"]) in done: continue
            if s.spent >= a.budget: print(f"Budget of ${a.budget} reached; run again to resume."); return
            root = r["condition"].replace("-noprime", "")
            system = R.skill_text(pathlib.Path(a.skill).with_name(skills[root])) if root in skills else None
            msgs = [{"role": "user", "content": it["prompt"] + channel(r["condition"])},
                    {"role": "assistant", "content": r["response"]},
                    {"role": "user", "content": ans + (NEXT_OTHER if a.reading == "other" else NEXT)}]
            text, to = ask2(s, system, msgs)
            if not text.strip(): continue
            f.write(json.dumps({"id": r["id"], "condition": r["condition"], "author": ans, "gold": gold, "response": text, "out_tokens": to}, ensure_ascii=False) + "\n"); f.flush()
            if n % 10 == 0: print(f"{n}/{len(todo)}  spent ${s.spent:.2f}")
    print(f"done -> {path}\nNext: python followup.py score {out}")

def score(a):
    out = pathlib.Path(a.run); by = {i["id"]: i for i in load_items(a.items)}
    rows = [json.loads(l) for l in open(out / ("followups-other.jsonl" if a.reading == "other" else "followups.jsonl"), encoding="utf-8")]
    def res(r):
        f = final_line(r["response"]); k = kind(f)
        if k == "noformat": return "no final line"
        if r["gold"] is None:    # the reading leaves the amount unknown, or makes the statements conflict
            return "solved" if k in ("ask", "impossible") else "wrong answer"
        return "asks again" if k == "ask" else "solved" if same(f, r["gold"]) else "wrong answer"
    for r in rows: r["result"] = res(r); r["category"] = by[r["id"]]["category"]
    L = ["# STAR-Clarify: questions followed by the author's answer", "", f"Questions answered: {len(rows)}.", ""]
    for key, title in (("condition", "By condition"), ("category", "By category")):
        L += [f"## {title}", "", f"| {key} | questions | solved | asks again | wrong answer | no final line |", "|---|---|---|---|---|---|"]
        for v in sorted({r[key] for r in rows}):
            g = [r for r in rows if r[key] == v]; c = lambda o: sum(r["result"] == o for r in g)
            L.append(f"| {v} | {len(g)} | {c('solved')} ({100 * c('solved') / len(g):.1f}%) | {c('asks again')} | {c('wrong answer')} | {c('no final line')} |")
        L.append("")
    (out / ("followup-other.md" if a.reading == "other" else "followup.md")).write_text("\n".join(L), encoding="utf-8"); print("\n".join(L))

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("run", "score"):
        m = sub.add_parser(name); m.add_argument("run")
        m.add_argument("--items", nargs="+", default=[str(HERE / "items.jsonl"), str(HERE / "items-heldout.jsonl"), str(HERE / "items-neutral.jsonl"), str(HERE / "items-plan.jsonl")])
        m.add_argument("--reading", default="first", choices=["first", "other"], help="other: answer each question with the second reading")
        if name == "run":
            m.add_argument("--skill", default=str(HERE / "skill" / "tested" / "SKILL.md"))
            m.add_argument("--provider", default="anthropic", choices=["anthropic", "openai"])
            m.add_argument("--base-url", default=""); m.add_argument("--key-env", default="ANTHROPIC_API_KEY")
            m.add_argument("--model", default="claude-opus-5-5")
            m.add_argument("--price-in", type=float, default=0.0); m.add_argument("--price-out", type=float, default=0.0)
            m.add_argument("--max-tokens", type=int, default=16000); m.add_argument("--temperature", type=float, default=None)
            m.add_argument("--timeout", type=int, default=600); m.add_argument("--budget", type=float, default=10.0)
            m.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    run(a) if a.cmd == "run" else score(a)

if __name__ == "__main__":
    main()
