from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from .config import load_config
from .flow_models import (
    ArtifactExportResult,
    EntityRender,
    IndexUpdateResult,
    NotebookRunResult,
    PersistResult,
    WikiRenderResult,
)
from .index_builder import update_index_file
from .notebooklm_client import NotebookLMClient
from .policy_compare import (
    build_comparison_draft,
    render_anthropic_entity,
    render_checklist_note,
    render_inbox_summary,
    render_openai_entity,
    render_raw_source_pack,
)
from .runner import NotebookLMRunner, run_qmd_update
from .wiki_builder import render_comparison_note
from .workflows import build_policy_compare_plan, load_workflow_yaml, slugify


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _safe_filename(title: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|]", "-", title).strip()
    return cleaned or slugify(title)


def _render_generic_entity(title: str, slug: str, created: str, source_notes: list[str], source_urls: list[str], summary: str | None = None) -> str:
    lines = [
        "---",
        f"title: {title}",
        f"created: {created}",
        f"updated: {created}",
        "type: entity",
        "tags: [ai-ml, company, technology]",
        f"source_notes: [{', '.join(source_notes)}]",
        "source_urls:",
        *[f"  - {url}" for url in source_urls],
        "---",
        "",
        f"# {title}",
        "",
        "## Overview",
        summary or f"{title} 관련 workflow 실행 결과에서 추출한 기본 entity 초안이다.",
        "",
        "## Related",
        f"[[{slugify(title)}]], [[llm-wiki]]",
        "",
    ]
    return "\n".join(lines)


def _append_log(log_path: Path, title: str, notebook_id: str, created_files: list[str], updated_files: list[str] | None = None) -> None:
    lines = [
        f"## [{date.today().isoformat()}] ingest | {title}",
        "- NotebookLM notebook created and artifacts exported",
        f"- Notebook ID: {notebook_id}",
        "- Files created:",
        *[f"  - {item}" for item in created_files],
    ]
    if updated_files:
        lines.append("- Files updated:")
        lines.extend(f"  - {item}" for item in updated_files)
    entry = "\n".join(lines)
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    if entry not in text:
        log_path.write_text(text.rstrip() + "\n\n" + entry + "\n", encoding="utf-8")


def _run_notebook_phase(plan: dict[str, Any], client: NotebookLMClient) -> NotebookRunResult:
    notebook = client.create_notebook(plan["title"])
    notebook_id = notebook["id"]

    sources: list[dict[str, Any]] = []
    for source_url in plan["sources"]:
        source = client.add_source(notebook_id, source_url)
        client.wait_source(notebook_id, source["id"])
        sources.append(source)

    report_task = client.generate_report(notebook_id, plan["report_append"])
    client.wait_artifact(notebook_id, report_task["task_id"])
    mind_map = client.generate_mind_map(notebook_id)
    qa = client.ask(notebook_id, plan["question"])
    return NotebookRunResult(
        notebook_id=notebook_id,
        sources=sources,
        report_task=report_task,
        mind_map=mind_map,
        qa=qa,
    )


def _export_artifacts_phase(cfg, client: NotebookLMClient, notebook_run: NotebookRunResult) -> ArtifactExportResult:
    artifacts_dir = cfg.artifacts_root / notebook_run.notebook_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "report.md"
    mind_map_path = artifacts_dir / "mind-map.json"
    qa_path = artifacts_dir / "qa.json"
    client.download_report(notebook_run.notebook_id, report_path)
    client.download_mind_map(notebook_run.notebook_id, mind_map_path)
    qa_path.write_text(json.dumps(notebook_run.qa, ensure_ascii=False, indent=2), encoding="utf-8")
    return ArtifactExportResult(
        artifacts_dir=artifacts_dir,
        report_path=report_path,
        mind_map_path=mind_map_path,
        qa_path=qa_path,
        raw_report_body=report_path.read_text(encoding="utf-8"),
    )


