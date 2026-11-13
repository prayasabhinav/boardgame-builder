# Changelog

What changed in boardgameBuilder and its wiki, newest first. The version is in `VERSION`, shown in the tool's header and written into every game file the tool hands out; `python check.py` fails if the newest entry here, `VERSION` and the README's version badge disagree. Versions before 0.5.0 were numbered afterwards, from the commit history. Approved wiki proposals carried in by the half-hourly sync are not listed: each is its own commit, "Carry approved wiki proposals into the knowledge base".

To add an entry: raise `VERSION` (the middle number for something people can use, the last for a fix), add a section at the top with the same number, the date and what changed, change the badge in `README.md`, and run `python check.py`.

## 0.22.4 — 13 November 2026

- **The clash model learnt from the pairs it was unsure of.** 212 pairs were labelled: the 17 where the three readers had split, the 194 the tool flags, and others it put between 10% and 90%. For each, a reader searched the books and research papers for a game with both blocks, or a passage saying they cannot go together, and otherwise decided by logical inference, saying so. 9 labels rest on a source whose words code found (among them Hoyle on craps, that there is little skill in it beyond knowing the odds); 201 on inference. One reader agreed with the three earlier readers' majority on 78% of the pairs both covered, so an inference label counts with that weight, and a source label counts as settled. Measured before it went in, each pair held out of its own training: on the newly labelled pairs, Brier 0.237 before and 0.196 after (17% better); on the readers' votes, 0.0111 before and 0.0098 after (12% better), correlation 0.812 to 0.830. The flags and their reasons are unchanged; the teacher's page shows the new probabilities. Training now runs on a separate machine (`review-model/train-remote.sh`).

## 0.22.3 — 13 November 2026

- **More of the feedback comes from research.** 146 more open-access papers on board games, play and game design were read for what two blocks do together. 48 of them gave 70 entries, among them Chowka Bhara's bonus throws, the extra turn in sowing games, hidden roles with teams in Werewolf, and a classroom game whose designers removed dice because students put outcomes down to luck rather than to the system the game showed. Each entry was checked as the books' are: a reader who had not written it found the passage, code found the reader's copied words in the paper, and the page was taken from the PDF in code (printed pages where the PDF matches the journal's, the PDF's own otherwise, and the reference says which). Two entries that failed are kept aside in `kb-books/removed/`; one clash the papers name was not kept, because a known game, Moksha Patam, has both blocks.
- The clash model was checked against 115 games those papers read from their rules. Of the 88 pairs they show that no known game does, it flags none and gives each 4% or less. Added to its training, they did not improve its held-out score (Brier 0.0111 before, 0.0113 after), so it was not retrained.

## 0.22.2 — 13 November 2026

- **Six research papers join the books.** Samarasinghe and others (2021), Björk, Lundgren and Holopainen (2003), Olsson, Björk and Dahlskog (2014), Sousa (2023), Chircop (2017) and Abu Makhadi (2025), each settled through Crossref, add 160 lines to the Ideas tab and 8 entries on what two blocks do together. Every line was checked against its paper as the books' lines were: a reader who had not written it found the passage, code found the reader's copied words in the paper, and the page was taken from the PDF in code. Three lines that failed are kept aside in `ideas/removed/`.
- The clash model was checked against the seven games whose rules Sousa read: of the nine pairs they show and no known game does, it flags none and gives each 1% or less. Added to its training, they left its held-out score unchanged, so it was not retrained.

## 0.22.1 — 13 November 2026

- **The books win where they speak, not where they are silent.** 0.22.0 kept only what a book states, and so took out true and useful text the books simply do not mention. That is put back: the 201 points for what a pair brings or costs that had been left empty, the 4 book entries taken out, 61 template lines (player counts, makers such as *Traditional*, origins, and five rule steps) and the game credits and phrases removed for that reason (Irving Finkel's rules for the Royal Game of Ur, Eleusis Express, the US National Park Service board for Three Men's Morris, and others). Everything a book contradicted stays corrected. The standard now: the book wins where it says otherwise; where it is silent, a logical inference that supports the entry stays. A BoardGameGeek entry alone backs nothing, being written by its users.
- The wiki's book check follows the same standard: a change to a book entry still quotes the book's words, and passes if the book supports it or if it follows from the book and the book does not contradict it.

