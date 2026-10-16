"""Stage 3a — template sentence structures.

Produces the feedback prose from Stage 2's structured matches. No model is
called: every sentence is a knowledge-base sentence, a fixed template line
here, or a bridge from bridges.py (16 October 2026).

Every claim in this module is traceable to the KB. No invented content.
"""

import zlib

from bridges import BRIDGES
from palette import DIMENSIONS

from typing import Any


# --- Element display mapping ------------------------------------------------

ELEMENT_DISPLAY = {b["id"]: b["display"] for d in DIMENSIONS for b in d["blocks"]}


def display(element_id: str) -> str:
    return ELEMENT_DISPLAY.get(element_id, element_id)


def list_to_prose(items: list) -> str:
    items = [display(x) for x in items]
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"


# --- Template functions -----------------------------------------------------


def template_diff_header(diff: dict) -> str:
    """Narrate what changed this turn."""
    if diff["is_first_turn"]:
        mechs, feels = diff["added_mechanics"], diff["added_feelings"]
        if not mechs and not feels:
            return "Your canvas is empty. Drag some blocks on to begin."
        if not mechs:
            return f"You've started with the feeling {list_to_prose(feels)}."
        with_feels = f", wanting the game to feel {list_to_prose(feels)}" if feels else ""
        return f"You've started by picking {list_to_prose(mechs)}{with_feels}."

    parts = []
    if diff["added_mechanics"]:
        parts.append(f"This turn you added {list_to_prose(diff['added_mechanics'])}")
    if diff["added_feelings"]:
        parts.append(f"added the feeling {list_to_prose(diff['added_feelings'])}")
    if diff["removed_mechanics"]:
        parts.append(f"took out {list_to_prose(diff['removed_mechanics'])}")
    if diff["removed_feelings"]:
        parts.append(f"removed the feeling {list_to_prose(diff['removed_feelings'])}")

    if not parts:
        return "Nothing changed this turn."
    parts[0] = parts[0].replace("This turn you ", "", 1)
    return "This turn you " + (", ".join(parts[:-1]) + ", and " + parts[-1] if len(parts) > 1 else parts[0]) + "."


def template_empty(canvas: dict) -> str:
    mech_count = len(canvas.get("mechanics", []))
    feel_count = len(canvas.get("feelings", []))

    if mech_count == 0 and feel_count == 0:
        return "Drag some blocks onto the canvas to start designing."
    if mech_count == 0:
        return (
            "You've chosen some feelings but no mechanics yet. "
            "Try adding a core mechanic to see how your game starts to take shape."
        )
    if mech_count == 1:
        return (
            "You have one block so far. Add a second block, in any slot, "
            "to see how the combination plays."
        )
    return ""


def template_pair(pair: dict) -> dict:
    """Return template fragments for one pair match."""
    return {
        "tendency": pair["tendency"],
        "pros": pair.get("pros", []),
        "cons": pair.get("cons", []),
        "exemplars": pair.get("exemplars", []),
        "elements": [display(e) for e in pair["elements"]],
        "tension_note": pair.get("tension_note"),
    }


def template_triad(triad: dict) -> dict:
    return {
        "tendency": triad["tendency"],
        "pros": triad.get("pros", []),
        "cons": triad.get("cons", []),
        "exemplars": triad.get("exemplars", []),
        "elements": [display(e) for e in triad["elements"]],
    }


def template_conflict(conflict: dict) -> dict:
    return {"elements": conflict["elements"], "student_note": conflict["student_note"]}


def template_feeling_service(fs: dict) -> str:
    neither = [n["feeling"] for n in fs.get("neither", [])]
    if fs["verdict"] == "neither":
        return (f"You said you wanted your game to feel {list_to_prose(neither)}. "
                f"The blocks you chose neither push toward that feeling nor away from it yet.")
    text = _feeling_verdict_text(fs)
    if text and neither:
        text += f" Your blocks neither push toward nor away from {list_to_prose(neither)} yet."
    return text


def _feeling_verdict_text(fs: dict) -> str:
    verdict = fs["verdict"]

    if verdict == "no-feelings":
        return ""

    sup = fs["supported"]
    opp = fs["opposed"]

    if verdict == "matches":
        names = [s["feeling"] for s in sup]
        return (
            f"You said you wanted your game to feel {list_to_prose(names)}. "
            f"The blocks you chose support that — your game is building toward what you want."
        )

    if verdict == "pulling-apart":
        opp_names = [o["feeling"] for o in opp]
        opp_by = _unique_union([o["by"] for o in opp])
        return (
            f"You said you wanted your game to feel {list_to_prose(opp_names)}. "
            f"But the blocks you chose — {list_to_prose(opp_by)} — tend to pull away from that. "
            f"This is something to notice, not to fix — you decide whether to change mechanics or change what you want."
        )

    if verdict == "partly-matches":
        sup_names = [s["feeling"] for s in sup]
        opp_names = [o["feeling"] for o in opp]
        return (
            f"You said you wanted your game to feel {list_to_prose(sup_names + opp_names)}. "
            f"Your blocks help with {list_to_prose(sup_names)}, but pull a little away from {list_to_prose(opp_names)}. "
            f"One game can hold two feelings that pull different ways."
        )

    return ""


