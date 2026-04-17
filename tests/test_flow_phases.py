from pathlib import Path

from notebooklm_llm_wiki_flow.flow import _export_artifacts_phase, _run_notebook_phase
from notebooklm_llm_wiki_flow.flow_models import ArtifactExportResult, NotebookRunResult
from notebooklm_llm_wiki_flow.models import WorkflowConfig
from notebooklm_llm_wiki_flow.workflows import build_policy_compare_plan


class FakeNotebookLMClient:
    def create_notebook(self, title: str) -> dict:
        return {"id": "nb-demo", "title": title}

    def add_source(self, notebook_id: str, source: str) -> dict:
        return {"id": f"src-{source.rsplit('/', 1)[-1]}", "url": source}

    def wait_source(self, notebook_id: str, source_id: str, timeout: int = 300) -> dict:
        return {"id": source_id, "status": "ready", "timeout": timeout}

    def generate_report(self, notebook_id: str, report_append: str) -> dict:
        return {"task_id": "task-report"}

    def wait_artifact(self, notebook_id: str, artifact_id: str, timeout: int = 900) -> dict:
        return {"id": artifact_id, "status": "ready", "timeout": timeout}

    def generate_mind_map(self, notebook_id: str) -> dict:
        return {"note_id": "mindmap-1"}

    def ask(self, notebook_id: str, question: str) -> dict:
        return {"answer": "- [ ] Keep human review in the loop"}

    def download_report(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Demo report\n", encoding="utf-8")

    def download_mind_map(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('{"note_id":"mindmap-1"}', encoding="utf-8")


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
    assert result.report_path.read_text(encoding="utf-8") == "# Demo report\n"
    assert result.mind_map_path.read_text(encoding="utf-8") == '{"note_id":"mindmap-1"}'
    assert 'Keep human review' in result.qa_path.read_text(encoding="utf-8")
