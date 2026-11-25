"""Rewrite-once test for STAR-Clarify: fix the prompt one time, then solve it without the skill.

Pass 1 (make): a rewriter (the model with the skill, or the model alone) rewrites each ambiguous prompt
               so that it reads one way, or asks its author a question.
Pass 2:        run.py on the rewritten prompts, conditions base and probe (no skill at solving time).
Report (score): what the rewriter did, whether the rewritten prompt is judged clear, and whether the
               answer to it agrees with one reading of the original. Code only, no judge.

  python rewrite.py make --rewriter skill --items items.jsonl items-heldout.jsonl --categories C2,H2 --out out\\rw-skill  [provider options as run.py]
  python run.py --items out\\rw-skill\\items-rewritten.jsonl --conditions base,probe --out out\\rw-skill\\solve  [provider options]
  python rewrite.py score out\\rw-skill
"""
import argparse, json, pathlib, sys, time
import run as R
from score import final_line, kind, same
from probe import verdict
HERE = pathlib.Path(__file__).parent

ASKREWRITE = ("\n\nDo not solve this prompt. You are helping its author improve it before it is sent to another reader. "
              "Rewrite it so that every value and every rule in it can be read in only one way. Keep its meaning, its numbers and its question. "
              "If you cannot do that without asking the author a question, ask the question and do not rewrite.\n"
              "End your reply in one of these two forms:\n"
              "REWRITE:\n<the complete rewritten prompt, and nothing after it>\n"
              "or one last line:\nFINAL: ASK: <your one question to the author>")

def parse(text):
    t = text.strip()
    i = t.rfind("REWRITE:")
    f = final_line(t)
    if f is not None and kind(f) == "ask" and (i < 0 or t.rfind("FINAL:") > i):
        return "asked", f
    if i >= 0:
        body = t[i + 8:].strip().strip("`").strip()
        if body: return "rewrote", body
    return "noformat", ""

def make(a):
    R.TIMEOUT = a.timeout
    items = []
    for f in a.items: items += [json.loads(l) for l in open(f, encoding="utf-8")]
    keep = set(",".join(a.categories).replace(" ", "").split(","))
    items = [i for i in items if i["category"] in keep and i["expect"] == "clarify"]
    system = R.skill_text(a.skill) if a.rewriter == "skill" else None
    out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
    log = out / "rewrites.jsonl"
    done = {json.loads(l)["id"] for l in open(log, encoding="utf-8")} if log.exists() else set()
    print(f"{len(items)} prompts to rewrite, rewriter: {a.rewriter}, model {a.model}")
    if a.dry_run:
        print("--- example user message ---\n" + items[0]["prompt"] + ASKREWRITE); return
    s = R.Subject(a)
    with open(log, "a", encoding="utf-8") as f:
        for n, it in enumerate(items, 1):
            if it["id"] in done: continue
            t0 = time.time(); text, ti, to = s.ask(system, it["prompt"] + ASKREWRITE)
            if not text.strip(): continue          # cut off: asked again on the next run
            act, body = parse(text)
            f.write(json.dumps({"id": it["id"], "action": act, "text": body, "response": text, "out_tokens": to,
                                "seconds": round(time.time() - t0, 1)}, ensure_ascii=False) + "\n"); f.flush()
            if n % 10 == 0: print(f"{n}/{len(items)}")
    by = {i["id"]: i for i in items}
    with open(out / "items-rewritten.jsonl", "w", encoding="utf-8") as f:
        for l in open(log, encoding="utf-8"):
            r = json.loads(l)
            if r["action"] == "rewrote":
                it = dict(by[r["id"]]); it["original"] = it["prompt"]; it["prompt"] = r["text"]
                f.write(json.dumps(it, ensure_ascii=False) + "\n")
    print(f"done -> {out / 'items-rewritten.jsonl'}\nNext: python run.py --items {out / 'items-rewritten.jsonl'} --conditions base,probe --out {out / 'solve'}")

