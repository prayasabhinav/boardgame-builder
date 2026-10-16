# boardgameBuilder wiki

A public wiki of boardgameBuilder's whole knowledge base, one page per entry, where people who sign in record the checks they make under their own names and propose changes and new entries.

The tool can only be as right as its entries, and 2,471 entries are too many for one person to check. The wiki is where the checking is shared.

## What is on it

Every entry the tool's feedback is made from, read straight from the tool's own files, so the wiki never holds a second copy that could drift:

| Kind | From | How many |
|---|---|---|
| Blocks, with their drawings | `block_meta.py` | 66 |
| Feelings | `interactions.json` | 15 |
| Pairs | `interactions.json` (curated) and `interactions-drafted.json` (drafted) | 1,369 |
| Triads | `interactions.json` | 15 |
| Conflicts | `interactions.json` | 5 |
| Theme lines | `interactions-drafted.json` | 11 |
| Feeling and block judgements | both | 990 |

Pairs and triads also show the BoardGameGeek check of their example games (`drafted/bgg-verdicts.json`) and the games removed after it. The two working notes, `mechanics-shortlist.md` and `feeling-blocks.md`, are on it too.

## What people can do

Anyone can read everything. Signing in, with GitHub or Google, lets a person:

- **Add a record** to an entry: *verified* (checked against a source) or *validated* (tried with people at a table), what they found (*holds*, *partly holds*, *does not hold*), how they know, and a suggested wording if they have one. Records appear at once, under the person's name, with the entry's text as it stood. A person can withdraw their own record; it stays visible as withdrawn.
- **Propose a change** to an entry: new wording, different example games, or a different judgement for a feeling and a block.
- **Propose a new entry**: a triad, a conflict, a block or a feeling.

A proposal stays private to its author and the editors until an editor approves or rejects it. A rejection carries a reason the author reads. An approved change shows on the entry at once, with the text the tool still has kept readable until the tool catches up; an approved new entry appears marked *proposed*. Who approved a proposal is stored and never shown or exported. Proposals using verdict words (good, bad, best, should, must and the like) are refused before an editor sees them, because the tool's build refuses them too.

The marks in the lists follow one rule: where every record of a kind on an entry gives the same finding, the mark shows it; where they differ, it says *records differ*. Nothing adds records up into a score for an entry or a count for a person.

Editors can also hide a record that is spam or abuse; the reason shows in its place.

Anyone signed in can apply to join the editors. Owners see a **Community** page: the applications, to accept or decline with a reason the applicant reads, and everyone who has signed in, where an owner makes or removes an editor. Editor rights are read afresh on every request, so a change applies at once.

## Applying to be an editor

Anyone signed in can apply from **Join the editors** in the top bar, saying why they would like to and what they know of games. An owner accepts or declines each application, with a reason the applicant reads.

## Carrying approved proposals into the tool

The repository's GitHub Action (`.github/workflows/wiki-sync.yml`) does this every half hour: it runs `pull.py` against the wiki, rebuilds the drafted entries, runs `check.py`, and only when the check passes commits the change and redeploys the tool and the wiki. It reads the wiki's address from the repository variable `WIKI_URL` and does nothing in a fork that has not set one. To do the same by hand, from the tool's folder:

```bash
python wiki/pull.py https://address-of-your-wiki
python drafted/build.py && python check.py
```

`pull.py` reads the wiki's export and applies every approved proposal it has not applied before: changes to pairs, triads, conflicts, theme lines, feeling and block descriptions and feeling-and-block judgements, and new triads and conflicts. It writes `interactions.json` in its existing layout, so a change shows as a small diff, and keeps the ids it has applied in `wiki-applied.json`. A drafted pair stays drafted when it is changed. A new block or feeling needs a drawing, a display name and pair entries, so the script lists it for doing by hand. Read the diff, then redeploy the tool and the wiki.

## Every record, for anyone

`/export.json` returns every record and every approved proposal, so the checking does not depend on one server. Withdrawn records are marked; hidden ones keep their reason and lose their text. Pending and rejected proposals are not in it.

## Privacy

Signing in keeps the name the account gives and, for GitHub, the username. Email addresses are not stored; a Google address is read once at sign-in to see whether the person is an editor. The session cookie lasts thirty days. There are no analytics or counters, and the server keeps no log of visits.

## Run it

You need Python 3.10 or newer. From this folder:

```bash
./start.sh
```

Then open http://127.0.0.1:8788. Reading works at once. For sign-in, register an OAuth app with GitHub (callback `<your address>/auth/github`) or an OAuth client with Google (redirect `<your address>/auth/google`), and put its keys in `.env` here:

```
SECRET_KEY=...            made for you by start.sh
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
OWNERS=github:yourlogin google:you@example.org
ADMINS=google:someone@example.org
```

A provider is offered only when its secret is set. `OWNERS` run the wiki: they are editors, and they manage editors and applications. `ADMINS` are editors to start with; each is added the first time they sign in, after which the Community page decides. Records and proposals are kept in `data/wiki.db` (`DB_PATH` to move it).

## Run it with Docker

The image needs the tool's corpus files beside the wiki's code, so build it from the tarball the script makes:

```bash
./make-caprover-tar.sh
mkdir build && tar -xf wiki.tar -C build && docker build -t boardgame-wiki build
docker run -p 8080:80 -v wiki-data:/app/data --env-file .env boardgame-wiki
```

`/app/data` must be a persistent volume, or the records go with the container. `wiki.tar` also deploys as it is to CapRover.

## Files

| File | What it is |
|---|---|
| `app.py` | The server: pages, sign-in, records, proposals, editors and applications, the export |
| `corpus.py` | Reads the tool's knowledge base into one list of entries, each with a stable key |
| `pull.py` | Carries approved proposals into the tool's files |
| `templates/`, `static/wiki.css` | The pages, in the tool's own look |
| `start.sh` | Runs it on this machine |
| `Dockerfile`, `make-caprover-tar.sh` | The container build |

## Licence

GNU Affero General Public License v3.0, as for the tool. See [../LICENSE](../LICENSE).

Made by Prayas Abhinav, https://prayasabhinav.net
