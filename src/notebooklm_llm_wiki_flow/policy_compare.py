from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .models import ComparisonDraft, ReportHighlights
from .report_parser import extract_report_highlights
from .template_renderer import render_entity_template

logger = logging.getLogger(__name__)


def extract_core_policy_table_rows(report_markdown: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in report_markdown.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if ":---" in stripped or "------" in stripped:
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 3:
            continue
        if cells[0].lower() == "feature":
            continue
        feature = re.sub(r"^\*\*|\*\*$", "", cells[0]).strip()
        openai = re.sub(r"^\*\*|\*\*$", "", cells[1]).strip()
        anthropic = re.sub(r"^\*\*|\*\*$", "", cells[2]).strip()
        rows.append((feature, openai, anthropic))
    return rows


def _clean_list_item(text: str) -> str:
    text = re.sub(r"^\*\*\d+[.)]?\s*", "", text).strip()
    text = re.sub(r"^\d+[.)]\s*", "", text).strip()
    text = text.replace("**", "")
    text = re.sub(r"\[[^\]]+\]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text.strip(" :-")


def extract_checklist_items(qa_answer: str, report_markdown: str, max_items: int = 8) -> list[str]:
    items: list[str] = []
    for line in qa_answer.splitlines():
        stripped = line.strip()
        if stripped.startswith("*") and "[ ]" in stripped:
            item = _clean_list_item(stripped.split("[ ]", 1)[1])
            if item and item not in items:
                items.append(item)
    if items:
        return items[:max_items]

    collecting = False
    for line in report_markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("##") and (
            "Policy Recommendations" in stripped or "Considerations for Education" in stripped
        ):
            collecting = True
            continue
        if collecting and stripped.startswith("##"):
            break
        if collecting and (re.match(r"^\d+\.", stripped) or stripped.startswith("*")):
            item = _clean_list_item(stripped.lstrip("*").strip())
            if item and item not in items:
                items.append(item)
    return items[:max_items]


def _fallback_key_differences(highlights: ReportHighlights) -> list[tuple[str, str, str, str]]:
    key_differences: list[tuple[str, str, str, str]] = []
    for bullet in highlights.bullets:
        cleaned = bullet.strip().lstrip("-* ")
        if ":" not in cleaned:
            continue
        label, detail = cleaned.split(":", 1)
        owner = label.strip()
        description = detail.strip()
        if not description:
            continue
        implication = "표 형식 비교가 없어 bullet 기반 fallback 요약을 사용"
        if "openai" in owner.lower():
            key_differences.append(("fallback", "", f"OpenAI: {description}", implication))
        elif "anthropic" in owner.lower():
            key_differences.append(("fallback", f"Anthropic: {description}", "", implication))
        if len(key_differences) >= 6:
            break
    return key_differences


def build_comparison_draft(report_markdown: str, qa_answer: str, title: str = "Anthropic vs OpenAI policy comparison for education vertical AI") -> ComparisonDraft:
    rows = extract_core_policy_table_rows(report_markdown)
    highlights = extract_report_highlights(report_markdown)
    checklist = extract_checklist_items(qa_answer, report_markdown)

    key_differences: list[tuple[str, str, str, str]] = []
    for feature, openai, anthropic in rows[:6]:
        implication = "교육 AI 정책 문서와 제품 제어 항목에 즉시 반영"
        key_differences.append((feature, anthropic, openai, implication))

    if not key_differences:
        logger.warning("Falling back to bullet-based comparison draft because no policy comparison table rows were parsed.")
        key_differences = _fallback_key_differences(highlights)

    summary_lines = [
        "NotebookLM report와 Q&A를 바탕으로 생성한 정책 비교 초안이다.",
        "주요 포인트는 데이터 소유권, 학습 기본값, 보존기간, 안전정책, 고위험 의사결정, 엔터프라이즈 통제다.",
    ]
    if highlights.bullets:
        summary_lines.append("핵심 하이라이트: " + "; ".join(highlights.bullets[:3]))

    return ComparisonDraft(
        title=title,
        summary=" ".join(summary_lines),
        key_differences=key_differences,
        checklist=checklist,
        related_links=["anthropic", "openai", "llm-wiki"],
    )


def build_generic_comparison_draft(report_markdown: str, qa_answer: str, *, title: str) -> ComparisonDraft:
    """Topic-agnostic comparison draft for `note-wiki` / `yaml` workflows."""
    highlights = extract_report_highlights(report_markdown)
    checklist = extract_checklist_items(qa_answer, report_markdown)

    key_differences: list[tuple[str, str, str, str]] = []
    for section in highlights.sections[:6]:
        head_line = section.body.splitlines()[0] if section.body else ""
        key_differences.append((section.title, head_line.strip(), "", "NotebookLM report에서 추출한 섹션 요지"))

    summary_lines = [f"NotebookLM report와 Q&A를 바탕으로 생성한 '{title}' 요약 초안이다."]
    if highlights.bullets:
        summary_lines.append("핵심 하이라이트: " + "; ".join(highlights.bullets[:3]))

    return ComparisonDraft(
        title=title,
        summary=" ".join(summary_lines),
        key_differences=key_differences,
        checklist=checklist,
        related_links=["llm-wiki"],
    )


def _yaml_list_lines(key: str, values: list[str]) -> list[str]:
    if not values:
        return []
    lines = [f"{key}:"]
    lines.extend(f"  - {value}" for value in values)
    return lines


def render_checklist_note(
    checklist: Iterable[str],
    sources: list[str],
    source_urls: list[str],
    created: str,
    title: str = "Education vertical AI policy checklist",
    *,
    tags: list[str] | None = None,
    related_links: list[str] | None = None,
) -> str:
    body = [
        "---",
        f"title: {title}",
        f"created: {created}",
        f"updated: {created}",
        "type: query",
        f"tags: [{', '.join(tags or ['ai-ml', 'education', 'technology', 'question'])}]",
        f"source_notes: [{', '.join(sources)}]",
    ]
    body.extend(_yaml_list_lines("source_urls", source_urls))
    body.extend([
        "---",
        "",
        f"# {title}",
        "",
        "## Checklist",
    ])
    body.extend(f"- [ ] {item}" for item in checklist)
    related = related_links if related_links is not None else ["anthropic", "openai", "llm-wiki"]
    body.extend([
        "",
        "## Related",
        ", ".join(f"[[{slug}]]" for slug in related),
        "",
    ])
    return "\n".join(body)


def render_openai_entity(created: str, sources: list[str], source_urls: list[str]) -> str:
    return render_entity_template(
        title="OpenAI",
        created=created,
        updated=created,
        source_notes=sources,
        source_urls=source_urls,
        overview="OpenAI는 ChatGPT Business, Enterprise, Edu, Healthcare, Teachers, 그리고 API 플랫폼을 통해 기업용 AI 서비스를 제공하는 회사다.",
        policy_posture=[
            "business data는 기본적으로 모델 학습에 사용하지 않음",
            "입력과 출력에 대한 고객 권리 보장",
            "enterprise retention control과 admin controls 제공",
            "compliance, trust portal, encryption, residency 옵션을 강하게 상품화",
        ],
        related_links=["[[anthropic]]", "[[llm-wiki]]", "[[rag]]"],
    )


def render_anthropic_entity(created: str, sources: list[str], source_urls: list[str]) -> str:
    return render_entity_template(
        title="Anthropic",
        created=created,
        updated=created,
        source_notes=sources,
        source_urls=source_urls,
        overview="Anthropic는 Claude 계열 모델과 Claude Platform을 만드는 AI 회사다. 최근에는 정책·거버넌스·고위험 사용사례 통제를 더 강하게 구조화하고 있다.",
        policy_posture=[
            "commercial customer content를 모델 학습에 사용하지 않음",
            "표준 API 데이터는 30일 내 삭제 가능 구조",
            "policy violation 데이터는 장기 보존될 수 있음",
            "고위험 사용 사례에서 human review와 disclosure를 중시",
        ],
        related_links=["[[managed-agents]]", "[[openai]]", "[[llm-wiki]]"],
    )


def render_inbox_summary(plan: dict[str, Any], notebook_id: str, artifacts_dir: Path, share_link: str | None = None) -> str:
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    lines = [
        "---",
        "title: Anthropic vs OpenAI 정책 비교 - 교육 Vertical AI",
        "tags:",
        "  - anthropic",
        "  - openai",
        "  - education",
        "  - vertical-ai",
        "  - policy",
        "  - notebooklm",
        "  - llm-wiki",
        f"date: {datetime.now().date().isoformat()}",
        f"created: {created}",
        f"updated: {created}",
        "type: research-note",
        "status: draft",
        "source:",
    ]
    for source in plan["sources"]:
        lines.append(f"  - {source}")
    lines.extend([
        f"notebook_id: {notebook_id}",
        f"notebook_title: {plan['title']}",
        f"artifacts_dir: {artifacts_dir}",
        "qmd_collection: learningmaster",
    ])
    if share_link:
        lines.append(f"share_link: {share_link}")
    lines.extend([
        "---",
        "",
        "# Anthropic vs OpenAI 정책 비교",
        "",
        "> [!success]",
        "> NotebookLM-LLM-Wiki flow로 정책 문서를 수집하고, report / mind map / Q&A를 생성해 wiki와 Obsidian에 반영했다.",
        "",
        "## 생성된 wiki 페이지",
        "- [[anthropic-vs-openai-education-vertical-ai-policy]]",
        "- [[education-vertical-ai-policy-checklist]]",
        "- [[anthropic]]",
        "- [[openai]]",
        "",
        "## 주요 시사점",
        "- Anthropic는 위험 통제, human review, disclosure를 강하게 전면화한다.",
        "- OpenAI는 enterprise privacy, retention control, admin tooling을 더 강하게 상품화한다.",
        "- 교육 vertical AI 기업은 학생 데이터 보호, minors safety, academic integrity, 관리자 통제를 정책의 핵심 축으로 가져가야 한다.",
        "",
    ])
    return "\n".join(lines)


def render_generic_inbox_summary(
    plan: dict[str, Any],
    notebook_id: str,
    artifacts_dir: Path,
    *,
    qmd_collection: str,
    wiki_links: list[str],
    share_link: str | None = None,
) -> str:
    """Topic-agnostic Obsidian inbox note for `note-wiki` / `yaml` workflows."""
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    title = plan["title"]
    lines = [
        "---",
        f"title: {title}",
        "tags:",
        "  - notebooklm",
        "  - llm-wiki",
        "  - research-note",
        f"date: {datetime.now().date().isoformat()}",
        f"created: {created}",
        f"updated: {created}",
        "type: research-note",
        "status: draft",
        "source:",
    ]
    for source in plan["sources"]:
        lines.append(f"  - {source}")
    lines.extend([
        f"notebook_id: {notebook_id}",
        f"notebook_title: {title}",
        f"artifacts_dir: {artifacts_dir}",
        f"qmd_collection: {qmd_collection}",
    ])
    if share_link:
        lines.append(f"share_link: {share_link}")
    lines.extend([
        "---",
        "",
        f"# {title}",
        "",
        "> [!success]",
        "> NotebookLM-LLM-Wiki flow로 소스를 수집하고 report / mind map / Q&A를 생성해 wiki와 Obsidian에 반영했다.",
        "",
        "## 생성된 wiki 페이지",
    ])
    lines.extend(f"- [[{slug}]]" for slug in wiki_links)
    lines.extend([
        "",
        "## 소스 URL",
    ])
    lines.extend(f"- {source}" for source in plan["sources"])
    lines.extend([
        "",
        f"## Report 원문 (전체)",
        f"- `{artifacts_dir}/report.md`",
        "",
    ])
    return "\n".join(lines)


def render_raw_source_pack(plan: dict[str, Any], created: str) -> str:
    lines = [
        "---",
        "title: Anthropic and OpenAI business policy source pack",
        f"created: {created}",
        f"updated: {created}",
        "type: source",
        "tags: [ai-ml, education, technology, research]",
        f"source_url: {plan['sources'][0]}",
        "source_site: Anthropic + OpenAI official policy pages",
        f"source_date: {created}",
    ]
    lines.extend(_yaml_list_lines("source_urls", plan["sources"]))
    lines.extend([
        "---",
        "",
        "# Anthropic and OpenAI business policy source pack",
        "",
        "## URLs",
    ])
    lines.extend(f"- {source}" for source in plan["sources"])
    lines.extend([
        "",
        "## Why these sources matter",
        "- data ownership and training defaults",
        "- retention and deletion windows",
        "- minors and student safety",
        "- human review for high-stakes decisions",
        "- enterprise controls and compliance posture",
        "- indemnity and legal risk allocation",
        "",
    ])
    return "\n".join(lines)


def render_generic_raw_source_pack(plan: dict[str, Any], created: str) -> str:
    """Topic-agnostic raw source pack for `note-wiki` / `yaml` workflows."""
    title = f"Source pack — {plan['title']}"
    sources: list[str] = plan["sources"]
    lines = [
        "---",
        f"title: {title}",
        f"created: {created}",
        f"updated: {created}",
        "type: source",
        "tags: [notebooklm, research, source-pack]",
        f"source_url: {sources[0] if sources else ''}",
        "source_site: user-provided",
        f"source_date: {created}",
    ]
    lines.extend(_yaml_list_lines("source_urls", sources))
    lines.extend([
        "---",
        "",
        f"# {title}",
        "",
        "## URLs",
    ])
    lines.extend(f"- {source}" for source in sources)
    lines.extend([
        "",
        "## Prompt",
        plan.get("source_prompt") or plan.get("report_append") or "",
        "",
    ])
    return "\n".join(lines)
