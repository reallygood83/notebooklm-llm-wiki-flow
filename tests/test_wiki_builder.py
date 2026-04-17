from notebooklm_llm_wiki_flow.models import ComparisonDraft
from notebooklm_llm_wiki_flow.wiki_builder import render_comparison_note


def test_render_comparison_note_contains_wikilinks_and_checklist():
    draft = ComparisonDraft(
        title="Anthropic vs OpenAI",
        summary="A comparison focused on education vertical AI.",
        key_differences=[
            ("data training", "No on customer content", "No by default", "Adopt no-training-by-default"),
        ],
        checklist=["Require human review for grading decisions"],
        related_links=["anthropic", "openai", "llm-wiki"],
    )

    note = render_comparison_note(draft)

    assert "## Side-by-side comparison" in note
    assert "[[anthropic]]" in note
    assert "[[openai]]" in note
    assert "- [ ] Require human review for grading decisions" in note
