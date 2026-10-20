// boardgameBuilder — frontend
// Local-only. Talks to FastAPI on same origin.
// Persists session to localStorage so refresh does not lose the design.

const STORAGE_KEY = "gameelementcombiner_multi_state_v1";

// A slot stacks blocks when its dimension says so in palette.py ("multi"); all others hold one.
const isMultiSlot = (dimId) => Boolean(state.dimensions.find((d) => d.id === dimId)?.multi);

const state = {
  dimensions: [],        // loaded from /palette
  feelings: [],          // loaded from /palette
  mechanics: {},         // { [dimensionId]: elementId | elementId[] } — array iff isMultiSlot(dim)
  chosenFeelings: [],    // [elementId, ...]
  previousMechanics: {}, // snapshot from end of last turn
  previousFeelings: [],
  turnNumber: 0,
  locked: false,
  pending: false,
  turnHistory: [],       // [{ turn: N, narration, source, kind: "turn"|"complete" }, ...]
  answers: {},           // { [blockId]: { [questionKey]: optionValue } } — answers to the questions asked when a block is placed
  tests: {},             // { [testKey]: { feelings, match, note } } — notes from the part tests
  pendingAnswers: null,
};

// ── Persistence ────────────────────────────────────────────────────

function snapshot() {
  return {
    mechanics: state.mechanics,
    chosenFeelings: state.chosenFeelings,
    previousMechanics: state.previousMechanics,
    previousFeelings: state.previousFeelings,
    turnNumber: state.turnNumber,
    locked: state.locked,
    turnHistory: state.turnHistory,
    answers: state.answers,
    tests: state.tests,
    savedAt: new Date().toISOString(),
  };
}

function saveState() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(snapshot()));
  } catch (err) {
    console.warn("Could not save state:", err);
  }
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return false;
    const saved = JSON.parse(raw);
    if (!saved || typeof saved !== "object") return false;

    state.mechanics = saved.mechanics || {};
    state.chosenFeelings = Array.isArray(saved.chosenFeelings) ? saved.chosenFeelings : [];
    state.previousMechanics = saved.previousMechanics || {};
    state.previousFeelings = Array.isArray(saved.previousFeelings) ? saved.previousFeelings : [];
    state.turnNumber = typeof saved.turnNumber === "number" ? saved.turnNumber : 0;
    state.locked = !!saved.locked;
    state.turnHistory = Array.isArray(saved.turnHistory) ? saved.turnHistory : [];
    state.answers = saved.answers && typeof saved.answers === "object" ? saved.answers : {};
    state.tests = saved.tests && typeof saved.tests === "object" ? saved.tests : {};

    // A block that has moved to another group since the design was saved goes with it (real-time span moved to Timing)
    for (const [dimId, value] of Object.entries(state.mechanics)) {
      for (const bid of [].concat(value)) {
        const home = state.dimensions.find((d) => d.blocks.some((b) => b.id === bid));
        if (home && home.id !== dimId) {
          state.mechanics[home.id] = home.multi ? [].concat(state.mechanics[home.id] || [], bid) : bid;
          state.mechanics[dimId] = Array.isArray(value) ? value.filter((x) => x !== bid) : null;
        }
      }
    }
    // Drop mechanics that reference dimensions no longer in the palette;
    // for multi-slots, keep an array; for single-slots, keep a string.
    for (const dimId of Object.keys(state.mechanics)) {
      const dim = state.dimensions.find((d) => d.id === dimId);
      if (!dim) { delete state.mechanics[dimId]; continue; }
      const value = state.mechanics[dimId];
      if (isMultiSlot(dimId)) {
        const arr = Array.isArray(value) ? value : (value ? [value] : []);
        const filtered = arr.filter((bid) => dim.blocks.find((b) => b.id === bid));
        if (filtered.length === 0) delete state.mechanics[dimId];
        else state.mechanics[dimId] = filtered;
      } else {
        const blockId = Array.isArray(value) ? value[0] : value;
        if (!blockId || !dim.blocks.find((b) => b.id === blockId)) {
          delete state.mechanics[dimId];
        } else {
          state.mechanics[dimId] = blockId;
        }
      }
    }
    state.chosenFeelings = state.chosenFeelings.filter((fid) =>
      state.feelings.find((f) => f.id === fid)
    );
    return true;
  } catch (err) {
    console.warn("Could not load state:", err);
    return false;
  }
}

function clearState() {
  try { localStorage.removeItem(STORAGE_KEY); } catch (_) {}
}

function pingSaved() {
  const el = document.getElementById("savedIndicator");
  if (!el) return;
  el.classList.add("show");
  clearTimeout(pingSaved._t);
  pingSaved._t = setTimeout(() => el.classList.remove("show"), 1200);
}

// ── Load palette on start ──────────────────────────────────────────

async function loadPalette() {
  const resp = await fetch("/palette");
  const data = await resp.json();
  state.dimensions = data.dimensions;
  state.feelings = data.feelings;
  renderPalette();
  renderMechanicsGrid();
}

function renderPalette() {
  const container = document.getElementById("paletteBody");
  container.innerHTML = "";

  // Feelings group first, in the same order as the canvas: intent above mechanics
  container.appendChild(buildPaletteGroup({
    dim: "feeling",
    letter: "F",
    title: "Feelings — what we want",
    description: "Drag these onto the feelings shelf at the top of the canvas.",
    blocks: state.feelings.map(f => ({ ...f, dim: "feeling" })),
    isFeeling: true,
  }));

  // Mechanic dimensions
  for (const dim of state.dimensions) {
    container.appendChild(buildPaletteGroup({
      dim: dim.id,
      letter: dimensionLetter(dim.id),
      title: dim.display,
      description: dim.description,
      blocks: dim.blocks.map(b => ({ ...b, dim: dim.id })),
    }));
  }
  filterPalette();
}

// Search box: shows the blocks whose name or description holds the words typed,
// or every block of a group whose title holds them
function filterPalette() {
  const words = document.getElementById("paletteSearch").value.toLowerCase().split(/\s+/).filter(Boolean);
  const has = (text) => words.every((w) => text.toLowerCase().includes(w));
  let shown = 0;
  for (const group of document.querySelectorAll("#paletteBody .palette-group")) {
    const groupMatch = has(group.querySelector(".group-title").textContent);
    let inGroup = 0;
    for (const block of group.querySelectorAll(".block")) {
      const meta = lookupBlockMeta(block.dataset.blockId, block.dataset.dim);
      block.hidden = !(groupMatch || has(block.textContent + " " + (meta.description || "")));
      if (!block.hidden) inGroup++;
    }
    group.hidden = inGroup === 0;
    shown += inGroup;
  }
  document.getElementById("paletteNoMatch").hidden = shown > 0;
}

document.getElementById("paletteSearch").addEventListener("input", filterPalette);
document.getElementById("paletteSearch").addEventListener("keydown", (e) => {
  if (e.key === "Escape") { e.target.value = ""; filterPalette(); }
});

function buildPaletteGroup({ dim, letter, title, description, blocks, isFeeling }) {
  const group = document.createElement("div");
  group.className = "palette-group" + (isFeeling ? " group-feeling" : "");
  group.dataset.dim = dim;

  const header = document.createElement("div");
  header.className = "group-header";

  const letterEl = document.createElement("span");
  letterEl.className = "group-letter";
  letterEl.textContent = letter;
  header.appendChild(letterEl);

  const titleEl = document.createElement("span");
  titleEl.className = "group-title";
  titleEl.textContent = title;
  header.appendChild(titleEl);

  group.appendChild(header);

  const desc = document.createElement("p");
  desc.className = "group-description";
  desc.textContent = description;
  group.appendChild(desc);

  const list = document.createElement("div");
  list.className = "block-list";
  for (const b of blocks) {
    list.appendChild(createBlock(b.id, b.display, b.dim, { meta: b }));
  }
  group.appendChild(list);

  return group;
}

