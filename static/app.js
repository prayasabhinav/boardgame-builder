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

  // Feelings group
  container.appendChild(buildPaletteGroup({
    dim: "feeling",
    letter: "F",
    title: "Feelings — what we want",
    description: "Drag these onto the feelings shelf at the top of the canvas.",
    blocks: state.feelings.map(f => ({ ...f, dim: "feeling" })),
    isFeeling: true,
  }));
}

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
    openBlockModal(id, dim);
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
          body.appendChild(createBlock(block.id, block.display, dim.id, { inSlot: true }));
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
        state.mechanics[dim.id] = data.id;
      }
      renderMechanicsGrid();
      saveState();
      pingSaved();
    });

    grid.appendChild(slot);
  }
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

// ── Save and open as Markdown ─────────────────────────────────────
// The file reads as a record of the game, and ends with the saved state as JSON, which is what Open game reads back.

function displayOf(blockId) {
  for (const d of state.dimensions) {
    const b = d.blocks.find((x) => x.id === blockId);
    if (b) return b.display;
  }
  return (state.feelings.find((f) => f.id === blockId) || {}).display || blockId;
}

function onSaveGame() {
  const lines = ["# A board game designed in boardgameBuilder", "",
    `Saved ${new Date().toLocaleString("en-GB", { day: "numeric", month: "long", year: "numeric", hour: "2-digit", minute: "2-digit" })}. To carry on, open ${location.origin} and choose Open game.`, "",
    "## What we want our game to feel like", ""];
  lines.push(...(state.chosenFeelings.length ? state.chosenFeelings.map((f) => `- ${displayOf(f)}`) : ["Nothing chosen yet."]), "", "## Our game", "");
  const rows = state.dimensions.filter((d) => state.mechanics[d.id])
    .map((d) => `- ${d.display}: ${[].concat(state.mechanics[d.id]).map(displayOf).join("; ")}`);
  lines.push(...(rows.length ? rows : ["No blocks yet."]), "");
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
  document.getElementById("saveGameLink").addEventListener("click", (e) => { e.preventDefault(); onSaveGame(); });
  document.getElementById("openGameLink").addEventListener("click", (e) => { e.preventDefault(); document.getElementById("openGameInput").click(); });
  document.getElementById("openGameInput").addEventListener("change", onOpenGame);
  document.getElementById("startFreshLink").addEventListener("click", (e) => {
    e.preventDefault();
    onStartFresh();
  });

  // Block modal handlers
  document.getElementById("blockModalClose").addEventListener("click", closeBlockModal);
  document.getElementById("blockModalBackdrop").addEventListener("click", closeBlockModal);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") { closeBlockModal(); closeOnboarding(); }
  });

  // Onboarding handlers
  document.getElementById("howItWorksLink").addEventListener("click", (e) => {
    e.preventDefault();
    openOnboarding();
  });
  for (const id of ["onboardingClose", "onboardingBackdrop", "onboardingStart"]) {
    document.getElementById(id).addEventListener("click", closeOnboarding);
  }
  if (!seenOnboarding()) openOnboarding();
});
