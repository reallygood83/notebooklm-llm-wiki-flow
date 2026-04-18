from __future__ import annotations

from .models import ComparisonDraft


def render_comparison_note(
    draft: ComparisonDraft,
    *,
    column_labels: tuple[str, str] = ("Anthropic", "OpenAI"),
    section_heading: str = "Side-by-side comparison",
) -> str:
    header = f"| 항목 | {column_labels[0]} | {column_labels[1]} | 시사점 |"
    divider = "|------|" + "------|" * 3
    table_rows = [header, divider]
    for axis, col_a, col_b, implication in draft.key_differences:
        table_rows.append(f"| {axis} | {col_a} | {col_b} | {implication} |")

    checklist_lines = [f"- [ ] {item}" for item in draft.checklist]
    related = ', '.join(f'[[{slug}]]' for slug in draft.related_links)

    return "\n".join([
        f"# {draft.title}",
        "",
        draft.summary,
        "",
        f"## {section_heading}",
        *table_rows,
        "",
        "## Checklist",
        *checklist_lines,
        "",
        "## Related",
        related,
        "",
    ])
