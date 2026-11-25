"""STAR-Clarify runner: ask a model every item, with and without the STAR skill.

Standard library only. Keys are read from environment variables set for this
process only (never write a key into a file).

  python run.py --dry-run
  python run.py --model claude-opus-5-5 --conditions base,skill
  python run.py --provider openai --base-url https://api.mistral.ai/v1 --key-env MISTRAL_API_KEY --model mistral-large-latest
  python run.py --provider openai --base-url http://<amd-box>:8000/v1 --key-env NONE --model qwen3-8b
  python run.py --model claude-opus-5-5 --sample 8        (8 items per category, quick check)
"""
import argparse, json, os, sys, time, random, datetime, pathlib, urllib.request, urllib.error
from collections import defaultdict

HERE = pathlib.Path(__file__).parent

# Added to every item in every condition, so asking is always possible and scoring is exact.
CHANNEL = ("\n\nIf you need to ask me a question before you can answer, ask it. "
           "End your reply with exactly one last line, in English, in one of these forms:\n"
           "FINAL: <your answer>\nFINAL: ASK: <your one question>\nFINAL: IMPOSSIBLE: <one-line reason>")

# No-priming variant: the reply format is fixed, but asking is never mentioned.
CHANNEL_NOPRIME = "\n\nEnd your reply with exactly one last line, in English, starting with FINAL:"

# Nobody-to-ask variant: an unattended pipeline. The model must answer; a stated reading is the only way to handle an ambiguity.
CHANNEL_NOASK = ("\n\nNobody is available to answer questions: give your best answer now. "
                 "End your reply with exactly one last line, in English, in one of these forms:\n"
                 "FINAL: <your answer>\nFINAL: IMPOSSIBLE: <one-line reason>")

# Recognition probe: the model judges the wording and does not solve the problem.
CHANNEL_PROBE = ("\n\nDo not solve this. Judge the wording only. Is there a value, a rule or a reference in this prompt that can be "
                 "read in two ways that lead to different answers, or a value needed for the answer that is not given, or two "
                 "statements that cannot both be true? End your reply with exactly one last line, in English, in one of these forms:\n"
                 "FINAL: CLEAR\nFINAL: UNCLEAR: <what is unclear, in one line>")

PRICES = {"opus": (5.0, 25.0), "fable": (15.0, 75.0), "sonnet": (3.0, 15.0), "haiku": (1.0, 5.0)}


def skill_text(path):
    s = pathlib.Path(path).read_text(encoding="utf-8")
    if s.startswith("---"):
        s = s.split("---", 2)[2]
    return ("Use the following skill whenever it applies to the user's request.\n\n" + s.strip())


TIMEOUT = 600  # seconds per request; --timeout raises it for slow local servers (CPU llama.cpp)


def post(url, body, headers, tries=6):
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST", headers=headers)
    for k in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")
            if e.code in (408, 429, 500, 502, 503, 529) and k < tries - 1:
                time.sleep(5 * 2 ** k); continue
            sys.exit(f"API error {e.code}: {msg[:500]}")
        except urllib.error.URLError as e:
            if k < tries - 1:
                time.sleep(5 * 2 ** k); continue
            sys.exit(f"Network error: {e}")


