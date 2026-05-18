from __future__ import annotations

import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from .models import ComparisonDraft, ReportHighlights
from .report_parser import extract_first_markdown_table, extract_report_highlights
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
    implication = "표 형식 비교가 없어 bullet 기반 fallback"
    for bullet in highlights.bullets:
        cleaned = bullet.strip().lstrip("-* ")
        if not cleaned:
            continue
        if ":" in cleaned:
            label, detail = cleaned.split(":", 1)
            owner = label.strip()
            description = detail.strip()
        else:
            owner = ""
            description = cleaned
        if not description:
            continue
        key_differences.append((owner or "관찰", description, "", implication))
        if len(key_differences) >= 6:
            break
    return key_differences


def build_comparison_draft(
    report_markdown: str,
    qa_answer: str,
    title: str,
    *,
    source_count: int | None = None,
) -> ComparisonDraft:
    rows = extract_core_policy_table_rows(report_markdown)
    highlights = extract_report_highlights(report_markdown)
    checklist = extract_checklist_items(qa_answer, report_markdown)
    raw_table_block = extract_first_markdown_table(report_markdown)

    key_differences: list[tuple[str, str, str, str]] = []
    for feature, value_a, value_b in rows[:6]:
        implication = "raw report 표 기반 자동 추출, 후속 검토 필요"
        key_differences.append((feature, value_a, value_b, implication))

    if not key_differences and not raw_table_block:
        logger.warning("Falling back to bullet-based comparison draft because no policy comparison table rows were parsed.")
        key_differences = _fallback_key_differences(highlights)

    source_clause = f"{source_count}개 source" if source_count else "여러 source"
    summary_lines = [f"본 비교는 {source_clause}를 NotebookLM에 ingest한 결과를 정리한 초안이다."]
    if highlights.bullets:
        summary_lines.append("핵심 하이라이트: " + "; ".join(highlights.bullets[:3]))

    return ComparisonDraft(
        title=title,
        summary=" ".join(summary_lines),
        key_differences=key_differences,
        checklist=checklist,
        related_links=[],
        raw_table_block=raw_table_block,
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
    title: str,
    *,
    related_links: list[str] | None = None,
) -> str:
    body = [
        "---",
        f"title: {title}",
        f"created: {created}",
        f"updated: {created}",
        "type: query",
        "tags: [checklist, llm-wiki]",
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
    if related_links:
        body.extend([
            "",
            "## Related",
            ", ".join(f"[[{slug}]]" for slug in related_links),
        ])
    body.append("")
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


def render_inbox_summary(
    plan: dict[str, Any],
    notebook_id: str,
    artifacts_dir: Path,
    share_link: str | None = None,
    *,
    wiki_links: list[str] | None = None,
) -> str:
    created = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z").strip()
    title = plan["title"]
    source_prompt = plan.get("source_prompt", "")
    lines = [
        "---",
        f"title: {title}",
        "tags:",
        "  - notebooklm",
        "  - llm-wiki",
        "  - inbox",
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
    ])
    if share_link:
        lines.append(f"share_link: {share_link}")
    lines.extend([
        "---",
        "",
        f"# {title}",
        "",
        "> [!success]",
        "> NotebookLM-LLM-Wiki flow로 source를 수집·분석하고 wiki와 Obsidian에 산출물을 적재했다.",
        "",
    ])
    if source_prompt:
        lines.extend([
            "## 원본 프롬프트",
            "",
            f"> {source_prompt}",
            "",
        ])
    if wiki_links:
        lines.append("## 생성된 wiki 페이지")
        for link in wiki_links:
            lines.append(f"- [[{link}]]")
        lines.append("")
    lines.extend([
        "## 다음 단계",
        "- raw report와 checklist를 검토한다",
        "- 필요 시 도메인(work/persona)에 맞는 폴더로 라우팅한다",
        "- comparison 페이지의 시사점을 의사결정 근거로 변환한다",
        "",
    ])
    return "\n".join(lines)


def render_raw_source_pack(plan: dict[str, Any], created: str) -> str:
    title = f"Source pack — {plan['title']}"
    source_prompt = plan.get("source_prompt", "")
    lines = [
        "---",
        f"title: {title}",
        f"created: {created}",
        f"updated: {created}",
        "type: source",
        "tags: [source, llm-wiki]",
        f"source_url: {plan['sources'][0]}",
        "source_site: User-provided sources",
        f"source_date: {created}",
    ]
    lines.extend(_yaml_list_lines("source_urls", plan["sources"]))
    lines.extend([
        "---",
        "",
        f"# {title}",
        "",
        "## URLs",
    ])
    lines.extend(f"- {source}" for source in plan["sources"])
    if source_prompt:
        lines.extend([
            "",
            "## 수집 의도 (원본 프롬프트)",
            "",
            f"> {source_prompt}",
        ])
    lines.append("")
    return "\n".join(lines)
