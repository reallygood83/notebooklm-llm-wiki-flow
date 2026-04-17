from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from dotenv import dotenv_values

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

ENV_KEY_MAP = {
    "project_name": "NLWFLOW_PROJECT_NAME",
    "obsidian_vault": "NLWFLOW_OBSIDIAN_VAULT",
    "wiki_path": "NLWFLOW_WIKI_PATH",
    "qmd_collection": "NLWFLOW_QMD_COLLECTION",
    "artifacts_root": "NLWFLOW_ARTIFACTS_ROOT",
    "notebooklm_command": "NLWFLOW_NOTEBOOKLM_COMMAND",
    "qmd_command": "NLWFLOW_QMD_COMMAND",
}


def _expand(value: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(value))).resolve()


def _dotenv_overrides(dotenv_path: Path | None) -> dict[str, str]:
    if dotenv_path is None or not dotenv_path.exists():
        return {}
    loaded = dotenv_values(dotenv_path)
    overrides: dict[str, str] = {}
    for key, env_name in ENV_KEY_MAP.items():
        value = loaded.get(env_name)
        if value is not None:
            overrides[key] = value
    return overrides


def _environment_overrides() -> dict[str, str]:
    overrides: dict[str, str] = {}
    for key, env_name in ENV_KEY_MAP.items():
        value = os.getenv(env_name)
        if value:
            overrides[key] = value
    return overrides


def load_config(path: str | Path | None = None) -> WorkflowConfig:
    raw: dict[str, Any] = dict(DEFAULT_CONFIG)
    config_path = Path(path).expanduser().resolve() if path else None

    raw.update(_dotenv_overrides(Path.cwd() / ".env"))
    if config_path is not None:
        raw.update(_dotenv_overrides(config_path.parent / ".env"))
        with config_path.open("r", encoding="utf-8") as handle:
            loaded = yaml.safe_load(handle) or {}
        raw.update(loaded)

    raw.update(_environment_overrides())
    return WorkflowConfig(
        project_name=str(raw["project_name"]),
        obsidian_vault=_expand(str(raw["obsidian_vault"])),
        wiki_path=_expand(str(raw["wiki_path"])),
        qmd_collection=str(raw["qmd_collection"]),
        artifacts_root=_expand(str(raw["artifacts_root"])),
        notebooklm_command=str(raw.get("notebooklm_command", "notebooklm")),
        qmd_command=str(raw.get("qmd_command", "qmd")),
    )
