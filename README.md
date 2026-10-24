# boardgameBuilder

[![Live](https://img.shields.io/badge/live-boardgame.blevn.xyz-2e7d32?style=flat-square)](https://boardgame.blevn.xyz)
[![Version](https://img.shields.io/badge/version-0.14.2-555555?style=flat-square)](CHANGELOG.md)
[![Licence: AGPL v3](https://img.shields.io/badge/licence-AGPL--3.0-blue?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776ab?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-backend-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![No AI at runtime](https://img.shields.io/badge/AI%20at%20runtime-none-555555?style=flat-square)](#how-the-feedback-is-made)
[![No analytics](https://img.shields.io/badge/analytics-none-555555?style=flat-square)](#privacy)
[![No login](https://img.shields.io/badge/login-none-555555?style=flat-square)](https://boardgame.blevn.xyz)
[![Blocks](https://img.shields.io/badge/blocks-86%20%2B%2015%20feelings-c75b39?style=flat-square)](#the-blocks)
[![Coverage](https://img.shields.io/badge/two--block%20combinations%20with%20feedback-3419%20of%203419-c75b39?style=flat-square)](#checks)
[![Example games](https://img.shields.io/badge/example%20games-checked%20against%20BoardGameGeek-ff5100?style=flat-square)](#example-games)
[![Docker](https://img.shields.io/badge/docker-ready-2496ed?style=flat-square&logo=docker&logoColor=white)](#run-it-with-docker)

A small browser tool for designing a board game by putting blocks together and reading what the combination tends to produce.

**Try it:** https://boardgame.blevn.xyz · **Check its knowledge base:** https://boardgame-wiki.blevn.xyz · **Its syntax:** https://syntax.prayasabhinav.net/board-game/ · **My work:** https://prayasabhinav.net · **Write to me:** me@prayasabhinav.net

![boardgameBuilder with feelings, mechanics and Simulation blocks on the canvas and a round of feedback](docs/screenshot.jpg)

---

## Contents

1. [What it does](#what-it-does)
2. [Using it](#using-it)
3. [Playing it on screen](#playing-it-on-screen)
4. [The blocks](#the-blocks)
5. [Simulation blocks for serious games](#simulation-blocks-for-serious-games)
6. [How the feedback is made](#how-the-feedback-is-made)
7. [Example games](#example-games)
8. [Known games, part tests and block questions](#known-games-part-tests-and-block-questions)
9. [Run it on your own machine](#run-it-on-your-own-machine)
10. [Run it with Docker](#run-it-with-docker)
11. [Changing the knowledge base](#changing-the-knowledge-base)
12. [The wiki](#the-wiki)
13. [Checks](#checks)
14. [Files](#files)
15. [Privacy](#privacy)
16. [Status and how to help](#status-and-how-to-help)
17. [References](#references)
18. [Licence](#licence)

---

## What it does

The screen has three columns.

- **Left: the palette.** The feelings at the top, then eight groups of blocks for the parts of a game. A search box above them shows only the blocks whose name or description holds the words typed, or a whole group when its name is typed; Esc clears it.
- **Centre: the canvas.** A shelf for the feelings you want the game to have, one slot for each group of blocks, and a box below them for writing how the game plays.
- **Right: the feedback.** Each press of **Iterate** reads the canvas and says what the combination tends to produce, what it brings, its trade-offs, any clash between blocks, whether the blocks serve the feelings you picked, and real games built on something similar where one has been checked.

You change a block, press Iterate again and see what moved. **Mark complete** writes a closing summary and locks the canvas.

## Using it

1. Drag one or more **feelings** (tense, clever, together, sneaky…) onto the shelf at the top.
2. Drag **blocks** into the slots. A block only fits its own slot.
3. **Core mechanic**, **Timing** and **Simulation** hold as many different blocks as your game needs, each once. Every other slot holds one, and a new block replaces the old one.
4. Write **how the game plays** in the box under the slots. Type **@** to tag a block on the canvas: the box it sits in is tagged with it, the tags are listed under the text by box (*Core mechanic › roll and move*), a tagged block is filled in, with a dark border, and its slot carries an **@** at its corner. A tag whose block has left the canvas is listed as no longer on it.
5. Press **Iterate**. Each press is one turn of design; the panel keeps the history.
6. Press the **?** on any block for a short description and a drawing. The feelings have none.
7. When a block has questions about how it works in your game, they open as you drop it; answer any you can, and change them later from the line under the block.
8. **Test parts**, beside the feedback, has short tests of one block, or two together, to play with things at hand; say how each felt.
9. Press **Play** to play the design on screen (see [Playing it on screen](#playing-it-on-screen)).
10. Press **Mark complete** for the summary, which ends with your answers and test notes in your own terms. **Start fresh** in the header clears everything.

Your design is kept in your browser, so a refresh does not lose it. **Save game** in the header downloads it as a Markdown file: the feelings, the blocks, how the game plays with its tags by box, and every turn of feedback, readable on its own, ending with the saved state. **Open game** reads that file back, in any browser or on another day, and carries on from the same turn. The steps also open on a first visit, and **How it works** in the header shows them again.

Every view has its own address, so it can be linked, reloaded and reached with Back: `#games` for the known games, `#games/pig` for one of them, `#games/pig/watch` to watch it, `#how-it-works`, `#blocks/push-your-luck` for a block, `#tests` for the part tests, and `#play` to play the design on screen.

It works for one person on a laptop and for a group around one big screen.

## Playing it on screen

**Play**, beside Iterate, plays the design on the canvas. Each block the screen can play has a rule written for it in `static/play-engine.js`, and the rules join into one game: a turn is one move, chosen from the moves the blocks offer, and the rounds, the scoring and the end follow from the victory condition. Nothing is generated; the same choices and the same dice give the same game.

55 of the 86 blocks have a rule, among them rolling and moving, pushing your luck, drafting, bidding, placing workers and pieces, patterns, hands and tricks, sets, tiles, a shared resource that refills the way a real one does, a pressure the team has to hold back, a hidden card to work out and a secret rule to find. The 12 themes name the pieces. The other 19 happen between people, such as negotiation, role-play, playing in silence or a debrief: the setup lists them under *You play at the table*, each with what to do, and they stay beside the board while you play. A few get help from the screen: it can move the points a negotiation agreed, and it asks the debrief questions at the end.

Each seat is a **person** or **fixed rules**. A fixed-rule player is played by the screen and always takes the move its rule values most, with a little chance between moves of nearly equal value. It fills a table; it does not play the way people do. When players keep secrets (hidden hands, secret goals, a traitor, secret sides, bluffs), the screen hides them and asks for the screen to be passed before each person's move. With **no turns**, whoever presses their key first (A, L, Z, M or Q, or a tap on their name) makes the next move. **Timed turns** give each move a clock, which shortens if the game is **accelerated**; when it runs out, a move is made at random. **Sedated** holds every move for a breath first.

The closing screen gives the result and the scores and, when the canvas has the blocks for them, what the rules rewarded, the debrief questions, and the feelings you chose with the question of whether the game felt that way. With **irreversible change**, the shared resource stays where it ended for the next game in the same browser.

**Full screen** gives the table the whole screen, for a group around one display. **Share link** gives an address that carries the design itself: the blocks and your answers to their questions. Whoever opens it gets the same game ready to play, and their own canvas stays as it is.

A share link also carries questions for whoever plays it, which makes it a playtest. **Share link** opens them for editing above the address: five to start with (what the players spent their turns on, a moment that needed thought, whether the result came from choices or luck, which rule they would change, and, if you chose feelings, whether it felt that way), each one changeable or removable, up to twelve. The address changes as you edit. The player sees the questions before starting and answers them on the closing screen; **Copy my answers** puts the answers, the blocks, the result and everything that happened in the game into one text to send back however they like. Nothing is sent or kept by the tool.

## The blocks

| Group | Blocks | Slot holds |
|---|---|---|
| Core mechanic | roll and move, drafting, bidding, push your luck, area control, worker placement, pattern building, hand management, trick-taking, negotiation, set collection, tile placement, call and response, playing in silence, change the rules, role-play, dexterity, drawing the map | many |
| Victory condition | race to finish, most points, last standing, cooperative survival, shared objective, hidden personal goal, narrative completion, no objective, set your own goal, one loser, keep the game going, cannot be won | one |
| Player interaction | solo in parallel, direct confrontation, indirect via board, fully cooperative, semi-cooperative, team vs team, traitor, playing by letter, absent player, game master, public game | one |
| Chance or skill | mostly chance, chance with mitigation, skill with luck, mostly skill, chance read as a sign, attunement, dice tell the story | one |
| Theme | abstract, historical, fantasy, science fiction, everyday life, absurd, educational, real-world issue, poetic, ritual or sacred, mortality and loss, war and conquest | one |
| Information visibility | full information, hidden hands, hidden identity, deduction, bluffing, rules you discover, one knows, cannot say, map revealed as you go | one |
| Timing | take turns, everyone at once, no turns, timed turns, real-time span, sedated, accelerated | many |
| Simulation | model a system, stakeholder roles, shared resource, delayed effects, try a rule, debrief, irreversible change, rules make an argument, stakes outside the game, points stand for values, rehearse a future | many |

Fourteen of the blocks, from role-play to rehearse a future, come from ideas of Dhruv Jani's; the wiki credits him on each of their entries. Where each of the 31 blocks added on 16 October 2026 came from, with references checked against Crossref, is in [`docs/block-sources.md`](docs/block-sources.md).

**Feelings (15):** excited, clever, silly, tense, together, sneaky, lucky, in charge, surprised, thoughtful, fast, unfair in a fun way, careful, daring, friendly.

Which slots stack is a field on each group in `palette.py` (`"multi": True`); the page reads it from there.

## Simulation blocks for serious games

These are for games that model a real problem so that the people playing can work on it: a shared water supply, unequal starting points, a rule nobody has tried yet.

| Block | What it means for the players |
|---|---|
| model a system | The board works like a real system, so a move has the effect it would have in life. |
| stakeholder roles | Each player plays a real group with its own needs. |
| shared resource | Everyone draws from one limited thing; taking too much leaves less for all. |
| delayed effects | A choice shows its effect only rounds later. |
| try a rule | Players agree a rule for everyone and play on to see what it changes. |
| debrief | After play, players compare what happened with the real problem. |

I checked the six against the literature before building them. Roles, the model, policies and the debriefing are among the elements Duke lists for a gaming-simulation (Duke, 2011). Games used to test a draft regulation show consequences that in real life arrive with a long delay, and let people try a rule before it applies (Olejniczak, Wolański and Widawski, 2018). The shared resource is the common-pool resource game, with four decades of experiments behind it (Malézieux and Spiegelman, 2025). Villages in Andhra Pradesh played collective-action games about their groundwater, followed by a community debrief, and more of them took up water registers and rules afterwards than comparable villages (Meinzen-Dick et al., 2018). Role-play is at the centre of serious games for natural resource management (Edwards et al., 2019), and the debriefing is where play is connected back to the real situation (Peters and Vissers, 2004). The debrief block's four questions are Duke's: what happened, why, how it compares with the real world, and what would happen if something changed.

## How the feedback is made

No AI model runs while you use the tool, and nothing is generated on the fly. The same canvas always gives the same text.

```
You drag blocks onto the canvas
        ↓
rules.py matches the canvas against the knowledge base
  (pairs, triads, conflicts, feelings, theme lines)
        ↓
templates.py joins the matched entries' own sentences,
  using the fixed joining phrases in bridges.py
        ↓
The paragraph appears in the right-hand panel
```

The judgement (which blocks work together, what they tend to produce, what clashes, which feelings a block serves) lives in the knowledge base, where anyone can read and change it. The code only finds the matching entries and joins their sentences. `bridges.py` holds the joining phrases, with a few versions of each, chosen by the sentence they introduce.

The knowledge base has two parts:

- **`interactions.json`, the curated part:** 51 pairs, 15 triads, 5 conflicts and 15 feelings, each with a tendency, pros, cons and, where checked, example games. It was assembled in April 2026 with Perplexity search and BoardGameGeek, then checked again in October 2026 (see [Example games](#example-games)).
- **`interactions-drafted.json`, the drafted part:** 2,481 more pairs so that every combination of blocks has an entry, a line for each of the 12 themes, and a judgement for every feeling against every block (supports, works against, or neither). Every drafted entry is marked `drafted-20261016-unreviewed`, names no games, and loads after the curated ones, so a curated entry is always found first.

Themes are treated as colour, not mechanics: each theme has one line about what it adds, and themes are not paired with other blocks.

## Example games

Example games appear at the end of the feedback ("Games that do something like this…") only when a curated pair or triad is on the canvas. The drafted entries name none, because a claim that a real game uses two mechanisms has to be checked first.

In October 2026 every example game in the curated pairs and triads was checked against its full BoardGameGeek tag list. A game was removed when it lacks a mechanism it was named for, using tags BoardGameGeek applies reliably, or when a *full information* claim met a hidden-information tag or rule. 26 games were removed this way, each with its reason kept in the entry's `exemplars_removed`; one (Skull) is kept and marked in `exemplars_unconfirmed`; 60 of the 66 entries still name at least one game. The rule is in `drafted/bgg_check.py`, the tags in `drafted/bgg-tags.json` and every verdict in `drafted/bgg-verdicts.json`.

## Known games, part tests and block questions

Three things carried over on 16 October 2026 from an April 2026 prototype of this tool, edited before use:

- **Known games** in the header lists 47 short games to play with paper, dice, coins or cards, each chosen for what it shows a designer: seven made for the April prototype (Pig, a small Hanabi, a paper auction and others), 38 classic, traditional and designed games (among them Eleusis, Nomic, The Mind, Sprouts, Hex, Aadu Puli Attam, Moksha Patam, the Royal Game of Ur, Mendikot and Set), and two games of mine, All or Nothing and 3 Quarters. Each card opens with **What it shows a designer**, the idea that playing it makes felt. Each has its credits (who made it where that is on record, *Traditional* where nobody is, and what this version changes), illustrated steps that say who starts, how it ends and what happens on a tie, things to talk about afterwards, and the blocks it is made of. Some also have an animation of the game being played, followed by questions: questions about what happened are marked right or wrong; questions about what a designer would change have no right answer and are left to talk about. **Download as a design** gives the game as a Markdown file, and **Open game** puts its blocks on the canvas to design from. Nothing is locked: designing works whether or not a game has been played. The games are in `games.json`, and `known_games.py` writes and reads their files. The rules of the classic games follow the sources listed with each; each game's blocks were checked against its BoardGameGeek tags where it has an entry (`drafted/bgg_check.py`). Anyone signed in to the wiki can propose a new game as a file in the same shape.
- **Test parts** holds a short test for thirteen blocks, and three tests of two blocks together, in `part-tests.json`. What players say about a test (how it felt, whether it matched what they wanted, one thing they would change) is kept with the design.
- **Block questions**, in `block-questions.json`, ask how 25 of the blocks work in this game: how much a bust costs in push your luck, how big the hands are in hand management. The answers are the designers' own. The closing summary says them back, with the test notes, in fixed words; they add no knowledge-base claim and change none of the feedback.

All three are kept in the saved Markdown file, and none of them uses a model.

## Run it on your own machine

You need Python 3.10 or newer.

```bash
git clone https://github.com/prayasabhinav/boardgame-builder.git
cd boardgame-builder
./start.sh
```

Then open http://127.0.0.1:8787. The first run creates a private Python environment in the folder (`.venv-darwin/` or `.venv-linux/`) and installs three packages; later runs start in a second or two. `Ctrl + C` stops it.

To use another port: `PORT=9001 ./start.sh`. If the script is not executable, run `bash start.sh`.

No key or account is needed. Nothing leaves your machine apart from the page loading its fonts from Google Fonts.

## Run it with Docker

```bash
docker build -t boardgame-builder .
docker run -p 8080:80 boardgame-builder
```

Then open http://127.0.0.1:8080. The container listens on port 80, writes nothing to disk and needs no environment variables. `captain-definition` is there for CapRover, if that is how you deploy.

## Changing the knowledge base

- **Curated entries:** edit `interactions.json` directly.
- **Drafted entries:** edit the plain-text files in `drafted/` and rebuild:
  - pairs, one per line: `block-a+block-b | tendency | pro | pro | con | con`
  - `drafted/themes.txt`: `theme-id | sentence`
  - `drafted/feelings.txt`: `feeling | + blocks it supports | - blocks it works against` (every other block is judged *neither*)

  ```bash
  python drafted/build.py
  ```

  The build refuses a duplicate, an unknown block, a drafted feeling link that contradicts a curated one, and words from a short list of verdicts (good, bad, best, should, must and the like), because the feedback describes tendencies and leaves the judging to the designer.
- **Joining phrases:** edit `bridges.py`.
- **Block descriptions and drawings** (the **?** button): `block_meta.py`.
- **Groups and blocks:** `palette.py`. A new block needs a description in `block_meta.py`, a display name in `templates.py`, and pair entries so `check.py` still passes.

## The wiki

Every entry in the knowledge base is also on a public wiki, https://boardgame-wiki.blevn.xyz, one page per entry. Anyone can read it. People who sign in with GitHub or Google can record a check under their own name (verified against a source, or validated by trying it with people at a table), propose a change to an entry, or propose a new triad, conflict, block or feeling. Proposals wait for an editor, and anyone can apply to become one from the wiki (sign in, then *Join the editors*). Approved proposals reach this repository and the live tool by themselves: every half hour a GitHub Action runs `wiki/pull.py`, rebuilds the drafted entries, runs `check.py`, and only if the check passes commits the change here and redeploys the tool and the wiki (`.github/workflows/wiki-sync.yml`). A change that breaks the check stops there and goes nowhere. The wiki's code and how to run your own are in [`wiki/`](wiki/README.md).

## Checks

```bash
python check.py
```

`check.py` builds every possible two-block canvas (3,419 of them) and confirms each gets text from the knowledge base, then picks each of the 15 feelings with every canvas (51,285 cases) and confirms each feeling is said. Larger canvases always contain a covered pair. It also confirms that every known game names only real blocks and that every marked question's answer is one of its options, and that `VERSION`, the newest entry in `CHANGELOG.md` and the version badge above agree. It exits with an error and names the first gaps if anything is missing, so run it after any change to the knowledge base, the blocks, the games or the version.

```bash
curl -s http://localhost:8787/palette | node check_play.js 3000
```

`check_play.js` plays that many random canvases to the end with fixed-rule players, each with random answers to the block questions and two to five seats, and fails on any game that throws an error, offers a choice with nothing to choose, or does not end. Run it, with the tool running, after any change to `static/play-engine.js` or to the blocks.

## Files

| File | What it is |
|---|---|
| `app.py` | The FastAPI server: serves the page, `/palette`, `/tests`, `/games`, `/games/<id>.md`, `/narrate` and `/complete` |
| `rules.py` | Matches a canvas against the knowledge base |
| `templates.py` | Turns the matches into the feedback paragraph and the closing summary |
| `bridges.py` | The fixed joining phrases between knowledge-base sentences |
| `palette.py` | The groups, their blocks, which slots stack, and the feelings |
| `block_meta.py` | Each block's description and drawing |
| `interactions.json` | The curated knowledge base |
| `interactions-drafted.json` | The drafted knowledge base, built from `drafted/` |
| `drafted/` | Plain-text sources for the drafted entries, the build script, and the BoardGameGeek check |
| `wiki/` | The public wiki of the knowledge base, and `pull.py`, which carries approved proposals into it |
| `wiki-applied.json` | The wiki proposals already carried into the knowledge base (made by `wiki/pull.py`) |
| `check.py` | The coverage check, the known games' blocks and answers, and that the version, the changelog and the badge agree |
| `games.json`, `part-tests.json`, `block-questions.json` | The known games, the part tests and the block questions |
| `known_games.py` | A known game as a Markdown file and back: the download, Open game, and the wiki's Propose a game all use it |
| `site_config.py` | Where the tool and the wiki live: one variable, `DOMAIN`, sets both addresses |
| `VERSION`, `CHANGELOG.md` | The version, shown in the header and written into every game file, and what changed in each one |
| `mechanics-shortlist.md`, `feeling-blocks.md` | Reference notes on the mechanic and feeling blocks |
| `static/` | The page: `index.html`, `app.js`, `style.css`, `base-ui.css`, `play-engine.js` (the rules for playing on screen), `play.js` (the table they are played on), and `og.png`, the link-preview card |
| `check_play.js` | Plays thousands of random canvases on screen with fixed-rule players and fails on any game that breaks |
| `docs/` | The screenshot, and `make_og.py`, which draws `static/og.png` from it |
| `start.sh` | One-command start on macOS or Linux |
| `Dockerfile`, `captain-definition` | Container build |
| `requirements.txt` | fastapi, uvicorn, pydantic |

## Privacy

There are no analytics, counters or tracking of any kind. The server keeps no request log and stores nothing: your design lives only in your browser's local storage, and a saved game is a file on your own computer that the server never sees. A share link carries the design and its questions after the `#` in its address, which a browser never sends to a server; a game played on screen runs entirely in the browser, and answers to a share link's questions stay on the player's screen until they copy and send them. The hosted copy is the same code. The wiki is separate: it keeps the records and proposals people make there, under the names they sign in with, and nothing else (see [`wiki/README.md`](wiki/README.md#privacy)).

## Status and how to help

The tool is new. The curated knowledge base has been checked; much of the drafted part is still a first draft. I would like people to try it and tell me where a reading is wrong, a block is missing, or a game example does not hold: students, teachers, game designers, anyone who has made a game on paper.

The easiest way is the [wiki](https://boardgame-wiki.blevn.xyz): open the entry, add a record or propose a change. You can also write to me at me@prayasabhinav.net, or open an issue here.

## References

Duke, R. D. (2011). Origin and evolution of policy simulation: A personal journey. *Simulation & Gaming*, 42(3), 342–358. https://doi.org/10.1177/1046878110367570

Edwards, P., Sharma-Wallace, L., Wreford, A., Holt, L., Cradock-Henry, N. A., Flood, S., and Velarde, S. J. (2019). Tools for adaptive governance for complex social-ecological systems: A review of role-playing-games as serious games at the community-policy interface. *Environmental Research Letters*, 14(11), 113002. https://doi.org/10.1088/1748-9326/ab4036

Malézieux, A., and Spiegelman, E. (2025). An anatomical review of the common pool resource game. *Experimental Economics*, 28(3), 468–491. https://doi.org/10.1017/eec.2024.6

Meinzen-Dick, R., Janssen, M. A., Kandikuppa, S., Chaturvedi, R., Rao, K., and Theis, S. (2018). Playing games to save water: Collective action games for groundwater management in Andhra Pradesh, India. *World Development*, 107, 40–53. https://doi.org/10.1016/j.worlddev.2018.02.006

Olejniczak, K., Wolański, M., and Widawski, I. (2018). Regulation crash-test: Applying serious games to policy design. *Policy Design and Practice*, 1(3), 194–214. https://doi.org/10.1080/25741292.2018.1504372

Peters, V. A. M., and Vissers, G. A. N. (2004). A simple classification model for debriefing simulation games. *Simulation & Gaming*, 35(1), 70–84. https://doi.org/10.1177/1046878103253719

## Licence

GNU Affero General Public License v3.0. See [LICENSE](LICENSE). If you run a changed version for others over a network, you share your changes under the same licence.

Made by Prayas Abhinav, https://prayasabhinav.net
