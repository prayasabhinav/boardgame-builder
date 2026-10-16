"""Carry approved wiki proposals into the tool's own files. Run from the tool's folder:

    python wiki/pull.py https://address-of-your-wiki
    python drafted/build.py && python check.py

then read the diff before deploying. It changes pairs, triads, conflicts, theme lines, feeling and block
descriptions, and feeling-and-block judgements, and adds new triads, conflicts and known games. A new game goes
into games.json without an animation or questions, so the tool offers it to play and to open as a design; a
change to a game already there is listed for doing by hand, since its animation may need redrawing. A new block or feeling
needs a drawing, a display name and pair entries, so it is listed for doing by hand. A drafted pair stays
drafted when it is changed: moving it into the curated part is a separate decision. The ids of proposals
already carried in are kept in wiki-applied.json, so running it again changes nothing twice.
"""
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, ".")
from known_games import from_markdown, teaches  # noqa: E402

DONE = Path("wiki-applied.json")
KB = Path("interactions.json")
GAMES = Path("games.json")
STATUS = "wiki-approved"


def inline(v):
    return json.dumps(v, ensure_ascii=False)


def write_kb(d):
    """interactions.json in its own layout: one key per line, values inline, so a change shows as a one-line diff."""
    def entry(e):
        return "    {\n" + ",\n".join(f"      {inline(k)}: {inline(v)}" for k, v in e.items()) + "\n    }"

    def nested(x):
        return "[\n" + ",\n".join(f"      {inline(i)}" for i in x) + "\n    ]" if isinstance(x, list) else inline(x)

    def value(v):
        if isinstance(v, list) and v and isinstance(v[0], dict):
            return "[\n" + ",\n".join(entry(e) for e in v) + "\n  ]"
        if isinstance(v, dict):
            return "{\n" + ",\n".join(f"    {inline(k)}: {nested(x)}" for k, x in v.items()) + "\n  }"
        return inline(v)

    KB.write_text("{\n" + ",\n".join(f"  {inline(k)}: {value(v)}" for k, v in d.items()) + "\n}\n", encoding="utf-8")


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def rewrite_line(files, match, new):
    """Replace the first line in files for which match(cells) is true with new(cells). Returns True if found."""
    for f in files:
        rows = f.read_text(encoding="utf-8").splitlines()
        for i, row in enumerate(rows):
            cells = [c.strip() for c in row.split("|")]
            if row.strip() and match(cells):
                rows[i] = new(cells)
                f.write_text("\n".join(rows) + "\n", encoding="utf-8")
                return True
    return False


def set_link(kb, feeling, block, judgement):
    fb = next(x for x in kb["feeling_blocks"] if x["feeling"] == feeling)
    for side in ("supported_by", "opposed_by"):
        if block in fb[side]:
            fb[side].remove(block)

    def strip(cells):
        plus = [b.strip() for b in cells[1].lstrip("+").split(",") if b.strip() and b.strip() != block]
        minus = [b.strip() for b in cells[2].lstrip("-").split(",") if b.strip() and b.strip() != block]
        return f"{cells[0]} | + {', '.join(plus)} | - {', '.join(minus)}"
    rewrite_line([Path("drafted/feelings.txt")], lambda c: c[0] == feeling, strip)
    if judgement != "neither":
        fb["supported_by" if judgement == "supports" else "opposed_by"].append(block)


