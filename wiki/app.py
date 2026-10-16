"""boardgameBuilder wiki: the tool's whole knowledge base, one page per entry, where signed-in people
record the checks they made under their own names.

A record is a person's verdict on one entry, kept with its evidence and the entry's text as it stood.
The code stores, shows and exports records. It never adds them up into a score for an entry or a count
for a person, and it never changes the knowledge base: folding a record back into the tool is done by
hand, in the tool's own files.

Anyone signed in can also propose a change to an existing entry, or a new entry (a triad, a conflict, a
block or a feeling), or a known game as a Markdown file in the shape known_games.py reads and writes. A proposal stays private to its author and the editors until an editor approves it.
An approved change shows on the entry at once, with the earlier text kept; an approved new entry appears
marked "proposed". Who approved it is kept but never shown or exported. pull.py carries approved
proposals into the tool's own files.

Environment:
  SECRET_KEY                                 signs the session cookie (required)
  GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET     sign-in with GitHub, if set
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET     sign-in with Google, if set
  OWNERS       who runs the wiki, space-separated, e.g. "github:somelogin google:someone@example.org";
               an owner is also an editor, and adds and removes editors and reviews applications to join
  ADMINS       editors to start with, in the same form; each is added to the editors on first sign-in,
               after which the community page decides (removing one there holds)
  DB_PATH      the SQLite file (default data/wiki.db beside this file)
  CORPUS_DIR   the tool's folder (default the folder above this one)
"""
import json
import os
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import markdown
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

import corpus

HERE = Path(__file__).resolve().parent
C = corpus.load()
ENTRIES = C["entries"]
DB_PATH = Path(os.environ.get("DB_PATH", HERE / "data" / "wiki.db"))
OWNERS = set(os.environ.get("OWNERS", "").split())
ADMINS = set(os.environ.get("ADMINS", "").split())

RECORD_KINDS = {
    "verified": "Verified: checked against a source",
    "validated": "Validated: tried with people at a table",
}
FINDINGS = ["holds", "partly holds", "does not hold"]
STATUS_WORDS = {
    "written-for-the-tool": "written for the tool",
    "exa-bgg-checked-20261016": "example games checked against BoardGameGeek's tags on 16 October 2026",
    "perplexity-bgg-verified": "assembled in April 2026; its example game was named then and not checked since",
    "perplexity-flagged-check": "assembled in April 2026 and flagged for checking",
    "drafted-20261016-unreviewed": "written on 16 October 2026 and not yet reviewed",
    "proposed-approved": "proposed by someone using the wiki and approved by an editor; not yet in the tool",
    "wiki-approved": "proposed on the wiki, approved by an editor, and added to the tool",
    "known-game": "a known game in the tool, to play with things at hand",
}
PROPOSAL_KINDS = {
    "triad": "A triad: what three blocks tend to produce together",
    "conflict": "A conflict: two blocks that pull against each other",
    "block": "A new block for one of the groups",
    "feeling": "A new feeling",
}
JUDGEMENTS = ["supports", "works against", "neither"]
# The tool's feedback describes tendencies and leaves judging to the designer; its build refuses these words
# (drafted/build.py), so a proposal carrying them is refused here before an editor has to read it.
VERDICT_WORDS = re.compile(r"\b(should|must|good|bad|better|worse|best|worst|great|well done|amazing|perfect|excellent|awesome)\b", re.I)

