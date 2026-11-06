# Small Go — surround more of the board

- From: Go (weiqi, baduk), an old game from China
- Players: 2 players
- Time: 10–15 min
- Made by: Traditional; played in China for more than two thousand years
- This version: A 7×7 grid on paper, and White adds 6 points for moving second

Made with boardgameBuilder 1.x. To design from it, open boardgameBuilder and choose Open game: its blocks go on the canvas, and the feelings are left for you to pick.

Two players take turns putting stones on the crossings of a grid. Stones never move, but a group that is surrounded is taken off. At the end, each player counts the space they hold.

## What it shows a designer

A stone placed in space claims territory; a stone placed against the other player's stones starts a fight. It shows how a game about holding areas makes every move a choice between building and attacking.

## What you need

- a sheet of paper with a grid of 7 lines by 7 lines (49 crossings)
- two kinds of small counters, about 25 of each, such as coins and buttons

## How to play

1. **Draw the grid.** Draw 7 lines across and 7 lines down. Stones go on the crossings, not in the squares.
2. **Place.** Black goes first and puts one stone on any empty crossing. Then White does the same. Take turns. Stones never move once placed.
3. **Capture.** Stones of one colour joined along the lines make a group. When a group has no empty crossing next to it, it is surrounded: take it off the board.
4. **Two limits.** You cannot place a stone where it would be surrounded at once, unless placing it captures something. You cannot capture one stone straight back if that would put the board exactly as it was one move ago.
5. **Pass.** Instead of placing, you can pass. When both players pass one after the other, the game ends.
6. **Count.** Each player counts their stones on the board and the empty crossings surrounded only by their stones. White adds 6. The higher total wins.

## After playing, talk about

- When did you place a stone to claim space, and when to fight?
- Which of your groups was in danger, and how could you tell?
- How did the small board change how much each stone mattered?

## Where the rules are written down

- https://en.wikipedia.org/wiki/Rules_of_Go

## Its blocks

- Core mechanic: area control; pattern building; capture by surrounding
- Victory condition: most points
- Player interaction: direct confrontation
- Chance or skill: mostly skill
- Theme: abstract
- Information visibility: full information
- Timing: take turns

## Saved state

boardgameBuilder reads this part back when the file is opened.

```json
{"mechanics": {"core-mechanic": ["area-control", "pattern-building", "capture-by-surrounding"], "victory-condition": "most-points", "player-interaction": "direct-confrontation", "chance-skill": "mostly-skill", "theme": "abstract", "information": "full-information", "timing": ["take-turns"]}, "chosenFeelings": [], "previousMechanics": {}, "previousFeelings": [], "turnNumber": 0, "locked": false, "turnHistory": [], "answers": {}, "tests": {}}
```
