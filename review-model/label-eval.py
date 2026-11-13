"""Measures what the new labels on khatka's uncertain pairs do to it (13 November 2026, his words: "parse and interpret more
from the papers and books. Label more"). Writes nothing the tool reads. Usage (from boardgame-builder): python3 review-model/label-eval.py

The labels are in review-model/source-labels-*.jsonl: one reader per pair, who searched the books and papers and labelled the
pair from a source (its copied words must be found in the source's text, or the line counts as inference) or by inference.
  1. How far one reader can be trusted: on pairs the three earlier readers also voted on, how often the new label agrees
     with their majority.
  2. khatka as it stands, on the newly labelled pairs nobody had voted on: an outside test it never trained on.
  3. khatka retrained with the new labels, each held out of its own fold, on the same pairs: the change is what labelling did.
     A source label is taken as settled (0 or 1); an inference label as one reader, softened by the agreement measured in 1.
"""
import glob, json, os, random, re

LIB = os.path.expanduser("~/play-and-game-research")
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", re.sub(r"-\s*\n\s*", "", t.lower())).strip()

# The copied words are checked against the library on the Mac, where it is (python3 review-model/label-eval.py --check writes
# review-model/source-labels-checked.json); gpubox, which has no library, reads that file.
CHECKED = "review-model/source-labels-checked.json"
if "--check" in __import__("sys").argv:
    ok = {}
    for f in sorted(glob.glob("review-model/source-labels-*.jsonl")):
        for r in map(json.loads, open(f)):
            path = os.path.join(LIB, (r.get("stem") or "").strip() + ".md")
            ok[r["pair"]] = r["basis"] == "source" and os.path.exists(path) and len(norm(r.get("words", "")).split()) >= 3 and norm(r["words"]) in norm(open(path, errors="ignore").read())
    json.dump(ok, open(CHECKED, "w"), indent=0); print(f"checked {len(ok)} labels: {sum(ok.values())} source words found"); raise SystemExit
found = json.load(open(CHECKED))
src = open("review-model/rules.py").read().split("json.dump(")[0]
ns = {"__file__": "review-model/rules.py", "__name__": "label-eval"}; exec(compile(src, "rules", "exec"), ns)
VOTES, fit, prob, features, reason, current = ns["VOTES"], ns["fit"], ns["prob"], ns["features"], ns["reason"], ns["p_clash"]
VOTES = {"+".join(k) if isinstance(k, tuple) else k: v for k, v in VOTES.items()}
labels, by_source, refused = {}, 0, 0
for f in sorted(glob.glob("review-model/source-labels-*.jsonl")):
    for r in map(json.loads, open(f)):
        if r["label"] not in ("holds", "clashes"):
            continue
        basis = r["basis"]
        if basis == "source":
            if found.get(r["pair"]): by_source += 1
            else: basis = "inference"; refused += 1
        labels[r["pair"]] = (int(r["label"] == "clashes"), basis)
print(f"new labels: {len(labels)} ({by_source} from a source whose words were found, {refused} source claims whose words were not, counted as inference)")

# 1. one reader against the three
both = [p for p in labels if p in VOTES and VOTES[p] != 0.5]
agree = sum(labels[p][0] == (VOTES[p] > 0.5) for p in both)
rel = agree / len(both) if both else 0.8
print(f"1. one new reader agrees with the three readers' majority on {agree} of {len(both)} pairs ({100 * rel:.0f}%)")

# 2. khatka as it stands, on pairs nobody had voted on
test = sorted(p for p in labels if p not in VOTES and p in current)
y = {p: labels[p][0] for p in test}
def scores(pred):
    brier = sum((pred[p] - y[p]) ** 2 for p in test) / len(test)
    acc = sum((pred[p] >= 0.5) == bool(y[p]) for p in test) / len(test)
    return brier, acc
b0, a0 = scores(current)
print(f"2. before: on {len(test)} newly labelled pairs ({sum(y.values())} clash), Brier {b0:.3f}, the 50% line matches the label on {100 * a0:.0f}%")

# 3. retrained with the new labels, each pair held out of its own fold
soft = lambda p: float(labels[p][0]) if labels[p][1] == "source" else (rel if labels[p][0] else 1 - rel)
base = [(features(*k.split("+")), v) for k, v in VOTES.items()]
extra_voted = {p for p in labels if p in VOTES}
order = test[:]; random.Random(7).shuffle(order)
pred = {}
for k in range(5):
    held = set(order[k::5])
    rows = [(x, (v * 3 + soft(p)) / 4) if p in extra_voted else (x, v) for (x, v), p in zip(base, VOTES)]
    rows += [(features(*p.split("+")), soft(p)) for p in test if p not in held]
    w = fit(rows)
    for p in held:
        pred[p] = prob(w, features(*p.split("+")))
b1, a1 = scores(pred)
print(f"3. after: Brier {b1:.3f}, the 50% line matches on {100 * a1:.0f}%  |  change: Brier {100 * (b1 - b0) / b0:+.0f}%, match {100 * (a1 - a0):+.0f} points")

# 4. does training on the new labels cost anything on the three readers' votes? (five folds over the votes, as cv.py)
items = sorted(VOTES.items()); random.Random(7).shuffle(items)
def votes_cv(with_new):
    out = []
    for k in range(5):
        held = {p for p, _ in items[k::5]}
        rows = [(features(*p.split("+")), v) for p, v in items if p not in held]
        if with_new:
            rows += [(features(*p.split("+")), soft(p)) for p in labels if p not in VOTES]
        w = fit(rows)
        out += [(prob(w, features(*p.split("+"))), v) for p, v in items if p in held]
    return sum((a - b) ** 2 for a, b in out) / len(out)
v0, v1 = votes_cv(False), votes_cv(True)
print(f"4. on the readers' votes, held out: Brier {v0:.4f} without the new labels, {v1:.4f} with them ({100 * (v1 - v0) / v0:+.0f}%)")
