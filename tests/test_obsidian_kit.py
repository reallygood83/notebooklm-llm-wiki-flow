from pathlib import Path

from typer.testing import CliRunner

from notebooklm_llm_wiki_flow.cli import app
from notebooklm_llm_wiki_flow.policy_compare import render_checklist_note


def test_render_checklist_note_includes_clickable_source_urls():
    note = render_checklist_note(
        checklist=["Require human review for grading decisions"],
        sources=["raw/articles/source-a.md"],
        source_urls=["https://example.com/policy"],
        created="2026-04-17",
    )

    assert "source_notes: [raw/articles/source-a.md]" in note
    assert "source_urls:" in note
    assert "- https://example.com/policy" in note


def test_install_obsidian_kit_command_copies_templates_into_vault(tmp_path: Path):
    result = CliRunner().invoke(app, ["install-obsidian-kit", "--vault", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "000-Inbox" / "NLW Getting Started.md").exists()
    assert (tmp_path / "100-Templates" / "NLW Comparison Template.md").exists()
    assert (tmp_path / "900-System" / "nlwflow-obsidian-skills-guide.md").exists()
