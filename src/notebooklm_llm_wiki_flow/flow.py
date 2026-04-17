from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from .config import load_config
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


def _update_index(index_path: Path, comparison_slug: str, comparison_summary: str, checklist_slug: str, checklist_summary: str, entity_entries: list[tuple[str, str]] | None = None) -> None:
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    section_lines = {
        "## Comparisons\n": f"- [[{comparison_slug}]] — {comparison_summary}\n",
        "## Queries\n": f"- [[{checklist_slug}]] — {checklist_summary}\n",
    }
    if entity_entries:
        for slug, summary in entity_entries:
            line = f"- [[{slug}]] — {summary}\n"
            if line.strip() not in text and "## Entities\n" in text:
                text = text.replace("## Entities\n", "## Entities\n" + line, 1)
    for header, line in section_lines.items():
        if line.strip() not in text and header in text:
            text = text.replace(header, header + line, 1)
    text = re.sub(r"Last updated: \d{4}-\d{2}-\d{2} \| Total pages: \d+", f"Last updated: {date.today().isoformat()} | Total pages: 13", text)
    index_path.write_text(text, encoding="utf-8")


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
    notebook = notebook_client.create_notebook(plan["title"])
    notebook_id = notebook["id"]

    sources = []
    for source_url in plan["sources"]:
        source = notebook_client.add_source(notebook_id, source_url)
        notebook_client.wait_source(notebook_id, source["id"])
        sources.append(source)

    report_task = notebook_client.generate_report(notebook_id, plan["report_append"])
    notebook_client.wait_artifact(notebook_id, report_task["task_id"])
    mind_map = notebook_client.generate_mind_map(notebook_id)
    qa = notebook_client.ask(notebook_id, plan["question"])

    artifacts_dir = cfg.artifacts_root / notebook_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "report.md"
    mind_map_path = artifacts_dir / "mind-map.json"
    qa_path = artifacts_dir / "qa.json"
    notebook_client.download_report(notebook_id, report_path)
    notebook_client.download_mind_map(notebook_id, mind_map_path)
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")

    created = date.today().isoformat()
    workflow_slug = slugify(plan["wiki_outputs"].get("comparison_slug") or plan["title"])
    raw_sources_rel = f"raw/articles/{workflow_slug}-sources-{created}.md"
    raw_report_rel = f"raw/articles/notebooklm-{workflow_slug}-report-{created}.md"
    _write(cfg.wiki_path / raw_sources_rel, render_raw_source_pack(plan, created))

    raw_report_body = report_path.read_text(encoding="utf-8")
    raw_report_frontmatter = "\n".join([
        "---",
        f"title: NotebookLM report — {plan['title']}",
        f"created: {created}",
        f"updated: {created}",
        "type: source",
        "tags: [ai-ml, education, technology, research]",
        f"source_url: notebooklm://{notebook_id}/report/{report_task['task_id']}",
        "source_site: NotebookLM",
        f"source_date: {created}",
        "source_urls:",
        *[f"  - {url}" for url in plan["sources"]],
        "---",
        "",
    ])
    _write(cfg.wiki_path / raw_report_rel, raw_report_frontmatter + raw_report_body)

    comparison_slug = plan["wiki_outputs"]["comparison_slug"]
    comparison_title = plan["wiki_outputs"]["comparison_title"]
    checklist_slug = plan["wiki_outputs"]["checklist_slug"]
    checklist_title = plan["wiki_outputs"]["checklist_title"]

    draft = build_comparison_draft(raw_report_body, qa["answer"], title=comparison_title)
    comparison_note = "\n".join([
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
    comparison_target = _write(cfg.wiki_path / f"comparisons/{comparison_slug}.md", comparison_note)
    checklist_target = _write(
        cfg.wiki_path / f"queries/{checklist_slug}.md",
        render_checklist_note(draft.checklist, [raw_sources_rel, raw_report_rel], plan["sources"], created, title=checklist_title),
    )

    created_files = [
        raw_sources_rel,
        raw_report_rel,
        f"comparisons/{comparison_slug}.md",
        f"queries/{checklist_slug}.md",
    ]

    entity_entries: list[tuple[str, str]] = []
    entity_targets: list[str] = []
    for entity in plan.get("entities", []):
        slug = entity["slug"]
        title = entity["title"]
        summary = entity.get("summary")
        if slug == "openai":
            content = render_openai_entity(created, [raw_sources_rel, raw_report_rel], plan["sources"])
        elif slug == "anthropic":
            content = render_anthropic_entity(created, [raw_sources_rel, raw_report_rel], plan["sources"])
        else:
            content = _render_generic_entity(title, slug, created, [raw_sources_rel, raw_report_rel], plan["sources"], summary)
        target = _write(cfg.wiki_path / f"entities/{slug}.md", content)
        entity_targets.append(str(target))
        entity_entries.append((slug, summary or f"{title} 관련 entity 초안"))
        created_files.append(f"entities/{slug}.md")

    inbox_note_path = cfg.obsidian_vault / f"000-Inbox/{_safe_filename(plan['title'])}_{created}.md"
    inbox_target = _write(inbox_note_path, render_inbox_summary(plan, notebook_id, artifacts_dir))

    _update_index(
        cfg.wiki_path / "index.md",
        comparison_slug,
        f"{comparison_title} 결과를 정리한 비교 문서",
        checklist_slug,
        f"{checklist_title} 결과를 정리한 실행 체크리스트",
        entity_entries or None,
    )
    _append_log(cfg.wiki_path / "log.md", plan["title"], notebook_id, created_files, ["index.md", "log.md"])

    qmd_output = None
    if qmd_update_enabled:
        qmd_output = run_qmd_update(cfg.qmd_command)

    return {
        "mode": "run",
        "workflow": plan["workflow"],
        "notebook_id": notebook_id,
        "artifacts_dir": str(artifacts_dir),
        "comparison_page": str(comparison_target),
        "checklist_page": str(checklist_target),
        "entity_pages": entity_targets,
        "inbox_note": str(inbox_target),
        "qmd_updated": bool(qmd_output is not None),
        "sources": [source["url"] for source in sources],
        "mind_map_note_id": mind_map.get("note_id"),
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
