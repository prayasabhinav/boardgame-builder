"""Five-fold held-out check of khatka (the clash model) on the three readers' votes, without writing review.json. Usage (from boardgame-builder): python3 review-model/cv.py [extra-fine-pairs.json]"""
import json, random, sys
src = open("review-model/rules.py").read().split("json.dump(")[0]          # everything before review.json is written
src = src.replace("labelled = VOTES", "EXTRA = json.load(open(sys.argv[1])) if len(sys.argv) > 1 else []\nlabelled = VOTES")
ns = {"__file__": "review-model/rules.py", "__name__": "cv"}; exec(compile(src, "rules", "exec"), ns)
VOTES, fit, prob, features = ns["VOTES"], ns["fit"], ns["prob"], ns["features"]
extra = {tuple(p): 0.0 for p in ns["EXTRA"]}
items = sorted(VOTES.items()); random.Random(7).shuffle(items)
pred = []
for k in range(5):
    test = items[k::5]; held = {p for p, _ in test}
    train = [(features(*p), y) for p, y in items if p not in held] + [(features(*p), y) for p, y in extra.items() if p not in held and p not in VOTES]
    train += [(features(*p), y) for p, y in ns.get("NEW_LABELS", {}).items() if p not in held and p not in VOTES]   # the labels rules.py trains on
    w = fit(train)
    pred += [(prob(w, features(*p)), y) for p, y in test]
brier = sum((p - y) ** 2 for p, y in pred) / len(pred)
mp, my = sum(p for p, _ in pred) / len(pred), sum(y for _, y in pred) / len(pred)
cov = sum((p - mp) * (y - my) for p, y in pred); vp = sum((p - mp) ** 2 for p, _ in pred) ** .5; vy = sum((y - my) ** 2 for _, y in pred) ** .5
print(f"held out over {len(pred)} voted pairs: Brier {brier:.4f}, correlation {cov / (vp * vy):.3f}; extra fine pairs used {len(extra)}; new labels trained on {len(ns.get('NEW_LABELS', {}))}")
