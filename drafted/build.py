"""Build interactions-drafted.json from the drafted/*.txt files and check them.

Each line of a pairs file: a+b | tendency | pro | pro | con | con
Each line of themes.txt:   theme-id | sentence
Run from the tool folder: python drafted/build.py   (exits 1 and says why if a check fails)
"""
import itertools, json, pathlib, re, sys

sys.path.insert(0, ".")
import palette

STATUS = "drafted-20261016-unreviewed"
BANNED = re.compile(r"\b(should|must|good|bad|better|worse|best|worst|great|well done|amazing|perfect|excellent|awesome)\b", re.I)

dim = {b["id"]: d["id"] for d in palette.DIMENSIONS for b in d["blocks"]}
stacks = {d["id"] for d in palette.DIMENSIONS if d.get("multi")}
curated = {frozenset(p["elements"]) for p in json.load(open("interactions.json"))["pairs"]}
wanted = {frozenset(p) for p in itertools.combinations([b for b in dim if dim[b] != "theme"], 2)
          if (dim[p[0]] != dim[p[1]] or dim[p[0]] in stacks)} - curated

problems, pairs, seen = [], [], set()
for f in sorted(pathlib.Path("drafted").glob("[0-9]*.txt")):
    for n, line in enumerate(f.read_text().splitlines(), 1):
        if not line.strip():
            continue
        cells = [c.strip() for c in line.split("|")]
        where = f"{f.name}:{n}"
        if len(cells) != 6:
            problems.append(f"{where}: {len(cells)} cells, expected 6"); continue
        key = frozenset(cells[0].split("+"))
        if key not in wanted:
            problems.append(f"{where}: {cells[0]} is not a missing pair"); continue
        if key in seen:
            problems.append(f"{where}: {cells[0]} written twice"); continue
        seen.add(key)
        for word in {m.lower() for c in cells[1:] for m in BANNED.findall(c)}:
            problems.append(f"{where}: banned word '{word}'")
        pairs.append({"elements": cells[0].split("+"), "tendency": cells[1], "pros": cells[2:4], "cons": cells[4:6],
                      "exemplars": [], "verification_status": STATUS})

themes = []
tf = pathlib.Path("drafted/themes.txt")
if tf.exists():
    for n, line in enumerate(tf.read_text().splitlines(), 1):
        if line.strip():
            tid, sentence = [c.strip() for c in line.split("|")]
            if dim.get(tid) != "theme":
                problems.append(f"themes.txt:{n}: {tid} is not a theme")
            for word in {m.lower() for m in BANNED.findall(sentence)}:
                problems.append(f"themes.txt:{n}: banned word '{word}'")
            themes.append({"theme": tid, "line": sentence, "verification_status": STATUS})

# feelings.txt: feeling | + blocks it supports | - blocks it works against; every other block is judged neither
feeling_links = {}
curated_feelings = {f["feeling"]: f for f in json.load(open("interactions.json"))["feeling_blocks"]}
ff = pathlib.Path("drafted/feelings.txt")
for n, line in enumerate(ff.read_text().splitlines(), 1):
    if not line.strip():
        continue
    name, plus, minus = [c.strip() for c in line.split("|")]
    where = f"feelings.txt:{n}"
    if name not in curated_feelings:
        problems.append(f"{where}: {name} is not a feeling"); continue
    add_s = [b.strip() for b in plus.lstrip("+").split(",") if b.strip()]
    add_o = [b.strip() for b in minus.lstrip("-").split(",") if b.strip()]
    cur = curated_feelings[name]
    for b in add_s + add_o:
        if b not in dim:
            problems.append(f"{where}: {b} is not a block")
    for b in set(add_s) & set(add_o):
        problems.append(f"{where}: {b} is on both sides")
    for b in add_s:
        if b in cur["opposed_by"]:
            problems.append(f"{where}: {b} contradicts the curated entry, which says it works against {name}")
        if b in cur["supported_by"]:
            problems.append(f"{where}: {b} already supports {name} in the curated entry")
    for b in add_o:
        if b in cur["supported_by"]:
            problems.append(f"{where}: {b} contradicts the curated entry, which says it supports {name}")
        if b in cur["opposed_by"]:
            problems.append(f"{where}: {b} already works against {name} in the curated entry")
    judged = set(cur["supported_by"]) | set(cur["opposed_by"]) | set(add_s) | set(add_o)
    feeling_links[name] = {"supported_by": add_s, "opposed_by": add_o,
                           "neither": sorted(b for b in dim if b not in judged), "verification_status": STATUS}
for name in set(curated_feelings) - set(feeling_links):
    problems.append(f"feelings.txt: no line for {name}")

missing = wanted - seen
print(f"pairs written: {len(seen)} of {len(wanted)} | themes: {len(themes)} of {sum(v == 'theme' for v in dim.values())} | feelings: {len(feeling_links)} of {len(curated_feelings)}")
if missing:
    print(f"still missing ({len(missing)}): " + " ".join(sorted("+".join(sorted(m)) for m in missing))[:2000])
for p in problems:
    print("PROBLEM", p)
if problems:
    sys.exit(1)
json.dump({"description": "Pair entries, theme lines and feeling links drafted on 16 October 2026 so every combination of blocks gets feedback. "
                          "Not reviewed; no example games, since none were checked. The curated entries in interactions.json come first.",
           "pairs": pairs, "themes": themes, "feeling_links": feeling_links}, open("interactions-drafted.json", "w"), indent=2, ensure_ascii=False)
print("wrote interactions-drafted.json")
