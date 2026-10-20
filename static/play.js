// play.js — the table for playing the canvas on screen (#play), drawn around play-engine.js.
// People take their own decisions; fixed-rule players take theirs by the rule in the engine. Where players keep
// secrets, the screen hides them and asks for it to be passed. A share link carries the design in its address.

const CARD_COLOURS = ["#C75B39", "#3F6E9E", "#D9A441", "#4A8C5C"];
const GRAB_KEYS = ["A", "L", "Z", "M", "Q"];
const BOT_DELAY = 450;

const play = { design: null, shared: false, seats: null, game: null, viewer: null, timers: [], questions: null, replies: [] };

// ── The design: from the canvas, or from a share link ──

function currentDesign() {
  const blocks = {};
  for (const dim of state.dimensions) {
    const v = state.mechanics[dim.id];
    const ids = Array.isArray(v) ? v : v ? [v] : [];
    if (ids.length) blocks[dim.id] = ids;
  }
  return { b: blocks, a: state.answers, f: state.chosenFeelings };
}

function designCode(d) {
  return btoa(unescape(encodeURIComponent(JSON.stringify(d)))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

// A shared design keeps only blocks this tool knows, in their own slots
function readDesign(code) {
  try {
    const d = JSON.parse(decodeURIComponent(escape(atob(code.replace(/-/g, "+").replace(/_/g, "/")))));
    const blocks = {};
    for (const dim of state.dimensions) {
      const ids = (d.b?.[dim.id] || []).filter((id) => dim.blocks.some((b) => b.id === id));
      if (ids.length) blocks[dim.id] = dim.multi ? ids : ids.slice(0, 1);
    }
    const answers = {};
    for (const [id, a] of Object.entries(d.a || {})) if (typeof a === "object") answers[id] = Object.fromEntries(Object.entries(a).map(([k, v]) => [k, String(v)]));
    const feelings = (d.f || []).filter((id) => state.feelings.some((f) => f.id === id));
    const questions = (Array.isArray(d.q) ? d.q : []).filter((q) => typeof q === "string" && q.trim()).map((q) => q.slice(0, 300)).slice(0, 12);
    return { b: blocks, a: answers, f: feelings, q: questions };
  } catch (_) {
    return null;
  }
}

// The link carries the design and the questions its sharer wants answered after the game
function shareUrl() {
  const questions = play.questions.map((q) => q.trim()).filter(Boolean);
  return `${location.origin}${location.pathname}#play/${designCode({ ...play.design, q: questions })}`;
}

function defaultQuestions() {
  const qs = [
    "What did you spend most of your turns doing?",
    "Was there a moment when you had to think hard? What was it?",
    "Did the result come from the choices people made, or from luck?",
    "If you could change one rule, which would it be, and why?",
  ];
  const feelings = play.design.f.map(displayOf);
  if (feelings.length) qs.push(`We wanted it to feel ${feelings.join(", ")}. Did it? When?`);
  return qs;
}

// ── Opening and closing ──

function openPlay(code) {
  const design = code ? readDesign(code) : currentDesign();
  document.getElementById("playOverlay").hidden = false;
  document.getElementById("playShare").hidden = true;
  document.getElementById("playFullBtn").hidden = !document.fullscreenEnabled;
  document.getElementById("playShareBtn").hidden = !design;
  if (!design) {
    document.getElementById("playBody").innerHTML = `<div class="phase-eyebrow">Play on screen</div><h1 class="phase-title">This link holds no design</h1>
      <p class="phase-intro">The address may have been cut short when it was copied. Ask for the link again, or go back to designing.</p>`;
    return;
  }
  const same = play.design && JSON.stringify(design) === JSON.stringify(play.design);
  play.design = design;
  play.shared = !!code;
  if (!same) { play.questions = design.q?.length ? [...design.q] : null; play.replies = []; }
  if (same && play.game) return drawPlay();
  play.game = null;
  drawSetup();
}

function closePlay() {
  document.getElementById("playOverlay").hidden = true;
  clearTimers();
  if (document.fullscreenElement) document.exitFullscreen();
}

function clearTimers() {
  play.timers.forEach(clearTimeout);
  play.timers.forEach(clearInterval);
  play.timers = [];
  document.onkeydown = null;
}

function toggleFullScreen() {
  const el = document.getElementById("playOverlay");
  if (document.fullscreenElement) document.exitFullscreen();
  else el.requestFullscreen?.();
}

// The questions are edited in place and the link changes with them; copying is tried, and said only when it worked
function showShare() {
  const box = document.getElementById("playShare");
  if (!box.hidden) { box.hidden = true; return; }
  play.questions = play.questions || defaultQuestions();
  box.hidden = false;
  drawQuestions();
}

function drawQuestions() {
  const list = document.getElementById("playQuestions");
  list.innerHTML = play.questions.map((q, i) => `<div class="play-question">
    <span>${i + 1}.</span><input type="text" maxlength="300" data-i="${i}" value="${escapeHtml(q)}" aria-label="Question ${i + 1}">
    <button type="button" class="play-seat-remove" data-i="${i}" aria-label="Remove">×</button></div>`).join("");
  list.querySelectorAll("input").forEach((el) => el.addEventListener("input", () => { play.questions[el.dataset.i] = el.value; updateLink(); }));
  list.querySelectorAll("button").forEach((el) => el.addEventListener("click", () => { play.questions.splice(el.dataset.i, 1); drawQuestions(); }));
  document.getElementById("playAddQuestion").hidden = play.questions.length >= 12;
  updateLink();
}

function updateLink() {
  document.getElementById("playShareInput").value = shareUrl();
  const n = play.questions.filter((q) => q.trim()).length;
  document.getElementById("playShareNote").textContent = `Whoever opens it plays this design${n ? ` and is asked ${n === 1 ? "this question" : `these ${n} questions`} at the end` : ""}; their canvas stays as it is. Their answers come back to you only if they send them.`;
}

function copyLink() {
  const input = document.getElementById("playShareInput");
  input.select();
  navigator.clipboard?.writeText(input.value).then(() => { document.getElementById("playShareNote").textContent = "Copied."; }, () => {});
}

// ── Setup: who plays ──

function drawSetup() {
  clearTimers();
  const d = play.design;
  const body = document.getElementById("playBody");
  const ids = Object.values(d.b).flat();
  if (!ids.length) {
    body.innerHTML = `<div class="phase-eyebrow">Play on screen</div><h1 class="phase-title">Nothing to play yet</h1>
      <p class="phase-intro">Put blocks on the canvas first, then press <em>Play</em>.</p>`;
    return;
  }
  const probe = createGame({ blocks: d.b, answers: d.a, seats: [{ name: "x", bot: true }, { name: "y", bot: true }], seed: 1 });
  play.seats = play.seats || [{ name: "Player 1", bot: false }, { name: "Player 2", bot: true }, { name: "Player 3", bot: true }];
  const needsGoal = ids.includes("set-your-own-goal");
  const needsValue = ids.includes("points-stand-for-values");
  body.innerHTML = `
    <div class="phase-eyebrow">Play on screen${play.shared ? " · a design shared with you" : ""}</div>
    <h1 class="phase-title">Play this game</h1>
    ${play.shared && d.q.length ? `<p class="play-private">Whoever shared this game asks ${d.q.length === 1 ? "one question" : `${d.q.length} questions`} at the end: ${d.q.map((q) => `“${escapeHtml(q)}”`).join(" ")} Your answers stay on this screen until you copy them and send them back.</p>` : ""}
    <p class="phase-intro">The screen plays every block it has a rule for, each written in code; nothing is generated. The blocks it cannot play are listed below for the people at the table. Players marked <em>fixed rules</em> are played by the screen, always choosing the move its rule values most.</p>
    <div class="play-columns">
      <div><div class="fam-equipment-label">The screen plays</div><ul class="play-list">${probe.played.map((id) => `<li>${escapeHtml(displayOf(id))}</li>`).join("") || "<li>a plain roll of the dice, since no block has a rule here</li>"}</ul></div>
      <div><div class="fam-equipment-label">You play at the table</div><ul class="play-list">${probe.offScreen.map((t) => `<li>${escapeHtml(t)}</li>`).join("") || "<li>Nothing: the screen plays it all.</li>"}</ul></div>
    </div>
    <div class="fam-equipment-label">Players</div>
    <div class="play-seats" id="playSeats"></div>
    <div class="phase-actions"><button class="k-btn-outline" type="button" id="playAddSeat">Add a player</button></div>
    ${needsValue ? `<label class="play-field">What do the points stand for? <input type="text" id="playValue" maxlength="30" placeholder="kindness"></label>` : ""}
    <div class="phase-actions play-start"><button class="k-btn-primary" type="button" id="playStart">Start</button></div>`;
  const seatsEl = document.getElementById("playSeats");
  const drawSeats = () => {
    seatsEl.innerHTML = play.seats.map((s, i) => `<div class="play-seat">
      <input type="text" value="${escapeHtml(s.name)}" maxlength="20" data-i="${i}" class="play-seat-name" aria-label="Name">
      <select data-i="${i}" class="play-seat-kind"><option value="person"${s.bot ? "" : " selected"}>Person</option><option value="bot"${s.bot ? " selected" : ""}>Fixed rules</option></select>
      ${needsGoal && !s.bot ? `<input type="text" data-i="${i}" class="play-seat-goal" maxlength="60" placeholder="What doing well means for you" value="${escapeHtml(s.goal || "")}">` : ""}
      ${play.seats.length > 2 ? `<button type="button" class="play-seat-remove" data-i="${i}" aria-label="Remove">×</button>` : ""}
    </div>`).join("");
    seatsEl.querySelectorAll(".play-seat-name").forEach((el) => el.addEventListener("input", () => { play.seats[el.dataset.i].name = el.value; }));
    seatsEl.querySelectorAll(".play-seat-goal").forEach((el) => el.addEventListener("input", () => { play.seats[el.dataset.i].goal = el.value; }));
    seatsEl.querySelectorAll(".play-seat-kind").forEach((el) => el.addEventListener("change", () => { play.seats[el.dataset.i].bot = el.value === "bot"; drawSeats(); }));
    seatsEl.querySelectorAll(".play-seat-remove").forEach((el) => el.addEventListener("click", () => { play.seats.splice(el.dataset.i, 1); drawSeats(); }));
    document.getElementById("playAddSeat").hidden = play.seats.length >= 5;
  };
  drawSeats();
  document.getElementById("playAddSeat").addEventListener("click", () => { play.seats.push({ name: `Player ${play.seats.length + 1}`, bot: true }); drawSeats(); });
  document.getElementById("playStart").addEventListener("click", () => {
    const value = document.getElementById("playValue")?.value.trim();
    startGame(value);
  });
}

function startGame(pointsName) {
  const seats = play.seats.map((s, i) => ({ name: s.name.trim() || `Player ${i + 1}`, bot: s.bot }));
  let carry = null;
  try { carry = JSON.parse(localStorage.getItem("boardgame_play_carry") || "null"); } catch (_) {}
  const ids = Object.values(play.design.b).flat();
  play.game = createGame({
    blocks: play.design.b, answers: play.design.a, seats, seed: Date.now() % 2147483647,
    pointsName, goals: play.seats.map((s) => s.goal || null), carry: ids.includes("irreversible-change") ? carry : null,
  });
  if (ids.includes("irreversible-change") && carry?.pool !== undefined) play.game.log.unshift({ round: 0, text: `This game starts where the last one ended: the ${play.game.names.pool} holds ${carry.pool}.` });
  play.viewer = null;
  drawPlay();
}

// ── The table ──

function drawPlay() {
  clearTimers();
  const g = play.game;
  if (g.over) return drawEnd();
  const a = g.ask;
  const body = document.getElementById("playBody");
  const persons = g.players.filter((p) => !p.bot);

  // Pass the screen when a person must decide something the others must not see
  if (a.player && !a.player.bot && g.private && persons.length > 1 && play.viewer !== a.player) {
    body.innerHTML = `<div class="play-curtain"><div class="phase-eyebrow">Pass the screen</div>
      <h1 class="phase-title">${escapeHtml(a.player.name)}'s move</h1>
      <p class="phase-intro">Press when only ${escapeHtml(a.player.name)} is looking.</p>
      <button class="k-btn-primary" type="button" id="playReveal">I am ${escapeHtml(a.player.name)}</button></div>`;
    document.getElementById("playReveal").addEventListener("click", () => { play.viewer = a.player; drawPlay(); });
    return;
  }
  if (a.player && !a.player.bot) play.viewer = a.player;

  body.innerHTML = `
    <div class="play-top">${statusLine(g)}</div>
    <div class="play-grid">
      <div class="play-main">
        <div class="play-decision" id="playDecision"></div>
        <div class="play-board">${boardHtml(g)}</div>
      </div>
      <div class="play-side">
        <div class="play-players">${g.players.map((p) => playerHtml(g, p)).join("")}</div>
        ${g.offScreen.length ? `<div class="play-offscreen"><div class="fam-equipment-label">At the table</div><ul>${g.offScreen.map((t) => `<li>${escapeHtml(t)}</li>`).join("")}</ul></div>` : ""}
        <div class="play-log"><div class="fam-equipment-label">What happened</div>${g.log.slice(-14).reverse().map((l) => `<p>${escapeHtml(l.text)}</p>`).join("")}</div>
      </div>
    </div>`;
  drawDecision(g, a);
}

function statusLine(g) {
  const bits = [`<strong>Round ${g.round}</strong>${g.rounds < 20 ? ` of ${g.rounds}` : ""}`];
  if (g.threat !== undefined) bits.push(`${escapeHtml(g.names.threat)}: ${g.threat} of ${g.limit}`);
  if (g.fire !== undefined) bits.push(`fire: ${g.fire}`);
  if (g.target !== undefined) bits.push(`goal: ${g.target}`);
  if (g.pool) bits.push(`${escapeHtml(g.names.pool)}: ${g.pool.level} of ${g.pool.cap}`);
  if (g.houseRule) bits.push(`house rule: ${escapeHtml(g.houseRule.text)}`);
  if (g.secretRule) bits.push(g.secretRule.found ? "secret rule found" : "a secret rule is in force");
  if (g.delayed.length) bits.push(`${g.delayed.reduce((s, d) => s + d.amount, 0)} ${escapeHtml(g.names.pts)} on their way`);
  return bits.join(" · ");
}

function playerHtml(g, p) {
  const open = !g.private || p === play.viewer;
  const bits = [];
  bits.push(`<strong>${g.scoresHidden ? "?" : p.score}</strong> ${escapeHtml(g.names.pts)}`);
  if (p.coins || g.players.some((q) => q.coins)) bits.push(`${p.coins} ${escapeHtml(g.names.coin)}`);
  if (p.life !== null) bits.push(`${Math.max(0, p.life)} life`);
  if (g.track) bits.push(`space ${p.pos + 1}${p.laps ? `, lap ${p.laps + 1}` : ""}`);
  if (p.hand.length) bits.push(open ? `hand: ${p.hand.map(cardHtml).join(" ")}` : `${p.hand.length} cards in hand`);
  if (p.cards.length) bits.push(`kept: ${p.cards.map(cardHtml).join(" ")}`);
  if (p.role) bits.push(escapeHtml(p.role.text || p.role.name));
  if (p.side !== undefined && !g.sidesSecret) bits.push(escapeHtml(g.sideNames[p.side]));
  return `<div class="play-player${p === g.ask?.player ? " now" : ""}${p.out ? " out" : ""}">
    <div class="play-player-name"><b class="play-seat-no">${p.seat + 1}</b> ${escapeHtml(p.name)}${p.bot ? ` <span class="play-tag">fixed rules</span>` : ""}${p.out ? ` <span class="play-tag">out</span>` : ""}</div>
    <div class="play-player-bits">${bits.join(" · ")}</div>
    ${p.grid ? gridHtml(p.grid, 3) : ""}</div>`;
}

function cardHtml(c) {
  return c ? `<span class="play-card" style="--c:${CARD_COLOURS[c.c]}">${c.n}</span>` : "";
}

function gridHtml(cells, size) {
  return `<div class="play-mini" style="grid-template-columns:repeat(${size},1fr)">${cells.map((v) => `<span style="${v === null ? "" : `background:${CARD_COLOURS[v]}`}"></span>`).join("")}</div>`;
}

function boardHtml(g) {
  const parts = [];
  if (g.track) parts.push(`<div class="fam-equipment-label">The ${escapeHtml(g.names.track)}</div><div class="play-track">${g.track.map((cell, i) => {
    const here = g.players.filter((p) => p.pos === i && !p.out).map((p) => `<b title="${escapeHtml(p.name)}">${p.seat + 1}</b>`).join("");
    const mark = cell.kind ? (cell.shown ? cell.kind : "?") : i === g.track.length - 1 ? "end" : "";
    return `<span class="play-cell${cell.kind ? " marked" : ""}"><i>${i + 1}</i>${escapeHtml(mark)}${here}</span>`;
  }).join("")}</div>`);
  if (g.market) parts.push(`<div class="fam-equipment-label">Cards on offer</div><div class="play-market">${g.market.map((c) => c ? (g.marketHidden ? `<span class="play-card back">?</span>` : cardHtml(c)) : "").join("")}<span class="play-note">${g.deckLeft()} in the deck · colours: ${g.names.colours.map((n, i) => `<span style="color:${CARD_COLOURS[i]}">${escapeHtml(n)}</span>`).join(", ")}</span></div>`);
  if (g.regions) parts.push(`<div class="fam-equipment-label">Areas</div><table class="play-table"><tr><th></th>${g.players.map((p) => `<th>${escapeHtml(p.name)}</th>`).join("")}</tr>${g.regions.map((r) => `<tr><td>${escapeHtml(r.name)} (${r.value})</td>${r.pieces.map((k) => `<td>${k || ""}</td>`).join("")}</tr>`).join("")}</table>`);
  if (g.spots) parts.push(`<div class="fam-equipment-label">Places for workers</div><div class="play-spots">${g.spots.map((s) => `<span class="play-spot${s.gone ? " gone" : ""}">${escapeHtml(s.name)}${s.takenBy.length ? `: ${s.takenBy.map((p) => escapeHtml(p.name)).join(", ")}` : ""}${s.gone ? " (worn out)" : ""}</span>`).join("")}</div>`);
  if (g.tiles) parts.push(`<div class="fam-equipment-label">Tiles</div><div class="play-tiles">${g.tiles.map((row, r) => row.map((v, c) => `<span style="${v === null ? "" : `background:${CARD_COLOURS[v]}`}">${v === null ? `${"ABCDEFG"[c]}${r + 1}` : ""}</span>`).join("")).join("")}</div>`);
  if (g.clues) parts.push(`<div class="fam-equipment-label">The hidden card</div><p class="play-note">${g.clues.length ? g.clues.map((c) => escapeHtml(c.text)).join(" ") : "Nothing asked yet."}</p>`);
  return parts.join("");
}

function privateHtml(g, p) {
  const bits = [];
  if (p.secretGoal) bits.push(`Your secret goal: ${escapeHtml(p.secretGoal.text)}`);
  if (p.traitor) bits.push("You are the traitor: you win if the others lose.");
  if (g.sidesSecret) bits.push(`You are on ${escapeHtml(g.sideNames[p.side])}.`);
  if (g.private && p.hand.length) bits.push(`Your hand: ${p.hand.map(cardHtml).join(" ")}`);
  return bits.length ? `<div class="play-private"><span class="play-tag">only you see this</span> ${bits.join(" · ")}</div>` : "";
}

function drawDecision(g, a) {
  const box = document.getElementById("playDecision");
  if (a.grab) return drawGrab(g, a, box);
  const p = a.player;
  if (p.bot) {
    box.innerHTML = `<p class="play-prompt">${escapeHtml(p.name)} is choosing…</p>`;
    play.timers.push(setTimeout(() => { g.choose(g.botChoice(a)); drawPlay(); }, BOT_DELAY));
    return;
  }
  box.innerHTML = `${privateHtml(g, p)}<p class="play-prompt">${escapeHtml(a.prompt)}</p>
    <div class="play-options">${a.options.map((o, i) => `<button type="button" class="k-btn-outline play-option" data-i="${i}">${escapeHtml(o.label)}</button>`).join("")}</div>
    <p class="play-note" id="playClock"></p>`;
  const buttons = [...box.querySelectorAll(".play-option")];
  const choose = (o) => { clearTimers(); g.choose(o); drawPlay(); };
  buttons.forEach((b) => b.addEventListener("click", () => choose(a.options[b.dataset.i])));

  // Sedated: a pause before any move; timed turns: a clock, after which a move is made at random
  const pause = g.pauseSeconds();
  if (pause) {
    buttons.forEach((b) => { b.disabled = true; });
    document.getElementById("playClock").textContent = "Breathe before you move…";
    play.timers.push(setTimeout(() => { buttons.forEach((b) => { b.disabled = false; }); startClock(); }, pause * 1000));
  } else startClock();

  function startClock() {
    let left = g.timerSeconds();
    const clock = document.getElementById("playClock");
    if (!left) { clock.textContent = ""; return; }
    clock.textContent = `${left} seconds`;
    play.timers.push(setInterval(() => {
      left--;
      clock.textContent = `${left} seconds`;
      if (left <= 0) {
        const o = a.options[Math.floor(Math.random() * a.options.length)];
        g.log.push({ round: g.round, text: `Time ran out; a move was made for ${p.name}: ${o.label}.` });
        choose(o);
      }
    }, 1000));
  }
}

// No turns: the first to press moves. Each person has a key, and can tap their name instead.
function drawGrab(g, a, box) {
  const people = a.players.filter((p) => !p.bot);
  box.innerHTML = `<p class="play-prompt">${escapeHtml(a.prompt)}</p>
    <div class="play-options">${people.map((p, i) => `<button type="button" class="k-btn-primary play-grab" data-i="${i}">${escapeHtml(p.name)} · key ${GRAB_KEYS[i]}</button>`).join("")}</div>`;
  let done = false;
  const win = (p) => { if (done) return; done = true; clearTimers(); g.choose(p); drawPlay(); };
  box.querySelectorAll(".play-grab").forEach((b) => b.addEventListener("click", () => win(people[b.dataset.i])));
  document.onkeydown = (e) => { const i = GRAB_KEYS.indexOf(e.key.toUpperCase()); if (i >= 0 && people[i]) win(people[i]); };
  for (const p of a.players.filter((q) => q.bot)) play.timers.push(setTimeout(() => win(p), 700 + Math.random() * 1200));
}

// ── The end ──

function drawEnd() {
  const g = play.game, o = g.over;
  if (o.carry) try { localStorage.setItem("boardgame_play_carry", JSON.stringify(o.carry)); } catch (_) {}
  const ids = Object.values(play.design.b).flat();
  const feelings = play.design.f.map(displayOf);
  document.getElementById("playBody").innerHTML = `
    <div class="phase-eyebrow">The game is over · round ${g.round}</div>
    <h1 class="phase-title">${escapeHtml(o.lines[0])}</h1>
    <div class="play-end">${o.lines.slice(1).map((l) => `<p>${escapeHtml(l)}</p>`).join("")}</div>
    <table class="play-table"><tr><th>Player</th><th>${escapeHtml(g.names.pts)}</th>${g.track ? "<th>space</th>" : ""}${o.scores.some((s) => s.life !== null) ? "<th>life</th>" : ""}</tr>
      ${o.scores.map((s) => `<tr><td>${escapeHtml(s.name)}${s.out ? " (out)" : ""}</td><td>${s.score}</td>${g.track ? `<td>${s.space}</td>` : ""}${s.life !== null ? `<td>${Math.max(0, s.life)}</td>` : ""}</tr>`).join("")}</table>
    ${ids.includes("rules-make-an-argument") && o.rewarded.length ? `<div class="fam-equipment-label">What your rules rewarded</div><p>${o.rewarded.map((r) => `${escapeHtml(r.what)} ${r.share}%`).join(" · ")}</p>` : ""}
    ${ids.includes("debrief") ? `<div class="fam-notice"><div class="fam-notice-label">Talk it through</div><ul><li>What happened?</li><li>Why did it happen?</li><li>How is it like the real thing?</li><li>What would change if one rule changed?</li></ul></div>` : ""}
    ${feelings.length && !(play.shared && play.design.q.length) ? `<div class="fam-notice"><div class="fam-notice-label">${play.shared ? "Its makers wanted it" : "You wanted it"} to feel ${escapeHtml(feelings.join(", "))}</div><ul><li>Did it? When, and when not?</li></ul></div>` : ""}
    ${o.carry ? `<p class="play-note">The ${escapeHtml(g.names.pool)} stays at ${o.carry.pool} for the next game on this device.</p>` : ""}
    ${play.shared && play.design.q.length ? `<div class="play-reply"><div class="fam-equipment-label">Questions from whoever shared this game</div>
      ${play.design.q.map((q, i) => `<label class="play-reply-q"><span>${i + 1}. ${escapeHtml(q)}</span><textarea data-i="${i}" rows="2">${escapeHtml(play.replies[i] || "")}</textarea></label>`).join("")}
      <div class="phase-actions"><button class="k-btn-primary" type="button" id="playCopyReply">Copy my answers</button></div>
      <textarea class="play-reply-text" id="playReplyText" readonly hidden></textarea>
      <p class="play-note" id="playReplyNote">Nothing is sent from here. Copy your answers, with everything that happened in the game, and send them back however you like.</p></div>` : ""}
    <div class="phase-actions play-start">
      <button class="k-btn-primary" type="button" id="playAgain">Play again</button>
      <button class="k-btn-outline" type="button" id="playSetupBtn">Change players</button>
    </div>
    <div class="play-log"><div class="fam-equipment-label">Everything that happened</div>${g.log.map((l) => `<p>${escapeHtml(l.text)}</p>`).join("")}</div>`;
  document.getElementById("playAgain").addEventListener("click", () => startGame(g.names.pts));
  document.querySelectorAll(".play-reply-q textarea").forEach((el) => el.addEventListener("input", () => { play.replies[el.dataset.i] = el.value; }));
  document.getElementById("playCopyReply")?.addEventListener("click", () => {
    const text = [
      "Playtest answers for a game made on boardgameBuilder",
      `Blocks: ${ids.map(displayOf).join(", ")}`,
      `Result: ${o.lines.slice(0, 2).join(" ")} (${g.players.length} players, ${g.players.filter((p) => !p.bot).length} of them people)`,
      ...play.design.q.map((q, i) => `\n${i + 1}. ${q}\n${(play.replies[i] || "").trim() || "(no answer)"}`),
      "\nEverything that happened",
      ...g.log.map((l) => l.text),
    ].join("\n");
    const box = document.getElementById("playReplyText");
    box.value = text; box.hidden = false; box.select();
    navigator.clipboard?.writeText(text).then(() => { document.getElementById("playReplyNote").textContent = "Copied. Send it back however you like."; }, () => {});
  });
  document.getElementById("playSetupBtn").addEventListener("click", () => { play.game = null; drawSetup(); });
}
