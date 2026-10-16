"""The joining words between knowledge-base sentences, written in advance (16 October 2026) so the feedback needs no model.

Each slot has a few versions. The code picks one from the sentence it introduces, so the same canvas always reads the same
and different canvases read differently. Edit freely; {blocks} and {games} are filled in by templates.py.
"""

BRIDGES = {
    # before the main tendency of the whole canvas
    "tendency": [
        "Your game tends to be like this:",
        "Put together, these blocks make a game like this:",
        "Here is the kind of game that is taking shape:",
    ],
    # before the tendency of a further pair or triad
    "more": [
        "{blocks} together add this:",
        "Look at {blocks} as well:",
        "And with {blocks}:",
    ],
    # before the pros of the main match
    "pros": [
        "What this brings:",
        "What players get from this mix:",
        "This combination adds a few things.",
    ],
    # before the cons of the main match
    "cons": [
        "Trade-offs to think about:",
        "Something to watch for:",
        "The other side of it:",
    ],
    # before a conflict's student note
    "conflict": [
        "Notice that you have {blocks} together.",
        "You have {blocks} on the same canvas.",
        "{blocks} are both in your game.",
    ],
    # before the example games
    "games": [
        "Games that do something like this: {games}.",
        "You can see a similar mix in {games}.",
        "Games built on blocks like these: {games}.",
    ],
    # first sentence of the closing summary
    "summary_open": [
        "Here is the game you designed.",
        "This is your finished design.",
        "Your game is complete.",
    ],
    # last sentence of the closing summary
    "summary_close": [
        "You designed a {blocks} game. That is a real shape. Now you would build a prototype.",
        "You designed a {blocks} game. Next comes a prototype on paper.",
        "You designed a {blocks} game. The next step is to make a rough copy and play it.",
    ],
}
