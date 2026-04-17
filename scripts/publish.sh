#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MESSAGE="${1:-chore: update notebooklm-llm-wiki-flow}"
BRANCH="$(git branch --show-current)"

if [ -z "$BRANCH" ]; then
  echo "Not inside a git repository branch."
  exit 1
fi

if [ -n "$(git status --short)" ]; then
  git add .
  git commit -m "$MESSAGE"
else
  echo "No local changes to commit."
fi

git push -u origin "$BRANCH"
