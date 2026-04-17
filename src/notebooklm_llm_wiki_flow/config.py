from __future__ import annotations

from pathlib import Path
import os
import yaml

from .models import WorkflowConfig


DEFAULT_CONFIG = {
    "project_name": "notebooklm-llm-wiki-flow",
    "obsidian_vault": "~/Documents/LearningMaster",
    "wiki_path": "~/Documents/LearningMaster/LLM-Wiki",
    "qmd_collection": "learningmaster",
    "artifacts_root": "./artifacts",
    "notebooklm_command": "notebooklm",
    "qmd_command": "qmd",
}


def _expand(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def load_config(path: str | Path | None = None) -> WorkflowConfig:
    raw = dict(DEFAULT_CONFIG)
    if path:
        with Path(path).expanduser().open('r', encoding='utf-8') as handle:
            loaded = yaml.safe_load(handle) or {}
        raw.update(loaded)
    return WorkflowConfig(
        project_name=raw["project_name"],
        obsidian_vault=_expand(raw["obsidian_vault"]),
        wiki_path=_expand(raw["wiki_path"]),
        qmd_collection=raw["qmd_collection"],
        artifacts_root=_expand(raw["artifacts_root"]),
        notebooklm_command=raw.get("notebooklm_command", "notebooklm"),
        qmd_command=raw.get("qmd_command", "qmd"),
    )
