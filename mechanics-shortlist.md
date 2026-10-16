# Mechanics Shortlist — boardgameBuilder v1

**Status:** v1 draft for KB assembly
**Date:** 24 April 2026
**Source:** BGG canonical mechanic names verified via Perplexity RAG (24 April 2026) with real exemplar games, cross-checked against BGG mechanism tags.
**Scope:** ~45 elements across 6 dimensions, plus 1 feelings dimension captured separately in `feeling-blocks.md`.

---

## Dimension 1 — Core mechanic (Blue, ~12 blocks)

The main thing players do on their turn. Mutually exclusive (pick one).

| Element | Plain-language description | BGG canonical | Exemplar 1 | Exemplar 2 |
|---------|---------------------------|---------------|------------|------------|
| roll and move | Roll dice, move your piece that many spaces. | Roll and Move | Monopoly | Snakes and Ladders |
| drafting | Pick one card from your hand, pass the rest around. | Drafting (Pick and Pass) | 7 Wonders | Sushi Go! |
| bidding | Offer money or resources; highest bid wins the thing. | Auction/Bidding | For Sale | Modern Art |
| push your luck | Keep risking for more; stop before it all goes wrong. | Push Your Luck | Can't Stop | Zombie Dice |
| area control | Fight to have the most pieces in regions of the board. | Area Majority/Influence | Risk | Blood Rage |
| worker placement | Place workers on spots to do jobs; others can't use taken spots. | Worker Placement | Agricola | Lords of Waterdeep |
| pattern building | Match colours or shapes to make patterns and score. | Pattern Building | Azul | Qwirkle |
| hand management | Choose which cards to play and when; hand size matters. | Hand Management | Race for the Galaxy | Dominion |
| trick-taking | Play one card; highest card wins the round; winner leads next. | Trick-taking | The Crew | Skull King |
| negotiation | Make deals and trades with other players. | Negotiation/Trading | Catan | Chinatown |
| set collection | Gather groups of matching items for points. | Set Collection | Ticket to Ride | Sushi Go! |
| tile placement | Lay tiles to build a shared map or pattern. | Tile Placement | Carcassonne | Kingdomino |

---

## Dimension 2 — Victory condition (Green, ~7 blocks)

What players are trying to do. Mutually exclusive (pick one).

| Element | Plain-language description | BGG canonical | Exemplar 1 | Exemplar 2 |
|---------|---------------------------|---------------|------------|------------|
| race to finish | First to reach the end wins. | Race | Formula D | Camel Up |
| most points | Whoever has the highest score at the end wins. | Victory Points as Game End Trigger | Ticket to Ride | Wingspan |
| last standing | Knock others out; last one alive wins. | Player Elimination | Risk | King of Tokyo |
| cooperative survival | Everyone wins or everyone loses — beat the game. | Cooperative Game | Pandemic | Forbidden Island |
| shared objective | Team earns points together by completing group goals. | Cooperative Game (partial) | Just One | Codenames |
| hidden personal goal | Chase your secret mission without others knowing. | Hidden Victory Points / Secret Objectives | Ethnos | Scotland Yard |
| narrative completion | Finish the story by making choices that complete the tale. | Storytelling / Variable Phase Order | Tales of the Arabian Nights | Betrayal at House on the Hill |

---

## Dimension 3 — Player interaction (Orange, ~7 blocks)

How players affect each other. Mutually exclusive (pick one).

| Element | Plain-language description | BGG canonical | Exemplar 1 | Exemplar 2 |
|---------|---------------------------|---------------|------------|------------|
| solo in parallel | Everyone plays alongside each other, barely touching. | Multi-use Cards / Low Interaction | Patchwork | Race for the Galaxy |
| direct confrontation | Attack, steal, or sabotage opponents directly. | Take That | Munchkin | Exploding Kittens |
| indirect via board | Affect others by changing the shared map or state. | Area Majority / Map Addition | Ticket to Ride | Carcassonne |
| fully cooperative | Everyone on the same team against the game. | Cooperative Game | Pandemic | Hanabi |
| semi-cooperative | Team play most of the time, personal bonuses sometimes. | Semi-Cooperative Game | Dead of Winter | Battlestar Galactica |
| team vs team | Two teams play head-to-head. | Team-Based Game | Codenames | Time's Up! |
| traitor/hidden role | Someone secretly plays for the other side. | Hidden Roles / Traitor Game | The Resistance | Secret Hitler |

---