## 0.22.0 — 13 November 2026

- **The books are the authority.** Every entry taken from a book, every game template and the 47 known games were checked against the full texts of the books by readers who had not written them, each finding the book's own words for what it checked, and code confirming those words are in the book. Then everything was corrected to the books, and the corrections were checked again the same way. 388 book pair entries changed; where a book states no advantage or cost for a pair, the place is now empty rather than filled with our own reading (200 places); 4 entries the books do not support were taken out (kept, with the reason, in `kb-books/removed/`). 96 templates changed: rules, player counts and origins now say what their book says, and a template's own simplifications are named on its *This version* line. 18 known games changed: credits (Pig to Scarne, 1946; Nim to Bouton, 1902; Sprouts to 1960), rules where a book describes the game (Eleusis, Chomp, Mū Tōrere, the Royal Game of Ur, Liar's Dice and others), and the move-by-move play-throughs, redrawn wherever a move broke the game's rules or a count did not add up. The pages cited were not checked: the book texts carry no page marks.
- **The check continues on the wiki.** A proposed change to an entry taken from a book now needs 3 to 12 of the book's own words in quotation marks; they are checked against the book, and a reader compares the change with that passage, before the change reaches the tool. `wiki/pull.py` waits for that check (`wiki-book-checked.json`) and sets aside a change that fails it. A pair from a book may now carry fewer than two points for what it brings or costs.

## 0.21.2 — 13 November 2026

- The tool and its wiki have an icon in the browser tab and in search results: the first three rows of the board game syntax's family mark from SYNTAX. There was none before.

## 0.21.1 — 13 November 2026

- The model behind the teacher's *N% likely to clash* has a name, **khatka**, and is released on its own with its data at https://github.com/prayasabhinav/khatka (AGPL-3.0). It gives the same flags, reasons and probabilities as before. Kinds of fun are not paired with core mechanics: a kind of fun is the enjoyment a game aims at and cannot contradict how it is played.

## 0.21.0 — 13 November 2026

- **Kind of fun**, a new group of 42 blocks, second after the core mechanic: the enjoyment a game is built to give, each named as the books on play and games name it (competition (agon), chance (alea), make-believe (mimicry), vertigo (ilinx), flow, hard fun, triumph (fiero), discovery, whimsy and the rest), with its definition and the books behind it under ? and in `kinds-of-fun.json`. A game can aim at several. The group is required: **Mark complete** asks for at least one before it writes the closing summary. Each kind has one line in the feedback, kept with the theme lines (`drafted/themes.txt`) and on the wiki; the lines are drafted and unreviewed.
- **Save game** gives every file a name of its own: the core mechanics on the canvas and six characters worked out from the file, such as `drafting-set-collection-3k9x0a.md`, in place of `boardgame-design.md` every time.

## 0.20.1 — 7 November 2026

- Space between **Develop further** and *Start again* under the closing summary; the two touched.

## 0.20.0 — 7 November 2026

- **Develop further.** Marking a design complete still writes the closing summary and greys out the canvas, and now the summary carries a **Develop further** button beside *Start again*. It opens the same design again: the blocks can be moved, Iterate and Mark complete come back, and the turn count goes on from where it stopped. The history, the summary included, stays in the feedback column.

## 0.19.0 — 6 November 2026

- Exploration time. A student in a class can press **Explore for 2 hours** in the header. For two hours the teacher still sees any clashing blocks on their canvas, on a card marked *Exploring until* that time and *not for review*, with no button to mark it looked at and sorted below the students who need a look. The student can stop it early, or start it again when it ends. The server holds only the time it ends, in memory, gone when the class ends.

## 0.18.3 — 6 November 2026

- The teacher's page shows, beside each clashing pair, how likely the two blocks are to clash, as a percentage. It comes from a small model trained on 2,160 answers: three independent readers asked of each of 720 sampled pairs whether both blocks can be true of the same game (`review-model/clash-votes.jsonl`). On pairs it had not seen, pairs it put near 85% were said to clash by 81% of readers, and pairs near 1% by 1%. It replaces the *Needs a look: N of 10* score, which was 8 for every flagged pair and 2 for every other, a yes or no written as a number. Students see the reason, not the percentage.

## 0.18.2 — 6 November 2026

- The teacher's page says what it shows in plain words, with an example, where it said *marked pair*: two blocks a student has put together that contradict each other, such as *chase and tag*, where everyone runs at once, with *take turns*. The student sees both marked *unusual*. The join dialog says *unusual pair*, the word students see.

## 0.18.1 — 6 November 2026

- The teacher's page no longer says *This class has ended* when it opens on a class remembered from an earlier visit that had already ended, for instance in a restart. It clears it and shows the page ready to start a class; the message appears only when a class ends while the page is showing it.
- The armed *End the class* button keeps white text on red when the pointer is over it; it had turned the text green.

## 0.18.0 — 6 November 2026

- Teachers sign in. `/teacher` shows a sign-in page until they do, and starting, reading and ending a class need a signed-in teacher; students still join without signing in. Logins are made with `teacher_logins.py`, and the server holds only salted hashes of the passwords.

## 0.17.0 — 6 November 2026

- A teacher's dashboard at `/teacher`. The class code is shown large, with a link that fills it in for students (`#join/<code>`), and can be shown full screen for a projector. Students with a marked pair are listed by student, with each pair, why it is marked, its score and the rest of their blocks by slot, or by pair, with the names of the students who have it. A teacher can mark a student as looked at; the mark lasts until that student's pairs change and is kept in the teacher's browser.
- An overview of the class as a whole: how many students joined, how many changes they made to their canvases and how many placed a marked pair. Nothing is counted for one student alone. To count each student once, the server keeps the names of those who joined, in memory, until the class ends; students are told so before they join.
- Ending a class takes two presses.
- `check.py` runs in seconds and skips the checks when nothing they read has changed (`check-log.txt`).

## 0.16.0 — 6 November 2026

- Unusual pairs are marked. If the knowledge base says two blocks on the canvas pull against each other, both are marked *unusual*, and hovering shows why. A palette block that would make such a pair is marked before it is dropped. Nothing stops anyone placing them.
- Other pairs are marked too, when the two blocks cannot both be true of one game; being new or unusual is not a reason. 194 of the 5,688 pairs of a core mechanic with another block are marked, each with its reason, such as *chase and tag runs with everyone moving at once, and take turns says otherwise*, and a score out of 10 for how likely a look is needed: 2, 5 or 8. The reasons come from a table of what each core mechanic makes or settles, and which blocks say otherwise (`review-model/properties.json`). The score comes from a small model trained on that table and on keyed pairs, none of them from known games, so a new pair scores no higher for being new; among keyed pairs it had not seen, none of those scored 2 were illogical and 94% of those scored 8 were.
- Feedback from books. Six books on games and their rules give 476 entries for pairs of blocks. Each is put in plain words and cites its book and page, such as *(Elias, Garfield and Gutschera, 2012, p. 275)*. A curated entry still comes first, then a book's, then a drafted one.
- An **Ideas** tab beside the feedback. It holds an alphabetical glossary of 3,102 terms and 3,366 key ideas from 25 books on play and games, each with its book and page or chapter. It has a search box, and the list of books comes at the end. Every line was checked against its book, and 257 that could not be traced to a passage were set aside.
- 65 blocks from the rule books, among them a trump suit, sowing seeds, chase and tag and the pie rule. Each has its **?** text and drawing. Until they have been tried in a class they sit at the end of their group, under *From the rule books, tentative*. Every pair they make has a drafted entry.
- All of this is on the wiki. The book entries show their pages, and a pair's page also shows what every other book says about that pair. The tentative blocks are there, and so is every glossary term and key idea. When a change is approved on the wiki, it is written back into the book's file, the Ideas file or `book-blocks.json`, and the page reference is kept.
- Teaching remotely. A teacher opens `/teacher` and starts a class, which gives a code. Students press **Join a class** in the header and type the code and their name. While a student's canvas holds an unusual pair, the teacher's page shows their name, the pair and their blocks. The server keeps this in memory and never writes it to disk. It is gone once the pair leaves the canvas or the class ends, and after a day at the latest.

## 0.15.0 — 31 October 2026

- All or Nothing can be played in the browser on Tabletopia: its card in Known games links there, under *Play it online*.
- All or Nothing and 3 Quarters link to their design files, under *Design files*: cards, board, pieces, rules and print files, to download from github.com/prayasabhinav/games.

## 0.14.4 — 30 October 2026

- The tool and the wiki have moved under SYNTAX, the project the board game syntax belongs to: the tool is at https://boardgame.syntax.prayasabhinav.net and the wiki at https://boardgame-wiki.syntax.prayasabhinav.net. The old addresses, boardgame.blevn.xyz and boardgame-wiki.blevn.xyz, send every link on to the same page at the new ones, so saved games, shared links and posters keep working. Signing in to the wiki with GitHub or Google works at the new address.

## 0.14.3 — 24 October 2026

- A tag in the text of *How our game plays* is marked where it is written: filled in the accent colour, with white letters and a dark edge, the same as the tagged block on the canvas. A text box can show only one colour, so the text is drawn again behind it with each tag marked, in the same type and spacing; the box grows with its text instead of scrolling, so the two stay aligned. A tag whose block has left the canvas is struck through.

## 0.14.2 — 24 October 2026

- A block tagged in *How our game plays* stands out on the canvas: filled in the accent colour, with white text and a dark border. Untagged blocks keep their light tint, and the tagged block's slot keeps its **@**.

## 0.14.1 — 24 October 2026

- In *How our game plays*, the **@** menu now closes once a tag is picked and stays closed while you write on. It used to stay open under the text saying *No block on the canvas by that name*, because it read the space after the tag as part of a name. The message now shows only for a single word typed after **@** that names no block.

## 0.14.0 — 24 October 2026

- **How our game plays**, a box on the canvas under the slots (*Stage 1c · Gameplay*), for writing how the game goes in your own words. Typing **@** lists the blocks on the canvas by the box they sit in; picking one puts the tag in the text, and tagging a block tags its box with it: the tags are listed under the text as *Core mechanic › roll and move*, and the slot carries an **@** at its corner. A tag whose block has since left the canvas is listed as no longer on it. The text is kept with the design, in **Save game**'s file (a section *How our game plays*, with its tags by box) and in **Open game**. Nothing reads it to make feedback.
- The feelings no longer show a **?**. It opened nothing for a feeling; the mechanic blocks keep theirs.
- The link-preview card (`static/og.png`) is redrawn from a new screenshot (`docs/screenshot.jpg`), showing 0.14.0 with no **?** on the feelings.

## 0.13.1 — 20 October 2026

- The answers a player copies after a shared game also carry everything that happened in it, move by move, so whoever shared it can read the playtest as well as the answers.

## 0.13.0 — 20 October 2026

- A share link carries questions for whoever plays it, so it works as a playtest. **Share link** opens five questions to edit, remove or add to (up to twelve), and the address changes with them. The player sees them before starting and answers them at the end; **Copy my answers** gives one text with the blocks, the result and the answers to send back. Nothing is sent or kept by the tool.

## 0.12.0 — 20 October 2026

- **Play**, beside Iterate, plays the design on screen. 55 of the 86 blocks have a rule in code, and they join into one game with turns, rounds, scores and an end set by the victory condition; nothing is generated. The 12 themes name the pieces, and the 19 blocks that happen between people are listed with what to do at the table.
- Each seat is a person or a player the screen moves by fixed rules. Secrets are hidden and the screen asks to be passed between people; with no turns, the quickest key moves; timed turns have a clock and sedated games a pause.
- **Full screen** and **Share link**: the link carries the design in its address, so whoever opens it plays the same game, and their canvas is left alone.
- `check_play.js` plays thousands of random canvases to the end and fails on any game that breaks.

## 0.11.0 — 20 October 2026

- A search box at the top of the palette. Typing shows only the blocks whose name or description holds the words, such as *water* for *model a system* and *shared resource*, or a whole group when its name is typed, such as *theme*. It stays at the top while the palette scrolls, says when nothing matches, and Esc clears it.

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
