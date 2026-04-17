import subprocess
from pathlib import Path

import pytest

from notebooklm_llm_wiki_flow import flow
from notebooklm_llm_wiki_flow.models import WorkflowConfig
from notebooklm_llm_wiki_flow.notebooklm_client import (
    NotebookLMClient,
    NotebookLMCommandError,
    NotebookLMTimeoutError,
)
from notebooklm_llm_wiki_flow.runner import NotebookLMRunner


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
        output_path.write_text("# Demo report\n\n## Findings\n\n| Feature | OpenAI | Anthropic |\n| --- | --- | --- |\n| Review | Human review | Human review |\n", encoding="utf-8")

    def download_mind_map(self, notebook_id: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text('{"note_id":"mindmap-1"}', encoding="utf-8")


def test_notebooklm_runner_implements_client_protocol():
    runner = NotebookLMRunner("notebooklm")

    assert isinstance(runner, NotebookLMClient)


def test_notebooklm_runner_wraps_called_process_error_with_step_context(monkeypatch: pytest.MonkeyPatch):
    def fake_run(*args, **kwargs):
        raise subprocess.CalledProcessError(
            1,
            ["notebooklm", "create", "Demo", "--json"],
            stderr="boom",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = NotebookLMRunner("notebooklm")

    with pytest.raises(NotebookLMCommandError) as exc_info:
        runner.create_notebook("Demo")

    error = exc_info.value
    assert error.step == "create_notebook"
    assert error.command == ["notebooklm", "create", "Demo", "--json"]
    assert "boom" in str(error)


def test_notebooklm_runner_wraps_invalid_json_with_step_context(monkeypatch: pytest.MonkeyPatch):
    def fake_run(*args, **kwargs):
        return subprocess.CompletedProcess(args[0], 0, stdout="not-json", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = NotebookLMRunner("notebooklm")

    with pytest.raises(NotebookLMCommandError) as exc_info:
        runner.create_notebook("Demo")

    error = exc_info.value
    assert error.step == "create_notebook"
    assert error.command == ["notebooklm", "create", "Demo", "--json"]
    assert "not-json" in error.stdout


def test_notebooklm_runner_wraps_timeout_with_step_context(monkeypatch: pytest.MonkeyPatch):
    def fake_run(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", fake_run)
    runner = NotebookLMRunner("notebooklm")

    with pytest.raises(NotebookLMTimeoutError) as exc_info:
        runner.wait_source("nb-demo", "src-1", timeout=300)

    error = exc_info.value
    assert error.step == "wait_source"
    assert error.command == ["notebooklm", "source", "wait", "-n", "nb-demo", "src-1", "--timeout", "300", "--json"]
    assert error.timeout_seconds == 305


def test_run_policy_compare_accepts_injected_client(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    wiki_path = tmp_path / "LLM-Wiki"
    wiki_path.mkdir(parents=True)
    (wiki_path / "index.md").write_text(
        "# Index\n\nLast updated: 2026-04-17 | Total pages: 1\n\n## Entities\n\n## Comparisons\n\n## Queries\n",
        encoding="utf-8",
    )
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

    payload = flow.run_policy_compare(qmd_update_enabled=False, client=FakeNotebookLMClient())

    assert payload["notebook_id"] == "nb-demo"
    assert Path(payload["comparison_page"]).exists()
    assert Path(payload["inbox_note"]).exists()
    assert Path(payload["manifest_path"]).exists()
