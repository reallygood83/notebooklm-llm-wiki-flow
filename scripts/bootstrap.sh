#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3.13}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3.13+ not found. Set PYTHON_BIN or install python3.13."
  exit 1
fi

if ! command -v pipx >/dev/null 2>&1; then
  echo "pipx not found. Install pipx first."
  exit 1
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js 20+ first."
  exit 1
fi

"$PYTHON_BIN" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -U pip
"$ROOT/.venv/bin/pip" install -e "$ROOT[dev]"

pipx install notebooklm-py --python "$PYTHON_BIN" || true
pipx inject notebooklm-py playwright || true
NOTEBOOKLM_VENV="$HOME/.local/pipx/venvs/notebooklm-py/bin/python"
if [ -x "$NOTEBOOKLM_VENV" ]; then
  "$NOTEBOOKLM_VENV" -m playwright install chromium || true
fi

npm install -g @tobilu/qmd || true

echo "Bootstrap complete. Next steps:"
echo "  1. notebooklm login"
echo "  2. nlwflow init-config"
echo "  3. nlwflow doctor --json"
