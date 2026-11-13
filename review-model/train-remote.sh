#!/usr/bin/env bash
# Trains khatka (review-model/rules.py) and checks it (review-model/cv.py) on gpubox, where training runs (his words,
# 13 November 2026: "do building and training on gpubox"). Sends the project to gpubox:~/work/boardgame-builder, runs
# detached in tmux (boardgame-khatka) with its log in that folder, waits, and brings back review.json and the log.
# Usage: bash review-model/train-remote.sh            train and check, bring back review.json
#        bash review-model/train-remote.sh <script>   run another script there (such as review-model/label-eval.py), bring back its log only
set -euo pipefail
HERE="$(cd "$(dirname "$0")/.." && pwd)"
REMOTE=work/boardgame-builder
JOB="${1:-}"
RUN="${JOB:+python3 $JOB}"; RUN="${RUN:-python3 review-model/rules.py && python3 review-model/cv.py}"
ssh gpubox "tmux has-session -t boardgame-khatka 2>/dev/null" && { echo "a khatka run is already going on gpubox"; exit 1; }
rsync -a --delete --exclude '.venv*' --exclude '.git' --exclude 'node_modules' --exclude 'wiki/data' "$HERE/" "gpubox:$REMOTE/"
ssh gpubox "rm -f ~/$REMOTE/train.done; tmux new-session -d -s boardgame-khatka 'cd ~/$REMOTE && { $RUN; } > train.log 2>&1; echo \$? > train.done'"
echo "$(date '+%e %B %Y, %H:%M')  training on gpubox; log: ssh gpubox cat ~/$REMOTE/train.log"
until ssh gpubox "test -f ~/$REMOTE/train.done" 2>/dev/null; do sleep 5; done
rsync -a "gpubox:$REMOTE/review.json" "gpubox:$REMOTE/train.log" "$HERE/review-model/remote/"
code=$(ssh gpubox "cat ~/$REMOTE/train.done")
cat "$HERE/review-model/remote/train.log"
[ -n "$JOB" ] && exit "$code"
[ "$code" = 0 ] || { echo "the run failed on gpubox (exit $code); review.json here is unchanged"; exit 1; }
cp "$HERE/review-model/remote/review.json" "$HERE/review.json"
echo "review.json brought back from gpubox"
