"""Check every curated example game against its full BoardGameGeek tags.

The mapping below is the rule: a block is confirmed when the game carries one of its tags, absent when it carries none,
and 'not checkable' when BoardGameGeek has no tag for that block. A claim is false only when a checkable block is absent,
or when full information meets a hidden-information tag. The known games' designs in games.json are checked the same way, against their 'bgg' entry.
Usage: python drafted/bgg_check.py drafted/bgg-tags.json   (writes drafted/bgg-verdicts.json)
"""
import json, sys

TAGS = {
    "roll-and-move": {"Roll / Spin and Move"},
    "drafting": {"Open Drafting", "Closed Drafting"},
    "bidding": {"Auction / Bidding", "Constrained Bidding", "Auction: Dutch", "Auction: English", "Auction: Once Around", "Auction: Sealed Bid",
                "Auction: Turn Order Until Pass", "Closed Economy Auction", "Auction: Fixed Placement", "Auction: Dexterity", "Auction: Dutch Priority",
                "Auction: Multiple Lot", "Auction: Sealed Bid With Cancellation", "Selection Order Bid", "Turn Order: Auction"},
    "push-your-luck": {"Push Your Luck"},
    "area-control": {"Area Majority / Influence", "King of the Hill"},
    "worker-placement": {"Worker Placement", "Worker Placement with Dice Workers", "Worker Placement, Different Worker Types"},
    "pattern-building": {"Pattern Building"},
    "hand-management": {"Hand Management"},
    "trick-taking": {"Trick-taking"},
    "negotiation": {"Negotiation", "Trading"},
    "set-collection": {"Set Collection"},
    "tile-placement": {"Tile Placement"},
    "race-to-finish": {"Race"},
    "last-standing": {"Player Elimination"},
    "cooperative-survival": {"Cooperative Game"},
    "shared-objective": {"Cooperative Game", "Team-Based Game"},
    "narrative-completion": {"Storytelling", "Narrative Choice / Paragraph", "Scenario / Mission / Campaign Game"},
    "direct-confrontation": {"Take That", "Player Elimination", "King of the Hill", "Fighting", "Wargame", "Area Majority / Influence"},
    "fully-cooperative": {"Cooperative Game"},
    "semi-cooperative": {"Semi-Cooperative Game"},
    "team-vs-team": {"Team-Based Game"},
    "traitor": {"Traitor Game"},
    "mostly-chance": {"Dice Rolling", "Push Your Luck"},
    "hidden-identity": {"Hidden Roles", "Traitor Game"},
    "deduction": {"Deduction"},
    "bluffing": {"Bluffing"},
}
HIDDEN = {"Hidden Roles", "Closed Drafting", "Hidden Victory Points", "Secret Unit Deployment", "Deduction", "Traitor Game", "Bluffing"}
# BoardGameGeek applies these unevenly (plainly confrontational games and plain race games often lack them), so a missing tag is no evidence
ONLY_CONFIRMS = {"direct-confrontation", "race-to-finish", "mostly-chance"}

cache = json.load(open(sys.argv[1]))
kb = json.load(open("interactions.json"))


def check(kind, elements, game, status=None):
    c = cache[game]
    tags = set(c["mechanisms"]) | set(c["categories"])
    verdicts = {}
    for el in elements:
        if el == "full-information":
            hidden = sorted(tags & HIDDEN)
            verdicts[el] = f"contradicted ({', '.join(hidden)})" if hidden else "not checkable"
        elif el in TAGS:
            hit = sorted(tags & TAGS[el])
            verdicts[el] = f"confirmed ({', '.join(hit)})" if hit else ("not checkable" if el in ONLY_CONFIRMS else "absent")
        else:
            verdicts[el] = "not checkable"
    false = [el for el, v in verdicts.items() if v == "absent" or v.startswith("contradicted")]
    result = "false" if false else ("confirmed" if all(v.startswith("confirmed") for v in verdicts.values()) else "partly checkable, nothing against it")
    return {"kind": kind, "elements": elements, "game": game, "status": status,
            "result": result, "verdicts": verdicts, "bgg": f"https://boardgamegeek.com/boardgame/{c['id']}"}


rows = []
for kind in ("pairs", "triads"):
    for e in kb[kind]:
        for g in e.get("exemplars", []):
            rows.append(check(kind[:-1], e["elements"], g, e.get("verification_status")))
for g in json.load(open("games.json")):
    if "bgg" in g:
        blocks = [b for v in g["design"].values() for b in (v if isinstance(v, list) else [v])]
        rows.append(check("known game", blocks, g["bgg"]))
json.dump(rows, open("drafted/bgg-verdicts.json", "w"), indent=1, ensure_ascii=False)
from collections import Counter
print(Counter(r["result"] for r in rows))
for r in rows:
    if r["result"] == "false":
        bad = {el: v for el, v in r["verdicts"].items() if v == "absent" or v.startswith("contradicted")}
        print(f"FALSE  {'+'.join(r['elements']):58} {r['game']:30} {bad}")
