"""Blind keying sheets for the needs-review model, and reading his keys back.

The pairs are a core mechanic and a block from another slot that no known game puts together. A sheet lists them in a random order,
numbered, with no model's mark. After each pair he writes r (needs review), f (fine) or ? (don't know), and fills 1:, 2:, 3: for the
components he defines in components.md. Read back, the keys go into keys.jsonl, the latest key for a pair winning.

usage:
  python review-model/sheet.py --sheet <name> [rows per core mechanic, default 8] [rows in all]   writes review-model/<name>-keys.txt
  python review-model/sheet.py --read <name> [who keyed, default Prayas]            reads the keys into review-model/keys.jsonl
"""
import datetime, glob, json, os, random, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palette import DIMENSIONS
from known_games import from_markdown

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = os.path.join(HERE, "keys.jsonl")
NAME = {b["id"]: b["display"] for d in DIMENSIONS for b in d["blocks"]}
SLOT = {b["id"]: d["display"] for d in DIMENSIONS for b in d["blocks"]}


def seen_pairs():
    """Core mechanic and partner block pairs that a known game puts together."""
    designs = [g["design"] for g in json.load(open("games.json"))] + [from_markdown(open(p).read())[0]["design"] for p in glob.glob("known-games-new/*.md")]
    return {(c, b) for d in designs for c in d.get("core-mechanic", []) for k, v in d.items() if k != "core-mechanic" for b in (v if isinstance(v, list) else [v])}


def keyed():
    """The latest key for each pair, with who keyed it."""
    return {(r["core"], r["block"]): (r["key"], r.get("by", "Prayas")) for r in map(json.loads, open(KEYS))} if os.path.exists(KEYS) else {}


if __name__ == "__main__" and sys.argv[1] == "--sheet":
    names = re.findall(r"^\d\. name:(.*)$", open(os.path.join(HERE, "components.md")).read(), re.M)
    if len(names) != 3 or not all(n.strip() for n in names):
        sys.exit("components.md names fewer than three components: the definitions are his, and a sheet waits for them")
    per = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    seen, done = seen_pairs(), keyed()
    rows = []
    for c in [b["id"] for b in DIMENSIONS[0]["blocks"]]:
        open_pairs = [(c, b["id"]) for d in DIMENSIONS[1:] for b in d["blocks"] if (c, b["id"]) not in seen and (c, b["id"]) not in done]
        rows += random.sample(open_pairs, min(per, len(open_pairs)))
    random.shuffle(rows)
    rows = rows[:int(sys.argv[4])] if len(sys.argv) > 4 else rows
    out = [f"# {sys.argv[2]}: {len(rows)} pairs no known game shows. After each, write r (needs review), f (fine) or ? (don't know), then fill 1:, 2:, 3:.", "1: " + names[0].strip() + ", 2: " + names[1].strip() + ", 3: " + names[2].strip() + " (components.md)", ""]
    for n, (c, b) in enumerate(rows, 1):
        out += [f"{n}. {NAME[c]} + {NAME[b]} ({SLOT[b]}) | {c}+{b} | key:", "   1:", "   2:", "   3:", ""]
    open(os.path.join(HERE, f"{sys.argv[2]}-keys.txt"), "w").write("\n".join(out))
    print(f"wrote review-model/{sys.argv[2]}-keys.txt: {len(rows)} pairs")
elif __name__ == "__main__" and sys.argv[1] == "--read":
    text = open(os.path.join(HERE, f"{sys.argv[2]}-keys.txt")).read()
    got = 0
    with open(KEYS, "a") as f:
        for block in re.split(r"\n(?=\d+\. )", text):
            m = re.match(r"\d+\. .*\| (\S+)\+(\S+) \| key:\s*([rf?])", block)
            if m:
                parts = dict(re.findall(r"^\s*([123]):(.*)$", block, re.M))
                f.write(json.dumps({"core": m[1], "block": m[2], "key": m[3], "components": {k: v.strip() for k, v in parts.items()},
                                    "sheet": sys.argv[2], "by": sys.argv[3] if len(sys.argv) > 3 else "Prayas", "date": datetime.date.today().isoformat()}) + "\n")
                got += 1
    print(f"read {got} keys into review-model/keys.jsonl")
