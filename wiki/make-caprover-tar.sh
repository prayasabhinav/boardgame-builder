#!/usr/bin/env bash
# Builds wiki.tar for CapRover: the wiki's code plus the corpus files it reads from the tool's folder.
set -euo pipefail
cd "$(dirname "$0")"
stage="$(mktemp -d)"
trap 'rm -rf "$stage"' EXIT
mkdir -p "$stage/wiki" "$stage/corpus/drafted"
cp app.py corpus.py requirements.txt "$stage/wiki/"
cp -r templates static "$stage/wiki/"
cp ../palette.py ../block_meta.py ../interactions.json ../interactions-drafted.json \
   ../mechanics-shortlist.md ../feeling-blocks.md "$stage/corpus/"
cp ../drafted/bgg-verdicts.json "$stage/corpus/drafted/"
cp Dockerfile "$stage/"
printf '{\n  "schemaVersion": 2,\n  "dockerfilePath": "./Dockerfile"\n}\n' > "$stage/captain-definition"
find "$stage" -name '._*' -delete
tar -C "$stage" -cf wiki.tar .
echo "wiki.tar: $(tar -tf wiki.tar | grep -vc '/$') files"
