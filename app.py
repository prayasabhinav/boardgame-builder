"""FastAPI local server for boardgameBuilder.

Runs on localhost. Serves the frontend and exposes these endpoints:
- GET  /palette   — palette data for the frontend (dimensions + feelings, each block with its questions)
- GET  /tests     — short tests of one part of a game, and of two parts together
- GET  /ideas     — the Ideas tab: glossary terms and key ideas from books, each with its book and page
- GET  /games     — known games to play with things at hand, then watch and answer questions about
- GET  /games/{id}.md — one known game as a Markdown file that Open game loads as a starting design
- POST /narrate   — stage 2 + 3 for one turn
- POST /complete  — stage 3 final summary for Mark complete
- POST /class, GET /class/{code}/key, POST /class/{code}/join, POST /class/{code}/design, GET /class/{code}/history, POST /class/{code}/reset-pin, GET /classes (admins), POST + GET /class/{code}/flags, POST /class/{code}/explore, GET /class/{code}/overview, DELETE /class/{code} — remote teacher mode, kept in CLASS_FILE
- GET  /teacher   — the teacher's page, or its sign-in page; POST /teacher/login, /teacher/logout, GET /teacher/me
"""

import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from pathlib import Path

from fastapi import Depends, FastAPI, HTTPException, Request
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
    # Pairs review-model/rules.py marks from its table, with the reason; a pair no known game has is not marked for that alone.
    # p is the small model's probability that the two blocks clash (review-model/rules.py); the teacher's page shows it, the student's note does not.
    if (ROOT / "review.json").exists():
        review = json.loads((ROOT / "review.json").read_text(encoding="utf-8"))
        unusual += [{"blocks": p.split("+"), "note": f"{review['reasons'][p][0].upper()}{review['reasons'][p][1:]}. Is that the new thing in your game, or a clash?", "p": review["p_clash"][p]}
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
# A class is kept in the file named by CLASS_FILE, rewritten on every change, so a restart or a deploy does not end it (his words,
# 16 November 2026: "classes should be held in persistent storage"); with no CLASS_FILE it lives in memory only. It lasts a semester
# unless a teacher ends it, and ending it deletes everything in it.
# Each student who joins chooses a four-digit PIN, and with the code, their name and the PIN they can come back from any device;
# every version of their design is kept for the class, a new version when the last is more than a minute old (his words, 16 November
# 2026: "students should be able to login anytime - store each student's history once they join class"). Teachers can step through it.
# A student's entry exists only while their canvas has an unusual pair: their name, their blocks and the pairs, replaced on every change.
# For the class as a whole the teacher also sees how many students joined, how many changes they made to their canvases, and how many
# placed a marked pair (his words, 6 November 2026: "I want usage statistics too - how many iterations how many students did. not
# surveillance, just overview"); the names behind those counts are held only to count each student once, and nothing per student is shown.

CLASS_LIFE = 120 * 24 * 3600   # a semester (his choice, 16 November 2026)
VERSION_GAP = 60                # seconds: a change within this of the last version replaces it
MAX_VERSIONS = 500
CLASS_FILE = os.environ.get("CLASS_FILE")
_class_lock = threading.Lock()


def _load_classes() -> dict[str, dict]:
    if not CLASS_FILE or not os.path.exists(CLASS_FILE):
        return {}
    saved = json.loads(Path(CLASS_FILE).read_text())
    return {code: {**c, "joined": set(c["joined"]), "flagged": set(c["flagged"]), "people": c.get("people", {})} for code, c in saved.items()
            if time.time() - c["made"] < CLASS_LIFE}


def save_classes():
    if not CLASS_FILE:
        return
    with _class_lock:
        data = {code: {**c, "joined": sorted(c["joined"]), "flagged": sorted(c["flagged"])} for code, c in CLASSES.items()}
        Path(CLASS_FILE + ".tmp").write_text(json.dumps(data))
        os.replace(CLASS_FILE + ".tmp", CLASS_FILE)


CLASSES: dict[str, dict] = _load_classes()
EXPLORE_LIFE = 2 * 3600   # exploration time: the teacher sees the student's clashing blocks but does not review them (his words, 6 November 2026)

# Teachers sign in (his words, 6 November 2026: "the teacher page should have a login"). TEACHER_LOGINS holds
# name:salt.hash entries (hex), comma-separated, made by teacher_logins.py; the passwords themselves are never on the server.
# With no TEACHER_LOGINS, nobody can start a class. A session is a signed cookie that lasts a week.
TEACHERS = dict(e.split(":", 1) for e in os.environ.get("TEACHER_LOGINS", "").split(",") if ":" in e)
# Teachers are not all equal (his words, 16 November 2026: "all teachers are not equal - I am super admin"): a name in
# TEACHER_ADMINS can end any class and sees every running class.
ADMINS = set(os.environ.get("TEACHER_ADMINS", "").split(","))
SESSION_KEY = (os.environ.get("TEACHER_SECRET") or secrets.token_hex(32)).encode()
SESSION_LIFE = 7 * 24 * 3600


def _sign(text: str) -> str:
    return hmac.new(SESSION_KEY, text.encode(), hashlib.sha256).hexdigest()


def signed_in(request: Request) -> str:
    """The signed-in teacher's name, or '' when there is none."""
    name, _, rest = request.cookies.get("bgb_teacher", "").partition("|")
    until, _, sig = rest.partition("|")
    ok = name in TEACHERS and until.isdigit() and int(until) > time.time() and hmac.compare_digest(sig, _sign(f"{name}|{until}"))
    return name if ok else ""


def teacher_only(request: Request) -> str:
    name = signed_in(request)
    if not name:
        raise HTTPException(401, "Sign in as a teacher first")
    return name


class Login(BaseModel):
    name: str
    password: str


class Flags(BaseModel):
    name: str
    token: str = ""
    mechanics: dict = {}
    unusual: list[dict] = []
    changed: bool = False   # the blocks on the canvas changed since the student's last report


@app.post("/teacher/login")
def teacher_login(login: Login, request: Request):
    name = login.name.strip().lower()
    salt, _, want = TEACHERS.get(name, "00.").partition(".")
    got = hashlib.pbkdf2_hmac("sha256", login.password.encode(), bytes.fromhex(salt), 200_000).hex()
    if name not in TEACHERS or not hmac.compare_digest(got, want):
        time.sleep(1)   # slows guessing
        raise HTTPException(401, "That name and password do not match")
    until = str(int(time.time()) + SESSION_LIFE)
    resp = JSONResponse({"ok": True, "name": name})
    resp.set_cookie("bgb_teacher", f"{name}|{until}|{_sign(f'{name}|{until}')}", max_age=SESSION_LIFE, httponly=True,
                    secure=request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https", samesite="strict")
    return resp


@app.post("/teacher/logout")
def teacher_logout():
    resp = JSONResponse({"ok": True})
    resp.delete_cookie("bgb_teacher")
    return resp


@app.get("/teacher/me")
def teacher_me(request: Request):
    name = signed_in(request)
    return {"name": name, "logins": bool(TEACHERS), "admin": name in ADMINS}


@app.post("/class")
def new_class(teacher: str = Depends(teacher_only)):
    now = time.time()
    for code in [c for c, v in CLASSES.items() if now - v["made"] > CLASS_LIFE]:
        del CLASSES[code]
    if len(CLASSES) >= 1000:
        raise HTTPException(503, "Too many classes are open; try again later")
    code = "".join(secrets.choice("ABCDEFGHJKLMNPQRSTUVWXYZ23456789") for _ in range(5))
    CLASSES[code] = {"key": secrets.token_urlsafe(16), "made": now, "students": {}, "joined": set(), "flagged": set(), "changes": 0, "exploring": {}, "people": {}, "teacher": teacher}
    save_classes()
    return {"code": code, "key": CLASSES[code]["key"], "owner": teacher}


@app.get("/class/{code}/key")
def class_key(code: str, teacher: str = Depends(teacher_only)):
    """Any signed-in teacher can open a class that is running, by its code (his words, 16 November 2026: "let me join ongoing class")."""
    c = CLASSES.get(code.strip().upper())
    if not c:
        raise HTTPException(404, "No class has that code")
    return {"code": code.strip().upper(), "key": c["key"], "owner": c.get("teacher", "")}


class Join(BaseModel):
    name: str
    pin: str


def _pin_hash(pin: str, salt: bytes) -> str:
    return salt.hex() + "." + hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 100_000).hex()


def student(code: str, name: str, token: str) -> dict:
    """The class, once the student's token checks out: the token is given at join and signs the class code and the name."""
    c = CLASSES.get(code.upper())
    if not c:
        raise HTTPException(404, "No class has that code")
    if name not in c["people"] or not hmac.compare_digest(token, _sign(f"student|{code.upper()}|{name}")):
        raise HTTPException(401, "Join the class again")
    return c


@app.post("/class/{code}/join")
def join_class(code: str, j: Join):
    c = CLASSES.get(code.strip().upper())
    if not c:
        raise HTTPException(404, "No class has that code")
    name, pin = j.name.strip()[:60], j.pin.strip()
    if not name:
        raise HTTPException(400, "A name is needed")
    if not (len(pin) == 4 and pin.isdigit()):
        raise HTTPException(400, "The PIN is four digits")
    person = c["people"].get(name)
    if person is None:
        if len(c["people"]) >= 300:
            raise HTTPException(400, "This class is full")
        person = c["people"][name] = {"pin": _pin_hash(pin, secrets.token_bytes(16)), "history": []}
    elif not person["pin"]:   # a teacher reset it
        person["pin"] = _pin_hash(pin, secrets.token_bytes(16))
    elif not hmac.compare_digest(_pin_hash(pin, bytes.fromhex(person["pin"].split(".")[0])), person["pin"]):
        time.sleep(1)   # slows guessing
        raise HTTPException(403, "Someone with that name is already in this class, with another PIN")
    c["joined"].add(name)
    save_classes()
    last = person["history"][-1]["design"] if person["history"] else None
    return {"code": code.strip().upper(), "name": name, "token": _sign(f"student|{code.strip().upper()}|{name}"), "design": last}


class Design(BaseModel):
    name: str
    token: str
    design: dict


@app.post("/class/{code}/design")
def save_design(code: str, d: Design):
    c = student(code, d.name, d.token)
    history = c["people"][d.name]["history"]
    now = time.time()
    if history and (now - history[-1]["at"] < VERSION_GAP or len(history) >= MAX_VERSIONS):
        history.pop()
    history.append({"at": now, "design": d.design})
    save_classes()
    return {"versions": len(history)}


@app.post("/class/{code}/flags")
def send_flags(code: str, f: Flags):
    name = f.name.strip()[:60]
    c = student(code, name, f.token)
    c["changes"] += f.changed
    if f.unusual:
        c["flagged"].add(name)
        c["students"][name] = {"name": name, "mechanics": f.mechanics, "unusual": f.unusual[:20], "at": time.time()}
    else:
        c["students"].pop(name, None)   # nothing unusual on the canvas: nothing about this student is kept
    save_classes()
    return {"ok": True}


class Explore(BaseModel):
    name: str
    token: str = ""
    on: bool


@app.post("/class/{code}/explore")
def explore(code: str, e: Explore):
    """A student starts or stops two hours of exploration time; only the end time is held, with the rest of the class."""
    name = e.name.strip()[:60]
    c = student(code, name, e.token)
    if e.on:
        c["exploring"][name] = time.time() + EXPLORE_LIFE
    else:
        c["exploring"].pop(name, None)
    save_classes()
    return {"until": c["exploring"].get(name)}


@app.delete("/class/{code}")
def end_class(code: str, key: str, teacher: str = Depends(teacher_only)):
    """Only the teacher who started a class, or an admin, can end it (his words, 16 November 2026: "only I can end class")."""
    c = CLASSES.get(code.upper())
    if c and c.get("teacher", teacher) != teacher and teacher not in ADMINS:
        raise HTTPException(403, "Only the teacher who started this class can end it")
    if c and secrets.compare_digest(key, c["key"]):
        del CLASSES[code.upper()]
        save_classes()
    return {"ok": True}


@app.get("/class/{code}/flags")
def read_flags(code: str, key: str, teacher: str = Depends(teacher_only)):
    c = CLASSES.get(code.upper())
    if not c or not secrets.compare_digest(key, c["key"]):
        raise HTTPException(404, "No class has that code and key")
    now = time.time()
    live = {n: t for n, t in c["exploring"].items() if t > now}
    return sorted(({**s, "exploring_until": live.get(s["name"])} for s in c["students"].values()), key=lambda s: s["at"], reverse=True)


@app.get("/class/{code}/overview")
def class_overview(code: str, key: str, teacher: str = Depends(teacher_only)):
    c = CLASSES.get(code.upper())
    if not c or not secrets.compare_digest(key, c["key"]):
        raise HTTPException(404, "No class has that code and key")
    return {"joined": len(c["joined"]), "changes": c["changes"], "flagged": len(c["flagged"]), "made": c["made"], "ends": c["made"] + CLASS_LIFE, "owner": c.get("teacher", "")}


class PinReset(BaseModel):
    name: str


@app.post("/class/{code}/reset-pin")
def reset_pin(code: str, key: str, r: PinReset, teacher: str = Depends(teacher_only)):
    """A student who forgot their PIN: the next time they join with their name, the PIN they type becomes their new one."""
    c = CLASSES.get(code.upper())
    if not c or not secrets.compare_digest(key, c["key"]) or r.name not in c["people"]:
        raise HTTPException(404, "No class has that code, key and student")
    c["people"][r.name]["pin"] = ""
    save_classes()
    return {"ok": True}


@app.get("/classes")
def all_classes(teacher: str = Depends(teacher_only)):
    """Every running class, for an admin only."""
    if teacher not in ADMINS:
        raise HTTPException(403, "Only an admin sees every class")
    return sorted(({"code": code, "owner": c.get("teacher", ""), "joined": len(c["joined"]), "made": c["made"]} for code, c in CLASSES.items()),
                  key=lambda c: c["made"], reverse=True)


@app.get("/class/{code}/history")
def class_history(code: str, key: str, teacher: str = Depends(teacher_only)):
    """Every student who joined, with each kept version of their design: its time, its blocks and its how-it-plays text."""
    c = CLASSES.get(code.upper())
    if not c or not secrets.compare_digest(key, c["key"]):
        raise HTTPException(404, "No class has that code and key")
    return sorted(({"name": n, "versions": [{"at": v["at"], "mechanics": v["design"].get("mechanics", {}), "narrative": v["design"].get("narrative", "")}
                                            for v in p["history"]]} for n, p in c["people"].items()), key=lambda s: s["name"].lower())


@app.get("/teacher")
def teacher(request: Request):
    page = "teacher.html" if signed_in(request) else "teacher-login.html"
    return HTMLResponse((STATIC_DIR / page).read_text(encoding="utf-8"), headers={"Cache-Control": "no-cache"})


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
