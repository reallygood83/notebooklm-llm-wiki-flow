from notebooklm_llm_wiki_flow.policy_compare import render_anthropic_entity, render_openai_entity


def test_render_openai_entity_uses_template_driven_fields():
    rendered = render_openai_entity(
        "2026-04-17",
        ["raw/articles/source.md", "raw/articles/report.md"],
        ["https://example.com/openai"],
    )

    assert "source_notes: [raw/articles/source.md, raw/articles/report.md]" in rendered
    assert "source_urls:" in rendered
    assert "  - https://example.com/openai" in rendered
    assert "## Policy posture" in rendered
    assert "OpenAI는" in rendered
    assert "updated: 2026-04-17" in rendered


def test_render_anthropic_entity_uses_dynamic_created_date_from_template():
    rendered = render_anthropic_entity(
        "2026-04-17",
        ["raw/articles/source.md"],
        ["https://example.com/anthropic"],
    )

    assert "created: 2026-04-17" in rendered
    assert "updated: 2026-04-17" in rendered
    assert "source_notes: [raw/articles/source.md]" in rendered
    assert "## Policy posture" in rendered
    assert "Anthropic는" in rendered