def add_game(p):
    g, problem = from_markdown(p["body"])
    games = json.loads(GAMES.read_text(encoding="utf-8"))
    gid = p["key"].split(":", 1)[1]
    if problem or any(x["id"] == gid for x in games):
        return f"a new game, '{p['name']}': {problem or 'a game with that id is already in games.json'}"
    games.append({"id": gid, "title": g["title"], "parent_game": g["parent_game"],
                  "credits": {**g["credits"], "added": f"Proposed on the wiki by {p['user_name']}"}, "teaches": teaches(g["design"]),
                  "design": g["design"], "duration": g["duration"], "players": g["players"], "equipment": g["equipment"],
                  "intro": g["intro"], "steps": g["steps"], "what_to_notice": g["what_to_notice"],
                  "animation_type": "", "animation": [], "questions": [], "sources": g["sources"]})
    GAMES.write_text(json.dumps(games, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return ""


def apply(p, kb):
    """Returns '' when applied, or why it was left for doing by hand."""
    els, kind = json.loads(p["elements"]), p["kind"]
    pros, cons, games = lines(p["pros"]), lines(p["cons"]), lines(p["games"])
    if kind == "game":
        return add_game(p)
    if kind in ("block", "feeling"):
        return f"a new {kind}, '{p['name']}': add it to palette.py and block_meta.py, with a drawing and its pairs"
    if kind in ("triad", "conflict"):
        if kind == "triad":
            kb["triads"].append({"elements": els, "tendency": p["text"], "pros": pros, "cons": cons,
                                 "exemplars": games, "verification_status": STATUS})
        else:
            kb["conflicts"].append({"elements": els, "note": p["text"], "student_note": p["text"]})
        return ""
    target = p["key"].split(":", 1)[0]
    if target == "game":
        return f"a change to the game {p['key']}: replace its entry in games.json by hand and check its animation still matches"
    same = set(els)
    if target in ("pair", "triad"):
        for e in kb[target + "s"]:
            if set(e["elements"]) == same:
                e.update(tendency=p["text"], pros=pros, cons=cons, exemplars=games, verification_status=STATUS)
                return ""
        if target == "pair" and rewrite_line(sorted(Path("drafted").glob("[0-9]*.txt")),
                                             lambda c: set(c[0].split("+")) == same,
                                             lambda c: " | ".join([c[0], p["text"], *pros, *cons])):
            return ""
    elif target == "conflict":
        for e in kb["conflicts"]:
            if set(e["elements"]) == same:
                e["student_note"] = p["text"]
                return ""
    elif target == "theme":
        if rewrite_line([Path("drafted/themes.txt")], lambda c: c[0] == els[0], lambda c: f"{c[0]} | {p['text']}"):
            return ""
    elif target == "feeling":
        for e in kb["feeling_blocks"]:
            if e["feeling"] == els[0]:
                e["description"] = p["text"]
                return ""
    elif target == "link":
        set_link(kb, els[0], els[1], p["judgement"])
        return ""
    elif target == "block":
        meta = Path("block_meta.py")
        src = meta.read_text(encoding="utf-8")
        pattern = re.compile(r'("%s":\s*\{\s*"description":\s*)"(?:[^"\\]|\\.)*"' % re.escape(els[0]))
        if pattern.search(src):
            meta.write_text(pattern.sub(lambda m: m.group(1) + inline(p["text"]), src, count=1), encoding="utf-8")
            return ""
    return f"a change to {p['key']}: no matching entry found in the tool's files"


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    done = set(json.loads(DONE.read_text())) if DONE.exists() else set()
    with urllib.request.urlopen(sys.argv[1].rstrip("/") + "/export.json", timeout=60) as r:
        todo = [p for p in json.load(r)["approved_proposals"] if p["id"] not in done]
    kb = json.loads(KB.read_text(encoding="utf-8"))
    by_hand = []
    for p in todo:
        why = apply(p, kb)
        if why:
            by_hand.append(f"  #{p['id']} {why}")
        else:
            done.add(p["id"])
            print(f"  #{p['id']} {p['kind']} {p['key']}: applied")
    write_kb(kb)
    DONE.write_text(json.dumps(sorted(done)) + "\n")
    print(f"{len(todo) - len(by_hand)} applied, {len(by_hand)} left for doing by hand")
    print("\n".join(by_hand))
    print("Next: python drafted/build.py && python check.py, read the diff, then deploy the tool and the wiki.")


if __name__ == "__main__":
    main()
