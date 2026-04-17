#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3.11}"
INSTALL_QMD_GLOBAL="${INSTALL_QMD_GLOBAL:-1}"
USE_PIPX="${USE_PIPX:-0}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "Python 3.11+ not found. Set PYTHON_BIN or install python3.11."
  exit 1
fi

if [ "$USE_PIPX" = "1" ] && ! command -v pipx >/dev/null 2>&1; then
  echo "USE_PIPX=1 was set but pipx is not installed."
  exit 1
fi

if [ "$INSTALL_QMD_GLOBAL" = "1" ] && ! command -v npm >/dev/null 2>&1; then
  echo "npm not found. Install Node.js 20+ first, or set INSTALL_QMD_GLOBAL=0."
  exit 1
fi

"$PYTHON_BIN" -m venv "$ROOT/.venv"
"$ROOT/.venv/bin/pip" install -U pip

if [ "$USE_PIPX" = "1" ]; then
  echo "Installing nlwflow (dev only) into .venv..."
  "$ROOT/.venv/bin/pip" install -e "$ROOT[dev]"

  echo "Installing notebooklm-py via pipx (isolated)..."
  pipx install notebooklm-py --python "$PYTHON_BIN" || pipx upgrade notebooklm-py
  pipx inject notebooklm-py playwright

  NOTEBOOKLM_VENV="$HOME/.local/pipx/venvs/notebooklm-py/bin/python"
  if [ ! -x "$NOTEBOOKLM_VENV" ]; then
    echo "NotebookLM pipx environment was not created as expected."
    exit 1
  fi
  echo "Installing Chromium for notebooklm-py Playwright..."
  "$NOTEBOOKLM_VENV" -m playwright install chromium
else
  echo "Installing nlwflow + notebooklm-py + Playwright into .venv..."
  "$ROOT/.venv/bin/pip" install -e "$ROOT[dev,notebooklm]"

  echo "Installing Chromium for Playwright..."
  "$ROOT/.venv/bin/python" -m playwright install chromium
fi

if [ "$INSTALL_QMD_GLOBAL" = "1" ]; then
  echo "Installing qmd globally via npm..."
  npm install -g @tobilu/qmd
else
  echo "Skipping optional global qmd install because INSTALL_QMD_GLOBAL=$INSTALL_QMD_GLOBAL"
fi

echo ""
echo "Bootstrap complete. Next steps:"
if [ "$USE_PIPX" = "1" ]; then
  echo "  1. notebooklm login"
else
  echo "  1. ./.venv/bin/notebooklm login"
  echo "     (or activate the venv: source ./.venv/bin/activate)"
fi
echo "  2. ./.venv/bin/nlwflow init-config"
echo "  3. ./.venv/bin/nlwflow doctor --json"
