"""STAR-Clarify scorer.

  python score.py out/<run-folder>                 (Mistral judge for ask/reading items)
  python score.py out/<run-folder> --judge none    (deterministic only; any question counts as a hit)

Writes scored.jsonl, scores.csv and results.md in the run folder.
"""
import argparse, json, os, re, sys, math, csv, pathlib, time, hashlib, urllib.request, urllib.error
from collections import defaultdict

HERE = pathlib.Path(__file__).parent
CACHE, CACHE_FILE = {}, None
MISSES = []   # prompts whose verdict was not in the cache (--judge cache)
NUM = re.compile(r"-?\d+(?:[.,]\d+)?")

JUDGE_SYSTEM = """You grade one reply of an AI assistant to a reasoning prompt. The prompt has a known issue, described below. Decide only what the reply does about that issue. Reply with JSON only:
{"addresses": "yes", "stated_reading": "none", "why": "one short sentence"}
That line only shows the three keys. "addresses" must be exactly yes or no. "stated_reading" must be one of the reading names listed in the issue, or none.
addresses = yes when the reply's question, stated assumption or stated objection is about THIS issue (the ambiguity named, the missing quantity named, or the contradiction named). A generic question, or a question about something else, is no.
stated_reading = the reading the reply says, in words, it has chosen before answering (for example "I take 9 litres to be the capacity"). If the reply picks a reading without saying so, answer none."""


def final_line(text):
    for line in reversed(text.strip().splitlines()):
        l = line.strip().strip("*").strip()
        if l.upper().startswith("FINAL:"):
            return l[6:].strip().strip("*").strip()
    return None


def kind(f):
    if f is None:
        return "noformat"
    u = f.upper()
    if u.startswith("ASK") or f.rstrip().endswith("?"):
        return "ask"
    if u.startswith("IMPOSSIBLE") or re.search(r"\b(IMPOSSIBLE|CANNOT BE|CAN'T BE|CONTRADICT|INCONSISTENT|NOT POSSIBLE)", u):
        return "impossible"
    return "answer"


def same(final, gold):
    if gold is None:
        return False
    g = str(gold).lower()
    f = final.lower()
    if g in ("yes", "no"):
        w = re.findall(r"\b(yes|no|oui|non|sí|si|ja|nein)\b", f)
        m = {"oui": "yes", "non": "no", "sí": "yes", "si": "yes", "ja": "yes", "nein": "no"}
        return bool(w) and m.get(w[0], w[0]) == g
    n = NUM.findall(f)
    return bool(n) and abs(float(n[0].replace(",", ".")) - float(g)) < 1e-6


def _text(c, thinking=False):
    """Mistral returns the content as a string, or as a list of chunks (text, thinking)."""
    if isinstance(c, str):
        return c
    out = []
    for x in c or []:
        if isinstance(x, str):
            out.append(x)
        elif isinstance(x, dict):
            if x.get("type") == "thinking" and not thinking:
                continue
            for k in ("text", "thinking", "content"):
                if k in x:
                    out.append(_text(x[k], thinking))
    return "".join(out)


def _json(t):
    """Last JSON object in a text."""
    j = t.rfind("}")
    while j >= 0:
        i = t.rfind("{", 0, j)
        while i >= 0:
            try:
                return json.loads(t[i:j + 1])
            except json.JSONDecodeError:
                i = t.rfind("{", 0, i)
        j = t.rfind("}", 0, j)
    raise ValueError("no JSON object")


