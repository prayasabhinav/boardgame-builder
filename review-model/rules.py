"""Writes review.json, the pairs the tool flags as illogical, from properties.json (what cannot be true of one game at the table),
and for every pair a probability that the two blocks clash, from his own small model.

A pair is a core mechanic and a block from another slot. It is flagged when the partner clashes with something the core mechanic
makes or settles, so the two cannot both hold; a pair that is only unusual is not flagged ("More than unusual the scale and flag
should be for the illogical"). A pair a known game has is never flagged, and a key of Prayas's in keys.jsonl outranks the table.

The probability (his words, 6 November 2026: "My own small model only", "so if the model says 2 and 8 its not a score, it is
boolean", "I was hoping a probility of illogical rtather than black and white"): logistic regression on the table's properties,
trained on clash-votes.jsonl, where three independent readers asked of each of 720 sampled pairs whether both blocks can be true
of the same game, and a pair's label is the share who said no (unsure counts half). His own keys outrank the readers (r 1, f 0).
Measured on held-out pairs before it went in: Brier 0.0116, correlation 0.80 with the readers' share; pairs it put near 85% were
said no by 81% of readers, near 1% by 1%. Usage: python3 review-model/rules.py
"""
import datetime, json, math, os, sys
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
    """Logistic regression on soft labels (a share between 0 and 1), with a light L2 penalty."""
    w = {}
    for _ in range(3000):
        g = {k: 0.0005 * v for k, v in w.items()}
        for x, y in rows:
            e = prob(w, x) - y
            for k, v in x.items():
                g[k] = g.get(k, 0) + e * v / len(rows)
        for k, v in g.items():
            w[k] = w.get(k, 0) - v
    return w


core = [b["id"] for b in DIMENSIONS[0]["blocks"]]
assert set(core) == set(MAKES), set(core) ^ set(MAKES)
seen, keys = seen_pairs(), keyed()
VOTES = {tuple(r["pair"].split("+")): r["share_no"] for r in map(json.loads, open("review-model/clash-votes.jsonl"))}
pairs = [(c, b["id"]) for c in core for d in DIMENSIONS[1:] if d["id"] != "kind-of-fun" for b in d["blocks"]]   # khatka reads what can be true of one game at the table; a kind of fun is not that
reasons = {}
for c, b in pairs:
    k, by = keys.get((c, b), (None, None))
    r = "a teacher has marked this pair for a look" if by == "Prayas" and k == "r" else "" if by == "Prayas" or (c, b) in seen else reason(c, b)
    if r:
        reasons[f"{c}+{b}"] = r
# Labels on the pairs khatka was unsure of (13 November 2026, his words: "parse and interpret more from the papers and books.
# Label more"): one reader per pair searched the books and papers (source-labels-*.jsonl). A label resting on a source whose
# copied words code found (source-labels-checked.json) is settled and outranks the readers' votes; one resting on inference
# counts for a pair nobody voted on, weighted by how often one reader agreed with the three readers' majority. Measured
# before they went in (label-eval.py, held out): on the voted pairs Brier 0.0111 without them, 0.0098 with them.
FOUND = json.load(open("review-model/source-labels-checked.json"))
NEW = {tuple(r["pair"].split("+")): (int(r["label"] == "clashes"), bool(FOUND.get(r["pair"])))
       for f in sorted(__import__("glob").glob("review-model/source-labels-*.jsonl")) for r in map(json.loads, open(f)) if r["label"] in ("holds", "clashes")}
both = [p for p in NEW if p in VOTES and VOTES[p] != 0.5]
REL = sum(NEW[p][0] == (VOTES[p] > 0.5) for p in both) / len(both)
NEW_LABELS = {p: float(y) for p, (y, src) in NEW.items() if src} | {p: (REL if y else 1 - REL) for p, (y, src) in NEW.items() if not src and p not in VOTES}
labelled = VOTES | NEW_LABELS | {p: int(k == "r") for p, (k, by) in keys.items() if by == "Prayas" and k != "?"}
w = fit([(features(*p), y) for p, y in labelled.items()])
p_clash = {f"{c}+{b}": round(prob(w, features(c, b)), 3) for c, b in pairs}
json.dump({"made": datetime.date.today().isoformat(), "from": "review-model/rules.py", "flagged": list(reasons), "reasons": reasons, "p_clash": p_clash},
          open("review.json", "w"), indent=1)
agree = sum((y >= 0.5) == bool(reason(*p)) for p, y in VOTES.items())
known = [p for p in seen if p[0] in MAKES and reason(*p)]
print(f"wrote review.json: {len(reasons)} of {len(pairs)} pairs flagged; trained on {len(VOTES)} voted pairs and {len(NEW_LABELS)} new labels (one reader agreed with the three on {100 * REL:.0f}%)")
print(f"against the readers: {agree} of {len(VOTES)} pairs where the table flags exactly those most readers said no to")
print("flagged pairs by probability:", sorted(__import__("collections").Counter(round(p_clash[k], 1) for k in reasons).items()))
print(f"known-game pairs the table would flag (never flagged on screen): {len(known)}")
