from __future__ import annotations

from pathlib import Path


MANAGED_HEADERS = ("## Entities", "## Comparisons", "## Queries")


def _dedupe_entries(entries: list[tuple[str, str]]) -> list[tuple[str, str]]:
    seen: set[str] = set()
    result: list[tuple[str, str]] = []
    for slug, summary in entries:
        if slug in seen:
            continue
        seen.add(slug)
        result.append((slug, summary))
    return result


def _render_section(header: str, entries: list[tuple[str, str]]) -> str:
    lines = [header]
    lines.extend(f"- [[{slug}]] — {summary}" for slug, summary in _dedupe_entries(entries))
    return "\n".join(lines)


def update_index_file(
    index_path: Path,
    *,
    entity_entries: list[tuple[str, str]],
    comparison_entries: list[tuple[str, str]],
    query_entries: list[tuple[str, str]],
    updated_on: str,
) -> None:
    existing_text = index_path.read_text(encoding="utf-8") if index_path.exists() else "# Index\n"
    lines = existing_text.splitlines()

    preamble: list[str] = []
    for line in lines:
        if line.startswith("Last updated: ") or line in MANAGED_HEADERS:
            break
        preamble.append(line)

    preamble_text = "\n".join(preamble).strip() or "# Index"
    total_pages = len(_dedupe_entries(entity_entries)) + len(_dedupe_entries(comparison_entries)) + len(_dedupe_entries(query_entries))

    sections = [
        _render_section("## Entities", entity_entries),
        _render_section("## Comparisons", comparison_entries),
        _render_section("## Queries", query_entries),
    ]

    rendered = "\n\n".join(
        [
            preamble_text,
            f"Last updated: {updated_on} | Total pages: {total_pages}",
            *sections,
        ]
    )
    index_path.write_text(rendered + "\n", encoding="utf-8")
