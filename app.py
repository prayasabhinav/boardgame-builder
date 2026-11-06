"""FastAPI local server for boardgameBuilder.

Runs on localhost. Serves the frontend and exposes these endpoints:
- GET  /palette   — palette data for the frontend (dimensions + feelings, each block with its questions)
- GET  /tests     — short tests of one part of a game, and of two parts together
- GET  /ideas     — the Ideas tab: glossary terms and key ideas from books, each with its book and page
- GET  /games     — known games to play with things at hand, then watch and answer questions about
- GET  /games/{id}.md — one known game as a Markdown file that Open game loads as a starting design
- POST /narrate   — stage 2 + 3 for one turn
- POST /complete  — stage 3 final summary for Mark complete
- POST /class, POST + GET /class/{code}/flags, DELETE /class/{code} — remote teacher mode, held in memory only
- GET  /teacher   — the teacher's page
"""

import json
import os
import secrets
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rules import compute_diff, match_kb
from templates import build_template_output, cite, display, render_summary, render_turn
from palette import DIMENSIONS, FEELINGS

# The slots that hold several blocks, named on the page from the palette so the text cannot fall behind it.
_multi = [f"<em>{d['display']}</em>" for d in DIMENSIONS if d.get("multi")]
MULTI_SLOTS = ", ".join(_multi[:-1]) + " and " + _multi[-1] if len(_multi) > 1 else "".join(_multi)
from block_meta import meta_for
from known_games import to_markdown
from site_config import SYNTAX_URL, TOOL_URL, WIKI_URL


def _enrich(blocks: list) -> list:
    """Attach description + svg metadata to each block dict."""
    out = []
    for b in blocks:
        meta = meta_for(b["id"])
        out.append({**b, "description": meta["description"], "svg": meta["svg"], "questions": QUESTIONS.get(b["id"], []),
                    **({"from": meta["credit"]} if meta.get("tentative") else {})})
    return out


def _palette_payload() -> dict:
    enriched_dims = []
    for d in DIMENSIONS:
        enriched_dims.append({**d, "blocks": _enrich(d["blocks"])})
    enriched_feels = _enrich(FEELINGS)
    # The pairs a placed block is marked unusual against; placing them stays allowed, and in a class the teacher sees them
    unusual = [{"blocks": c["elements"], "note": c["student_note"] + cite(c)} for c in KB["conflicts"]]
    # Pairs review-model/rules.py marks from its table, with the reason; a pair no known game has is not marked for that alone
    if (ROOT / "review.json").exists():
        review = json.loads((ROOT / "review.json").read_text(encoding="utf-8"))
        unusual += [{"blocks": p.split("+"), "note": f"{review['reasons'][p][0].upper()}{review['reasons'][p][1:]}. Needs a look: {review['score'][p]} of 10. Is that the new thing in your game, or a clash?"}
                    for p in review["flagged"]]
    return {"dimensions": enriched_dims, "feelings": enriched_feels, "unusual": unusual}


# --- Paths + KB load --------------------------------------------------------

ROOT = Path(__file__).parent
STATIC_DIR = ROOT / "static"
KB_PATH = ROOT / "interactions.json"

with open(KB_PATH, "r", encoding="utf-8") as f:
    KB = json.load(f)

# The drafted pairs come after the curated ones, so a curated entry is always found first
with open(ROOT / "interactions-drafted.json", "r", encoding="utf-8") as f:
    DRAFTED = json.load(f)
# Entries taken from books, each with its book and page, sit between the two: one entry per pair, curated first, then a book's, then drafted
BOOKS = json.loads((ROOT / "interactions-books.json").read_text(encoding="utf-8"))
_have = {frozenset(p["elements"]) for p in KB["pairs"]}
KB["pairs"] += [p for p in BOOKS["pairs"] if frozenset(p["elements"]) not in _have]
_have |= {frozenset(p["elements"]) for p in BOOKS["pairs"]}
KB["pairs"] += [p for p in DRAFTED["pairs"] if frozenset(p["elements"]) not in _have]
KB["conflicts"] += BOOKS["conflicts"]
KB["themes"] = DRAFTED["themes"]
for fb in KB["feeling_blocks"]:
    links = DRAFTED["feeling_links"][fb["feeling"]]
    fb["supported_by"] = fb["supported_by"] + links["supported_by"]
    fb["opposed_by"] = fb["opposed_by"] + links["opposed_by"]


# Carried from the April 2026 demo on 16 October 2026: questions asked when a block is placed, short tests of one part, and known games
QUESTIONS = json.loads((ROOT / "block-questions.json").read_text(encoding="utf-8"))
PART_TESTS = json.loads((ROOT / "part-tests.json").read_text(encoding="utf-8"))
GAMES = json.loads((ROOT / "games.json").read_text(encoding="utf-8"))
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def own_choices(canvas: dict) -> str:
    """The designers' answers to the block questions and their notes from the part tests, said back in fixed words."""
    said = []
    for block, picked in canvas["answers"].items():
        names = [o["n"].lower() for q in QUESTIONS.get(block, []) for o in q["options"] if picked.get(q["key"]) == o["v"]]
        if names:
            said.append(f"{display(block)} works like this: {', '.join(names)}")
    out = [f"You said {'; '.join(said)}."] if said else []
    titles = {"+".join(t["blocks"]): t["title"] for t in PART_TESTS["pairs"]} | {b: t["title"] for b, t in PART_TESTS["tests"].items()}
    for key, report in canvas["tests"].items():
        bits = [f"it felt {', '.join(report['feelings'])}"] if report.get("feelings") else []
        if report.get("match"):
            bits.append(f"it matched what you wanted: {report['match']}")
        if report.get("note"):
            bits.append(f"one thing you would change: {report['note']}")
        if bits and key in titles:
            out.append(f"When you tested {titles[key]}, {'; '.join(bits)}.")
    return " ".join(out)