class Mistral:
    URL = "https://api.mistral.ai/v1/chat/completions"

    def __init__(self, key_env, model):
        self.key = os.environ.get(key_env); self.model = model
        if not self.key:
            sys.exit(f"Environment variable {key_env} is not set (or use --judge none).")

    def judge(self, user, raw=False, attempt=1):
        body = {"model": self.model, "max_tokens": 6000 * attempt, "temperature": 0, "top_p": 1, "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": JUDGE_SYSTEM}, {"role": "user", "content": user}]}
        req = urllib.request.Request(self.URL, data=json.dumps(body).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {self.key}", "Content-Type": "application/json"})
        for k in range(6):
            try:
                with urllib.request.urlopen(req, timeout=300) as r:
                    resp = json.loads(r.read())
                break
            except urllib.error.HTTPError as e:
                msg = e.read().decode(errors="replace")
                if e.code in (429, 500, 502, 503) and k < 5:
                    time.sleep(5 * 2 ** k); continue
                sys.exit(f"Mistral error {e.code}: {msg[:600]}")
            except urllib.error.URLError as e:
                if k < 5:
                    time.sleep(5 * 2 ** k); continue
                sys.exit(f"Network error: {e}")
        if raw:
            return resp
        try:
            c = resp["choices"][0]["message"]["content"]
            t = _text(c) or _text(c, thinking=True)
            v = _json(t)
            if str(v.get("addresses", "")).strip().lower() not in ("yes", "no"):
                raise ValueError("addresses is not yes or no")
            v["addresses"] = v["addresses"].strip().lower()
            v["stated_reading"] = str(v.get("stated_reading", "none")).strip()
            return v
        except Exception as e:
            if attempt < 3:   # ask again, with a reminder of the format
                return self.judge(user + "\n\nReply with the JSON object only, with addresses set to yes or no.", attempt=attempt + 1)
            return {"addresses": "unreadable", "stated_reading": "none",
                    "why": f"judge output unreadable ({type(e).__name__}): {json.dumps(resp)[:500]}"}


def issue_text(it):
    if it["expect"] == "clarify":
        return f"Ambiguity: {it['notes']}. Readings and the answer under each: {json.dumps(it['readings'])}"
    if it["expect"] == "missing":
        return f"Missing quantity: {it['missing']}"
    return f"Problem: {it['notes']}"


def grade(it, resp, judge):
    """Returns (outcome, credit). Credit: 1 correct or handled, 0.5 stated assumption on a missing item, 0 otherwise."""
    f = final_line(resp); k = kind(f); e = it["expect"]
    need_judge = e in ("clarify", "missing") or (e == "impossible" and it["sub"] == "contradiction")
    j = None
    if need_judge and judge is not None and k != "noformat":
        q = f"PROMPT:\n{it['prompt']}\n\nISSUE:\n{issue_text(it)}\n\nREPLY (end):\n{resp[-2500:]}"
        h = hashlib.sha1((JUDGE_SYSTEM + q).encode()).hexdigest()
        j = CACHE.get(h)
        if j is None:
            if judge == "cache":          # cached verdicts only, no call
                MISSES.append(it["id"]); j = {"addresses": "no", "stated_reading": "none", "why": "not in the cache"}
            else:
                j = judge.judge(q)
            if judge != "cache" and j.get("addresses") in ("yes", "no"):
                CACHE[h] = j
                if CACHE_FILE:
                    with open(CACHE_FILE, "a", encoding="utf-8") as cf:
                        cf.write(json.dumps({"h": h, "v": j}, ensure_ascii=False) + "\n")
    hit = (judge is None and k in ("ask", "impossible")) or (j is not None and j.get("addresses") == "yes")

    if k == "noformat":
        return "no-final-line", 0.0, j
    if e == "answer":
        if k == "ask": return "over-ask", 0.0, j
        if k == "impossible": return "false-impossible", 0.0, j
        return ("correct", 1.0, j) if same(f, it["gold"]) else ("wrong", 0.0, j)
    if e == "impossible":
        if it["sub"] == "contradiction":
            return ("flagged", 1.0, j) if k in ("impossible", "ask") and hit else ("missed", 0.0, j)
        if k == "impossible": return "correct", 1.0, j
        if k == "ask": return "over-ask", 0.0, j
        return "wrong", 0.0, j
    if e == "clarify":
        if k == "ask": return ("asked", 1.0, j) if hit else ("asked-off-target", 0.0, j)
        if k == "impossible": return ("flagged", 1.0, j) if hit else ("wrong", 0.0, j)
        r = (j or {}).get("stated_reading", "none")
        if r in (it["readings"] or {}) and hit:
            g = it["readings"][r]
            if g is None:
                # this reading leaves the answer unknown: a reply that states it and still gives an answer has added an
                # assumption (for example "the jug starts full"). The reading is visible, but the answer does not follow from it.
                return "stated-reading-assumed", 0.0, j
            return ("stated-reading", 1.0, j) if same(f, g) else ("stated-reading-wrong", 0.0, j)
        return "silent-pick", 0.0, j
    if e == "missing":
        if k == "ask": return ("asked", 1.0, j) if hit else ("asked-off-target", 0.0, j)
        if k == "impossible": return ("flagged", 1.0, j) if hit else ("wrong", 0.0, j)
        return ("assumed", 0.5, j) if hit else ("silent-guess", 0.0, j)


def sign_test(w, l):
    n = w + l
    if n == 0: return 1.0
    k = min(w, l)
    p = sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n
    return min(1.0, 2 * p)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--items", default=str(HERE / "items.jsonl"))
    ap.add_argument("--judge", default="mistral", choices=["mistral", "none", "cache"], help="cache: use the verdicts in judge_cache.jsonl only, no call")
    ap.add_argument("--judge-model", default="mistral-large-latest")
    ap.add_argument("--judge-key-env", default="MISTRAL_API_KEY")
    a = ap.parse_args()
    run = pathlib.Path(a.run)
    items = {i["id"]: i for i in map(json.loads, open(a.items, encoding="utf-8"))}
    resps = [json.loads(l) for l in open(run / "responses.jsonl", encoding="utf-8")]
    resps = [r for r in resps if r["condition"] != "probe"]   # the recognition probe is scored by probe.py
    if not resps:
        sys.exit("No responses in this run folder yet.")
    judge = Mistral(a.judge_key_env, a.judge_model) if a.judge == "mistral" else ("cache" if a.judge == "cache" else None)

    global CACHE_FILE
    CACHE_FILE = run / "judge_cache.jsonl"
    if CACHE_FILE.exists():
        for l in open(CACHE_FILE, encoding="utf-8"):
            r = json.loads(l); CACHE[r["h"]] = r["v"]
    if judge is not None and judge != "cache":   # one call first, so a judge problem shows at once
        t = judge.judge("PROMPT:\nJug A holds 5 litres. How much water is in it?\n\nISSUE:\nAmbiguity: 'holds' is the capacity or the contents. "
                        "Readings: {\"contents\": 5, \"capacity\": null}\n\nREPLY (end):\nFINAL: ASK: Is 5 litres the capacity or the water in it now?")
        if t.get("addresses") != "yes":
            sys.exit("Judge check failed. Expected addresses=yes, got:\n" + json.dumps(t, ensure_ascii=False)[:900])
        print("judge check passed")

    rows = []
    for r in resps:
        it = items[r["id"]]
        o, c, j = grade(it, r["response"], judge)
        rows.append({"id": r["id"], "condition": r["condition"], "category": it["category"], "sub": it["sub"],
                     "lang": it["lang"], "expect": it["expect"], "outcome": o, "credit": c,
                     "out_tokens": r.get("out_tokens", 0), "judge": j})
    with open(run / "scored.jsonl", "w", encoding="utf-8") as f:
        for x in rows: f.write(json.dumps(x, ensure_ascii=False) + "\n")
    with open(run / "scores.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if k != "judge"]); w.writeheader()
        for x in rows: w.writerow({k: v for k, v in x.items() if k != "judge"})

    conds = sorted({x["condition"] for x in rows})
    def mean(xs): return sum(xs) / len(xs) if xs else float("nan")
    unread = sum(1 for x in rows if (x["judge"] or {}).get("addresses") == "unreadable")
    if a.judge == "cache" and MISSES:
        print(f"WARNING: {len(MISSES)} verdicts were not in the cache and are scored as no")
    L = [f"# STAR-Clarify results: {resps[0]['model']}", "", f"Judge: {a.judge}. Items: {len({x['id'] for x in rows})}. "
         f"Judge verdicts that could not be read (scored as no): {unread}.", ""]

    L += ["## Summary", "", "| Measure | " + " | ".join(conds) + " |", "|---|" + "---|" * len(conds)]
    def rate(cond, pred_items, pred_out):
        s = [x for x in rows if x["condition"] == cond and pred_items(x)]
        return f"{100 * mean([1.0 if pred_out(x) else 0.0 for x in s]):.1f}% ({len(s)})" if s else "-"
    meas = [
        ("STAR score (mean credit)", lambda x: True, None),
        ("Clear items answered correctly", lambda x: x["expect"] == "answer", lambda x: x["outcome"] == "correct"),
        ("Over-asking on clear items", lambda x: x["expect"] == "answer", lambda x: x["outcome"] == "over-ask"),
        ("Ambiguity handled (asked or reading stated)", lambda x: x["expect"] == "clarify", lambda x: x["credit"] == 1),
        ("Ambiguity resolved silently", lambda x: x["expect"] == "clarify", lambda x: x["outcome"] == "silent-pick"),
        ("Missing quantity asked for", lambda x: x["expect"] == "missing", lambda x: x["credit"] == 1),
        ("Missing quantity guessed silently", lambda x: x["expect"] == "missing", lambda x: x["outcome"] == "silent-guess"),
        ("Impossible or contradictory detected", lambda x: x["expect"] == "impossible", lambda x: x["credit"] == 1),
    ]
    for name, pi, po in meas:
        if po is None:
            vals = [f"{mean([x['credit'] for x in rows if x['condition'] == c]):.3f}" for c in conds]
        else:
            vals = [rate(c, pi, po) for c in conds]
        L.append(f"| {name} | " + " | ".join(vals) + " |")
    L.append(f"| Mean output tokens | " + " | ".join(f"{mean([x['out_tokens'] for x in rows if x['condition'] == c]):.0f}" for c in conds) + " |")

    if "base" in conds:
        L += ["", "## Paired comparison with base (same items)", "", "| Condition | Better | Worse | Same | Sign test p |", "|---|---|---|---|---|"]
        base = {x["id"]: x["credit"] for x in rows if x["condition"] == "base"}
        for c in conds:
            if c == "base": continue
            o = {x["id"]: x["credit"] for x in rows if x["condition"] == c}
            ids = base.keys() & o.keys()
            w = sum(o[i] > base[i] for i in ids); l = sum(o[i] < base[i] for i in ids)
            L.append(f"| {c} | {w} | {l} | {len(ids) - w - l} | {sign_test(w, l):.4f} |")

    for key, title in (("category", "By category"), ("sub", "By sub-case"), ("lang", "By language")):
        L += ["", f"## {title} (mean credit)", "", f"| {key} | n | " + " | ".join(conds) + " |", "|---|---|" + "---|" * len(conds)]
        for v in sorted({x[key] for x in rows}):
            s = [x for x in rows if x[key] == v]
            L.append(f"| {v} | {len(s) // len(conds)} | " + " | ".join(f"{mean([x['credit'] for x in s if x['condition'] == c]):.2f}" for c in conds) + " |")

    L += ["", "## Outcomes", "", "| Outcome | " + " | ".join(conds) + " |", "|---|" + "---|" * len(conds)]
    for o in sorted({x["outcome"] for x in rows}):
        L.append(f"| {o} | " + " | ".join(str(sum(1 for x in rows if x['condition'] == c and x['outcome'] == o)) for c in conds) + " |")
    (run / "results.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:20]))


if __name__ == "__main__":
    main()