def _render_wiki_phase(plan: dict[str, Any], notebook_run: NotebookRunResult, artifacts: ArtifactExportResult) -> WikiRenderResult:
    created = date.today().isoformat()
    workflow_slug = slugify(plan["wiki_outputs"].get("comparison_slug") or plan["title"])
    raw_sources_rel = f"raw/articles/{workflow_slug}-sources-{created}.md"
    raw_report_rel = f"raw/articles/notebooklm-{workflow_slug}-report-{created}.md"
    raw_sources_content = render_raw_source_pack(plan, created)

    raw_report_frontmatter = "\n".join([
        "---",
        f"title: NotebookLM report — {plan['title']}",
        f"created: {created}",
        f"updated: {created}",
        "type: source",
        "tags: [ai-ml, education, technology, research]",
        f"source_url: notebooklm://{notebook_run.notebook_id}/report/{notebook_run.report_task['task_id']}",
        "source_site: NotebookLM",
        f"source_date: {created}",
        "source_urls:",
        *[f"  - {url}" for url in plan["sources"]],
        "---",
        "",
    ])
    raw_report_content = raw_report_frontmatter + artifacts.raw_report_body

    comparison_slug = plan["wiki_outputs"]["comparison_slug"]
    comparison_title = plan["wiki_outputs"]["comparison_title"]
    checklist_slug = plan["wiki_outputs"]["checklist_slug"]
    checklist_title = plan["wiki_outputs"]["checklist_title"]

    draft = build_comparison_draft(artifacts.raw_report_body, notebook_run.qa["answer"], title=comparison_title)
    comparison_content = "\n".join([
        "---",
        f"title: {comparison_title}",
        f"created: {created}",
        f"updated: {created}",
        "type: comparison",
        "tags: [ai-ml, education, technology, comparison]",
        f"source_notes: [{raw_sources_rel}, {raw_report_rel}]",
        "source_urls:",
        *[f"  - {url}" for url in plan["sources"]],
        "---",
        "",
        render_comparison_note(draft),
    ])
    checklist_content = render_checklist_note(
        draft.checklist,
        [raw_sources_rel, raw_report_rel],
        plan["sources"],
        created,
        title=checklist_title,
    )

    entity_renders: list[EntityRender] = []
    for entity in plan.get("entities", []):
        slug = entity["slug"]
        title = entity["title"]
        summary = entity.get("summary") or f"{title} 관련 entity 초안"
        if slug == "openai":
            content = render_openai_entity(created, [raw_sources_rel, raw_report_rel], plan["sources"])
        elif slug == "anthropic":
            content = render_anthropic_entity(created, [raw_sources_rel, raw_report_rel], plan["sources"])
        else:
            content = _render_generic_entity(title, slug, created, [raw_sources_rel, raw_report_rel], plan["sources"], entity.get("summary"))
        entity_renders.append(EntityRender(slug=slug, title=title, content=content, summary=summary))

    return WikiRenderResult(
        created=created,
        raw_sources_rel=raw_sources_rel,
        raw_sources_content=raw_sources_content,
        raw_report_rel=raw_report_rel,
        raw_report_content=raw_report_content,
        comparison_slug=comparison_slug,
        comparison_title=comparison_title,
        comparison_content=comparison_content,
        checklist_slug=checklist_slug,
        checklist_title=checklist_title,
        checklist_content=checklist_content,
        entity_renders=entity_renders,
        draft=draft,
    )


def _persist_outputs_phase(
    cfg,
    plan: dict[str, Any],
    notebook_run: NotebookRunResult,
    artifacts: ArtifactExportResult,
    wiki_render: WikiRenderResult,
) -> PersistResult:
    _write(cfg.wiki_path / wiki_render.raw_sources_rel, wiki_render.raw_sources_content)
    _write(cfg.wiki_path / wiki_render.raw_report_rel, wiki_render.raw_report_content)
    comparison_target = _write(
        cfg.wiki_path / f"comparisons/{wiki_render.comparison_slug}.md",
        wiki_render.comparison_content,
    )
    checklist_target = _write(
        cfg.wiki_path / f"queries/{wiki_render.checklist_slug}.md",
        wiki_render.checklist_content,
    )

    created_files = [
        wiki_render.raw_sources_rel,
        wiki_render.raw_report_rel,
        f"comparisons/{wiki_render.comparison_slug}.md",
        f"queries/{wiki_render.checklist_slug}.md",
    ]
    entity_entries: list[tuple[str, str]] = []
    entity_targets: list[str] = []
    for entity in wiki_render.entity_renders:
        target = _write(cfg.wiki_path / f"entities/{entity.slug}.md", entity.content)
        entity_targets.append(str(target))
        entity_entries.append((entity.slug, entity.summary))
        created_files.append(f"entities/{entity.slug}.md")

    inbox_note_path = cfg.obsidian_vault / f"000-Inbox/{_safe_filename(plan['title'])}_{wiki_render.created}.md"
    inbox_target = _write(inbox_note_path, render_inbox_summary(plan, notebook_run.notebook_id, artifacts.artifacts_dir))

    return PersistResult(
        comparison_target=comparison_target,
        checklist_target=checklist_target,
        entity_targets=entity_targets,
        inbox_target=inbox_target,
        created_files=created_files,
        entity_entries=entity_entries,
    )


