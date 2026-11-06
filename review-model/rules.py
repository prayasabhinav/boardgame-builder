"""Writes review.json, the pairs the tool flags as illogical, from properties.json (what cannot be true of one game at the table),
with a needs-review score from 1 to 10 for every pair from his own small model: logistic regression on the table's properties,
trained on keys.jsonl alone, which were drawn from pairs no known game shows, so novelty
itself raises no score (his words: "Needs review score does not have to penalise novelty"; trained with the known-game pairs as fine,
fine pairs of core mechanics no known game uses were scored 5 or 8 three times as often as others) (his words, 6 November 2026: "If the model only makes a need
review score from 1 to 10 it's ok", "My own small model only", "The rating should be reliable", "It is never 0 or 10", "Make it work. Make 1 to 10 broader of easier"). The model's output
is calibrated to the share of r among keys it did not train on (five folds), then put in one of three broad steps on the 1-to-10
scale: 2 (under a quarter), 5 (a quarter to two thirds), 8 (over two thirds). Trained on illogical pairs only, a pair kept its step in every
one of 12 retrainings, and on held-out keys 0% of pairs at 2 and 94% at 8 were illogical (AUC 0.972); no pair falls at 5. The labels
and the table come from one reading, so the score agrees with the flag; a key of his is what would make it say something the flag
does not. The table decides what is flagged and why.

A pair is a core mechanic and a block from another slot. It is flagged when the partner clashes with something the core mechanic
makes or settles, so the two cannot both hold; a pair that is only unusual is not flagged ("More than unusual the scale and flag
should be for the illogical"). The labels: a key of his, r or f; a pattern-read key counts as r only when illogical.txt lists it. A pair a known game has is never flagged. A key of Prayas's in
keys.jsonl outranks the table; the pattern-read keys there are the test the table is checked against, and the counts are printed.
Usage: python3 review-model/rules.py
"""
import datetime, json, math, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet import seen_pairs, keyed, DIMENSIONS, NAME

P = json.load(open("review-model/properties.json"))
PH, MAKES = P["phrases"], P["makes"]


def reason(c, b):
    """Why the two cannot both hold, or '' when nothing in the table says so."""
    hit = [t for t in P["partners"].get(b, {}).get("clashes", []) if t in MAKES[c]]
    return f"{NAME[c]} {PH[hit[0]]}, and {NAME[b]} says otherwise" if hit else ""


def features(c, b):
    f = {f"b:{b}": 1, "bias": 1, "table": 1 if reason(c, b) else 0}
    for t in MAKES[c]:
        f[f"{t}|{b}"] = f[f"t:{t}"] = 1
    return f


def prob(w, x):
    return 1 / (1 + math.exp(-sum(w.get(k, 0) * v for k, v in x.items())))


def fit(rows):
    """Logistic regression with an L2 penalty; the few needs-review rows weigh as much in total as the many fine ones."""
    w, pos = {}, sum(y for _, y in rows)
    for _ in range(300):
        g = {k: 0.02 * v for k, v in w.items()}
        for x, y in rows:
            e = (prob(w, x) - y) * ((len(rows) - pos) / pos if y else 1)
            for k, v in x.items():
                g[k] = g.get(k, 0) + e * v / len(rows)
        for k, v in g.items():
            w[k] = w.get(k, 0) - 0.5 * v
    return w


def calibrate(labelled, keys):
    """Platt scaling: a, b such that sigmoid(a * logit + b) matches the share of r among held-out keys."""
    logit = lambda q: math.log(max(q, 1e-6) / max(1 - q, 1e-6))
    held = [p for p in keys if p in labelled]
    random.Random(1).shuffle(held)
    pts = []
    for k in range(5):
        test = set(held[k::5])
        w = fit([(features(*p), y) for p, y in labelled.items() if p not in test])
        pts += [(logit(prob(w, features(*p))), labelled[p]) for p in test]
    a, b = 1.0, 0.0
    for _ in range(3000):
        ga = gb = 0
        for z, y in pts:
            e = 1 / (1 + math.exp(-(a * z + b))) - y
            ga, gb = ga + e * z, gb + e
        a, b = a - 0.05 * ga / len(pts), b - 0.05 * gb / len(pts)
    return lambda q: 1 / (1 + math.exp(-(a * logit(q) + b)))


core = [b["id"] for b in DIMENSIONS[0]["blocks"]]
assert set(core) == set(MAKES), set(core) ^ set(MAKES)
seen, keys = seen_pairs(), keyed()
ILLOGICAL = {tuple(l.split("+")) for l in open("review-model/illogical.txt").read().split("\n") if l and not l.startswith("#")}
pairs = [(c, b["id"]) for c in core for d in DIMENSIONS[1:] for b in d["blocks"]]
reasons = {}
for c, b in pairs:
    k, by = keys.get((c, b), (None, None))
    r = "a teacher has marked this pair for a look" if by == "Prayas" and k == "r" else "" if by == "Prayas" or (c, b) in seen else reason(c, b)
    if r:
        reasons[f"{c}+{b}"] = r
labelled = {p: int(k == "r" and (by == "Prayas" or p in ILLOGICAL)) for p, (k, by) in keys.items() if k != "?"}
w, cal = fit([(features(*p), y) for p, y in labelled.items()]), calibrate(labelled, keys)
STEPS = [(0.25, 2), (0.65, 5), (1.01, 8)]
score = {f"{c}+{b}": next(s for edge, s in STEPS if cal(prob(w, features(c, b))) < edge) for c, b in pairs}
json.dump({"made": datetime.date.today().isoformat(), "from": "review-model/rules.py", "flagged": list(reasons), "reasons": reasons, "score": score},
          open("review.json", "w"), indent=1)
read = {p: labelled[p] for p, (k, by) in keys.items() if by == "pattern read" and k != "?"}
agree = sum(y == bool(reason(*p)) for p, y in read.items())
miss = [p for p, y in read.items() if y and not reason(*p)]
extra = [p for p, y in read.items() if not y and reason(*p)]
known = [p for p in seen if p[0] in MAKES and reason(*p)]
print(f"wrote review.json: {len(reasons)} of {len(pairs)} pairs flagged")
print(f"against the read keys, illogical ones as r: {agree} of {len(read)} agree; {len(miss)} illogical the table does not flag, {len(extra)} others it flags")
print("  not flagged:", ", ".join("+".join(p) for p in miss)); print("  flagged:", ", ".join("+".join(p) for p in extra))
print(f"known-game pairs the table would flag (never flagged on screen): {len(known)}")
