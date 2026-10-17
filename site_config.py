"""Where boardgameBuilder and its wiki live. Change DOMAIN and both move together.

The tool's page, the wiki's pages and the link-preview image all take their addresses from here.
After changing it: point the new names at the server and add them as custom domains in CapRover,
set the callback addresses of the wiki's GitHub and Google sign-in to the new wiki address, set the
repository variable WIKI_URL, run docs/make_og.py to redraw the preview image (the wiki's own preview image, wiki/static/og.png, is a screenshot and is redrawn by hand), and update the
addresses written in README.md and DEPLOY.md.
"""

DOMAIN = "blevn.xyz"

TOOL_URL = f"https://boardgame.{DOMAIN}"
WIKI_URL = f"https://boardgame-wiki.{DOMAIN}"
