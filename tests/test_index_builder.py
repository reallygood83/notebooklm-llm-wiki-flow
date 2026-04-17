from pathlib import Path

from notebooklm_llm_wiki_flow.index_builder import update_index_file


def test_update_index_file_renders_missing_sections_and_dynamic_page_count(tmp_path: Path):
    index_path = tmp_path / "index.md"
    index_path.write_text("# Index\n\nIntro text\n", encoding="utf-8")

    update_index_file(
        index_path,
        entity_entries=[("anthropic", "Anthropic entity"), ("openai", "OpenAI entity")],
        comparison_entries=[("anthropic-vs-openai", "Comparison note")],
        query_entries=[("education-policy-checklist", "Checklist note")],
        updated_on="2026-04-17",
    )

    text = index_path.read_text(encoding="utf-8")
    assert "Intro text" in text
    assert "Last updated: 2026-04-17 | Total pages: 4" in text
    assert "## Entities" in text
    assert "- [[anthropic]] — Anthropic entity" in text
    assert "## Comparisons" in text
    assert "- [[anthropic-vs-openai]] — Comparison note" in text
    assert "## Queries" in text
    assert "- [[education-policy-checklist]] — Checklist note" in text


def test_update_index_file_replaces_managed_sections_without_duplicates(tmp_path: Path):
    index_path = tmp_path / "index.md"
    index_path.write_text(
        "# Index\n\nIntro text\n\nLast updated: 2026-04-01 | Total pages: 99\n\n## Entities\n- [[anthropic]] — Old text\n\n## Comparisons\n- [[old-comparison]] — Old comparison\n\n## Queries\n- [[old-query]] — Old query\n",
        encoding="utf-8",
    )

    update_index_file(
        index_path,
        entity_entries=[("anthropic", "Anthropic entity")],
        comparison_entries=[("anthropic-vs-openai", "Comparison note")],
        query_entries=[("education-policy-checklist", "Checklist note")],
        updated_on="2026-04-17",
    )

    text = index_path.read_text(encoding="utf-8")
    assert text.count("## Entities") == 1
    assert text.count("## Comparisons") == 1
    assert text.count("## Queries") == 1
    assert "Old comparison" not in text
    assert "Old query" not in text
    assert text.count("[[anthropic]]") == 1
    assert "Total pages: 3" in text
