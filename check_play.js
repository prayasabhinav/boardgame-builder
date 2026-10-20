// check_play.js — plays thousands of random canvases to the end with fixed-rule players, and fails on any game that
// throws, offers a decision with no options, or does not end. Run: curl -s https://boardgame.blevn.xyz/palette | node check_play.js
"use strict";
const { createGame } = require("./static/play-engine.js");
const questions = require("./block-questions.json");

const palette = JSON.parse(require("fs").readFileSync(0, "utf8"));
const GAMES = Number(process.argv[2] || 3000);
let seed = 1;
const rand = () => { seed = (seed * 16807) % 2147483647; return seed / 2147483647; };
const pick = (arr) => arr[Math.floor(rand() * arr.length)];

const failures = [];
let asks = 0, longest = 0;
for (let i = 1; i <= GAMES; i++) {
  const blocks = {};
  for (const dim of palette.dimensions) {
    const count = dim.multi ? Math.floor(rand() * 4) : rand() < 0.8 ? 1 : 0;
    const ids = [...new Set(Array.from({ length: count }, () => pick(dim.blocks).id))];
    if (ids.length) blocks[dim.id] = ids;
  }
  const answers = {};
  for (const id of Object.values(blocks).flat()) for (const q of questions[id] || []) (answers[id] ||= {})[q.key] = pick(q.options).v;
  const seats = Array.from({ length: 2 + Math.floor(rand() * 4) }, (_, k) => ({ name: `P${k + 1}`, bot: true }));
  try {
    const g = createGame({ blocks, answers, seats, seed: i, goals: seats.map(() => "do well") });
    let steps = 0;
    while (g.ask) {
      if (++steps > 20000) throw new Error("did not end");
      if (g.ask.grab) g.choose(g.botGrab(g.ask));
      else if (!g.ask.options.length) throw new Error(`no options: ${g.ask.prompt}`);
      else g.choose(g.botChoice(g.ask));
    }
    if (!g.over || !g.over.lines.length) throw new Error("ended without a result");
    asks += steps; longest = Math.max(longest, steps);
  } catch (err) {
    failures.push({ game: i, blocks, error: err.stack.split("\n").slice(0, 3).join(" | ") });
  }
}
console.log(`games: ${GAMES} | failed: ${failures.length} | decisions per game: ${(asks / Math.max(1, GAMES - failures.length)).toFixed(0)} average, ${longest} most`);
for (const f of failures.slice(0, 8)) console.log(JSON.stringify(f));
process.exit(failures.length ? 1 : 0);
