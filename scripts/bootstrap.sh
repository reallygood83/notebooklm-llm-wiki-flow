#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN="${PYTHON_BIN:-python3.13}"
INSTALL_QMD_GLOBAL="${INSTALL_QMD_GLOBAL:-1}"

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

echo "Installing notebooklm-py via pipx..."
pipx install notebooklm-py --python "$PYTHON_BIN"

echo "Injecting Playwright into notebooklm-py environment..."
pipx inject notebooklm-py playwright

NOTEBOOKLM_VENV="$HOME/.local/pipx/venvs/notebooklm-py/bin/python"
if [ ! -x "$NOTEBOOKLM_VENV" ]; then
  echo "NotebookLM pipx environment was not created as expected."
  exit 1
fi

echo "Installing Chromium for notebooklm-py Playwright..."
"$NOTEBOOKLM_VENV" -m playwright install chromium

if [ "$INSTALL_QMD_GLOBAL" = "1" ]; then
  echo "Installing qmd globally via npm..."
  npm install -g @tobilu/qmd
else
  echo "Skipping optional global qmd install because INSTALL_QMD_GLOBAL=$INSTALL_QMD_GLOBAL"
fi

echo "Bootstrap complete. Next steps:"
echo "  1. notebooklm login"
echo "  2. nlwflow init-config"
echo "  3. nlwflow doctor --json"
