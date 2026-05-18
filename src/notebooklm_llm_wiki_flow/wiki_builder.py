from __future__ import annotations

from .models import ComparisonDraft


def render_comparison_note(draft: ComparisonDraft) -> str:
    """Render the comparison page body for any source pair (or N-way).

    The previous implementation hard-coded a two-column "Anthropic / OpenAI"
    table. We now emit a generic Key points list that does not assume a fixed
    pair, and fall back to a clear "see raw report" message when no structured
    comparison rows are available.
    """
    lines: list[str] = [f"# {draft.title}", "", draft.summary, ""]

    if draft.raw_table_block:
        lines.extend(["## Side-by-side comparison", "", draft.raw_table_block, ""])
    elif draft.key_differences:
        lines.extend(["## Key points", ""])
        for axis, value_a, value_b, implication in draft.key_differences:
            parts: list[str] = [axis]
            if value_a:
                parts.append(value_a)
            if value_b:
                parts.append(value_b)
            line = "- " + " — ".join(parts)
            if implication:
                line += f"  (시사점: {implication})"
            lines.append(line)
        lines.append("")
    else:
        lines.extend([
            "## 상세 비교",
            "",
            "구조화된 비교 항목이 추출되지 않았다. NotebookLM raw report에서 상세 표·섹션을 참조한다.",
            "",
        ])

    if draft.checklist:
        lines.append("## Checklist")
        for item in draft.checklist:
            lines.append(f"- [ ] {item}")
        lines.append("")

    if draft.related_links:
        lines.append("## Related")
        lines.append(", ".join(f"[[{slug}]]" for slug in draft.related_links))
        lines.append("")

    return "\n".join(lines)
