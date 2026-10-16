# Changelog

What changed in boardgameBuilder and its wiki, newest first. The version is in `VERSION`, shown in the tool's header and written into every game file the tool hands out; `python check.py` fails if the newest entry here, `VERSION` and the README's version badge disagree. Versions before 0.5.0 were numbered afterwards, from the commit history. Approved wiki proposals carried in by the half-hourly sync are not listed: each is its own commit, "Carry approved wiki proposals into the knowledge base".

To add an entry: raise `VERSION` (the middle number for something people can use, the last for a fix), add a section at the top with the same number, the date and what changed, change the badge in `README.md`, and run `python check.py`.

## 0.6.0 — 16 October 2026

- Credits on every known game are now labelled rows (made by, rules from, this version, sources) with links, on the card, in the game file and on the wiki. A game file in the earlier one-line form still reads.
- 3 Quarters and All or Nothing now link to their new home, github.com/prayasabhinav/games; the account that first held them can no longer be signed in to.
- Each game card has **Download as a design (.md)** at the top, and the Known games introduction says how to get the file.
- The page and the game list are sent with `Cache-Control: no-cache`, so reloading never shows a page from before a deploy.

## 0.5.0 — 16 October 2026

Known games:

- 28 more known games, 38 in all. Classic and traditional games to play with things at hand: Nim, Raja Mantri Chor Sipahi, Name Place Animal Thing, Antakshari, Chidiya Ud, Pen fight, Hand cricket, Gulaam Chor, Satte pe Satta, Dots and Boxes, Battleship on paper, Bulls and Cows, Go Fish, Cheat, Snap, Twenty Questions, Hangman, Spoons, Telephone, Fizz Buzz, Two Truths and a Lie, Ghost, Cram, SOS, Three Men's Morris, and Set (Marsha J. Falco). And two games by Prayas Abhinav: All or Nothing and 3 Quarters.
- The rules of the classic games follow the sources listed with each game, and every game's blocks were checked against its BoardGameGeek tags where it has an entry. Charades no longer claims team vs team, which BoardGameGeek does not tag it with; Set names no core mechanic for the same reason.
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
