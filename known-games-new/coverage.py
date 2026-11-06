"""How many core-mechanic pairs the known games show: games.json plus every proposed game file in this folder.
A pair is a core mechanic and a block from another slot placed in the same game. Usage: python known-games-new/coverage.py"""
import glob, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palette import DIMENSIONS
from known_games import from_markdown

here = os.path.dirname(os.path.abspath(__file__))
designs = [g["design"] for g in json.load(open(os.path.join(here, "..", "games.json")))]
for path in sorted(glob.glob(os.path.join(here, "*.md"))):
    game, problem = from_markdown(open(path).read())
    if problem:
        sys.exit(f"{os.path.basename(path)}: {problem}")
    designs.append(game["design"])

core = [b["id"] for d in DIMENSIONS if d["id"] == "core-mechanic" for b in d["blocks"]]
other = [b["id"] for d in DIMENSIONS if d["id"] != "core-mechanic" for b in d["blocks"]]
seen = set()
for d in designs:
    rest = {b for k, v in d.items() if k != "core-mechanic" for b in (v if isinstance(v, list) else [v])}
    seen |= {(c, b) for c in d.get("core-mechanic", []) for b in rest}
for c in core:
    print(f"{c:22} {sum(1 for p in seen if p[0] == c):2}/{len(other)}")
print(f"games {len(designs)}  pairs {len(seen)}/{len(core) * len(other)} = {100 * len(seen) / (len(core) * len(other)):.0f}%")
