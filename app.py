"""FastAPI local server for boardgameBuilder.

Runs on localhost. Serves the frontend and exposes these endpoints:
- GET  /palette   — palette data for the frontend (dimensions + feelings, each block with its questions)
- GET  /tests     — short tests of one part of a game, and of two parts together
- GET  /games     — known games to play with things at hand, then watch and answer questions about
- GET  /games/{id}.md — one known game as a Markdown file that Open game loads as a starting design
- POST /narrate   — stage 2 + 3 for one turn
- POST /complete  — stage 3 final summary for Mark complete
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rules import compute_diff, match_kb
from templates import build_template_output, display, render_summary, render_turn
from palette import DIMENSIONS, FEELINGS
from block_meta import meta_for
from known_games import to_markdown
from site_config import SYNTAX_URL, TOOL_URL, WIKI_URL


def _enrich(blocks: list) -> list:
    """Attach description + svg metadata to each block dict."""
    out = []
    for b in blocks:
        meta = meta_for(b["id"])
        out.append({**b, "description": meta["description"], "svg": meta["svg"], "questions": QUESTIONS.get(b["id"], [])})
    return out


def _palette_payload() -> dict:
    enriched_dims = []
    for d in DIMENSIONS:
        enriched_dims.append({**d, "blocks": _enrich(d["blocks"])})
    enriched_feels = _enrich(FEELINGS)
    return {"dimensions": enriched_dims, "feelings": enriched_feels}


# --- Paths + KB load --------------------------------------------------------

ROOT = Path(__file__).parent
STATIC_DIR = ROOT / "static"
KB_PATH = ROOT / "interactions.json"

with open(KB_PATH, "r", encoding="utf-8") as f:
    KB = json.load(f)

# The drafted pairs come after the curated ones, so a curated entry is always found first
with open(ROOT / "interactions-drafted.json", "r", encoding="utf-8") as f:
    DRAFTED = json.load(f)
KB["pairs"] += DRAFTED["pairs"]
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
@app.get("/")
def root():
    # Stamp the newest static file's time onto the script and stylesheet links, so a browser never keeps an old copy after a change
    stamp = int(max(f.stat().st_mtime for f in STATIC_DIR.iterdir()))
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    # no-cache: a browser asks again before reusing the page, so a reload never shows a page from before a deploy
    page = html.replace('.js"', f'.js?v={stamp}"').replace('.css"', f'.css?v={stamp}"').replace("__VERSION__", VERSION).replace("__TOOL_URL__", TOOL_URL).replace("__WIKI_URL__", WIKI_URL).replace("__SYNTAX_URL__", SYNTAX_URL)
    return HTMLResponse(page, headers={"Cache-Control": "no-cache"})


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8787))
    # HOST is 0.0.0.0 only inside the container; access_log off, so no per-visitor request lines are kept
    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=port, access_log=False)
