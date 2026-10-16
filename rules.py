"""Stage 2 — deterministic rules.

Input: canvas state (mechanics + feelings) from Stage 1.
Output: structured match data drawn from interactions.json.

The rules layer does no language work. It produces a JSON-shaped verdict
that templates.py then converts to prose.
"""

from typing import Any


def match_kb(canvas: dict, kb: dict) -> dict:
    """Match the current canvas state against the knowledge body.

    canvas: {"mechanics": ["push-your-luck", ...], "feelings": ["excited", ...]}
    kb:     loaded interactions.json

    Returns:
        {
          "pairs":     [matched pair entries],
          "triads":    [matched triad entries],
          "conflicts": [matched conflict entries],
          "feeling_service": {
              "verdict":    "matches" | "partly-matches" | "pulling-apart" | "no-feelings",
              "supported":  [{"feeling": name, "by": [mechanic_ids]}, ...],
              "opposed":    [{"feeling": name, "by": [mechanic_ids]}, ...],
              "unknown":    [{"feeling": name}, ...]
          },
          "summary": {
              "mechanic_count": int,
              "feeling_count":  int,
              "pair_count":     int,
              "triad_count":    int,
              "conflict_count": int
          }
        }
    """
    mechs = set(canvas.get("mechanics", []))
    feels = set(canvas.get("feelings", []))

    pairs = _match_pairs(mechs, kb["pairs"])
    triads = _match_triads(mechs, kb["triads"])
    conflicts = _match_conflicts(mechs | feels, kb["conflicts"])
    feeling_service = _compute_intent_service(mechs, feels, kb["feeling_blocks"])
    themes = [t for t in kb["themes"] if t["theme"] in mechs]

    return {
        "pairs": pairs,
        "themes": themes,
        "triads": triads,
        "conflicts": conflicts,
        "feeling_service": feeling_service,
        "summary": {
            "mechanic_count": len(mechs),
            "feeling_count": len(feels),
            "pair_count": len(pairs),
            "triad_count": len(triads),
            "conflict_count": len(conflicts),
        },
    }


def _match_pairs(mechs: set, kb_pairs: list) -> list:
    matched = []
    for entry in kb_pairs:
        if all(el in mechs for el in entry["elements"]):
            matched.append(entry)
    return matched


def _match_triads(mechs: set, kb_triads: list) -> list:
    matched = []
    for entry in kb_triads:
        if all(el in mechs for el in entry["elements"]):
            matched.append(entry)
    return matched


def _match_conflicts(canvas_all: set, kb_conflicts: list) -> list:
    matched = []
    for entry in kb_conflicts:
        if all(el in canvas_all for el in entry["elements"]):
            matched.append(entry)
    return matched


def _compute_intent_service(mechs: set, feels: set, kb_feelings: list) -> dict:
    if not feels:
        return {"verdict": "no-feelings", "supported": [], "opposed": [], "unknown": []}

    supported = []
    opposed = []
    neither = []   # every block is judged against every feeling, so 'none of these blocks moves it' is a finding
    unknown = []

    for feeling_name in feels:
        fb = next((f for f in kb_feelings if f["feeling"] == feeling_name), None)
        if fb is None:
            unknown.append({"feeling": feeling_name})
            continue

        sups_in_canvas = [m for m in mechs if m in fb["supported_by"]]
        opps_in_canvas = [m for m in mechs if m in fb["opposed_by"]]

        if not mechs:
            # No mechanics chosen yet — can't yet tell
            unknown.append({"feeling": feeling_name})
        elif opps_in_canvas and not sups_in_canvas:
            opposed.append({"feeling": feeling_name, "by": opps_in_canvas})
        elif opps_in_canvas and sups_in_canvas:
            # Mixed signal — weighed by which side has more weight
            if len(opps_in_canvas) > len(sups_in_canvas):
                opposed.append({"feeling": feeling_name, "by": opps_in_canvas})
            else:
                supported.append({"feeling": feeling_name, "by": sups_in_canvas})
        elif sups_in_canvas:
            supported.append({"feeling": feeling_name, "by": sups_in_canvas})
        else:
            neither.append({"feeling": feeling_name})

    verdict = _verdict_from_counts(len(supported), len(opposed), len(neither), len(feels))

    return {
        "verdict": verdict,
        "supported": supported,
        "opposed": opposed,
        "neither": neither,
        "unknown": unknown,
    }


def _verdict_from_counts(sup: int, opp: int, neither: int, total: int) -> str:
    if total == 0:
        return "no-feelings"
    if opp == 0 and sup > 0:
        return "matches"
    if sup == 0 and opp > 0:
        return "pulling-apart"
    if sup > 0 and opp > 0:
        return "partly-matches"
    if neither > 0:
        return "neither"
    # No mechanics yet, or the feeling is not in the knowledge base
    return "no-feelings"


def compute_diff(current: dict, previous: dict) -> dict:
    """Compute what changed between two canvas states.

    Returns:
        {
          "added_mechanics": [...],
          "removed_mechanics": [...],
          "added_feelings": [...],
          "removed_feelings": [...],
          "is_first_turn": bool
        }
    """
    prev_mechs = set(previous.get("mechanics", []))
    prev_feels = set(previous.get("feelings", []))
    cur_mechs = set(current.get("mechanics", []))
    cur_feels = set(current.get("feelings", []))

    return {
        "added_mechanics": sorted(cur_mechs - prev_mechs),
        "removed_mechanics": sorted(prev_mechs - cur_mechs),
        "added_feelings": sorted(cur_feels - prev_feels),
        "removed_feelings": sorted(prev_feels - cur_feels),
        "is_first_turn": not prev_mechs and not prev_feels,
    }
