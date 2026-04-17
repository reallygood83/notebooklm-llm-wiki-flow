from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

from .config import load_config
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
from .workflows import build_policy_compare_plan


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _update_index(index_path: Path) -> None:
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    sections = {
        "## Entities\n": "- [[openai]] — Enterprise, Edu, API를 통해 데이터 보호·관리 통제를 상품화하는 AI 회사\n",
        "## Comparisons\n": "- [[anthropic-vs-openai-education-vertical-ai-policy]] — Anthropic와 OpenAI의 business policy를 비교하고 교육 vertical AI 정책 시사점을 정리한 비교 문서\n",
        "## Queries\n": "- [[education-vertical-ai-policy-checklist]] — 학교·교사·학생·보호자 대상 교육 AI 기업 정책 체크리스트\n",
    }
    for header, line in sections.items():
        if line.strip() not in text and header in text:
            text = text.replace(header, header + line, 1)
    text = text.replace(
        "Last updated: 2026-04-16 | Total pages: 10",
        f"Last updated: {date.today().isoformat()} | Total pages: 13",
    )
    index_path.write_text(text, encoding="utf-8")


def _append_log(log_path: Path, notebook_id: str) -> None:
    entry = "\n".join([
        f"## [{date.today().isoformat()}] ingest | Anthropic vs OpenAI business policy comparison for education vertical AI",
        "- NotebookLM notebook created and artifacts exported",
        f"- Notebook ID: {notebook_id}",
        "- Files created/updated:",
        f"  - raw/articles/anthropic-openai-policy-sources-{date.today().isoformat()}.md",
        f"  - raw/articles/notebooklm-anthropic-openai-policy-report-{date.today().isoformat()}.md",
        "  - entities/openai.md",
        "  - comparisons/anthropic-vs-openai-education-vertical-ai-policy.md",
        "  - queries/education-vertical-ai-policy-checklist.md",
        "  - entities/anthropic.md",
        "  - index.md",
        "  - log.md",
    ])
    text = log_path.read_text(encoding="utf-8") if log_path.exists() else ""
    if entry not in text:
        updated = text.rstrip() + "\n\n" + entry + "\n"
        log_path.write_text(updated, encoding="utf-8")


def run_policy_compare(config_path: str | None = None, *, dry_run: bool = False, qmd_update_enabled: bool = True) -> dict[str, Any]:
    cfg = load_config(config_path) if config_path else load_config()
    plan = build_policy_compare_plan()
    if dry_run:
        return {"mode": "dry-run", "plan": plan}

    runner = NotebookLMRunner(cfg.notebooklm_command)
    notebook = runner.create_notebook(plan["title"])
    notebook_id = notebook["id"]

    sources = []
    for source_url in plan["sources"]:
        source = runner.add_source(notebook_id, source_url)
        runner.wait_source(notebook_id, source["id"])
        sources.append(source)

    report_task = runner.generate_report(notebook_id, plan["report_append"])
    runner.wait_artifact(notebook_id, report_task["task_id"])
    mind_map = runner.generate_mind_map(notebook_id)
    qa = runner.ask(
        notebook_id,
        "Compare Anthropic and OpenAI business policies across data ownership, data retention, model training, acceptable use, enterprise controls, compliance, and IP/legal risk allocation. Then extract a policy checklist for an education vertical AI company serving schools, teachers, students, and guardians.",
    )

    artifacts_dir = cfg.artifacts_root / notebook_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifacts_dir / "report.md"
    mind_map_path = artifacts_dir / "mind-map.json"
    qa_path = artifacts_dir / "qa.json"
    runner.download_report(notebook_id, report_path)
    runner.download_mind_map(notebook_id, mind_map_path)
    qa_path.write_text(json.dumps(qa, ensure_ascii=False, indent=2), encoding="utf-8")

    created = date.today().isoformat()
    raw_sources_rel = f"raw/articles/anthropic-openai-policy-sources-{created}.md"
    raw_report_rel = f"raw/articles/notebooklm-anthropic-openai-policy-report-{created}.md"
    _write(cfg.wiki_path / raw_sources_rel, render_raw_source_pack(plan, created))
    raw_report_target = cfg.wiki_path / raw_report_rel
    raw_report_body = report_path.read_text(encoding="utf-8")
    raw_report_frontmatter = "\n".join([
        "---",
        "title: NotebookLM report — Anthropic and OpenAI business policy comparison",
        f"created: {created}",
        f"updated: {created}",
        "type: source",
        "tags: [ai-ml, education, technology, research]",
        f"source_url: notebooklm://{notebook_id}/report/{report_task['task_id']}",
        "source_site: NotebookLM",
        f"source_date: {created}",
        "---",
        "",
    ])
    raw_report_target.write_text(raw_report_frontmatter + raw_report_body, encoding="utf-8")

    draft = build_comparison_draft(raw_report_body, qa["answer"])
    comparison_note = "\n".join([
        "---",
        "title: Anthropic vs OpenAI policy comparison for education vertical AI",
        f"created: {created}",
        f"updated: {created}",
        "type: comparison",
        "tags: [ai-ml, education, technology, comparison]",
        f"sources: [{raw_sources_rel}, {raw_report_rel}]",
        "---",
        "",
        render_comparison_note(draft),
    ])
    comparison_target = _write(cfg.wiki_path / "comparisons/anthropic-vs-openai-education-vertical-ai-policy.md", comparison_note)
    checklist_target = _write(cfg.wiki_path / "queries/education-vertical-ai-policy-checklist.md", render_checklist_note(draft.checklist, [raw_sources_rel, raw_report_rel], created))
    openai_target = _write(cfg.wiki_path / "entities/openai.md", render_openai_entity(created, [raw_sources_rel, raw_report_rel]))
    anthropic_target = _write(cfg.wiki_path / "entities/anthropic.md", render_anthropic_entity(created, [raw_sources_rel, raw_report_rel]))
    inbox_target = _write(cfg.obsidian_vault / f"000-Inbox/Anthropic-vs-OpenAI-정책비교_교육-Vertical-AI_{created}.md", render_inbox_summary(plan, notebook_id, artifacts_dir))

    _update_index(cfg.wiki_path / "index.md")
    _append_log(cfg.wiki_path / "log.md", notebook_id)

    qmd_output = None
    if qmd_update_enabled:
        qmd_output = run_qmd_update(cfg.qmd_command)

    return {
        "mode": "run",
        "notebook_id": notebook_id,
        "artifacts_dir": str(artifacts_dir),
        "comparison_page": str(comparison_target),
        "checklist_page": str(checklist_target),
        "openai_page": str(openai_target),
        "anthropic_page": str(anthropic_target),
        "inbox_note": str(inbox_target),
        "qmd_updated": bool(qmd_output is not None),
        "sources": [source["url"] for source in sources],
        "mind_map_note_id": mind_map.get("note_id"),
    }
