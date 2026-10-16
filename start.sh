#!/usr/bin/env bash
# One-command startup for boardgameBuilder.
# Cross-platform: works on macOS and Linux.
#
# Usage:
#   ./start.sh
#
# Then open http://127.0.0.1:8787 in a browser.

set -euo pipefail
cd "$(dirname "$0")"

# ── Per-OS venv (avoids breakage when Dropbox syncs across Mac↔Linux) ──
OS_TAG="$(uname -s | tr '[:upper:]' '[:lower:]')"
VENV_DIR=".venv-${OS_TAG}"

# Sanity-check the existing venv. If it's a dead venv synced from another
# machine (or another OS), python in it will fail — rebuild from scratch.
need_venv=true
if [[ -d "$VENV_DIR" ]] && "$VENV_DIR/bin/python" --version >/dev/null 2>&1; then
  need_venv=false
fi

if [[ "$need_venv" == "true" ]]; then
  if [[ -d "$VENV_DIR" ]]; then
    echo "Existing $VENV_DIR is unusable on this machine — rebuilding."
    rm -rf "$VENV_DIR"
  fi
  echo "Creating virtualenv ($VENV_DIR)..."
  if command -v python3 >/dev/null 2>&1; then
    python3 -m venv "$VENV_DIR"
  elif command -v python >/dev/null 2>&1; then
    python -m venv "$VENV_DIR"
  else
    echo "ERROR: neither python3 nor python is on PATH. Install Python 3.10+." >&2
    exit 1
  fi
fi

# shellcheck disable=SC1091
source "$VENV_DIR/bin/activate"

# python -m pip, not pip: pip's own script hard-codes the folder path and breaks if the folder is moved or renamed
"$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
"$VENV_DIR/bin/python" -m pip install --quiet -r requirements.txt

# Load .env if present
if [[ -f .env ]]; then
  echo "Loading environment from .env"
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

PORT="${PORT:-8787}"

echo ""
echo "╭──────────────────────────────────────────────────────╮"
echo "│ boardgameBuilder running at:                         │"
printf "│   http://127.0.0.1:%-32s│\n" "${PORT}"
echo "│                                                      │"
echo "│ Ctrl-C to stop.                                      │"
echo "╰──────────────────────────────────────────────────────╯"
echo ""

# Use the venv's python explicitly — survives unusual PATH/activate states
"$VENV_DIR/bin/python" app.py