// ── Block meta lookup (description + svg from /palette payload) ────

function lookupBlockMeta(blockId, dim) {
  if (dim === "feeling") {
    return state.feelings.find((f) => f.id === blockId) || {};
  }
  for (const d of state.dimensions) {
    const found = (d.blocks || []).find((b) => b.id === blockId);
    if (found) return found;
  }
  return {};
}

function dimensionDisplayLabel(dim) {
  if (dim === "feeling") return "Feeling";
  const found = state.dimensions.find((d) => d.id === dim);
  return found ? found.display : "Block";
}

function dimensionLetter(dimId) {
  return {
    "core-mechanic": "C",
    "victory-condition": "V",
    "player-interaction": "P",
    "chance-skill": "S",
    "theme": "T",
    "information": "I",
    "timing": "W",
    "simulation": "M",
  }[dimId] || "·";
}

function createBlock(id, display, dim, { inSlot = false, meta = null } = {}) {
  const el = document.createElement("div");
  el.className = "block" + (inSlot ? " block-in-slot" : "");
  el.dataset.blockId = id;
  el.dataset.dim = dim;
  el.draggable = !state.locked;

  const label = document.createElement("span");
  label.className = "block-label";
  label.textContent = display;
  el.appendChild(label);

  // Info button (?). Tap → modal with description + SVG.
  const infoBtn = document.createElement("button");
  infoBtn.type = "button";
  infoBtn.className = "info-btn";
  infoBtn.textContent = "?";
  infoBtn.title = `What does “${display}” mean?`;
  infoBtn.draggable = false;
  infoBtn.addEventListener("click", (e) => {
    e.stopPropagation();
    e.preventDefault();
    go(`blocks/${id}`);
  });
  // Stop drag from initiating on the info button
  infoBtn.addEventListener("mousedown", (e) => e.stopPropagation());
  infoBtn.addEventListener("dragstart", (e) => { e.preventDefault(); e.stopPropagation(); });
  el.appendChild(infoBtn);

  if (inSlot) {
    const x = document.createElement("span");
    x.className = "remove-x";
    x.textContent = "×";
    x.title = "remove";
    x.addEventListener("click", (e) => {
      e.stopPropagation();
      removeFromCanvas(id, dim);
    });
    el.appendChild(x);
  }

  el.addEventListener("dragstart", (e) => {
    if (state.locked) { e.preventDefault(); return; }
    e.dataTransfer.setData("application/x-gc-block", JSON.stringify({ id, dim, fromCanvas: inSlot }));
    e.dataTransfer.effectAllowed = "move";
    el.classList.add("dragging");
  });
  el.addEventListener("dragend", () => el.classList.remove("dragging"));
  return el;
}

// ── Block info modal ──────────────────────────────────────────────

function openBlockModal(blockId, dim) {
  const meta = lookupBlockMeta(blockId, dim);
  const display = meta.display || blockId;
  const description = meta.description || "No description yet.";
  const svgMarkup = meta.svg || "";

  document.getElementById("blockModalEyebrow").textContent = dimensionDisplayLabel(dim);
  document.getElementById("blockModalTitle").textContent = display;
  document.getElementById("blockModalDesc").textContent = description;

  const svgWrap = document.getElementById("blockModalSvg");
  svgWrap.innerHTML = svgMarkup;
  if (!svgMarkup) svgWrap.style.display = "none";
  else svgWrap.style.display = "";

  const modal = document.getElementById("blockModal");
  modal.hidden = false;
}

function closeBlockModal() {
  document.getElementById("blockModal").hidden = true;
}

// ── Onboarding ─────────────────────────────────────────────────────

const ONBOARDED_KEY = "boardgame_onboarded_v1";

function openOnboarding() {
  document.getElementById("onboarding").hidden = false;
}

function closeOnboarding() {
  document.getElementById("onboarding").hidden = true;
  try { localStorage.setItem(ONBOARDED_KEY, "1"); } catch (_) {}
}

function seenOnboarding() {
  try { return localStorage.getItem(ONBOARDED_KEY) === "1"; } catch (_) { return false; }
}

// ── Mechanics grid (one slot per dimension, dimension-gated) ────────

function renderMechanicsGrid() {
  const grid = document.getElementById("mechanicsGrid");
  grid.innerHTML = "";
  for (const dim of state.dimensions) {
    const slot = document.createElement("div");
    slot.className = "mechanic-slot";
    slot.dataset.dim = dim.id;

    const multi = isMultiSlot(dim.id);
    if (multi) slot.classList.add("multi");

    // Slot label (mono, persistent)
    const lbl = document.createElement("div");
    lbl.className = "slot-label";
    const lLetter = document.createElement("span");
    lLetter.className = "slot-letter";
    lLetter.textContent = dimensionLetter(dim.id);
    const lText = document.createElement("span");
    lText.textContent = dim.slot_label;
    const lCard = document.createElement("span");
    lCard.className = "slot-cardinality" + (multi ? " many" : "");
    lCard.textContent = multi ? "many" : "1×";
    lCard.title = multi
      ? "this slot holds many blocks — drop more to stack them"
      : "this slot holds one block";
    lbl.appendChild(lLetter);
    lbl.appendChild(lText);
    lbl.appendChild(lCard);
    slot.appendChild(lbl);

    // Slot body (block(s) or empty hint)
    const body = document.createElement("div");
    body.className = "slot-body" + (multi ? " slot-body-multi" : "");

    const value = state.mechanics[dim.id];
    const filledIds = multi
      ? (Array.isArray(value) ? value : [])
      : (value ? [value] : []);

    if (filledIds.length > 0) {
      slot.classList.add("filled");
      for (const fid of filledIds) {
        const block = dim.blocks.find((b) => b.id === fid);
        if (block) {
          // A block and its "say how it works" button stay together as one item
          const item = document.createElement("div");
          item.className = "slot-item";
          item.appendChild(createBlock(block.id, block.display, dim.id, { inSlot: true }));
          if ((block.questions || []).length) {
            const how = document.createElement("button");
            how.type = "button";
            how.className = "slot-config";
            how.textContent = answerSummary(block.id) || "say how it works";
            how.title = answerSummary(block.id) || `How ${block.display} works in your game`;
            how.disabled = state.locked;
            how.addEventListener("click", () => openQuestions(block.id));
            item.appendChild(how);
          }
          body.appendChild(item);
        }
      }
      if (multi) {
        const more = document.createElement("span");
        more.className = "slot-more-hint";
        more.textContent = "drop another to stack";
        body.appendChild(more);
      }
    } else {
      const hint = document.createElement("span");
      hint.className = "slot-empty-hint";
      hint.textContent = multi ? "drop one or more blocks here" : "drop one block here";
      body.appendChild(hint);
    }
    slot.appendChild(body);

    slot.addEventListener("dragover", (e) => {
      if (state.locked) return;
      e.preventDefault();
      slot.classList.add("drop-active");
    });
    slot.addEventListener("dragleave", () => slot.classList.remove("drop-active"));
    slot.addEventListener("drop", (e) => {
      if (state.locked) return;
      e.preventDefault();
      slot.classList.remove("drop-active");
      const data = JSON.parse(e.dataTransfer.getData("application/x-gc-block") || "{}");
      if (!data.id || data.dim !== dim.id) return;
      if (multi) {
        const current = Array.isArray(state.mechanics[dim.id]) ? state.mechanics[dim.id] : [];
        // Append unless block is already present in this slot.
        if (!current.includes(data.id)) {
          state.mechanics[dim.id] = [...current, data.id];
        }
      } else {
        if (state.mechanics[dim.id] && state.mechanics[dim.id] !== data.id) delete state.answers[state.mechanics[dim.id]];
        state.mechanics[dim.id] = data.id;
      }
      renderMechanicsGrid();
      saveState();
      pingSaved();
      if ((lookupBlockMeta(data.id).questions || []).length && !state.answers[data.id]) openQuestions(data.id);
    });

    grid.appendChild(slot);
  }
  if (!document.querySelector('[data-panel="tests"]').hidden) renderTests();
}