# --- Records ----------------------------------------------------------------

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
with sqlite3.connect(DB_PATH) as db:
    db.execute("""CREATE TABLE IF NOT EXISTS records (
        id INTEGER PRIMARY KEY, entry TEXT NOT NULL, kind TEXT NOT NULL, finding TEXT NOT NULL,
        evidence TEXT NOT NULL, suggestion TEXT NOT NULL, text_seen TEXT NOT NULL,
        user_id TEXT NOT NULL, user_name TEXT NOT NULL, user_handle TEXT NOT NULL,
        created TEXT NOT NULL, withdrawn TEXT, hidden TEXT, hidden_reason TEXT)""")
    db.execute("""CREATE TABLE IF NOT EXISTS proposals (
        id INTEGER PRIMARY KEY, key TEXT NOT NULL, kind TEXT NOT NULL, elements TEXT NOT NULL,
        grp TEXT NOT NULL, name TEXT NOT NULL, text TEXT NOT NULL, pros TEXT NOT NULL, cons TEXT NOT NULL,
        games TEXT NOT NULL, evidence TEXT NOT NULL, user_id TEXT NOT NULL, user_name TEXT NOT NULL,
        user_handle TEXT NOT NULL, judgement TEXT NOT NULL, created TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'pending',
        decided TEXT, decided_by TEXT, reason TEXT)""")
    db.execute("""CREATE TABLE IF NOT EXISTS people (
        user_id TEXT PRIMARY KEY, name TEXT NOT NULL, handle TEXT NOT NULL, first_signed_in TEXT NOT NULL)""")
    db.execute("""CREATE TABLE IF NOT EXISTS editors (
        user_id TEXT PRIMARY KEY, how TEXT NOT NULL, added TEXT NOT NULL, added_by TEXT NOT NULL, removed TEXT)""")
    # named: when an owner set this editor to be named on the about page, which they do once the editor has agreed
    if "named" not in [c[1] for c in db.execute("PRAGMA table_info(editors)")]:
        db.execute("ALTER TABLE editors ADD COLUMN named TEXT")
    # Names an owner typed in to show on the about page, for editors who have not signed in yet; no account is stored with them
    db.execute("CREATE TABLE IF NOT EXISTS named_people (name TEXT PRIMARY KEY, added TEXT NOT NULL)")
    # body: the Markdown file of a proposed game, kept whole so the tool can read it with known_games.from_markdown
    if "body" not in [c[1] for c in db.execute("PRAGMA table_info(proposals)")]:
        db.execute("ALTER TABLE proposals ADD COLUMN body TEXT")
    db.execute("""CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY, user_id TEXT NOT NULL, statement TEXT NOT NULL, created TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending', decided TEXT, reason TEXT)""")


def query(sql, *args):
    with sqlite3.connect(DB_PATH) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute(sql, args)]


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def entry_text(e):
    """The entry as a reader sees it, stored with each record so a later edit cannot change what was checked."""
    parts = [e["text"]]
    parts += [f"+ {p}" for p in e.get("pros", [])] + [f"- {c}" for c in e.get("cons", [])]
    if e.get("exemplars"):
        parts.append("Games: " + ", ".join(e["exemplars"]))
    return "\n".join(parts)


def lines(text):
    return [line.strip() for line in text.splitlines() if line.strip()]


def proposal_entry(p):
    els = json.loads(p["elements"])
    if p["kind"] == "game":
        g = corpus.from_markdown(p["body"])[0]
        e = {"key": p["key"], "kind": "game", "title": g["title"], "source": "proposed", "status": "proposed-approved",
             "elements": els, "text": g["intro"], "game": g, "checks": [],
             "proposal": {k: p[k] for k in ("user_name", "user_handle", "evidence", "created", "decided")}}
        e["search"] = " ".join([e["title"], e["text"]]).lower()
        return e
    if p["kind"] in ("triad", "conflict"):
        title = (" + " if p["kind"] == "triad" else " against ").join(C["display"][b] for b in els)
    else:
        title = p["name"]
    group = next((g["display"] for g in C["groups"] if g["id"] == p["grp"]), "")
    e = {"key": p["key"], "kind": p["kind"], "title": title, "source": "proposed", "status": "proposed-approved",
         "elements": els, "text": p["text"], "pros": lines(p["pros"]), "cons": lines(p["cons"]),
         "exemplars": lines(p["games"]), "removed": [], "unconfirmed": [], "checks": [], "group": group,
         "proposal": {k: p[k] for k in ("user_name", "user_handle", "evidence", "created", "decided")}}
    e["search"] = " ".join([title, e["text"], *e["pros"], *e["cons"]]).lower()
    return e


def apply_edit(p):
    """Show an approved change on its entry, keeping the text the tool has so the difference stays visible."""
    e = ENTRIES.get(p["key"])
    if not e:
        return
    e.setdefault("tool_text", entry_text(e))
    if e["kind"] == "game":
        e["game"] = corpus.from_markdown(p["body"])[0]
        e.update(title=e["game"]["title"], text=e["game"]["intro"])
    elif e["kind"] == "link":
        e["judgement"] = p["judgement"]
        e["text"] = corpus.link_text(*e["elements"], p["judgement"], C["display"])
    else:
        e["text"] = p["text"]
        if e["kind"] in ("pair", "triad"):
            e.update(pros=lines(p["pros"]), cons=lines(p["cons"]), exemplars=lines(p["games"]))
    e.setdefault("edits", []).append({k: p[k] for k in ("user_name", "user_handle", "evidence", "created", "decided")})
    e["search"] = " ".join([e["title"], e["text"], *e.get("pros", []), *e.get("cons", [])]).lower()


