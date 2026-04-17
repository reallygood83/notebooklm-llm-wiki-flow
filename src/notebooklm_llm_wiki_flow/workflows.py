from __future__ import annotations

from datetime import date


POLICY_COMPARE_SOURCES = [
    "https://www.anthropic.com/legal/commercial-terms",
    "https://www.anthropic.com/legal/aup",
    "https://privacy.anthropic.com/en/articles/9957937-how-does-anthropic-use-submitted-feedback",
    "https://openai.com/policies/services-agreement/",
    "https://openai.com/policies/usage-policies/",
    "https://openai.com/business-data/",
    "https://openai.com/enterprise-privacy/",
]


def build_policy_compare_plan() -> dict:
    today = date.today().isoformat()
    return {
        "workflow": "policy-compare",
        "title": f"Anthropic vs OpenAI Policy Comparison for Education Vertical AI {today}",
        "sources": POLICY_COMPARE_SOURCES,
        "report_append": (
            "Compare Anthropic and OpenAI business policies. Focus on data ownership, retention, "
            "training usage, acceptable use, enterprise controls, compliance, liability, and what "
            "an education vertical AI company should copy into its own policy."
        ),
        "required_wiki_outputs": [
            "comparison page",
            "education policy checklist",
            "entity update for Anthropic",
            "entity page for OpenAI",
        ],
    }
