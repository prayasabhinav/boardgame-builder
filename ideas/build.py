"""Builds ideas.json, the Ideas tab's glossary and key ideas, from one file per book in ideas/.

Each line is one entry:
    term: word or phrase | what it means | p. 87
    idea: a short name | what the book argues or shows, with an example from it | p. 87
in our own words, citing the printed page (or, for a book without pages, under 'Whist'). The book's reference comes
from kb-books/sources.tsv. Usage: python ideas/build.py
"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BANNED = re.compile(r"\b(should|must|good|bad|better|worse|best|worst|great|well done|amazing|perfect|excellent|awesome)\b", re.I)
SOURCES = {r[0]: {"ref": r[1], "short": r[2]} for r in (l.rstrip("\n").split("\t") for l in list(open(os.path.join(HERE, "..", "kb-books", "sources.tsv"), encoding="utf-8"))[1:])}
terms, ideas, problems = [], [], []
for path in sorted(glob.glob(os.path.join(HERE, "*.txt"))):
    name = os.path.basename(path)
    book = SOURCES.get(name.split(".")[0])
    if not book:
        problems.append(f"{name}: no line for this book in kb-books/sources.tsv"); continue
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        kind, _, rest = line.strip().partition(": ")
        if not line.strip():
            continue
        cells = [c.strip() for c in rest.split("|")]
        where = f"{name}:{n}"
        if kind not in ("term", "idea") or len(cells) != 3:
            problems.append(f"{where}: expected 'term:' or 'idea:' with three cells"); continue
        page = re.sub(r"(\d)-(\d)", r"\1–\2", cells[2])
        if not re.fullmatch(r"pp?\. ([ivxlc]+|\d+)(–\d+)?(, \d+)*|ch\. \d+(, [^|]+)?|(?i:introduction|conclusion|foreword|preface|afterword|epilogue|prologue|appendix( [A-Z0-9]+)?)|under '.+'", page):
            problems.append(f"{where}: the page should read like 'p. 87', 'pp. 87–89' or under 'Whist'"); continue
        # terms of art that carry a refused word without judging anything: they are names, so they stay as the books use them
        # A term's name is the book's own and is never changed to pass this check; in a definition, a book's term in single quotes passes too
        plain = [re.sub(r"'[^']+'|\b(im)?perfect information\b|\bbest[- ]of[- ](three|five|seven|several|\w+ games)\b", "", cells[1], flags=re.I)]
        for word in {m.lower() for c in plain for m in BANNED.findall(c)}:
            problems.append(f"{where}: banned word '{word}'")
        entry = {"name": cells[0], "text": cells[1], "short": book["short"], "page": page}
        (terms if kind == "term" else ideas).append(entry)
for p in problems:
    print("PROBLEM", p)
if problems:
    sys.exit(1)
terms.sort(key=lambda t: re.sub(r"^(the|a|an) ", "", t["name"].lower()))
refs = sorted({SOURCES[os.path.basename(p).split(".")[0]]["ref"] for p in glob.glob(os.path.join(HERE, "*.txt"))})
json.dump({"terms": terms, "ideas": ideas, "references": refs}, open(os.path.join(HERE, "..", "ideas.json"), "w"), indent=1, ensure_ascii=False)
print(f"wrote ideas.json: {len(terms)} terms, {len(ideas)} ideas, from {len(refs)} books")
