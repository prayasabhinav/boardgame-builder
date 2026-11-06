"""Read boardgameBuilder's knowledge base into one list of wiki entries.

The corpus is read from the tool's own files (CORPUS_DIR, the folder above this one by default),
so the wiki never holds a second copy that could drift. Every entry has a stable key, which is
what a check is recorded against:

  block:<id>            a block's description          feeling:<id>         a feeling's description
  pair:<a>+<b>          a two-block entry              triad:<a>+<b>+<c>    a three-block entry
  conflict:<a>+<b>      a clash between two blocks     theme:<id>           a theme line
  link:<feeling>:<id>   whether a block supports a feeling, works against it, or neither
  game:<id>             a known game: rules to play with things at hand, and the blocks it is made of
  term:<short>: <name>  a glossary term on the Ideas tab   idea:<short>: <name>  a key idea on the Ideas tab

Pairs come from three places, and the wiki shows the one the tool uses: curated first, then a book's, then drafted.
"""
import json
import os
import sys
from pathlib import Path

CORPUS_DIR = Path(os.environ.get("CORPUS_DIR", Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(CORPUS_DIR))

import palette  # noqa: E402
from block_meta import meta_for  # noqa: E402
from known_games import from_markdown, to_markdown  # noqa: E402,F401  (used by the wiki through this module)
from site_config import SYNTAX_URL, TOOL_URL, WIKI_URL  # noqa: E402,F401  (the addresses, from one variable)

KINDS = {
    "block": "Block",
    "feeling": "Feeling",
    "pair": "Pair",
    "triad": "Triad",
    "conflict": "Conflict",
    "theme": "Theme line",
    "link": "Feeling and block",
    "game": "Known game",
    "term": "Glossary term",
    "idea": "Key idea",
}
PLURAL = {"block": "Blocks", "feeling": "Feelings", "pair": "Pairs", "triad": "Triads", "conflict": "Conflicts",
          "theme": "Theme lines", "link": "Feelings and blocks", "game": "Known games",
          "term": "Glossary terms", "idea": "Key ideas"}


def _load(name):
    with open(CORPUS_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def link_text(feeling, block, judgement, display):
    verb = "neither supports nor works against" if judgement == "neither" else judgement
    return f"{display[block]} {verb} the feeling {display.get(feeling, feeling)}."


def cite(entry):
    """Where a book's entry comes from, as the tool's feedback cites it: short form and page."""
    src = entry.get("source")
    return f"{src['short']}, {src['page']}" if isinstance(src, dict) else ""


def _key(kind, elements):
    return f"{kind}:" + "+".join(sorted(elements))


def load():
    curated = _load("interactions.json")
    drafted = _load("interactions-drafted.json")
    books = _load("interactions-books.json")
    ideas = _load("ideas.json")
    verdicts = _load("drafted/bgg-verdicts.json")

    groups, display, group_of = [], {}, {}
    for d in palette.DIMENSIONS:
        groups.append({"id": d["id"], "display": d["display"], "description": d["description"],
                       "blocks": [b["id"] for b in d["blocks"]]})
        for b in d["blocks"]:
            display[b["id"]] = b["display"]
            group_of[b["id"]] = d["display"]
    for f in palette.FEELINGS:
        display[f["id"]] = f["display"]

    entries = {}

    def add(key, kind, title, source, status, **fields):
        entries[key] = {"key": key, "kind": kind, "title": title, "source": source, "status": status, **fields}

    for bid, name in group_of.items():
        meta = meta_for(bid)
        add(f"block:{bid}", "block", display[bid], "book" if meta.get("tentative") else "curated",
            "tentative-20261106" if meta.get("tentative") else "written-for-the-tool",
            group=name, text=meta["description"], svg=meta["svg"], elements=[bid], credit=meta.get("credit"))

    for fb in curated["feeling_blocks"]:
        f = fb["feeling"]
        add(f"feeling:{f}", "feeling", display.get(f, f), "curated", fb["verification_status"],
            text=fb["description"], svg=meta_for(f)["svg"], exemplar=fb.get("exemplar"), elements=[f])

    games = {}
    for v in verdicts:
        games.setdefault(_key(v["kind"], v["elements"]), []).append(v)

    # Later wins for one key, so drafted, then a book's (its first entry for the pair), then curated: the one the tool uses.
    # A pair's other book entries are kept with it, as `also`.
    also = {}
    for p in books["pairs"]:
        also.setdefault(_key("pair", p["elements"]), []).append(
            {"text": p["tendency"], "pros": p["pros"], "cons": p["cons"], "cite": cite(p)})
    for kind, items, source in (("pair", drafted["pairs"], "drafted"), ("pair", books["pairs"][::-1], "book"),
                                ("pair", curated["pairs"], "curated"), ("triad", curated["triads"], "curated")):
        for p in items:
            key = _key(kind, p["elements"])
            add(key, kind, " + ".join(display[e] for e in p["elements"]), source, p["verification_status"],
                elements=p["elements"], text=p["tendency"], pros=p["pros"], cons=p["cons"],
                exemplars=p.get("exemplars", []), removed=p.get("exemplars_removed", []),
                unconfirmed=p.get("exemplars_unconfirmed", []), tension=p.get("tension_note"),
                checks=games.get(key, []), cite=cite(p), reference=(p.get("source") or {}).get("ref", "") if isinstance(p.get("source"), dict) else "")
            entries[key]["also"] = [a for a in also.get(key, []) if a["cite"] != entries[key]["cite"]]

    for c in curated["conflicts"] + books["conflicts"]:
        add(_key("conflict", c["elements"]), "conflict", " against ".join(display[e] for e in c["elements"]),
            "book" if c.get("source") else "curated", c.get("verification_status", "written-for-the-tool"),
            elements=c["elements"], text=c["student_note"], note=c["note"] if not c.get("source") else None, cite=cite(c),
            reference=c["source"]["ref"] if c.get("source") else "")

    for t in drafted["themes"]:
        add(f"theme:{t['theme']}", "theme", display[t["theme"]], "drafted", t["verification_status"],
            elements=[t["theme"]], text=t["line"])

    curated_links = {}
    for fb in curated["feeling_blocks"]:
        for b in fb["supported_by"]:
            curated_links[(fb["feeling"], b)] = "supports"
        for b in fb["opposed_by"]:
            curated_links[(fb["feeling"], b)] = "works against"
    for f, links in drafted["feeling_links"].items():
        judged = {b: "supports" for b in links["supported_by"]}
        judged |= {b: "works against" for b in links["opposed_by"]}
        judged |= {b: "neither" for b in links["neither"]}
        for b in group_of:
            if (f, b) in curated_links:
                judgement, source, status = curated_links[(f, b)], "curated", entries[f"feeling:{f}"]["status"]
            else:
                judgement, source, status = judged[b], "drafted", links["verification_status"]
            add(f"link:{f}:{b}", "link", f"{display.get(f, f)} · {display[b]}", source, status,
                elements=[f, b], judgement=judgement, text=link_text(f, b, judgement, display))

    for g in _load("games.json"):
        add(f"game:{g['id']}", "game", g["title"], "curated", "known-game", text=g["intro"], game=g,
            elements=[b for v in g["design"].values() for b in (v if isinstance(v, list) else [v])],
            checks=[v for v in verdicts if v["kind"] == "known game" and v["game"] == g.get("bgg")])

    refs = {r.split(" (")[0]: r for r in ideas["references"]}
    for kind, items in (("term", ideas["terms"]), ("idea", ideas["ideas"])):
        for i in items:
            key = f"{kind}:{i['short']}: {i['name']}"
            n = 2
            while key in entries:  # a book that names one term in two places keeps both
                key, n = f"{kind}:{i['short']}: {i['name']} ({n})", n + 1
            add(key, kind, i["name"], "book", "checked-against-book-20261106", text=i["text"], elements=[],
                cite=f"{i['short']}, {i['page']}", reference=next((r for a, r in refs.items() if r.startswith(i["short"].split(",")[0])), ""))

    for e in entries.values():
        e["search"] = " ".join([e["title"], e["text"], *e.get("pros", []), *e.get("cons", [])]).lower()

    notes = {}
    for name, title in (("mechanics-shortlist.md", "Mechanics shortlist"), ("feeling-blocks.md", "Feeling blocks")):
        notes[name.removesuffix(".md")] = {"title": title, "markdown": (CORPUS_DIR / name).read_text(encoding="utf-8")}

    return {"entries": entries, "groups": groups, "display": display, "notes": notes,
            "feelings": [f["id"] for f in palette.FEELINGS], "version": (CORPUS_DIR / "VERSION").read_text().strip()}
