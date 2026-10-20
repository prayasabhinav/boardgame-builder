# Changelog

What changed in boardgameBuilder and its wiki, newest first. The version is in `VERSION`, shown in the tool's header and written into every game file the tool hands out; `python check.py` fails if the newest entry here, `VERSION` and the README's version badge disagree. Versions before 0.5.0 were numbered afterwards, from the commit history. Approved wiki proposals carried in by the half-hourly sync are not listed: each is its own commit, "Carry approved wiki proposals into the knowledge base".

To add an entry: raise `VERSION` (the middle number for something people can use, the last for a fix), add a section at the top with the same number, the date and what changed, change the badge in `README.md`, and run `python check.py`.

## 0.10.6 — 20 October 2026

- The slots no longer spill out of the canvas. A long block or answer, such as *forces in-character choices* under Theme, used to widen the two columns of slots past the edge of the canvas and under the feedback panel; it now wraps inside its slot.
- The feelings are the first group in the palette, in the same order as the canvas, where the feelings shelf sits above the slots. They used to come last, below every group of blocks.
- The two parts of the canvas read *Stage 1a · Intent* and *Stage 1b · Mechanics*. Both are the first stage, what the designer puts in; the feedback is stages 2 and 3. They used to read *Stage 1* twice.
- The picture for *model a system* has its arrowheads on the ends of its arrows. Two of the three were set at an angle to their lines.

## 0.10.5 — 17 October 2026

- The slots that hold several blocks are described as holding as many *different* blocks as a game needs, each once: a block cannot go into the same slot twice, so a slot holds at most every block of its group.

## 0.10.4 — 17 October 2026

- Every place that says which slots hold several blocks now names the same three, Core mechanic, Timing and Simulation, in the same words. The How it works box and the wiki's form for proposing a game still named only two, from before Timing took several. The tool and the wiki now take the list from the palette, so the text cannot fall behind it again.

## 0.10.3 — 17 October 2026

- The tool's header and the wiki's header and footer link the board game syntax on SYNTAX, of which boardgameBuilder is an instance. Its address is `SYNTAX_URL` in `site_config.py`.

## 0.10.2 — 17 October 2026

- The addresses of the tool and the wiki come from one variable, `DOMAIN` in `site_config.py`, so the tool can move to its own domain by changing one line. Nothing moves yet.

## 0.10.1 — 17 October 2026

- The canvas and the README say that Timing, like Core mechanic and Simulation, holds several blocks.

## 0.10.0 — 17 October 2026

- A new group of blocks, **Timing**: when and how fast players act. Take turns, everyone at once, no turns, timed turns, real-time span (moved here from Simulation), sedated and accelerated. A design can stack several, such as taking turns against a clock.
- 423 new drafted pair entries, so every combination with a Timing block has feedback (3,419 two-block canvases, all covered), and every feeling is judged against each new block.
- Every known game names its Timing. Set is confirmed against BoardGameGeek's "Real-Time" tag.
- A design saved before this version keeps real-time span: it moves from Simulation to Timing when the design is opened.
- The April note on feelings named a *timers* block that did not exist; it now names *timed turns*.
- 3 Quarters' rules now settle where a piece goes, what the die turns, which circles count and who takes the penalty, as I decided them on 17 October 2026.

## 0.9.3 — 17 October 2026

- Every button in the tool has one type, size and height; *Watch it and answer* had been taking the page's body type, and link-buttons its link colour.
- The wiki's top bar lines up with the page below it.
- The wiki's top bar is one line, starting with a link back to the tool; its search box has moved to a Find page.

## 0.9.2 — 16 October 2026

- The wiki's top bar is wide enough for its links on one row when signed in.
- The wiki's list of known games shows what each game shows a designer, without the *curated* badge.

## 0.9.1 — 16 October 2026

- The two buttons at the top of the known games, *All games* and *Back to designing*, are the same size.

## 0.9.0 — 16 October 2026