def score(a):
    out = pathlib.Path(a.run)
    rw = [json.loads(l) for l in open(out / "rewrites.jsonl", encoding="utf-8")]
    n = len(rw); acts = {k: sum(r["action"] == k for r in rw) for k in ("rewrote", "asked", "noformat")}
    L = ["# STAR-Clarify rewrite-once test", "", f"Ambiguous prompts given to the rewriter: {n}.", "",
         "## What the rewriter did", "", "| Action | n | share |", "|---|---|---|",
         f"| rewrote the prompt | {acts['rewrote']} | {100 * acts['rewrote'] / n:.1f}% |",
         f"| asked the author a question | {acts['asked']} | {100 * acts['asked'] / n:.1f}% |",
         f"| no usable output | {acts['noformat']} | {100 * acts['noformat'] / n:.1f}% |",
         f"| mean output tokens | {sum(r['out_tokens'] for r in rw) / n:.0f} | |"]
    sp = out / "solve" / "responses.jsonl"
    if sp.exists():
        items = {}
        for l in open(out / "items-rewritten.jsonl", encoding="utf-8"):
            i = json.loads(l); items[i["id"]] = i
        res = {"base": {}, "probe": {}}
        for l in open(sp, encoding="utf-8"):
            r = json.loads(l)
            if r["condition"] in res: res[r["condition"]][r["id"]] = r
        pv = [verdict(r["response"]) for r in res["probe"].values()]
        if pv:
            L += ["", "## Rewritten prompts judged by the model (probe)", "", f"- Called clear: {sum(x == 'clear' for x in pv)} of {len(pv)} ({100 * sum(x == 'clear' for x in pv) / len(pv):.1f}%)."]
        cnt = {}
        for i, r in res["base"].items():
            f = final_line(r["response"]); k = kind(f); rd = items[i]["readings"] or {}
            if k == "noformat": o = "no final line"
            elif k in ("ask", "impossible"):
                o = "asks or reports a missing value (agrees with a reading whose answer is unknown)" if any(g is None for g in rd.values()) else "asks or reports a problem (agrees with no reading)"
            else:
                hit = [name for name, g in rd.items() if g is not None and same(f, g)]
                o = f"answers under the reading '{hit[0]}'" if hit else "answers with a value that matches no reading"
            cnt[o] = cnt.get(o, 0) + 1
        if cnt:
            m = len(res["base"])
            L += ["", "## Solving the rewritten prompt without the skill", "", "| Outcome | n | share |", "|---|---|---|"]
            for o in sorted(cnt, key=cnt.get, reverse=True): L.append(f"| {o} | {cnt[o]} | {100 * cnt[o] / m:.1f}% |")
            L.append(f"| mean output tokens | {sum(r.get('out_tokens', 0) for r in res['base'].values()) / m:.0f} | |")
    (out / "rewrite.md").write_text("\n".join(L) + "\n", encoding="utf-8"); print("\n".join(L))

def main():
    ap = argparse.ArgumentParser(); sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("make")
    m.add_argument("--rewriter", default="skill", choices=["skill", "base"])
    m.add_argument("--items", nargs="+", default=[str(HERE / "items.jsonl"), str(HERE / "items-heldout.jsonl")])
    m.add_argument("--categories", nargs="+", default=["C2,H2"])
    m.add_argument("--skill", default=str(HERE / "skill" / "tested" / "SKILL.md"))
    m.add_argument("--provider", default="anthropic", choices=["anthropic", "openai"])
    m.add_argument("--base-url", default=""); m.add_argument("--key-env", default="ANTHROPIC_API_KEY")
    m.add_argument("--model", default="claude-opus-5-5")
    m.add_argument("--price-in", type=float, default=0.0); m.add_argument("--price-out", type=float, default=0.0)
    m.add_argument("--max-tokens", type=int, default=16000); m.add_argument("--temperature", type=float, default=None)
    m.add_argument("--timeout", type=int, default=600); m.add_argument("--out", required=True)
    m.add_argument("--dry-run", action="store_true")
    s = sub.add_parser("score"); s.add_argument("run")
    a = ap.parse_args()
    make(a) if a.cmd == "make" else score(a)

if __name__ == "__main__":
    main()