def _unique_union(lists: list) -> list:
    seen = set()
    out = []
    for lst in lists:
        for item in lst:
            if item not in seen:
                seen.add(item)
                out.append(item)
    return out


# --- Compose full template output ------------------------------------------


def build_template_output(matches: dict, canvas: dict, diff: dict) -> dict:
    """Assemble the full structured template output for one turn."""
    empty_msg = template_empty(canvas)
    if empty_msg:
        return {
            "mode": "empty",
            "diff_header": template_diff_header(diff),
            "body": empty_msg,
            "pairs": [],
            "triads": [],
            "conflicts": [],
            "feeling_service": "",
        }

    pair_templates = [template_pair(p) for p in matches["pairs"]]
    triad_templates = [template_triad(t) for t in matches["triads"]]
    conflict_texts = [template_conflict(c) for c in matches["conflicts"]]
    feeling_text = template_feeling_service(matches["feeling_service"])

    # Sort pairs and triads to foreground diff-relevant matches
    added = set(diff["added_mechanics"])
    def _relevance(entry):
        return sum(1 for el in entry["elements"] if el in added)

    # Pair entries are stored as dicts with `elements` key — match that
    matches_pairs_sorted = sorted(matches["pairs"], key=_relevance, reverse=True)
    matches_triads_sorted = sorted(matches["triads"], key=_relevance, reverse=True)

    pair_templates = [template_pair(p) for p in matches_pairs_sorted]
    triad_templates = [template_triad(t) for t in matches_triads_sorted]

    return {
        "mode": "full",
        "diff_header": template_diff_header(diff),
        "pairs": pair_templates,
        "triads": triad_templates,
        "conflicts": conflict_texts,
        "feeling_service": feeling_text,
        "themes": [t["line"] for t in matches["themes"]],
        "overall_tendency": _overall_tendency(pair_templates, triad_templates),
    }


def _overall_tendency(pairs: list, triads: list) -> str:
    """Pick the most salient single-sentence tendency from matched entries.
    Prefer triads (more specific) over pairs; within each, prefer the first.
    """
    if triads:
        return triads[0]["tendency"]
    if pairs:
        return pairs[0]["tendency"]
    return ""


def _pick(slot: str, key: str, **fill) -> str:
    """One version of a bridge, chosen by the text it introduces, so the same canvas always reads the same."""
    versions = BRIDGES[slot]
    return versions[zlib.crc32(key.encode()) % len(versions)].format(**fill)


def _tendency_sentences(entries: list) -> list:
    out = [f"{_pick('tendency', entries[0]['tendency'])} {entries[0]['tendency']}"] if entries else []
    for e in entries[1:3]:
        out.append(f"{_pick('more', e['tendency'], blocks=list_to_prose(e['elements'])).capitalize()} {e['tendency']}")
    return out


def _detail_sentences(template_output: dict, entries: list) -> list:
    out = list(template_output["themes"])
    if entries and entries[0]["pros"]:
        out.append(f"{_pick('pros', entries[0]['pros'][0])} {' '.join(entries[0]['pros'])}")
    if entries and entries[0]["cons"]:
        out.append(f"{_pick('cons', entries[0]['cons'][0])} {' '.join(entries[0]['cons'])}")
    for c in template_output["conflicts"]:
        out.append(f"{_pick('conflict', c['student_note'], blocks=list_to_prose(c['elements'])).capitalize()} {c['student_note']}")
    if template_output["feeling_service"]:
        out.append(template_output["feeling_service"])
    games = exemplar_games(template_output)
    if games:
        out.append(_pick("games", games[0], games=list_to_prose(games)))
    return out


def render_turn(template_output: dict) -> str:
    """One paragraph of feedback for a turn: every sentence is from the knowledge base or bridges.py."""
    if template_output["mode"] == "empty":
        return f"{template_output['diff_header']} {template_output['body']}"
    entries = template_output["triads"] + template_output["pairs"]
    return " ".join([template_output["diff_header"]] + _tendency_sentences(entries) + _detail_sentences(template_output, entries))


def render_summary(template_output: dict, canvas: dict) -> str:
    """The closing summary: the design by dimension and what it tends to be, then the details and a last line."""
    if template_output["mode"] == "empty":
        return "Your canvas was empty — no game was designed this session."
    entries = template_output["triads"] + template_output["pairs"]
    chosen = canvas.get("mechanics", [])
    rows = [f"{d['display']}: {list_to_prose([b['id'] for b in d['blocks'] if b['id'] in chosen])}"
            for d in DIMENSIONS if any(b["id"] in chosen for b in d["blocks"])]
    core = [b["id"] for b in DIMENSIONS[0]["blocks"] if b["id"] in chosen]
    key = " ".join(chosen)
    first = " ".join([_pick("summary_open", key), "; ".join(rows) + "."] + _tendency_sentences(entries))
    close = _pick("summary_close", key, blocks=list_to_prose(core)) if core else "Now you would build a prototype."
    return first + "\n\n" + " ".join(_detail_sentences(template_output, entries) + [close])


def exemplar_games(template_output: dict) -> list:
    """The example games the template names: up to two from each of the first two matches, at most three."""
    games = []
    for entry in (template_output["triads"] + template_output["pairs"])[:2]:
        for g in entry.get("exemplars", [])[:2]:
            if g not in games:
                games.append(g)
    return games[:3]