- 25 more known games, chosen because each shows a design idea the others don't: Eleusis and Mao (rules you discover), Nomic (rules you change), The Mind (playing in silence), Exquisite Corpse and Consequences (made blind, no winner), Racetrack, Sprouts and Paper soccer (drawing the board), Hex, Sim, Chomp, Kayles, Quantum tic-tac-toe, Ultimate tic-tac-toe and Mū Tōrere (abstract strategy), Aadu Puli Attam (two unequal sides), Moksha Patam, the Royal Game of Ur and Senet (old race games, two of them sacred), Kemps (a secret signal), Liar's Dice, Cuttle, Mendikot (trick-taking) and Penney's game (a fair-looking bet that isn't). 47 in all. The new ones have no animation yet.
- Every game now says **what it shows a designer**: the idea that playing it makes felt. A game file needs it, so games proposed on the wiki say it too.
- Buttons keep their natural size instead of stretching across the page, and on the wiki every button has one shape. A block's *say how it works* button stays beside its block, at the block's height.

## 0.8.0 — 16 October 2026

- I removed sixteen known games as too ordinary to teach much, among them Charades, Memory match and Tic-tac-toe Plus from the first ten. 22 remain.

## 0.7.0 — 16 October 2026

- Every view has its own address, so it can be linked, reloaded and reached with Back: `#games` for the known games, `#games/<id>` for one game, `#games/<id>/watch` to watch it, `#how-it-works`, `#blocks/<id>` for a block's description, and `#tests` for the part tests.
- The known games list sets each game's time and players apart from where it comes from.
- Source links that end in a bracket, such as Wikipedia's, now open the right page.

## 0.6.0 — 16 October 2026

- Credits on every known game are now labelled rows (made by, rules from, this version, sources) with links, on the card, in the game file and on the wiki. A game file in the earlier one-line form still reads.
- 3 Quarters and All or Nothing now link to their new home, github.com/prayasabhinav/games; I can no longer sign in to the account I first published them under.
- Each game card has **Download as a design (.md)** at the top, and the Known games introduction says how to get the file.
- The page and the game list are sent with `Cache-Control: no-cache`, so reloading never shows a page from before a deploy.

## 0.5.0 — 16 October 2026

Known games:

- More known games. Classic and traditional games to play with things at hand: Nim, Raja Mantri Chor Sipahi, Gulaam Chor, Satte pe Satta, Dots and Boxes, Battleship on paper, Bulls and Cows, Cheat, Spoons, Cram, SOS, Three Men's Morris and Set (Marsha J. Falco), and sixteen more, removed in 0.8.0. And two games of mine: All or Nothing and 3 Quarters.
- The rules of the classic games follow the sources listed with each game, and every game's blocks were checked against its BoardGameGeek tags where it has an entry. Set names no core mechanic, because BoardGameGeek does not tag it with one.
- Every game has credits: who made it where that is on record, *Traditional* where nobody is, and what this version changes from the usual one.
- Every game's rules now say who starts, how it ends and what happens on a tie, so it can be played from the card. The earlier ten gained rules they lacked: clue tokens in Three-card Hanabi, how the wolf's choice is made known in Werewolf-5, a winner for the blocking grid, wild cards and an empty draw pile in Last-card-out.
- **Download as a design** on each game: its rules, credits and blocks as a Markdown file; **Open game** puts its blocks on the canvas.
- A game without an animation (3 Quarters for now, and games added from the wiki) is offered to play and to download, without *Watch it and answer*.

Wiki:

- A page for each known game, linked from the blocks it uses, open to records like every entry, with its file to download.
- **Propose a game**: anyone signed in sends a game as a Markdown file in the same shape (a blank template is on the wiki). An editor approves it, and the half-hourly sync adds it to the tool. A changed file for a game already there proposes a change, which is carried in by hand.

Fixes:

- The Known games list showed the *Watch it and answer* bar before any game was chosen. Anything marked hidden now stays hidden.

Versions:

- This changelog, `VERSION`, the version in the tool's header and in every game file.

## 0.4.0 — 16 October 2026, 13:49

- Fourteen blocks from Dhruv Jani's ideas, and where the newer blocks came from, with checked references.

## 0.3.0 — 16 October 2026, 13:22

- Seventeen unusual blocks and their entries.
- Save a game as a Markdown file and open it again later.
- Known games (ten), part tests and block questions, carried over from the April 2026 prototype.
- Wiki: a link-preview card; owners can name editors on the about page, or type in a name.

## 0.2.0 — 16 October 2026, 11:42

- The wiki, and the half-hourly sync that carries its approved proposals into the tool.

## 0.1.0 — 16 October 2026, 07:29

- boardgameBuilder published, followed by a link-preview card and readable header links.
