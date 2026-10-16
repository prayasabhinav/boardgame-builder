"""A known game as a Markdown file, and back again.

The tool hands out these files (Download as a design) and Open game reads the saved state at their end; the wiki
hands out the same files and takes new games as files in the same shape, so one format serves both. The parts:

    # Title
    - From: ...    - Players: ...    - Time: ...    - Made by: ...    (- Rules from: ...    - This version: ...)
    a paragraph or two about the game
    ## What it shows a designer (one or two sentences: the design idea that playing it makes felt)
    ## What you need / ## How to play (1. **Step.** what to do) / ## After playing, talk about
    ## Where the rules are written down (optional) / ## Its blocks (- Group: block; block)
    ## Saved state (written for Open game; ignored when a file is read back)
"""
import json
import re

from palette import DIMENSIONS

META = {"from": "parent_game", "players": "players", "time": "duration"}
# Credits are rows: who made the game, where its rules were taken from, what this version changes, and how it was added
CREDITS = {"by": "Made by", "rules": "Rules from", "version": "This version", "added": "Added"}
SECTIONS = {"what it shows a designer": "lesson", "what you need": "equipment", "how to play": "steps", "after playing, talk about": "what_to_notice",
            "where the rules are written down": "sources", "its blocks": "blocks", "saved state": None}
BLOCK = {d["id"]: {b["id"]: b["display"] for b in d["blocks"]} for d in DIMENSIONS}


def to_markdown(g, version):
    lines = [f"# {g['title']}", "", f"- From: {g['parent_game']}", f"- Players: {g['players']}", f"- Time: {g['duration']}",
             *[f"- {label}: {g['credits'][k]}" for k, label in CREDITS.items() if g["credits"].get(k)], "",
             f"Made with boardgameBuilder {version}. To design from it, open boardgameBuilder and choose Open game: "
             "its blocks go on the canvas, and the feelings are left for you to pick.", "",
             g["intro"], "", "## What it shows a designer", "", g["lesson"], "", "## What you need", "", *[f"- {e}" for e in g["equipment"]], "", "## How to play", "",
             *[f"{s['n']}. **{s['title']}{'' if s['title'][-1] in '?!.' else '.'}** {s['body']}" for s in g["steps"]], "",
             "## After playing, talk about", "", *[f"- {n}" for n in g["what_to_notice"]], ""]
    if g.get("sources"):
        lines += ["## Where the rules are written down", "", *[f"- {u}" for u in g["sources"]], ""]
    lines += ["## Its blocks", ""]
    for d in DIMENSIONS:
        picked = g["design"].get(d["id"], [])
        if picked:
            lines.append(f"- {d['display']}: {'; '.join(BLOCK[d['id']][b] for b in (picked if isinstance(picked, list) else [picked]))}")
    state = {"mechanics": g["design"], "chosenFeelings": [], "previousMechanics": {}, "previousFeelings": [], "turnNumber": 0,
             "locked": False, "turnHistory": [], "answers": {}, "tests": {}}
    lines += ["", "## Saved state", "", "boardgameBuilder reads this part back when the file is opened.", "",
              "```json", json.dumps(state), "```", ""]
    return "\n".join(lines)


def teaches(design):
    """The short line a game card shows under 'Shows': its core blocks first, then how information and play work."""
    parts = list(design.get("core-mechanic", [])) + [design[k] for k in ("information", "player-interaction", "victory-condition") if k in design]
    return " + ".join(parts[:3])


def from_markdown(text):
    """Returns (game, problem). The game has no id, animation or questions; problem is '' when the file reads."""
    g = {"title": "", "intro": "", "lesson": "", "equipment": [], "steps": [], "what_to_notice": [], "sources": [], "design": {}, "credits": {}}
    credit_keys = {label.lower(): k for k, label in CREDITS.items()} | {"credits": "by"}
    section, intro, problems = "", [], []
    for raw in text.replace("\r\n", "\n").split("\n"):
        line = raw.strip()
        if line.startswith("# ") and not g["title"]:
            g["title"] = line[2:].strip()
        elif line.startswith("## "):
            section = line[3:].strip().lower()
            if section not in SECTIONS:
                problems.append(f"the heading '{line[3:].strip()}' is not one the format has")
        elif section == "saved state" or not line:
            continue
        elif not section:
            m = re.match(r"- ([A-Za-z ]+): (.+)", line)
            key = m.group(1).strip().lower() if m else ""
            if key in META:
                g[META[key]] = m.group(2).strip()
            elif key in credit_keys:
                g["credits"][credit_keys[key]] = m.group(2).strip()
            elif not line.startswith("Made with boardgameBuilder"):
                intro.append(line)
        elif SECTIONS[section] == "steps":
            m = re.match(r"\d+\.\s+\*\*(.+?)\.?\*\*\s*(.*)", line)
            if m:
                g["steps"].append({"n": len(g["steps"]) + 1, "title": m.group(1).strip(), "body": m.group(2).strip()})
            else:
                problems.append(f"a step should read '1. **Title.** What to do', not '{line[:60]}'")
        elif SECTIONS[section] == "lesson":
            g["lesson"] = (g["lesson"] + " " + line).strip()
        elif SECTIONS[section] == "blocks":
            problems += read_blocks(line, g["design"])
        elif line.startswith("- "):
            g[SECTIONS[section]].append(line[2:].strip())
    g["intro"] = " ".join(intro)
    missing = [label for label, ok in (("a title", g["title"]), ("From", g.get("parent_game")), ("Players", g.get("players")),
                                       ("Time", g.get("duration")), ("Made by", g["credits"].get("by")), ("a paragraph about the game", g["intro"]), ("What it shows a designer", g["lesson"]),
                                       ("What you need", g["equipment"]), ("at least two steps", len(g["steps"]) > 1),
                                       ("After playing, talk about", g["what_to_notice"]), ("Its blocks", g["design"])) if not ok]
    if missing:
        problems.append("it is missing " + ", ".join(missing))
    return g, "; ".join(problems)


def read_blocks(line, design):
    m = re.match(r"- ([^:]+):\s*(.+)", line)
    dim = next((d for d in DIMENSIONS if m and d["display"].lower() == m.group(1).strip().lower()), None)
    if not dim:
        return [f"'{line[:60]}' should start with a group: " + ", ".join(d["display"] for d in DIMENSIONS)]
    names = {v.lower(): k for k, v in BLOCK[dim["id"]].items()}
    picked = [names.get(n.strip().lower()) for n in m.group(2).split(";")]
    if None in picked:
        return [f"in {dim['display']}, the blocks are: " + "; ".join(BLOCK[dim["id"]].values())]
    if not dim.get("multi") and len(picked) > 1:
        return [f"{dim['display']} takes one block"]
    design[dim["id"]] = picked if dim.get("multi") else picked[0]
    return []