# --- FastAPI ---------------------------------------------------------------

app = FastAPI(title="boardgameBuilder")

# CORS — permissive for local use only
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class CanvasState(BaseModel):
    mechanics: list[str] = []
    feelings: list[str] = []
    answers: dict[str, dict[str, str]] = {}  # block id -> question key -> chosen option
    tests: dict[str, dict] = {}              # test key -> {feelings, match, note}


class TurnRequest(BaseModel):
    canvas: CanvasState
    previous: CanvasState = CanvasState()


@app.get("/palette")
def get_palette():
    return _palette_payload()


@app.get("/tests")
def get_tests():
    return PART_TESTS


@app.get("/ideas")
def get_ideas():
    """The Ideas tab: an alphabetical glossary and key ideas from books, each with its book and page."""
    return JSONResponse(json.loads((ROOT / "ideas.json").read_text(encoding="utf-8")))


@app.get("/games")
def get_games():
    return JSONResponse(GAMES, headers={"Cache-Control": "no-cache"})


@app.get("/games/{game_id}.md")
def game_file(game_id: str):
    """The game's rules, then its blocks, then a saved state in the same shape Save game writes, so Open game loads it."""
    g = next((x for x in GAMES if x["id"] == game_id), None)
    if not g:
        raise HTTPException(404)
    return Response(to_markdown(g, VERSION), media_type="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{game_id}.md"'})


@app.post("/narrate")
def narrate(req: TurnRequest):
    canvas = req.canvas.model_dump()
    previous = req.previous.model_dump()

    diff = compute_diff(canvas, previous)
    matches = match_kb(canvas, KB)
    template_output = build_template_output(matches, canvas, diff)

    return {
        "narration": render_turn(template_output),
        "source": "empty" if template_output["mode"] == "empty" else "knowledge-base",
        "matches": matches,
        "diff": diff,
    }


@app.post("/complete")
def complete(req: TurnRequest):
    canvas = req.canvas.model_dump()
    previous = req.previous.model_dump()

    diff = compute_diff(canvas, previous)
    matches = match_kb(canvas, KB)
    template_output = build_template_output(matches, canvas, diff)

    choices = own_choices(canvas)
    return {
        "narration": render_summary(template_output, canvas) + (f"\n\n{choices}" if choices else ""),
        "source": "empty" if template_output["mode"] == "empty" else "knowledge-base",
        "matches": matches,
    }


# Serve frontend from /static/* and root
# --- Remote teacher mode ----------------------------------------------------
# A class lives in this process's memory only: never written to disk, gone after a day or a restart.
# A student's entry exists only while their canvas has an unusual pair: their name, their blocks and the pairs, replaced on every change.

CLASSES: dict[str, dict] = {}
CLASS_LIFE = 24 * 3600


class Flags(BaseModel):
    name: str
    mechanics: dict = {}
    unusual: list[dict] = []


@app.post("/class")
def new_class():
    now = time.time()
    for code in [c for c, v in CLASSES.items() if now - v["made"] > CLASS_LIFE]:
        del CLASSES[code]
    if len(CLASSES) >= 1000:
        raise HTTPException(503, "Too many classes are open; try again later")
    code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(5))
    CLASSES[code] = {"key": secrets.token_urlsafe(16), "made": now, "students": {}}
    return {"code": code, "key": CLASSES[code]["key"]}


@app.post("/class/{code}/flags")
def send_flags(code: str, f: Flags):
    c = CLASSES.get(code.upper())
    if not c:
        raise HTTPException(404, "No class has that code")
    name = f.name.strip()[:60]
    if not name or (name not in c["students"] and len(c["students"]) >= 300):
        raise HTTPException(400, "A name is needed")
    if f.unusual:
        c["students"][name] = {"name": name, "mechanics": f.mechanics, "unusual": f.unusual[:20], "at": time.time()}
    else:
        c["students"].pop(name, None)   # nothing unusual on the canvas: nothing about this student is kept
    return {"ok": True}


@app.delete("/class/{code}")
def end_class(code: str, key: str):
    c = CLASSES.get(code.upper())
    if c and secrets.compare_digest(key, c["key"]):
        del CLASSES[code.upper()]
    return {"ok": True}


@app.get("/class/{code}/flags")
def read_flags(code: str, key: str):
    c = CLASSES.get(code.upper())
    if not c or not secrets.compare_digest(key, c["key"]):
        raise HTTPException(404, "No class has that code and key")
    return sorted(c["students"].values(), key=lambda s: s["at"], reverse=True)


@app.get("/teacher")
def teacher():
    return HTMLResponse((STATIC_DIR / "teacher.html").read_text(encoding="utf-8"), headers={"Cache-Control": "no-cache"})


@app.get("/")
def root():
    # Stamp the newest static file's time onto the script and stylesheet links, so a browser never keeps an old copy after a change
    stamp = int(max(f.stat().st_mtime for f in STATIC_DIR.iterdir()))
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    # no-cache: a browser asks again before reusing the page, so a reload never shows a page from before a deploy
    page = html.replace('.js"', f'.js?v={stamp}"').replace('.css"', f'.css?v={stamp}"').replace("__VERSION__", VERSION).replace("__TOOL_URL__", TOOL_URL).replace("__WIKI_URL__", WIKI_URL).replace("__SYNTAX_URL__", SYNTAX_URL).replace("__MULTI_SLOTS__", MULTI_SLOTS)
    return HTMLResponse(page, headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8787))
    # HOST is 0.0.0.0 only inside the container; access_log off, so no per-visitor request lines are kept
    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=port, access_log=False)