class Subject:
    def __init__(self, a):
        self.a = a
        self.key = None if a.key_env == "NONE" else os.environ.get(a.key_env)
        if a.key_env != "NONE" and not self.key and not a.dry_run:
            sys.exit(f"Environment variable {a.key_env} is not set .")
        self.spent = 0.0

    def ask(self, system, user):
        a = self.a
        if a.provider == "anthropic":
            body = {"model": a.model, "max_tokens": a.max_tokens, "messages": [{"role": "user", "content": user}]}
            if a.temperature is not None:
                body["temperature"] = a.temperature
            if system:
                body["system"] = system
            r = post("https://api.anthropic.com/v1/messages", body,
                     {"x-api-key": self.key, "anthropic-version": "2023-06-01", "content-type": "application/json"})
            text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
            u = r.get("usage", {}); ti, to = u.get("input_tokens", 0), u.get("output_tokens", 0)
            fam = next((k for k in PRICES if k in a.model), "opus")
            self.spent += (ti * PRICES[fam][0] + to * PRICES[fam][1]) / 1e6
        else:
            msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}]
            body = {"model": a.model, "max_tokens": a.max_tokens, "messages": msgs}
            if a.temperature is not None:
                body["temperature"] = a.temperature
            h = {"Content-Type": "application/json"}
            if self.key:
                h["Authorization"] = f"Bearer {self.key}"
            r = post(a.base_url.rstrip("/") + "/chat/completions", body, h)
            text = r["choices"][0]["message"].get("content") or ""
            u = r.get("usage", {}); ti, to = u.get("prompt_tokens", 0), u.get("completion_tokens", 0)
            self.spent += (ti * a.price_in + to * a.price_out) / 1e6
        return text, ti, to


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--items", default=str(HERE / "items.jsonl"))
    ap.add_argument("--skill", default=str(HERE / "skill" / "tested" / "SKILL.md"))
    ap.add_argument("--conditions", nargs="+", default=["base,skill"], help="any of base, skill, skill2, skill3, control (careful-reading prompt without STAR), probe (judge the wording, do not solve); add -noprime (e.g. base-noprime) to drop the line that says asking is allowed, or -noask (e.g. skill-noask) to say that nobody can be asked")
    ap.add_argument("--provider", default="anthropic", choices=["anthropic", "openai"])
    ap.add_argument("--base-url", default="")
    ap.add_argument("--key-env", default="ANTHROPIC_API_KEY")
    ap.add_argument("--model", default="claude-opus-5-5")
    ap.add_argument("--price-in", type=float, default=0.0, help="USD per million input tokens (openai provider)")
    ap.add_argument("--price-out", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=16000)
    ap.add_argument("--temperature", type=float, default=None, help="omit for models that refuse it (Opus 5.5)")
    ap.add_argument("--sample", type=int, default=0, help="items per category (0 = all)")
    ap.add_argument("--exclude", default="", help="a responses.jsonl: items already in it are left out (to test on items a skill version has not been tuned on)")
    ap.add_argument("--categories", nargs="*", default=[], help="e.g. C2,C3")
    ap.add_argument("--budget", type=float, default=30.0, help="stop when this many USD are spent")
    ap.add_argument("--out", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--timeout", type=int, default=600, help="seconds per request (raise for a slow local server)")
    a = ap.parse_args()
    global TIMEOUT
    TIMEOUT = a.timeout
    # PowerShell splits a,b,c into separate arguments: accept both forms
    a.conditions = ",".join(a.conditions).replace(" ", "")
    a.categories = ",".join(a.categories).replace(" ", "")

    items = [json.loads(l) for l in open(a.items, encoding="utf-8")]
    if a.categories:
        keep = set(a.categories.split(",")); items = [i for i in items if i["category"] in keep]
    if a.exclude:
        seen = {json.loads(l)["id"] for l in open(a.exclude, encoding="utf-8")}
        items = [i for i in items if i["id"] not in seen]
    if a.sample:
        rnd = random.Random(7); by = defaultdict(list)
        for i in items: by[i["category"]].append(i)
        items = [x for c in sorted(by) for x in rnd.sample(by[c], min(a.sample, len(by[c])))]
    conds = a.conditions.split(",")
    roots = {c.replace("-noprime", "").replace("-noask", "") for c in conds}
    bad = roots - {"base", "skill", "skill2", "skill3", "control", "probe"}
    if bad:
        sys.exit(f"Unknown condition: {sorted(bad)}")
    systems = {"base": None, "probe": None, "skill": skill_text(a.skill),
               "control": skill_text(pathlib.Path(a.skill).with_name("CONTROL.md")) if "control" in roots else None,
               "skill2": skill_text(pathlib.Path(a.skill).with_name("SKILL-v2.md")) if "skill2" in roots else None,
               "skill3": skill_text(pathlib.Path(a.skill).with_name("SKILL-v3.md")) if "skill3" in roots else None}

    print(f"{len(items)} items x {len(conds)} conditions = {len(items) * len(conds)} calls, model {a.model}")
    if a.dry_run:
        print("--- example user message ---\n" + items[0]["prompt"] + CHANNEL); return

    tag = a.model.replace("/", "_").replace(":", "_")
    out = pathlib.Path(a.out or HERE / "out" / f"{datetime.date.today()}-{tag}")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "responses.jsonl"
    done = set()
    if path.exists():   # keep finished replies; an empty reply (cut off at the token limit) is asked again
        keep = [l for l in open(path, encoding="utf-8") if json.loads(l)["response"].strip()]
        open(path, "w", encoding="utf-8").writelines(keep)
        for l in keep:
            r = json.loads(l); done.add((r["id"], r["condition"]))
    json.dump(vars(a), open(out / "config.json", "w"), indent=1)
    (HERE / "out" / "last-run.txt").write_text(str(out.resolve()), encoding="utf-8")   # the folder of the last run

    s = Subject(a)
    with open(path, "a", encoding="utf-8") as f:
        for n, it in enumerate(items, 1):
            for c in conds:
                if (it["id"], c) in done:
                    continue
                if s.spent >= a.budget:
                    print(f"Budget of ${a.budget} reached; re-run the same command to resume."); return
                t0 = time.time()
                text, ti, to = s.ask(systems[c.replace("-noprime", "").replace("-noask", "")],
                                     it["prompt"] + (CHANNEL_PROBE if c == "probe" else CHANNEL_NOASK if c.endswith("-noask") else CHANNEL_NOPRIME if c.endswith("-noprime") else CHANNEL))
                f.write(json.dumps({"id": it["id"], "condition": c, "model": a.model, "response": text,
                                    "in_tokens": ti, "out_tokens": to, "seconds": round(time.time() - t0, 1)},
                                   ensure_ascii=False) + "\n"); f.flush()
            if n % 10 == 0:
                print(f"{n}/{len(items)}  spent ${s.spent:.2f}")
    print(f"done, spent ${s.spent:.2f} -> {path}\nNext: python score.py {out}")


if __name__ == "__main__":
    main()
