from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .models import ComparisonDraft


@dataclass(slots=True)
class NotebookRunResult:
    notebook_id: str
    sources: list[dict[str, Any]] = field(default_factory=list)
    report_task: dict[str, Any] = field(default_factory=dict)
    mind_map: dict[str, Any] = field(default_factory=dict)
    qa: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ArtifactExportResult:
    artifacts_dir: Path
    report_path: Path
    mind_map_path: Path
    qa_path: Path
    raw_report_body: str


@dataclass(slots=True)
class EntityRender:
    slug: str
    title: str
    content: str
    summary: str


@dataclass(slots=True)
class WikiRenderResult:
    created: str
    raw_sources_rel: str
    raw_sources_content: str
    raw_report_rel: str
    raw_report_content: str
    comparison_slug: str
    comparison_title: str
    comparison_content: str
    checklist_slug: str
    checklist_title: str
    checklist_content: str
    entity_renders: list[EntityRender] = field(default_factory=list)
    draft: ComparisonDraft | None = None


@dataclass(slots=True)
class PersistResult:
    comparison_target: Path
    checklist_target: Path
    entity_targets: list[str]
    inbox_target: Path
    created_files: list[str]
    entity_entries: list[tuple[str, str]] = field(default_factory=list)


@dataclass(slots=True)
class IndexUpdateResult:
    updated_files: list[str] = field(default_factory=list)
