"""Writes review-model/labels.json for train.mjs: every core-mechanic pair with its label and where the label came from.

0 (fine): a known game puts the two together. 1 (needs review): a book's cited conflict names them, with no known game against it.
Keys in keys.jsonl override both: r is 1, f is 0, ? is left out. Each says who keyed it: Prayas, or the pattern read he chose on
6 November 2026 in place of keying ("Use the read of the patterns that emerges - not possible fore to key"),
for this model and this case only, not as a rule. Every other pair has no label, and train.mjs predicts it.
Usage: python3 review-model/labels.py
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sheet import seen_pairs, keyed, DIMENSIONS

core = [b["id"] for b in DIMENSIONS[0]["blocks"]]
labels = {f"{c}+{b}": {"label": 0, "from": "a known game has both"} for c, b in seen_pairs()}
for c in json.load(open("interactions-books.json"))["conflicts"]:
    a, b = c["elements"]
    if a in core or b in core:
        c0, b0 = (a, b) if a in core else (b, a)
        labels[f"{c0}+{b0}"] = {"label": 1, "from": f"conflict in {c['source']['short']}, {c['source']['page']}"}
for (c, b), (k, by) in keyed().items():
    if k == "?":
        labels.pop(f"{c}+{b}", None)
    else:
        labels[f"{c}+{b}"] = {"label": 1 if k == "r" else 0, "from": "his key" if by == "Prayas" else f"key by {by}"}
pairs = [f"{c}+{b['id']}" for c in core for d in DIMENSIONS[1:] for b in d["blocks"]]
json.dump({"pairs": pairs, "labels": labels}, open("review-model/labels.json", "w"), indent=1)
print(f"labels: {sum(v['label'] == 0 for v in labels.values())} fine, {sum(v['label'] == 1 for v in labels.values())} needs review, {len(pairs) - len(labels)} to predict")