def _update_indexes_phase(
    cfg,
    plan: dict[str, Any],
    notebook_run: NotebookRunResult,
    wiki_render: WikiRenderResult,
    persist_result: PersistResult,
) -> IndexUpdateResult:
    update_index_file(
        cfg.wiki_path / "index.md",
        entity_entries=persist_result.entity_entries,
        comparison_entries=[
            (wiki_render.comparison_slug, f"{wiki_render.comparison_title} 결과를 정리한 비교 문서"),
        ],
        query_entries=[
            (wiki_render.checklist_slug, f"{wiki_render.checklist_title} 결과를 정리한 실행 체크리스트"),
        ],
        updated_on=wiki_render.created,
    )
    updated_files = ["index.md", "log.md"]
    _append_log(cfg.wiki_path / "log.md", plan["title"], notebook_run.notebook_id, persist_result.created_files, updated_files)
    return IndexUpdateResult(updated_files=updated_files)


def _run_plan(
    plan: dict[str, Any],
    config_path: str | None = None,
    *,
    dry_run: bool = False,
    qmd_update_enabled: bool = True,
    client: NotebookLMClient | None = None,
) -> dict[str, Any]:
    cfg = load_config(config_path) if config_path else load_config()
    if dry_run:
        return {"mode": "dry-run", "plan": plan}

    notebook_client = client if client is not None else NotebookLMRunner(cfg.notebooklm_command)
    notebook_run = _run_notebook_phase(plan, notebook_client)
    artifacts = _export_artifacts_phase(cfg, notebook_client, notebook_run)
    wiki_render = _render_wiki_phase(plan, notebook_run, artifacts)
    persist_result = _persist_outputs_phase(cfg, plan, notebook_run, artifacts, wiki_render)
    _update_indexes_phase(cfg, plan, notebook_run, wiki_render, persist_result)

    qmd_output = None
    if qmd_update_enabled:
        qmd_output = run_qmd_update(cfg.qmd_command)

    return {
        "mode": "run",
        "workflow": plan["workflow"],
        "notebook_id": notebook_run.notebook_id,
        "artifacts_dir": str(artifacts.artifacts_dir),
        "comparison_page": str(persist_result.comparison_target),
        "checklist_page": str(persist_result.checklist_target),
        "entity_pages": persist_result.entity_targets,
        "inbox_note": str(persist_result.inbox_target),
        "qmd_updated": bool(qmd_output is not None),
        "sources": [source["url"] for source in notebook_run.sources],
        "mind_map_note_id": notebook_run.mind_map.get("note_id"),
    }


def run_policy_compare(
    config_path: str | None = None,
    *,
    dry_run: bool = False,
    qmd_update_enabled: bool = True,
    client: NotebookLMClient | None = None,
) -> dict[str, Any]:
    plan = build_policy_compare_plan()
    return _run_plan(plan, config_path, dry_run=dry_run, qmd_update_enabled=qmd_update_enabled, client=client)


def run_from_yaml(
    workflow_path: str | Path,
    config_path: str | None = None,
    *,
    dry_run: bool = False,
    qmd_update_enabled: bool = True,
    client: NotebookLMClient | None = None,
) -> dict[str, Any]:
    plan = load_workflow_yaml(workflow_path)
    return _run_plan(plan, config_path, dry_run=dry_run, qmd_update_enabled=qmd_update_enabled, client=client)