// ── Feelings shelf ────────────────────────────────────────────────

function renderFeelingsShelf() {
  const shelf = document.getElementById("feelingsShelf");
  shelf.innerHTML = "";
  if (state.chosenFeelings.length === 0) {
    const hint = document.createElement("div");
    hint.className = "empty-hint";
    hint.textContent = "drag feeling-blocks here";
    shelf.appendChild(hint);
    return;
  }
  for (const feelingId of state.chosenFeelings) {
    const f = state.feelings.find((x) => x.id === feelingId);
    if (!f) continue;
    shelf.appendChild(createBlock(f.id, f.display, "feeling", { inSlot: true }));
  }
}

function setupFeelingsDropZone() {
  const shelf = document.getElementById("feelingsShelf");
  shelf.addEventListener("dragover", (e) => {
    if (state.locked) return;
    e.preventDefault();
    shelf.classList.add("drop-active");
  });
  shelf.addEventListener("dragleave", () => shelf.classList.remove("drop-active"));
  shelf.addEventListener("drop", (e) => {
    if (state.locked) return;
    e.preventDefault();
    shelf.classList.remove("drop-active");
    const data = JSON.parse(e.dataTransfer.getData("application/x-gc-block") || "{}");
    if (!data.id || data.dim !== "feeling") return;
    if (!state.chosenFeelings.includes(data.id)) {
      state.chosenFeelings.push(data.id);
    }
    renderFeelingsShelf();
    saveState();
    pingSaved();
  });
}

// ── Remove block handlers ─────────────────────────────────────────

function removeFromCanvas(id, dim) {
  if (state.locked) return;
  delete state.answers[id];
  if (dim === "feeling") {
    state.chosenFeelings = state.chosenFeelings.filter((x) => x !== id);
    renderFeelingsShelf();
  } else {
    if (isMultiSlot(dim)) {
      const current = Array.isArray(state.mechanics[dim]) ? state.mechanics[dim] : [];
      const next = current.filter((x) => x !== id);
      if (next.length === 0) delete state.mechanics[dim];
      else state.mechanics[dim] = next;
    } else if (state.mechanics[dim] === id) {
      delete state.mechanics[dim];
    }
    renderMechanicsGrid();
  }
  saveState();
  pingSaved();
}

// ── Turn handlers ─────────────────────────────────────────────────

function flattenMechanics(mechanicsObj) {
  const out = [];
  for (const v of Object.values(mechanicsObj || {})) {
    if (Array.isArray(v)) out.push(...v);
    else if (v) out.push(v);
  }
  return out;
}

function buildCanvasPayload(from = "current") {
  if (from === "current") {
    return {
      mechanics: flattenMechanics(state.mechanics),
      feelings: state.chosenFeelings.slice(),
      answers: state.answers,
      tests: state.tests,
    };
  }
  return {
    mechanics: flattenMechanics(state.previousMechanics),
    feelings: state.previousFeelings.slice(),
  };
}

