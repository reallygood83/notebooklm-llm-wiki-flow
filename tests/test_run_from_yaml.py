import json
from pathlib import Path

from typer.testing import CliRunner

from notebooklm_llm_wiki_flow.cli import app
from notebooklm_llm_wiki_flow.workflows import build_note_wiki_plan, load_workflow_yaml


def test_load_workflow_yaml_reads_custom_titles_and_sources(tmp_path: Path):
    workflow = tmp_path / "workflow.yaml"
    workflow.write_text(
        """
        title: Custom Education Policy Comparison
        sources:
          - https://example.com/a
          - https://example.com/b
        report_append: Compare the two policies.
        question: What should an education AI company copy?
        wiki_outputs:
          comparison_slug: custom-policy-comparison
          comparison_title: Custom policy comparison
          checklist_slug: custom-policy-checklist
          checklist_title: Custom checklist
        """,
        encoding="utf-8",
    )

    plan = load_workflow_yaml(workflow)

    assert plan["title"] == "Custom Education Policy Comparison"
    assert plan["sources"] == ["https://example.com/a", "https://example.com/b"]
    assert plan["wiki_outputs"]["comparison_slug"] == "custom-policy-comparison"
    assert plan["wiki_outputs"]["checklist_title"] == "Custom checklist"


def test_run_from_yaml_dry_run_returns_yaml_plan(tmp_path: Path):
    workflow = tmp_path / "workflow.yaml"
    workflow.write_text(
        """
        title: Custom Education Policy Comparison
        sources:
          - https://example.com/a
        report_append: Compare the policy.
        wiki_outputs:
          comparison_slug: custom-policy-comparison
          checklist_slug: custom-policy-checklist
        """,
        encoding="utf-8",
    )

    result = CliRunner().invoke(app, ["run-from-yaml", str(workflow), "--dry-run", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["mode"] == "dry-run"
    assert payload["plan"]["title"] == "Custom Education Policy Comparison"
    assert payload["plan"]["wiki_outputs"]["comparison_slug"] == "custom-policy-comparison"


def test_build_note_wiki_plan_extracts_urls_and_builds_note_outputs():
    plan = build_note_wiki_plan(
        "Summarize these sources for teachers https://example.com/a https://example.com/b",
    )

    assert plan["workflow"] == "note-wiki"
    assert plan["sources"] == ["https://example.com/a", "https://example.com/b"]
    assert plan["wiki_outputs"]["comparison_slug"].startswith("note-wiki-")
    assert "teachers" in plan["title"].lower()