for _p in query("SELECT * FROM proposals WHERE status = 'approved' ORDER BY id"):
    if _p["kind"] == "edit":
        apply_edit(_p)
    else:
        ENTRIES.setdefault(_p["key"], proposal_entry(_p))


def states():
    """Per entry and kind of record: the finding all active records share, or 'records differ'."""
    out = {}
    for r in query("SELECT entry, kind, finding FROM records WHERE withdrawn IS NULL AND hidden IS NULL"):
        out.setdefault(r["entry"], {}).setdefault(r["kind"], set()).add(r["finding"])
    return {k: {kind: (f.pop() if len(f) == 1 else "records differ") for kind, f in v.items()} for k, v in out.items()}


# --- App and sign-in --------------------------------------------------------

app = FastAPI(title="boardgameBuilder wiki", docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(SessionMiddleware, secret_key=os.environ["SECRET_KEY"], same_site="lax",
                   https_only=os.environ.get("HTTPS_ONLY") == "1", max_age=60 * 60 * 24 * 30)
app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
templates = Jinja2Templates(directory=HERE / "templates")
templates.env.globals.update(DIMENSIONS=corpus.palette.DIMENSIONS, C=C, KINDS=corpus.KINDS, PLURAL=corpus.PLURAL, PROPOSAL_KINDS=PROPOSAL_KINDS, JUDGEMENTS=JUDGEMENTS, RECORD_KINDS=RECORD_KINDS, FINDINGS=FINDINGS,
                             STATUS_WORDS=STATUS_WORDS)
templates.env.filters["day"] = lambda iso: datetime.fromisoformat(iso).strftime("%-d %b %Y")

oauth = OAuth()
PROVIDERS = []
if os.environ.get("GITHUB_CLIENT_SECRET"):
    PROVIDERS.append("github")
    oauth.register("github", client_id=os.environ["GITHUB_CLIENT_ID"],
                   client_secret=os.environ["GITHUB_CLIENT_SECRET"],
                   authorize_url="https://github.com/login/oauth/authorize",
                   access_token_url="https://github.com/login/oauth/access_token",
                   api_base_url="https://api.github.com/")
if os.environ.get("GOOGLE_CLIENT_SECRET"):
    PROVIDERS.append("google")
    oauth.register("google", client_id=os.environ["GOOGLE_CLIENT_ID"],
                   client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
                   server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
                   client_kwargs={"scope": "openid profile email"})
templates.env.globals["PROVIDERS"] = PROVIDERS


def current(request):
    """The signed-in person, with editor rights read afresh from the editors table, so a change applies at once."""
    user = request.session.get("user")
    if not user:
        return None
    editor = query("SELECT 1 FROM editors WHERE user_id = ? AND removed IS NULL", user["id"])
    return {**user, "owner": bool(user.get("owner")), "admin": bool(user.get("owner") or editor)}


def execute(sql, *args):
    with sqlite3.connect(DB_PATH) as db:
        db.execute(sql, args)


def page(request, name, **ctx):
    return templates.TemplateResponse(request, name, {"user": current(request), **ctx})


@app.get("/login/{provider}")
async def login(request: Request, provider: str, next: str = "/"):
    if provider not in PROVIDERS:
        raise HTTPException(404)
    request.session["next"] = next if next.startswith("/") else "/"
    return await oauth.create_client(provider).authorize_redirect(request, request.url_for("auth", provider=provider))


@app.get("/auth/{provider}")
async def auth(request: Request, provider: str):
    if provider not in PROVIDERS:
        raise HTTPException(404)
    client = oauth.create_client(provider)
    try:
        token = await client.authorize_access_token(request)
    except OAuthError:
        # Usually a code already used by a repeated request; when that first request signed the person in, carry on.
        if request.session.get("user"):
            return RedirectResponse(quote(request.session.pop("next", "/"), safe="/:+"), status_code=303)
        return page(request, "message.html", title="Sign-in did not finish",
                    message="The sign-in did not complete. Please try again.")
    if provider == "github":
        u = (await client.get("user", token=token)).json()
        user = {"id": f"github:{u['id']}", "name": u.get("name") or u["login"], "handle": u["login"]}
        account = f"github:{u['login']}"
    else:
        u = token["userinfo"]
        user = {"id": f"google:{u['sub']}", "name": u.get("name") or "A Google account", "handle": ""}
        account = f"google:{u.get('email')}"  # read here to match OWNERS and ADMINS; never stored or shown
    user["owner"] = account in OWNERS
    execute("INSERT INTO people (user_id, name, handle, first_signed_in) VALUES (?,?,?,?) ON CONFLICT(user_id)"
            " DO UPDATE SET name = excluded.name, handle = excluded.handle", user["id"], user["name"], user["handle"], now())
    if account in ADMINS or user["owner"]:
        # Only the first time: once a row exists, the community page decides, so a removal holds.
        execute("INSERT OR IGNORE INTO editors (user_id, how, added, added_by) VALUES (?, 'settings', ?, 'settings')",
                user["id"], now())
    request.session["user"] = user
    return RedirectResponse(quote(request.session.pop("next", "/"), safe="/:+"), status_code=303)


@app.get("/logout")
async def logout(request: Request):
    request.session.pop("user", None)
    return RedirectResponse("/", status_code=303)


# --- Pages ------------------------------------------------------------------

@app.get("/")
async def home(request: Request):
    return page(request, "home.html", states=states())


@app.get("/about")
async def about(request: Request):
    named = query("""SELECT p.name FROM editors e JOIN people p ON p.user_id = e.user_id
                     WHERE e.named IS NOT NULL AND e.removed IS NULL ORDER BY e.named""")
    typed = query("SELECT name FROM named_people ORDER BY added")
    return page(request, "about.html", named=list(dict.fromkeys(n["name"] for n in named + typed)))


@app.get("/e/{key:path}")
async def entry(request: Request, key: str):
    e = ENTRIES.get(key)
    if not e:
        raise HTTPException(404)
    related = []
    if e["kind"] in ("block", "feeling"):
        own = e["elements"][0]
        related = [x for x in ENTRIES.values() if x["key"] != key and x["kind"] != e["kind"] and own in x["elements"]]
    records = query("SELECT * FROM records WHERE entry = ? ORDER BY id", key)
    return page(request, "entry.html", e=e, records=records, related=related, states=states(),
                current=entry_text(e))


@app.post("/e/{key:path}/record")
async def add_record(request: Request, key: str, kind: str = Form(...), finding: str = Form(...),
                     evidence: str = Form(...), suggestion: str = Form("")):
    user = current(request)
    e = ENTRIES.get(key)
    if not e:
        raise HTTPException(404)
    if not user:
        raise HTTPException(403, "Sign in to add a record.")
    evidence, suggestion = evidence.strip(), suggestion.strip()
    if kind not in RECORD_KINDS or finding not in FINDINGS or not evidence or len(evidence) > 4000 or len(suggestion) > 4000:
        raise HTTPException(400, "A record needs a kind, a finding and its evidence (up to 4,000 characters each).")
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT INTO records (entry, kind, finding, evidence, suggestion, text_seen,
                      user_id, user_name, user_handle, created) VALUES (?,?,?,?,?,?,?,?,?,?)""",
                   (key, kind, finding, evidence, suggestion, entry_text(e),
                    user["id"], user["name"], user["handle"], now()))
    return RedirectResponse(f"/e/{quote(key, safe=':+')}#records", status_code=303)


@app.post("/r/{rid}/withdraw")
async def withdraw(request: Request, rid: int):
    user = current(request) or {}
    r = (query("SELECT * FROM records WHERE id = ?", rid) or [None])[0]
    if not r or r["user_id"] != user.get("id"):
        raise HTTPException(403)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("UPDATE records SET withdrawn = ? WHERE id = ? AND withdrawn IS NULL", (now(), rid))
    return RedirectResponse(f"/e/{quote(r['entry'], safe=':+')}#records", status_code=303)


@app.post("/r/{rid}/hide")
async def hide(request: Request, rid: int, reason: str = Form(...)):
    user = current(request) or {}
    r = (query("SELECT * FROM records WHERE id = ?", rid) or [None])[0]
    if not r or not user.get("admin") or not reason.strip():
        raise HTTPException(403)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("UPDATE records SET hidden = ?, hidden_reason = ? WHERE id = ?", (now(), reason.strip()[:500], rid))
    return RedirectResponse(f"/e/{quote(r['entry'], safe=':+')}#records", status_code=303)


@app.get("/propose")
async def propose_form(request: Request):
    if not current(request):
        raise HTTPException(403, "Sign in to propose an entry.")
    return page(request, "propose.html", error="", form={})


@app.post("/propose")
async def propose(request: Request, kind: str = Form(...), blocks: list[str] = Form([]), grp: str = Form(""),
                  name: str = Form(""), text: str = Form(...), pros: str = Form(""), cons: str = Form(""),
                  games: str = Form(""), evidence: str = Form(...)):
    user = current(request)
    if not user:
        raise HTTPException(403, "Sign in to propose an entry.")
    name, text, evidence = name.strip(), text.strip(), evidence.strip()
    themes = next(g["blocks"] for g in C["groups"] if g["id"] == "theme")
    blocks = list(dict.fromkeys(b for b in blocks if b in C["display"] and b not in C["feelings"] and b not in themes))
    error, key = "", ""
    if kind not in PROPOSAL_KINDS:
        error = "Choose what kind of entry you are proposing."
    elif kind in ("triad", "conflict"):
        need = 3 if kind == "triad" else 2
        if len(blocks) != need:
            error = f"A {kind} needs exactly {need} different blocks; you chose {len(blocks)}."
        else:
            key = corpus._key(kind, blocks)
    elif not name or len(name) > 60:
        error = "Give the new block or feeling a name of up to 60 characters."
    elif kind == "block" and grp not in {g["id"] for g in C["groups"]}:
        error = "Choose the group the new block belongs to."
    else:
        key = f"{kind}:" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not error and key in ENTRIES:
        error = "That entry already exists. Open it and propose a change instead."
    if not error and query("SELECT id FROM proposals WHERE key = ? AND status = 'pending'", key):
        error = "Someone has already proposed that entry and it is waiting for an editor."
    if not error:
        error = text_problem(text, pros, cons, games, evidence)
    if error:
        form = dict(kind=kind, blocks=blocks, grp=grp, name=name, text=text, pros=pros, cons=cons, games=games, evidence=evidence)
        return page(request, "propose.html", error=error, form=form)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT INTO proposals (key, kind, elements, grp, name, text, pros, cons, games, evidence,
                      user_id, user_name, user_handle, judgement, created) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,'',?)""",
                   (key, kind, json.dumps(blocks if kind in ("triad", "conflict") else [key.split(":", 1)[1]]),
                    grp if kind == "block" else "", name if kind in ("block", "feeling") else "", text,
                    pros.strip(), cons.strip(), games.strip(), evidence, user["id"], user["name"], user["handle"], now()))
    return RedirectResponse("/proposals", status_code=303)


