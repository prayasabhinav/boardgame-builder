"""Check that no combination of blocks goes without feedback. Run after editing the knowledge base: python check.py

1. Every possible two-block canvas gets at least one sentence from the knowledge base (a pair, triad or theme line).
   Larger canvases always contain such a pair, so this covers them too.
2. Every feeling, picked with any two-block canvas, is said: supported, pulled away from, or neither.
3. Every known game's design uses real blocks (a list only where the group takes several), and every marked question's answer is one of its options, and every game says who made it.
4. VERSION, the newest entry in CHANGELOG.md and the version badge in README.md agree.
Exits 1 and names the first gaps if any fails.
"""
import itertools, re, sys

import app, palette, rules, templates

dim = {b["id"]: d["id"] for d in palette.DIMENSIONS for b in d["blocks"]}
stacks = {d["id"] for d in palette.DIMENSIONS if d.get("multi")}
canvases = [list(p) for p in itertools.combinations(dim, 2) if dim[p[0]] != dim[p[1]] or dim[p[0]] in stacks]
feelings = [f["feeling"] for f in app.KB["feeling_blocks"]]
empty = {"mechanics": [], "feelings": []}

no_text, silent = [], []
for mech in canvases:
    canvas = {"mechanics": mech, "feelings": []}
    out = templates.build_template_output(rules.match_kb(canvas, app.KB), canvas, rules.compute_diff(canvas, empty))
    if out["mode"] != "full" or not (out["triads"] or out["pairs"] or out["themes"]):
        no_text.append(mech)
    for f in feelings:
        service = rules.match_kb({"mechanics": mech, "feelings": [f]}, app.KB)["feeling_service"]
        if not templates.template_feeling_service(service):
            silent.append((f, mech))

print(f"two-block canvases: {len(canvases)} | without knowledge-base text: {len(no_text)}")
print(f"feeling with two-block canvas: {len(canvases) * len(feelings)} | feeling not said: {len(silent)}")
bad_games = []
for g in app.GAMES:
    for d, picked in g["design"].items():
        if any(dim.get(b) != d for b in (picked if isinstance(picked, list) else [picked])) or isinstance(picked, list) != (d in stacks):
            bad_games.append((g["id"], d))
    bad_games += [(g["id"], q["id"]) for q in g["questions"] if q["answer"] is not None and not 0 <= q["answer"] < len(q["options"])]
    if not g["credits"].get("by"):
        bad_games.append((g["id"], "credits"))
print(f"known games: {len(app.GAMES)} | with a bad block or answer: {len(bad_games)}")
newest = re.search(r"^## (\S+)", open("CHANGELOG.md", encoding="utf-8").read(), re.M).group(1)
badge = f"version-{app.VERSION}-" in open("README.md", encoding="utf-8").read()
version_ok = newest == app.VERSION and badge
print(f"version {app.VERSION} | newest changelog entry {newest} | README badge {'matches' if badge else 'missing or different'}")
if no_text or silent or bad_games or not version_ok:
    print("first gaps:", no_text[:5], silent[:5], bad_games[:5])
    sys.exit(1)
