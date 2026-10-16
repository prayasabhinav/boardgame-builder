"""Check that no combination of blocks goes without feedback. Run after editing the knowledge base: python check.py

1. Every possible two-block canvas gets at least one sentence from the knowledge base (a pair, triad or theme line).
   Larger canvases always contain such a pair, so this covers them too.
2. Every feeling, picked with any two-block canvas, is said: supported, pulled away from, or neither.
Exits 1 and names the first gaps if either fails.
"""
import itertools, sys

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
if no_text or silent:
    print("first gaps:", no_text[:5], silent[:5])
    sys.exit(1)
