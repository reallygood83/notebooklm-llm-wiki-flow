from __future__ import annotations

from .models import ComparisonDraft


def render_comparison_note(draft: ComparisonDraft) -> str:
    table_rows = ["| 항목 | Anthropic | OpenAI | 시사점 |", "|------|-----------|--------|--------|"]
    for axis, anthropic, openai, implication in draft.key_differences:
        table_rows.append(f"| {axis} | {anthropic} | {openai} | {implication} |")

    checklist_lines = [f"- [ ] {item}" for item in draft.checklist]
    related = ', '.join(f'[[{slug}]]' for slug in draft.related_links)

    return "\n".join([
        f"# {draft.title}",
        "",
        draft.summary,
        "",
        "## Side-by-side comparison",
        *table_rows,
        "",
        "## Checklist",
        *checklist_lines,
        "",
        "## Related",
        related,
        "",
    ])
