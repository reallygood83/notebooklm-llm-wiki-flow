from __future__ import annotations

from datetime import date
from pathlib import Path


def build_log_entry(
    title: str,
    notebook_id: str,
    created_files: list[str],
    updated_files: list[str] | None = None,
    today: str | None = None,
) -> str:
    today = today or date.today().isoformat()
    lines = [
        f"## [{today}] ingest | {title}",
        "- NotebookLM notebook created and artifacts exported",
        f"- Notebook ID: {notebook_id}",
        "- Files created:",
        *[f"  - {item}" for item in created_files],
    ]
    if updated_files:
        lines.append("- Files updated:")
        lines.extend(f"  - {item}" for item in updated_files)
    return "\n".join(lines)


def append_log_entry(
    log_path: Path,
    title: str,
    notebook_id: str,
    created_files: list[str],
    updated_files: list[str] | None = None,
) -> None:
    entry = build_log_entry(title, notebook_id, created_files, updated_files)
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    if entry in text:
        return
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(text.rstrip() + "\n\n" + entry + "\n", encoding="utf-8")
