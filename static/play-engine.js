// play-engine.js — plays the game on the canvas, with no model: every rule is written here, one module per block
// the screen can play. Blocks it cannot play are handed to the people at the table, in words (OFF_SCREEN).
// It draws nothing: play.js draws the table, and check_play.js plays thousands of games with fixed-rule players.
//
// The game runs as a generator. It yields an ask — whose decision, the question and the options — and is resumed
// with the option chosen. A grab ask (no turns) is resumed with the player who pressed first.

"use strict";

// ── What the people at the table do for blocks the screen cannot play ──
const OFF_SCREEN = {
  "negotiation": "Talk and make deals. The screen only moves the points you agree to give.",
  "call-and-response": "Before each move, answer the last player's move out loud with one of your own.",
  "playing-in-silence": "Nobody talks while playing. Show what you mean only by what you choose and when.",
  "role-play": "Speak and decide as your character, not as yourself.",
  "dexterity": "Settle each tie by hand at the table: a flick, a stack or a balance.",
  "drawing-the-map": "Keep a sheet of paper beside the screen and draw the world as the game goes.",
  "narrative-completion": "Tell the story as you play, and decide together how it ends.",
  "set-your-own-goal": "Each of you says what doing well means for you; afterwards, say whether you did.",
  "playing-by-letter": "Play one round, then send the share link and wait for the reply before the next.",
  "game-master": "One person says what each move means in the world and plays everyone the players meet.",
  "public-game": "Play where anyone passing can watch and join at the next round.",
  "attunement": "Before each round, everyone points at the same moment at who will lead it; say what you sensed.",
  "real-time-span": "Play one round a day, not all at once.",
  "one-knows-cannot-say": "One person picks a secret word before you start; between rounds the others guess it from that person's hints alone.",
  "stakes-outside-the-game": "Agree before you start what the result will mean outside the game, and keep to it.",
  "rehearse-a-future": "Before you start, say what way of living the game practises; afterwards, say how it felt.",
  "rules-make-an-argument": "Afterwards, read what your rules rewarded and say what they argue about the world.",
  "points-stand-for-values": "The points carry the name you gave them; notice when you chase the points instead of the thing.",
  "debrief": "Afterwards: What happened? Why? How is it like the real thing? What would change if one rule changed?",
  "theme": "The theme names the pieces; what they mean is yours to say.",
};

// ── Names the pieces carry, by theme ──
const THEMES = {
  "abstract": { pts: "points", coin: "chips", track: "path", pool: "pool", threat: "pressure", colours: ["red", "blue", "yellow", "green"], regions: ["north", "east", "south", "west"], spots: ["square", "circle", "triangle", "star"] },
  "historical": { pts: "honour", coin: "coins", track: "trade road", pool: "granary", threat: "unrest", colours: ["silk", "spice", "salt", "copper"], regions: ["port", "fort", "market", "temple town"], spots: ["fields", "bazaar", "stepwell", "court"] },
  "fantasy": { pts: "renown", coin: "gold", track: "quest road", pool: "spring of power", threat: "darkness", colours: ["fire", "water", "earth", "air"], regions: ["forest", "mountain", "marsh", "keep"], spots: ["farm", "market", "spring", "throne"] },
  "science-fiction": { pts: "credits", coin: "units", track: "jump route", pool: "fuel reserve", threat: "hull damage", colours: ["red", "cyan", "amber", "violet"], regions: ["orbit", "moon", "belt", "station"], spots: ["hydroponics", "dock", "reactor", "bridge"] },
  "everyday-life": { pts: "points", coin: "rupees", track: "road", pool: "water tank", threat: "bills due", colours: ["red", "blue", "yellow", "green"], regions: ["home", "school", "market", "station"], spots: ["kitchen", "shop", "tap", "front door"] },
  "absurd": { pts: "giggles", coin: "buttons", track: "wobbly path", pool: "jelly tub", threat: "chaos", colours: ["pink", "lime", "polka dot", "tartan"], regions: ["sock drawer", "fridge", "attic", "bathtub"], spots: ["sofa", "fridge", "tap", "hat stand"] },
  "educational": { pts: "points", coin: "tokens", track: "number line", pool: "answer bank", threat: "time used", colours: ["red", "blue", "yellow", "green"], regions: ["maths", "words", "science", "history"], spots: ["library", "lab", "well", "stage"] },
  "real-world-issue": { pts: "points", coin: "rupees", track: "road", pool: "groundwater", threat: "crisis", colours: ["red", "blue", "yellow", "green"], regions: ["village", "town", "river", "forest"], spots: ["fields", "market", "well", "council"] },
  "poetic": { pts: "notes", coin: "breaths", track: "path", pool: "silence", threat: "noise", colours: ["dawn", "noon", "dusk", "night"], regions: ["shore", "hill", "garden", "window"], spots: ["bench", "door", "pond", "lamp"] },
  "ritual-or-sacred": { pts: "merit", coin: "offerings", track: "path", pool: "sacred tank", threat: "forgetting", colours: ["saffron", "white", "green", "blue"], regions: ["shrine", "river ghat", "grove", "hall"], spots: ["kitchen", "courtyard", "tank", "steps"] },
  "mortality-and-loss": { pts: "memories", coin: "days", track: "path", pool: "time left", threat: "forgetting", colours: ["morning", "afternoon", "evening", "night"], regions: ["home", "garden", "hospital", "riverbank"], spots: ["table", "window", "well", "door"] },
  "war-and-conquest": { pts: "glory", coin: "coins", track: "march", pool: "supplies", threat: "siege", colours: ["infantry", "cavalry", "elephants", "chariots"], regions: ["pass", "plain", "river", "fort"], spots: ["camp", "armoury", "well", "war room"] },
};

// What each source of points is called on the closing screen
const SOURCES = {
  move: "moving", push: "pushing your luck", card: "cards", worker: "workers", area: "areas", pattern: "patterns",
  tile: "tiles", pool: "drawing from the pool", trick: "tricks", auction: "auctions", event: "events",
  take: "taking from others", deduce: "naming the hidden card", bluff: "claims", roll: "plain rolls", sets: "sets",
  goal: "secret goals", given: "gifts",
};

// House rules: changed by players (change the rules) or voted in (try a rule)
const HOUSE_RULES = [
  { id: "double-small", text: "Every gain of 1 or 2 counts double." },
  { id: "leader-pays", text: "At the end of each round the leader loses 2." },
  { id: "last-gets", text: "At the end of each round the player in last place gains 2." },
  { id: "big-cut", text: "Every gain of 5 or more is cut by 2." },
];

// The threat a team must keep below, in cooperative, semi-cooperative and traitor games
const LIMIT = 15;

const SIGNS = ["Wait before you choose.", "Give something away.", "Look at who is behind you.", "Change one habit.", "Go first if you can.", "Keep going as you are."];