async function onIterate() {
  if (state.locked || state.pending) return;
  state.pending = true;
  setButtonsEnabled(false);
  showThinking();

  const payload = {
    canvas: buildCanvasPayload("current"),
    previous: buildCanvasPayload("previous"),
  };

  try {
    const resp = await fetch("/narrate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    state.turnNumber += 1;
    document.getElementById("turnIndicator").textContent = `Turn ${state.turnNumber}`;

    hideThinking();
    const turnEntry = {
      turn: state.turnNumber,
      narration: data.narration,
      source: data.source,
      kind: "turn",
    };
    state.turnHistory.push(turnEntry);
    renderTurnEntry(turnEntry);

    // Snapshot state for next diff (deep copy arrays so multi-slots don't share refs)
    state.previousMechanics = {};
    for (const [k, v] of Object.entries(state.mechanics)) {
      state.previousMechanics[k] = Array.isArray(v) ? v.slice() : v;
    }
    state.previousFeelings = state.chosenFeelings.slice();

    saveState();
    pingSaved();
  } catch (err) {
    hideThinking();
    appendSystemMessage(`Something went wrong: ${err.message}`);
  } finally {
    state.pending = false;
    setButtonsEnabled(true);
  }
}

async function onComplete() {
  if (state.locked || state.pending) return;
  state.pending = true;
  setButtonsEnabled(false);
  showThinking("Writing your game's summary...");

  const payload = {
    canvas: buildCanvasPayload("current"),
    previous: buildCanvasPayload("previous"),
  };

  try {
    const resp = await fetch("/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await resp.json();
    hideThinking();
    const entry = {
      turn: state.turnNumber,
      narration: data.narration,
      source: data.source,
      kind: "complete",
    };
    state.turnHistory.push(entry);
    renderCompletionEntry(entry);
    state.locked = true;
    applyLockedUi();
    saveState();
  } catch (err) {
    hideThinking();
    appendSystemMessage(`Something went wrong on complete: ${err.message}`);
  } finally {
    state.pending = false;
    if (!state.locked) setButtonsEnabled(true);
  }
}

// ── Feedback rendering ────────────────────────────────────────────

function clearWelcome() {
  const scroll = document.getElementById("feedbackScroll");
  const welcome = scroll.querySelector(".feedback-welcome");
  if (welcome) welcome.remove();
}

function renderTurnEntry(entry) {
  clearWelcome();
  const scroll = document.getElementById("feedbackScroll");
  const block = document.createElement("div");
  block.className = "turn-block";
  const body = document.createElement("div");
  body.className = "turn-block-body";

  const header = document.createElement("div");
  header.className = "turn-number";
  header.textContent = `Turn ${entry.turn}`;

  const narration = document.createElement("div");
  narration.className = "turn-narration";
  narration.textContent = entry.narration;

  const source = document.createElement("div");
  source.className = "source-tag";
  source.textContent = `source · ${entry.source}`;

  body.appendChild(header);
  body.appendChild(narration);
  body.appendChild(source);
  block.appendChild(body);

  scroll.appendChild(block);
  scroll.scrollTop = scroll.scrollHeight;
}

function renderCompletionEntry(entry) {
  clearWelcome();
  const scroll = document.getElementById("feedbackScroll");
  const block = document.createElement("div");
  block.className = "turn-block complete-summary";
  const body = document.createElement("div");
  body.className = "turn-block-body";

  const header = document.createElement("div");
  header.className = "turn-number";
  header.textContent = "Final — your game";

  const narration = document.createElement("div");
  narration.className = "turn-narration";
  narration.textContent = entry.narration;

  const link = document.createElement("a");
  link.className = "start-again";
  link.textContent = "Start again";
  link.href = "#";
  link.addEventListener("click", (e) => { e.preventDefault(); onStartFresh(); });

  body.appendChild(header);
  body.appendChild(narration);
  body.appendChild(link);
  block.appendChild(body);

  scroll.appendChild(block);
  scroll.scrollTop = scroll.scrollHeight;
}

function renderHistoryFromState() {
  if (!state.turnHistory.length) return;
  for (const entry of state.turnHistory) {
    if (entry.kind === "complete") renderCompletionEntry(entry);
    else renderTurnEntry(entry);
  }
}

function appendSystemMessage(msg) {
  const scroll = document.getElementById("feedbackScroll");
  const div = document.createElement("div");
  div.className = "turn-block";
  div.innerHTML = `<div class="turn-narration"><em>${escapeHtml(msg)}</em></div>`;
  scroll.appendChild(div);
  scroll.scrollTop = scroll.scrollHeight;
}

function showThinking(msg = "Thinking...") {
  hideThinking();
  const scroll = document.getElementById("feedbackScroll");
  const div = document.createElement("div");
  div.className = "thinking";
  div.id = "thinkingIndicator";
  div.textContent = msg;
  scroll.appendChild(div);
  scroll.scrollTop = scroll.scrollHeight;
}
function hideThinking() {
  const t = document.getElementById("thinkingIndicator");
  if (t) t.remove();
}

function setButtonsEnabled(on) {
  document.getElementById("iterateBtn").disabled = !on;
  document.getElementById("completeBtn").disabled = !on;
}

function applyLockedUi() {
  document.querySelector(".app-main").classList.add("locked");
  document.getElementById("feedbackActions").style.display = "none";
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

// ── Questions asked when a block is placed ───────────────────────
// Carried from the April 2026 demo. The answers are the designers' own; they show under the block, are saved, and go into the closing summary.

function answerSummary(blockId, sep = " · ") {
  const picked = state.answers[blockId] || {};
  return (lookupBlockMeta(blockId).questions || [])
    .map((q) => (q.options.find((o) => o.v === picked[q.key]) || {}).n)
    .filter(Boolean).map((n) => n.toLowerCase()).join(sep);
}

function openQuestions(blockId) {
  const meta = lookupBlockMeta(blockId);
  state.pendingAnswers = { blockId, raw: { ...(state.answers[blockId] || {}) } };
  document.getElementById("configModalTitle").textContent = meta.display;
  const body = document.getElementById("configModalBody");
  body.innerHTML = "";
  const what = document.createElement("p");
  what.className = "config-q-label";
  what.textContent = meta.description || "";
  body.appendChild(what);
  for (const q of meta.questions) {
    const qEl = document.createElement("div");
    qEl.className = "config-q";
    const label = document.createElement("div");
    label.className = "config-q-label";
    label.textContent = q.label;
    qEl.appendChild(label);
    const opts = document.createElement("div");
    opts.className = "config-opts";
    for (const o of q.options) {
      const opt = document.createElement("label");
      opt.className = "config-opt" + (state.pendingAnswers.raw[q.key] === o.v ? " selected" : "");
      opt.innerHTML = `<input type="radio" name="q-${q.key}" ${state.pendingAnswers.raw[q.key] === o.v ? "checked" : ""}>
        <div><div class="config-opt-name">${escapeHtml(o.n)}</div><div class="config-opt-detail">${escapeHtml(o.d || "")}</div></div>`;
      opt.addEventListener("click", () => {
        opts.querySelectorAll(".config-opt").forEach((x) => x.classList.remove("selected"));
        opt.classList.add("selected");
        state.pendingAnswers.raw[q.key] = o.v;
      });
      opts.appendChild(opt);
    }
    qEl.appendChild(opts);
    body.appendChild(qEl);
  }
  document.getElementById("configModal").hidden = false;
}

function closeQuestions() {
  if (!state.pendingAnswers) return;
  const { blockId, raw } = state.pendingAnswers;
  if (Object.keys(raw).length) state.answers[blockId] = raw;
  state.pendingAnswers = null;
  document.getElementById("configModal").hidden = true;
  renderMechanicsGrid();
  saveState();
  pingSaved();
}

// ── Test parts ────────────────────────────────────────────────────
// Short tests of one block, or of two together, played with things at hand. The notes are the designers' own.

let PART_TESTS = null;

async function loadPartTests() {
  if (!PART_TESTS) PART_TESTS = await (await fetch("/tests")).json();
  return PART_TESTS;
}

async function renderTests() {
  const { tests, pairs } = await loadPartTests();
  const ids = flattenMechanics(state.mechanics);
  const together = pairs.filter((p) => p.blocks.every((b) => ids.includes(b)));
  const covered = new Set(together.flatMap((p) => p.blocks));
  const found = [...together, ...ids.filter((b) => tests[b] && !covered.has(b)).map((b) => ({ blocks: [b], ...tests[b] }))];
  const list = document.getElementById("testsList");
  const empty = document.getElementById("testsEmpty");
  list.innerHTML = "";
  empty.hidden = found.length > 0;
  empty.textContent = ids.length
    ? `None of the blocks on the canvas has a test yet. There are tests for ${Object.keys(tests).map(displayOf).join(", ")}.`
    : "Put blocks on the canvas. Tests for them appear here.";
  found.forEach((t) => list.appendChild(renderTestCard(t)));
}

function renderTestCard(t) {
  const key = t.blocks.join("+");
  const report = state.tests[key] || { feelings: [], match: null, note: "" };
  const keep = () => { state.tests[key] = report; saveState(); pingSaved(); };
  const card = document.createElement("div");
  card.className = "test-card";
  card.innerHTML = `<div class="test-card-tag${t.blocks.length > 1 ? " seam" : ""}">test · ${escapeHtml(t.blocks.map(displayOf).join(" + "))}</div>
    <h3>${escapeHtml(t.title)}</h3><span class="test-card-time">${escapeHtml(t.time || "")}</span>
    <div class="test-card-rules"><span class="label">How to play</span>${escapeHtml(t.rules)}</div>`;

  const pills = (label, options, isOn, onClick) => {
    const q = document.createElement("div");
    q.className = "form-q";
    q.innerHTML = `<div class="form-q-label">${label}</div>`;
    const row = document.createElement("div");
    row.className = "opts";
    for (const o of options) {
      const pill = document.createElement("span");
      pill.className = "opt-pill" + (isOn(o) ? " selected" : "");
      pill.textContent = o;
      pill.addEventListener("click", () => { if (state.locked) return; onClick(o); keep(); card.replaceWith(renderTestCard(t)); });
      row.appendChild(pill);
    }
    q.appendChild(row);
    card.appendChild(q);
  };
  pills("It felt", t.feeling_options, (f) => report.feelings.includes(f),
    (f) => { report.feelings = report.feelings.includes(f) ? report.feelings.filter((x) => x !== f) : [...report.feelings, f]; });
  pills("Did it match what you wanted?", ["yes", "partly", "no"], (o) => report.match === o, (o) => { report.match = o; });

  const note = document.createElement("div");
  note.className = "form-q";
  note.innerHTML = `<div class="form-q-label">One thing you would change</div>`;
  const input = document.createElement("input");
  input.className = "text-input";
  input.value = report.note || "";
  input.disabled = state.locked;
  input.addEventListener("change", () => { report.note = input.value.trim(); keep(); });
  note.appendChild(input);
  card.appendChild(note);
  return card;
}

function showTab(name) {
  document.querySelectorAll(".panel-tab").forEach((t) => t.classList.toggle("active", t.dataset.tab === name));
  document.querySelectorAll(".panel-pane").forEach((p) => { p.hidden = p.dataset.panel !== name; });
  if (name === "tests") renderTests();
}

// ── Addresses: every view has its own, so it can be linked, reloaded and reached with Back ──
// #games, #games/<id>, #games/<id>/watch, #how-it-works, #blocks/<id>, #tests

function go(hash) {
  location.hash = hash;
}

function leave() {
  history.pushState(null, "", location.pathname + location.search);
  route();
}

async function route() {
  const [view, id, sub] = decodeURIComponent(location.hash.replace(/^#\/?/, "")).split("/");
  document.getElementById("blockModal").hidden = true;
  document.getElementById("onboarding").hidden = true;
  if (view !== "games") closeGames();
  showTab(view === "tests" ? "tests" : "feedback");
  if (view === "how-it-works") openOnboarding();
  if (view === "blocks") {
    const dim = state.dimensions.find((d) => d.blocks.some((b) => b.id === id));
    if (dim) openBlockModal(id, dim.id);
  }
  if (view === "games") {
    await openGames();
    const g = id && GAMES.find((x) => x.id === id);
    if (g) showFam(g);
    if (g && sub === "watch" && g.animation.length) showWatch();
  }
}

// ── Known games: play one, then watch it and answer ──────────────
// Ten short games from the April 2026 demo, their rules, animations and answers checked against each other on 16 October 2026.
// Questions about what a designer would change have no right answer; they are asked and talked about, never marked.

let GAMES = null;
const CREDIT_ROWS = [["by", "Made by"], ["rules", "Rules from"], ["version", "This version"], ["added", "Added"]];

// Escaped text with its web addresses, written with or without https://, turned into links
function linkify(text) {
  return escapeHtml(text).replace(/(https:\/\/|\bgithub\.com\/)[^\s,;]+/g, (u) => {
    let tail = "";
    // A closing bracket ends the address only when the address has no opening one to match it
    while (/[.)]$/.test(u) && (u.endsWith(".") || (u.match(/\(/g) || []).length < (u.match(/\)/g) || []).length)) { tail = u.slice(-1) + tail; u = u.slice(0, -1); }
    return `<a href="${u.startsWith("https://") ? u : "https://" + u}" target="_blank" rel="noopener">${u.replace(/^https:\/\//, "")}</a>${tail}`;
  });
}

function creditsHtml(g) {
  const rows = CREDIT_ROWS.filter(([k]) => g.credits[k]).map(([k, label]) => `<dt>${label}</dt><dd>${linkify(g.credits[k])}</dd>`);
  if ((g.sources || []).length) rows.push(`<dt>Sources</dt><dd>${g.sources.map(linkify).join("<br>")}</dd>`);
  return `<div class="fam-credits"><div class="fam-equipment-label">Credits</div><dl>${rows.join("")}</dl></div>`;
}
const analysisState = { data: null, selectedAnswers: {} };

async function openGames() {
  if (!GAMES) GAMES = await (await fetch("/games")).json();
  document.getElementById("gamesOverlay").hidden = false;
  showGamesView("list");
  const grid = document.getElementById("gamesGrid");
  grid.innerHTML = "";
  for (const g of GAMES) {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "game-pick";
    b.innerHTML = `<strong>${escapeHtml(g.title)}</strong>
      <span class="game-pick-meta"><span><em>Time</em> ${escapeHtml(g.duration)}</span><span><em>Players</em> ${escapeHtml(g.players.replace(/ players?$/, ""))}</span></span>
      <span class="game-pick-from">from ${escapeHtml(g.parent_game)}</span>`;
    b.addEventListener("click", () => go(`games/${g.id}`));
    grid.appendChild(b);
  }
}

function showGamesView(view) {
  document.getElementById("gamesList").hidden = view !== "list";
  document.getElementById("gamesListBtn").hidden = view === "list";
  document.getElementById("famCardWrap").hidden = view !== "play";
  document.getElementById("famActions").hidden = view !== "play";
  document.getElementById("analysisStage").hidden = view !== "watch";
  document.getElementById("gamesOverlay").scrollTop = 0;
}

function closeGames() {
  document.getElementById("gamesOverlay").hidden = true;
}

function showFam(g) {
  analysisState.data = g;
  const wrap = document.getElementById("famCardWrap");
  wrap.innerHTML = "";
  const card = document.createElement("div");
  card.className = "fam-card";
  card.innerHTML = `<div class="fam-card-tag">Shows · ${escapeHtml(g.teaches.replace(/-/g, " "))}</div>
    <h2>${escapeHtml(g.title)}</h2><div class="fam-parent">from ${escapeHtml(g.parent_game)}</div>
    <a class="fam-download" href="/games/${encodeURIComponent(g.id)}.md" download>Download as a design (.md)</a>
    <div class="fam-meta"><span><strong>Time</strong> · ${escapeHtml(g.duration)}</span><span><strong>Players</strong> · ${escapeHtml(g.players)}</span></div>
    <div class="fam-intro">${escapeHtml(g.intro)}</div>
    <div class="fam-lesson"><div class="fam-equipment-label">What it shows a designer</div><p>${escapeHtml(g.lesson)}</p></div>
    ${creditsHtml(g)}
    <div class="fam-equipment"><div class="fam-equipment-label">What you need</div><ul>${g.equipment.map((e) => `<li>${linkify(e)}</li>`).join("")}</ul></div>
    <div class="fam-equipment-label">How to play</div>
    <div class="fam-steps">${g.steps.map((s) => `<div class="fam-step${s.svg ? "" : " plain"}">${s.svg ? `<div class="fam-step-svg">${s.svg}</div>` : ""}<div>
      <div class="fam-step-num">Step ${s.n}</div><div class="fam-step-title">${escapeHtml(s.title)}</div><div class="fam-step-body">${escapeHtml(s.body)}</div></div></div>`).join("")}</div>
    <div class="fam-notice"><div class="fam-notice-label">After playing, talk about</div><ul>${g.what_to_notice.map((n) => `<li>${escapeHtml(n)}</li>`).join("")}</ul></div>`;
  wrap.appendChild(card);
  document.getElementById("famDownload").href = `/games/${g.id}.md`;
  document.getElementById("famWatchBtn").hidden = !g.animation.length;
  showGamesView("play");
}

function showWatch() {
  const g = analysisState.data;
  analysisState.selectedAnswers = {};
  renderSceneByType(document.getElementById("analysisAnim"), g.animation_type, g.animation[0].scene || {});
  document.getElementById("animNarration").innerHTML = `<em>${escapeHtml(g.title)}: press <strong>Play</strong> to watch it played.</em>`;
  document.getElementById("animCounter").textContent = `0 / ${g.animation.length}`;
  document.getElementById("mcqBlock").hidden = true;
  document.getElementById("animPlayBtn").hidden = false;
  document.getElementById("animReplayBtn").hidden = true;
  showGamesView("watch");
}

async function playAnalysis() {
  const g = analysisState.data;
  document.getElementById("animPlayBtn").hidden = true;
  document.getElementById("animReplayBtn").hidden = true;
  const svg = document.getElementById("analysisAnim");
  for (let i = 0; i < g.animation.length; i++) {
    const b = g.animation[i];
    renderSceneByType(svg, g.animation_type, b.scene || {});
    document.getElementById("animNarration").textContent = b.narration || "";
    document.getElementById("animCounter").textContent = `${i + 1} / ${g.animation.length}`;
    const ending = b.scene && ["win", "bust", "draw"].includes(b.scene.outcome);
    await new Promise((r) => setTimeout(r, ending ? 2600 : 2000));
  }
  document.getElementById("animReplayBtn").hidden = false;
  document.getElementById("mcqBlock").hidden = false;
  renderMCQs();
}

function renderMCQs() {
  const list = document.getElementById("mcqList");
  list.innerHTML = "";
  analysisState.data.questions.forEach((q, i) => {
    const card = document.createElement("div");
    card.className = "mcq-card";
    card.dataset.qid = q.id;
    card.innerHTML = `<div class="mcq-q"><span class="mcq-q-num">Q${i + 1}</span>${escapeHtml(q.question)}${q.answer === null ? ' <em class="mcq-discuss">No right answer: talk about it.</em>' : ""}</div>`;
    const opts = document.createElement("div");
    opts.className = "mcq-opts";
    q.options.forEach((o, oi) => {
      const lab = document.createElement("label");
      lab.className = "mcq-opt";
      lab.innerHTML = `<input type="radio" name="mcq-${q.id}"><div>${escapeHtml(o)}</div>`;
      lab.addEventListener("click", () => {
        opts.querySelectorAll(".mcq-opt").forEach((x) => x.classList.remove("selected"));
        lab.classList.add("selected");
        analysisState.selectedAnswers[q.id] = oi;
      });
      opts.appendChild(lab);
    });
    card.appendChild(opts);
    const fb = document.createElement("div");
    fb.className = "mcq-feedback";
    card.appendChild(fb);
    list.appendChild(card);
  });
}

function checkMCQs() {
  for (const q of analysisState.data.questions) {
    const card = document.querySelector(`.mcq-card[data-qid="${q.id}"]`);
    const opts = card.querySelectorAll(".mcq-opt");
    const fb = card.querySelector(".mcq-feedback");
    const chosen = analysisState.selectedAnswers[q.id];
    opts.forEach((o) => o.classList.remove("correct", "wrong"));
    fb.classList.remove("correct", "wrong");
    if (q.answer === null) {
      fb.textContent = q.feedback_correct;
      fb.classList.add("show");
      continue;
    }
    if (chosen === undefined) {
      fb.textContent = "Not answered yet.";
      fb.classList.add("show");
      continue;
    }
    const right = chosen === q.answer;
    opts[chosen].classList.add(right ? "correct" : "wrong");
    opts[q.answer].classList.add("correct");
    fb.textContent = right ? q.feedback_correct : q.feedback_wrong;
    fb.classList.add(right ? "correct" : "wrong", "show");
  }
}

function renderSceneByType(svg, type, scene) {
  while (svg.firstChild) svg.removeChild(svg.firstChild);
  const W = 600, H = 280;
  const NS = "http://www.w3.org/2000/svg";
  const make = (n, attrs = {}, parent = svg) => {
    const e = document.createElementNS(NS, n);
    for (const k in attrs) e.setAttribute(k, attrs[k]);
    parent.appendChild(e);
    return e;
  };
  // background
  make("rect", { x: 0, y: 0, width: W, height: H, fill: "#FAF7F1" });

  if (type === "dice") return renderDiceScene(svg, scene, make, W, H);
  if (type === "grid") return renderGridScene(svg, scene, make, W, H);
  if (type === "social") return renderSocialScene(svg, scene, make, W, H);
  if (type === "cards") return renderCardsScene(svg, scene, make, W, H);
  // fallback: dice
  return renderDiceScene(svg, scene, make, W, H);
}

// Helpers — tiny stick figure
function drawStick(make, parent, x, y, active, scale = 1) {
  const g = make("g", { transform: `translate(${x},${y}) scale(${scale})` }, parent);
  const fill = active ? "#C75B39" : "#2D3127";
  make("circle", { cx: 0, cy: -18, r: 12, fill }, g);
  make("line", { x1: 0, y1: -6, x2: 0, y2: 18, stroke: fill, "stroke-width": 3.5, "stroke-linecap": "round" }, g);
  make("line", { x1: -15, y1: 0, x2: 15, y2: 0, stroke: fill, "stroke-width": 3.5, "stroke-linecap": "round" }, g);
  make("line", { x1: 0, y1: 18, x2: -10, y2: 35, stroke: fill, "stroke-width": 3.5, "stroke-linecap": "round" }, g);
  make("line", { x1: 0, y1: 18, x2: 10, y2: 35, stroke: fill, "stroke-width": 3.5, "stroke-linecap": "round" }, g);
  return g;
}

function drawDie(make, parent, x, y, value) {
  const isOne = value === 1;
  const fill = isOne ? "#FFE5DC" : "#FFFFFF";
  const stroke = isOne ? "#C75B39" : "#2D3127";
  make("rect", { x, y, width: 40, height: 40, rx: 5, fill, stroke, "stroke-width": 2 }, parent);
  const pips = {
    1: [[20, 20]],
    2: [[10, 10], [30, 30]],
    3: [[10, 10], [20, 20], [30, 30]],
    4: [[10, 10], [10, 30], [30, 10], [30, 30]],
    5: [[10, 10], [10, 30], [30, 10], [30, 30], [20, 20]],
    6: [[10, 10], [10, 20], [10, 30], [30, 10], [30, 20], [30, 30]],
  }[value] || [];
  pips.forEach(([px, py]) => make("circle", { cx: x + px, cy: y + py, r: 3, fill: stroke }, parent));
}

function drawScoreBox(make, parent, x, y, label, value, active) {
  make("text", { x, y, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 11, fill: "#6B6960", "letter-spacing": "0.08em" }, parent).textContent = label;
  const t = make("text", { x, y: y + 30, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 28, "font-weight": 600, fill: active ? "#C75B39" : "#2D3127" }, parent);
  t.textContent = value;
}

// ── Scene type: DICE (push-luck-style) ─────────────────────────
function renderDiceScene(svg, scene, make, W, H) {
  const actors = scene.actors || [{ id: "P1", active: false }, { id: "P2", active: false }];
  const positions = [
    [140, 100], [460, 100], [W / 2 - 80, 100], [W / 2 + 80, 100]
  ];
  actors.forEach((a, i) => {
    const [x, y] = positions[i] || [W / 2, 100];
    drawStick(make, svg, x, y, !!a.active);
    drawScoreBox(make, svg, x, 170, a.id.toUpperCase(), (scene.scores || {})[a.id] || 0, !!a.active);
  });
  // Central die
  if (scene.die !== undefined && scene.die !== null) {
    drawDie(make, svg, W / 2 - 20, 95, scene.die);
  }
  // Turn score
  if (scene.turn_score && scene.turn_score > 0) {
    make("text", { x: W / 2, y: 165, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 10, fill: "#6B6960", "letter-spacing": "0.1em" }).textContent = "TURN SCORE";
    make("text", { x: W / 2, y: 188, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 22, "font-weight": 600, fill: "#C75B39" }).textContent = scene.turn_score;
  }
  // BUST overlay
  if (scene.outcome === "bust") {
    make("rect", { x: W / 2 - 60, y: 80, width: 120, height: 80, fill: "#C75B39", opacity: 0.92, rx: 4 });
    make("text", { x: W / 2, y: 130, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 26, "font-weight": 600, fill: "white", "letter-spacing": "0.08em" }).textContent = scene.outcome_label || "BUST";
  }
  if (scene.outcome === "win") {
    make("text", { x: W / 2, y: 245, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 12, fill: "#C75B39", "letter-spacing": "0.1em" }).textContent = "GAME OVER · WINNER ABOVE";
  }
}

// ── Scene type: GRID ───────────────────────────────────────────
function renderGridScene(svg, scene, make, W, H) {
  const grid = scene.grid || [];
  const rows = grid.length || 3;
  const cols = (grid[0] && grid[0].length) || 3;
  const cellW = 50, cellH = 50, gap = 6;
  const totalW = cols * (cellW + gap) - gap;
  const totalH = rows * (cellH + gap) - gap;
  const startX = (W - totalW) / 2;
  const startY = (H - totalH) / 2 - 14;

  for (let r = 0; r < rows; r++) {
    for (let c = 0; c < cols; c++) {
      const x = startX + c * (cellW + gap);
      const y = startY + r * (cellH + gap);
      const val = grid[r] && grid[r][c];
      const cellFill = val === "P1" ? "#C75B39" : val === "P2" ? "#3A6E8F" : "white";
      make("rect", { x, y, width: cellW, height: cellH, fill: cellFill, stroke: "#2D3127", "stroke-width": 1.4, rx: 3 });
      if (val === "P1" || val === "P2") {
        make("text", { x: x + cellW / 2, y: y + cellH / 2 + 6, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 18, "font-weight": 600, fill: "white" }).textContent = val === "P1" ? "X" : "O";
      } else if (val === "?") {
        make("text", { x: x + cellW / 2, y: y + cellH / 2 + 6, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 16, fill: "#9C9888" }).textContent = "?";
      } else if (val && typeof val === "string") {
        // single character (e.g. "★") for memory match
        make("text", { x: x + cellW / 2, y: y + cellH / 2 + 6, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 16, fill: "#2D3127" }).textContent = val;
      }
    }
  }

  // Scores on side
  const scores = scene.scores || {};
  const scoreKeys = Object.keys(scores);
  if (scoreKeys.length) {
    let yi = 60;
    scoreKeys.forEach(k => {
      const colour = k === "P1" ? "#C75B39" : "#3A6E8F";
      make("text", { x: 30, y: yi, "font-family": "IBM Plex Mono", "font-size": 10, fill: colour, "letter-spacing": "0.08em" }).textContent = k.toUpperCase();
      make("text", { x: 30, y: yi + 22, "font-family": "Fraunces", "font-size": 22, "font-weight": 600, fill: colour }).textContent = scores[k];
      yi += 60;
    });
  }
  if (scene.outcome === "win") {
    make("text", { x: W / 2, y: H - 16, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 11, fill: "#C75B39", "letter-spacing": "0.1em" }).textContent = `WINNER · ${scene.winner || "—"}`;
  } else if (scene.outcome === "draw") {
    make("text", { x: W / 2, y: H - 16, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 11, fill: "#6B6960", "letter-spacing": "0.1em" }).textContent = "DRAW";
  }
}

// ── Scene type: SOCIAL (circle of figures, deduction games) ────
function renderSocialScene(svg, scene, make, W, H) {
  const layout = scene.layout || "circle5";
  const actors = scene.actors || [];
  let positions = [];

  if (layout === "circle5") {
    const cx = W / 2, cy = H / 2 + 6, r = 95;
    for (let i = 0; i < actors.length; i++) {
      const a = -Math.PI / 2 + (i / Math.max(actors.length, 1)) * Math.PI * 2;
      positions.push([cx + r * Math.cos(a), cy + r * Math.sin(a) * 0.85]);
    }
  } else if (layout === "triangle") {
    const cx = W / 2, cy = H / 2 + 8;
    positions = [[cx, cy - 80], [cx - 110, cy + 50], [cx + 110, cy + 50]];
  } else if (layout === "line2" || layout === "line3") {
    const n = layout === "line3" ? 3 : 2;
    const teamSize = actors.length / 2;
    const usableW = W - 80;
    actors.forEach((_, i) => {
      const team = i < teamSize ? 0 : 1;
      const idxInTeam = team === 0 ? i : i - teamSize;
      const xBase = team === 0 ? 80 : W / 2 + 40;
      const x = xBase + idxInTeam * 60;
      positions.push([x, H / 2 - 15]);
    });
  } else {
    // default: line of actors
    const usableW = W - 100;
    actors.forEach((_, i) => {
      positions.push([60 + (usableW / Math.max(actors.length - 1, 1)) * i, H / 2 - 10]);
    });
  }

  // Fireworks for hanabi-style "win"
  if (scene.fireworks && scene.fireworks.length) {
    scene.fireworks.forEach((f, i) => {
      const colour = f.startsWith("r") ? "#C75B39" : f.startsWith("b") ? "#3A6E8F" : "#7A8B3F";
      make("circle", { cx: 100 + i * 30, cy: 30, r: 8, fill: colour });
    });
  }

  // Speech bubble (if any)
  if (scene.speech && scene.active) {
    const idx = actors.findIndex(a => a.id === scene.active);
    if (idx >= 0 && positions[idx]) {
      const [px, py] = positions[idx];
      const bx = px - 50, by = py - 60;
      make("rect", { x: bx, y: by, width: 100, height: 26, fill: "#FFF8E8", stroke: "#D9883D", "stroke-width": 1.5, rx: 13 });
      make("text", { x: bx + 50, y: by + 17, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 11, "font-style": "italic", fill: "#7A4A1F" }).textContent = scene.speech;
    }
  }

  // Draw actors
  actors.forEach((a, i) => {
    const [x, y] = positions[i] || [W / 2, H / 2];
    const isActive = scene.active === a.id;
    const out = a.out;
    drawStick(make, svg, x, y, isActive);
    if (a.wolf && (a.out || scene.outcome)) {
      // reveal wolf
      make("circle", { cx: x, cy: y - 18, r: 16, fill: "none", stroke: "#C75B39", "stroke-width": 2.5, "stroke-dasharray": "3,2" });
      make("text", { x, y: y + 50, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 9, fill: "#C75B39", "letter-spacing": "0.1em" }).textContent = "WOLF";
    }
    // out marker
    if (out) {
      make("line", { x1: x - 16, y1: y - 30, x2: x + 16, y2: y + 36, stroke: "#C75B39", "stroke-width": 3, "stroke-linecap": "round" });
    }
    // ID label
    make("text", { x, y: y + 50, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 9, fill: "#6B6960", "letter-spacing": "0.08em" }).textContent = a.id.toUpperCase();
    // Score under (line2 layout)
    if (a.tokens !== undefined) {
      make("text", { x, y: y + 65, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 10, fill: "#C75B39" }).textContent = `${a.tokens} tokens`;
    }
    // Bid
    if (a.bid !== undefined) {
      make("text", { x, y: y + 80, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 16, "font-weight": 600, fill: "#C75B39" }).textContent = `bid ${a.bid}`;
    }
    // Cards (Hanabi)
    if (a.cards && a.cards.length) {
      a.cards.forEach((c, ci) => {
        const cx = x - (a.cards.length - 1) * 8 + ci * 16;
        const cy = y + 55;
        const colour = c.face && c.face[0] === "r" ? "#C75B39" : c.face && c.face[0] === "b" ? "#3A6E8F" : "#7A8B3F";
        make("rect", { x: cx - 7, y: cy, width: 14, height: 20, rx: 1.5, fill: colour });
        make("text", { x: cx, y: cy + 13, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 10, fill: "white", "font-weight": 600 }).textContent = c.face ? c.face[1] : "?";
      });
    }
  });

  // Prize (auction)
  if (scene.prize) {
    make("rect", { x: W / 2 - 22, y: 30, width: 44, height: 60, fill: "white", stroke: "#2D3127", "stroke-width": 2, rx: 4 });
    make("text", { x: W / 2, y: 70, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 18, "font-weight": 600, fill: "#C75B39" }).textContent = scene.prize;
  }

  // Scores on top (team games)
  if (scene.scores) {
    const keys = Object.keys(scene.scores);
    if (keys.length) {
      keys.forEach((k, i) => {
        const x = 100 + i * 200;
        make("text", { x, y: 22, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 10, fill: "#6B6960" }).textContent = k.toUpperCase();
        make("text", { x, y: 44, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 20, "font-weight": 600, fill: "#C75B39" }).textContent = scene.scores[k];
      });
    }
  }

  // Outcome
  if (scene.outcome === "win") {
    make("text", { x: W / 2, y: H - 12, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 11, fill: "#C75B39", "letter-spacing": "0.1em" }).textContent = `WINNER · ${(scene.winner || "team").toUpperCase()}`;
  }
}

// ── Scene type: CARDS (drafting / hand management) ────────────
function renderCardsScene(svg, scene, make, W, H) {
  const actors = scene.actors || [];
  // Place actors in 4 quadrants
  const positions = [[120, 60], [W - 120, 60], [120, H - 60], [W - 120, H - 60]];
  const colourMap = { r: "#C75B39", b: "#3A6E8F", g: "#7A8B3F", y: "#D9883D", k: "#2D3127", wild: "#9C5B9F" };

  actors.forEach((a, i) => {
    const [x, y] = positions[i] || [W / 2, H / 2];
    drawStick(make, svg, x, y, scene.active === a.id, 0.7);
    make("text", { x, y: y + 40, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 9, fill: "#6B6960" }).textContent = a.id.toUpperCase();
    // Show their kept stack as small coloured rectangles
    const cards = a.kept || a.hand || [];
    cards.forEach((c, ci) => {
      const cardX = x - (cards.length - 1) * 8 + ci * 16;
      const cardY = y + 50;
      const code = typeof c === "string" ? c : (c.face || "");
      const colour = code === "wild" ? colourMap.wild : (colourMap[code[0]] || "white");
      make("rect", { x: cardX - 7, y: cardY, width: 14, height: 20, fill: colour, stroke: "#2D3127", "stroke-width": 1, rx: 2 });
      const num = code === "wild" ? "★" : code.slice(1);
      make("text", { x: cardX, y: cardY + 14, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 10, fill: "white", "font-weight": 600 }).textContent = num;
    });
    if (a.score !== undefined) {
      make("text", { x, y: y + 78, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 14, "font-weight": 600, fill: "#C75B39" }).textContent = `score ${a.score}`;
    }
  });

  // Centre — discard pile (last-card-out style)
  if (scene.discard) {
    const code = scene.discard;
    const colour = colourMap[code[0]] || "white";
    make("rect", { x: W / 2 - 22, y: H / 2 - 30, width: 44, height: 60, fill: colour, stroke: "#2D3127", "stroke-width": 2, rx: 4 });
    make("text", { x: W / 2, y: H / 2 + 5, "text-anchor": "middle", "font-family": "Fraunces", "font-size": 22, fill: "white", "font-weight": 600 }).textContent = code.slice(1);
    make("text", { x: W / 2, y: H / 2 + 24, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 8, fill: "white" }).textContent = ({ r: "RED", b: "BLUE", g: "GREEN", y: "YEL" })[code[0]] || "";
  }

  if (scene.outcome === "win") {
    make("text", { x: W / 2, y: H - 14, "text-anchor": "middle", "font-family": "IBM Plex Mono", "font-size": 11, fill: "#C75B39", "letter-spacing": "0.1em" }).textContent = `WINNER · ${scene.winner || "—"}`;
  }
}


// ── Save and open as Markdown ─────────────────────────────────────
// The file reads as a record of the game, and ends with the saved state as JSON, which is what Open game reads back.

function displayOf(blockId) {
  for (const d of state.dimensions) {
    const b = d.blocks.find((x) => x.id === blockId);
    if (b) return b.display;
  }
  return (state.feelings.find((f) => f.id === blockId) || {}).display || blockId;
}

async function onSaveGame() {
  const { tests, pairs } = await loadPartTests();
  const titles = Object.fromEntries([...pairs.map((p) => [p.blocks.join("+"), p.title]), ...Object.entries(tests).map(([b, t]) => [b, t.title])]);
  const lines = ["# A board game designed in boardgameBuilder", "",
    `Saved ${new Date().toLocaleString("en-GB", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" })}. To carry on, open ${location.origin} and choose Open game.`, "",
    "## What we want our game to feel like", ""];
  lines.push(...(state.chosenFeelings.length ? state.chosenFeelings.map((f) => `- ${displayOf(f)}`) : ["Nothing chosen yet."]), "", "## Our game", "");
  const rows = state.dimensions.filter((d) => state.mechanics[d.id])
    .map((d) => `- ${d.display}: ${[].concat(state.mechanics[d.id]).map(displayOf).join("; ")}`);
  lines.push(...(rows.length ? rows : ["No blocks yet."]), "");
  const said = Object.keys(state.answers).filter((b) => answerSummary(b)).map((b) => `- ${displayOf(b)}: ${answerSummary(b, ", ")}`);
  if (said.length) lines.push("## How our blocks work", "", ...said, "");
  const tried = Object.entries(state.tests).filter(([k]) => titles[k]).map(([k, r]) => `- ${titles[k]}: ` +
    [r.feelings.length && `it felt ${r.feelings.join(", ")}`, r.match && `matched what we wanted: ${r.match}`, r.note && `one thing we would change: ${r.note}`].filter(Boolean).join("; "));
  if (tried.length) lines.push("## What we tested", "", ...tried, "");
  if (state.turnHistory.length) {
    lines.push("## Feedback", "");
    for (const e of state.turnHistory) lines.push(`### ${e.kind === "complete" ? "Final, your game" : `Turn ${e.turn}`}`, "", e.narration, "");
  }
  lines.push("## Saved state", "", "boardgameBuilder reads this part back when the file is opened.", "", "```json", JSON.stringify(snapshot()), "```", "");
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob([lines.join("\n")], { type: "text/markdown" }));
  a.download = "boardgame-design.md";
  a.click();
  URL.revokeObjectURL(a.href);
}

async function onOpenGame(e) {
  const file = e.target.files[0];
  e.target.value = "";
  if (!file) return;
  const found = (await file.text()).match(/```json\n([\s\S]*?)\n```\s*$/);
  let saved = null;
  try { saved = found && JSON.parse(found[1]); } catch (_) {}
  if (!saved || typeof saved !== "object") {
    appendSystemMessage(`${file.name} is not a game saved from boardgameBuilder, so nothing was opened.`);
    return;
  }
  if ((flattenMechanics(state.mechanics).length || state.chosenFeelings.length) && !confirm("Replace the design on screen with the one in this file?")) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(saved));
  } catch (_) {
    appendSystemMessage("This browser is not letting the page store anything, so the file could not be opened.");
    return;
  }
  window.location.reload();
}

// ── Start fresh ───────────────────────────────────────────────────

function onStartFresh() {
  const ok = confirm("Clear the saved design and start over?");
  if (!ok) return;
  clearState();
  window.location.reload();
}

// ── Init ──────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  await loadPalette();

  const restored = loadState();

  if (restored) {
    document.getElementById("turnIndicator").textContent = `Turn ${state.turnNumber}`;
    renderMechanicsGrid();
    renderFeelingsShelf();
    renderHistoryFromState();
    if (state.locked) applyLockedUi();
  } else {
    renderFeelingsShelf();
  }

  setupFeelingsDropZone();
  document.getElementById("iterateBtn").addEventListener("click", onIterate);
  document.getElementById("completeBtn").addEventListener("click", onComplete);
  document.getElementById("gamesCloseBtn").addEventListener("click", leave);
  document.getElementById("famWatchBtn").addEventListener("click", () => go(`games/${analysisState.data.id}/watch`));
  document.getElementById("animPlayBtn").addEventListener("click", playAnalysis);
  document.getElementById("animReplayBtn").addEventListener("click", playAnalysis);
  document.getElementById("mcqSubmit").addEventListener("click", checkMCQs);
  for (const id of ["configDoneBtn", "configModalClose", "configModalBackdrop"]) {
    document.getElementById(id).addEventListener("click", closeQuestions);
  }
  document.querySelectorAll(".panel-tab").forEach((t) => t.addEventListener("click", () => (t.dataset.tab === "tests" ? go("tests") : leave())));
  document.getElementById("saveGameLink").addEventListener("click", (e) => { e.preventDefault(); onSaveGame(); });
  document.getElementById("openGameLink").addEventListener("click", (e) => { e.preventDefault(); document.getElementById("openGameInput").click(); });
  document.getElementById("openGameInput").addEventListener("change", onOpenGame);
  document.getElementById("startFreshLink").addEventListener("click", (e) => {
    e.preventDefault();
    onStartFresh();
  });

  // Block modal handlers
  document.getElementById("blockModalClose").addEventListener("click", leave);
  document.getElementById("blockModalBackdrop").addEventListener("click", leave);
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    closeQuestions();
    if (location.hash === "#how-it-works") closeOnboarding();
    if (location.hash) leave();
  });

  // Onboarding handlers
  for (const id of ["onboardingClose", "onboardingBackdrop", "onboardingStart"]) {
    document.getElementById(id).addEventListener("click", () => { closeOnboarding(); leave(); });
  }
  if (!seenOnboarding() && !location.hash) history.replaceState(null, "", "#how-it-works");
  window.addEventListener("hashchange", route);
  route();
});
