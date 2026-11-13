"""Builds interactions-books.json from the knowledge-base lines taken from books, one file per book in kb-books/.

A file is named <book>.<chunk>.txt; the book's full reference and the short form the feedback cites come from
sources.tsv (settled through Consensus, find-research-papers and Crossref, then library catalogues, 6 November 2026).
Each line is one entry:
    pair: block+block | what tends to happen | pro | pro | con | con | page   (a pro or con the book does not state is '-')
    conflict: block+block | the sentence a student reads | page
Every sentence says what tends to happen, in our own words, and the page is where the book says it.
Nothing here is reviewed; curated entries come first, then these, then the drafted ones.
Usage: python kb-books/build.py
"""
import glob, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from palette import DIMENSIONS

BANNED = re.compile(r"\b(should|must|good|bad|better|worse|best|worst|great|well done|amazing|perfect|excellent|awesome)\b", re.I)
BLOCKS = {b["id"] for d in DIMENSIONS for b in d["blocks"]}
STATUS = "book-20261106-unreviewed"
HERE = os.path.dirname(os.path.abspath(__file__))
SOURCES = {r[0]: {"source": r[1], "short": r[2]} for r in (l.rstrip("\n").split("\t") for l in list(open(os.path.join(HERE, "sources.tsv"), encoding="utf-8"))[1:])}
pairs, conflicts, problems = [], [], []
for path in sorted(glob.glob(os.path.join(HERE, "*.txt"))):
    name = os.path.basename(path)
    lines = [l.strip() for l in open(path, encoding="utf-8")]
    head = SOURCES.get(name.split(".")[0])
    if not head:
        problems.append(f"{name}: no line for this book in sources.tsv"); continue
    for n, line in enumerate(lines, 1):
        if not line or line.startswith(("source:", "short:")):
            continue
        kind, _, rest = line.partition(": ")
        cells = [c.strip() for c in rest.split("|")]
        cells[-1] = re.sub(r"(\d)-(\d)", r"\1–\2", cells[-1])   # a hyphen in a page range becomes an en dash
        where = f"{name}:{n}"
        elements = cells[0].split("+")
        if kind not in ("pair", "conflict") or len(cells) != (7 if kind == "pair" else 3):
            problems.append(f"{where}: expected 'pair:' with 7 cells or 'conflict:' with 3"); continue
        if len(elements) != 2 or any(e not in BLOCKS for e in elements):
            problems.append(f"{where}: {cells[0]} is not two blocks"); continue
        if not re.fullmatch(r"pp?\. ([ivxlc]+|\d+)(–\d+)?(, \d+)*|under '.+'", cells[-1]):
            problems.append(f"{where}: the page should read like 'p. 87', 'pp. 87–89' or, for a book without pages, under 'Whist'"); continue
        for word in {m.lower() for c in cells[1:-1] for m in BANNED.findall(c)}:
            problems.append(f"{where}: banned word '{word}'")
        source = {"ref": head["source"], "short": head["short"], "page": cells[-1]}
        if kind == "pair":
            # a pro or con the book gives no ground for is written "-" and left out (13 November 2026: books are the authority)
            pairs.append({"elements": elements, "tendency": cells[1], "pros": [c for c in cells[2:4] if c != "-"], "cons": [c for c in cells[4:6] if c != "-"], "exemplars": [],
                          "source": source, "verification_status": STATUS})
        else:
            conflicts.append({"elements": elements, "note": cells[1], "student_note": cells[1], "source": source, "verification_status": STATUS})
# A pair that a known game puts together is not a conflict: the known games show what goes together (Prayas, 6 November 2026)
from known_games import from_markdown
designs = [g["design"] for g in json.load(open("games.json"))] + [from_markdown(open(f).read())[0]["design"] for f in glob.glob("known-games-new/*.md")]
together = [{b for v in d.values() for b in (v if isinstance(v, list) else [v])} for d in designs]
kept = []
for c in conflicts:
    if any(set(c["elements"]) <= t for t in together):
        print(f"not a conflict, a known game has both: {'+'.join(c['elements'])} ({c['source']['short']}, {c['source']['page']})")
    else:
        kept.append(c)
conflicts = kept
for p in problems:
    print("PROBLEM", p)
if problems:
    sys.exit(1)
json.dump({"description": "Pair and conflict entries taken from books on 6 November 2026, each with its book and page. Not reviewed.",
           "pairs": pairs, "conflicts": conflicts}, open("interactions-books.json", "w"), indent=2, ensure_ascii=False)
print(f"wrote interactions-books.json: {len(pairs)} pairs, {len(conflicts)} conflicts")
