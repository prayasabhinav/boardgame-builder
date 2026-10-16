"""Per-block kid-friendly explanations + simple SVG illustrations.

Used by the /palette endpoint. Frontend renders the description + SVG
when a child taps the "?" info icon on a block.

Visual style: 120×80 viewBox, stroke-only line art, single accent fill
where useful, ~10–20 elements per SVG. Designed to read at small size.
"""

# Reusable SVG building blocks for tight, consistent style.
_S = 'stroke="#2D3436" stroke-width="2.2" fill="none" stroke-linecap="round" stroke-linejoin="round"'
_FILL = 'fill="#C75B39"'   # accent fill
_TINT = 'fill="#fbe4d8"'   # accent tint


def svg(inner: str) -> str:
    """Wrap inner SVG content in a 120×80 viewBox."""
    return f'<svg viewBox="0 0 120 80" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">{inner}</svg>'


# ─────────────────────────────────────────────────────────────────────
# CORE MECHANICS (12)
# ─────────────────────────────────────────────────────────────────────

CORE_MECHANICS = {
    "roll-and-move": {
        "description": "You roll a dice, then move your piece that many spaces along a path. Like Snakes and Ladders or Monopoly.",
        "svg": svg(f'<rect x="14" y="20" width="22" height="22" rx="3" {_S}/><circle cx="20" cy="26" r="1.6" {_FILL} stroke="none"/><circle cx="30" cy="36" r="1.6" {_FILL} stroke="none"/><circle cx="20" cy="36" r="1.6" {_FILL} stroke="none"/><path d="M44 50 Q60 30 76 50 T108 50" {_S}/><circle cx="108" cy="50" r="4" {_FILL} stroke="none"/><path d="M50 56 l4 -4 l4 4" {_S}/>'),
    },
    "drafting": {
        "description": "You pick one card from your hand, then pass the rest to the next player. Everyone keeps choosing the best one left, like sharing snacks but for cards.",
        "svg": svg(f'<rect x="14" y="22" width="14" height="22" rx="2" {_S} {_TINT}/><rect x="32" y="22" width="14" height="22" rx="2" {_S}/><rect x="50" y="22" width="14" height="22" rx="2" {_S}/><rect x="68" y="22" width="14" height="22" rx="2" {_S}/><path d="M86 33 l16 0 m-4 -4 l4 4 l-4 4" {_S}/><path d="M21 14 l-2 4" {_S}/><circle cx="21" cy="11" r="2.2" {_FILL} stroke="none"/>'),
    },
    "bidding": {
        "description": "Players offer money or things to buy something. Whoever offers the most wins it. Like an auction at a market.",
        "svg": svg(f'<path d="M20 60 l24 -32 l24 32 z" {_S}/><circle cx="44" cy="44" r="4" {_FILL} stroke="none"/><text x="80" y="36" font-family="serif" font-size="14" {_FILL} stroke="none">5</text><text x="92" y="50" font-family="serif" font-size="14" {_FILL} stroke="none">8</text><text x="78" y="58" font-family="serif" font-size="14" {_FILL} stroke="none">12</text>'),
    },
    "push-your-luck": {
        "description": "Keep risking for more points — but if you go too far, you lose what you had. Like saying \"one more dive!\" when you should have stopped.",
        "svg": svg(f'<path d="M14 60 l16 -10 l16 0 l16 -10 l16 0 l16 -10" {_S}/><circle cx="14" cy="60" r="3" {_FILL} stroke="none"/><circle cx="46" cy="50" r="3" {_FILL} stroke="none"/><circle cx="78" cy="40" r="3" {_FILL} stroke="none"/><path d="M94 30 l16 -8" {_S}/><path d="M104 18 l8 0 l-4 -4 m4 4 l-4 4" {_S}/><circle cx="106" cy="22" r="9" stroke="#C75B39" stroke-width="2" fill="none"/><line x1="100" y1="16" x2="112" y2="28" stroke="#C75B39" stroke-width="2"/>'),
    },
    "area-control": {
        "description": "Players fight to have the most pieces in different parts of a map. Whoever holds the most spots wins that area.",
        "svg": svg(f'<path d="M14 14 L60 14 L60 50 L14 50 z" {_S} {_TINT}/><path d="M60 14 L106 14 L106 40 L60 40 z" {_S}/><path d="M60 40 L106 40 L106 66 L60 66 z" {_S}/><path d="M14 50 L60 50 L60 66 L14 66 z" {_S}/><circle cx="28" cy="32" r="3" {_FILL} stroke="none"/><circle cx="40" cy="36" r="3" {_FILL} stroke="none"/><circle cx="34" cy="24" r="3" {_FILL} stroke="none"/><circle cx="80" cy="26" r="3" stroke="#2D3436" stroke-width="1.6" fill="white"/><circle cx="80" cy="54" r="3" stroke="#2D3436" stroke-width="1.6" fill="white"/><circle cx="30" cy="58" r="3" stroke="#2D3436" stroke-width="1.6" fill="white"/>'),
    },
    "worker-placement": {
        "description": "You put your little workers on different jobs on the board. If someone takes a spot, no one else can use it that turn.",
        "svg": svg(f'<rect x="14" y="44" width="20" height="22" rx="2" {_S}/><rect x="40" y="44" width="20" height="22" rx="2" {_S} {_TINT}/><rect x="66" y="44" width="20" height="22" rx="2" {_S}/><rect x="92" y="44" width="20" height="22" rx="2" {_S}/><circle cx="50" cy="36" r="4" {_FILL} stroke="none"/><circle cx="76" cy="36" r="4" {_FILL} stroke="none"/><path d="M48 32 l4 -8 m0 0 l4 8" {_S}/><path d="M74 32 l4 -8 m0 0 l4 8" {_S}/>'),
    },
    "pattern-building": {
        "description": "You match colours or shapes to make patterns — straight lines, mosaics, sets. Like building with bright tiles.",
        "svg": svg(f'<rect x="20" y="20" width="14" height="14" {_S} {_FILL}/><rect x="36" y="20" width="14" height="14" {_S}/><rect x="52" y="20" width="14" height="14" {_S} {_TINT}/><rect x="68" y="20" width="14" height="14" {_S}/><rect x="84" y="20" width="14" height="14" {_S} {_FILL}/><rect x="20" y="36" width="14" height="14" {_S}/><rect x="36" y="36" width="14" height="14" {_S} {_FILL}/><rect x="52" y="36" width="14" height="14" {_S}/><rect x="68" y="36" width="14" height="14" {_S} {_FILL}/><rect x="84" y="36" width="14" height="14" {_S}/>'),
    },
    "hand-management": {
        "description": "You hold a hand of cards and decide which to play, when, and which to keep for later. Choosing carefully matters most.",
        "svg": svg(f'<g transform="translate(60 50) rotate(-18)"><rect x="-9" y="-22" width="18" height="32" rx="2" {_S} {_TINT}/></g><g transform="translate(60 50) rotate(-6)"><rect x="-9" y="-26" width="18" height="32" rx="2" {_S}/></g><g transform="translate(60 50) rotate(6)"><rect x="-9" y="-26" width="18" height="32" rx="2" {_S}/></g><g transform="translate(60 50) rotate(18)"><rect x="-9" y="-22" width="18" height="32" rx="2" {_S}/></g><circle cx="60" cy="20" r="3" {_FILL} stroke="none"/>'),
    },
    "trick-taking": {
        "description": "Everyone plays one card. The highest card wins all of them — that's a \"trick\". Whoever wins leads next.",
        "svg": svg(f'<rect x="20" y="22" width="18" height="26" rx="2" {_S}/><text x="29" y="40" font-family="serif" font-size="13" text-anchor="middle">3</text><rect x="42" y="22" width="18" height="26" rx="2" {_S} {_TINT}/><text x="51" y="40" font-family="serif" font-size="13" text-anchor="middle" {_FILL} stroke="none">9</text><rect x="64" y="22" width="18" height="26" rx="2" {_S}/><text x="73" y="40" font-family="serif" font-size="13" text-anchor="middle">7</text><rect x="86" y="22" width="18" height="26" rx="2" {_S}/><text x="95" y="40" font-family="serif" font-size="13" text-anchor="middle">2</text><path d="M44 58 l16 0 l-4 -4 m4 4 l-4 4" {_S}/><circle cx="51" cy="35" r="14" stroke="#C75B39" stroke-width="2" fill="none" opacity="0.6"/>'),
    },
    "negotiation": {
        "description": "Players talk to each other and make deals. \"I'll give you wood if you give me wheat.\" Trades and promises shape the game.",
        "svg": svg(f'<circle cx="32" cy="34" r="9" {_S}/><circle cx="32" cy="34" r="2" fill="#2D3436"/><circle cx="88" cy="34" r="9" {_S}/><circle cx="88" cy="34" r="2" fill="#2D3436"/><path d="M44 34 l32 0" {_S}/><path d="M44 30 l8 -3 l-2 6 z" {_FILL} stroke="none"/><path d="M76 38 l-8 3 l2 -6 z" {_FILL} stroke="none"/><path d="M28 44 l8 14" {_S}/><path d="M36 44 l-4 14" {_S}/><path d="M84 44 l8 14" {_S}/><path d="M92 44 l-4 14" {_S}/>'),
    },
    "set-collection": {
        "description": "You gather groups of matching things — three of one colour, four of one type — to score points. Like collecting stamp sets.",
        "svg": svg(f'<circle cx="28" cy="32" r="6" {_S} {_FILL} stroke-width="0"/><circle cx="42" cy="32" r="6" {_S} {_FILL} stroke-width="0"/><circle cx="56" cy="32" r="6" {_S} {_FILL} stroke-width="0"/><rect x="72" y="26" width="12" height="12" {_S}/><rect x="86" y="26" width="12" height="12" {_S}/><path d="M28 50 l70 0" {_S}/><text x="50" y="68" font-family="serif" font-size="11" text-anchor="middle">three of a kind</text>'),
    },
    "tile-placement": {
        "description": "You lay tiles down to build a shared map — connecting roads, cities, fields. Like Carcassonne.",
        "svg": svg(f'<rect x="20" y="22" width="22" height="22" {_S} {_TINT}/><rect x="42" y="22" width="22" height="22" {_S}/><rect x="64" y="22" width="22" height="22" {_S} {_TINT}/><rect x="42" y="44" width="22" height="22" {_S}/><rect x="64" y="44" width="22" height="22" {_S} {_TINT}/><path d="M20 33 l22 0 M64 33 l22 0" {_S}/><path d="M53 22 l0 22 M75 44 l0 22" {_S}/><path d="M92 56 l10 -10 l-3 -3 m3 3 l-3 3" {_S}/><rect x="92" y="56" width="14" height="14" stroke="#C75B39" stroke-width="2" stroke-dasharray="3 2" fill="none"/>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# VICTORY CONDITIONS (7)
# ─────────────────────────────────────────────────────────────────────

VICTORY = {
    "race-to-finish": {
        "description": "First player to reach the end wins. The whole game is a race.",
        "svg": svg(f'<path d="M14 56 L106 56" {_S}/><circle cx="22" cy="56" r="4" {_FILL} stroke="none"/><circle cx="40" cy="56" r="4" stroke="#2D3436" stroke-width="2" fill="white"/><circle cx="58" cy="56" r="4" stroke="#2D3436" stroke-width="2" fill="white"/><line x1="100" y1="20" x2="100" y2="56" stroke="#2D3436" stroke-width="2"/><rect x="100" y="20" width="6" height="4" fill="#2D3436"/><rect x="106" y="24" width="6" height="4" fill="#2D3436"/><rect x="100" y="28" width="6" height="4" fill="#2D3436"/><rect x="106" y="32" width="6" height="4" fill="#2D3436"/><rect x="100" y="36" width="6" height="4" fill="#2D3436"/>'),
    },
    "most-points": {
        "description": "Whoever has the highest score at the end wins. Points come from many sources — sets, places, cards.",
        "svg": svg(f'<rect x="22" y="40" width="18" height="30" {_S} {_TINT}/><text x="31" y="58" font-family="serif" font-size="12" text-anchor="middle">12</text><rect x="46" y="28" width="18" height="42" {_S} {_FILL} stroke-width="0"/><text x="55" y="50" font-family="serif" font-size="12" text-anchor="middle" fill="white">19</text><rect x="70" y="48" width="18" height="22" {_S}/><text x="79" y="62" font-family="serif" font-size="12" text-anchor="middle">8</text><path d="M55 24 l-3 6 l6 0 z" {_FILL} stroke="none"/>'),
    },
    "last-standing": {
        "description": "Knock out other players one by one. The last one alive wins.",
        "svg": svg(f'<g transform="translate(28 50)"><circle cx="0" cy="-12" r="5" {_S}/><line x1="-6" y1="-4" x2="6" y2="6" {_S}/><line x1="6" y1="-4" x2="-6" y2="6" {_S}/></g><g transform="translate(60 50)"><circle cx="0" cy="-12" r="5" {_S}/><line x1="-6" y1="-4" x2="6" y2="6" {_S}/><line x1="6" y1="-4" x2="-6" y2="6" {_S}/></g><g transform="translate(92 50)"><circle cx="0" cy="-12" r="5" {_S} {_FILL} stroke-width="0"/><line x1="0" y1="-7" x2="0" y2="14" {_S}/><line x1="-5" y1="0" x2="5" y2="0" {_S}/><line x1="-3" y1="14" x2="3" y2="14" {_S}/></g>'),
    },
    "cooperative-survival": {
        "description": "Everyone wins or loses together. The game tries to beat all of you. Stay alive long enough and you all win.",
        "svg": svg(f'<g transform="translate(34 48)"><circle cx="0" cy="-10" r="5" {_S}/><path d="M-5 -2 l-2 14 M5 -2 l2 14 M0 -2 l0 14" {_S}/></g><g transform="translate(58 48)"><circle cx="0" cy="-10" r="5" {_S}/><path d="M-5 -2 l-2 14 M5 -2 l2 14 M0 -2 l0 14" {_S}/></g><g transform="translate(82 48)"><circle cx="0" cy="-10" r="5" {_S}/><path d="M-5 -2 l-2 14 M5 -2 l2 14 M0 -2 l0 14" {_S}/></g><path d="M30 14 Q60 4 90 14" stroke="#C75B39" stroke-width="3" fill="none" stroke-dasharray="4 3"/><path d="M58 22 l-4 -8 m4 8 l4 -8" stroke="#C75B39" stroke-width="2"/>'),
    },
    "shared-objective": {
        "description": "All players work together to reach a goal — a score, a final state, a saved world.",
        "svg": svg(f'<circle cx="60" cy="36" r="14" stroke="#C75B39" stroke-width="2.5" fill="none"/><circle cx="60" cy="36" r="6" {_FILL} stroke="none"/><path d="M28 60 l28 -22 M92 60 l-28 -22 M60 70 l0 -32" {_S} stroke-dasharray="3 3"/><circle cx="28" cy="60" r="3" {_S} fill="white"/><circle cx="92" cy="60" r="3" {_S} fill="white"/><circle cx="60" cy="70" r="3" {_S} fill="white"/>'),
    },
    "hidden-personal-goal": {
        "description": "Each player has a secret goal. No one knows what the others are trying to do. Win without giving yourself away.",
        "svg": svg(f'<rect x="40" y="22" width="40" height="36" rx="3" {_S} {_TINT}/><text x="60" y="46" font-family="serif" font-size="20" text-anchor="middle" {_FILL} stroke="none">?</text><circle cx="22" cy="40" r="6" {_S}/><line x1="22" y1="46" x2="22" y2="62" {_S}/><circle cx="98" cy="40" r="6" {_S}/><line x1="98" y1="46" x2="98" y2="62" {_S}/>'),
    },
    "narrative-completion": {
        "description": "You play through a story. The game ends when the story does — happy ending, tragic ending, your choice.",
        "svg": svg(f'<rect x="20" y="22" width="80" height="44" rx="2" {_S} {_TINT}/><line x1="60" y1="22" x2="60" y2="66" {_S}/><line x1="28" y1="32" x2="54" y2="32" {_S}/><line x1="28" y1="40" x2="54" y2="40" {_S}/><line x1="28" y1="48" x2="50" y2="48" {_S}/><line x1="66" y1="32" x2="92" y2="32" {_S}/><line x1="66" y1="40" x2="92" y2="40" {_S}/><line x1="66" y1="48" x2="88" y2="48" {_S}/><text x="92" y="60" font-family="serif" font-size="14" {_FILL} stroke="none">END</text>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# PLAYER INTERACTION (7)
# ─────────────────────────────────────────────────────────────────────

INTERACTION = {
    "solo-in-parallel": {
        "description": "Everyone plays at the same time but doesn't really affect each other. You build your own thing while others build theirs.",
        "svg": svg(f'<g transform="translate(28 36)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/><line x1="-6" y1="2" x2="6" y2="2" {_S}/></g><g transform="translate(60 36)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/><line x1="-6" y1="2" x2="6" y2="2" {_S}/></g><g transform="translate(92 36)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/><line x1="-6" y1="2" x2="6" y2="2" {_S}/></g><line x1="42" y1="20" x2="42" y2="62" stroke="#C75B39" stroke-dasharray="2 3"/><line x1="74" y1="20" x2="74" y2="62" stroke="#C75B39" stroke-dasharray="2 3"/>'),
    },
    "direct-confrontation": {
        "description": "Players attack, steal, or sabotage each other on purpose. \"Take that!\" — they target you, you target them.",
        "svg": svg(f'<g transform="translate(28 40)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(92 40)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><path d="M40 38 l36 0" stroke="#C75B39" stroke-width="2.5"/><path d="M76 34 l4 4 l-4 4" stroke="#C75B39" stroke-width="2.5" fill="none"/><path d="M80 42 l-36 0" stroke="#C75B39" stroke-width="2.5"/><path d="M44 46 l-4 -4 l4 -4" stroke="#C75B39" stroke-width="2.5" fill="none"/>'),
    },
    "indirect-via-board": {
        "description": "You don't attack each other directly — you change the board, take spots, build walls. They feel it through the game state.",
        "svg": svg(f'<rect x="34" y="20" width="52" height="36" {_S} {_TINT}/><circle cx="46" cy="32" r="3" {_FILL} stroke="none"/><circle cx="60" cy="32" r="3" stroke="#2D3436" fill="white"/><circle cx="74" cy="32" r="3" {_FILL} stroke="none"/><circle cx="46" cy="46" r="3" stroke="#2D3436" fill="white"/><circle cx="60" cy="46" r="3" {_FILL} stroke="none"/><circle cx="74" cy="46" r="3" stroke="#2D3436" fill="white"/><g transform="translate(18 50)"><circle cx="0" cy="-10" r="4" {_S}/><line x1="0" y1="-6" x2="0" y2="10" {_S}/></g><g transform="translate(102 50)"><circle cx="0" cy="-10" r="4" {_S}/><line x1="0" y1="-6" x2="0" y2="10" {_S}/></g>'),
    },
    "fully-cooperative": {
        "description": "Everyone is on the same team, against the game itself. You all win together, or you all lose together.",
        "svg": svg(f'<g transform="translate(36 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/><line x1="6" y1="2" x2="20" y2="2" {_S}/></g><g transform="translate(60 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(84 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/><line x1="-6" y1="2" x2="-20" y2="2" {_S}/></g><path d="M30 64 Q60 70 90 64" stroke="#C75B39" stroke-width="2.5" fill="none"/>'),
    },
    "semi-cooperative": {
        "description": "Mostly working together, but each player has a small private reason to win more than the others.",
        "svg": svg(f'<g transform="translate(40 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(64 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(88 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/><rect x="-6" y="-22" width="12" height="6" rx="1" {_FILL} stroke="none"/><text x="0" y="-17" font-family="serif" font-size="6" fill="white" text-anchor="middle">★</text></g><path d="M34 60 Q64 66 94 60" stroke="#2D3436" stroke-width="2" fill="none" stroke-dasharray="3 3"/>'),
    },
    "team-vs-team": {
        "description": "Two teams play against each other. You and your teammates work together, against the other side.",
        "svg": svg(f'<g transform="translate(20 44)"><circle cx="0" cy="-10" r="5" {_S} {_TINT}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(40 44)"><circle cx="0" cy="-10" r="5" {_S} {_TINT}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><line x1="58" y1="20" x2="58" y2="64" {_FILL} stroke-width="2" stroke="#C75B39" stroke-dasharray="4 3"/><g transform="translate(76 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(96 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g>'),
    },
    "traitor": {
        "description": "Most players are on the same team — but one (or more) is secretly playing against everyone else. Can you spot them?",
        "svg": svg(f'<g transform="translate(28 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(54 44)"><circle cx="0" cy="-10" r="5" {_S}/><line x1="0" y1="-5" x2="0" y2="14" {_S}/></g><g transform="translate(80 44)"><circle cx="0" cy="-10" r="5" {_S} {_FILL} stroke-width="0"/><line x1="0" y1="-5" x2="0" y2="14" stroke="#C75B39" stroke-width="2"/><path d="M-3 -12 l3 -4 l3 4" stroke="#C75B39" stroke-width="1.5" fill="none"/></g><text x="80" y="20" font-family="serif" font-size="12" text-anchor="middle" {_FILL} stroke="none">?</text>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# CHANCE-SKILL (4)
# ─────────────────────────────────────────────────────────────────────

CHANCE_SKILL = {
    "mostly-chance": {
        "description": "Dice and random draws decide most of what happens. Skill barely matters. Snakes and Ladders is mostly chance.",
        "svg": svg(f'<rect x="34" y="18" width="28" height="28" rx="4" {_S}/><circle cx="40" cy="24" r="2" {_FILL} stroke="none"/><circle cx="48" cy="32" r="2" {_FILL} stroke="none"/><circle cx="56" cy="40" r="2" {_FILL} stroke="none"/><rect x="64" y="32" width="28" height="28" rx="4" {_S} {_TINT}/><circle cx="72" cy="38" r="2" {_FILL} stroke="none"/><circle cx="84" cy="38" r="2" {_FILL} stroke="none"/><circle cx="78" cy="46" r="2" {_FILL} stroke="none"/><circle cx="72" cy="54" r="2" {_FILL} stroke="none"/><circle cx="84" cy="54" r="2" {_FILL} stroke="none"/>'),
    },
    "chance-with-mitigation": {
        "description": "There IS dice and randomness, but you have ways to soften bad luck — re-rolls, cards, choices. You're not helpless.",
        "svg": svg(f'<rect x="22" y="22" width="24" height="24" rx="3" {_S}/><circle cx="29" cy="29" r="2" {_FILL} stroke="none"/><circle cx="39" cy="39" r="2" {_FILL} stroke="none"/><path d="M58 32 l8 -2 l8 2 l0 10 q-8 6 -16 0 z" {_S} {_TINT}/><path d="M66 32 l0 14" {_S}/><path d="M58 38 l16 0" {_S}/><text x="92" y="40" font-family="serif" font-size="11" {_FILL} stroke="none">+</text>'),
    },
    "skill-with-luck-tempering": {
        "description": "Mostly your choices matter, but a small bit of luck adds spice. Catan and Carcassonne sit here.",
        "svg": svg(f'<g transform="translate(38 36)"><circle cx="0" cy="0" r="14" {_S} {_TINT}/><path d="M-7 -2 q3 -8 7 -4 q4 -4 7 4 q-3 8 -7 6 q-4 2 -7 -6" {_FILL} stroke="none"/></g><rect x="78" y="32" width="14" height="14" rx="2" {_S}/><circle cx="85" cy="39" r="1.6" {_FILL} stroke="none"/>'),
    },
    "mostly-skill": {
        "description": "Pure brain-work. No dice, no surprises. The smartest player wins. Chess and Go are mostly skill.",
        "svg": svg(f'<g transform="translate(60 38)"><circle cx="0" cy="0" r="20" {_S} {_TINT}/><path d="M-12 -4 q4 -16 12 -8 q8 -8 12 8 q-4 16 -12 10 q-8 6 -12 -10" {_FILL} stroke="none"/><line x1="-12" y1="0" x2="12" y2="0" stroke="#fbe4d8" stroke-width="0.6"/></g>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# THEME (8)
# ─────────────────────────────────────────────────────────────────────

THEME = {
    "abstract": {
        "description": "No story — just shapes, colours, patterns. Like Chess or Go. The game is the game.",
        "svg": svg(f'<rect x="22" y="22" width="20" height="20" {_S} {_TINT}/><circle cx="60" cy="32" r="10" {_S} {_FILL} stroke-width="0"/><polygon points="86,18 102,46 70,46" {_S}/>'),
    },
    "historical": {
        "description": "Set in real history — wars, empires, trade routes. Real places, real times.",
        "svg": svg(f'<path d="M22 24 q-4 -4 0 -8 l68 0 q4 4 0 8 l0 32 q4 4 0 8 l-68 0 q-4 -4 0 -8 z" {_S} {_TINT}/><line x1="30" y1="30" x2="80" y2="30" {_S}/><line x1="30" y1="38" x2="80" y2="38" {_S}/><line x1="30" y1="46" x2="70" y2="46" {_S}/><circle cx="98" cy="36" r="8" {_S} {_FILL} stroke-width="0"/><text x="98" y="40" font-family="serif" font-size="10" text-anchor="middle" fill="white">★</text>'),
    },
    "fantasy": {
        "description": "Magic, dragons, wizards, quests. Things that don't exist in real life.",
        "svg": svg(f'<line x1="50" y1="14" x2="50" y2="48" {_S}/><polygon points="50,10 56,18 44,18" {_FILL} stroke="none"/><line x1="42" y1="48" x2="58" y2="48" {_S}/><line x1="50" y1="48" x2="50" y2="58" {_S}/><path d="M70 28 q12 -2 16 6 q-2 12 -10 12 q-2 8 -8 8 q-6 -2 -4 -10 q-8 -2 -6 -10 q4 -8 12 -6" {_S}/><circle cx="78" cy="36" r="2" {_FILL} stroke="none"/>'),
    },
    "science-fiction": {
        "description": "Space, robots, distant futures. Aliens, lasers, planets.",
        "svg": svg(f'<path d="M60 14 q-6 4 -8 14 l0 24 l16 0 l0 -24 q-2 -10 -8 -14 z" {_S} {_TINT}/><circle cx="60" cy="32" r="3" {_FILL} stroke="none"/><path d="M52 52 l-6 10 l8 -2 z" {_FILL} stroke="none"/><path d="M68 52 l6 10 l-8 -2 z" {_FILL} stroke="none"/><path d="M58 64 l4 6 l-2 0 z" {_FILL} stroke="none"/><circle cx="22" cy="22" r="1" fill="#2D3436"/><circle cx="100" cy="32" r="1" fill="#2D3436"/><circle cx="28" cy="58" r="1" fill="#2D3436"/>'),
    },
    "everyday-life": {
        "description": "Farms, kitchens, trains, cities — places and things you recognise from real life.",
        "svg": svg(f'<polygon points="40,28 60,16 80,28" {_S}/><rect x="40" y="28" width="40" height="30" {_S} {_TINT}/><rect x="54" y="40" width="12" height="18" {_S}/><rect x="44" y="34" width="6" height="6" {_S}/><rect x="70" y="34" width="6" height="6" {_S}/>'),
    },
    "absurd": {
        "description": "Weird, silly, nonsense — exploding kittens, unstable unicorns. Made to make you laugh.",
        "svg": svg(f'<circle cx="60" cy="36" r="20" {_S}/><circle cx="52" cy="32" r="2" fill="#2D3436"/><circle cx="68" cy="32" r="2" fill="#2D3436"/><path d="M50 44 q10 8 20 0" {_S}/><path d="M44 22 l-4 -8 m4 -2 l4 6" {_S}/><path d="M76 22 l4 -8 m-4 -2 l-4 6" {_S}/><circle cx="40" cy="14" r="2" {_FILL} stroke="none"/>'),
    },
    "educational": {
        "description": "Teaches you something while you play — history facts, words, maths.",
        "svg": svg(f'<rect x="32" y="22" width="44" height="32" rx="2" {_S} {_TINT}/><line x1="40" y1="30" x2="68" y2="30" {_S}/><line x1="40" y1="36" x2="68" y2="36" {_S}/><line x1="40" y1="42" x2="60" y2="42" {_S}/><circle cx="86" cy="32" r="8" {_FILL} stroke="none"/><path d="M86 24 q-2 -4 2 -6" {_S}/><text x="86" y="36" font-family="serif" font-size="10" text-anchor="middle" fill="white">A+</text>'),
    },
    "real-world-issue": {
        "description": "About something happening now — climate, justice, migration. The game makes you think about it.",
        "svg": svg(f'<circle cx="60" cy="40" r="22" {_S} {_TINT}/><path d="M38 40 q22 -16 44 0" {_S}/><path d="M38 40 q22 16 44 0" {_S}/><line x1="60" y1="18" x2="60" y2="62" {_S}/><path d="M44 30 q16 -2 32 0" {_S}/><path d="M44 50 q16 2 32 0" {_S}/><path d="M48 16 l4 -4 m-4 0 l4 4" stroke="#C75B39" stroke-width="2"/>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# INFORMATION VISIBILITY (5)
# ─────────────────────────────────────────────────────────────────────

INFORMATION = {
    "full-information": {
        "description": "Everything is visible. Every player sees every card, every move. No secrets. Like Chess.",
        "svg": svg(f'<path d="M16 40 q22 -22 44 -22 q22 0 44 22 q-22 22 -44 22 q-22 0 -44 -22 z" {_S} {_TINT}/><circle cx="60" cy="40" r="10" {_S}/><circle cx="60" cy="40" r="4" {_FILL} stroke="none"/>'),
    },
    "hidden-hands": {
        "description": "Each player holds cards no one else can see. You bluff, hint, and guess.",
        "svg": svg(f'<g transform="translate(60 50) rotate(-12)"><rect x="-9" y="-22" width="18" height="32" rx="2" {_S} {_TINT}/></g><g transform="translate(60 50) rotate(0)"><rect x="-9" y="-26" width="18" height="32" rx="2" {_S} {_TINT}/><line x1="-3" y1="-20" x2="3" y2="-20" stroke="#C75B39" stroke-width="1.6"/><line x1="-3" y1="-14" x2="3" y2="-14" stroke="#C75B39" stroke-width="1.6"/></g><g transform="translate(60 50) rotate(12)"><rect x="-9" y="-22" width="18" height="32" rx="2" {_S} {_TINT}/></g><path d="M28 40 q-6 6 0 12" stroke="#2D3436" stroke-width="1.6" fill="none"/>'),
    },
    "hidden-identity": {
        "description": "Some players have a secret role — like a spy or a villain. Nobody knows who is who at the start.",
        "svg": svg(f'<path d="M30 28 q30 -8 60 0 q4 6 -2 12 q-12 6 -28 6 q-16 0 -28 -6 q-6 -6 -2 -12 z" {_S} {_TINT}/><circle cx="44" cy="34" r="4" fill="#2D3436"/><circle cx="76" cy="34" r="4" fill="#2D3436"/><path d="M58 40 q2 4 4 0" {_S}/><path d="M40 50 l4 8 M80 50 l-4 8" {_S}/>'),
    },
    "deduction": {
        "description": "Use clues to figure out hidden facts — who, what, where. Like Cluedo or a mystery.",
        "svg": svg(f'<circle cx="44" cy="34" r="14" {_S}/><circle cx="44" cy="34" r="9" {_S} {_TINT}/><line x1="55" y1="44" x2="74" y2="62" stroke="#2D3436" stroke-width="3" stroke-linecap="round"/><text x="44" y="38" font-family="serif" font-size="14" text-anchor="middle" {_FILL} stroke="none">?</text>'),
    },
    "bluffing": {
        "description": "Lie about what you have. Pretend you're stronger or weaker than you are. Other players have to guess.",
        "svg": svg(f'<circle cx="60" cy="38" r="20" {_S} {_TINT}/><path d="M52 32 l4 4 M68 32 l-4 4" {_S}/><path d="M50 50 l20 0" {_S} stroke-width="2"/><path d="M44 28 q4 -8 14 -6" {_S}/><path d="M76 28 q-4 -8 -14 -6" {_S}/><circle cx="84" cy="20" r="4" {_FILL} stroke="none"/><text x="84" y="24" font-family="serif" font-size="6" text-anchor="middle" fill="white">!</text>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# FEELINGS (15)
# ─────────────────────────────────────────────────────────────────────

FEELINGS_META = {
    "excited": {
        "description": "Loud table. Big swings. Everyone leaning in. The kind of feeling where you can't sit still.",
        "svg": svg(f'<text x="40" y="50" font-family="serif" font-size="36" font-weight="700" {_FILL} stroke="none">!</text><text x="60" y="50" font-family="serif" font-size="36" font-weight="700" {_FILL} stroke="none">!</text><text x="80" y="50" font-family="serif" font-size="36" font-weight="700" {_FILL} stroke="none">!</text><path d="M30 56 l-6 8 M90 56 l6 8" {_S}/>'),
    },
    "clever": {
        "description": "You feel smart. Your choices made the game work. The good move was hard to see — but you saw it.",
        "svg": svg(f'<path d="M60 14 q-12 0 -12 14 q0 8 6 12 l0 8 l12 0 l0 -8 q6 -4 6 -12 q0 -14 -12 -14 z" {_S} {_TINT}/><line x1="54" y1="52" x2="66" y2="52" {_S}/><line x1="56" y1="58" x2="64" y2="58" {_S}/><circle cx="60" cy="28" r="3" {_FILL} stroke="none"/>'),
    },
    "silly": {
        "description": "Everything feels ridiculous. Cards explode, unicorns appear, you laugh until you can't breathe.",
        "svg": svg(f'<circle cx="60" cy="38" r="20" {_S} {_TINT}/><circle cx="52" cy="32" r="2.5" fill="#2D3436"/><circle cx="68" cy="32" r="2.5" fill="#2D3436"/><path d="M48 44 q12 12 24 0" {_S} stroke-width="2.5"/><path d="M40 22 l-4 -6 m4 -2 l2 6" {_S}/><path d="M82 22 l4 -6 m-4 -2 l-2 6" {_S}/>'),
    },
    "tense": {
        "description": "Something could go wrong any second. You're holding your breath. Every choice feels heavy.",
        "svg": svg(f'<line x1="14" y1="40" x2="106" y2="40" {_S} stroke-width="2.5"/><path d="M40 40 q20 -16 40 0" stroke="#C75B39" stroke-width="2.5" fill="none"/><circle cx="60" cy="32" r="4" {_FILL} stroke="none"/><line x1="14" y1="36" x2="14" y2="44" {_S}/><line x1="106" y1="36" x2="106" y2="44" {_S}/>'),
    },
    "together": {
        "description": "You and your friends share what happens. Wins are everyone's. Losses are too. One team, one feeling.",
        "svg": svg(f'<g transform="translate(36 44)"><circle cx="0" cy="-10" r="5" {_S}/></g><g transform="translate(60 44)"><circle cx="0" cy="-10" r="5" {_S} {_FILL} stroke-width="0"/></g><g transform="translate(84 44)"><circle cx="0" cy="-10" r="5" {_S}/></g><path d="M30 38 l24 0 l6 -4 l6 4 l24 0" {_S}/><path d="M36 50 l0 14 M60 50 l0 14 M84 50 l0 14" {_S}/>'),
    },
    "sneaky": {
        "description": "You're hiding something. Plotting in secret. The fun is in not letting anyone see your move.",
        "svg": svg(f'<g transform="translate(60 50)"><circle cx="0" cy="-22" r="6" {_S}/><path d="M-6 -16 l-2 12 M6 -16 l2 12" {_S}/><line x1="-8" y1="-4" x2="-12" y2="10" {_S}/><line x1="8" y1="-4" x2="12" y2="10" {_S}/><path d="M-12 -22 l24 0 l0 4 l-24 0 z" {_FILL} stroke="none"/></g><path d="M14 70 q4 -10 14 -8 q10 4 18 -2 q10 -8 22 -2 q10 6 22 0 q10 -4 16 4" stroke="#C75B39" stroke-width="1.5" fill="none" stroke-dasharray="3 3"/>'),
    },
    "lucky": {
        "description": "The dice rolled your way. The card you drew was perfect. You can't believe how it worked out.",
        "svg": svg(f'<path d="M60 18 q-6 12 -16 14 q10 4 16 16 q6 -12 16 -16 q-10 -2 -16 -14 z" {_FILL} stroke="none"/><path d="M30 50 l4 8 l-8 0 z" {_FILL} stroke="none"/><path d="M88 56 l4 8 l-8 0 z" {_FILL} stroke="none"/><circle cx="40" cy="28" r="2" {_FILL} stroke="none"/><circle cx="86" cy="32" r="2" {_FILL} stroke="none"/><circle cx="44" cy="62" r="2" {_FILL} stroke="none"/>'),
    },
    "in charge": {
        "description": "Your decisions matter. You're directing what happens — choosing where to spend, where to build, what to do.",
        "svg": svg(f'<path d="M30 52 l8 -22 l10 14 l12 -22 l12 22 l10 -14 l8 22 z" {_S} {_TINT}/><line x1="30" y1="52" x2="90" y2="52" {_S} stroke-width="2.5"/><circle cx="44" cy="34" r="2.5" {_FILL} stroke="none"/><circle cx="60" cy="26" r="2.5" {_FILL} stroke="none"/><circle cx="76" cy="34" r="2.5" {_FILL} stroke="none"/>'),
    },
    "surprised": {
        "description": "You did NOT see that coming. The card flips, the secret is revealed, the game changes shape.",
        "svg": svg(f'<circle cx="60" cy="40" r="20" {_S} {_TINT}/><circle cx="52" cy="36" r="3" fill="#2D3436"/><circle cx="68" cy="36" r="3" fill="#2D3436"/><circle cx="60" cy="50" r="4" {_S}/><path d="M40 18 l-2 -6 M80 18 l2 -6 M28 40 l-6 0 M92 40 l6 0" stroke="#C75B39" stroke-width="2"/>'),
    },
    "thoughtful": {
        "description": "You stop. You look at the board. You think. There's no rush — the game waits for you.",
        "svg": svg(f'<path d="M40 36 q-8 -16 6 -22 q14 -4 22 4 q14 -2 16 12 q4 12 -8 18 q-4 8 -14 6 q-12 4 -18 -6 q-12 -2 -4 -12 z" {_S} {_TINT}/><circle cx="36" cy="56" r="3" {_TINT} stroke="#2D3436" stroke-width="2"/><circle cx="28" cy="64" r="2" {_TINT} stroke="#2D3436" stroke-width="1.5"/>'),
    },
    "fast": {
        "description": "Turns whip by. You don't have time to plan everything. Quick hands, quick choices.",
        "svg": svg(f'<line x1="14" y1="30" x2="86" y2="30" stroke="#C75B39" stroke-width="3"/><line x1="22" y1="40" x2="94" y2="40" stroke="#C75B39" stroke-width="3"/><line x1="14" y1="50" x2="80" y2="50" stroke="#C75B39" stroke-width="3"/><path d="M86 30 l8 -4 l0 8 z M94 40 l8 -4 l0 8 z M80 50 l8 -4 l0 8 z" {_FILL} stroke="none"/>'),
    },
    "unfair-in-a-fun-way": {
        "description": "Someone got wrecked — and everyone laughed, including them. It wasn't \"fair\" but it was so funny.",
        "svg": svg(f'<polygon points="50,14 64,14 56,32 70,32 44,62 50,40 36,40" {_FILL} stroke="none"/><circle cx="86" cy="22" r="3" {_FILL} stroke="none"/><circle cx="100" cy="36" r="2" {_FILL} stroke="none"/><circle cx="92" cy="56" r="2.5" {_FILL} stroke="none"/>'),
    },
    "careful": {
        "description": "One wrong move and it's over. Every action matters. You triple-check before you commit.",
        "svg": svg(f'<line x1="60" y1="14" x2="60" y2="56" {_S}/><line x1="40" y1="22" x2="80" y2="22" {_S}/><path d="M40 22 l-6 14 l12 0 z" {_S} {_TINT}/><path d="M80 22 l-6 14 l12 0 z" {_S} {_TINT}/><line x1="50" y1="56" x2="70" y2="56" {_S}/><circle cx="42" cy="38" r="3" {_FILL} stroke="none"/><circle cx="80" cy="38" r="3" {_FILL} stroke="none"/>'),
    },
    "daring": {
        "description": "You went for it. The risky move. The big play. It might fail spectacularly — and that's the point.",
        "svg": svg(f'<path d="M14 56 l36 0 l0 -8 l36 0 l0 -22 l20 0" {_S} fill="none"/><circle cx="74" cy="20" r="5" {_FILL} stroke="none"/><path d="M86 22 l16 0 l-4 -4 m4 4 l-4 4" stroke="#C75B39" stroke-width="2.5" fill="none"/><line x1="14" y1="56" x2="14" y2="62" stroke="#2D3436"/><line x1="106" y1="20" x2="106" y2="14" stroke="#2D3436"/>'),
    },
    "friendly": {
        "description": "Warm. No one's out to get anyone. The game is something you do together, not against each other.",
        "svg": svg(f'<path d="M60 60 q-30 -16 -30 -34 q0 -10 10 -10 q10 0 20 10 q10 -10 20 -10 q10 0 10 10 q0 18 -30 34 z" {_S} {_FILL} stroke-width="0"/>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# SIMULATION (6) — added 16 October 2026
# ─────────────────────────────────────────────────────────────────────

SIMULATION = {
    "model-a-system": {
        "description": "The board works like a real system, such as how water moves between a village's wells and fields, so a move has the effect it would have in real life.",
        "svg": svg(f'<circle cx="30" cy="24" r="9" {_S} {_TINT}/><circle cx="90" cy="24" r="9" {_S} {_TINT}/><circle cx="60" cy="62" r="9" {_S} {_FILL}/><path d="M41 24 h38 M86 33 l-18 21 M52 55 l-17 -22" {_S}/><path d="M74 20 l5 4 l-5 4 M66 50 l2 4 l-5 0 M38 39 l-3 -6 l6 1" {_S}/>'),
    },
    "stakeholder-roles": {
        "description": "Each player plays a real group with its own needs, such as farmers, a village council or a shopkeeper. You see the problem from where they stand.",
        "svg": svg(f'<circle cx="30" cy="26" r="7" {_S} {_TINT}/><path d="M20 58 q10 -22 20 0" {_S}/><circle cx="60" cy="26" r="7" {_S} {_FILL}/><path d="M50 58 q10 -22 20 0" {_S}/><circle cx="90" cy="26" r="7" {_S} {_TINT}/><path d="M80 58 q10 -22 20 0" {_S}/><path d="M52 16 h16" {_S}/>'),
    },
    "shared-resource": {
        "description": "Everyone draws from one limited thing, such as the water under a village. If players take too much, it runs out for everyone. Villages in Andhra Pradesh have played games like this about their own groundwater.",
        "svg": svg(f'<ellipse cx="60" cy="56" rx="34" ry="12" {_S} {_TINT}/><path d="M60 14 v28 M28 18 l18 26 M92 18 l-18 26" {_S}/><circle cx="60" cy="14" r="3" {_FILL} stroke="none"/><circle cx="28" cy="18" r="3" {_FILL} stroke="none"/><circle cx="92" cy="18" r="3" {_FILL} stroke="none"/>'),
    },
    "delayed-effects": {
        "description": "What you do now shows its effect only a few rounds later, the way a choice made this year shows up years later in real life.",
        "svg": svg(f'<path d="M14 54 h92" {_S}/><path d="M100 49 l6 5 l-6 5" {_S}/><path d="M34 50 v8 M54 50 v8 M74 50 v8" {_S}/><circle cx="20" cy="54" r="4" {_FILL} stroke="none"/><path d="M92 50 v-20" {_S}/><path d="M92 36 q-10 -6 -12 -14 q10 2 12 10 q2 -8 12 -10 q-2 8 -12 14" {_S} {_TINT}/>'),
    },
    "try-a-rule": {
        "description": "Players agree a new rule for everyone, then play on to see what it changes. It is a safe way to test a rule before trying it for real.",
        "svg": svg(f'<rect x="30" y="12" width="46" height="58" rx="3" {_S} {_TINT}/><path d="M38 24 h30 M38 34 h30 M38 44 h18" {_S}/><circle cx="82" cy="58" r="12" {_S}/><path d="M76 58 l4 4 l8 -8" stroke="#C75B39" stroke-width="2.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'),
    },
    "debrief": {
        "description": "After the game, everyone talks it through: What happened? Why? How is it like the real problem? What would happen if we changed something?",
        "svg": svg(f'<path d="M14 18 h48 a6 6 0 0 1 6 6 v18 a6 6 0 0 1 -6 6 h-30 l-10 8 v-8 h-8 a6 6 0 0 1 -6 -6 v-18 a6 6 0 0 1 6 -6 z" {_S} {_TINT}/><path d="M58 34 h44 a6 6 0 0 1 6 6 v16 a6 6 0 0 1 -6 6 h-6 v8 l-10 -8 h-28 a6 6 0 0 1 -6 -6" {_S}/><text x="38" y="38" font-family="serif" font-size="14" text-anchor="middle" {_FILL} stroke="none">?</text>'),
    },
}


# ─────────────────────────────────────────────────────────────────────
# Combined map — id → {description, svg}
# ─────────────────────────────────────────────────────────────────────

ALL_BLOCKS: dict = {}
for d in (CORE_MECHANICS, VICTORY, INTERACTION, CHANCE_SKILL, THEME, INFORMATION, SIMULATION, FEELINGS_META):
    ALL_BLOCKS.update(d)


def meta_for(block_id: str) -> dict:
    return ALL_BLOCKS.get(block_id, {"description": "", "svg": ""})
