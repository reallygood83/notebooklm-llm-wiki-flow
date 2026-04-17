from __future__ import annotations

from datetime import date
from pathlib import Path
import re

import yaml


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


def build_policy_compare_plan() -> dict:
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


def load_workflow_yaml(path: str | Path) -> dict:
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
