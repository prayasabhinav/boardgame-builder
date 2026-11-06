"""Keeps an Ideas line only where a checker found its passage in the book and code finds the checker's copied words there too.

A checker that did not write the lines wrote, per line, `n<TAB>supported<TAB>place<TAB>up to 12 words copied from the book` or
`n<TAB>not found`. This script looks for the copied words in the book's text (case and spacing ignored, hyphenated line breaks
joined). A line stays when its row says supported and the words are found; otherwise it moves to ideas/removed/<file>, with the
reason, and nothing is deleted. Usage: python3 ideas/verify.py <folder of checker files> [book text folder]
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BOOKS = os.path.expanduser(sys.argv[2] if len(sys.argv) > 2 else "~/play-and-game-research")
norm = lambda t: re.sub(r"[^a-z0-9]+", " ", re.sub(r"-\s*\n\s*", "", t.lower())).strip()
os.makedirs(os.path.join(HERE, "removed"), exist_ok=True)
for check in sorted(glob.glob(os.path.join(sys.argv[1], "*.txt.tsv"))):
    name = os.path.basename(check)[:-4]
    path = os.path.join(HERE, name)
    book = norm(open(os.path.join(BOOKS, name.split(".")[0] + ".md"), errors="ignore").read())
    rows = {}
    for r in open(check, encoding="utf-8"):
        cells = r.rstrip("\n").split("\t")
        if cells and cells[0].strip().isdigit():
            rows[int(cells[0])] = cells
    lines = [l for l in open(path, encoding="utf-8") if l.strip()]
    keep, gone = [], []
    for n, line in enumerate(lines, 1):
        r = rows.get(n)
        if not r or len(r) < 2:
            gone.append(f"no row from the checker\t{line}")
        elif r[1].strip() != "supported":
            gone.append(f"checker found no passage\t{line}")
        elif len(r) < 4 or len(norm(r[3]).split()) < 3 or norm(r[3]) not in book:
            gone.append(f"copied words not in the book: {r[3] if len(r) > 3 else ''}\t{line}")
        else:
            keep.append(line)
    open(path, "w", encoding="utf-8").writelines(keep)
    if gone:
        open(os.path.join(HERE, "removed", name), "a", encoding="utf-8").writelines(gone)
    print(f"{name:58} kept {len(keep):4}  moved {len(gone):4}")