function mulberry32(seed) {
  return function () {
    seed |= 0; seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function createGame(cfg) {
  // cfg: { blocks: { [slot]: [blockId] }, answers: { [blockId]: { [key]: value } }, seats: [{ name, bot }],
  //        seed, pointsName, goals: [text per seat], carry: { pool } }
  const rand = mulberry32(cfg.seed || 1);
  const all = Object.values(cfg.blocks).flat();
  const has = (id) => all.includes(id);
  const ans = (block, key, dflt) => (cfg.answers?.[block] || {})[key] || dflt;
  const pick = (arr) => arr[Math.floor(rand() * arr.length)];
  const d6 = () => 1 + Math.floor(rand() * 6);
  const names = { ...THEMES[(cfg.blocks.theme || [])[0]] || THEMES.abstract };
  if (has("points-stand-for-values")) names.pts = cfg.pointsName || "kindness";

  const victory = (cfg.blocks["victory-condition"] || [])[0] || "most-points";
  const interaction = (cfg.blocks["player-interaction"] || [])[0] || "indirect-via-board";
  const chance = (cfg.blocks["chance-skill"] || [])[0] || "skill-with-luck-tempering";
  const info = (cfg.blocks.information || [])[0] || null;

  const g = {
    names, log: [], round: 0, over: null, secret: false, sources: {}, delayed: [], houseRule: null,
    offScreen: all.filter((id) => OFF_SCREEN[id]).map((id) => OFF_SCREEN[id]),
    played: all.filter((id) => !OFF_SCREEN[id]),
  };
  if ((cfg.blocks.theme || []).length) g.offScreen.push(OFF_SCREEN.theme);
  const say = (text) => g.log.push({ round: g.round, text });
  // Whether each player keeps something the others must not see; the screen then hides it and passes between players
  g.limit = LIMIT;
  g.private = ["hidden-hands", "hidden-identity", "bluffing"].includes(info) || interaction === "traitor" || victory === "hidden-personal-goal";

  // ── Players ──
  const seats = [...cfg.seats];
  if (has("absent-player")) seats.push({ name: "The absent player", bot: true, absent: true });
  g.players = seats.map((s, i) => ({
    name: s.name, bot: s.bot, absent: !!s.absent, seat: i, score: 0, coins: has("bidding") ? 4 : 0,
    life: victory === "last-standing" ? 10 : null, out: false, hand: [], cards: [], played: null,
    grid: has("pattern-building") ? Array(9).fill(null) : null, pos: 0, laps: 0,
    tokens: chance === "mostly-skill" ? [1, 2, 3, 4, 5, 6] : null, rerolls: chance === "chance-with-mitigation" ? 2 : 0,
    goal: cfg.goals?.[i] || null, skip: false,
  }));
  const active = () => g.players.filter((p) => !p.out);
  const n = g.players.length;

  // ── Who plays with whom ──
  g.coop = ["fully-cooperative", "cooperative-survival", "shared-objective"].includes(victory) || interaction === "fully-cooperative";
  if (interaction === "team-vs-team" || info === "hidden-identity") {
    const sides = g.players.map((_, i) => i % 2);
    if (info === "hidden-identity") for (let i = sides.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [sides[i], sides[j]] = [sides[j], sides[i]]; }
    g.players.forEach((p, i) => { p.side = sides[i]; });
    g.sideNames = ["the Sun side", "the Moon side"];
    g.sidesSecret = info === "hidden-identity";
  }
  if (interaction === "traitor") pick(g.players.filter((p) => !p.absent)).traitor = true;
  if (victory === "hidden-personal-goal") {
    for (const p of g.players) {
      const other = pick(g.players.filter((q) => q !== p));
      p.secretGoal = pick([
        { text: `Finish ahead of ${other.name}.`, met: () => p.score > other.score },
        { text: "Finish in second place.", met: () => ranked().indexOf(p) === 1 },
        { text: `See ${other.name} finish last.`, met: () => ranked().at(-1) === other },
        { text: "Finish with an even score.", met: () => p.score % 2 === 0 },
      ]);
    }
  }
  const ranked = () => [...g.players].sort((a, b) => b.score - a.score);

  // ── Components, made only when a block needs them ──
  const usesCards = ["drafting", "hand-management", "trick-taking", "set-collection", "pattern-building"].some(has);
  let deck = [], discard = [];
  const freshDeck = () => {
    const d = [];
    for (let c = 0; c < 4; c++) for (let k = 1; k <= 9; k++) d.push({ c, n: k });
    for (let i = d.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [d[i], d[j]] = [d[j], d[i]]; }
    return d;
  };
  if (usesCards) deck = freshDeck();
  const draw = () => {
    if (!deck.length && !has("irreversible-change")) { deck = discard.length ? discard : freshDeck(); discard = []; for (let i = deck.length - 1; i > 0; i--) { const j = Math.floor(rand() * (i + 1)); [deck[i], deck[j]] = [deck[j], deck[i]]; } }
    return deck.pop() || null;
  };
  g.cardName = (card) => `${names.colours[card.c]} ${card.n}`;
  g.deckLeft = () => deck.length;

  const handSize = { tight: 3, medium: 5, wide: 7 }[ans("hand-management", "size", "medium")] || 5;
  if (has("hand-management") || has("trick-taking")) for (const p of g.players) while (p.hand.length < handSize) p.hand.push(draw());

  const openDraft = has("drafting") && ans("drafting", "style", "passing") === "open";
  if (usesCards && (openDraft || has("set-collection") || has("pattern-building"))) {
    g.market = [];
    while (g.market.length < 4) g.market.push(draw());
    g.marketHidden = info === "map-revealed-as-you-go" && !has("roll-and-move");
  }
  const refillMarket = () => { g.market = g.market.filter(Boolean); while (g.market.length < 4 && g.deckLeft() + discard.length > 0) { const c = draw(); if (!c) break; g.market.push(c); } };

  if (has("roll-and-move")) {
    const len = victory === "race-to-finish" ? { short: 15, medium: 25, long: 40 }[ans("race-to-finish", "length", "medium")] : 30;
    const every = { none: Infinity, some: 4, all: 2 }[ans("roll-and-move", "landing", "some")];
    const hidden = info === "map-revealed-as-you-go";
    g.track = Array.from({ length: len }, (_, i) => {
      if (i === 0 || i === len - 1 || i % every) return { kind: null, shown: true };
      const kind = hidden ? pick(["+2", "+3", "−2", "go 2"]) : victory === "race-to-finish" ? "go 2" : "+2";
      return { kind, shown: !hidden };
    });
    g.trackLoop = ans("roll-and-move", "path", "linear") === "loop";
  }
  if (has("area-control")) g.regions = names.regions.map((name, i) => ({ name, value: 3 + i, pieces: g.players.map(() => 0) }));
  if (has("worker-placement")) {
    const count = { small: 3, medium: n + 1, large: n + 3 }[ans("worker-placement", "spots", "medium")];
    g.spots = Array.from({ length: count }, (_, i) => ({ type: i % 4, name: names.spots[i % 4] + (i >= 4 ? ` ${Math.floor(i / 4) + 1}` : ""), takenBy: [], uses: 0 }));
    g.spotsShared = interaction === "solo-in-parallel" || ans("worker-placement", "interact", "block") === "shared";
  }
  if (has("tile-placement")) {
    g.tiles = Array.from({ length: 7 }, () => Array(7).fill(null));
    g.tiles[3][3] = Math.floor(rand() * 4);
  }
  if (has("shared-resource") || has("model-a-system")) g.pool = { level: cfg.carry?.pool ?? 20, cap: 30 };
  if (["cooperative-survival", "semi-cooperative", "traitor"].some((id) => id === victory || id === interaction)) g.threat = 0;
  if (victory === "keep-the-game-going") { g.fire = 6; g.feedCost = 3; }
  if (victory === "cannot-be-won") g.target = 25;
  if (info === "deduction") { g.hiddenCard = { c: Math.floor(rand() * 4), n: 1 + Math.floor(rand() * 9) }; g.clues = []; }
  if (has("stakeholder-roles")) {
    const groups = ["farmers", "the village council", "a shopkeeper", "fishers", "a school", "a water board"];
    g.players.forEach((p, i) => { p.role = { name: groups[i % groups.length] }; });
  }

  // How many rounds; some games end sooner
  g.rounds = { "keep-the-game-going": 20, "last-standing": 20, "race-to-finish": 20 }[victory] || (victory === "most-points" && ans("most-points", "end", "timed") === "target" ? 20 : 8);
  g.scoresHidden = victory === "most-points" && ans("most-points", "visible", "visible") === "hidden";

  // ── Points ──
  function gain(p, amount, source) {
    if (amount <= 0) return;
    if (g.houseRule?.id === "double-small" && amount <= 2) amount *= 2;
    if (g.houseRule?.id === "big-cut" && amount >= 5) amount -= 2;
    if (p.role?.source === source) amount += 1;
    if (has("delayed-effects")) { g.delayed.push({ p, amount, source, at: g.round + 2 }); say(`${p.name}: ${amount} ${names.pts} arrive in two rounds.`); return; }
    apply(p, amount, source);
  }
  function apply(p, amount, source) {
    g.sources[source] = (g.sources[source] || 0) + amount;
    if (!p.traitor) g.roundGain += amount;
    // In a race along a track, what you gain moves you on: two points make one space
    if (victory === "race-to-finish" && g.track && source !== "move") {
      const steps = Math.ceil(amount / 2);
      p.pos = Math.min(g.track.length - 1, p.pos + steps);
      say(`${p.name} moves on ${steps} for it.`);
      return;
    }
    p.score += amount;
  }
  function lose(p, amount) { p.score -= amount; }
  g.total = () => g.players.filter((p) => !p.traitor).reduce((s, p) => s + p.score, 0);

  // Cards a player takes go where the game uses them
  function takeCard(p, card, source) {
    if (!card) return;
    if (has("set-collection")) { const before = setScore(p); p.cards.push(card); gain(p, setScore(p) - before, "sets"); }
    else if (has("hand-management") || has("trick-taking")) p.hand.push(card);
    else gain(p, Math.ceil(card.n / 2), source);
  }
  function cardWorth(p, card) {
    if (!card) return 0;
    if (has("set-collection")) {
      const mode = ans("set-collection", "set", "matching");
      if (mode === "matching") return 2 + p.cards.filter((c) => c.c === card.c).length * 2;
      if (mode === "diverse") return p.cards.some((c) => c.c === card.c) ? 1 : 4;
      return p.cards.some((c) => Math.abs(c.n - card.n) === 1) ? 4 : 2;
    }
    return Math.ceil(card.n / 2);
  }
  function setScore(p) {
    const mode = ans("set-collection", "set", "matching");
    const byColour = [0, 1, 2, 3].map((c) => p.cards.filter((x) => x.c === c).length);
    if (mode === "matching") return byColour.reduce((s, k) => s + Math.floor(k / 3) * 10, 0);
    if (mode === "diverse") return Math.min(...byColour) * 12;
    const nums = [...new Set(p.cards.map((x) => x.n))].sort((a, b) => a - b);
    let runs = 0, len = 1;
    for (let i = 1; i < nums.length; i++) { len = nums[i] === nums[i - 1] + 1 ? len + 1 : 1; if (len === 3) { runs++; len = 0; } }
    return runs * 8;
  }

  // ── Asking ──
  function ask(player, prompt, options, extra = {}) { return { player, prompt, options, ...extra }; }

  // A die roll: chosen from number tokens when skill rules, re-rolled with a token when luck can be softened
  function* roll(p, why) {
    if (p.tokens) {
      if (!p.tokens.length) p.tokens = [1, 2, 3, 4, 5, 6];
      const o = yield ask(p, `${why}: spend a number instead of rolling`, p.tokens.map((t) => ({ label: String(t), value: t })));
      p.tokens.splice(p.tokens.indexOf(o.value), 1);
      return o.value;
    }
    let r = d6();
    if (p.rerolls && r <= 2) {
      const o = yield ask(p, `${why}: you rolled ${r}`, [{ label: `Keep ${r}`, value: 0, keep: true }, { label: `Re-roll (${p.rerolls} left)`, value: 1 }]);
      if (!o.keep) { p.rerolls--; r = d6(); say(`${p.name} re-rolled and got ${r}.`); }
    }
    return r;
  }

  // ── Actions on a turn: one builder per block ──
  function turnOptions(p) {
    const opts = [];
    const others = active().filter((q) => q !== p);

    if (has("roll-and-move")) opts.push({ kind: "move", label: `Roll and move along the ${names.track}`, value: victory === "race-to-finish" ? 8 : 4, *run() { yield* moveAlong(p); } });

    if (has("push-your-luck")) opts.push({ kind: "push", label: "Push your luck", value: 6, *run() {
      const stakes = { small: 0, medium: 2, big: 5 }[ans("push-your-luck", "stakes", "small")];
      const min = ans("push-your-luck", "timing", "optional") === "forced" ? 2 : 1;
      let pot = 0, rolls = 0;
      for (;;) {
        const r = yield* roll(p, "Push your luck");
        rolls++;
        if (r === 1) {
          say(pot ? `${p.name} rolled a 1 and lost the ${pot} in the pot${stakes ? `, and ${stakes} more` : ""}.` : `${p.name} rolled a 1 at once${stakes ? ` and lost ${stakes}` : ""}.`);
          if (stakes) lose(p, stakes);
          if (victory === "last-standing") p.life -= 1;
          return;
        }
        pot += r;
        if (rolls < min) continue;
        const o = yield ask(p, `You rolled ${r}; the pot holds ${pot}. Roll again or bank it?`, [
          { label: `Bank ${pot}`, value: pot, bank: true },
          { label: "Roll again", value: pot < 12 ? pot + 2 : 0 },
        ]);
        if (o.bank) { say(`${p.name} banked ${pot}.`); gain(p, pot, "push"); return; }
      }
    } });

    if (g.market && (openDraft || has("set-collection"))) for (const [i, card] of g.market.entries()) if (card) opts.push({
      kind: "card", label: g.marketHidden ? "Take a face-down card" : `Take ${g.cardName(card)}`, value: g.marketHidden ? 2 : cardWorth(p, card),
      *run() {
        const c = g.market[i];
        if (!c) { say(`${p.name} reached for a card someone else had already taken.`); return; }
        g.market[i] = null; takeCard(p, c, "card"); say(`${p.name} took ${g.cardName(c)}.`); refillMarket();
      },
    });

    if (g.spots) for (const spot of g.spots) {
      if (spot.gone || (!g.spotsShared && spot.takenBy.length)) continue;
      const effect = [`+3 ${names.pts}`, usesCards ? "take the top card" : `+2 ${names.pts}${has("bidding") ? ` and 1 ${names.coin}` : ""}`, g.pool ? `draw 3 from the ${names.pool}` : `+2 ${names.pts}`, `+1 ${names.pts}, go first next round`][spot.type];
      opts.push({ kind: "worker", spot, label: `Send a worker to the ${spot.name}: ${effect}`, value: [3, 2.5, 2.5, 1.5][spot.type], *run() {
        spot.takenBy.push(p); spot.uses++;
        if (has("irreversible-change") && spot.uses >= 3) { spot.gone = true; say(`The ${spot.name} is worn out for good.`); }
        if (spot.type === 0) gain(p, 3, "worker");
        if (spot.type === 1) { if (usesCards) takeCard(p, draw(), "worker"); else { gain(p, 2, "worker"); if (has("bidding")) p.coins++; } }
        if (spot.type === 2) { if (g.pool) drawPool(p, 3); else gain(p, 2, "worker"); }
        if (spot.type === 3) { gain(p, 1, "worker"); g.firstNext = p; }
        say(`${p.name} sent a worker to the ${spot.name}.`);
      } });
    }

    if (g.regions) for (const r of g.regions) opts.push({ kind: "area", label: `Place a piece in ${r.name} (worth ${r.value})`, value: regionValue(p, r), *run() { r.pieces[p.seat]++; say(`${p.name} placed a piece in ${r.name}.`); } });

    if (p.grid && g.market?.some(Boolean) && p.grid.includes(null)) opts.push({ kind: "pattern", label: "Take a card and place its colour on your grid", value: bestPattern(p).points, *run() {
      if (!g.market.some(Boolean) || !p.grid.includes(null)) { say(`${p.name} found nothing left to place.`); return; }
      const co = yield ask(p, "Which card?", g.market.map((c, i) => c && { label: g.cardName(c), value: bestPattern(p, c).points, i }).filter(Boolean));
      const card = g.market[co.i];
      const cells = p.grid.map((v, i) => v === null ? i : -1).filter((i) => i >= 0);
      const ce = yield ask(p, `Where on your grid does ${g.cardName(card)} go?`, cells.map((i) => ({ label: `Row ${Math.floor(i / 3) + 1}, column ${i % 3 + 1} (+${patternPoints(p, i, card.c)})`, value: patternPoints(p, i, card.c), i })));
      p.grid[ce.i] = card.c; g.market[co.i] = null; refillMarket();
      gain(p, patternPoints(p, ce.i, card.c, true), "pattern");
      say(`${p.name} placed ${names.colours[card.c]} on their grid.`);
    } });

    if (has("hand-management") && p.hand.length) {
      opts.push({ kind: "card", label: "Play a card from your hand", value: Math.max(...p.hand.map((c) => handPlayValue(p, c))), *run() {
        const o = yield ask(p, "Which card? A card of the same colour as your last one counts double.", p.hand.map((c, i) => ({ label: g.cardName(c), value: handPlayValue(p, c), i })), { secret: true });
        const card = p.hand.splice(o.i, 1)[0];
        gain(p, handPlayValue(p, card), "card");
        p.played = card; discard.push(card);
        const next = draw(); if (next) p.hand.push(next);
        say(`${p.name} played ${g.cardName(card)}.`);
      } });
      if (p.hand.length < handSize) opts.push({ kind: "draw", label: "Draw a card and wait", value: 1, *run() { const c = draw(); if (c) p.hand.push(c); say(`${p.name} drew a card.`); } });
    }

    if (g.tiles) opts.push({ kind: "tile", label: "Draw a tile and lay it down", value: 3, *run() {
      const colour = Math.floor(rand() * 4);
      const cells = tileCells(colour).map(([r, c]) => ({ r, c, pts: 1 + 2 * neighbours(g.tiles, r, c).filter((x) => x === colour).length }))
        .sort((a, b) => b.pts - a.pts).slice(0, 6);
      if (!cells.length) { say("There is no room left for tiles."); return; }
      const o = yield ask(p, `You drew a ${names.colours[colour]} tile. Where does it go?`, cells.map((x) => ({ label: `${"ABCDEFG"[x.c]}${x.r + 1} (+${x.pts})`, value: x.pts, x })));
      g.tiles[o.x.r][o.x.c] = colour; gain(p, o.x.pts, "tile");
      say(`${p.name} laid a ${names.colours[colour]} tile.`);
    } });

    if (g.pool && g.pool.level > 0) opts.push({ kind: "pool", label: `Draw from the ${names.pool} (${g.pool.level} left)`, value: 3, *run() {
      if (!g.pool.level) { say(`${p.name} came to the ${names.pool} and found it empty.`); return; }
      const most = Math.min(4, g.pool.level);
      const o = yield ask(p, `How much do you draw from the ${names.pool}?`, Array.from({ length: most }, (_, i) => ({ label: String(i + 1), value: poolValue(i + 1), k: i + 1 })));
      drawPool(p, o.k);
    } });

    if (has("negotiation") && others.length && p.score > 0) opts.push({ kind: "given", label: `Give ${names.pts} to another player, as you agreed`, value: -5, *run() {
      const w = yield ask(p, "To whom?", others.map((q) => ({ label: q.name, value: 0, q })));
      const a = yield ask(p, "How many?", [1, 2, 3].filter((k) => k <= p.score).map((k) => ({ label: String(k), value: -k, k })));
      lose(p, a.k); w.q.score += a.k; g.sources.given = (g.sources.given || 0) + a.k;
      say(`${p.name} gave ${a.k} to ${w.q.name}.`);
    } });

    if (has("change-the-rules")) opts.push({ kind: "rule", label: "Change the house rule", value: 0.5, *run() {
      const choices = HOUSE_RULES.filter((r) => r !== g.houseRule).sort(() => rand() - 0.5).slice(0, 2);
      const o = yield ask(p, "Which rule holds from now on?", choices.map((r) => ({ label: r.text, value: rand(), r })));
      g.houseRule = o.r; say(`${p.name} changed the rule: ${o.r.text}`);
    } });

    if (interaction === "direct-confrontation") {
      const how = ans("direct-confrontation", "how", "take");
      for (const q of others) {
        if (how === "block") opts.push({ kind: "take", label: `Block ${q.name}: they lose their next move`, value: q.skip ? 0 : 2, *run() { q.skip = true; say(`${p.name} blocked ${q.name}.`); } });
        else if (how === "hurt" || victory === "last-standing") opts.push({ kind: "take", label: victory === "last-standing" ? `Hurt ${q.name}: they lose 2 life` : `Hurt ${q.name}: they lose 3`, value: 2.5, *run() { if (q.life !== null) q.life -= 2; else lose(q, 3); say(`${p.name} hurt ${q.name}.`); } });
        else opts.push({ kind: "take", label: `Take 2 ${names.pts} from ${q.name}`, value: q.score >= 2 ? 3 : 0, *run() { const k = Math.min(2, Math.max(0, q.score)); lose(q, k); p.score += k; g.sources.take = (g.sources.take || 0) + k; say(`${p.name} took ${k} from ${q.name}.`); } });
      }
    }

    if (g.hiddenCard) {
      const left = deductionCandidates();
      opts.push({ kind: "deduce", label: "Ask about the hidden card", value: left.length > 3 ? 2 : 0.5, *run() {
        const qs = [0, 1, 2, 3].map((c) => ({ label: `Is it ${names.colours[c]}?`, test: (h) => h.c === c }))
          .concat([{ label: "Is its number above 5?", test: (h) => h.n > 5 }, { label: "Is its number even?", test: (h) => h.n % 2 === 0 }]);
        const o = yield ask(p, "Ask one question; everyone hears the answer.", qs.map((x) => ({ ...x, value: splitValue(x.test) })));
        const yes = o.test(g.hiddenCard);
        g.clues.push({ text: `${o.label} ${yes ? "Yes" : "No"}.`, test: o.test, yes });
        say(`${p.name} asked: ${o.label} ${yes ? "Yes" : "No"}.`);
      } });
      opts.push({ kind: "deduce", label: "Name the hidden card", value: left.length <= 2 ? 6 : left.length <= 4 ? 2 : -1, *run() {
        const c = yield ask(p, "Its colour?", [0, 1, 2, 3].map((k) => ({ label: names.colours[k], value: left.filter((h) => h.c === k).length, k })));
        const k = yield ask(p, "Its number?", Array.from({ length: 9 }, (_, i) => ({ label: String(i + 1), value: left.filter((h) => h.c === c.k && h.n === i + 1).length, k: i + 1 })));
        if (c.k === g.hiddenCard.c && k.k === g.hiddenCard.n) {
          gain(p, 8, "deduce"); say(`${p.name} named the hidden card: ${g.cardName(g.hiddenCard)}. A new one is set aside.`);
          g.hiddenCard = { c: Math.floor(rand() * 4), n: 1 + Math.floor(rand() * 9) }; g.clues = [];
        } else { lose(p, 3); say(`${p.name} guessed ${names.colours[c.k]} ${k.k}: wrong.`); }
      } });
    }

    if (info === "bluffing" && others.length) opts.push({ kind: "bluff", label: "Roll in secret and make a claim", value: 2.5, *run() {
      const r = d6();
      const o = yield ask(p, `You rolled ${r} in secret. What do you claim?`, [1, 2, 3, 4, 5, 6].map((k) => ({ label: `I rolled ${k}`, value: k === r ? 3 : k > r && k - r <= 2 ? 3.5 : 0, k })), { secret: true });
      const caller = others[0];
      const c = yield ask(caller, `${p.name} claims a ${o.k}. Believe it or call it?`, [
        { label: `Believe: ${p.name} scores ${o.k}`, value: o.k <= 3 ? 1 : 0, believe: true },
        { label: "Call the bluff", value: o.k >= 5 ? 1 : 0.2 },
      ]);
      if (c.believe) { gain(p, o.k, "bluff"); say(`${caller.name} believed ${p.name}'s ${o.k}.`); }
      else if (o.k > r) { lose(p, 3); gain(caller, 2, "bluff"); say(`${caller.name} called it: ${p.name} had rolled ${r}.`); }
      else { lose(caller, 2); gain(p, o.k, "bluff"); say(`${caller.name} called it, but ${p.name} really had ${r}.`); }
    } });

    if (g.secretRule && !g.secretRule.found) opts.push({ kind: "guess-rule", label: "Guess the secret rule", value: g.secretRule.broken ? 2 : -1, *run() {
      const o = yield ask(p, "Which move does the secret rule punish?", g.secretRule.kinds.map((k) => ({ label: KIND_NAMES[k] || k, value: k === g.secretRule.lastBroken ? 3 : 0, k })));
      if (o.k === g.secretRule.kind) { g.secretRule.found = true; gain(p, 5, "deduce"); say(`${p.name} found the secret rule: ${KIND_NAMES[o.k]} costs 2.`); }
      else { lose(p, 1); say(`${p.name} guessed the secret rule wrong.`); }
    } });

    if (g.fire !== undefined && p.score >= g.feedCost) opts.push({ kind: "fire", label: `Keep the game going: give ${g.feedCost} ${names.pts}, the fire grows by 2`, value: g.fire <= 2 ? 5 : -1, *run() { lose(p, g.feedCost); g.feedCost++; g.fire += 2; say(`${p.name} kept the game going; next time it costs ${g.feedCost}.`); } });

    if (p.traitor && g.threat !== undefined) opts.push({ kind: "sabotage", label: `Sabotage in secret: the ${names.threat} rises by 3`, value: g.threat >= LIMIT - 4 ? 5 : 1, secret: true, *run() { g.threat += 3; say("Something stirred."); } });

    // A game with no move the screen can play gets a plain roll
    if (!opts.length || opts.every((o) => ["given", "rule", "take", "guess-rule", "fire", "sabotage"].includes(o.kind))) opts.push({ kind: "roll", label: "Roll a die and score it", value: 3.5, *run() { const r = yield* roll(p, "Roll"); gain(p, r, "roll"); say(`${p.name} rolled ${r}.`); } });
    return opts;
  }

  const KIND_NAMES = { move: "Rolling and moving", push: "Pushing your luck", card: "Taking or playing a card", worker: "Sending a worker", area: "Placing a piece", pattern: "Placing on your grid", draw: "Drawing a card", tile: "Laying a tile", pool: "Drawing from the pool", deduce: "Asking about the hidden card", bluff: "Making a claim", roll: "A plain roll", given: "Giving", rule: "Changing the rule", take: "Taking from others" };

  function* moveAlong(p) {
    let r = yield* roll(p, "Move");
    const catchUp = { none: 0, some: 1, strong: 2 }[ans("race-to-finish", "catchup", "none")];
    if (victory === "race-to-finish" && catchUp && active().every((q) => q.pos + q.laps * g.track.length >= p.pos + p.laps * g.track.length)) r += catchUp;
    yield* stepTo(p, r);
  }
  function* stepTo(p, steps) {
    const len = g.track.length;
    let to = p.pos + steps;
    if (to >= len) {
      if (g.trackLoop) { to -= len; p.laps++; gain(p, 3, "move"); say(`${p.name} passed the start: +3.`); }
      else to = len - 1;
    }
    if (victory !== "race-to-finish") gain(p, steps, "move");
    p.pos = to;
    const cell = g.track[to];
    say(`${p.name} moved ${steps} to space ${to + 1}.`);
    if (cell.kind) {
      if (!cell.shown) { cell.shown = true; say(`Space ${to + 1} turned over: ${cell.kind}.`); }
      if (cell.kind === "go 2") { if (to < len - 1) yield* stepTo(p, 2); }
      else if (cell.kind === "−2") { if (victory === "race-to-finish") p.pos = Math.max(0, to - 2); else lose(p, 2); }
      else gain(p, parseInt(cell.kind, 10), "event");
    }
  }

  function regionValue(p, r) {
    const mine = r.pieces[p.seat], best = Math.max(...r.pieces.filter((_, i) => i !== p.seat));
    return mine <= best ? r.value * (mine + 1 > best ? 1 : 0.5) : r.value * 0.3;
  }
  function patternPoints(p, i, colour) {
    const row = Math.floor(i / 3), col = i % 3;
    const near = [[row - 1, col], [row + 1, col], [row, col - 1], [row, col + 1]].filter(([a, b]) => a >= 0 && a < 3 && b >= 0 && b < 3).map(([a, b]) => p.grid[a * 3 + b]);
    let pts = 1 + near.filter((x) => x === colour).length;
    const line = (cells) => cells.every((k) => (k === i ? colour : p.grid[k]) === colour);
    if (line([row * 3, row * 3 + 1, row * 3 + 2])) pts += 5;
    if (line([col, col + 3, col + 6])) pts += 5;
    return pts;
  }
  function bestPattern(p, only) {
    let best = { points: 0 };
    for (const card of only ? [only] : g.market.filter(Boolean)) for (let i = 0; i < 9; i++) if (p.grid[i] === null) {
      const pts = patternPoints(p, i, card.c);
      if (pts > best.points) best = { points: pts };
    }
    return best;
  }
  function handPlayValue(p, card) { return p.played && p.played.c === card.c ? card.n * 2 : card.n; }
  function neighbours(grid, r, c) { return [[r - 1, c], [r + 1, c], [r, c - 1], [r, c + 1]].filter(([a, b]) => a >= 0 && a < 7 && b >= 0 && b < 7).map(([a, b]) => grid[a][b]); }
  function tileCells(colour) {
    const mode = ans("tile-placement", "placement", "constrained");
    const cells = [];
    for (let r = 0; r < 7; r++) for (let c = 0; c < 7; c++) if (g.tiles[r][c] === null && (mode === "free" || neighbours(g.tiles, r, c).some((x) => x !== null))) cells.push([r, c]);
    if (mode === "matching") { const same = cells.filter(([r, c]) => neighbours(g.tiles, r, c).includes(colour)); if (same.length) return same; }
    return cells;
  }
  function drawPool(p, k) {
    k = Math.min(k, g.pool.level);
    g.pool.level -= k; gain(p, k, "pool");
    say(`${p.name} drew ${k} from the ${names.pool}; ${g.pool.level} left.`);
  }
  function poolValue(k) { return g.pool.level - k < 6 && g.coop ? k - 3 : k; }
  function deductionCandidates() {
    const all = [];
    for (let c = 0; c < 4; c++) for (let k = 1; k <= 9; k++) all.push({ c, n: k });
    return all.filter((h) => g.clues.every((cl) => cl.test(h) === cl.yes));
  }
  function splitValue(test) { const left = deductionCandidates(); const yes = left.filter(test).length; return Math.min(yes, left.length - yes); }

  // ── A turn: choose one action and play it ──
  function* turn(p) {
    let opts = turnOptions(p);
    if (!g.secretRule && info === "rules-you-discover") {
      const kinds = [...new Set(opts.map((o) => o.kind))].filter((k) => !["sabotage", "fire", "guess-rule"].includes(k));
      g.secretRule = { kind: pick(kinds), kinds, found: false, broken: false };
      opts = turnOptions(p);
    }
    if (chance === "mostly-chance") { const o = pick(opts); opts = [{ ...o, label: `The dice chose: ${o.label}` }]; }
    const o = yield ask(p, `${p.name}, your move`, opts, { secret: g.private });
    yield* playOption(p, o);
  }
  function* playOption(p, o) {
    if (o.spot && !g.spotsShared && o.spot.takenBy.length) { say(`${p.name} wanted the ${o.spot.name}, but it was taken.`); return; }
    yield* o.run();
    if (g.secretRule && !g.secretRule.found && o.kind === g.secretRule.kind) {
      lose(p, 2); g.secretRule.broken = true; g.secretRule.lastBroken = o.kind;
      say(`No: ${p.name} broke the secret rule (−2).`);
    }
  }

  // ── Things that happen once a round, before the moves ──
  function* roundStart() {
    say(`Round ${g.round} begins.`);
    if (has("bidding")) for (const p of active()) p.coins += 2;
    if (g.threat !== undefined) {
      const rise = d6() + Math.ceil(active().length * 0.75);
      g.threat += rise; say(`The ${names.threat} rises by ${rise}, to ${g.threat} of ${LIMIT}.`);
      if (interaction === "traitor" && rand() < 0.3) { g.threat += 3; say("Something stirred."); }
    }
    if (chance === "dice-tell-the-story") {
      const r = d6(), first = ranked()[0], last = ranked().at(-1);
      const events = [
        [`A hard season: everyone loses 1 ${names.pts}.`, () => active().forEach((p) => lose(p, 1))],
        [`A gift for ${last.name}, in last place: +3.`, () => gain(last, 3, "event")],
        ["Nothing happens.", () => {}],
        [`A fair: everyone gains 1 ${names.pts}.`, () => active().forEach((p) => gain(p, 1, "event"))],
        [`A thief visits ${first.name}, in the lead: −2.`, () => lose(first, 2)],
        [`Good luck for ${g.players[g.first % n].name}, who goes first: +2.`, () => gain(g.players[g.first % n], 2, "event")],
      ];
      say(`The dice tell the story (${r}): ${events[r - 1][0]}`); events[r - 1][1]();
    }
    if (chance === "chance-read-as-a-sign") say(`The dice give a sign: “${SIGNS[d6() - 1]}”`);
    if (has("trick-taking")) for (const p of active()) while (p.hand.length < handSize) { const c = draw(); if (!c) break; p.hand.push(c); }

    if (has("try-a-rule") && g.round === Math.floor(g.rounds / 2) + 1 && !g.tried) {
      const choices = HOUSE_RULES.slice().sort(() => rand() - 0.5).slice(0, 3);
      const votes = choices.map(() => 0);
      for (const p of active()) { const o = yield ask(p, "Which rule do you want to try from now on?", choices.map((r, i) => ({ label: r.text, value: rand(), i }))); votes[o.i]++; }
      const win = choices[votes.indexOf(Math.max(...votes))];
      g.houseRule = win; g.tried = { rule: win, round: g.round, before: g.total() };
      say(`Rule tried from now on: ${win.text}`);
    }

    if (has("drafting") && !openDraft && deck.length + discard.length > 0) {
      const ps = active();
      let packs = ps.map(() => [draw(), draw(), draw()].filter(Boolean));
      for (let pickNo = 0; pickNo < 3; pickNo++) {
        for (const [i, p] of ps.entries()) {
          if (!packs[i].length) continue;
          const o = yield ask(p, "Draft: keep one card, pass the rest on", packs[i].map((c, k) => ({ label: g.cardName(c), value: cardWorth(p, c), k })), { secret: true });
          takeCard(p, packs[i].splice(o.k, 1)[0], "card");
        }
        packs = packs.map((_, i) => packs[(i + 1) % ps.length]);
      }
      say("Everyone drafted three cards.");
    }

    if (has("bidding")) {
      const card = ["set-collection", "hand-management", "trick-taking", "pattern-building"].some(has) ? draw() : null;
      const prize = card ? g.cardName(card) : `${d6() + 2} ${names.pts}`;
      const bids = [];
      for (const p of active()) {
        const worth = card ? cardWorth(p, card) : parseInt(prize, 10);
        const o = yield ask(p, `Auction for ${prize}: bid in secret (you have ${p.coins} ${names.coin})`, Array.from({ length: Math.min(p.coins, 8) + 1 }, (_, k) => ({ label: k ? `${k} ${names.coin}` : "Pass", value: k <= worth ? k * 0.6 + rand() * 0.2 : -k, k })), { secret: true });
        bids.push([p, o.k]);
      }
      const top = Math.max(...bids.map((b) => b[1]));
      const winner = top > 0 ? bids.find((b) => b[1] === top)[0] : null;
      if (winner) { winner.coins -= top; if (card) takeCard(winner, card, "auction"); else gain(winner, parseInt(prize, 10), "auction"); say(`${winner.name} won ${prize} for ${top}.`); }
      else { if (card) discard.push(card); say(`Nobody bid for ${prize}.`); }
    }

    if (has("trick-taking")) {
      const ps = active();
      const lead = g.trickLeader && !g.trickLeader.out ? g.trickLeader : ps[0];
      const order = ps.slice(ps.indexOf(lead)).concat(ps.slice(0, ps.indexOf(lead)));
      const trick = [];
      for (const p of order) {
        if (!p.hand.length) continue;
        const led = trick[0]?.card.c;
        const legal = p.hand.map((c, i) => ({ c, i })).filter((x) => led === undefined || x.c.c === led || !p.hand.some((h) => h.c === led));
        const o = yield ask(p, trick.length ? `Trick: follow ${names.colours[led]} if you can` : "Trick: lead a card", legal.map((x) => ({ label: g.cardName(x.c), value: trickValue(trick, x.c), i: x.i })), { secret: true });
        trick.push({ p, card: p.hand.splice(o.i, 1)[0] });
      }
      if (trick.length) {
        const led = trick[0].card.c;
        const win = trick.filter((t) => t.card.c === led).sort((a, b) => b.card.n - a.card.n)[0];
        gain(win.p, trick.length + 2, "trick"); g.trickLeader = win.p;
        discard.push(...trick.map((t) => t.card));
        say(`Trick: ${trick.map((t) => `${t.p.name} ${g.cardName(t.card)}`).join(", ")}. ${win.p.name} took it.`);
      }
    }
  }
  function trickValue(trick, card) {
    if (!trick.length) return card.n;
    const led = trick[0].card.c, best = Math.max(...trick.filter((t) => t.card.c === led).map((t) => t.card.n));
    return card.c === led && card.n > best ? 10 : 9 - card.n;
  }

  // ── Things that happen once a round, after the moves ──
  function roundEnd() {
    if (g.threat !== undefined) {
      // Half of what the team gained this round pushes the threat back
      const back = Math.min(g.threat, Math.floor(g.roundGain / 2));
      g.threat -= back;
      say(`What you gained together pushed the ${names.threat} back by ${back}, to ${g.threat} of ${LIMIT}.`);
      if (g.threat >= LIMIT) g.collapsed = true;
    }
    if (g.regions) {
      const when = ans("area-control", "timing", "snapshots");
      if (when === "continuous" || (when === "snapshots" && g.round % 3 === 0)) scoreRegions();
    }
    if (g.pool) {
      const before = g.pool.level;
      if (has("model-a-system")) g.pool.level = Math.min(g.pool.cap, g.pool.level + Math.round(0.5 * g.pool.level * (1 - g.pool.level / g.pool.cap)));
      else if (g.pool.level > 0) g.pool.level = Math.min(g.pool.cap, g.pool.level + 2);
      if (g.pool.level !== before) say(`The ${names.pool} refills to ${g.pool.level}.`);
      else if (!g.pool.level) say(`The ${names.pool} is empty.`);
    }
    for (const d of g.delayed.filter((x) => x.at <= g.round)) { apply(d.p, d.amount, d.source); say(`${d.amount} ${names.pts} arrived for ${d.p.name}.`); }
    g.delayed = g.delayed.filter((x) => x.at > g.round);
    if (g.houseRule?.id === "leader-pays") lose(ranked()[0], 2);
    if (g.houseRule?.id === "last-gets") gain(ranked().at(-1), 2, "event");
    if (g.spots) for (const s of g.spots) s.takenBy = [];
    if (victory === "last-standing" && g.round >= 3) { const low = active().sort((a, b) => a.score - b.score)[0]; low.life -= 3; say(`${low.name}, lowest, loses 3 life.`); }
    for (const p of g.players) if (p.life !== null && p.life <= 0 && !p.out) { p.out = true; say(`${p.name} is out.`); }
    if (g.fire !== undefined) { g.fire--; say(`The fire burns down to ${g.fire}.`); }
    if (g.target !== undefined) { const lead = ranked()[0]; g.target += Math.max(1, lead.score - (g.lastLead || 0)); g.lastLead = lead.score; say(`The goal moves away to ${g.target}.`); }
  }
  function scoreRegions() {
    for (const r of g.regions) {
      const order = r.pieces.map((k, i) => [k, i]).filter(([k]) => k > 0).sort((a, b) => b[0] - a[0]);
      if (!order.length) continue;
      if (order.length === 1 || order[0][0] > order[1][0]) { gain(g.players[order[0][1]], r.value, "area"); say(`${g.players[order[0][1]].name} holds ${r.name}: +${r.value}.`); }
      else say(`${r.name} is tied; nobody scores it.`);
    }
  }

  // ── Has the game ended? ──
  function ended() {
    const teamSum = g.total();
    if (g.collapsed) return { lost: true, why: `The ${names.threat} reached ${LIMIT}.` };
    if (victory === "last-standing" && active().length <= 1) return { why: "One player is left." };
    if (victory === "race-to-finish") {
      const goal = g.track ? null : { short: 20, medium: 30, long: 45 }[ans("race-to-finish", "length", "medium")];
      const done = g.players.filter((p) => g.track ? (g.trackLoop ? p.laps >= 2 : p.pos >= g.track.length - 1) : p.score >= goal);
      if (done.length) return { why: `${done[0].name} reached the end first.`, first: done[0] };
    }
    if (victory === "most-points" && ans("most-points", "end", "timed") === "target" && ranked()[0].score >= 40) return { why: `${ranked()[0].name} reached 40.` };
    if (victory === "shared-objective" && teamSum >= 15 * n) return { why: `Together you reached ${15 * n}.`, won: true };
    if (victory === "keep-the-game-going" && g.fire <= 0) return { why: `The fire went out after ${g.round} rounds.` };
    if (has("irreversible-change") && usesCards && !deck.length && !discard.length && !(g.market || []).some(Boolean)) return { why: "The last card is gone." };
    if (g.round >= g.rounds) return { why: `${g.rounds} rounds are over.` };
    return null;
  }

  // ── The closing screen ──
  function finish(end) {
    if (g.regions && ans("area-control", "timing", "snapshots") !== "continuous") scoreRegions();
    const lines = [end.why];
    let winners = [];
    if (victory === "hidden-personal-goal") for (const p of g.players) { const met = p.secretGoal.met(); lines.push(`${p.name}'s secret goal: ${p.secretGoal.text} ${met ? "Met: +10." : "Not met."}`); if (met) { p.score += 10; g.sources.goal = (g.sources.goal || 0) + 10; } }
    const order = ranked();
    const teamSum = g.total();
    if (interaction === "traitor") {
      const t = g.players.find((p) => p.traitor);
      lines.push(`The traitor was ${t.name}.`);
      winners = end.lost ? [t] : g.players.filter((p) => !p.traitor);
    } else if (end.lost) { lines.push("Everyone lost together."); }
    else if (g.coop || victory === "cooperative-survival") {
      const won = end.won || (victory === "cooperative-survival") || (victory === "shared-objective" ? teamSum >= 15 * n : teamSum >= 12 * n);
      lines.push(won ? `You held out and won together, with ${teamSum} ${names.pts} between you.` : `Together you made ${teamSum} ${names.pts}; the aim was ${(victory === "shared-objective" ? 15 : 12) * n}. You lost together.`);
      if (won) winners = g.players.slice();
    } else if (["no-objective", "narrative-completion", "set-your-own-goal", "keep-the-game-going"].includes(victory)) {
      lines.push(victory === "keep-the-game-going" ? `You kept it going for ${g.round} rounds. Nobody wins.` : "Nobody wins or loses.");
      if (victory === "set-your-own-goal") for (const p of g.players) lines.push(`${p.name} set out to: ${p.goal || "(no goal given)"}`);
    } else if (victory === "cannot-be-won") {
      lines.push(`Nobody reached the goal; it moved to ${g.target}. The game cannot be won.`);
    } else if (victory === "one-loser") {
      const low = order.at(-1);
      lines.push(`${low.name} lost. Everyone else is simply safe.`);
    } else if (g.sideNames) {
      const sums = [0, 1].map((s) => g.players.filter((p) => p.side === s).reduce((a, p) => a + p.score, 0));
      const best = sums[0] === sums[1] ? -1 : sums[0] > sums[1] ? 0 : 1;
      for (const s of [0, 1]) lines.push(`${g.sideNames[s]}: ${g.players.filter((p) => p.side === s).map((p) => p.name).join(", ")} — ${sums[s]}.`);
      lines.push(best < 0 ? "The sides tied." : `${g.sideNames[best]} won.`);
      winners = best < 0 ? [] : g.players.filter((p) => p.side === best);
    } else if (victory === "last-standing") {
      winners = active().length ? [active().sort((a, b) => b.life - a.life)[0]] : [];
    } else if (end.first) {
      winners = [end.first];
    } else if (victory === "race-to-finish" && g.track) {
      const far = Math.max(...g.players.map((p) => p.laps * g.track.length + p.pos));
      winners = g.players.filter((p) => p.laps * g.track.length + p.pos === far);
      lines.push("Nobody reached the end; the furthest along wins.");
    } else {
      winners = order.filter((p) => p.score === order[0].score);
    }
    if (interaction === "semi-cooperative" && !end.lost) lines.push(`The ${names.threat} was held off; ${order[0].name} did best.`);
    if (winners.length && !g.coop && interaction !== "traitor") lines.push(`${winners.map((p) => p.name).join(" and ")} won.`);
    if (g.sidesSecret && victory !== "most-points") lines.push(`Secret sides: ${g.players.map((p) => `${p.name}, ${g.sideNames[p.side]}`).join("; ")}.`);
    if (g.tried) {
      const before = g.tried.before / Math.max(1, g.tried.round - 1), after = (g.total() - g.tried.before) / Math.max(1, g.round - g.tried.round + 1);
      lines.push(`The rule you tried, “${g.tried.rule.text}”: ${before.toFixed(1)} ${names.pts} a round before it, ${after.toFixed(1)} after.`);
    }
    if (g.secretRule) lines.push(`The secret rule: ${KIND_NAMES[g.secretRule.kind] || g.secretRule.kind} cost 2. ${g.secretRule.found ? "It was found." : "Nobody found it."}`);
    if (g.hiddenCard) lines.push(`The hidden card was ${g.cardName(g.hiddenCard)}.`);
    const total = Object.values(g.sources).reduce((a, b) => a + b, 0);
    g.over = {
      lines, winners, scores: order.map((p) => ({ name: p.name, score: p.score, life: p.life, out: p.out, space: g.track ? p.pos + 1 : null })),
      rewarded: total ? Object.entries(g.sources).sort((a, b) => b[1] - a[1]).map(([k, v]) => ({ what: SOURCES[k] || k, share: Math.round((100 * v) / total) })) : [],
      carry: g.pool && has("irreversible-change") ? { pool: g.pool.level } : null,
    };
    say("The game is over.");
  }

  // ── The game ──
  function* flow() {
    g.first = 0;
    if (has("stakeholder-roles")) {
      const kinds = [...new Set(turnOptions(g.players[0]).map((o) => o.kind))].filter((k) => SOURCES[k]);
      g.players.forEach((p, i) => { p.role.source = kinds[i % Math.max(1, kinds.length)]; p.role.text = `${p.role.name}: +1 whenever you score from ${SOURCES[p.role.source] || "anything"}`; });
    }
    for (;;) {
      g.round++;
      g.roundGain = 0;
      yield* roundStart();
      let end = ended();
      if (end) { finish(end); return; }
      const ps = active();
      const start = g.firstNext && !g.firstNext.out ? ps.indexOf(g.firstNext) : g.first % ps.length;
      g.firstNext = null;
      const order = ps.slice(start).concat(ps.slice(0, start));
      let turns = has("worker-placement") ? 2 : 1;
      if (has("accelerated")) turns += (g.round > g.rounds / 2 ? 1 : 0) + (g.round > (3 * g.rounds) / 4 ? 1 : 0);

      for (let t = 0; t < turns; t++) {
        if (has("no-turns") && !has("take-turns")) {
          // No turns: whoever presses first moves, as many times as there are players
          for (let k = 0; k < order.length; k++) {
            const p = yield ask(null, "Be quickest: the first to press makes the next move", [], { grab: true, players: order });
            say(`${p.name} was quickest.`);
            yield* turn(p);
            if (ended()) break;
          }
        } else if (has("everyone-at-once") && !has("take-turns")) {
          // Everyone at once: all choose in secret, then all moves are made together
          const chosen = [];
          for (const p of order) {
            if (p.skip) { p.skip = false; continue; }
            let opts = turnOptions(p);
            if (chance === "mostly-chance") { const o = pick(opts); opts = [{ ...o, label: `The dice chose: ${o.label}` }]; }
            chosen.push([p, yield ask(p, `${p.name}, choose in secret`, opts, { secret: true })]);
          }
          say("Everyone reveals at once.");
          for (const [p, o] of chosen) yield* playOption(p, o);
        } else {
          for (const p of order) {
            if (p.out) continue;
            if (p.skip) { p.skip = false; say(`${p.name} is blocked and misses a move.`); continue; }
            yield* turn(p);
            if (ended()) break;
          }
        }
        if (ended()) break;
      }
      roundEnd();
      g.first++;
      end = ended();
      if (end) { finish(end); return; }
    }
  }

  const it = flow();
  g.ask = it.next().value;
  g.choose = (option) => { g.ask = it.next(option).value || null; return g.ask; };
  // A fixed-rule player: the option worth most by its own estimate, with a little noise so games differ
  g.botChoice = (a) => {
    const scored = a.options.map((o) => [o.value + rand() * 0.3, o]);
    return scored.reduce((best, x) => (x[0] > best[0] ? x : best))[1];
  };
  g.botGrab = (a) => pick(a.players);
  g.timerSeconds = () => (has("timed-turns") ? Math.max(5, 15 - (has("accelerated") ? g.round : 0)) : null);
  g.pauseSeconds = () => (has("sedated") ? 4 : 0);
  return g;
}

if (typeof module !== "undefined") module.exports = { createGame, OFF_SCREEN, THEMES };
