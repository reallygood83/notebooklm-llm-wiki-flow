from pathlib import Path

from notebooklm_llm_wiki_flow import flow
from notebooklm_llm_wiki_flow.models import WorkflowConfig
from tests.fakes.fake_notebooklm_client import FakeNotebookLMClient


def test_run_policy_compare_full_flow_updates_manifest_index_and_log(monkeypatch, tmp_path: Path):
    wiki_path = tmp_path / "LLM-Wiki"
    wiki_path.mkdir(parents=True)
    (wiki_path / "index.md").write_text("# Index\n\nIntro text\n", encoding="utf-8")
    (wiki_path / "log.md").write_text("# Log\n", encoding="utf-8")
    obsidian_vault = tmp_path / "LearningMaster"
    obsidian_vault.mkdir()
    artifacts_root = tmp_path / "artifacts"

    cfg = WorkflowConfig(
        project_name="test-project",
        obsidian_vault=obsidian_vault,
        wiki_path=wiki_path,
        qmd_collection="learningmaster",
        artifacts_root=artifacts_root,
    )
    monkeypatch.setattr(flow, "load_config", lambda path=None: cfg)

    payload = flow.run_policy_compare(
        qmd_update_enabled=False,
        client=FakeNotebookLMClient(),
    )

    manifest_path = Path(payload["manifest_path"])
    assert manifest_path.exists()
    assert Path(payload["comparison_page"]).exists()
    assert Path(payload["checklist_page"]).exists()
    assert Path(payload["inbox_note"]).exists()
    assert len(payload["entity_pages"]) == 2

    index_text = (wiki_path / "index.md").read_text(encoding="utf-8")
    assert "## Entities" in index_text
    assert "## Comparisons" in index_text
    assert "## Queries" in index_text
    assert "anthropic-vs-openai-education-vertical-ai-policy" in index_text

    log_text = (wiki_path / "log.md").read_text(encoding="utf-8")
    assert "Notebook ID: nb-demo" in log_text
    assert "Files created:" in log_text

    manifest_text = manifest_path.read_text(encoding="utf-8")
    assert "raw/articles/anthropic-vs-openai-education-vertical-ai-policy-sources" in manifest_text
    assert payload["qmd_updated"] is False