## Dimension 4 — Chance–skill balance (Purple, ~4 blocks)

How much luck versus brain-work decides the game. Mutually exclusive (pick one).

| Element | Plain-language description | BGG canonical | Exemplar 1 | Exemplar 2 |
|---------|---------------------------|---------------|------------|------------|
| mostly chance | Dice and draws decide almost everything. | Dice Rolling | Candy Land | War (card game) |
| chance with mitigation | Luck happens, but clever play softens the blow. | Dice Rolling + Trading | Catan | Backgammon |
| skill with luck tempering | Choices matter most; a little luck adds spice. | Variable Setup + Tile Draw | Ticket to Ride | Carcassonne |
| mostly skill | Pure brain-work; no dice, no hidden draws. | Deterministic / No Luck | Chess | Go |

---

## Dimension 5 — Theme (Pink, ~8 blocks)

What the game is *about*. Mutually exclusive (pick one).

| Element | Plain-language description | Exemplar 1 | Exemplar 2 |
|---------|---------------------------|------------|------------|
| abstract | No story — pure shapes, colours, patterns. | Azul | Go |
| historical | Set in real history — wars, empires, trade routes. | 7 Wonders | Twilight Struggle |
| fantasy | Magic, dragons, wizards, quests. | Gloomhaven | Terra Mystica |
| science fiction | Space, robots, distant futures. | Race for the Galaxy | Terraforming Mars |
| everyday life | Farms, kitchens, trains, cities — things you recognise. | Agricola | Ticket to Ride |
| absurd / silly | Jokes, nonsense, chaos for its own sake. | Exploding Kittens | Unstable Unicorns |
| educational | Teaches something — history facts, words, maths. | Timeline | Professor Noggin's |
| real-world issue | About something happening now — climate, migration, justice. | CO₂: Second Chance | Freedom: The Underground Railroad |

---

## Dimension 6 — Information visibility (Yellow, ~5 blocks)

What players can see about each other. Mutually exclusive (pick one).

| Element | Plain-language description | BGG canonical | Exemplar 1 | Exemplar 2 |
|---------|---------------------------|---------------|------------|------------|
| full information | Everyone sees everything — no secrets. | Open Information / Perfect Information | Chess | Go |
| hidden hands | Your cards are secret; opponents' are too. | Hand Management + Hidden Information | Poker | Magic: The Gathering |
| hidden identity | Some players have secret roles or teams. | Hidden Roles | The Resistance | Secret Hitler |
| deduction | Use clues to figure out hidden information. | Deduction | Clue (Cluedo) | Mysterium |
| bluffing | Lie about what you have or what you're doing. | Bluffing | Coup | Liar's Dice |

---

## Totals

- **6 dimensions**, 45 elements
- Mutually exclusive within dimension; combine freely across dimensions
- Cross-dimensional pair count: 6-choose-2 dimensions × average (element count per dim × element count per other dim)
  - Approx: 12×7 + 12×7 + 12×4 + 12×8 + 12×5 + 7×7 + 7×4 + 7×8 + 7×5 + 7×4 + 7×8 + 7×5 + 4×8 + 4×5 + 8×5 = 84+84+48+96+60+49+28+56+35+28+56+35+32+20+40 = **751 cross-dimensional pairs**
- Same as the spec's ~780 estimate, close enough

---

## Flags and open notes

- **"Secret Hitler" appears twice** — as a hidden-identity exemplar and a traitor exemplar. It fits both. Accept the overlap; it is an accurate exemplar for both.
- **"Hidden personal goal" without hidden identity** is structurally rare. Ethnos (end-game bonus cards) and Scotland Yard (hunter's secret movement) are the cleanest exemplars.
- **"Shared objective" and "cooperative survival"** both fall under BGG's Cooperative Game tag but are functionally different — survival is existential (beat the game or die), shared objective is accumulative (reach a score together). Keep both.
- **Theme dimension has no BGG canonical mechanism column** — theme is a category on BGG, not a mechanic. Omitted the column.
- **Semi-cooperative vs traitor** — Battlestar Galactica has both semi-cooperative + traitor. The element "semi-cooperative" refers to games where *personal bonuses* exist alongside team play, not necessarily with traitors. Dead of Winter is the cleaner exemplar.
- **Workshop-readiness**: the plain-language descriptions are first drafts. Test during the weekend workshops — some may need further simplification for 10-12 year olds.

---

*Next: `feeling-blocks.md`, then `interactions-draft.json` via clustered Perplexity generation.*
