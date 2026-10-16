"""FastAPI local server for boardgameBuilder.

Runs on localhost. Serves the frontend and exposes three endpoints:
- GET  /palette   — palette data for the frontend (dimensions + feelings)
- POST /narrate   — stage 2 + 3 for one turn
- POST /complete  — stage 3 final summary for Mark complete
"""

import json
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from rules import compute_diff, match_kb
from templates import build_template_output, render_summary, render_turn
from palette import DIMENSIONS, FEELINGS
from block_meta import meta_for


def _enrich(blocks: list) -> list:
    """Attach description + svg metadata to each block dict."""
    out = []
    for b in blocks:
        meta = meta_for(b["id"])
        out.append({**b, "description": meta["description"], "svg": meta["svg"]})
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


class TurnRequest(BaseModel):
    canvas: CanvasState
    previous: CanvasState = CanvasState()


@app.get("/palette")
def get_palette():
    return _palette_payload()


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

    return {
        "narration": render_summary(template_output, canvas),
        "source": "empty" if template_output["mode"] == "empty" else "knowledge-base",
        "matches": matches,
    }


# Serve frontend from /static/* and root
@app.get("/")
def root():
    # Stamp the newest static file's time onto the script and stylesheet links, so a browser never keeps an old copy after a change
    stamp = int(max(f.stat().st_mtime for f in STATIC_DIR.iterdir()))
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    return HTMLResponse(html.replace('.js"', f'.js?v={stamp}"').replace('.css"', f'.css?v={stamp}"'))


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8787))
    # HOST is 0.0.0.0 only inside the container; access_log off, so no per-visitor request lines are kept
    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=port, access_log=False)
