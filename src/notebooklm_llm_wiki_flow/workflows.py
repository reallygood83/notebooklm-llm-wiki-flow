from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

import yaml

URL_RE = re.compile(r"https?://\S+")

POLICY_COMPARE_SOURCES = [
    "https://www.anthropic.com/legal/commercial-terms",
    "https://www.anthropic.com/legal/aup",
    "https://privacy.anthropic.com/en/articles/9957937-how-does-anthropic-use-submitted-feedback",
    "https://openai.com/policies/services-agreement/",
    "https://openai.com/policies/usage-policies/",
    "https://openai.com/business-data/",
    "https://openai.com/enterprise-privacy/",
]


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "workflow"


def extract_urls(text: str) -> list[str]:
    return [match.rstrip(").,]") for match in URL_RE.findall(text)]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def build_note_wiki_plan(prompt: str, *, title: str | None = None, sources: list[str] | None = None) -> dict[str, Any]:
    prompt_sources = extract_urls(prompt)
    merged_sources = _dedupe([*(sources or []), *prompt_sources])
    cleaned_prompt = URL_RE.sub("", prompt)
    cleaned_prompt = re.sub(r"\s+", " ", cleaned_prompt).strip(" -:\n\t")
    title_text = title or cleaned_prompt or "Note Wiki Request"
    base_slug = f"note-wiki-{slugify(title_text)}"
    return {
        "workflow": "note-wiki",
        "title": title_text,
        "sources": merged_sources,
        "report_append": prompt,
        "question": (
            "Create a practical note, synthesis, and actionable checklist for this request: "
            f"{cleaned_prompt or prompt}"
        ),
        "wiki_outputs": {
            "comparison_slug": base_slug,
            "comparison_title": title_text,
            "checklist_slug": f"{base_slug}-checklist",
            "checklist_title": f"{title_text} checklist",
        },
        "entities": [],
        "required_wiki_outputs": [
            "comparison page",
            "checklist page",
            "raw source capture",
        ],
        "source_prompt": prompt,
    }


def build_policy_compare_plan() -> dict[str, Any]:
    today = date.today().isoformat()
    title = f"Anthropic vs OpenAI Policy Comparison for Education Vertical AI {today}"
    base_slug = "anthropic-vs-openai-education-vertical-ai-policy"
    return {
        "workflow": "policy-compare",
        "title": title,
        "sources": POLICY_COMPARE_SOURCES,
        "report_append": (
            "Compare Anthropic and OpenAI business policies. Focus on data ownership, retention, "
            "training usage, acceptable use, enterprise controls, compliance, liability, and what "
            "an education vertical AI company should copy into its own policy."
        ),
        "question": (
            "Compare Anthropic and OpenAI business policies across data ownership, data retention, "
            "model training, acceptable use, enterprise controls, compliance, and IP/legal risk "
            "allocation. Then extract a policy checklist for an education vertical AI company serving "
            "schools, teachers, students, and guardians."
        ),
        "wiki_outputs": {
            "comparison_slug": base_slug,
            "comparison_title": "Anthropic vs OpenAI policy comparison for education vertical AI",
            "checklist_slug": "education-vertical-ai-policy-checklist",
            "checklist_title": "Education vertical AI policy checklist",
        },
        "entities": [
            {"slug": "anthropic", "title": "Anthropic", "summary": "Anthropic 관련 policy entity"},
            {"slug": "openai", "title": "OpenAI", "summary": "OpenAI 관련 policy entity"},
        ],
        "required_wiki_outputs": [
            "comparison page",
            "education policy checklist",
            "entity update for Anthropic",
            "entity page for OpenAI",
        ],
    }


def load_workflow_yaml(path: str | Path) -> dict[str, Any]:
    workflow_path = Path(path).expanduser().resolve()
    with workflow_path.open("r", encoding="utf-8") as handle:
        raw = yaml.safe_load(handle) or {}

    title = raw.get("title")
    sources = raw.get("sources") or []
    if not title:
        raise ValueError("workflow yaml must include title")
    if not sources:
        raise ValueError("workflow yaml must include at least one source URL")

    base_slug = slugify(raw.get("wiki_outputs", {}).get("comparison_slug") or title)
    wiki_outputs = dict(raw.get("wiki_outputs") or {})
    wiki_outputs.setdefault("comparison_slug", base_slug)
    wiki_outputs.setdefault("comparison_title", title)
    wiki_outputs.setdefault("checklist_slug", f"{base_slug}-checklist")
    wiki_outputs.setdefault("checklist_title", f"{title} checklist")

    return {
        "workflow": "yaml",
        "title": title,
        "sources": sources,
        "report_append": raw.get("report_append") or f"Summarize and compare the sources for: {title}",
        "question": raw.get("question") or (
            "What are the most important similarities, differences, and implementation takeaways from these sources? "
            "Produce an actionable checklist."
        ),
        "wiki_outputs": wiki_outputs,
        "entities": raw.get("entities") or [],
        "required_wiki_outputs": [
            "comparison page",
            "checklist page",
            "raw source capture",
        ],
    }
