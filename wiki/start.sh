#!/usr/bin/env bash
# Runs the wiki on this machine at http://127.0.0.1:8788. Sign-in works only once a provider's
# keys are in wiki/.env (see README.md); reading every entry works without them.
set -euo pipefail
cd "$(dirname "$0")"
venv=".venv-$(uname -s | tr '[:upper:]' '[:lower:]')"
[ -d "$venv" ] || { python3 -m venv "$venv" && "$venv/bin/pip" install -q -r requirements.txt; }
[ -f .env ] || printf 'SECRET_KEY=%s\n' "$(python3 -c 'import secrets; print(secrets.token_hex(32))')" > .env
set -a; . ./.env; set +a
exec "$venv/bin/python" app.py
