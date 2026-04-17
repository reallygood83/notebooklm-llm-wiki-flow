from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class ExtractedTopic:
    path: list[str]
    depth: int
    importance: str


@dataclass(slots=True)
class ReportSection:
    title: str
    body: str
    score: int


@dataclass(slots=True)
class ReportHighlights:
    title: str
    sections: list[ReportSection] = field(default_factory=list)
    bullets: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ComparisonDraft:
    title: str
    summary: str
    key_differences: list[tuple[str, str, str, str]]
    checklist: list[str]
    related_links: list[str]


@dataclass(slots=True)
class WorkflowConfig:
    project_name: str
    obsidian_vault: Path
    wiki_path: Path
    qmd_collection: str
    artifacts_root: Path
    notebooklm_command: str = "notebooklm"
    qmd_command: str = "qmd"
