# Feeling-Blocks Catalogue — boardgameBuilder v1

**Status:** v1 draft for KB assembly
**Date:** 24 April 2026
**Role in architecture:** Intent layer. Dragged onto the canvas "What we want" region. Feeds the Stage 2 intent-service channel. Separate from the six mechanic dimensions.

---

## Design principles

- **Plain school-child vocabulary.** Not game-design jargon. "excited" not "high arousal". "sneaky" not "asymmetric information with deceptive intent".
- **Play experiences, not game genres.** "tense" (a feeling), not "thriller" (a genre).
- **Orthogonal where possible.** Children should be able to pick 2-4 feelings without every combination feeling contradictory. Some contradictions are deliberate (*together* + *sneaky*) — the tool surfaces them as tensions.
- **Short.** One or two words per block. If you can't say it in two words, the children won't remember it.
- **Soft cap of ~5 blocks on the shelf.** The catalogue is 15, the canvas holds up to ~5. The group curates.

---

## The 15 feeling-blocks

Colour family: Red / coral (all feeling-blocks share a colour to visually separate them from mechanic blocks).

| Block | What it feels like in play | Supported by (mechanical tendency) | Opposed by (mechanical tendency) |
|-------|----------------------------|-----------------------------------|----------------------------------|
| **excited** | Loud table. Big swings. You can't look away. | push-your-luck, direct-confrontation, race, dice | solo-in-parallel, mostly-skill, long turns |
| **clever** | You feel smart when you play well. Your choices matter. | mostly-skill, hand-management, full-information | mostly-chance, random-draw |
| **silly** | Laughing at what just happened. Absurd moments. | absurd theme, direct-confrontation, push-your-luck, bluffing | abstract theme, mostly-skill, long turns |
| **tense** | You're on edge. Something could go wrong any moment. | push-your-luck, hidden-identity, cooperative-survival, timers | full-information, mostly-skill race |
| **together** | You and your friends are in it as one. Shared fate. | fully-cooperative, team-vs-team, shared-objective | direct-confrontation, last-standing, traitor |
| **sneaky** | Hiding things, tricking people, secret plans. | hidden-hands, hidden-identity, bluffing, traitor | full-information, fully-cooperative |
| **lucky** | The dice or the draw felt magical. You got away with it. | mostly-chance, push-your-luck, dice-rolling | mostly-skill, full-information |
| **in charge** | You're directing something. Deep decisions have weight. | worker-placement, area-control, hand-management | roll-and-move, mostly-chance |
| **surprised** | Something unexpected keeps happening. | hidden-hands, chance-with-mitigation, narrative-completion | full-information, mostly-skill |
| **thoughtful** | You sit back and think. Time to plan. | mostly-skill, worker-placement, full-information | push-your-luck, direct-confrontation, timers |
| **fast** | The game moves. Short turns, quick rounds. | drafting, trick-taking, roll-and-move, push-your-luck | worker-placement, negotiation |
| **unfair (in a fun way)** | Someone got wrecked. Everyone laughed. Including them. | direct-confrontation, take-that, traitor, last-standing | fully-cooperative, shared-objective |
| **careful** | One wrong move and you're in trouble. Precision matters. | cooperative-survival, hidden-hands cooperation, worker-placement | push-your-luck, mostly-chance |
| **daring** | You tried something risky and it paid off (or didn't). | push-your-luck, bidding, direct-confrontation | mostly-skill, full-information, solo-in-parallel |
| **friendly** | Warm. Nobody's out to get anyone. | fully-cooperative, shared-objective, indirect-via-board | direct-confrontation, traitor, last-standing |

---

## How feeling-blocks work in the pipeline

### Stage 1 — Human qualification
The group drags 2-4 feeling-blocks to the "What we want" shelf. No AI. Order doesn't matter. Blocks can be added or removed at any time during building.

### Stage 2 — Intent-service channel
For each feeling-block on the shelf, the rules body looks up which mechanical elements in the "Our game" region *support* that feeling and which *oppose* it. The system produces one of three verdicts for the whole assembly:

- **matches** — All (or most) feeling-blocks are supported by the mechanical choices; none are opposed.
- **partly matches** — Some feeling-blocks are supported, others are opposed or unsupported.
- **pulling apart** — The majority of feeling-blocks are opposed by the mechanical choices. The game being built will not feel like what the group said they wanted.

When feeling-blocks themselves are internally contradictory (e.g. *together* + *sneaky* + *unfair-in-a-fun-way*), the verdict is *pulling apart* — but the narration names it as "you want different kinds of feelings at once — that's interesting, but one game can't easily do all of them."

### Stage 3 — Narration register
The Stage 3 prompt receives both the mechanical-pair verdicts AND the intent-service verdict. The feedback states both in plain words (since 16 October 2026 assembled in code from the knowledge base, with no model):

- First paragraph: mechanical consequence ("what this combination tends to do")
- Second paragraph: intent-service ("does this match what you wanted")
- If both agree → short affirmation + one or two games that do this
- If they disagree → surface the tension: "your combination makes sense on its own, but it tends to produce a game that feels more X than Y — and you said you wanted Y"
- Register: surfacing, never corrective. The group decides what to do.

---

## Notes on the "opposed by" column

The "opposed by" column is where intent-service does its real work. A feeling is *opposed* by a mechanic when the mechanic's characteristic play experience pulls in the opposite direction. Example: *thoughtful* is opposed by *push-your-luck* because push-your-luck rewards gut-level quick decisions, not deliberation. *Clever* is opposed by *mostly-chance* because chance minimises the impact of skillful play.

Some pairs are deterministic opposites (you can't have both feel strong at once). Others are *soft* opposition (a skilled designer can build a game that partly does both — e.g. *together* + *sneaky* is present in cooperative-with-traitor games like Dead of Winter, but the two feelings still pull against each other).

The rules body encodes both hard and soft opposition. Hard opposition triggers a *pulling apart* verdict. Soft opposition lowers the match score but does not alone trigger it.

---

## Shelf dynamics

- Soft cap: ~5 feeling-blocks. No hard limit. The UI may display a subtle warning at 6+ ("that's a lot of feelings — can one game really have all of these?").
- Order-independent: the shelf is a basket, not a sequence.
- Removal: drag off to remove. No confirmation.
- Empty shelf: intent-service channel stays quiet. Narration mentions mechanical consequence only.
- 1 feeling-block on shelf: intent-service is binary (matches or opposed) — still useful for the workshop.

---

## Open design questions (for after the weekend)

- Do 15 feelings feel like too many to school children? Watch for paralysis vs engagement.
- Does the soft cap work? Do groups naturally pick 2-4, or do they try to pick all of them?
- Are there feelings missing that children reach for but the catalogue doesn't have? ("scary", "romantic", "weird" — possibly add.)
- Is the "red/coral" colour the right signal? Feeling-blocks are *different* from mechanic blocks — does the colour distinction land?

These are grounding questions, not spec questions. Decide after the workshops.

---

*Next: `interactions-draft.json` via clustered Perplexity generation (pending MCP reconnect) or training-knowledge generation flagged as unverified.*
