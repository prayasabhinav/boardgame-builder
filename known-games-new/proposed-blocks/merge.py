"""Merge the proposed-block files into book-blocks.json, which palette.py and block_meta.py read.

Run once from the tool's folder, on 6 November 2026: python known-games-new/proposed-blocks/merge.py
From then on book-blocks.json is the record, edited by hand; running this again would undo those edits.

Each block keeps the first full ? text and drawing found for it, and every book and games line behind it. Three pairs
proposed from different books name one mechanism in one slot, so each pair becomes one block (SAME below); undo by
deleting its line. Every block is marked tentative: added 6 November 2026 on Prayas's word ("proposed blocks are fine -
key them tentatively"), not yet tried in a class.
"""
import csv
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SHORT = {r["book"]: r["short"] for r in csv.DictReader(open(ROOT / "kb-books/sources.tsv", encoding="utf-8"), delimiter="\t")}
SAME = {"earn-another-turn": "extra-turn", "help-the-player-behind": "catch-up-help", "trap-between-two": "capture-by-surrounding"}
SLOTS = ["core-mechanic", "victory-condition", "player-interaction", "chance-skill", "information", "timing", "simulation"]


def field(sec, name):
    m = re.search(r"^- " + re.escape(name) + r": (.*)$", sec, re.M)
    return m.group(1).strip() if m else ""


blocks = {}
for f in sorted(HERE.glob("*.md")):
    if f.name == "INDEX.md":
        continue
    book = f.name.split(".")[0]
    for sec in re.split(r"^## ", f.read_text(encoding="utf-8"), flags=re.M)[1:]:
        bid = field(sec, "Id").split(" ")[0]
        if not bid:
            continue
        merged, bid = bid in SAME, SAME.get(bid, bid)
        b = blocks.setdefault(bid, {"id": bid, "slot": "", "display": "", "description": "", "svg": "", "books": [], "games": []})
        title = re.sub(r"^Proposed block: |\s*\(.*\)$", "", sec.splitlines()[0]).strip()
        if not merged and not b["display"] and "already" not in title:
            b["display"] = title
        b["slot"] = b["slot"] or field(sec, "Slot")
        text = field(sec, "? text")
        if not merged and not b["description"] and text and not re.match(r"(As already|Use the text|Already)", text):
            b["description"] = text
        svg = field(sec, "Drawing")
        if not merged and not b["svg"] and svg.startswith("<svg"):
            b["svg"] = svg
        if SHORT[book] not in b["books"]:
            b["books"].append(SHORT[book])
        games = field(sec, "Games in this book that use it") or field(sec, "More games that use it")
        if games:
            b["games"].append(f"{SHORT[book]}: {games}")

out = []
for b in sorted(blocks.values(), key=lambda b: (SLOTS.index(b["slot"]), b["id"])):
    b["display"] = b["display"] or b["id"].replace("-", " ")
    missing = [k for k in ("slot", "description", "svg") if not b[k]]
    if missing:
        raise SystemExit(f"{b['id']}: no {', '.join(missing)}")
    out.append({**b, "tentative": True})
(ROOT / "book-blocks.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote book-blocks.json: {len(out)} blocks", {s: sum(b["slot"] == s for b in out) for s in SLOTS})
