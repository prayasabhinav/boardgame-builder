"""Check that no combination of blocks goes without feedback. Run after editing the knowledge base: python check.py

1. Every possible two-block canvas gets at least one sentence from the knowledge base (a pair, triad or theme line).
   Larger canvases always contain such a pair, so this covers them too.
2. Every feeling, picked with any two-block canvas, is said: supported, pulled away from, or neither.
3. Every known game's design uses real blocks (a list only where the group takes several), and every marked question's answer is one of its options, and every game says who made it and what it shows a designer.
4. VERSION, the newest entry in CHANGELOG.md and the version badge in README.md agree.
Exits 1 and names the first gaps if any fails.

check-log.txt keeps one line per pass: when, and a fingerprint of everything the checks read (every .py and .json file here but
review.json, which carries the day's date and is not checked; VERSION, CHANGELOG.md, README.md). If nothing has changed since the last pass, the checks are not run again (his words,
6 November 2026: "mantain a check log - if no change is made, iot does not need to be checked again"). --again runs them anyway.
"""
import datetime, glob, hashlib, itertools, re, sys

INPUTS = sorted(f for f in glob.glob("*.py") + glob.glob("*.json") if f != "review.json") + ["VERSION", "CHANGELOG.md", "README.md"]
digest = hashlib.sha256(b"".join(f.encode() + open(f, "rb").read() for f in INPUTS)).hexdigest()[:16]
try:
    last = open("check-log.txt", encoding="utf-8").read().splitlines()[-1]
except (FileNotFoundError, IndexError):
    last = ""
if last.split(" | ")[1:2] == [digest] and "--again" not in sys.argv:
    print(f"nothing has changed since the pass on {last.split(' | ')[0]} (fingerprint {digest}); not checked again")
    sys.exit(0)

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
        service = rules._compute_intent_service(set(mech), {f}, app.KB["feeling_blocks"])   # what match_kb gives as feeling_service
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
    if not g["credits"].get("by") or not g.get("lesson"):
        bad_games.append((g["id"], "credits"))
print(f"known games: {len(app.GAMES)} | with a bad block or answer: {len(bad_games)}")
newest = re.search(r"^## (\S+)", open("CHANGELOG.md", encoding="utf-8").read(), re.M).group(1)
badge = f"version-{app.VERSION}-" in open("README.md", encoding="utf-8").read()
version_ok = newest == app.VERSION and badge
print(f"version {app.VERSION} | newest changelog entry {newest} | README badge {'matches' if badge else 'missing or different'}")
if no_text or silent or bad_games or not version_ok:
    print("first gaps:", no_text[:5], silent[:5], bad_games[:5])
    sys.exit(1)
with open("check-log.txt", "a", encoding="utf-8") as log:
    log.write(f"{datetime.datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %z')} | {digest} | passed: {len(canvases)} canvases, {len(canvases) * len(feelings)} feeling cases, {len(app.GAMES)} games, version {app.VERSION}\n")
