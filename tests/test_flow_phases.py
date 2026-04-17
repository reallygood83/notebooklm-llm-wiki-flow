from pathlib import Path

from notebooklm_llm_wiki_flow.flow import _export_artifacts_phase, _run_notebook_phase
from notebooklm_llm_wiki_flow.flow_models import ArtifactExportResult, NotebookRunResult
from notebooklm_llm_wiki_flow.models import WorkflowConfig
from notebooklm_llm_wiki_flow.workflows import build_policy_compare_plan
from tests.fakes.fake_notebooklm_client import FakeNotebookLMClient


def test_run_notebook_phase_returns_typed_result():
    plan = build_policy_compare_plan()

    result = _run_notebook_phase(plan, FakeNotebookLMClient())

    assert isinstance(result, NotebookRunResult)
    assert result.notebook_id == "nb-demo"
    assert result.report_task["task_id"] == "task-report"
    assert result.mind_map["note_id"] == "mindmap-1"
    assert result.qa["answer"] == "- [ ] Keep human review in the loop"
    assert len(result.sources) == len(plan["sources"])


def test_export_artifacts_phase_writes_expected_files(tmp_path: Path):
    cfg = WorkflowConfig(
        project_name="test-project",
        obsidian_vault=tmp_path / "vault",
        wiki_path=tmp_path / "wiki",
        qmd_collection="learningmaster",
        artifacts_root=tmp_path / "artifacts",
    )
    run_result = NotebookRunResult(
        notebook_id="nb-demo",
        sources=[{"id": "src-1", "url": "https://example.com/1"}],
        report_task={"task_id": "task-report"},
        mind_map={"note_id": "mindmap-1"},
        qa={"answer": "- [ ] Keep human review in the loop"},
    )

    result = _export_artifacts_phase(cfg, FakeNotebookLMClient(), run_result)

    assert isinstance(result, ArtifactExportResult)
    assert result.artifacts_dir == tmp_path / "artifacts" / "nb-demo"
    assert result.report_path.read_text(encoding="utf-8").startswith("# Demo report\n")
    assert result.mind_map_path.read_text(encoding="utf-8") == '{"note_id":"mindmap-1"}'
    assert 'Keep human review' in result.qa_path.read_text(encoding="utf-8")