def text_problem(text, pros, cons, games, evidence):
    if not text or not evidence or max(map(len, (text, pros, cons, games, evidence))) > 4000:
        return "A proposal needs its text and how you know (up to 4,000 characters each)."
    words = sorted({w.lower() for w in VERDICT_WORDS.findall(" ".join((text, pros, cons)))})
    if words:
        return ("The entries describe what a combination tends to do and leave the judging to the designer, so they "
                "avoid words like " + ", ".join(f"'{w}'" for w in words) + ". Say what happens instead.")
    return ""


@app.get("/edit/{key:path}")
async def edit_form(request: Request, key: str):
    e = ENTRIES.get(key)
    if not e:
        raise HTTPException(404)
    if e["kind"] == "game":
        return RedirectResponse("/propose-game", status_code=303)
    if not current(request):
        raise HTTPException(403, "Sign in to propose a change.")
    form = dict(text=e["text"], pros="\n".join(e.get("pros", [])), cons="\n".join(e.get("cons", [])),
                games="\n".join(e.get("exemplars", [])), judgement=e.get("judgement", ""), evidence="")
    return page(request, "edit.html", e=e, form=form, error="")


@app.post("/edit/{key:path}")
async def edit(request: Request, key: str, text: str = Form(""), pros: str = Form(""), cons: str = Form(""),
               games: str = Form(""), judgement: str = Form(""), evidence: str = Form(...)):
    user = current(request)
    e = ENTRIES.get(key)
    if not e:
        raise HTTPException(404)
    if not user:
        raise HTTPException(403, "Sign in to propose a change.")
    text, evidence = text.strip(), evidence.strip()
    if e["source"] == "drafted":
        games = ""  # drafted entries name no games until one has been checked and the entry moves to the curated part
    if e["kind"] == "link":
        error = "" if judgement in JUDGEMENTS and evidence else "Choose the judgement and say how you know."
        text = corpus.link_text(*e["elements"], judgement, C["display"]) if not error else text
    else:
        error = text_problem(text, pros, cons, games, evidence)
        if not error and e["source"] == "drafted" and e["kind"] == "pair" and (len(lines(pros)), len(lines(cons))) != (2, 2):
            error = "Drafted pairs keep exactly two points for what it brings and two for what it costs."
    if not error and (text, lines(pros), lines(cons), lines(games), judgement) == (
            e["text"], e.get("pros", []), e.get("cons", []), e.get("exemplars", []), e.get("judgement", "")):
        error = "Nothing was changed."
    if error:
        form = dict(text=text, pros=pros, cons=cons, games=games, judgement=judgement, evidence=evidence)
        return page(request, "edit.html", e=e, form=form, error=error)
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT INTO proposals (key, kind, elements, grp, name, text, pros, cons, games, evidence,
                      user_id, user_name, user_handle, judgement, created) VALUES (?,'edit',?,'','',?,?,?,?,?,?,?,?,?,?)""",
                   (key, json.dumps(e["elements"]), text, pros.strip(), cons.strip(), games.strip(), evidence,
                    user["id"], user["name"], user["handle"], judgement, now()))
    return RedirectResponse("/proposals", status_code=303)


GAME_TEMPLATE = {
    "title": "Name of the game — a few words on what it does", "parent_game": "where it comes from: a folk game, a published game, or your own",
    "players": "2–4 players", "duration": "5–10 min", "credits": "who made it, as far as anyone knows; Traditional if nobody does",
    "intro": "Two or three sentences on what playing it is like.", "equipment": ["what you need, one thing per line"],
    "steps": [{"n": 1, "title": "Set up", "body": "What to lay out, and who starts."}, {"n": 2, "title": "A turn", "body": "What a player does on their turn."},
              {"n": 3, "title": "The end", "body": "When it ends, who wins, and what happens on a tie."}],
    "what_to_notice": ["a question to talk about after playing"], "sources": ["a link to where the rules are written down, if they are"],
    "design": {"core-mechanic": ["push-your-luck"], "victory-condition": "race-to-finish"}}


def game_slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.split(" — ")[0].lower()).strip("-")[:60]


@app.get("/games/{gid}.md")
async def game_file(gid: str):
    """A known game as a file: Open game in the tool puts its blocks on the canvas, and Propose a game takes it back."""
    if gid == "template":
        g = GAME_TEMPLATE
    else:
        e = ENTRIES.get(f"game:{gid}")
        if not e:
            raise HTTPException(404)
        g = e["game"]
    return Response(corpus.to_markdown(g, C["version"]), media_type="text/markdown; charset=utf-8",
                    headers={"Content-Disposition": f'attachment; filename="{gid}.md"'})


@app.get("/propose-game")
async def propose_game_form(request: Request):
    if not current(request):
        raise HTTPException(403, "Sign in to propose a game.")
    return page(request, "propose_game.html", error="", pasted="", evidence="")


@app.post("/propose-game")
async def propose_game(request: Request, file: UploadFile | None = File(None), pasted: str = Form(""), evidence: str = Form(...)):
    user = current(request)
    if not user:
        raise HTTPException(403, "Sign in to propose a game.")
    body = (await file.read(60_001)).decode("utf-8", "replace") if file and file.filename else pasted
    body, evidence = body.strip(), evidence.strip()
    g, problem = corpus.from_markdown(body)
    error = "Choose a file or paste one." if not body else (f"The file could not be read: {problem}." if problem else "")
    key = f"game:{game_slug(g['title'])}"
    if not error and len(body) > 60_000:
        error = "The file is longer than 60,000 characters."
    if not error and g["title"] == GAME_TEMPLATE["title"]:
        error = "The file is still the template. Write your game into it first."
    if not error:
        error = text_problem(g["intro"], "\n".join(g["what_to_notice"]), "", "", evidence)
    if not error and query("SELECT id FROM proposals WHERE key = ? AND status = 'pending'", key):
        error = "A proposal for a game with that name is already waiting for an editor."
    if error:
        return page(request, "propose_game.html", error=error, pasted=body, evidence=evidence)
    kind = "edit" if key in ENTRIES else "game"
    blocks = [b for v in g["design"].values() for b in (v if isinstance(v, list) else [v])]
    with sqlite3.connect(DB_PATH) as db:
        db.execute("""INSERT INTO proposals (key, kind, elements, grp, name, text, pros, cons, games, evidence,
                      user_id, user_name, user_handle, judgement, created, body) VALUES (?,?,?,'',?,?,'','','',?,?,?,?,'',?,?)""",
                   (key, kind, json.dumps(blocks), g["title"], g["intro"], evidence, user["id"], user["name"], user["handle"], now(), body))
    return RedirectResponse("/proposals", status_code=303)


@app.get("/proposals")
async def proposals(request: Request):
    user = current(request)
    if not user:
        raise HTTPException(403, "Sign in to see proposals.")
    if user.get("admin"):
        rows = query("SELECT * FROM proposals ORDER BY status = 'pending' DESC, id DESC")
    else:
        rows = query("SELECT * FROM proposals WHERE user_id = ? ORDER BY id DESC", user["id"])
    for r in rows:
        r["blocks"] = [C["display"].get(b, b) for b in json.loads(r["elements"])] if r["kind"] in ("triad", "conflict") else []
        r["entry"] = ENTRIES.get(r["key"])
    return page(request, "proposals.html", rows=rows)


@app.post("/p/{pid}/{decision}")
async def decide(request: Request, pid: int, decision: str, reason: str = Form("")):
    user = current(request) or {}
    p = (query("SELECT * FROM proposals WHERE id = ? AND status = 'pending'", pid) or [None])[0]
    if not user.get("admin") or not p or decision not in ("approve", "reject"):
        raise HTTPException(403)
    if decision == "reject" and not reason.strip():
        raise HTTPException(400, "Say why, so the person who proposed it can read the reason.")
    if decision == "approve" and p["kind"] != "edit" and p["key"] in ENTRIES:
        raise HTTPException(409, "That entry exists now; reject this proposal and point to it.")
    status = "approved" if decision == "approve" else "rejected"
    with sqlite3.connect(DB_PATH) as db:
        db.execute("UPDATE proposals SET status = ?, decided = ?, decided_by = ?, reason = ? WHERE id = ?",
                   (status, now(), user["id"], reason.strip()[:1000], pid))
    if status == "approved":
        p = query("SELECT * FROM proposals WHERE id = ?", pid)[0]
        if p["kind"] == "edit":
            apply_edit(p)
        else:
            ENTRIES[p["key"]] = proposal_entry(p)
    return RedirectResponse("/proposals", status_code=303)


@app.get("/apply")
async def apply_form(request: Request):
    user = current(request)
    if not user:
        raise HTTPException(403, "Sign in to apply.")
    mine = query("SELECT * FROM applications WHERE user_id = ? ORDER BY id DESC", user["id"])
    return page(request, "apply.html", mine=mine, error="")


@app.post("/apply")
async def apply(request: Request, statement: str = Form(...)):
    user = current(request)
    if not user:
        raise HTTPException(403, "Sign in to apply.")
    statement = statement.strip()
    mine = query("SELECT * FROM applications WHERE user_id = ? ORDER BY id DESC", user["id"])
    error = ""
    if user["admin"]:
        error = "You are already an editor."
    elif any(a["status"] == "pending" for a in mine):
        error = "Your application is already waiting."
    elif not statement or len(statement) > 2000:
        error = "Say in up to 2,000 characters why you would like to moderate and what you know of games."
    if error:
        return page(request, "apply.html", mine=mine, error=error)
    execute("INSERT INTO applications (user_id, statement, created) VALUES (?,?,?)", user["id"], statement, now())
    return RedirectResponse("/apply", status_code=303)


def owner_only(request):
    user = current(request)
    if not user or not user["owner"]:
        raise HTTPException(403)
    return user


@app.get("/community")
async def community(request: Request):
    owner_only(request)
    people = query("""SELECT p.*, e.how, e.added, e.removed, e.named FROM people p LEFT JOIN editors e ON e.user_id = p.user_id
                      ORDER BY p.name COLLATE NOCASE""")
    applications = query("""SELECT a.*, p.name, p.handle FROM applications a JOIN people p ON p.user_id = a.user_id
                            ORDER BY a.status = 'pending' DESC, a.id DESC""")
    return page(request, "community.html", people=people, applications=applications,
                typed_names=query("SELECT name FROM named_people ORDER BY added"),
                settings_editors=sorted(ADMINS - OWNERS))


@app.post("/community/editor")
async def set_editor(request: Request, user_id: str = Form(...), action: str = Form(...)):
    owner = owner_only(request)
    if not query("SELECT 1 FROM people WHERE user_id = ?", user_id) or action not in ("add", "remove"):
        raise HTTPException(400)
    if action == "add":
        execute("""INSERT INTO editors (user_id, how, added, added_by) VALUES (?, 'owner', ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET how = 'owner', added = excluded.added,
                   added_by = excluded.added_by, removed = NULL""", user_id, now(), owner["id"])
    elif user_id != owner["id"]:
        execute("UPDATE editors SET removed = ? WHERE user_id = ?", now(), user_id)
    return RedirectResponse("/community", status_code=303)


@app.post("/community/named")
async def set_named(request: Request, user_id: str = Form(...), named: str = Form(...)):
    owner_only(request)
    execute("UPDATE editors SET named = ? WHERE user_id = ? AND removed IS NULL", now() if named == "yes" else None, user_id)
    return RedirectResponse("/community", status_code=303)


@app.post("/community/named-name")
async def set_named_name(request: Request, name: str = Form(...), action: str = Form(...)):
    owner_only(request)
    name = " ".join(name.split())[:80]
    if not name or action not in ("add", "remove"):
        raise HTTPException(400)
    if action == "add":
        execute("INSERT OR IGNORE INTO named_people (name, added) VALUES (?, ?)", name, now())
    else:
        execute("DELETE FROM named_people WHERE name = ?", name)
    return RedirectResponse("/community", status_code=303)


@app.post("/community/application/{aid}/{decision}")
async def decide_application(request: Request, aid: int, decision: str, reason: str = Form("")):
    owner = owner_only(request)
    a = (query("SELECT * FROM applications WHERE id = ? AND status = 'pending'", aid) or [None])[0]
    if not a or decision not in ("accept", "decline"):
        raise HTTPException(400)
    if decision == "decline" and not reason.strip():
        raise HTTPException(400, "Say why, so the person who applied can read the reason.")
    execute("UPDATE applications SET status = ?, decided = ?, reason = ? WHERE id = ?",
            "accepted" if decision == "accept" else "declined", now(), reason.strip()[:1000], aid)
    if decision == "accept":
        execute("""INSERT INTO editors (user_id, how, added, added_by) VALUES (?, 'application', ?, ?)
                   ON CONFLICT(user_id) DO UPDATE SET how = 'application', added = excluded.added,
                   added_by = excluded.added_by, removed = NULL""", a["user_id"], now(), owner["id"])
    return RedirectResponse("/community", status_code=303)


@app.get("/list/{kind}")
async def listing(request: Request, kind: str, source: str = "", state: str = ""):
    if kind not in corpus.KINDS:
        raise HTTPException(404)
    st = states()
    rows = [e for e in ENTRIES.values() if e["kind"] == kind and (not source or e["source"] == source)
            and (state != "none" or e["key"] not in st)]
    return page(request, "list.html", kind=kind, rows=rows, states=st, source=source, state=state)


@app.get("/search")
async def search(request: Request, q: str = ""):
    words = q.lower().split()
    rows = [e for e in ENTRIES.values() if words and all(w in e["search"] for w in words)]
    return page(request, "list.html", kind="", rows=rows, states=states(), q=q, source="", state="")


@app.get("/records")
async def records(request: Request):
    rows = query("SELECT * FROM records WHERE hidden IS NULL ORDER BY id DESC LIMIT 500")
    return page(request, "records.html", rows=rows)


@app.get("/notes/{name}")
async def note(request: Request, name: str):
    n = C["notes"].get(name)
    if not n:
        raise HTTPException(404)
    return page(request, "note.html", title=n["title"],
                body=markdown.markdown(n["markdown"], extensions=["tables"]))


@app.get("/export.json")
async def export():
    """Every record and approved proposal, so anyone can keep a copy. Withdrawn records are marked; hidden ones keep
    their reason, not their text. Pending and rejected proposals, and who decided any proposal, are left out."""
    return JSONResponse({"exported": now(), "records": query(
        "SELECT id, entry, kind, finding, CASE WHEN hidden IS NULL THEN evidence ELSE '' END AS evidence,"
        " CASE WHEN hidden IS NULL THEN suggestion ELSE '' END AS suggestion, text_seen, user_id, user_name,"
        " user_handle, created, withdrawn, hidden, hidden_reason FROM records ORDER BY id"),
        "approved_proposals": query(
        "SELECT id, key, kind, elements, grp, name, text, pros, cons, games, evidence, user_id, user_name,"
        " user_handle, judgement, created, decided, body FROM proposals WHERE status = 'approved' ORDER BY id")})


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.environ.get("HOST", "127.0.0.1"), port=int(os.environ.get("PORT", 8788)),
                access_log=False, proxy_headers=True, forwarded_allow_ips="*")
